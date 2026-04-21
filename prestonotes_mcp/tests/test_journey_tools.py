"""Tests for challenge lifecycle MCP tools (TASK-010, TASK-047, TASK-048)."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def _today() -> "datetime":
    return datetime.now(timezone.utc)


def _iso(d) -> str:
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def test_update_challenge_state_identified_to_in_progress(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    out1 = update_challenge_state(
        "AcmeCo",
        "ch-001",
        "identified",
        "Call record ch-001",
        transitioned_at="2026-04-18",
    )
    assert json.loads(out1).get("ok") is True

    out2 = update_challenge_state(
        "AcmeCo",
        "ch-001",
        "in_progress",
        "[Verified: 2026-04-19 | Jane | CISO] Customer agreed to POC scope.",
        transitioned_at="2026-04-19",
    )
    assert json.loads(out2).get("ok") is True

    jpath = (
        repo_ctx / "MyNotes" / "Customers" / "AcmeCo" / "AI_Insights" / "challenge-lifecycle.json"
    )
    data = json.loads(jpath.read_text(encoding="utf-8"))
    entry = data["ch-001"]
    assert entry["current_state"] == "in_progress"
    assert len(entry["history"]) == 2
    assert entry["history"][0]["state"] == "identified"
    assert entry["history"][0]["evidence"] == "Call record ch-001"
    assert entry["history"][0]["at"] == "2026-04-18"
    assert entry["history"][1]["state"] == "in_progress"
    assert "POC" in entry["history"][1]["evidence"]
    assert entry["history"][1]["at"] == "2026-04-19"
    for h in entry["history"]:
        assert re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", h["at"])


def test_update_challenge_state_rejects_illegal_jump(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    update_challenge_state(
        "Beta", "ch-002", "identified", "seen on discovery", transitioned_at="2026-04-10"
    )
    with pytest.raises(ValueError, match="illegal|transition|allowed"):
        update_challenge_state(
            "Beta", "ch-002", "resolved", "skip ahead", transitioned_at="2026-04-11"
        )


def test_read_challenge_lifecycle_missing_file(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_challenge_lifecycle

    out = read_challenge_lifecycle("Ghost")
    payload = json.loads(out)
    assert payload.get("error") == "file not found"
    assert "path" in payload
    assert payload["path"].endswith("challenge-lifecycle.json")


def test_read_challenge_lifecycle_seeded_round_trip(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import read_challenge_lifecycle, update_challenge_state

    update_challenge_state(
        "Gamma", "ch-100", "identified", "Initial discovery", transitioned_at="2026-04-18"
    )
    update_challenge_state(
        "Gamma",
        "ch-100",
        "in_progress",
        "[Verified: 2026-04-20 | Alex | Eng] POC scoped",
        transitioned_at="2026-04-20",
    )

    out = read_challenge_lifecycle("Gamma")
    payload = json.loads(out)
    assert "error" not in payload
    assert payload.get("path", "").endswith("challenge-lifecycle.json")

    data = payload["data"]
    assert isinstance(data, dict)
    entry = data["ch-100"]
    assert entry["current_state"] == "in_progress"
    assert len(entry["history"]) == 2
    assert entry["history"][0]["state"] == "identified"
    assert entry["history"][1]["state"] == "in_progress"
    for h in entry["history"]:
        assert re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", h["at"])
        assert isinstance(h["evidence"], str) and h["evidence"]


# ---------------------------------------------------------------------------
# TASK-048 — write-side discipline validations
# ---------------------------------------------------------------------------


def _lifecycle_path(repo_ctx: Path, customer: str) -> Path:
    return (
        repo_ctx / "MyNotes" / "Customers" / customer / "AI_Insights" / "challenge-lifecycle.json"
    )


def test_update_challenge_state_rejects_future_at(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    future = (_today().date() + timedelta(days=2)).isoformat()
    out = update_challenge_state(
        "Delta",
        "ch-future",
        "identified",
        "discovery call",
        transitioned_at=future,
    )
    payload = json.loads(out)
    assert payload.get("ok") is False
    assert payload.get("error") == "transitioned_at in future"
    assert payload.get("field") == "transitioned_at"
    assert payload.get("value") == future
    assert "expected" in payload
    assert not _lifecycle_path(repo_ctx, "Delta").exists()


def test_update_challenge_state_rejects_regression(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    out_seed = update_challenge_state(
        "Epsilon",
        "ch-regress",
        "identified",
        "seen on 4/10 call",
        transitioned_at="2026-04-10",
    )
    assert json.loads(out_seed).get("ok") is True

    out = update_challenge_state(
        "Epsilon",
        "ch-regress",
        "in_progress",
        "older call evidence",
        transitioned_at="2026-04-05",
    )
    payload = json.loads(out)
    assert payload.get("ok") is False
    assert payload.get("error") == "transitioned_at regresses history"
    assert payload.get("field") == "transitioned_at"
    assert payload.get("value") == "2026-04-05"
    assert payload.get("latest_existing") == "2026-04-10"

    data = json.loads(_lifecycle_path(repo_ctx, "Epsilon").read_text(encoding="utf-8"))
    assert len(data["ch-regress"]["history"]) == 1


def test_update_challenge_state_accepts_month_old_at(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    old = (_today().date() - timedelta(days=45)).isoformat()
    out = update_challenge_state(
        "Zeta",
        "ch-month-old",
        "identified",
        "older transcript, catch-up ingest",
        transitioned_at=old,
    )
    payload = json.loads(out)
    assert payload.get("ok") is True

    data = json.loads(_lifecycle_path(repo_ctx, "Zeta").read_text(encoding="utf-8"))
    hist = data["ch-month-old"]["history"]
    assert len(hist) == 1
    assert hist[0]["at"] == old


def test_update_challenge_state_accepts_year_old_at(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    old = (_today().date() - timedelta(days=400)).isoformat()
    out = update_challenge_state(
        "Eta",
        "ch-year-old",
        "identified",
        "archived meeting evidence",
        transitioned_at=old,
    )
    payload = json.loads(out)
    assert payload.get("ok") is True

    data = json.loads(_lifecycle_path(repo_ctx, "Eta").read_text(encoding="utf-8"))
    hist = data["ch-year-old"]["history"]
    assert len(hist) == 1
    assert hist[0]["at"] == old


def test_update_challenge_state_rejects_forbidden_evidence(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    out = update_challenge_state(
        "Theta",
        "ch-vocab",
        "identified",
        "UCN round-1: challenge rows added to Notes doc Challenge Tracker.",
        transitioned_at="2026-04-15",
    )
    payload = json.loads(out)
    assert payload.get("ok") is False
    assert payload.get("error") == "evidence contains forbidden harness vocabulary"
    assert payload.get("field") == "evidence"
    # "UCN round" wins in declaration order over "round 1" and "challenge rows added".
    assert payload.get("matched") == "UCN round"
    assert not _lifecycle_path(repo_ctx, "Theta").exists()

    out2 = update_challenge_state(
        "Theta",
        "ch-vocab-2",
        "identified",
        "E2E harness notes from the fixture",
        transitioned_at="2026-04-15",
    )
    payload2 = json.loads(out2)
    assert payload2.get("ok") is False
    # "E2E" appears before "harness" and "fixture" in FORBIDDEN_EVIDENCE_TERMS.
    assert payload2.get("matched") == "E2E"


def test_update_challenge_state_requires_transitioned_at(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    with pytest.raises(ValueError, match="transitioned_at"):
        update_challenge_state(
            "Iota",
            "ch-missing-at",
            "identified",
            "evidence with no call date",
            transitioned_at="",
        )

    assert not _lifecycle_path(repo_ctx, "Iota").exists()
