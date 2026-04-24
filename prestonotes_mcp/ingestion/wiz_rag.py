"""Wiz product documentation RAG: Chroma persistent store + Gemini embeddings."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from pathlib import Path
from typing import Any, cast

import chromadb
from chromadb import Collection
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.errors import NotFoundError
from google import genai

WIZ_COLLECTION_NAME = "wiz_docs"
DEFAULT_CHROMA_REL = ".vector_db/wiz_chroma"
DEFAULT_DOCS_REL = "docs/ai/cache/wiz_mcp_server/docs"
DEFAULT_WIZ_EXT_PAGES_REL = "docs/ai/cache/wiz_mcp_server/ext/pages"
DEFAULT_MCP_MATERIALIZATIONS_REL = "docs/ai/cache/wiz_mcp_server/mcp_materializations"
DEFAULT_MANIFEST_REL = "docs/ai/cache/wiz_mcp_server/manifest.json"


def gemini_api_key() -> str | None:
    k = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    return k or None


def default_embedding_model() -> str:
    env = (os.environ.get("PRESTONOTES_GEMINI_EMBEDDING_MODEL") or "").strip()
    return env or "text-embedding-004"


def embedding_model_from_config(config: dict[str, Any] | None) -> str | None:
    if not config:
        return None
    rag = config.get("rag")
    if not isinstance(rag, dict):
        return None
    m = str(rag.get("embedding_model") or "").strip()
    return m or None


def wiz_chroma_directory(repo_root: Path, config: dict[str, Any] | None = None) -> Path:
    rag: dict[str, Any] = {}
    if isinstance(config, dict):
        raw = config.get("rag")
        if isinstance(raw, dict):
            rag = raw
    rel = str(rag.get("chroma_path", "") or "").strip() or DEFAULT_CHROMA_REL
    return (repo_root / rel).resolve()


def wiz_docs_cache_rel(config: dict[str, Any] | None) -> str:
    rag = (
        config.get("rag")
        if isinstance(config, dict) and isinstance(config.get("rag"), dict)
        else {}
    )
    rel = str(rag.get("wiz_docs_cache", "") or "").strip()
    return rel or DEFAULT_DOCS_REL


def wiz_ext_pages_rel(config: dict[str, Any] | None) -> str:
    rag = (
        config.get("rag")
        if isinstance(config, dict) and isinstance(config.get("rag"), dict)
        else {}
    )
    rel = str(rag.get("wiz_ext_pages", "") or "").strip()
    return rel or DEFAULT_WIZ_EXT_PAGES_REL


def wiz_mcp_materializations_rel(config: dict[str, Any] | None) -> str:
    rag = (
        config.get("rag")
        if isinstance(config, dict) and isinstance(config.get("rag"), dict)
        else {}
    )
    rel = str(rag.get("wiz_mcp_materializations", "") or "").strip()
    return rel or DEFAULT_MCP_MATERIALIZATIONS_REL


def load_wiz_manifest(repo_root: Path) -> dict[str, Any]:
    path = (repo_root / DEFAULT_MANIFEST_REL).resolve()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _rel_under_docs_cache(rel_posix: str, docs_cache_rel: str) -> bool:
    base = docs_cache_rel.strip().replace("\\", "/").strip("/")
    r = rel_posix.strip().replace("\\", "/").strip("/")
    return r == base or r.startswith(base + "/")


def manifest_meta_for_source_path(
    manifest: dict[str, Any],
    rel_posix: str,
    *,
    docs_cache_rel: str | None = None,
    mcp_materializations_rel: str | None = None,
) -> dict[str, str]:
    """Map a repo-relative markdown path to manifest fields for ``doc:{stem}`` WIN rows.

    Applies to static WIN exports under ``wiz_docs_cache`` and MCP materializations under
    ``wiz_mcp_materializations`` when filenames match ``<doc_name>.md``.
    """
    cache_rel = (docs_cache_rel or DEFAULT_DOCS_REL).strip().replace("\\", "/").strip("/")
    mcp_rel = (
        (mcp_materializations_rel or DEFAULT_MCP_MATERIALIZATIONS_REL)
        .strip()
        .replace("\\", "/")
        .strip("/")
    )
    r = rel_posix.strip().replace("\\", "/")
    if not (_rel_under_docs_cache(r, cache_rel) or _rel_under_docs_cache(r, mcp_rel)):
        return {}
    name = Path(r).name
    if not name.endswith(".md"):
        return {}
    stem = name[: -len(".md")]
    entry_id = f"doc:{stem}"
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        if e.get("id") != entry_id:
            continue
        if e.get("type") != "win_doc":
            continue
        out: dict[str, str] = {}
        for key in ("last_cached", "next_refresh_due", "status"):
            v = e.get(key)
            if v is not None and str(v).strip() != "":
                out[key] = str(v)
        return out
    return {}


def stable_chunk_id(source_rel: str, chunk_index: int) -> str:
    """Legacy chunk id (single-root); prefer :func:`stable_chunk_id_with_root` for multi-root ingest."""
    return hashlib.sha256(f"{source_rel}\n{chunk_index}".encode()).hexdigest()


def stable_chunk_id_with_root(ingest_root_tag: str, rel: str, chunk_index: int) -> str:
    tag = (ingest_root_tag or "default").strip()
    payload = f"{tag}|{rel}|{chunk_index}"
    return hashlib.sha256(payload.encode()).hexdigest()


def split_wiz_chunks(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    text = text.replace("\r\n", "\n")
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = end - overlap
    return chunks


class GeminiEmbeddingFunction(EmbeddingFunction[Documents]):
    """Gemini text embeddings via ``google.genai.Client`` (Chroma ``EmbeddingFunction``)."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = (api_key or gemini_api_key() or "").strip()
        if not key:
            raise ValueError("Missing Google API key (GOOGLE_API_KEY or GEMINI_API_KEY)")
        self._model = (model or default_embedding_model()).strip() or "text-embedding-004"
        self._client = genai.Client(api_key=key)

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []
        out: list[list[float]] = []
        batch_size = 64
        for i in range(0, len(input), batch_size):
            batch = list(input[i : i + batch_size])
            out.extend(self._embed_batch_strings(batch))
        return cast(Embeddings, out)

    def _embed_batch_strings(self, batch: list[str]) -> list[list[float]]:
        if len(batch) == 1:
            return [self._embed_one(batch[0])]
        try:
            resp = self._client.models.embed_content(model=self._model, contents=batch)
            return self._vectors_from_response(resp, len(batch))
        except Exception:  # noqa: BLE001
            acc: list[list[float]] = []
            for s in batch:
                acc.extend(self._embed_batch_strings([s]))
            return acc

    def _embed_one(self, text: str) -> list[float]:
        resp = self._client.models.embed_content(model=self._model, contents=text)
        return self._vectors_from_response(resp, 1)[0]

    @staticmethod
    def _vectors_from_response(resp: Any, expected: int) -> list[list[float]]:
        embs = getattr(resp, "embeddings", None) or []
        if len(embs) != expected:
            raise ValueError("embedding count mismatch")
        rows: list[list[float]] = []
        for e in embs:
            vals = getattr(e, "values", None)
            if vals is None:
                raise ValueError("missing embedding values")
            rows.append([float(x) for x in vals])
        return rows

    @staticmethod
    def name() -> str:
        return "prestonotes_gemini_text_embedding"

    def get_config(self) -> dict[str, Any]:
        return {"model": self._model}

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> GeminiEmbeddingFunction:
        GeminiEmbeddingFunction.validate_config(config)
        rag = config.get("rag") if isinstance(config.get("rag"), dict) else {}
        model = str(rag.get("embedding_model") or config.get("model") or "").strip() or None
        return GeminiEmbeddingFunction(api_key=gemini_api_key(), model=model)

    @staticmethod
    def validate_config(config: dict[str, Any]) -> None:
        if not isinstance(config, dict):
            raise TypeError("config must be a dict")


