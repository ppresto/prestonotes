"""Offline materialize script (dry-run only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import materialize_wiz_mcp_docs as mat  # noqa: E402


@pytest.fixture()
def tiny_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "r"
    cache = repo / "docs" / "ai" / "cache" / "wiz_mcp_server"
    cache.mkdir(parents=True)
    idx = {"categories": {"test": ["alpha-doc", "beta-doc"]}}
    (cache / "win_apis_doc_index.json").write_text(json.dumps(idx), encoding="utf-8")
    (cache / "manifest.json").write_text(
        json.dumps({"entries": [], "cache_version": "1.0"}),
        encoding="utf-8",
    )
    return repo


def test_run_materialize_dry_run_counts(tiny_repo: Path) -> None:
    rc = mat.run_materialize(
        repo=tiny_repo,
        dry_run=True,
        min_age_days=7,
        force=False,
        delay_seconds=0.0,
        max_docs=2,
        doc_name_filter=None,
        dotenv=None,
    )
    assert rc == 0
