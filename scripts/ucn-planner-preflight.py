#!/usr/bin/env python3
"""Preflight validator for UCN mutation plans.

Contracts enforced:
- TASK-072: DAL parity + Deal Stage trigger path.
- TASK-073: pre-write section coverage via planner decisions (always **full** matrix; see
  ``_required_targets_full()`` — ``partial`` mode is no longer used).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

COMMERCIAL_SKUS = {"cloud", "sensor", "defend", "code"}
_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?(%|h|hrs|hours|days)?$", re.IGNORECASE)

# Skip reasons: preflight enforces that every matrix target was *reviewed* (``mutate`` or ``skip``).
# A ``skip`` with one of these reasons is success — it records “checked, no change” and avoids
# fabricating GDoc/ledger lines. Prefer specific reasons; ``no_in_scope_transcript_signal`` is the
# usual label when the active corpus has no defensible signal for that section.
ALLOWED_SKIP_REASONS = {
    "no_in_scope_transcript_signal",
    "same_as_current_entry",
    "evidence_below_confidence_threshold",
    "section_off_by_opt_out",
    "empty_transcript",
}

# TASK-073 canonical planner-governed targets. ``required_in_ucn_partial`` is legacy (unused);
# :func:`_required_targets_full` is the only required set used for validation.
TARGET_MATRIX: dict[str, dict[str, Any]] = {
    # Account Summary tab
    "exec_account_summary.top_goal": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {
            "append_with_history",
            "set_if_empty",
            "replace_field_entries",
        },
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "exec_account_summary.risk": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {
            "append_with_history",
            "set_if_empty",
            "replace_field_entries",
        },
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "exec_account_summary.upsell_path": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {
            "append_with_history",
            "set_if_empty",
            "update_in_place",
            "replace_field_entries",
        },
        "evidence_rule": "deal_stage_trigger_path",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "challenge_tracker": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_table_row", "update_table_row"},
        "evidence_rule": "challenge_row_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "company_overview.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"append_with_history"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "contacts.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"append_with_history", "replace_field_entries"},
        "evidence_rule": "named_contact_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "org_structure.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"append_with_history"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.csp_regions": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place", "replace_field_entries"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.platforms": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.idp_sso": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place", "replace_field_entries"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.devops_vcs": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.security_tools": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.aspm_tools": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.ticketing": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.languages": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
        "evidence_rule": "tool_evidence",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.sizing": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place", "replace_field_entries"},
        "evidence_rule": "numeric_or_capacity_signal",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "cloud_environment.archive": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"append_with_history"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "use_cases.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {"append_with_history", "replace_field_entries"},
        "evidence_rule": "requirements_signal",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "workflows.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {"append_with_history", "replace_field_entries"},
        "evidence_rule": "workflow_signal",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "accomplishments.free_text": {
        "tab": "account_summary",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"append_with_history"},
        "evidence_rule": "resolved_outcome_signal",
        "validator_fail_code": "coverage_mutation_missing",
    },
    # Daily Activity tab
    "daily_activity_logs.free_text": {
        "tab": "daily_activity",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": True,
        "allowed_mutation_actions": {"prepend_daily_activity_ai_summary"},
        "evidence_rule": "dal_parity",
        "validator_fail_code": "coverage_mutation_missing",
    },
    # Account Metadata tab
    "account_motion_metadata.exec_buyer": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "explicit_statement_required",
        "validator_fail_code": "coverage_explicit_statement_required",
    },
    "account_motion_metadata.champion": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "explicit_statement_required",
        "validator_fail_code": "coverage_explicit_statement_required",
    },
    "account_motion_metadata.technical_owner": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "standard",
        "validator_fail_code": "coverage_mutation_missing",
    },
    "account_motion_metadata.sensor_coverage_pct": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "numeric_value_required",
        "validator_fail_code": "coverage_numeric_value_invalid",
    },
    "account_motion_metadata.critical_issues_open": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "numeric_value_required",
        "validator_fail_code": "coverage_numeric_value_invalid",
    },
    "account_motion_metadata.mttr_days": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "numeric_value_required",
        "validator_fail_code": "coverage_numeric_value_invalid",
    },
    "account_motion_metadata.monthly_reporting_hours": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"set_if_empty", "update_in_place"},
        "evidence_rule": "numeric_value_required",
        "validator_fail_code": "coverage_numeric_value_invalid",
    },
    "deal_stage_tracker": {
        "tab": "account_metadata",
        "required_in_ucn_full": True,
        "required_in_ucn_partial": False,
        "allowed_mutation_actions": {"add_table_row", "update_table_row"},
        "evidence_rule": "deal_stage_trigger_path",
        "validator_fail_code": "coverage_mutation_missing",
    },
}

STRICT_EXPLICIT_STATEMENT_TARGETS = {
    "account_motion_metadata.exec_buyer",
    "account_motion_metadata.champion",
}
NUMERIC_VALUE_TARGETS = {
    "account_motion_metadata.sensor_coverage_pct",
    "account_motion_metadata.critical_issues_open",
    "account_motion_metadata.mttr_days",
    "account_motion_metadata.monthly_reporting_hours",
}


def _normalize_heading_key(heading_line: str) -> str:
    text = (heading_line or "").strip().lower()
    if not text:
        return ""
    text = text.lstrip("#").strip()
    m = _DATE_RE.search(text)
    if not m:
        return ""
    date = m.group(1)
    tail = text[m.end() :].strip(" -:|")
    slug = re.sub(r"[^a-z0-9]+", "-", tail).strip("-")
    return f"{date}:{slug}" if slug else date


def _sku_tokens_in_text(text: str) -> set[str]:
    lower = (text or "").lower()
    hits: set[str] = set()
    for sku in COMMERCIAL_SKUS:
        if f"wiz {sku}" in lower or re.search(rf"\b{re.escape(sku)}\b", lower):
            hits.add(sku)
    return hits


def _load_mutations(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        data = payload.get("mutations", [])
        if isinstance(data, list):
            return [m for m in data if isinstance(m, dict)]
        return []
    if isinstance(payload, list):
        return [m for m in payload if isinstance(m, dict)]
    return []


def _required_targets_full() -> set[str]:
    """Planner-governed targets for every UCN preflight run (``required_in_ucn_full``)."""
    return {
        target for target, cfg in TARGET_MATRIX.items() if bool(cfg.get("required_in_ucn_full"))
    }


def _normalize_coverage_decisions(raw: Any) -> tuple[dict[str, dict[str, Any]], list[str]]:
    codes: list[str] = []
    decisions: dict[str, dict[str, Any]] = {}
    if isinstance(raw, dict):
        items = raw.items()
        for target, value in items:
            if isinstance(value, dict):
                decision = dict(value)
            else:
                decision = {"action": value}
            decision["target"] = str(target)
            decisions[str(target)] = decision
        return decisions, codes

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                codes.append("coverage_decisions_invalid_entry")
                continue
            target = str(item.get("target") or "").strip()
            if not target:
                codes.append("coverage_decisions_target_missing")
                continue
            if target in decisions:
                codes.append(f"coverage_decisions_duplicate_target:{target}")
            decisions[target] = item
        return decisions, codes

    codes.append("coverage_decisions_invalid_type")
    return decisions, codes


def _mutations_for_target(mutations: list[dict[str, Any]], target: str) -> list[dict[str, Any]]:
    if target in {"challenge_tracker", "deal_stage_tracker"}:
        return [m for m in mutations if str(m.get("section_key") or "") == target]
    section_key, _, field_key = target.partition(".")
    return [
        m
        for m in mutations
        if str(m.get("section_key") or "") == section_key
        and str(m.get("field_key") or "") == field_key
    ]


def _is_numeric_like(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    return bool(_NUMERIC_RE.match(text))


def _validate_coverage_contract(
    contract: dict[str, Any],
    mutations: list[dict[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    codes: list[str] = []
    metrics: dict[str, Any] = {}

    coverage = contract.get("coverage")
    if not isinstance(coverage, dict):
        return ["coverage_contract_missing"], {"ucn_mode": "full"}

    decisions_raw = coverage.get("decisions")
    decisions, decision_codes = _normalize_coverage_decisions(decisions_raw)
    codes.extend(decision_codes)

    required_targets = _required_targets_full()
    missing_required = sorted(required_targets - set(decisions.keys()))
    if missing_required:
        codes.append("coverage_decisions_missing_required:" + ",".join(missing_required))

    unknown_targets = sorted({t for t in decisions.keys() if t not in TARGET_MATRIX})
    for target in unknown_targets:
        codes.append(f"coverage_decision_unknown_target:{target}")

    mutate_count = 0
    skip_count = 0
    for target, decision in decisions.items():
        if target not in TARGET_MATRIX:
            continue
        cfg = TARGET_MATRIX[target]
        action = str(decision.get("action") or "").strip().lower()
        if action == "no_evidence":
            action = "skip"

        if action not in {"mutate", "skip"}:
            codes.append(f"coverage_decision_invalid_action:{target}:{action or 'missing'}")
            continue

        if action == "skip":
            skip_count += 1
            reason = str(decision.get("skip_reason") or "").strip()
            if not reason:
                codes.append(f"coverage_skip_reason_missing:{target}")
            elif reason not in ALLOWED_SKIP_REASONS:
                codes.append(f"coverage_skip_reason_invalid:{target}:{reason}")
            continue

        mutate_count += 1
        target_mutations = _mutations_for_target(mutations, target)
        if not target_mutations:
            codes.append(f"coverage_mutation_missing:{target}")
            continue

        allowed_actions = set(cfg.get("allowed_mutation_actions", set()))
        matching_actions = {str(m.get("action") or "") for m in target_mutations}
        if not (matching_actions & allowed_actions):
            joined = ",".join(sorted(matching_actions)) if matching_actions else "none"
            codes.append(f"coverage_mutation_action_invalid:{target}:{joined}")
            continue

        if target in STRICT_EXPLICIT_STATEMENT_TARGETS:
            has_explicit_statement = any(
                bool(m.get("explicit_statement"))
                for m in target_mutations
                if str(m.get("action") or "") in allowed_actions
            )
            if not has_explicit_statement:
                codes.append(f"coverage_explicit_statement_required:{target}")

        if target in NUMERIC_VALUE_TARGETS:
            values = [
                m.get("new_value")
                for m in target_mutations
                if str(m.get("action") or "") in allowed_actions and m.get("new_value") is not None
            ]
            if not values or not any(_is_numeric_like(v) for v in values):
                example = str(values[0]) if values else ""
                codes.append(f"coverage_numeric_value_invalid:{target}:{example}")

    metrics = {
        "ucn_mode": "full",
        "required_targets_count": len(required_targets),
        "required_targets": sorted(required_targets),
        "decision_count": len(decisions),
        "mutate_count": mutate_count,
        "skip_count": skip_count,
        "allowed_skip_reasons": sorted(ALLOWED_SKIP_REASONS),
    }
    return codes, metrics


def validate_payload(
    payload: Any, ucn_mode: str | None = None
) -> tuple[bool, list[str], dict[str, Any]]:
    """Validate a UCN mutation plan.

    The ``ucn_mode`` parameter is **deprecated and ignored**; preflight always
    enforces the **full** ``TARGET_MATRIX`` (``required_in_ucn_full``). Remove
    ``planner_contract.ucn_mode`` or set it to ``full`` for clarity.
    """
    _ = ucn_mode  # deprecated; kept for backward compatibility with callers/tests
    codes: list[str] = []
    metrics: dict[str, Any] = {}
    mutations = _load_mutations(payload)

    if not isinstance(payload, dict):
        return False, ["planner_contract_missing"], {"reason": "top_level_not_object"}

    contract = payload.get("planner_contract")
    if not isinstance(contract, dict):
        return False, ["planner_contract_missing"], {"reason": "planner_contract_missing"}

    coverage_codes, coverage_metrics = _validate_coverage_contract(contract, mutations)
    codes.extend(coverage_codes)
    metrics["coverage"] = coverage_metrics

    dal_cfg = contract.get("dal")
    if not isinstance(dal_cfg, dict):
        codes.append("dal_contract_missing")
    else:
        expected_missing_count = dal_cfg.get("expected_missing_count")
        if not isinstance(expected_missing_count, int) or expected_missing_count < 0:
            codes.append("dal_contract_invalid_expected_missing_count")
            expected_missing_count = 0

        dal_skips = dal_cfg.get("skips", [])
        skip_keys: set[str] = set()
        if isinstance(dal_skips, list):
            for item in dal_skips:
                if not isinstance(item, dict):
                    continue
                key = str(item.get("meeting_key") or "").strip().lower()
                if key:
                    skip_keys.add(key)
        else:
            codes.append("dal_contract_invalid_skips")

        prepend_mutations = [
            m
            for m in mutations
            if (m.get("action") or "") == "prepend_daily_activity_ai_summary"
            and (m.get("section_key") or "") == "daily_activity_logs"
        ]
        emitted_count = len(prepend_mutations)
        required_count = max(0, expected_missing_count - len(skip_keys))
        if emitted_count != required_count:
            codes.append(f"dal_parity_failed:expected={required_count}:emitted={emitted_count}")

        expected_keys_raw = dal_cfg.get("expected_missing_keys", [])
        expected_keys: set[str] = set()
        if isinstance(expected_keys_raw, list):
            expected_keys = {str(k).strip().lower() for k in expected_keys_raw if str(k).strip()}
        elif expected_keys_raw:
            codes.append("dal_contract_invalid_expected_missing_keys")

        prepend_keys = {
            _normalize_heading_key(str(m.get("heading_line") or "")) for m in prepend_mutations
        }
        prepend_keys.discard("")
        unresolved = sorted(expected_keys - skip_keys - prepend_keys)
        if unresolved:
            codes.append("dal_missing_prepend_for_meeting:" + ",".join(unresolved))

        metrics["dal"] = {
            "expected_missing_count": expected_missing_count,
            "skip_count": len(skip_keys),
            "required_prepends": required_count,
            "emitted_prepends": emitted_count,
            "expected_missing_keys": sorted(expected_keys),
            "resolved_keys": sorted(prepend_keys | skip_keys),
        }

    ds_cfg = contract.get("deal_stage")
    if not isinstance(ds_cfg, dict):
        codes.append("deal_stage_contract_missing")
    else:
        expected_skus_raw = ds_cfg.get("expected_skus", [])
        if not isinstance(expected_skus_raw, list):
            codes.append("deal_stage_contract_invalid_expected_skus")
            expected_skus_raw = []
        expected_skus = {
            str(s).strip().lower()
            for s in expected_skus_raw
            if str(s).strip().lower() in COMMERCIAL_SKUS
        }

        no_change_raw = ds_cfg.get("no_change_with_reason", [])
        no_change_skus: set[str] = set()
        if isinstance(no_change_raw, list):
            for item in no_change_raw:
                if not isinstance(item, dict):
                    continue
                sku = str(item.get("sku") or "").strip().lower()
                reason = str(item.get("reason") or "").strip()
                if sku in COMMERCIAL_SKUS and reason:
                    no_change_skus.add(sku)
        elif no_change_raw:
            codes.append("deal_stage_contract_invalid_no_change_with_reason")

        upsell_lines = [
            str(m.get("new_value") or "")
            for m in mutations
            if (m.get("section_key") or "") == "exec_account_summary"
            and (m.get("field_key") or "") == "upsell_path"
            and (m.get("action") or "")
            in {"append_with_history", "set_if_empty", "update_in_place"}
        ]
        auto_skus: set[str] = set()
        for line in upsell_lines:
            auto_skus |= _sku_tokens_in_text(line)

        explicit_skus: set[str] = set()
        for m in mutations:
            if (m.get("section_key") or "") != "deal_stage_tracker":
                continue
            if (m.get("action") or "") not in {"update_table_row", "add_table_row"}:
                continue
            row = m.get("row")
            if not isinstance(row, dict):
                continue
            sku = str(row.get("sku") or row.get("challenge") or "").strip().lower()
            if sku in COMMERCIAL_SKUS:
                explicit_skus.add(sku)

        unresolved = sorted(expected_skus - auto_skus - explicit_skus - no_change_skus)
        if unresolved:
            codes.append("deal_stage_trigger_missing:" + ",".join(unresolved))

        metrics["deal_stage"] = {
            "expected_skus": sorted(expected_skus),
            "auto_skus": sorted(auto_skus),
            "explicit_skus": sorted(explicit_skus),
            "no_change_skus": sorted(no_change_skus),
        }

    return len(codes) == 0, codes, metrics


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Validate UCN planner contract before write_doc. "
            "Always enforces full matrix coverage (see TARGET_MATRIX required_in_ucn_full)."
        )
    )
    ap.add_argument("--mutations", required=True, help="Path to mutation JSON file")
    ap.add_argument(
        "--json-output",
        action="store_true",
        help="Print structured JSON result in addition to plain summary",
    )
    args = ap.parse_args()

    path = Path(args.mutations)
    if not path.exists():
        print(
            json.dumps({"ok": False, "codes": ["mutations_file_missing"], "path": str(path)})
            if args.json_output
            else f"planner_contract_failed: mutations_file_missing ({path})"
        )
        return 2

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"ok": False, "codes": ["mutations_json_invalid"], "error": str(exc)})
            if args.json_output
            else f"planner_contract_failed: mutations_json_invalid ({exc})"
        )
        return 2

    pc = payload.get("planner_contract") if isinstance(payload, dict) else None
    if isinstance(pc, dict) and "ucn_mode" in pc:
        raw_um = str(pc.get("ucn_mode") or "").strip().lower()
        if raw_um and raw_um != "full":
            print(
                f"ucn-planner-preflight: planner_contract.ucn_mode={pc.get('ucn_mode')!r} is ignored; "
                'preflight always enforces full matrix coverage. Omit ucn_mode or set it to "full".',
                file=sys.stderr,
            )

    ok, codes, metrics = validate_payload(payload)
    if args.json_output:
        print(json.dumps({"ok": ok, "codes": codes, "metrics": metrics}, indent=2))
    else:
        if ok:
            print("planner_contract_ok")
        else:
            print("planner_contract_failed: " + "; ".join(codes))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
