"""Tests for challenge_lifecycle_parity (GDoc ↔ lifecycle journal)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def parity_mod():
    import importlib.util

    path = REPO_ROOT / "prestonotes_gdoc" / "challenge_lifecycle_parity.py"
    spec = importlib.util.spec_from_file_location("_parity", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parity_warns_when_lifecycle_exists_but_no_markers(tmp_path: Path, parity_mod) -> None:
    cust = "ParityCust"
    (tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights").mkdir(parents=True)
    life = {"a": {"current_state": "identified", "history": []}}
    (
        tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights" / "challenge-lifecycle.json"
    ).write_text(json.dumps(life), encoding="utf-8")
    rows = [SimpleNamespace(challenge="Something", notes_references="no anchors here")]
    warns, errs = parity_mod.check_tracker_lifecycle_parity(tmp_path, cust, rows)
    assert warns and not errs
    assert "LIFECYCLE_PARITY" in warns[0]


def test_parity_errors_when_markers_partial(tmp_path: Path, parity_mod) -> None:
    cust = "ParityCust2"
    (tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights").mkdir(parents=True)
    life = {
        "foo": {"current_state": "in_progress", "history": []},
        "bar": {"current_state": "identified", "history": []},
    }
    (
        tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights" / "challenge-lifecycle.json"
    ).write_text(json.dumps(life), encoding="utf-8")
    rows = [SimpleNamespace(challenge="x [lifecycle_id:foo]", notes_references="")]
    warns, errs = parity_mod.check_tracker_lifecycle_parity(tmp_path, cust, rows)
    assert not warns
    assert len(errs) == 1 and "bar" in errs[0]


def test_parity_ok_when_all_markers(tmp_path: Path, parity_mod) -> None:
    cust = "ParityCust3"
    (tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights").mkdir(parents=True)
    life = {"foo": {"current_state": "in_progress", "history": []}}
    (
        tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights" / "challenge-lifecycle.json"
    ).write_text(json.dumps(life), encoding="utf-8")
    rows = [SimpleNamespace(challenge="t", notes_references="[lifecycle_id:foo] extra")]
    warns, errs = parity_mod.check_tracker_lifecycle_parity(tmp_path, cust, rows)
    assert not warns and not errs


def test_parity_accepts_legacy_bare_lifecycle_anchor(tmp_path: Path, parity_mod) -> None:
    """TASK-052: the 22:10 E2E row used bare ``lifecycle:ch-soc-budget``
    instead of the canonical ``[lifecycle_id:ch-soc-budget]``. Reconciler
    MARKER_RE must accept both so row-status rewrite can heal older rows.
    """
    cust = "ParityCust4"
    (tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights").mkdir(parents=True)
    life = {"ch-soc-budget": {"current_state": "stalled", "history": []}}
    (
        tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights" / "challenge-lifecycle.json"
    ).write_text(json.dumps(life), encoding="utf-8")
    rows = [
        SimpleNamespace(
            challenge="Splunk CDR — SOC budget blocks purchase",
            notes_references="lifecycle:ch-soc-budget | evidence in procurement and QBR calls",
        )
    ]
    warns, errs = parity_mod.check_tracker_lifecycle_parity(tmp_path, cust, rows)
    assert not warns and not errs, (warns, errs)
    found = parity_mod.markers_in_tracker(rows)
    assert "ch-soc-budget" in found


def test_missing_anchor_auto_inserted(tmp_path: Path, parity_mod) -> None:
    """TASK-052: auto-insert canonical anchors when id is present without marker."""
    cust = "ParityCust5"
    (tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights").mkdir(parents=True)
    life = {"ch-soc-budget": {"current_state": "stalled", "history": []}}
    (
        tmp_path / "MyNotes" / "Customers" / cust / "AI_Insights" / "challenge-lifecycle.json"
    ).write_text(json.dumps(life), encoding="utf-8")
    rows = [
        SimpleNamespace(
            challenge="ch-soc-budget procurement blocker",
            notes_references="mentioned in this week's readout",
        )
    ]
    inserted = parity_mod.auto_insert_missing_lifecycle_anchors(tmp_path, cust, rows)
    assert inserted
    assert "[lifecycle_id:ch-soc-budget]" in rows[0].notes_references
    warns, errs = parity_mod.check_tracker_lifecycle_parity(tmp_path, cust, rows)
    assert not warns and not errs


def test_write_doc_forwards_customer_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import patch

    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    (tmp_path / "prestonotes_mcp").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
        tmp_path / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
    )
    from prestonotes_mcp.config import load_config
    from prestonotes_mcp.runtime import init_ctx

    init_ctx(tmp_path, load_config(tmp_path))

    from prestonotes_mcp.server import write_doc

    done = __import__("subprocess").CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
    with patch("prestonotes_mcp.server.run_uv_script", return_value=done) as run:
        write_doc("docid", "{}", dry_run=True, customer_name="AcmeCo")
    pos = run.call_args[0]
    assert "--customer-name" in pos
    assert "AcmeCo" in pos
