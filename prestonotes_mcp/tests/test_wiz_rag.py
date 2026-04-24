"""Tests for Wiz RAG (Stage 4) — mocked Gemini, no network."""

from __future__ import annotations

from pathlib import Path

import pytest

import prestonotes_mcp.ingestion.wiz_rag as wiz_rag
from prestonotes_mcp.ingestion import build_vector_db
from prestonotes_mcp.ingestion.wiz_rag import query_wiz_knowledge


class _FakeEmb:
    def __init__(self, values: list[float]) -> None:
        self.values = values


class _FakeResp:
    def __init__(self, embeddings: list[_FakeEmb]) -> None:
        self.embeddings = embeddings


def _embed_vectors_for_texts(texts: list[str]) -> _FakeResp:
    rows: list[_FakeEmb] = []
    for t in texts:
        if "UNIQUE_NEEDLE_XYZ" in t:
            rows.append(_FakeEmb([1.0, 0.0, 0.0]))
        else:
            rows.append(_FakeEmb([0.0, 1.0, 0.0]))
    return _FakeResp(rows)


class _FakeModels:
    def embed_content(self, *, model: str, contents: object) -> _FakeResp:
        if isinstance(contents, str):
            texts = [contents]
        else:
            texts = list(contents)  # type: ignore[arg-type]
        return _embed_vectors_for_texts(texts)


class _FakeClient:
    def __init__(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)
        self.models = _FakeModels()


def _write_minimal_mcp_yaml(repo: Path, *, chroma_rel: str) -> None:
    p = repo / "prestonotes_mcp" / "prestonotes-mcp.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "\n".join(
            [
                "server:",
                "  name: prestonotes",
                "  version: '2.0.0'",
                "paths:",
                "  gdrive_base: ''",
                "rag:",
                f"  chroma_path: {chroma_rel}",
                "google: {}",
                "defaults: {}",
                "security: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_wiz_build_two_chunks_query_top_has_needle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiz_rag.genai, "Client", _FakeClient)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    repo = tmp_path / "repo"
    docs = repo / "docs" / "ai" / "cache" / "wiz_mcp_server" / "docs"
    docs.mkdir(parents=True)
    # Two chunks: first chunk is filler; second contains the needle.
    body = ("x" * 1199) + "\n" + "UNIQUE_NEEDLE_XYZ" + ("y" * 2500)
    (docs / "wiz-page.md").write_text(body, encoding="utf-8")

    chroma_rel = ".vector_db/wiz_test_chroma"
    _write_minimal_mcp_yaml(repo, chroma_rel=chroma_rel)

    rc = build_vector_db.main(
        [
            "--repo-root",
            str(repo),
            "--docs-dir",
            "docs/ai/cache/wiz_mcp_server/docs",
            "--reset",
        ]
    )
    assert rc == 0

    cfg = {"rag": {"chroma_path": chroma_rel}}
    raw = query_wiz_knowledge(repo, "UNIQUE_NEEDLE_XYZ", 5, cfg)
    assert raw.get("ok") is True
    results = raw.get("results") or []
    assert results, results
    top = results[0]["document_excerpt"]
    assert "UNIQUE_NEEDLE_XYZ" in top
    assert (
        results[0]["metadata"].get("source_path") == "docs/ai/cache/wiz_mcp_server/docs/wiz-page.md"
    )


def test_query_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    out = query_wiz_knowledge(Path("/tmp"), "hello", 3, {})
    assert out.get("error")
    assert "GOOGLE_API_KEY" in out.get("hint", "")
