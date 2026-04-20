"""Tests for write/sync MCP tools (TASK-003)."""

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


@pytest.fixture
def repo_ctx_gdrive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Minimal Drive mirror + rsync script so sync_notes can run (TASK-006)."""
    gdrive = tmp_path / "gdrive_mynotes"
    (gdrive / "Customers" / "Acme").mkdir(parents=True)
    (gdrive / "Customers" / "Acme" / "note.txt").write_text("from-drive", encoding="utf-8")
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(gdrive))
    (tmp_path / "prestonotes_mcp").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
        tmp_path / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
    )
    cfg = load_config(tmp_path)
    init_ctx(tmp_path, cfg)
    (tmp_path / "scripts").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "scripts" / "rsync-gdrive-notes.sh",
        tmp_path / "scripts" / "rsync-gdrive-notes.sh",
    )
    return tmp_path


def test_write_doc_dry_run_mocks_subprocess(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_doc

    done = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        out = write_doc("1a2b3c4d5e6f7g8h9i0j0k1l2m3n", "{}", dry_run=True)
    run.assert_called_once()
    call = run.call_args[0]
    assert "prestonotes_gdoc/update-gdoc-customer-notes.py" in call[0]
    assert "--dry-run" in call
    data = json.loads(out)
    assert data.get("exit_code") == 0


def test_append_ledger_mocks_subprocess(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import append_ledger

    applied = repo_ctx / "tmp" / "applied.json"
    applied.parent.mkdir(parents=True)
    applied.write_text('{"ok": true}', encoding="utf-8")

    done = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        append_ledger("Acme", "docid12345", "tmp/applied.json")
    run.assert_called_once()
    args = run.call_args[0]
    assert "ledger-append" in args


def test_bootstrap_customer_dry_run_mocks_subprocess(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import bootstrap_customer

    done = subprocess.CompletedProcess(args=[], returncode=0, stdout="dry", stderr="")
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        out = bootstrap_customer("Acme", dry_run=True)
    run.assert_called_once()
    assert "--dry-run" in run.call_args[0]
    assert json.loads(out)["exit_code"] == 0


def test_log_run_appends_to_audit_file(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import log_run

    (repo_ctx / "MyNotes" / "Customers" / "Acme").mkdir(parents=True)
    raw = log_run("Acme", "test note")
    data = json.loads(raw)
    assert data.get("ok") is True
    p = repo_ctx / "MyNotes" / "Customers" / "Acme" / "pnotes_agent_log.md"
    assert p.is_file()
    assert "test note" in p.read_text(encoding="utf-8")


def test_sync_notes_missing_script_returns_json(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import sync_notes

    out = sync_notes(None)
    data = json.loads(out)
    assert "error" in data or "exit_code" in data


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_sync_notes_runs_rsync_for_customer(repo_ctx_gdrive: Path) -> None:
    from prestonotes_mcp.server import sync_notes

    out = sync_notes("Acme")
    data = json.loads(out)
    assert data.get("exit_code") == 0, data.get("output")
    local = repo_ctx_gdrive / "MyNotes" / "Customers" / "Acme" / "note.txt"
    assert local.is_file()
    assert local.read_text(encoding="utf-8") == "from-drive"
