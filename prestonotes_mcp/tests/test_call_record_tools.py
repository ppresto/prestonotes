"""Tests for call record MCP tools (TASK-004)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from prestonotes_mcp.config import load_config
from prestonotes_mcp.runtime import init_ctx

REPO_ROOT = Path(__file__).resolve().parents[2]

MINIMAL_RECORD = {
    "call_id": "2026-04-15-discovery-1",
    "date": "2026-04-15",
    "call_type": "discovery",
    "call_number_in_sequence": 1,
    "participants": [{"name": "Jane Smith", "role": "CISO", "company": "Acme", "is_new": True}],
    "summary_one_liner": "First discovery call.",
    "key_topics": ["CSPM"],
    "challenges_mentioned": [
        {"id": "ch-001", "description": "No unified visibility", "status": "identified"}
    ],
    "products_discussed": ["Wiz Cloud"],
    "action_items": [{"owner": "SE", "action": "Send overview", "due": "2026-04-22"}],
    "sentiment": "positive",
    "deltas_from_prior_call": [],
    "verbatim_quotes": [{"speaker": "Jane Smith", "quote": "We need visibility."}],
    "raw_transcript_ref": "2026-04-15-discovery-call.txt",
    "extraction_date": "2026-04-16",
    "extraction_confidence": "high",
}


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


def test_write_read_call_records_round_trip(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_call_records, write_call_record

    payload = json.dumps(MINIMAL_RECORD)
    out = write_call_record("AcmeCo", "2026-04-15-discovery-1", payload)
    assert json.loads(out).get("ok") is True

    raw = read_call_records("AcmeCo")
    data = json.loads(raw)
    assert data["count"] == 1
    assert data["records"][0]["call_id"] == "2026-04-15-discovery-1"
    assert data["records"][0]["summary_one_liner"] == "First discovery call."


def test_read_call_records_filters(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_call_records, write_call_record

    r1 = {**MINIMAL_RECORD, "call_id": "2026-01-01-discovery-1", "date": "2026-01-01"}
    r2 = {
        **MINIMAL_RECORD,
        "call_id": "2026-06-01-campaign-1",
        "date": "2026-06-01",
        "call_type": "campaign",
        "call_number_in_sequence": 2,
    }
    write_call_record("Beta", "2026-01-01-discovery-1", json.dumps(r1))
    write_call_record("Beta", "2026-06-01-campaign-1", json.dumps(r2))

    all_recs = json.loads(read_call_records("Beta"))
    assert all_recs["count"] == 2

    since = json.loads(read_call_records("Beta", since_date="2026-06-01"))
    assert since["count"] == 1
    assert since["records"][0]["call_type"] == "campaign"

    only_disc = json.loads(read_call_records("Beta", call_type="discovery"))
    assert only_disc["count"] == 1


def test_write_call_record_rejects_bad_call_id(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_call_record

    with pytest.raises(ValueError, match="path segments|call_id"):
        write_call_record("AcmeCo", "../evil", json.dumps(MINIMAL_RECORD))


def test_write_call_record_schema_validation(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_call_record

    bad = {**MINIMAL_RECORD}
    del bad["sentiment"]
    with pytest.raises(ValueError, match="schema|sentiment"):
        write_call_record("AcmeCo", "2026-04-15-discovery-1", json.dumps(bad))
