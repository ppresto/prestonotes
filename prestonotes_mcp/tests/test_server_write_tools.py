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


def test_write_doc_persists_ucn_recovery_latest_for_real_write(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_doc

    done = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
    mutations = '{"mutations":[{"section_key":"exec_account_summary","field_key":"risk","action":"append_with_history","new_value":"test"}]}'
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done):
        out = write_doc(
            "1a2b3c4d5e6f7g8h9i0j0k1l2m3n",
            mutations,
            dry_run=False,
            customer_name="Acme",
        )
    assert json.loads(out).get("exit_code") == 0

    recovery_dir = repo_ctx / "MyNotes" / "Customers" / "Acme" / "AI_Insights" / "ucn-recovery"
    mut_path = recovery_dir / "latest-mutations.json"
    state_path = recovery_dir / "latest-write-state.json"
    assert mut_path.is_file()
    assert state_path.is_file()
    cached = json.loads(mut_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert isinstance(cached, dict)
    assert state.get("status") == "write_succeeded_ledger_pending"
    assert state.get("mutations_path") == str(mut_path)
    assert state.get("doc_id") == "1a2b3c4d5e6f7g8h9i0j0k1l2m3n"


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


def test_append_ledger_row_marks_recovery_complete(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import append_ledger_row

    state_path = (
        repo_ctx
        / "MyNotes"
        / "Customers"
        / "Acme"
        / "AI_Insights"
        / "ucn-recovery"
        / "latest-write-state.json"
    )
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "customer_name": "Acme",
                "status": "write_succeeded_ledger_pending",
                "doc_id": "docid12345",
                "ledger_attempt_count": 0,
            }
        ),
        encoding="utf-8",
    )

    row = {
        "run_date": "2026-04-24",
        "call_type": "other",
        "account_health": "good",
        "sentiment": "neutral",
        "coverage": "baseline",
        "value_realized": "outcome",
        "next_critical_event": "next event",
        "wiz_license_evidence_quality": "low",
    }

    with patch("prestonotes_mcp.server._append_ledger_row", return_value=repo_ctx / "ledger.md"):
        out = append_ledger_row("Acme", json.dumps(row))
    data = json.loads(out)
    assert data.get("ok") is True

    new_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert new_state.get("status") == "complete"
    assert new_state.get("ledger_source") == "append_ledger_row"
    assert new_state.get("ledger_attempt_count") == 1


def test_recover_ledger_from_latest_uses_cached_mutations(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import recover_ledger_from_latest

    recovery_dir = repo_ctx / "MyNotes" / "Customers" / "Acme" / "AI_Insights" / "ucn-recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    (recovery_dir / "latest-mutations.json").write_text('{"mutations":[]}', encoding="utf-8")

    done = subprocess.CompletedProcess(args=[], returncode=0, stdout="ledger ok", stderr="")
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        out = recover_ledger_from_latest("Acme", "docid12345", dry_run=False)
    payload = json.loads(out)
    assert payload.get("ok") is True
    run_args = run.call_args[0]
    assert "ledger-append" in run_args
    assert "MyNotes/Customers/Acme/AI_Insights/ucn-recovery/latest-mutations.json" in run_args


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


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_sync_notes_runs_rsync_for_leading_underscore_customer(repo_ctx_gdrive: Path) -> None:
    from prestonotes_mcp.server import sync_notes

    gdrive_customer = repo_ctx_gdrive / "gdrive_mynotes" / "Customers" / "_TEST_CUSTOMER"
    gdrive_customer.mkdir(parents=True, exist_ok=True)
    (gdrive_customer / "note.txt").write_text("from-drive-underscore", encoding="utf-8")

    out = sync_notes("_TEST_CUSTOMER")
    data = json.loads(out)
    assert data.get("exit_code") == 0, data.get("output")
    local = repo_ctx_gdrive / "MyNotes" / "Customers" / "_TEST_CUSTOMER" / "note.txt"
    assert local.is_file()
    assert local.read_text(encoding="utf-8") == "from-drive-underscore"


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_sync_notes_deletes_local_only_transcripts_and_call_records_when_absent_on_gdrive(
    repo_ctx_gdrive: Path,
) -> None:
    """Pull is a normal mirror: --delete removes per-call files that exist only under MyNotes.

    E2E re-seeds from ``tests/fixtures/...`` via ``e2e-test-customer-materialize.py`` / prep-v1.
    """
    from prestonotes_mcp.server import sync_notes

    gdrive_customer = repo_ctx_gdrive / "gdrive_mynotes" / "Customers" / "_TEST_CUSTOMER"
    gdrive_customer.mkdir(parents=True, exist_ok=True)
    (gdrive_customer / "note.txt").write_text("from-drive-underscore", encoding="utf-8")

    local_customer = repo_ctx_gdrive / "MyNotes" / "Customers" / "_TEST_CUSTOMER"
    transcripts = local_customer / "Transcripts"
    transcripts.mkdir(parents=True, exist_ok=True)
    tx = transcripts / "2026-04-20-fixture-call.txt"
    tx.write_text("fixture transcript\n", encoding="utf-8")

    cr = local_customer / "call-records"
    cr.mkdir(parents=True, exist_ok=True)
    rec = cr / "2026-04-20-fixture-call.json"
    rec.write_text('{"call_id":"2026-04-20-fixture-call"}\n', encoding="utf-8")

    out = sync_notes("_TEST_CUSTOMER")
    data = json.loads(out)
    assert data.get("exit_code") == 0, data.get("output")

    assert not tx.is_file()
    assert not rec.is_file()
    assert (local_customer / "note.txt").read_text(encoding="utf-8") == "from-drive-underscore"
