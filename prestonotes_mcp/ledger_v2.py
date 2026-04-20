"""History ledger v2: 19 legacy columns + 5 extensions (TASK-011)."""

from __future__ import annotations

import os
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Final

from prestonotes_mcp.security import customer_dir, validate_customer_name

# Mirror prestonotes_gdoc/update-gdoc-customer-notes.py LEDGER_REQUIRED_COLUMNS (do not import gdoc).
LEDGER_BASE_COLUMNS: Final[list[str]] = [
    "Date",
    "Account Health",
    "Wiz Score",
    "Sentiment",
    "Coverage",
    "Open Challenges",
    "Aging Blockers",
    "Resolved Issues",
    "New Blockers",
    "Goals Changed",
    "Tools Changed",
    "Stakeholder Shifts",
    "Value Realized",
    "Next Critical Event",
    "Key Drivers",
    "Wiz Licensed Products",
    "Wiz License Purchase Dates",
    "Wiz License Expiration/Renewal",
    "Wiz License Evidence Quality",
]

LEDGER_V2_EXTRA_COLUMNS: Final[list[str]] = [
    "call_type",
    "challenges_in_progress",
    "challenges_resolved",
    "value_realized",
    "key_stakeholders",
]

LEDGER_V2_ALL: Final[list[str]] = [*LEDGER_BASE_COLUMNS, *LEDGER_V2_EXTRA_COLUMNS]

_STANDARD_SECTION = "## Standard ledger row"
_MIGRATE_HINT = "Ledger standard table is not v2 (24 columns). Run: python -m prestonotes_mcp.tools.migrate_ledger"


def _today_iso() -> str:
    return date.today().isoformat()


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
        if line.startswith("#") and i > 0 and _STANDARD_SECTION in lines[i - 1]:
            pass
        stripped = line.strip()
        if not stripped.startswith("|"):
            if stripped == "":
                continue
            if stripped.startswith("#"):
                continue
        if "| Date |" not in line or "Account Health" not in line:
            continue
        cells = _split_table_cells(line)
        if len(cells) >= 2 and cells[0] == "Date":
            return i
    return None


def detect_standard_table_column_count(content: str) -> int | None:
    """Return column count for the standard ledger markdown table, or None if not found."""
    lines = content.splitlines()
    hi = _find_standard_table_start(lines)
    if hi is None:
        return None
    cells = _split_table_cells(lines[hi])
    return len(cells) if cells else None


def migrate_standard_table_to_v2(content: str) -> str:
    """Extend the standard ledger table from 19 to 24 columns; no-op if already 24+."""
    lines = content.splitlines(keepends=True)
    # Normalize to splitlines without keepends for mutation, then rejoin
    raw = content.splitlines()
    hi = _find_standard_table_start(raw)
    if hi is None:
        return content

    header_cells = _split_table_cells(raw[hi])
    n = len(header_cells)
    if n != len(LEDGER_BASE_COLUMNS):
        return content
    if n == len(LEDGER_V2_ALL):
        return content

    sep_idx = hi + 1
    if sep_idx >= len(raw) or "---" not in raw[sep_idx]:
        return content

    new_header = _format_table_row([*header_cells, *LEDGER_V2_EXTRA_COLUMNS])
    new_sep = _format_table_row([":---"] * len(LEDGER_V2_ALL))

    out_lines = list(lines)
    if not out_lines:
        return content

    def set_line(idx: int, body: str) -> None:
        old = out_lines[idx]
        eol = "\n"
        if old.endswith("\r\n"):
            eol = "\r\n"
        elif old.endswith("\r"):
            eol = "\r"
        out_lines[idx] = body + eol

    set_line(hi, new_header)
    set_line(sep_idx, new_sep)

    j = sep_idx + 1
    while j < len(raw):
        line = raw[j]
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        if _is_separator_row(line):
            j += 1
            continue
        cells = _split_table_cells(line)
        if not cells:
            break
        if len(cells) < len(LEDGER_BASE_COLUMNS):
            cells = [*cells, *([""] * (len(LEDGER_BASE_COLUMNS) - len(cells)))]
        elif len(cells) > len(LEDGER_BASE_COLUMNS):
            cells = cells[: len(LEDGER_BASE_COLUMNS)]
        cells = [*cells, *([""] * len(LEDGER_V2_EXTRA_COLUMNS))]
        set_line(j, _format_table_row(cells))
        j += 1

    return "".join(out_lines)


def validate_ledger_v2_row(row: dict[str, str]) -> None:
    if not isinstance(row, dict):
        raise TypeError("row must be a dict")
    keys = set(row)
    expected = set(LEDGER_V2_ALL)
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        parts = []
        if missing:
            parts.append(f"missing={missing}")
        if extra:
            parts.append(f"extra={extra}")
        raise ValueError("ledger v2 row keys must match LEDGER_V2_ALL exactly: " + "; ".join(parts))
    for col in LEDGER_V2_ALL:
        v = row[col]
        if not isinstance(v, str):
            raise ValueError(f"ledger column {col!r} must be a string, got {type(v).__name__}")


def _table_insert_line_index(raw: list[str]) -> int:
    """Index in raw lines where a new table row should be inserted (after existing data rows)."""
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


def append_ledger_v2_row(customer_name: str, row: dict[str, str]) -> Path:
    """Append one v2 row to the customer History Ledger; returns path written."""
    validate_customer_name(customer_name)
    validate_ledger_v2_row(row)

    cdir = customer_dir(customer_name)
    ledger = cdir / "AI_Insights" / f"{customer_name}-History-Ledger.md"
    if not ledger.is_file():
        raise FileNotFoundError(f"Ledger not found: {ledger}")

    existing = ledger.read_text(encoding="utf-8")
    n = detect_standard_table_column_count(existing)
    if n != len(LEDGER_V2_ALL):
        raise ValueError(_MIGRATE_HINT)

    cells = [row[c] for c in LEDGER_V2_ALL]
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
