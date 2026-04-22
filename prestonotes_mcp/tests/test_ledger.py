"""Tests for History Ledger schema v3 (TASK-049)."""

from __future__ import annotations

import json
import shutil
from datetime import date, timedelta
from pathlib import Path

import pytest

from prestonotes_mcp.config import load_config
from prestonotes_mcp.journey import FORBIDDEN_EVIDENCE_TERMS
from prestonotes_mcp.ledger import (
    LEDGER_V3_COLUMNS,
    LedgerValidationError,
    append_ledger_row,
    read_ledger,
)
from prestonotes_mcp.runtime import init_ctx

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_V3_COLUMNS = [
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


def _good_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "run_date": date.today().isoformat(),
        "call_type": "qbr",
        "account_health": "good",
        "wiz_score": 88,
        "sentiment": "positive",
        "coverage": "Cloud + Sensor coverage steady across 3 subs.",
        "challenges_new": ["kubelet-noise"],
        "challenges_in_progress": ["sensor-rollout", "kubelet-noise"],
        "challenges_stalled": [],
        "challenges_resolved": ["prisma-decom"],
        "goals_delta": "FedRAMP timeline reaffirmed for Q3.",
        "tools_delta": "Wiz Code onboarding kicked off.",
        "stakeholders_delta": "New VP Eng sponsor confirmed.",
        "stakeholders_present": ["alice", "bob"],
        "value_realized": "92% Wiz Score narrative; Cloud PO signed.",
        "next_critical_event": "2026-05-15: executive readout",
        "wiz_licensed_products": ["wiz_cloud", "wiz_sensor"],
        "wiz_license_purchases": ["2026-03-28:wiz_cloud"],
        "wiz_license_renewals": ["2026-03-28:wiz_sensor"],
        "wiz_license_evidence_quality": "high",
    }
    base.update(overrides)
    return base


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


def _customer_dir(root: Path, customer: str) -> Path:
    d = root / "MyNotes" / "Customers" / customer
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Schema shape
# ---------------------------------------------------------------------------


def test_ledger_v3_columns_matches_spec_order() -> None:
    assert list(LEDGER_V3_COLUMNS) == EXPECTED_V3_COLUMNS
    assert len(LEDGER_V3_COLUMNS) == 20


# ---------------------------------------------------------------------------
# Lazy-create + round-trip
# ---------------------------------------------------------------------------


def test_append_creates_ledger_when_missing(repo_ctx: Path) -> None:
    customer = "LazyCo"
    _customer_dir(repo_ctx, customer)
    row = _good_row()
    path = append_ledger_row(customer, row)
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "schema_version: 3" in text
    header_line = next(ln for ln in text.splitlines() if ln.strip().startswith("| run_date |"))
    cells = [c.strip() for c in header_line.strip().strip("|").split("|")]
    assert cells == list(LEDGER_V3_COLUMNS)


def test_round_trip_returns_typed_rows(repo_ctx: Path) -> None:
    customer = "RoundTrip"
    _customer_dir(repo_ctx, customer)
    row = _good_row()
    append_ledger_row(customer, row)

    payload = read_ledger(customer, max_rows=10)
    assert payload["schema_version"] == 3
    rows = payload["rows"]
    assert len(rows) == 1
    got = rows[0]
    assert got["wiz_score"] == 88
    assert got["challenges_in_progress"] == ["sensor-rollout", "kubelet-noise"]
    assert got["challenges_stalled"] == []
    assert got["wiz_license_purchases"] == ["2026-03-28:wiz_cloud"]
    assert got["coverage"] == row["coverage"]
    assert got["account_health"] == "good"


def test_read_ledger_empty_response_when_missing(repo_ctx: Path) -> None:
    customer = "NoFileYet"
    _customer_dir(repo_ctx, customer)
    payload = read_ledger(customer)
    assert payload.get("empty") is True
    assert customer in payload["path"]
    assert "append_ledger_row" in payload["message"]


# ---------------------------------------------------------------------------
# Enum rejections
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("call_type", "standup"),
        ("account_health", "amazing"),
        ("sentiment", "cheerful"),
        ("wiz_license_evidence_quality", "excellent"),
    ],
)
def test_enum_rejection(repo_ctx: Path, field: str, bad_value: str) -> None:
    customer = f"EnumCo{field}"
    _customer_dir(repo_ctx, customer)
    row = _good_row(**{field: bad_value})
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    payload = exc_info.value.payload
    assert payload["field"] == field
    assert payload["value"] == bad_value
    assert isinstance(payload["expected"], list)


# ---------------------------------------------------------------------------
# Date rejections
# ---------------------------------------------------------------------------


def test_future_run_date_rejected(repo_ctx: Path) -> None:
    customer = "FutureCo"
    _customer_dir(repo_ctx, customer)
    future = (date.today() + timedelta(days=5)).isoformat()
    row = _good_row(run_date=future)
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    assert exc_info.value.payload["field"] == "run_date"
    assert "future" in exc_info.value.payload["error"]


