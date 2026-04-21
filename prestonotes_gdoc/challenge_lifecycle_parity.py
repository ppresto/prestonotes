"""Verify Challenge Tracker rows carry lifecycle anchors vs challenge-lifecycle.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

MARKER_RE = re.compile(r"\[lifecycle_id:([a-zA-Z0-9_.-]+)\]", re.IGNORECASE)


def _safe_customer_segment(name: str) -> str:
    s = (name or "").strip()
    if not s or ".." in s or "/" in s or "\\" in s:
        raise ValueError(f"invalid customer_name for parity check: {name!r}")
    return s


def load_lifecycle_challenge_ids(repo_root: Path, customer_name: str) -> list[str]:
    """Return sorted lifecycle JSON keys (challenge ids), or empty if file missing."""
    path = (
        repo_root
        / "MyNotes"
        / "Customers"
        / _safe_customer_segment(customer_name)
        / "AI_Insights"
        / "challenge-lifecycle.json"
    )
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    return [k for k in data if isinstance(k, str) and k.strip()]


def _tracker_blob(rows: list) -> str:
    parts: list[str] = []
    for r in rows:
        ch = getattr(r, "challenge", "") or ""
        notes = getattr(r, "notes_references", "") or ""
        parts.append(f"{ch}\n{notes}")
    return "\n".join(parts)


def markers_in_tracker(rows: list) -> set[str]:
    """Lowercased lifecycle ids found in [lifecycle_id:…] anchors."""
    blob = _tracker_blob(rows)
    return {m.group(1).lower() for m in MARKER_RE.finditer(blob)}


def check_tracker_lifecycle_parity(
    repo_root: Path,
    customer_name: str,
    tracker_rows: list,
) -> tuple[list[str], list[str]]:
    """
    Returns (warnings, errors).

    - If lifecycle has ids but the tracker has no [lifecycle_id:…] anchors at all → warning only
      (migration / older docs).
    - If any anchor exists → every lifecycle id must have a matching [lifecycle_id:<id>] token
      (case-insensitive id match) or errors list is non-empty (write should abort).
    """
    ids = load_lifecycle_challenge_ids(repo_root, customer_name)
    if not ids:
        return [], []

    blob = _tracker_blob(tracker_rows).lower()
    if "[lifecycle_id:" not in blob:
        msg = (
            "LIFECYCLE_PARITY: challenge-lifecycle.json has entries but Challenge Tracker rows "
            "have no [lifecycle_id:…] anchors. Add anchors to challenge or Notes & References "
            "(see docs/ai/references/customer-notes-mutation-rules.md). "
            f"Lifecycle ids: {', '.join(ids)}"
        )
        return [msg], []

    found = markers_in_tracker(tracker_rows)
    errors: list[str] = []
    for kid in ids:
        if kid.lower() not in found:
            errors.append(
                "LIFECYCLE_PARITY_FAIL: "
                f"lifecycle id {kid!r} is missing matching anchor [lifecycle_id:{kid}] "
                "in Challenge Tracker after applying mutations."
            )
    return [], errors
