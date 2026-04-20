"""Tests for read-only MCP tools (TASK-002)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from prestonotes_mcp.config import load_config
from prestonotes_mcp.runtime import init_ctx

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def repo_ctx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    (tmp_path / "prestonotes_mcp").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
        tmp_path / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
    )
    cfg = load_config(tmp_path)
    init_ctx(tmp_path, cfg)
    return tmp_path


def test_check_google_auth_returns_json_ok(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import check_google_auth

    fake = subprocess.CompletedProcess(
        args=["gcloud", "auth", "print-access-token"],
        returncode=0,
        stdout="ya29.fake-token\n",
        stderr="",
    )
    with patch("prestonotes_mcp.server.subprocess.run", return_value=fake):
        raw = check_google_auth()
    data = json.loads(raw)
    assert data.get("ok") is True
    assert "message" in data


def test_read_doc_uses_uv_script_mock(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_doc

    done = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout='{"ok": true, "sections": []}',
        stderr="",
    )

    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        out = read_doc("1a2b3c4d5e6f7g8h9i0j", include_internal=True)
    run.assert_called_once()
    assert "sections" in out or "ok" in out


def test_no_run_pipeline_tool() -> None:
    """v2 does not expose deprecated run_pipeline (run-main-task). Write tools are TASK-003."""
    import prestonotes_mcp.server as server

    assert not hasattr(server, "run_pipeline")


def test_main_does_not_block(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from prestonotes_mcp import server

    (tmp_path / "prestonotes_mcp").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
        tmp_path / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
    )
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))

    with patch.object(server.mcp, "run", lambda **k: None):
        server.main()


def test_read_transcripts_prefers_per_call_files(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_transcripts

    base = repo_ctx / "MyNotes" / "Customers" / "Acme" / "Transcripts"
    base.mkdir(parents=True)
    old = base / "_MASTER_TRANSCRIPT_Acme.txt"
    new = base / "2026-01-10-discovery.txt"
    old.write_text("master", encoding="utf-8")
    new.write_text("per-call", encoding="utf-8")

    raw = read_transcripts("Acme", limit=5)
    data = json.loads(raw)
    assert "transcripts" in data
    names = [t["file"] for t in data["transcripts"]]
    assert "2026-01-10-discovery.txt" in names
    assert "_MASTER_TRANSCRIPT_Acme.txt" not in names
