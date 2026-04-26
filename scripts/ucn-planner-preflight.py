#!/usr/bin/env python3
"""Preflight validator for UCN mutation plans.

TASK-072 contract:
- DAL parity: expected missing meetings -> prepend actions.
- Deal Stage trigger path: expected SKU motion has an auto or explicit trigger.
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


def validate_payload(payload: Any) -> tuple[bool, list[str], dict[str, Any]]:
    codes: list[str] = []
    metrics: dict[str, Any] = {}
    mutations = _load_mutations(payload)

    if not isinstance(payload, dict):
        return False, ["planner_contract_missing"], {"reason": "top_level_not_object"}

    contract = payload.get("planner_contract")
    if not isinstance(contract, dict):
        return False, ["planner_contract_missing"], {"reason": "planner_contract_missing"}

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
    ap = argparse.ArgumentParser(description="Validate UCN planner contract before write_doc.")
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
