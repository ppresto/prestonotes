"""Challenge lifecycle JSON helpers (project_spec §4, §7.4)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prestonotes_mcp.security import customer_dir, validate_customer_name

CHALLENGE_STATES = frozenset(
    {
        "identified",
        "acknowledged",
        "in_progress",
        "resolved",
        "reopened",
        "stalled",
    }
)

# Allowed single-step transitions (§7.4). `identified` may skip to `in_progress` for MCP/tests.
_ALLOWED_NEXT: dict[str, frozenset[str]] = {
    "identified": frozenset({"acknowledged", "in_progress"}),
    "acknowledged": frozenset({"in_progress"}),
    "in_progress": frozenset({"resolved", "stalled"}),
    "resolved": frozenset({"reopened"}),
    "reopened": frozenset({"in_progress"}),
    "stalled": frozenset({"in_progress"}),
}


def validate_challenge_id(challenge_id: str) -> str:
    """Safe id for JSON keys (no path segments). Mirrors validate_call_id style."""
    s = (challenge_id or "").strip()
    if not s:
        raise ValueError("challenge_id is required")
    if ".." in s or "/" in s or "\\" in s:
        raise ValueError("challenge_id must not contain path segments")
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,190}$", s):
        raise ValueError(f"Invalid challenge_id (allowed: letters, digits, ._-): {challenge_id!r}")
    return s


def validate_challenge_state(state: str) -> str:
    s = (state or "").strip()
    if s not in CHALLENGE_STATES:
        raise ValueError(
            f"Invalid new_state {state!r}; must be one of: {', '.join(sorted(CHALLENGE_STATES))}"
        )
    return s


def challenge_lifecycle_path(customer_name: str) -> Path:
    validate_customer_name(customer_name)
    ai = customer_dir(customer_name) / "AI_Insights"
    return (ai / "challenge-lifecycle.json").resolve()


def utc_date_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _load_lifecycle(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid challenge-lifecycle.json: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("challenge-lifecycle.json must be a JSON object at the root")
    return raw


def _normalize_entry(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError("challenge entry must be an object with current_state and history")
    cur = obj.get("current_state")
    hist = obj.get("history")
    if not isinstance(cur, str) or cur not in CHALLENGE_STATES:
        raise ValueError("invalid or missing current_state in stored challenge entry")
    if not isinstance(hist, list):
        raise ValueError("history must be an array")
    out_hist: list[dict[str, Any]] = []
    for i, item in enumerate(hist):
        if not isinstance(item, dict):
            raise ValueError(f"history[{i}] must be an object")
        st = item.get("state")
        at = item.get("at")
        ev = item.get("evidence")
        if not isinstance(st, str) or st not in CHALLENGE_STATES:
            raise ValueError(f"history[{i}].state invalid")
        if not isinstance(at, str) or not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", at):
            raise ValueError(f"history[{i}].at must be YYYY-MM-DD")
        if not isinstance(ev, str):
            raise ValueError(f"history[{i}].evidence must be a string")
        out_hist.append({"state": st, "at": at, "evidence": ev})
    return {"current_state": cur, "history": out_hist}


def append_challenge_transition(
    customer_name: str,
    challenge_id: str,
    new_state: str,
    evidence: str,
    *,
    at: str | None = None,
) -> dict[str, Any]:
    """
    Append-only transition: merge into challenge-lifecycle.json.

    First transition for a challenge_id creates the entry. Illegal state jumps raise ValueError.
    """
    cid = validate_challenge_id(challenge_id)
    nxt = validate_challenge_state(new_state)
    ev = (evidence or "").strip()
    if not ev:
        raise ValueError("evidence is required")

    date_s = (at or "").strip() or utc_date_iso()
    if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date_s):
        raise ValueError("at must be YYYY-MM-DD (UTC calendar date)")

    path = challenge_lifecycle_path(customer_name)
    data = _load_lifecycle(path)

    prev_raw = data.get(cid)
    if prev_raw is None:
        entry: dict[str, Any] = {"current_state": nxt, "history": []}
    else:
        entry = _normalize_entry(prev_raw)

    cur = entry["current_state"]
    if prev_raw is not None:
        if nxt == cur:
            raise ValueError(f"new_state {nxt!r} matches current_state; no transition to record")
        allowed = _ALLOWED_NEXT.get(cur, frozenset())
        if nxt not in allowed:
            raise ValueError(
                f"Illegal challenge transition {cur!r} → {nxt!r}; "
                f"allowed next states: {', '.join(sorted(allowed))}"
            )

    entry["history"] = list(entry["history"])
    entry["history"].append({"state": nxt, "at": date_s, "evidence": ev})
    entry["current_state"] = nxt
    data[cid] = entry

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"path": str(path), "challenge_id": cid, "current_state": nxt}