def wiz_persistent_client(chroma_dir: Path) -> chromadb.PersistentClient:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir))


def get_wiz_collection(
    client: chromadb.PersistentClient,
    embedding_function: GeminiEmbeddingFunction,
    *,
    reset: bool = False,
) -> Collection:
    names = {c.name for c in client.list_collections()}
    if reset and WIZ_COLLECTION_NAME in names:
        client.delete_collection(WIZ_COLLECTION_NAME)
        names.discard(WIZ_COLLECTION_NAME)
    if WIZ_COLLECTION_NAME in names:
        return client.get_collection(
            name=WIZ_COLLECTION_NAME,
            embedding_function=embedding_function,
        )
    return client.create_collection(
        name=WIZ_COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )


def query_wiz_knowledge(
    repo_root: Path,
    query: str,
    max_results: int,
    config: dict[str, Any] | None = None,
    *,
    include_staleness: bool = False,
) -> dict[str, Any]:
    """Query Wiz docs collection; returns a dict suitable for JSON serialization."""
    if not gemini_api_key():
        return {
            "error": "Missing Google API key for embeddings.",
            "hint": "Set GOOGLE_API_KEY in .cursor/mcp.env (or GEMINI_API_KEY), then restart the MCP server.",
        }
    cfg = config if isinstance(config, dict) else {}
    model = embedding_model_from_config(cfg)
    try:
        ef = GeminiEmbeddingFunction(model=model)
    except ValueError as exc:
        return {"error": str(exc)}

    chroma_dir = wiz_chroma_directory(repo_root.resolve(), cfg)
    client = wiz_persistent_client(chroma_dir)
    try:
        col = client.get_collection(
            name=WIZ_COLLECTION_NAME,
            embedding_function=ef,
        )
    except NotFoundError:
        return {
            "error": "Wiz vector collection not found.",
            "hint": (
                "Run `uv run python -m prestonotes_mcp.ingestion.build_vector_db` "
                "from the repo root after caching Wiz docs under docs/ai/cache/wiz_mcp_server/docs."
            ),
        }

    if col.count() == 0:
        return {
            "error": "Wiz vector collection is empty.",
            "hint": (
                "Run `uv run python -m prestonotes_mcp.ingestion.build_vector_db` "
                "to index markdown, then retry wiz_knowledge_search."
            ),
        }

    q = (query or "").strip()
    if not q:
        return {"error": "query is empty"}

    n = max(1, min(int(max_results), 50))
    raw = col.query(
        query_texts=[q],
        n_results=min(n, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    ids_batch = raw.get("ids") or [[]]
    dist_batch = raw.get("distances") or [[]]
    docs_batch = raw.get("documents") or [[]]
    meta_batch = raw.get("metadatas") or [[]]

    docs_cache_rel = wiz_docs_cache_rel(cfg)
    today = date.today()
    manifest: dict[str, Any] = load_wiz_manifest(repo_root.resolve()) if include_staleness else {}

    results: list[dict[str, Any]] = []
    for i, doc_id in enumerate(ids_batch[0]):
        doc = (docs_batch[0][i] if i < len(docs_batch[0]) else "") or ""
        dist = dist_batch[0][i] if i < len(dist_batch[0]) else None
        meta = meta_batch[0][i] if i < len(meta_batch[0]) else None
        meta_out: dict[str, str] = {}
        source_path = ""
        if isinstance(meta, dict):
            for k, v in meta.items():
                if v is None:
                    continue
                meta_out[str(k)] = str(v)
            source_path = meta_out.get("source_path", "")
        row: dict[str, Any] = {
            "id": doc_id,
            "distance": dist,
            "document_excerpt": doc[:500],
            "metadata": meta_out if meta_out else {"source_path": source_path},
        }
        if include_staleness:
            mm = manifest_meta_for_source_path(manifest, source_path, docs_cache_rel=docs_cache_rel)
            due = mm.get("next_refresh_due")
            if due:
                try:
                    if date.fromisoformat(due) <= today:
                        row["stale"] = True
                except ValueError:
                    pass
        results.append(row)

    return {"ok": True, "results": results}
