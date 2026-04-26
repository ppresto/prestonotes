"""Call record file I/O and JSON Schema validation (project_spec §7.1).

TASK-051 §A + §C extends the v1 schema with optional richness arrays
(``goals_mentioned``, ``risks_mentioned``, ``metrics_cited``,
``stakeholder_signals``), tightens existing fields, and layers on content-
quality guardrails (banned defaults, speaker-in-participants, serialized
size cap, extraction-confidence downgrade). Quote-substring and anti-
regression checks that need filesystem / prior-record context live in
``validate_call_record_against_transcript`` and are invoked by
``write_call_record`` in ``server.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
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

# TASK-051 §A: constrained Wiz SKU list. ``Other: <name>`` is the escape
# hatch for non-Wiz products the customer names in passing.
_WIZ_SKU_ENUM = (
    "Wiz Cloud",
    "Wiz Sensor",
    "Wiz Defend",
    "Wiz DSPM",
    "Wiz CIEM",
    "Wiz Code",
    "Wiz CLI",
    "Wiz Sensor POV",
)

_SENTIMENT_ENUM = ("positive", "neutral", "cautious", "negative")

# TASK-051 §A: banned defaults specific to call records. Kept SEPARATE from
# ``FORBIDDEN_EVIDENCE_TERMS`` in ``prestonotes_mcp/journey.py`` because the
# journey list is harness-vocabulary for ledger / lifecycle evidence strings,
# whereas these three strings are the stub-fallback fingerprints the TASK-051
# problem statement observed on every ``_TEST_CUSTOMER`` call record.
BANNED_CALL_RECORD_DEFAULTS: tuple[str, ...] = (
    "ch-stub",
    "Fixture narrative",
    "E2E fixture",
    # TASK-052 wave-2 fingerprints: observed 2026-04-21 22:10 E2E when the
    # agent took a shortcut and wrote the same hardcoded strings on every
    # record. These are the "new stubs" that TASK-051 did not catch.
    "Capture next steps from call",
    "Wiz platform",
    "Security posture",
)

# Hard cap per record, serialized as UTF-8 JSON (2.5 KB).
CALL_RECORD_MAX_BYTES = 2560


# Optional v2 fields whose emptiness triggers extraction_confidence downgrade.
_OPTIONAL_V2_FIELDS: tuple[str, ...] = (
    "goals_mentioned",
    "risks_mentioned",
    "metrics_cited",
    "stakeholder_signals",
    "deltas_from_prior_call",
)

# JSON Schema for §7.1. Schema v2 widens the schema with optional richness
# arrays while tightening existing fields; v1 records remain readable because
# the new arrays default to empty and the tightened bounds match what the spec
# already required informally.
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
        "participants": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "role": {"type": "string"},
                    "company": {"type": "string"},
                    "is_new": {"type": "boolean"},
                },
                "required": ["name"],
                "additionalProperties": True,
            },
        },
        "summary_one_liner": {"type": "string", "minLength": 1},
        "key_topics": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 3},
        },
        "challenges_mentioned": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "description", "status"],
                "properties": {
                    "id": {
                        "type": "string",
                        "pattern": r"^ch-[a-z0-9][a-z0-9-]{1,40}$",
                    },
                    "description": {"type": "string", "minLength": 10},
                    "status": {"type": "string", "minLength": 1},
                },
                "additionalProperties": True,
            },
        },
        "products_discussed": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string", "enum": list(_WIZ_SKU_ENUM)},
                    {"type": "string", "pattern": r"^Other: .+$"},
                ]
            },
        },
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["owner", "action"],
                "properties": {
                    "owner": {"type": "string", "minLength": 1},
                    "action": {"type": "string", "minLength": 1},
                    "due": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "sentiment": {"type": "string", "enum": list(_SENTIMENT_ENUM)},
        "deltas_from_prior_call": {"type": "array"},
        "verbatim_quotes": {
            "type": "array",
            "maxItems": 3,
            "items": {
                "type": "object",
                "required": ["speaker", "quote"],
                "properties": {
                    "speaker": {"type": "string", "minLength": 1},
                    "quote": {"type": "string", "minLength": 1, "maxLength": 280},
                },
                "additionalProperties": True,
            },
        },
        "raw_transcript_ref": {"type": "string", "minLength": 1},
        "extraction_date": {"type": "string", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "extraction_confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
        # v2 optional richness arrays (TASK-051 §A) — all may be empty.
        "goals_mentioned": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string", "minLength": 3},
                    "evidence_quote": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [
                            "adoption",
                            "commercial",
                            "operational",
                            "security_posture",
                            "stakeholder",
                        ],
                    },
                },
                "additionalProperties": True,
            },
        },
        "risks_mentioned": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "severity"],
                "properties": {
                    "description": {"type": "string", "minLength": 3},
                    "severity": {"type": "string", "enum": ["low", "med", "high"]},
                    "evidence_quote": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "metrics_cited": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["metric", "value"],
                "properties": {
                    "metric": {"type": "string", "minLength": 1},
                    "value": {"type": "string", "minLength": 1},
                    "context": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "stakeholder_signals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "signal"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "role": {"type": "string"},
                    "signal": {
                        "type": "string",
                        "enum": [
                            "sponsor_engaged",
                            "champion_exit",
                            "new_contact",
                            "decision_maker",
                            "detractor",
                        ],
                    },
                    "note": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
    },
}

_CALL_RECORD_VALIDATOR = Draft202012Validator(CALL_RECORD_SCHEMA)


# ---------------------------------------------------------------------------
# Content-quality helpers
# ---------------------------------------------------------------------------


def _string_fields_for_banned_check(data: dict[str, Any]) -> list[tuple[str, str]]:
    """Return ``(path, value)`` tuples to scan for banned-default equality.

    We only scan the fields the TASK-051 problem statement actually saw
    stubbed: ``key_topics`` items, ``challenges_mentioned[].id`` and
    ``.description``. Callers layer substring scans on top via the lint CLI.
    """
    out: list[tuple[str, str]] = []
    for i, t in enumerate(data.get("key_topics") or []):
        if isinstance(t, str):
            out.append((f"key_topics[{i}]", t))
    for i, ch in enumerate(data.get("challenges_mentioned") or []):
        if not isinstance(ch, dict):
            continue
        cid = ch.get("id")
        desc = ch.get("description")
        if isinstance(cid, str):
            out.append((f"challenges_mentioned[{i}].id", cid))
        if isinstance(desc, str):
            out.append((f"challenges_mentioned[{i}].description", desc))
    return out


def _check_banned_defaults(data: dict[str, Any]) -> None:
    banned_lower = {b.lower() for b in BANNED_CALL_RECORD_DEFAULTS}
    for path, value in _string_fields_for_banned_check(data):
        if value.strip().lower() in banned_lower:
            raise ValueError(
                f"call record content quality: banned default {value!r} at {path}; "
                f"extract real values or downgrade extraction_confidence"
            )


_KEBAB_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _kebab_prefix(s: str, n: int) -> str:
    """Lower-kebab slug of the first ``n`` non-trivial chars of ``s``."""
    head = s[:n].lower()
    return _KEBAB_NON_ALNUM.sub("-", head).strip("-")


def _check_no_shortcut_fingerprints(data: dict[str, Any]) -> None:
    """Reject the 2026-04-21 "wave-2" stub pattern.

    Observed symptom: the E2E agent produced records where
    ``challenges_mentioned[i].id`` is a ~24-char kebab slug of the opening
    characters of ``challenges_mentioned[i].description`` (i.e. the id is
    a truncated restatement of the description, not a theme). The signature
    is safe to check at write time because a well-formed record uses short
    thematic ids (``ch-soc-budget``, ``ch-champion-exit``) that are never
    the first 25 chars of any human-written description.

    Also reject when ``summary_one_liner`` is a verbatim copy of any
    ``verbatim_quotes[].quote`` — that is the other wave-2 fingerprint
    (summary field used as a quote echo rather than a paraphrase).
    """
    for i, ch in enumerate(data.get("challenges_mentioned") or []):
        if not isinstance(ch, dict):
            continue
        cid = ch.get("id")
        desc = ch.get("description")
        if not isinstance(cid, str) or not isinstance(desc, str):
            continue
        if len(cid) < 25:
            continue
        ktail = cid[3:] if cid.startswith("ch-") else cid
        if _kebab_prefix(desc, len(ktail)) == ktail:
            raise ValueError(
                f"call record content quality: challenges_mentioned[{i}].id "
                f"{cid!r} is a truncated slug of its own description "
                f"(shortcut-extraction fingerprint). Give the challenge a "
                f"short thematic kebab id (e.g. ch-soc-budget, "
                f"ch-champion-exit) that is not a rewording of the description."
            )
    summary = str(data.get("summary_one_liner") or "").strip()
    if summary:
        summary_norm = _normalize_ws(summary)
        for i, q in enumerate(data.get("verbatim_quotes") or []):
            if not isinstance(q, dict):
                continue
            qt = q.get("quote")
            if isinstance(qt, str) and _normalize_ws(qt) == summary_norm:
                raise ValueError(
                    f"call record content quality: summary_one_liner is a "
                    f"verbatim copy of verbatim_quotes[{i}].quote; summary "
                    f"must be a paraphrase, not an echo of a quote."
                )


def _check_speaker_in_participants(data: dict[str, Any]) -> None:
    names: set[str] = set()
    for p in data.get("participants") or []:
        if isinstance(p, dict):
            n = p.get("name")
            if isinstance(n, str) and n.strip():
                names.add(n.strip())
    for i, q in enumerate(data.get("verbatim_quotes") or []):
        if not isinstance(q, dict):
            continue
        sp = q.get("speaker")
        if isinstance(sp, str) and sp.strip() and sp.strip() not in names:
            raise ValueError(
                f"call record content quality: verbatim_quotes[{i}].speaker "
                f"{sp!r} is not in participants[].name; add the speaker to "
                f"participants or fix attribution"
            )


def _check_size_cap(data: dict[str, Any]) -> None:
    size = len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    if size > CALL_RECORD_MAX_BYTES:
        raise ValueError(
            f"call record content quality: serialized size {size} bytes exceeds "
            f"{CALL_RECORD_MAX_BYTES} bytes (2.5 KB hard cap)"
        )


def _downgrade_extraction_confidence(data: dict[str, Any]) -> None:
    """Mutate ``data`` in-place per TASK-051 §A optional-emptiness rule.

    Counts empty optional v2 fields out of the five-field set; 3 or more
    empties forces ``high → medium``, 5 empties further forces
    ``{high, medium} → low``. In-place mutation matches how
    ``validate_call_record_object`` already treats its input (callers in
    ``server.write_call_record`` re-serialize ``data`` after validation).
    """
    empties = 0
    for key in _OPTIONAL_V2_FIELDS:
        v = data.get(key)
        if v is None or (isinstance(v, list) and len(v) == 0):
            empties += 1
    current = str(data.get("extraction_confidence") or "")
    if empties >= 5 and current in {"high", "medium"}:
        data["extraction_confidence"] = "low"
    elif empties >= 3 and current == "high":
        data["extraction_confidence"] = "medium"


def validate_call_record_object(data: dict[str, Any]) -> None:
    """Validate a call-record dict against §7.1 schema v2 + content rules.

    This function MUTATES ``data`` in place to downgrade
    ``extraction_confidence`` when the optional-emptiness rule fires. The
    transcript-substring check is intentionally NOT invoked here; it lives in
    :func:`validate_call_record_against_transcript` and is called by
    ``write_call_record`` only, because it requires filesystem context.
    """
    try:
        _CALL_RECORD_VALIDATOR.validate(data)
    except jsonschema.ValidationError as exc:
        path = "/".join(str(p) for p in exc.absolute_path) if exc.absolute_path else ""
        raise ValueError(
            f"call record schema{f' ({path})' if path else ''}: {exc.message}"
        ) from exc
    _check_banned_defaults(data)
    _check_no_shortcut_fingerprints(data)
    _check_speaker_in_participants(data)
    _check_size_cap(data)
    _downgrade_extraction_confidence(data)


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


# ---------------------------------------------------------------------------
# Transcript-backed checks (used by write_call_record in server.py)
# ---------------------------------------------------------------------------


_WS_RUN = re.compile(r"\s+")


def _normalize_ws(s: str) -> str:
    return _WS_RUN.sub(" ", s).strip()


def _quote_substring_check(data: dict[str, Any], transcript_text: str) -> None:
    """Raise ``ValueError`` if any verbatim quote is not a whitespace-
    normalized substring of ``transcript_text``.
    """
    haystack = _normalize_ws(transcript_text)
    for i, q in enumerate(data.get("verbatim_quotes") or []):
        if not isinstance(q, dict):
            continue
        quote = q.get("quote")
        if not isinstance(quote, str) or not quote.strip():
            continue
        needle = _normalize_ws(quote)
        if needle not in haystack:
            raise ValueError(
                f"call record content quality: verbatim_quotes[{i}].quote is not "
                f"a substring of raw_transcript_ref; quotes must be copy-pasted "
                f"from the transcript (whitespace-collapsed match)"
            )


def validate_call_record_against_transcript(data: dict[str, Any], customer_name: str) -> None:
    """Locate the referenced transcript on disk and verify verbatim quotes.

    Raises ``ValueError`` when the referenced transcript is missing or
    unreadable, or when any quote is not a substring of the transcript after
    whitespace normalization. A missing transcript is a hard reject — we do
    not want the extractor to fabricate quotes under a missing-file loophole.
    """
    ref = str(data.get("raw_transcript_ref") or "").strip()
    if not ref:
        raise ValueError("raw_transcript_ref is required")
    basename = Path(ref).name
    if basename != ref or "/" in ref or "\\" in ref or ".." in ref:
        raise ValueError(f"raw_transcript_ref must be a basename, got {ref!r}")
    tpath = (customer_dir(customer_name) / "Transcripts" / basename).resolve()
    if not tpath.is_file():
        raise ValueError(
            f"raw_transcript_ref not found on disk: {basename!r} under "
            f"MyNotes/Customers/{customer_name}/Transcripts/"
        )
    try:
        text = tpath.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValueError(f"raw_transcript_ref not readable: {basename!r}: {exc}") from exc
    _quote_substring_check(data, text)


# ---------------------------------------------------------------------------
# Lint CLI — python -m prestonotes_mcp.call_records lint <customer>
# ---------------------------------------------------------------------------


def _lint_one_record(  # noqa: C901 — readable linear scanner
    path: Path,
    customer: str,
    record: dict[str, Any],
) -> tuple[list[str], int]:
    """Return ``(errors, size_bytes)`` for a single record."""
    errors: list[str] = []
    size = len(json.dumps(record, ensure_ascii=False).encode("utf-8"))
    try:
        validate_call_record_object(record)
    except ValueError as exc:
        errors.append(f"validation: {exc}")
    # Content-quality scan (substring sweep for banned defaults + forbidden
    # harness vocabulary; §C asks specifically for stub rejection, and the
    # journey forbidden list is an extra safety net).
    from prestonotes_mcp.journey import FORBIDDEN_EVIDENCE_TERMS

    def _walk(obj: Any) -> list[str]:
        out: list[str] = []
        if isinstance(obj, str):
            out.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                out.extend(_walk(v))
        elif isinstance(obj, list):
            for v in obj:
                out.extend(_walk(v))
        return out

    all_strings = _walk(record)
    banned_lower = {b.lower() for b in BANNED_CALL_RECORD_DEFAULTS}
    for s in all_strings:
        sl = s.lower()
        for b in banned_lower:
            if b in sl:
                errors.append(f"banned default substring {b!r} found in a string field")
                break
        for term in FORBIDDEN_EVIDENCE_TERMS:
            if term.lower() in sl:
                errors.append(f"forbidden harness vocabulary {term!r} found in a string field")
                break
    # Attempt the transcript substring check as a warning (the hard reject
    # already runs at write time). Missing transcripts are a warning here.
    try:
        validate_call_record_against_transcript(record, customer)
    except ValueError as exc:
        msg = str(exc)
        if "not found on disk" in msg or "not readable" in msg:
            errors.append(f"warning: {msg}")
        else:
            errors.append(f"transcript: {msg}")
    if size > CALL_RECORD_MAX_BYTES:
        errors.append(f"size: {size} bytes exceeds per-record cap {CALL_RECORD_MAX_BYTES}")
    _ = path  # retained for future per-file error context
    return errors, size


def _lint_corpus(customer: str) -> int:
    cdir = customer_dir(customer) / "call-records"
    if not cdir.is_dir():
        print(f"lint: no call-records directory for {customer!r}: {cdir}", file=sys.stderr)
        return 1
    files = sorted(cdir.glob("*.json"))
    if not files:
        print(f"lint: no call-records/*.json files for {customer!r}", file=sys.stderr)
        return 1
    total_bytes = 0
    any_errors = False
    lines: list[str] = []
    lines.append(f"{'call_id':<48}  {'bytes':>6}  status")
    for p in files:
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"lint: {p.name}: invalid JSON: {exc}", file=sys.stderr)
            any_errors = True
            lines.append(f"{p.stem:<48}  {'?':>6}  FAIL(json)")
            continue
        if not isinstance(rec, dict):
            print(f"lint: {p.name}: not a JSON object", file=sys.stderr)
            any_errors = True
            lines.append(f"{p.stem:<48}  {'?':>6}  FAIL(shape)")
            continue
        errs, size = _lint_one_record(p, customer, rec)
        total_bytes += size
        if errs:
            any_errors = True
            lines.append(f"{p.stem:<48}  {size:>6}  FAIL")
            for e in errs:
                print(f"lint: {p.name}: {e}", file=sys.stderr)
        else:
            lines.append(f"{p.stem:<48}  {size:>6}  OK")
    avg = total_bytes // max(1, len(files))
    for ln in lines:
        print(ln)
    print(f"-- corpus: {len(files)} records, total {total_bytes} bytes, avg {avg} bytes")
    if avg > 1536:
        any_errors = True
        print(
            f"lint: corpus average {avg} bytes exceeds 1.5 KB target",
            file=sys.stderr,
        )
    return 1 if any_errors else 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m prestonotes_mcp.call_records``."""
    parser = argparse.ArgumentParser(
        prog="prestonotes_mcp.call_records",
        description="Call-record utilities (schema v2 + lint).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    lint_p = sub.add_parser("lint", help="Lint a customer's call-records/*.json corpus.")
    lint_p.add_argument("customer", help="Customer name (e.g. _TEST_CUSTOMER).")
    args = parser.parse_args(argv)

    # Lazy runtime init so the CLI can run outside an MCP server process.
    from prestonotes_mcp.config import (
        gdrive_base_from_config,
        load_config,
        repo_root_from_env_or_file,
    )
    from prestonotes_mcp.runtime import init_ctx

    root = repo_root_from_env_or_file()
    os.environ.setdefault("PRESTONOTES_REPO_ROOT", str(root))
    cfg = load_config(root)
    gb = gdrive_base_from_config(cfg)
    if gb:
        os.environ.setdefault("GDRIVE_BASE_PATH", gb)
    init_ctx(root, cfg)

    if args.cmd == "lint":
        return _lint_corpus(args.customer)
    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover — exercised via subprocess
    raise SystemExit(main())
