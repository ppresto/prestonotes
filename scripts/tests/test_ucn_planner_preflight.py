"""Tests for scripts/ucn-planner-preflight.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "ucn-planner-preflight.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("ucn_planner_preflight", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = _load_mod()


def _partial_coverage_decisions() -> list[dict[str, str]]:
    return [
        {
            "target": "exec_account_summary.top_goal",
            "action": "skip",
            "skip_reason": "same_as_current_entry",
        },
        {
            "target": "exec_account_summary.risk",
            "action": "skip",
            "skip_reason": "same_as_current_entry",
        },
        {"target": "exec_account_summary.upsell_path", "action": "mutate"},
        {
            "target": "use_cases.free_text",
            "action": "skip",
            "skip_reason": "no_in_scope_transcript_signal",
        },
        {
            "target": "workflows.free_text",
            "action": "skip",
            "skip_reason": "no_in_scope_transcript_signal",
        },
        {"target": "daily_activity_logs.free_text", "action": "mutate"},
    ]


def _base_payload() -> dict:
    return {
        "planner_contract": {
            "ucn_mode": "partial",
            "coverage": {
                "decisions": _partial_coverage_decisions(),
            },
            "dal": {
                "expected_missing_count": 2,
                "expected_missing_keys": [
                    "2026-04-11:shift-left-secrets-ci",
                    "2026-04-21:qbr-and-monthly-sync",
                ],
                "skips": [],
            },
            "deal_stage": {
                "expected_skus": ["cloud"],
                "no_change_with_reason": [],
            },
        },
        "mutations": [
            {
                "section_key": "daily_activity_logs",
                "field_key": "free_text",
                "action": "prepend_daily_activity_ai_summary",
                "heading_line": "2026-04-11 - Shift left secrets CI",
            },
            {
                "section_key": "daily_activity_logs",
                "field_key": "free_text",
                "action": "prepend_daily_activity_ai_summary",
                "heading_line": "2026-04-21 — QBR and monthly sync",
            },
            {
                "section_key": "exec_account_summary",
                "field_key": "upsell_path",
                "action": "append_with_history",
                "new_value": "Wiz Cloud - expansion motion with POV on 2026-04-21",
            },
        ],
    }


def test_contract_passes_with_matching_dal_and_deal_stage() -> None:
    ok, codes, metrics = m.validate_payload(_base_payload())
    assert ok is True
    assert codes == []
    assert metrics["coverage"]["ucn_mode"] == "partial"
    assert metrics["dal"]["required_prepends"] == 2
    assert metrics["deal_stage"]["auto_skus"] == ["cloud"]


def test_dal_parity_failure_when_missing_prepend() -> None:
    payload = _base_payload()
    payload["mutations"] = payload["mutations"][:2]
    payload["mutations"].pop(0)
    ok, codes, _ = m.validate_payload(payload)
    assert ok is False
    assert any(code.startswith("dal_parity_failed") for code in codes)


def test_deal_stage_trigger_missing_without_auto_or_explicit() -> None:
    payload = _base_payload()
    payload["mutations"] = [
        m for m in payload["mutations"] if m.get("section_key") != "exec_account_summary"
    ]
    coverage = payload["planner_contract"]["coverage"]["decisions"]  # type: ignore[index]
    for row in coverage:
        if row.get("target") == "exec_account_summary.upsell_path":
            row["action"] = "skip"
            row["skip_reason"] = "same_as_current_entry"
    ok, codes, _ = m.validate_payload(payload)
    assert ok is False
    assert "deal_stage_trigger_missing:cloud" in codes


def test_no_change_with_reason_allows_expected_sku() -> None:
    payload = _base_payload()
    payload["planner_contract"]["deal_stage"]["no_change_with_reason"] = [  # type: ignore[index]
        {"sku": "cloud", "reason": "already win"}
    ]
    payload["mutations"] = [
        m for m in payload["mutations"] if m.get("section_key") != "exec_account_summary"
    ]
    coverage = payload["planner_contract"]["coverage"]["decisions"]  # type: ignore[index]
    for row in coverage:
        if row.get("target") == "exec_account_summary.upsell_path":
            row["action"] = "skip"
            row["skip_reason"] = "same_as_current_entry"
    ok, codes, metrics = m.validate_payload(payload)
    assert ok is True
    assert codes == []
    assert metrics["deal_stage"]["no_change_skus"] == ["cloud"]


def test_coverage_missing_required_targets_for_full_mode() -> None:
    payload = _base_payload()
    ok, codes, metrics = m.validate_payload(payload, ucn_mode="full")
    assert ok is False
    assert any(code.startswith("coverage_decisions_missing_required:") for code in codes)
    assert metrics["coverage"]["ucn_mode"] == "full"


def test_coverage_skip_reason_invalid() -> None:
    payload = _base_payload()
    coverage = payload["planner_contract"]["coverage"]["decisions"]  # type: ignore[index]
    coverage[0]["skip_reason"] = "maybe"
    ok, codes, _ = m.validate_payload(payload)
    assert ok is False
    assert "coverage_skip_reason_invalid:exec_account_summary.top_goal:maybe" in codes


def test_coverage_requires_explicit_statement_for_exec_buyer() -> None:
    payload = _base_payload()
    payload["planner_contract"]["coverage"]["decisions"].append(  # type: ignore[index]
        {"target": "account_motion_metadata.exec_buyer", "action": "mutate"}
    )
    payload["mutations"].append(  # type: ignore[index]
        {
            "section_key": "account_motion_metadata",
            "field_key": "exec_buyer",
            "action": "update_in_place",
            "new_value": "Pat VP Security",
        }
    )
    ok, codes, _ = m.validate_payload(payload)
    assert ok is False
    assert "coverage_explicit_statement_required:account_motion_metadata.exec_buyer" in codes


def test_coverage_rejects_non_numeric_account_metadata_value() -> None:
    payload = _base_payload()
    payload["planner_contract"]["coverage"]["decisions"].append(  # type: ignore[index]
        {"target": "account_motion_metadata.sensor_coverage_pct", "action": "mutate"}
    )
    payload["mutations"].append(  # type: ignore[index]
        {
            "section_key": "account_motion_metadata",
            "field_key": "sensor_coverage_pct",
            "action": "update_in_place",
            "new_value": "high",
        }
    )
    ok, codes, _ = m.validate_payload(payload)
    assert ok is False
    assert any(
        code.startswith(
            "coverage_numeric_value_invalid:account_motion_metadata.sensor_coverage_pct:"
        )
        for code in codes
    )


def test_main_json_output_success(tmp_path: Path, capsys) -> None:
    payload = _base_payload()
    path = tmp_path / "mutations.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    # call through CLI entry behavior
    import sys

    prev = sys.argv
    try:
        sys.argv = ["ucn-planner-preflight.py", "--mutations", str(path), "--json-output"]
        ret = m.main()
    finally:
        sys.argv = prev
    out = capsys.readouterr().out
    data = json.loads(out)
    assert ret == 0
    assert data["ok"] is True
