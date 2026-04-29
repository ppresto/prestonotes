"""Tests for scripts/ucn-prep.py (import by path; filename uses a hyphen)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO / "scripts" / "ucn-prep.py"


def _load_ucn_prep():
    sys.path.insert(0, str(_REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("ucn_prep_mod", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ucn_prep():
    return _load_ucn_prep()


def test_splice_notes_lite_skips_daily_activity(ucn_prep):
    raw = """# Account Summary

Hello summary

# Daily Activity Logs

SHOULD NOT APPEAR

### 2026-01-01

dal body

# Account Metadata

meta line

"""
    lite, meta = ucn_prep.splice_notes_lite(raw)
    assert "# Account Summary" in lite
    assert "# Account Metadata" in lite
    assert "SHOULD NOT APPEAR" not in lite
    assert "dal body" not in lite
    assert "meta line" in lite
    assert meta["had_daily_activity_heading"] is True


def test_splice_drops_long_and_data_image_lines(ucn_prep):
    long_line = "x" * 12_000
    raw = f"""# Account Summary

ok

{long_line}

# Daily Activity Logs

x

# Account Metadata

also ok

data:image/png;base64,ZZZ

"""
    lite, _ = ucn_prep.splice_notes_lite(raw)
    assert "ok" in lite
    assert "also ok" in lite
    assert long_line not in lite
    assert "data:image/" not in lite


def test_parse_master_blocks(ucn_prep):
    text = """MEETING: Alpha Sync
DATE: 2026-02-21T10:00:00.000Z
ID: uuid-one
========================================
Body one line

MEETING: Beta Call
DATE: 2026-03-01T12:00:00.000Z
ID: uuid-two
====
Body two
"""
    calls, warns = ucn_prep.parse_master_blocks(text)
    assert len(calls) == 2
    assert calls[0].title == "Alpha Sync"
    assert calls[0].body.strip() == "Body one line"
    assert not warns


def test_partition_bundles_1w(ucn_prep):
    root = Path("/tmp")  # paths only used for names / resolve in test
    files = [
        root / "2026-02-01-a.txt",
        root / "2026-02-05-b.txt",
        root / "2026-02-20-c.txt",
    ]
    bundles = ucn_prep.partition_bundles(files, "1w")
    assert len(bundles) >= 2
    assert all("transcript_paths" in b for b in bundles)


def test_end_to_end_default(tmp_path, ucn_prep):
    cust = "FixtureUcnPrep"
    cdir = tmp_path / "MyNotes" / "Customers" / cust
    (cdir / "Transcripts").mkdir(parents=True)
    (cdir / "AI_Insights").mkdir(parents=True)
    (cdir / f"{cust} Notes.md").write_text(
        "# Account Summary\n\nTop\n\n# Daily Activity Logs\n\nSkip\n\n# Account Metadata\n\nTail\n",
        encoding="utf-8",
    )
    (cdir / "Transcripts" / "2026-04-20-first.txt").write_text(
        "---\ngranola_meeting_id: a\n---\n\nx", encoding="utf-8"
    )
    (cdir / "Transcripts" / "2026-04-22-second.txt").write_text(
        "---\ngranola_meeting_id: b\n---\n\ny", encoding="utf-8"
    )

    out = tmp_path / "out-default"
    rc = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--customer",
            cust,
            "--out",
            str(out),
            "--priors",
            "1",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "PRESTONOTES_REPO_ROOT": str(tmp_path),
            "PYTHONPATH": str(_REPO / "scripts"),
        },
    )
    assert rc.returncode == 0, rc.stderr + rc.stdout
    handoff = json.loads((out / "handoff.json").read_text(encoding="utf-8"))
    assert handoff["customer"] == cust
    assert handoff["mode"] == "default"
    assert len(handoff["transcript_paths"]) == 2
    lite = (out / "notes-lite.md").read_text(encoding="utf-8")
    assert "Skip" not in lite
    assert "Tail" in lite


def test_end_to_end_bundle_split_master(tmp_path, ucn_prep):
    cust = "FixtureUcnBundle"
    cdir = tmp_path / "MyNotes" / "Customers" / cust
    tdir = cdir / "Transcripts"
    tdir.mkdir(parents=True)
    (cdir / "AI_Insights").mkdir(parents=True)
    (cdir / f"{cust} Notes.md").write_text(
        "# Account Summary\n\nS\n\n# Daily Activity Logs\n\nD\n\n# Account Metadata\n\nM\n",
        encoding="utf-8",
    )
    master = tdir / "_MASTER_FIX.txt"
    master.write_text(
        """MEETING: Zeta QBR
DATE: 2026-01-10T10:00:00.000Z
ID: 11111111-1111-1111-1111-111111111111
========================================
Alpha body

MEETING: Eta Sync
DATE: 2026-02-15T11:00:00.000Z
ID: 22222222-2222-2222-2222-222222222222
====
Beta body
""",
        encoding="utf-8",
    )
    out = tmp_path / "out-bundle"
    rc = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--customer",
            cust,
            "--out",
            str(out),
            "bundle",
            "--window",
            "1m",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "PRESTONOTES_REPO_ROOT": str(tmp_path),
            "PYTHONPATH": str(_REPO / "scripts"),
        },
    )
    assert rc.returncode == 0, rc.stderr + rc.stdout
    per_call = list(tdir.glob("2026-*.txt"))
    assert len(per_call) == 2
    state = json.loads((out / "migration-state.json").read_text(encoding="utf-8"))
    assert state["window"] == "1m"
    assert state["bundles"]
    handoff = json.loads((out / "handoff.json").read_text(encoding="utf-8"))
    assert handoff.get("bundle_id") == "b0"
