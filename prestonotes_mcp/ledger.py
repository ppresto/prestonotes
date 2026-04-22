"""History Ledger schema v3 (TASK-049) — single 20-column, snake_case table.

Everything here is canonical — there is no legacy v1/v2 migration scaffolding and
no auto-migration of on-disk v2 rows. The first successful ``append_ledger_row``
against a customer with no existing ledger writes a fresh ``schema_version: 3``
stub and appends the row.

Validation reuses the single source of truth for harness vocabulary from
``prestonotes_mcp.journey`` (``FORBIDDEN_EVIDENCE_TERMS``) and mirrors the
error-payload style of ``ChallengeValidationError`` introduced in TASK-048.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final

from prestonotes_mcp.journey import FORBIDDEN_EVIDENCE_TERMS
from prestonotes_mcp.security import customer_dir, validate_customer_name


def _match_forbidden(haystack: str) -> str | None:
    """Return the first forbidden term (declaration order) found as a
    case-insensitive substring of ``haystack``; ``None`` when none match.

    Local helper that consults the canonical ``FORBIDDEN_EVIDENCE_TERMS``
    tuple defined in ``prestonotes_mcp.journey`` (single source of truth per
    TASK-047/048). Reusing the imported constant — not redefining it — keeps
    journey.py's vocabulary list authoritative for both write surfaces.
    """
    hay = haystack.lower()
    for term in FORBIDDEN_EVIDENCE_TERMS:
        if term.lower() in hay:
            return term
    return None


# Ordered list of the 20 v3 columns (see TASK-049 §A). Order matters: it
# determines the markdown table column order and `read_ledger` key order.
LEDGER_V3_COLUMNS: Final[list[str]] = [
    "run_date",
    "call_type",
    "account_health",
    "wiz_score",
    "sentiment",
    "coverage",
    "challenges_new",
    "challenges_in_progress",
    "challenges_stalled",
    "challenges_resolved",
    "goals_delta",
    "tools_delta",
    "stakeholders_delta",
    "stakeholders_present",
    "value_realized",
    "next_critical_event",
    "wiz_licensed_products",
    "wiz_license_purchases",
    "wiz_license_renewals",
    "wiz_license_evidence_quality",
]

# Cell typing (see §A of the task file).
_ID_LIST_COLUMNS: Final[frozenset[str]] = frozenset(
    {
        "challenges_new",
        "challenges_in_progress",
        "challenges_stalled",
        "challenges_resolved",
        "stakeholders_present",
        "wiz_licensed_products",
        "wiz_license_purchases",
        "wiz_license_renewals",
    }
)
_INT_COLUMNS: Final[frozenset[str]] = frozenset({"wiz_score"})
_ISO_SKU_COLUMNS: Final[frozenset[str]] = frozenset(
    {"wiz_license_purchases", "wiz_license_renewals"}
)

_ENUMS: Final[dict[str, tuple[str, ...]]] = {
    "call_type": (
        "qbr",
        "exec_readout",
        "product_demo",
        "commercial_close",
        "technical_pov",
        "champion_1on1",
        "kickoff",
        "other",
    ),
    "account_health": ("great", "good", "at_risk", "critical"),
    "sentiment": ("positive", "neutral", "negative", "mixed"),
    "wiz_license_evidence_quality": ("high", "medium", "low"),
}

# Free-text character caps (§B, with a sane default for next_critical_event).
_FREE_TEXT_CAPS: Final[dict[str, int]] = {
    "coverage": 160,
    "goals_delta": 160,
    "tools_delta": 160,
    "stakeholders_delta": 160,
    "value_realized": 240,
    "next_critical_event": 240,
}

_ISO_SKU_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}:[a-z0-9_]+$")
_ISO_DATE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

_STANDARD_SECTION = "## Standard ledger row"
_STANDARD_SECTION_HEADING = "## Standard ledger row (required columns — core rules)"
_STANDARD_SECTION_PROSE = "Append-only. One row per run; **do not edit prior rows**."

# Re-export so external consumers never have to reach into journey.py for the
# forbidden-vocabulary constant. The tuple itself is still owned by journey.py
# (single source of truth per TASK-047/048); this alias exists purely for
# discoverability from the ledger module's public surface.
__all__ = [
    "LEDGER_V3_COLUMNS",
    "LedgerValidationError",
    "append_ledger_row",
    "read_ledger",
    "ensure_ledger_stub",
    "empty_ledger_markdown",
    "FORBIDDEN_EVIDENCE_TERMS",
]


class LedgerValidationError(ValueError):
    """Structured write-side rejection carrying a JSON-serializable payload.

    Mirrors ``ChallengeValidationError`` in ``prestonotes_mcp.journey``. The MCP
    tool layer catches this and emits ``{"ok": false, **payload}`` as JSON so
    operators see a named field + value/expected or matched vocabulary term.
    """

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        super().__init__(json.dumps(payload, ensure_ascii=False))


def _today_iso() -> str:
    return date.today().isoformat()


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


# ---------------------------------------------------------------------------
# Markdown table helpers
# ---------------------------------------------------------------------------


def _split_table_cells(line: str) -> list[str]:
    s = line.strip()
    if not s.startswith("|"):
        return []
    inner = s[1:-1] if s.endswith("|") else s[1:]
    return [c.strip() for c in inner.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_table_cells(line)
    if not cells:
        return False
    for c in cells:
        t = c.strip()
        if not t or not re.fullmatch(r":?-{3,}", t):
            return False
    return True


def _format_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _find_standard_table_start(lines: list[str]) -> int | None:
    """Line index of header row for the standard ledger table, or None."""
    in_section = False
    for i, line in enumerate(lines):
        if line.startswith(_STANDARD_SECTION):
            in_section = True
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_table_cells(line)
        if not cells:
            continue
        if cells[0] == LEDGER_V3_COLUMNS[0]:
            return i
    return None


def _table_insert_line_index(raw: list[str]) -> int:
    """Index in raw lines where a new table row should be inserted."""
    hi = _find_standard_table_start(raw)
    if hi is None:
        raise ValueError("Could not find standard ledger table header")
    sep_idx = hi + 1
    if sep_idx >= len(raw):
        raise ValueError("Could not find standard ledger table separator row")
    if not _is_separator_row(raw[sep_idx]) and "---" not in raw[sep_idx]:
        raise ValueError("Could not find standard ledger table separator row")
    j = sep_idx + 1
    insert_at = j
    while j < len(raw):
        stripped = raw[j].strip()
        if not stripped.startswith("|"):
            break
        if _is_separator_row(raw[j]):
            j += 1
            continue
        insert_at = j + 1
        j += 1
    return insert_at


# ---------------------------------------------------------------------------
# Stub / empty ledger
# ---------------------------------------------------------------------------


def empty_ledger_markdown(customer_name: str) -> str:
    """YAML frontmatter + title + standard section + 20-column header only."""
    name = validate_customer_name(customer_name)
    front = f"""---
