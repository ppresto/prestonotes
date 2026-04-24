"""Manifest metadata merged into Chroma ingest (TASK-024)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import prestonotes_mcp.ingestion.wiz_rag as wiz_rag
from prestonotes_mcp.ingestion import build_vector_db
from prestonotes_mcp.ingestion.wiz_rag import (
    manifest_meta_for_source_path,
    query_wiz_knowledge,
    stable_chunk_id_with_root,
)
from prestonotes_mcp.tests.test_wiz_rag import (  # noqa: PLC2701 — reuse fakes
    _FakeClient,
    _write_minimal_mcp_yaml,
)


def test_manifest_meta_matches_doc_entry() -> None:
    manifest = {
        "entries": [
            {
                "id": "doc:foo",
                "type": "win_doc",
                "status": "cached",
                "last_cached": "2026-01-01",
                "next_refresh_due": "2026-12-31",
            }
        ]
    }
    rel = "docs/ai/cache/wiz_mcp_server/docs/foo.md"
    meta = manifest_meta_for_source_path(manifest, rel)
    assert meta["status"] == "cached"
    assert meta["last_cached"] == "2026-01-01"
    assert meta["next_refresh_due"] == "2026-12-31"


def test_manifest_meta_empty_for_ext_pages_path() -> None:
    manifest = {
        "entries": [
            {
                "id": "doc:bar",
                "type": "win_doc",
                "next_refresh_due": "2026-12-31",
            }
        ]
    }
    rel = "docs/ai/cache/wiz_mcp_server/ext/pages/bar.md"
    assert manifest_meta_for_source_path(manifest, rel) == {}


def test_manifest_meta_mcp_materializations_path() -> None:
    manifest = {
        "entries": [
            {
                "id": "doc:from_mcp",
                "type": "win_doc",
                "status": "cached",
                "last_cached": "2026-04-01",
                "next_refresh_due": "2026-04-15",
            }
        ]
    }
    rel = "docs/ai/cache/wiz_mcp_server/mcp_materializations/from_mcp.md"
    meta = manifest_meta_for_source_path(manifest, rel)
    assert meta.get("last_cached") == "2026-04-01"
    assert meta.get("status") == "cached"


def test_stable_chunk_id_with_root_avoids_collision() -> None:
    rel = "docs/ai/cache/wiz_mcp_server/docs/x.md"
    assert stable_chunk_id_with_root("docs", rel, 0) != stable_chunk_id_with_root("ext", rel, 0)


def test_build_indexes_manifest_dates_on_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiz_rag.genai, "Client", _FakeClient)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    repo = tmp_path / "repo"
    cache = repo / "docs" / "ai" / "cache" / "wiz_mcp_server"
    cache.mkdir(parents=True)
    manifest = {
        "entries": [
            {
                "id": "doc:sample_doc",
                "type": "win_doc",
                "category": "test",
                "status": "cached",
                "last_cached": "2026-02-01",
                "next_refresh_due": "2026-08-01",
            }
        ]
    }
    (cache / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    docs = cache / "docs"
    docs.mkdir()
    body = ("alpha " * 300) + "\nMANIFEST_META_NEEDLE\n" + ("beta " * 300)
    (docs / "sample_doc.md").write_text(body, encoding="utf-8")

    chroma_rel = ".vector_db/wiz_manifest_meta_test"
    _write_minimal_mcp_yaml(repo, chroma_rel=chroma_rel)

    rc = build_vector_db.main(
        [
            "--repo-root",
            str(repo),
            "--reset",
            "--no-ingest-ext",
        ]
    )
    assert rc == 0

    cfg = {"rag": {"chroma_path": chroma_rel}}
    out = query_wiz_knowledge(repo, "MANIFEST_META_NEEDLE", 20, cfg)
    assert out.get("ok") is True
    hit = next(
        (
            r
            for r in (out.get("results") or [])
            if (r.get("metadata") or {}).get("next_refresh_due") == "2026-08-01"
        ),
        None,
    )
    assert hit is not None, out
    md = hit.get("metadata") or {}
    assert md.get("last_cached") == "2026-02-01"
    assert md.get("status") == "cached"


def test_query_include_staleness(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(wiz_rag.genai, "Client", _FakeClient)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    repo = tmp_path / "repo2"
    cache = repo / "docs" / "ai" / "cache" / "wiz_mcp_server"
    cache.mkdir(parents=True)
    manifest = {
        "entries": [
            {
                "id": "doc:stale_doc",
                "type": "win_doc",
                "category": "test",
                "status": "cached",
                "last_cached": "2020-01-01",
                "next_refresh_due": "2000-01-01",
            }
        ]
    }
    (cache / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    docs = cache / "docs"
    docs.mkdir()
    (docs / "stale_doc.md").write_text("STALE_NEEDLE_TOKEN " + ("x" * 500), encoding="utf-8")

    chroma_rel = ".vector_db/wiz_stale_test"
    _write_minimal_mcp_yaml(repo, chroma_rel=chroma_rel)
    assert build_vector_db.main(["--repo-root", str(repo), "--reset", "--no-ingest-ext"]) == 0

    cfg = {"rag": {"chroma_path": chroma_rel}}
    raw = query_wiz_knowledge(repo, "STALE_NEEDLE_TOKEN", 5, cfg, include_staleness=True)
    assert raw.get("ok") is True
    results = raw.get("results") or []
    assert results and results[0].get("stale") is True
