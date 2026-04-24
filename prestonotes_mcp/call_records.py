"""Call record file I/O and JSON Schema validation (project_spec §7.1)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

from prestonotes_mcp.security import customer_dir

# §7.3 call types
_CALL_TYPES = frozenset(
    {
        "discovery",
        "technical_deep_dive",
        "campaign",
        "exec_qbr",
        "poc_readout",
        "renewal",
        "internal",
    }
)

# JSON Schema for §7.1 (required top-level fields from the spec example)
CALL_RECORD_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": True,
    "required": [
        "call_id",
        "date",
        "call_type",
        "call_number_in_sequence",
        "participants",
        "summary_one_liner",
        "key_topics",
        "challenges_mentioned",
        "products_discussed",
        "action_items",
        "sentiment",
        "deltas_from_prior_call",
        "verbatim_quotes",
        "raw_transcript_ref",
        "extraction_date",
        "extraction_confidence",
    ],
    "properties": {
        "call_id": {"type": "string", "minLength": 1},
        "date": {"type": "string", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "call_type": {"type": "string", "enum": sorted(_CALL_TYPES)},
        "call_number_in_sequence": {"type": "integer", "minimum": 1},
        "duration_minutes": {"type": "integer", "minimum": 0},
        "participants": {"type": "array"},
        "summary_one_liner": {"type": "string"},
        "key_topics": {"type": "array", "items": {"type": "string"}},
        "challenges_mentioned": {"type": "array"},
        "products_discussed": {"type": "array", "items": {"type": "string"}},
        "action_items": {"type": "array"},
        "sentiment": {"type": "string"},
        "deltas_from_prior_call": {"type": "array"},
        "verbatim_quotes": {"type": "array"},
        "raw_transcript_ref": {"type": "string"},
        "extraction_date": {"type": "string", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "extraction_confidence": {"type": "string"},
    },
}

_CALL_RECORD_VALIDATOR = Draft202012Validator(CALL_RECORD_SCHEMA)


def validate_call_record_object(data: dict[str, Any]) -> None:
    try:
        _CALL_RECORD_VALIDATOR.validate(data)
    except jsonschema.ValidationError as exc:
        path = "/".join(str(p) for p in exc.absolute_path) if exc.absolute_path else ""
        raise ValueError(
            f"call record schema{f' ({path})' if path else ''}: {exc.message}"
        ) from exc


def validate_call_id(call_id: str) -> str:
    """Return a safe basename for call-records/*.json (no path segments)."""
    s = (call_id or "").strip()
    if not s:
        raise ValueError("call_id is required")
    if ".." in s or "/" in s or "\\" in s:
        raise ValueError("call_id must not contain path segments")
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,190}$", s):
        raise ValueError(f"Invalid call_id (allowed: letters, digits, ._-): {call_id!r}")
    return s


def call_records_path(customer_name: str, call_id: str) -> Path:
    cid = validate_call_id(call_id)
    base = customer_dir(customer_name) / "call-records"
    return (base / f"{cid}.json").resolve()


def validate_call_type_filter(call_type: str | None) -> str | None:
    if call_type is None or not str(call_type).strip():
        return None
    ct = str(call_type).strip()
    if ct not in _CALL_TYPES:
        raise ValueError(f"call_type must be one of: {', '.join(sorted(_CALL_TYPES))}")
    return ct


def read_call_record_files(
    customer_name: str,
    since_date: str | None,
    call_type: str | None,
) -> list[dict[str, Any]]:
    """Load all valid call record JSON objects with optional filters."""
    cdir = customer_dir(customer_name) / "call-records"
    if not cdir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for p in sorted(cdir.glob("*.json")):
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        d_str = str(data.get("date") or "")
        if since_date and (not d_str or d_str < since_date):
            continue
        if call_type and str(data.get("call_type") or "") != call_type:
            continue
        out.append(data)
    out.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("call_id") or "")))
    return out
