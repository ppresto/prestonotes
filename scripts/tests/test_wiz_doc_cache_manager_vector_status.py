"""wiz_doc_cache_manager vector-index-status subcommand."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def _load_wdc():
    path = Path(__file__).resolve().parents[1] / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_vector_index_status_empty_repo(tmp_path: Path, capsys) -> None:
    wdc = _load_wdc()
    ns = argparse.Namespace(repo_root=tmp_path)
    wdc.cmd_vector_index_status(ns)
    out = capsys.readouterr().out
    assert "manifest_entries: 0" in out


def test_vector_index_status_with_stale_manifest(tmp_path: Path, capsys) -> None:
    wdc = _load_wdc()
    cache = tmp_path / "docs" / "ai" / "cache" / "wiz_mcp_server"
    cache.mkdir(parents=True)
    manifest = {
        "cache_version": "1.0",
        "entries": [
            {
                "id": "doc:x",
                "type": "win_doc",
                "status": "cached",
                "next_refresh_due": "2000-01-01",
            }
        ],
    }
    (cache / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    wdc.cmd_vector_index_status(argparse.Namespace(repo_root=tmp_path))
    out = capsys.readouterr().out
    assert "manifest_stale_or_due: 1" in out
