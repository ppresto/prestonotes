"""Challenge lifecycle JSON helpers (project_spec §4, §7.4)."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
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

# Forbidden evidence vocabulary — single source of truth, shared by
# `append_challenge_transition` and the TASK-047 rule-side artifact hygiene
# block in `.cursor/rules/11-e2e-test-customer-trigger.mdc`. Keep the two
# lists in lockstep; the rule file is the operator-facing mirror. Order
# matters: the first match (substring, case-insensitive) is reported.
FORBIDDEN_EVIDENCE_TERMS: tuple[str, ...] = (
    "round 1",
    "round 2",
    "v1 corpus",
    "v2 corpus",
    "phase",
    "E2E",
    "harness",
    "fixture",
    "UCN round",
    "UCN wrote",
    "challenge rows added",
    "TASK-",
    "prestoNotes session",
)


class ChallengeValidationError(ValueError):
    """Structured write-side rejection carrying a JSON-serializable payload.

    The MCP tool layer catches this and emits the payload as a JSON error
    response. Plain ``ValueError`` (e.g. the existing illegal-transition check)
    continues to propagate unchanged so the current test contract is preserved.
    """

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        super().__init__(json.dumps(payload, ensure_ascii=False))


def _match_forbidden_evidence(evidence: str) -> str | None:
    """Return the first forbidden term (in declaration order) found as a
    case-insensitive substring of ``evidence``; ``None`` when none match.
    """
    haystack = evidence.lower()
    for term in FORBIDDEN_EVIDENCE_TERMS:
        if term.lower() in haystack:
            return term
    return None


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
    transitioned_at: str | None = None,
) -> dict[str, Any]:
    """
    Append-only transition: merge into challenge-lifecycle.json.

    ``transitioned_at`` is REQUIRED (ISO ``YYYY-MM-DD``, UTC calendar date of the
    cited transcript / call). There is no silent default — TASK-048 removed the
    prior fallback to today so every transition carries the real call date.

    Raises:
        ValueError: missing ``transitioned_at``, malformed ISO date, empty
            evidence, illegal single-step transition, or redundant same-state.
        ChallengeValidationError: one of the three hard-reject structured
            validations (future date, history regression, forbidden evidence
            vocabulary). The exception's ``payload`` attribute carries the
            user-facing dict the MCP tool layer returns as JSON.
    """
    cid = validate_challenge_id(challenge_id)
    nxt = validate_challenge_state(new_state)
    ev = (evidence or "").strip()
    if not ev:
        raise ValueError("evidence is required")

    # TASK-048 §D: required, no silent default. Raise a plain ValueError (not
    # ChallengeValidationError) so a missing-field bug in an upstream caller
    # surfaces as a hard error, not a user-visible MCP JSON response.
    date_s = (transitioned_at or "").strip()
    if not date_s:
        raise ValueError(
            "transitioned_at is required (ISO YYYY-MM-DD call date); no silent default"
        )
    if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date_s):
        raise ValueError("transitioned_at must be YYYY-MM-DD (UTC calendar date)")
    try:
        incoming = date.fromisoformat(date_s)
    except ValueError as exc:
        raise ValueError(f"transitioned_at is not a valid calendar date: {date_s}") from exc

    # TASK-048 §C.1 — Future date rejection (today + 1 day of slop permitted).
    today = datetime.now(timezone.utc).date()
    if incoming > today + timedelta(days=1):
        raise ChallengeValidationError(
            {
                "error": "transitioned_at in future",
                "field": "transitioned_at",
                "value": date_s,
                "expected": "<= today (UTC)",
            }
        )

    # TASK-048 §C.3 — Forbidden evidence vocabulary (pre-load so we fail fast
    # before reading the lifecycle file; matches the TASK-047 hygiene list).
    matched_term = _match_forbidden_evidence(ev)
    if matched_term is not None:
        raise ChallengeValidationError(
            {
                "error": "evidence contains forbidden harness vocabulary",
                "field": "evidence",
                "matched": matched_term,
            }
        )

    path = challenge_lifecycle_path(customer_name)
    data = _load_lifecycle(path)

    prev_raw = data.get(cid)
    if prev_raw is None:
        entry: dict[str, Any] = {"current_state": nxt, "history": []}
    else:
        entry = _normalize_entry(prev_raw)

    # TASK-048 §C.2 — History regression rejection (strictly greater only;
    # equal `at` is allowed — same-day multi-transition is handled by the
    # extractor-side collapse rule in 21-extractor.mdc).
    if entry["history"]:
        latest_existing = max(h["at"] for h in entry["history"])
        if latest_existing > date_s:
            raise ChallengeValidationError(
                {
                    "error": "transitioned_at regresses history",
                    "field": "transitioned_at",
                    "value": date_s,
                    "latest_existing": latest_existing,
                }
            )

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
