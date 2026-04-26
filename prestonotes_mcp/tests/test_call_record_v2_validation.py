"""TASK-051 §A+§C: call-record schema v2 + write-side guardrails + lint CLI.

These tests cover the content-quality enforcement that lives in
``prestonotes_mcp/call_records.py`` (schema tightening, banned defaults,
speaker-in-participants, serialized size cap, extraction-confidence
downgrade, quote substring check, anti-regression) and the
``python -m prestonotes_mcp.call_records lint <customer>`` CLI.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from prestonotes_mcp.config import load_config
from prestonotes_mcp.runtime import init_ctx

REPO_ROOT = Path(__file__).resolve().parents[2]


_BASE_V2_RECORD: dict = {
    "call_id": "2026-04-15-discovery-1",
    "date": "2026-04-15",
    "call_type": "discovery",
    "call_number_in_sequence": 1,
    "participants": [
        {"name": "Jane Smith", "role": "CISO", "company": "Acme", "is_new": True},
        {"name": "John Doe", "role": "Exec Sponsor", "company": "Acme", "is_new": False},
    ],
    "summary_one_liner": "First discovery call covering posture and SIEM integration.",
    "key_topics": ["cloud posture", "SIEM integration", "agent rollout"],
    "challenges_mentioned": [
        {
            "id": "ch-unified-visibility",
            "description": "No unified cloud visibility across AWS and Azure tenants.",
            "status": "identified",
        }
    ],
    "products_discussed": ["Wiz Cloud", "Wiz Sensor"],
    "action_items": [
        {"owner": "Jane Smith", "action": "Send architecture overview", "due": "2026-04-22"}
    ],
    "sentiment": "positive",
    "deltas_from_prior_call": [],
    "verbatim_quotes": [
        {"speaker": "Jane Smith", "quote": "We need unified visibility across tenants."}
    ],
    "raw_transcript_ref": "2026-04-15-discovery-call.txt",
    "extraction_date": "2026-04-16",
    "extraction_confidence": "high",
    "goals_mentioned": [
        {"description": "Sensor coverage ≥ 95% prod Azure", "category": "adoption"}
    ],
    "risks_mentioned": [{"description": "SOC budget freeze may delay SIEM", "severity": "med"}],
    "metrics_cited": [{"metric": "Wiz Score", "value": "92%"}],
    "stakeholder_signals": [
        {"name": "John Doe", "role": "Exec Sponsor", "signal": "sponsor_engaged"}
    ],
}


def base_v2_record() -> dict:
    return copy.deepcopy(_BASE_V2_RECORD)


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


# ---------------------------------------------------------------------------
# Schema v2 — optional arrays and tightening
# ---------------------------------------------------------------------------


def test_schema_v2_accepts_new_optional_arrays() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    validate_call_record_object(base_v2_record())


def test_schema_v2_rejects_ch_stub_id() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["challenges_mentioned"] = [
        {"id": "ch-stub", "description": "placeholder content long enough", "status": "identified"}
    ]
    with pytest.raises(ValueError):
        validate_call_record_object(rec)


def test_schema_v2_rejects_fixture_narrative_description() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["challenges_mentioned"] = [
        {"id": "ch-splunk", "description": "Fixture narrative", "status": "identified"}
    ]
    with pytest.raises(ValueError):
        validate_call_record_object(rec)


def test_schema_v2_rejects_e2e_fixture_topic() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["key_topics"] = ["E2E fixture"]
    with pytest.raises(ValueError):
        validate_call_record_object(rec)


def test_schema_v2_rejects_wave2_hardcoded_key_topics() -> None:
    """TASK-052: the 2026-04-21 E2E agent wrote `["Wiz platform", "Security
    posture"]` on every record; reject those as banned defaults."""
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["key_topics"] = ["Wiz platform", "Security posture"]
    with pytest.raises(ValueError, match="Wiz platform|Security posture"):
        validate_call_record_object(rec)


def test_schema_v2_rejects_wave2_generic_action_item() -> None:
    """TASK-052: generic `Capture next steps from call` action item is the
    shortcut-extractor fingerprint; reject as a banned default.

    Write-time validator currently scans ``key_topics`` and
    ``challenges_mentioned[].{id,description}`` for banned substrings; the
    lint CLI does a full-string walk. We assert the banned list carries
    the new entry so the lint CLI fails hard on corpora that contain it.
    """
    from prestonotes_mcp.call_records import BANNED_CALL_RECORD_DEFAULTS

    assert "Capture next steps from call" in BANNED_CALL_RECORD_DEFAULTS


def test_schema_v2_rejects_shortcut_challenge_id_fingerprint() -> None:
    """TASK-052: id is a truncated kebab slug of description (observed on
    every 22:10 E2E record, e.g. ch-we-want-a-timeboxed-sens with
    description 'We want a timeboxed Sensor POV on Azure...')."""
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["challenges_mentioned"] = [
        {
            "id": "ch-we-want-a-timeboxed-sens",
            "description": (
                "We want a timeboxed Sensor POV on Azure production — success "
                "means runtime coverage parity with Cloud findings."
            ),
            "status": "identified",
        }
    ]
    with pytest.raises(ValueError, match="shortcut-extraction fingerprint"):
        validate_call_record_object(rec)


def test_schema_v2_rejects_summary_equals_quote() -> None:
    """TASK-052: summary_one_liner must be a paraphrase, not a verbatim
    copy of a quote."""
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    shared = "We need unified visibility across tenants."
    rec["summary_one_liner"] = shared
    rec["verbatim_quotes"] = [{"speaker": "Jane Smith", "quote": shared}]
    with pytest.raises(ValueError, match="verbatim copy"):
        validate_call_record_object(rec)


def test_schema_v2_accepts_legit_short_themed_challenge_id() -> None:
    """Sanity: short themed ids like ch-sensor-pov must not trip the
    shortcut-fingerprint guard even if description starts with the theme."""
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["challenges_mentioned"] = [
        {
            "id": "ch-sensor-pov",
            "description": "Sensor POV kickoff with runtime parity metrics.",
            "status": "identified",
        }
    ]
    validate_call_record_object(rec)


def test_schema_v2_rejects_products_not_in_enum_without_other_prefix() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    bad = base_v2_record()
    bad["products_discussed"] = ["Splunk"]
    with pytest.raises(ValueError):
        validate_call_record_object(bad)

    ok = base_v2_record()
    ok["products_discussed"] = ["Wiz Cloud", "Other: Splunk"]
    validate_call_record_object(ok)


def test_schema_v2_speaker_must_be_participant() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["verbatim_quotes"] = [{"speaker": "Nobody Here", "quote": "An orphan line."}]
    with pytest.raises(ValueError, match="speaker|participant"):
        validate_call_record_object(rec)


def test_schema_v2_quote_too_long() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["verbatim_quotes"] = [{"speaker": "Jane Smith", "quote": "a" * 281}]
    with pytest.raises(ValueError):
        validate_call_record_object(rec)


def test_schema_v2_more_than_three_quotes_rejected() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["verbatim_quotes"] = [
        {"speaker": "Jane Smith", "quote": f"line {i} with some substance"} for i in range(4)
    ]
    with pytest.raises(ValueError):
        validate_call_record_object(rec)


def test_schema_v2_size_cap_rejected() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    # Pad metrics_cited context to exceed the 2.5 KB cap while staying
    # schema-valid (strings are allowed inside metrics_cited[].context).
    filler = "x" * 600
    rec["metrics_cited"] = [
        {"metric": f"m{i}", "value": str(i), "context": filler} for i in range(6)
    ]
    assert len(json.dumps(rec, ensure_ascii=False).encode("utf-8")) > 2560
    with pytest.raises(ValueError, match="size|2560|2\\.5"):
        validate_call_record_object(rec)


# ---------------------------------------------------------------------------
# extraction_confidence downgrade
# ---------------------------------------------------------------------------


def test_extraction_confidence_downgrade_medium() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    # Empty 3 of the 5 optional v2 fields → downgrade high → medium.
    rec["goals_mentioned"] = []
    rec["risks_mentioned"] = []
    rec["stakeholder_signals"] = []
    # deltas_from_prior_call is already [].
    validate_call_record_object(rec)
    assert rec["extraction_confidence"] == "medium"


def test_extraction_confidence_downgrade_low() -> None:
    from prestonotes_mcp.call_records import validate_call_record_object

    rec = base_v2_record()
    rec["goals_mentioned"] = []
    rec["risks_mentioned"] = []
    rec["metrics_cited"] = []
    rec["stakeholder_signals"] = []
    # deltas_from_prior_call is already []. Five empties → downgrade to low.
    validate_call_record_object(rec)
    assert rec["extraction_confidence"] == "low"


# ---------------------------------------------------------------------------
# write_call_record — quote substring + missing transcript + anti-regression
# ---------------------------------------------------------------------------


def _seed_transcript(tmp_path: Path, customer: str, basename: str, body: str) -> Path:
    d = tmp_path / "MyNotes" / "Customers" / customer / "Transcripts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / basename
    p.write_text(body, encoding="utf-8")
    return p


def test_write_call_record_quote_substring_check(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_call_record

    _seed_transcript(
        repo_ctx,
        "AcmeCo",
        "2026-04-15-discovery-call.txt",
        "Speaker: Jane Smith: We need unified visibility across tenants.\n",
    )
    ok = base_v2_record()
    out = write_call_record("AcmeCo", ok["call_id"], json.dumps(ok))
    assert json.loads(out).get("ok") is True

    bad = base_v2_record()
    bad["call_id"] = "2026-04-15-discovery-2"
    bad["call_number_in_sequence"] = 2
    bad["verbatim_quotes"] = [
        {"speaker": "Jane Smith", "quote": "This exact line does not appear in the transcript."}
    ]
    with pytest.raises(ValueError, match="quote|substring|transcript"):
        write_call_record("AcmeCo", bad["call_id"], json.dumps(bad))


def test_write_call_record_missing_transcript_rejected(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_call_record

    rec = base_v2_record()
    rec["raw_transcript_ref"] = "does-not-exist.txt"
    with pytest.raises(ValueError, match="raw_transcript_ref|not found"):
        write_call_record("AcmeCo", rec["call_id"], json.dumps(rec))


def test_write_call_record_anti_regression(repo_ctx: Path) -> None:
    from prestonotes_mcp.server import write_call_record

    _seed_transcript(
        repo_ctx,
        "AcmeCo",
        "2026-04-15-discovery-call.txt",
        "Speaker: Jane Smith: We need unified visibility across tenants.\n",
    )
    rich = base_v2_record()
    write_call_record("AcmeCo", rich["call_id"], json.dumps(rich))

    thin = base_v2_record()
    thin["goals_mentioned"] = []
    thin["risks_mentioned"] = []
    thin["metrics_cited"] = []
    thin["stakeholder_signals"] = []
    thin["deltas_from_prior_call"] = []
    # Thin record has fewer populated fields than the existing high-confidence
    # record — the writer must refuse to overwrite.
    with pytest.raises(ValueError, match="anti-regression|fewer populated"):
        write_call_record("AcmeCo", thin["call_id"], json.dumps(thin))


# ---------------------------------------------------------------------------
# CLI — python -m prestonotes_mcp.call_records lint <customer>
# ---------------------------------------------------------------------------


def _write_clean_corpus(repo_ctx: Path) -> None:
    customer = "_TEST_CUSTOMER"
    _seed_transcript(
        repo_ctx,
        customer,
        "2026-04-15-discovery-call.txt",
        "Speaker: Jane Smith: We need unified visibility across tenants.\n",
    )
    from prestonotes_mcp.server import write_call_record

    rec = base_v2_record()
    write_call_record(customer, rec["call_id"], json.dumps(rec))


def _run_cli(repo_ctx: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "prestonotes_mcp.call_records", *args],
        cwd=repo_ctx,
        env={
            **_cli_env(repo_ctx),
        },
        capture_output=True,
        text=True,
        check=False,
    )


def _cli_env(repo_ctx: Path) -> dict:
    import os as _os

    env = dict(_os.environ)
    env["PRESTONOTES_REPO_ROOT"] = str(repo_ctx)
    # Ensure the CLI subprocess can import the package under test.
    pythonpath = env.get("PYTHONPATH", "")
    extra = str(REPO_ROOT)
    env["PYTHONPATH"] = f"{extra}:{pythonpath}" if pythonpath else extra
    return env


def test_cli_lint_exits_zero_on_clean_corpus(repo_ctx: Path) -> None:
    _write_clean_corpus(repo_ctx)
    proc = _run_cli(repo_ctx, "lint", "_TEST_CUSTOMER")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cli_lint_exits_nonzero_on_stub_corpus(repo_ctx: Path) -> None:
    customer = "_TEST_CUSTOMER"
    _seed_transcript(
        repo_ctx,
        customer,
        "2026-04-15-discovery-call.txt",
        "Speaker: Jane Smith: We need unified visibility across tenants.\n",
    )
    # Drop a stub record on disk directly so the lint scanner hits it — we
    # deliberately bypass write_call_record (which would reject the stub).
    cr_dir = repo_ctx / "MyNotes" / "Customers" / customer / "call-records"
    cr_dir.mkdir(parents=True, exist_ok=True)
    stub = base_v2_record()
    stub["challenges_mentioned"] = [
        {"id": "ch-stub", "description": "Fixture narrative", "status": "identified"}
    ]
    stub["key_topics"] = ["E2E fixture"]
    (cr_dir / f"{stub['call_id']}.json").write_text(
        json.dumps(stub, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    proc = _run_cli(repo_ctx, "lint", customer)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    combined = proc.stdout + proc.stderr
    assert "ch-stub" in combined or "E2E fixture" in combined or "Fixture narrative" in combined
