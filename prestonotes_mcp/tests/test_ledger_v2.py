"""Tests for ledger v2 migration and append (TASK-011)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from prestonotes_mcp.config import load_config
from prestonotes_mcp.ledger_v2 import (
    LEDGER_V2_ALL,
    append_ledger_v2_row,
    detect_standard_table_column_count,
    migrate_standard_table_to_v2,
)
from prestonotes_mcp.runtime import init_ctx

REPO_ROOT = Path(__file__).resolve().parents[2]

LEDGER_FIXTURE_19 = """---
customer_name: Acme
last_ai_update: 2026-01-01
ledger_version: 1
schema_version: 2
---

# Acme — History Ledger

## Standard ledger row (required columns — core rules)

Append-only. One row per run; **do not edit prior rows**.

| Date | Account Health | Wiz Score | Sentiment | Coverage | Open Challenges | Aging Blockers | Resolved Issues | New Blockers | Goals Changed | Tools Changed | Stakeholder Shifts | Value Realized | Next Critical Event | Key Drivers | Wiz Licensed Products | Wiz License Purchase Dates | Wiz License Expiration/Renewal | Wiz License Evidence Quality |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-01-02 | good | 1 | pos | full | 0 | | | | | | | | | | | | | |

"""


def _row_values(suffix: str) -> dict[str, str]:
    return {c: f"v-{suffix}-{i}" for i, c in enumerate(LEDGER_V2_ALL)}


@pytest.fixture
def repo_ctx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    (tmp_path / "prestonotes_mcp").mkdir(parents=True)
    shutil.copy(
        REPO_ROOT / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
        tmp_path / "prestonotes_mcp" / "prestonotes-mcp.yaml.example",
    )
    cfg = load_config(tmp_path)
    init_ctx(tmp_path, cfg)
    return tmp_path


def test_migrate_19_to_24_columns() -> None:
    out = migrate_standard_table_to_v2(LEDGER_FIXTURE_19)
    assert detect_standard_table_column_count(out) == 24
    lines = [ln for ln in out.splitlines() if ln.strip().startswith("|")]
    header = lines[0]
    assert "call_type" in header
    assert "key_stakeholders" in header
    data_lines = [ln for ln in lines[2:] if "2026-01-02" in ln]
    assert len(data_lines) == 1
    cells = [c.strip() for c in data_lines[0].strip().strip("|").split("|")]
    assert len(cells) == 24
    assert cells[0] == "2026-01-02"
    assert cells[-5:] == ["", "", "", "", ""]


def test_append_after_migrate(repo_ctx: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    customer = "Acme"
    ai = repo_ctx / "MyNotes" / "Customers" / customer / "AI_Insights"
    ai.mkdir(parents=True)
    ledger = ai / f"{customer}-History-Ledger.md"
    migrated = migrate_standard_table_to_v2(LEDGER_FIXTURE_19.replace("Acme", customer))
    ledger.write_text(migrated, encoding="utf-8")

    monkeypatch.setattr("prestonotes_mcp.ledger_v2._today_iso", lambda: "2099-12-31")

    row = _row_values("t1")
    path = append_ledger_v2_row(customer, row)
    assert path == ledger
    text = ledger.read_text(encoding="utf-8")
    assert "last_ai_update: 2099-12-31" in text
    last_data = [ln for ln in text.splitlines() if ln.strip().startswith("|")][-1]
    for v in row.values():
        assert v in last_data


def test_append_copies_to_gdrive_when_parent_exists(
    repo_ctx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    customer = "DriveCo"
    g = repo_ctx / "gdrive_mirror"
    (g / "Customers" / customer / "AI_Insights").mkdir(parents=True)
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(g))

    ai = repo_ctx / "MyNotes" / "Customers" / customer / "AI_Insights"
    ai.mkdir(parents=True)
    ledger = ai / f"{customer}-History-Ledger.md"
    migrated = migrate_standard_table_to_v2(LEDGER_FIXTURE_19.replace("Acme", customer))
    ledger.write_text(migrated, encoding="utf-8")
    monkeypatch.setattr("prestonotes_mcp.ledger_v2._today_iso", lambda: "2099-01-01")

    append_ledger_v2_row(customer, _row_values("gd"))
    mirror = g / "Customers" / customer / "AI_Insights" / f"{customer}-History-Ledger.md"
    assert mirror.is_file()
    assert mirror.read_text(encoding="utf-8") == ledger.read_text(encoding="utf-8")


def test_append_rejects_19_column_table(repo_ctx: Path) -> None:
    customer = "Beta"
    ai = repo_ctx / "MyNotes" / "Customers" / customer / "AI_Insights"
    ai.mkdir(parents=True)
    ledger = ai / f"{customer}-History-Ledger.md"
    ledger.write_text(LEDGER_FIXTURE_19.replace("Acme", customer), encoding="utf-8")
    row = _row_values("x")
    with pytest.raises(ValueError, match="migrate_ledger"):
        append_ledger_v2_row(customer, row)


def test_append_ledger_v2_tool_json(repo_ctx: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from prestonotes_mcp.server import append_ledger_v2

    customer = "Gamma"
    ai = repo_ctx / "MyNotes" / "Customers" / customer / "AI_Insights"
    ai.mkdir(parents=True)
    ledger = ai / f"{customer}-History-Ledger.md"
    migrated = migrate_standard_table_to_v2(LEDGER_FIXTURE_19.replace("Acme", customer))
    ledger.write_text(migrated, encoding="utf-8")
    monkeypatch.setattr("prestonotes_mcp.ledger_v2._today_iso", lambda: "2099-06-01")
    row = _row_values("tool")
    out = append_ledger_v2(customer, json.dumps(row))
    data = json.loads(out)
    assert data.get("ok") is True
    assert str(ledger) in data.get("path", "")