def test_regression_run_date_rejected(repo_ctx: Path) -> None:
    customer = "RegressCo"
    _customer_dir(repo_ctx, customer)
    today = date.today()
    append_ledger_row(customer, _good_row(run_date=today.isoformat()))
    earlier = (today - timedelta(days=30)).isoformat()
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, _good_row(run_date=earlier))
    p = exc_info.value.payload
    assert p["field"] == "run_date"
    assert p["value"] == earlier
    assert p["latest_existing"] == today.isoformat()


# ---------------------------------------------------------------------------
# Format rejections (id-list, ISO-SKU)
# ---------------------------------------------------------------------------


def test_id_list_empty_fragment_rejected(repo_ctx: Path) -> None:
    customer = "IdListEmpty"
    _customer_dir(repo_ctx, customer)
    # Non-string in list would fail type check first, so we feed a pre-joined
    # string via a custom payload by using an already-empty-fragment list.
    row = _good_row(challenges_in_progress=["a", "", "b"])
    # An empty string inside the list produces an empty fragment after render.
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "challenges_in_progress"
    assert "empty fragment" in p["error"]


def test_id_list_whitespace_fragment_rejected(repo_ctx: Path) -> None:
    customer = "IdListWs"
    _customer_dir(repo_ctx, customer)
    row = _good_row(challenges_in_progress=["a", " b "])
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "challenges_in_progress"
    assert "whitespace" in p["error"]


def test_iso_sku_format_rejected(repo_ctx: Path) -> None:
    customer = "BadSku"
    _customer_dir(repo_ctx, customer)
    row = _good_row(wiz_license_purchases=["2026/03/28:wiz_cloud"])
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "wiz_license_purchases"
    assert "ISO:sku" in p["error"]


# ---------------------------------------------------------------------------
# Forbidden vocabulary — couples to journey.py single source of truth.
# ---------------------------------------------------------------------------


def test_forbidden_vocab_rejected_couples_to_journey_ssot(repo_ctx: Path) -> None:
    # Pull ONE term straight from the imported constant so if journey.py's
    # FORBIDDEN_EVIDENCE_TERMS ever drifts, this test drifts with it.
    term = FORBIDDEN_EVIDENCE_TERMS[0]
    assert isinstance(term, str) and term
    customer = "ForbiddenCo"
    _customer_dir(repo_ctx, customer)
    row = _good_row(coverage=f"Coverage strong; note during {term} run.")
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "coverage"
    assert p["matched"].lower() == term.lower()
    assert "forbidden harness vocabulary" in p["error"]


def test_forbidden_vocab_rejected_inside_id_list(repo_ctx: Path) -> None:
    term = FORBIDDEN_EVIDENCE_TERMS[0]
    customer = "ForbiddenListCo"
    _customer_dir(repo_ctx, customer)
    row = _good_row(stakeholders_present=["alice", f"bob-{term}"])
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "stakeholders_present"
    assert p["matched"].lower() == term.lower()


# ---------------------------------------------------------------------------
# Length-cap rejection
# ---------------------------------------------------------------------------


def test_length_cap_rejection(repo_ctx: Path) -> None:
    customer = "TooLongCo"
    _customer_dir(repo_ctx, customer)
    row = _good_row(coverage="x" * 161)
    with pytest.raises(LedgerValidationError) as exc_info:
        append_ledger_row(customer, row)
    p = exc_info.value.payload
    assert p["field"] == "coverage"
    assert "length cap" in p["error"]
    assert p["expected"] == "<= 160 characters"


# ---------------------------------------------------------------------------
# GDrive mirror parity (kept from prior suite)
# ---------------------------------------------------------------------------


def test_append_copies_to_gdrive_when_parent_exists(
    repo_ctx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    customer = "DriveCo"
    g = repo_ctx / "gdrive_mirror"
    (g / "Customers" / customer / "AI_Insights").mkdir(parents=True)
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(g))
    _customer_dir(repo_ctx, customer)

    append_ledger_row(customer, _good_row())
    mirror = g / "Customers" / customer / "AI_Insights" / f"{customer}-History-Ledger.md"
    local = (
        repo_ctx
        / "MyNotes"
        / "Customers"
        / customer
        / "AI_Insights"
        / f"{customer}-History-Ledger.md"
    )
    assert mirror.is_file()
    assert mirror.read_text(encoding="utf-8") == local.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# MCP tool wrapper — append_ledger_row emits payload JSON on validation errors.
# ---------------------------------------------------------------------------


def test_append_ledger_row_tool_success(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import append_ledger_row as tool_append

    customer = "ToolOk"
    _customer_dir(repo_ctx, customer)
    out = tool_append(customer, json.dumps(_good_row()))
    data = json.loads(out)
    assert data["ok"] is True
    assert customer in data["path"]


def test_append_ledger_row_tool_rejects_and_returns_payload(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import append_ledger_row as tool_append

    customer = "ToolBad"
    _customer_dir(repo_ctx, customer)
    bad = _good_row(call_type="standup")
    out = tool_append(customer, json.dumps(bad))
    data = json.loads(out)
    assert data["ok"] is False
    assert data["field"] == "call_type"
    assert "expected" in data