customer_name: {name}
last_ai_update: {_today_iso()}
ledger_version: 1
schema_version: 3
---

# {name} — History Ledger

{_STANDARD_SECTION_HEADING}

{_STANDARD_SECTION_PROSE}

"""
    header = _format_table_row(list(LEDGER_V3_COLUMNS))
    sep = _format_table_row([":---"] * len(LEDGER_V3_COLUMNS))
    return front + header + "\n" + sep + "\n"


def ensure_ledger_stub(customer_name: str) -> Path:
    """Create AI_Insights/ if needed and write an empty v3 ledger when missing."""
    validate_customer_name(customer_name)
    cdir = customer_dir(customer_name)
    ai = cdir / "AI_Insights"
    ai.mkdir(parents=True, exist_ok=True)
    ledger = ai / f"{customer_name}-History-Ledger.md"
    if ledger.is_file():
        return ledger
    ledger.write_text(empty_ledger_markdown(customer_name), encoding="utf-8")
    return ledger


# ---------------------------------------------------------------------------
# Row rendering and validation
# ---------------------------------------------------------------------------


def _render_cell(col: str, value: Any) -> str:
    """Render a single row dict value to its markdown-cell string form.

    Type normalization happens here; downstream validators operate on the
    already-rendered cell value for format-level checks.
    """
    if value is None:
        return ""
    if col in _INT_COLUMNS:
        if isinstance(value, bool):
            raise LedgerValidationError(
                {
                    "error": "invalid type",
                    "field": col,
                    "value": str(value),
                    "expected": "int in 0..100 or empty",
                }
            )
        if isinstance(value, int):
            if value < 0 or value > 100:
                raise LedgerValidationError(
                    {
                        "error": "out of range",
                        "field": col,
                        "value": str(value),
                        "expected": "0..100",
                    }
                )
            return str(value)
        if isinstance(value, str) and value == "":
            return ""
        raise LedgerValidationError(
            {
                "error": "invalid type",
                "field": col,
                "value": repr(value),
                "expected": "int in 0..100 or empty",
            }
        )
    if col in _ID_LIST_COLUMNS:
        if isinstance(value, str):
            # Accept strings only when empty — explicit typed list required
            # otherwise, so caller mistakes surface as validation errors.
            if value == "":
                return ""
            raise LedgerValidationError(
                {
                    "error": "invalid type",
                    "field": col,
                    "value": value,
                    "expected": "list[str] (semicolon-joined on write)",
                }
            )
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, str):
                    raise LedgerValidationError(
                        {
                            "error": "invalid type",
                            "field": col,
                            "value": repr(item),
                            "expected": "list[str]",
                        }
                    )
            return ";".join(value)
        raise LedgerValidationError(
            {
                "error": "invalid type",
                "field": col,
                "value": repr(value),
                "expected": "list[str]",
            }
        )
    # Free text / enum cells.
    if not isinstance(value, str):
        raise LedgerValidationError(
            {
                "error": "invalid type",
                "field": col,
                "value": repr(value),
                "expected": "str",
            }
        )
    return value


def _validate_rendered_cells(cells: dict[str, str]) -> None:
    """Enum / date / id-list / ISO-SKU / vocab / length checks on rendered cells."""
    run_date = cells.get("run_date", "")
    if not run_date:
        raise LedgerValidationError(
            {
                "error": "run_date is required",
                "field": "run_date",
                "value": "",
                "expected": "ISO YYYY-MM-DD <= today + 1 (UTC)",
            }
        )
    if not _ISO_DATE_PATTERN.match(run_date):
        raise LedgerValidationError(
            {
                "error": "invalid run_date format",
                "field": "run_date",
                "value": run_date,
                "expected": "YYYY-MM-DD",
            }
        )
    try:
        run_d = date.fromisoformat(run_date)
    except ValueError as exc:
        raise LedgerValidationError(
            {
                "error": "invalid run_date calendar value",
                "field": "run_date",
                "value": run_date,
                "expected": "YYYY-MM-DD",
            }
        ) from exc
    if run_d > _today_utc() + timedelta(days=1):
        raise LedgerValidationError(
            {
                "error": "run_date in future",
                "field": "run_date",
                "value": run_date,
                "expected": "<= today + 1 day (UTC)",
            }
        )

    for col, allowed in _ENUMS.items():
        v = cells.get(col, "")
        if v == "":
            # Enum cells are required; an empty value is a hard reject so
            # summaries don't silently render "" where an enum should be.
            raise LedgerValidationError(
                {
                    "error": f"{col} is required",
                    "field": col,
                    "value": "",
                    "expected": list(allowed),
                }
            )
        if v not in allowed:
            raise LedgerValidationError(
                {
                    "error": f"invalid {col}",
                    "field": col,
                    "value": v,
                    "expected": list(allowed),
                }
            )

    # ID-list format checks: after render, we split on ";" and verify no empty
    # fragments and no surrounding whitespace around a fragment.
    for col in _ID_LIST_COLUMNS:
        rendered = cells.get(col, "")
        if rendered == "":
            continue
        fragments = rendered.split(";")
        for frag in fragments:
            if frag == "":
                raise LedgerValidationError(
                    {
                        "error": "id-list contains empty fragment",
                        "field": col,
                        "value": rendered,
                        "expected": "semicolon-separated, no empty fragments",
                    }
                )
            if frag != frag.strip():
                raise LedgerValidationError(
                    {
                        "error": "id-list fragment has surrounding whitespace",
                        "field": col,
                        "value": rendered,
                        "expected": "fragments stripped of surrounding whitespace",
                    }
                )
        if col in _ISO_SKU_COLUMNS:
            for frag in fragments:
                if not _ISO_SKU_PATTERN.match(frag):
                    raise LedgerValidationError(
                        {
                            "error": "invalid ISO:sku format",
                            "field": col,
                            "value": frag,
                            "expected": "YYYY-MM-DD:<snake_case_sku>",
                        }
                    )

    # Length caps (free text only — enum / id-list / int already constrained).
    for col, cap in _FREE_TEXT_CAPS.items():
        v = cells.get(col, "")
        if len(v) > cap:
            raise LedgerValidationError(
                {
                    "error": "cell exceeds length cap",
                    "field": col,
                    "value": v[:80] + ("…" if len(v) > 80 else ""),
                    "expected": f"<= {cap} characters",
                }
            )

    # Forbidden-vocabulary check: every non-run_date cell is inspected. For
    # id-list cells, inspect each fragment independently so a single bad id
    # still surfaces with `matched` naming the term.
    for col in LEDGER_V3_COLUMNS:
        if col == "run_date":
            continue
        rendered = cells.get(col, "")
        if rendered == "":
            continue
        if col in _ID_LIST_COLUMNS:
            haystacks = rendered.split(";")
        else:
            haystacks = [rendered]
        for h in haystacks:
            if not h:
                continue
            matched = _match_forbidden(h)
            if matched is not None:
                raise LedgerValidationError(
                    {
                        "error": "cell contains forbidden harness vocabulary",
                        "field": col,
                        "matched": matched,
                    }
                )


def _extract_existing_run_dates(content: str) -> list[str]:
    """Return run_date cell values already present in the standard table."""
    raw = content.splitlines()
    hi = _find_standard_table_start(raw)
    if hi is None:
        return []
    out: list[str] = []
    j = hi + 2  # header + separator
    while j < len(raw):
        stripped = raw[j].strip()
        if not stripped.startswith("|"):
            break
        if _is_separator_row(raw[j]):
            j += 1
            continue
        cells = _split_table_cells(raw[j])
        if cells and _ISO_DATE_PATTERN.match(cells[0]):
            out.append(cells[0])
        j += 1
    return out


# ---------------------------------------------------------------------------
# Public API: append / read
# ---------------------------------------------------------------------------


def append_ledger_row(customer_name: str, row: dict[str, str | int | list[str]]) -> Path:
    """Append one v3 row to the customer History Ledger; returns path written.

    Validation layers (each raises ``LedgerValidationError`` with an
    MCP-layer-renderable payload):

    * Cell type conformance (str / int / list[str] per column).
    * Enum membership for call_type / account_health / sentiment /
      wiz_license_evidence_quality.
    * run_date format + <= today + 1 day (UTC); rejected if a newer run_date
      already exists in the table.
    * ID-list format (no empty fragments, no fragment whitespace).
    * ISO:sku format for wiz_license_purchases / wiz_license_renewals.
    * Free-text length caps per §B of TASK-049.
    * Forbidden harness vocabulary from ``FORBIDDEN_EVIDENCE_TERMS``.
    """
    if not isinstance(row, dict):
        raise TypeError("row must be a dict")
    validate_customer_name(customer_name)

    # Unexpected keys surface as a hard error so drift / stale callers are
    # detected at write time rather than silently dropping data.
    extra = sorted(set(row) - set(LEDGER_V3_COLUMNS))
    if extra:
        raise LedgerValidationError(
            {
                "error": "unknown ledger columns",
                "field": "<row>",
                "value": extra,
                "expected": list(LEDGER_V3_COLUMNS),
            }
        )

    rendered: dict[str, str] = {}
    for col in LEDGER_V3_COLUMNS:
        rendered[col] = _render_cell(col, row.get(col, ""))

    _validate_rendered_cells(rendered)

    cdir = customer_dir(customer_name)
    ledger = cdir / "AI_Insights" / f"{customer_name}-History-Ledger.md"
    if not ledger.is_file():
        ensure_ledger_stub(customer_name)

    existing = ledger.read_text(encoding="utf-8")

    # Regression guard: do not allow a row whose run_date is strictly older
    # than the newest existing run_date. Equal dates are permitted (same-day
    # multi-row is not prevented here; the wider append-only contract plus
    # upstream UCN discipline handle that case).
    prior = _extract_existing_run_dates(existing)
    if prior:
        newest = max(prior)
        if rendered["run_date"] < newest:
            raise LedgerValidationError(
                {
                    "error": "run_date regresses history",
                    "field": "run_date",
                    "value": rendered["run_date"],
                    "latest_existing": newest,
                }
            )

    cells = [rendered[c] for c in LEDGER_V3_COLUMNS]
    new_row = _format_table_row(cells) + "\n"

    text = existing
    if re.search(r"(?m)^last_ai_update:\s*\S", text):
        text = re.sub(
            r"(?m)^last_ai_update:\s*.*$",
            f"last_ai_update: {_today_iso()}",
            text,
            count=1,
        )

    raw = text.splitlines()
    keepends = text.splitlines(keepends=True)
    insert_at = _table_insert_line_index(raw)
    new_body = "".join(keepends[:insert_at]) + new_row + "".join(keepends[insert_at:])
    ledger.write_text(new_body, encoding="utf-8")

    gbp = os.environ.get("GDRIVE_BASE_PATH", "").strip()
    if gbp:
        gdest = Path(gbp) / "Customers" / customer_name / "AI_Insights" / ledger.name
        if gdest.parent.is_dir():
            shutil.copy2(str(ledger), str(gdest))

    return ledger


def _parse_cell(col: str, raw_value: str) -> str | int | list[str] | None:
    """Inverse of ``_render_cell`` — produce typed values from the markdown cell."""
    if col in _INT_COLUMNS:
        if raw_value == "":
            return None
        try:
            return int(raw_value)
        except ValueError:
            return raw_value  # keep as string for downstream visibility
    if col in _ID_LIST_COLUMNS:
        if raw_value == "":
            return []
        return [frag for frag in raw_value.split(";") if frag != ""]
    return raw_value


def read_ledger(customer_name: str, max_rows: int = 10) -> dict[str, Any]:
    """Return the last ``max_rows`` rows of the v3 ledger as typed dicts.

    Preserves the ``{"empty": True, "path": ..., "message": ...}`` shape when
    no ledger file exists yet under ``AI_Insights`` for backward compatibility
    with ``read_ledger`` consumers.
    """
    validate_customer_name(customer_name)
    ai = customer_dir(customer_name) / "AI_Insights"
    expected = ai / f"{customer_name}-History-Ledger.md"
    if not ai.is_dir() or not expected.is_file():
        return {
            "empty": True,
            "path": str(expected),
            "message": (
                "No History Ledger file yet under AI_Insights; the first successful "
                "append_ledger_row creates it."
            ),
        }
    text = expected.read_text(encoding="utf-8")
    raw = text.splitlines()
    hi = _find_standard_table_start(raw)
    if hi is None:
        return {"path": str(expected), "rows": [], "schema_version": 3}
    rows: list[dict[str, Any]] = []
    j = hi + 2
    while j < len(raw):
        stripped = raw[j].strip()
        if not stripped.startswith("|"):
            break
        if _is_separator_row(raw[j]):
            j += 1
            continue
        cells = _split_table_cells(raw[j])
        if len(cells) != len(LEDGER_V3_COLUMNS):
            j += 1
            continue
        typed: dict[str, Any] = {}
        for col, cell in zip(LEDGER_V3_COLUMNS, cells, strict=True):
            typed[col] = _parse_cell(col, cell)
        rows.append(typed)
        j += 1
    if max_rows and max_rows > 0:
        rows = rows[-max_rows:]
    return {"path": str(expected), "rows": rows, "schema_version": 3}
