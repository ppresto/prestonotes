"""Build local Chroma DB for Wiz markdown from configurable cache roots."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from prestonotes_mcp.ingestion.wiz_rag import (
    WIZ_COLLECTION_NAME,
    GeminiEmbeddingFunction,
    default_embedding_model,
    embedding_model_from_config,
    gemini_api_key,
    get_wiz_collection,
    load_wiz_manifest,
    manifest_meta_for_source_path,
    split_wiz_chunks,
    stable_chunk_id_with_root,
    wiz_chroma_directory,
    wiz_docs_cache_rel,
    wiz_ext_pages_rel,
    wiz_mcp_materializations_rel,
    wiz_persistent_client,
)


def _load_optional_config(repo_root: Path) -> dict:
    try:
        from prestonotes_mcp.config import load_config

        return load_config(repo_root)
    except Exception:
        return {}


def _ensure_under_repo(repo_root: Path, path: Path) -> Path:
    resolved = path.resolve()
    root = repo_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path must stay inside repo: {path}") from exc
    return resolved


def _iter_markdown_files(docs_dir: Path) -> list[Path]:
    return sorted(p for p in docs_dir.rglob("*.md") if p.is_file())


def _collect_ingest_roots(
    repo_root: Path,
    docs_cache_rel: str,
    ext_pages_rel: str,
    mcp_mat_rel: str,
    *,
    ingest_ext: bool,
    ingest_mcp: bool,
) -> tuple[list[tuple[Path, str]], bool]:
    """Return list of (absolute_dir, ingest_tag)) and whether ext was skipped (missing dir)."""
    roots: list[tuple[Path, str]] = []
    ext_skipped = False
    d_docs = _ensure_under_repo(repo_root, repo_root / docs_cache_rel)
    if d_docs.is_dir():
        roots.append((d_docs, "docs"))
    if ingest_mcp:
        d_mcp = _ensure_under_repo(repo_root, repo_root / mcp_mat_rel)
        if d_mcp.is_dir():
            roots.append((d_mcp, "mcp"))
    if ingest_ext:
        d_ext = _ensure_under_repo(repo_root, repo_root / ext_pages_rel)
        if d_ext.is_dir():
            roots.append((d_ext, "ext"))
        else:
            ext_skipped = True
    return roots, ext_skipped


def _build_impl(
    repo_root: Path,
    docs_cache_rel: str,
    ext_pages_rel: str,
    mcp_mat_rel: str,
    *,
    ingest_ext: bool,
    ingest_mcp: bool,
    reset: bool,
    dry_run: bool,
    config: dict | None = None,
) -> int:
    cfg = config if isinstance(config, dict) else _load_optional_config(repo_root)
    roots, ext_skipped = _collect_ingest_roots(
        repo_root,
        docs_cache_rel,
        ext_pages_rel,
        mcp_mat_rel,
        ingest_ext=ingest_ext,
        ingest_mcp=ingest_mcp,
    )
    if ext_skipped and ingest_ext:
        print(
            f"note: optional Wiz ext pages dir not found, skipping: {ext_pages_rel!r}",
            file=sys.stderr,
        )
    if not roots:
        print(
            "error: no Wiz ingest directories exist under the repo "
            f"(docs cache={docs_cache_rel!r}"
            + (f", ext pages={ext_pages_rel!r}" if ingest_ext else "")
            + ")",
            file=sys.stderr,
        )
        return 1

    all_files: list[tuple[Path, str]] = []
    for base, tag in roots:
        for p in _iter_markdown_files(base):
            all_files.append((p, tag))

    if dry_run:
        print(
            f"dry-run: would index {len(all_files)} markdown files from "
            f"{len(roots)} root(s): {[str(b.relative_to(repo_root)) for b, _ in roots]}"
        )
        return 0

    if not roots:
        print(
            f"error: no ingest directories exist (checked docs={docs_cache_rel!r}",
            file=sys.stderr,
        )
        if ingest_ext:
            print(f"  and ext={ext_pages_rel!r})", file=sys.stderr)
        return 1

    key = gemini_api_key()
    if not key:
        print(
            "error: GOOGLE_API_KEY or GEMINI_API_KEY is required to call Gemini embeddings.",
            file=sys.stderr,
        )
        return 1

    model = embedding_model_from_config(cfg) or default_embedding_model()
    ef = GeminiEmbeddingFunction(model=model)
    chroma_dir = wiz_chroma_directory(repo_root, cfg)
    client = wiz_persistent_client(chroma_dir)
    col = get_wiz_collection(client, ef, reset=reset)

    manifest = load_wiz_manifest(repo_root.resolve())
    docs_rel_norm = docs_cache_rel.strip().replace("\\", "/").strip("/")
    mcp_rel_norm = mcp_mat_rel.strip().replace("\\", "/").strip("/")

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []
    root = repo_root.resolve()

    for path, ingest_tag in all_files:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks = split_wiz_chunks(text)
        file_meta = manifest_meta_for_source_path(
            manifest,
            rel,
            docs_cache_rel=docs_rel_norm,
            mcp_materializations_rel=mcp_rel_norm,
        )
        for idx, chunk in enumerate(chunks):
            ids.append(stable_chunk_id_with_root(ingest_tag, rel, idx))
            documents.append(chunk)
            meta: dict[str, str] = {"source_path": rel, "ingest_root": ingest_tag}
            meta.update(file_meta)
            metadatas.append(meta)

    if not ids:
        print(f"warning: no chunks produced from {len(all_files)} files", file=sys.stderr)
        return 0

    batch = 128
    for i in range(0, len(ids), batch):
        chunk_ids = ids[i : i + batch]
        chunk_docs = documents[i : i + batch]
        chunk_meta = metadatas[i : i + batch]
        if reset:
            col.add(ids=chunk_ids, documents=chunk_docs, metadatas=chunk_meta)
        else:
            col.upsert(ids=chunk_ids, documents=chunk_docs, metadatas=chunk_meta)

    print(
        f"indexed {len(all_files)} files, {len(ids)} chunks into "
        f"{chroma_dir} collection {WIZ_COLLECTION_NAME!r} (model={model!r})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Wiz markdown Chroma index (wiz_docs).")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: PRESTONOTES_REPO_ROOT or cwd)",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=None,
        help="Override primary Wiz docs cache dir (relative to repo); default from YAML rag.wiz_docs_cache",
    )
    parser.add_argument(
        "--ingest-ext",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Also index rag.wiz_ext_pages when that directory exists (default: true)",
    )
    parser.add_argument(
        "--ingest-mcp",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Also index rag.wiz_mcp_materializations when present (default: true)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help=f"Delete and recreate the {WIZ_COLLECTION_NAME!r} collection before indexing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only count markdown files; do not call embeddings or write Chroma data",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root or Path(
        os.environ.get("PRESTONOTES_REPO_ROOT") or os.getcwd(),
    )
    repo_root = repo_root.resolve()
    cfg = _load_optional_config(repo_root)
    docs_cache_rel = (args.docs_dir or "").strip() or wiz_docs_cache_rel(cfg)
    ext_pages_rel = wiz_ext_pages_rel(cfg)
    mcp_mat_rel = wiz_mcp_materializations_rel(cfg)

    try:
        return _build_impl(
            repo_root,
            docs_cache_rel,
            ext_pages_rel,
            mcp_mat_rel,
            ingest_ext=bool(args.ingest_ext),
            ingest_mcp=bool(args.ingest_mcp),
            reset=args.reset,
            dry_run=args.dry_run,
            config=cfg,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
