"""Tests for journey timeline + challenge lifecycle MCP tools (TASK-010)."""

from __future__ import annotations

import json
import re
import shutil
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


def test_write_journey_timeline_round_trip(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_journey_timeline

    body = "# Journey\n\nHello **world**.\n"
    out = write_journey_timeline("AcmeCo", body)
    assert json.loads(out).get("ok") is True

    timeline = (
        repo_ctx / "MyNotes" / "Customers" / "AcmeCo" / "AI_Insights" / "AcmeCo-Journey-Timeline.md"
    )
    assert timeline.is_file()
    assert timeline.read_text(encoding="utf-8") == body


def test_update_challenge_state_identified_to_in_progress(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    out1 = update_challenge_state("AcmeCo", "ch-001", "identified", "Call record ch-001")
    assert json.loads(out1).get("ok") is True

    out2 = update_challenge_state(
        "AcmeCo",
        "ch-001",
        "in_progress",
        "[Verified: 2026-04-19 | Jane | CISO] Customer agreed to POC scope.",
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
    assert "at" in entry["history"][0]
    assert entry["history"][1]["state"] == "in_progress"
    assert "POC" in entry["history"][1]["evidence"]
    for h in entry["history"]:
        assert re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", h["at"])


def test_update_challenge_state_rejects_illegal_jump(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import update_challenge_state

    update_challenge_state("Beta", "ch-002", "identified", "seen on discovery")
    with pytest.raises(ValueError, match="illegal|transition|allowed"):
        update_challenge_state("Beta", "ch-002", "resolved", "skip ahead")
