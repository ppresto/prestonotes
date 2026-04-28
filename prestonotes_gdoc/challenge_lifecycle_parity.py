"""Verify Challenge Tracker rows carry lifecycle anchors vs challenge-lifecycle.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Canonical anchor: ``[lifecycle_id:<id>]``.
# Tolerated legacy / abbreviated form: bare ``lifecycle:<id>`` (seen on
# 2026-04-21 22:10 E2E run where the agent wrote the shorter form into the
# Challenge Tracker notes cell). The legacy form is accepted for lookup
# so the reconciler can heal older rows; the writer still emits the
# canonical bracketed form (see TASK-052 §D).
MARKER_RE = re.compile(
    r"(?:\[lifecycle_id:|(?<![a-z])lifecycle:)([a-zA-Z0-9_.-]+)\]?",
    re.IGNORECASE,
)


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
    """Lowercased lifecycle ids found in [lifecycle_id:…] anchors (challenge + notes)."""
    blob = _tracker_blob(rows)
    return {m.group(1).lower() for m in MARKER_RE.finditer(blob)}


def markers_in_notes_references_only(rows: list) -> set[str]:
    """Lowercased lifecycle ids from anchors appearing only in Notes & References cells."""
    parts: list[str] = []
    for r in rows:
        parts.append(getattr(r, "notes_references", "") or "")
    blob = "\n".join(parts)
    return {m.group(1).lower() for m in MARKER_RE.finditer(blob)}


def markers_in_challenge_only(rows: list) -> set[str]:
    """Lowercased lifecycle ids from anchors appearing in Challenge column text."""
    parts: list[str] = []
    for r in rows:
        parts.append(getattr(r, "challenge", "") or "")
    blob = "\n".join(parts)
    return {m.group(1).lower() for m in MARKER_RE.finditer(blob)}


def strip_lifecycle_markers_from_challenge_text(text: str) -> str:
    """Remove lifecycle anchor tokens from challenge text; collapse whitespace."""
    stripped = MARKER_RE.sub(" ", text or "")
    return " ".join(stripped.split()).strip()


def _mentions_lifecycle_id(text: str, lifecycle_id: str) -> bool:
    """Return True when a row text references a lifecycle id token directly."""
    token_re = re.compile(
        rf"(?<![a-zA-Z0-9_.-]){re.escape(lifecycle_id)}(?![a-zA-Z0-9_.-])",
        re.IGNORECASE,
    )
    return bool(token_re.search(text or ""))


def auto_insert_missing_lifecycle_anchors(
    repo_root: Path, customer_name: str, tracker_rows: list
) -> list[str]:
    """Insert canonical anchors when rows reference lifecycle ids but miss anchors.

    The preflight auto-repair is intentionally conservative:
    - only inserts an anchor when the row text already contains the exact id token
    - keeps existing row text and appends canonical ``[lifecycle_id:<id>]`` in notes
    """
    lifecycle_ids = load_lifecycle_challenge_ids(repo_root, customer_name)
    if not lifecycle_ids:
        return []

    inserted: list[str] = []
    for idx, row in enumerate(tracker_rows):
        row_blob = f"{getattr(row, 'challenge', '')}\n{getattr(row, 'notes_references', '')}"
        existing_ids = markers_in_notes_references_only([row])
        missing_for_row: list[str] = []
        for lifecycle_id in lifecycle_ids:
            lid = lifecycle_id.lower()
            if lid in existing_ids:
                continue
            if _mentions_lifecycle_id(row_blob, lifecycle_id):
                missing_for_row.append(lifecycle_id)
        if not missing_for_row:
            continue

        notes = str(getattr(row, "notes_references", "") or "").strip()
        anchors = " ".join(f"[lifecycle_id:{cid}]" for cid in missing_for_row)
        if notes:
            sep = "; " if not notes.endswith((";", "|")) else " "
            setattr(row, "notes_references", f"{notes}{sep}{anchors}".strip())
        else:
            setattr(row, "notes_references", anchors)
        inserted.append(f"row[{idx}] -> {' '.join(missing_for_row)}")

    for row in tracker_rows:
        ch_orig = str(getattr(row, "challenge", "") or "")
        if not MARKER_RE.search(ch_orig):
            continue
        ch_stripped = strip_lifecycle_markers_from_challenge_text(ch_orig)
        if ch_stripped:
            setattr(row, "challenge", ch_stripped)
        else:
            setattr(row, "challenge", "")
    return inserted


def check_tracker_lifecycle_parity(
    repo_root: Path,
    customer_name: str,
    tracker_rows: list,
) -> tuple[list[str], list[str]]:
    """
    Returns (warnings, errors).

    - Parity is satisfied only when every lifecycle id has a matching anchor in
      **Notes & References** (not the Challenge column).
    - If challenge-lifecycle.json has ids but **no** anchors appear in Notes & References
      → migration warning (legacy docs).
    - If any anchor appears in the Challenge column → placement warning (anchors belong
      in Notes & References only).
    - If any anchor exists in Notes **or** Challenge, every lifecycle id must appear
      in Notes & References or errors list is non-empty (write should abort).
    """
    ids = load_lifecycle_challenge_ids(repo_root, customer_name)
    if not ids:
        return [], []

    warns: list[str] = []
    notes_ids = markers_in_notes_references_only(tracker_rows)
    challenge_ids = markers_in_challenge_only(tracker_rows)

    if not notes_ids:
        warns.append(
            "LIFECYCLE_PARITY: challenge-lifecycle.json has entries but Challenge Tracker "
            "Notes & References cells have no [lifecycle_id:…] (or legacy lifecycle:) anchors. "
            "Add anchors to Notes & References only "
            "(see docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md). "
            f"Lifecycle ids: {', '.join(ids)}"
        )

    if challenge_ids:
        warns.append(
            "LIFECYCLE_PARITY_PLACEMENT: lifecycle anchors were found in the Challenge column; "
            "they belong in Notes & References only. Move [lifecycle_id:…] tokens out of "
            "Challenge text (see docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md)."
        )

    if not notes_ids and not challenge_ids:
        return warns, []

    errors: list[str] = []
    for kid in ids:
        if kid.lower() not in notes_ids:
            errors.append(
                "LIFECYCLE_PARITY_FAIL: "
                f"lifecycle id {kid!r} is missing matching anchor [lifecycle_id:{kid}] "
                "in Challenge Tracker Notes & References after applying mutations."
            )
    return warns, errors
