"""Tests for scripts/granola-sync.py (Granola cache → per-call Transcripts)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "granola-sync.py"


def _load_granola_sync():
    spec = importlib.util.spec_from_file_location("granola_sync", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


g = _load_granola_sync()


def _minimal_cache(
    *,
    meeting_id: str = "meet-aaa",
    title: str = "Discovery Call",
    folder_name: str = "Acme Corp",
    transcript_lines: list[tuple[str, str]] | None = None,
    created_at: str = "2026-03-10T15:00:00Z",
) -> dict:
    if transcript_lines is None:
        transcript_lines = [("Alice", "Hello from Granola.")]
    segs = [{"text": t, "source": spk} for spk, t in transcript_lines]
    inner = {
        "documents": {
            meeting_id: {
                "title": title,
                "created_at": created_at,
                "folders": [{"id": "f1", "name": folder_name}],
            }
        },
        "transcripts": {meeting_id: segs},
    }
    return {"state": inner}


def test_sync_writes_one_file_per_meeting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(json.dumps(_minimal_cache()), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    monkeypatch.delenv("GRANOLA_DEFAULT_CUSTOMER", raising=False)

    r = g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    assert len(r["written"]) == 1
    p = Path(r["written"][0]["path"])
    assert p.is_file()
    body = p.read_text(encoding="utf-8")
    assert "Hello from Granola." in body
    assert "granola_meeting_id:" in body


def test_idempotent_second_run_no_duplicate_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(json.dumps(_minimal_cache()), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    monkeypatch.delenv("GRANOLA_DEFAULT_CUSTOMER", raising=False)

    g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    tdir = mynotes / "Customers" / "Acme Corp" / "Transcripts"
    first = list(tdir.glob("*.txt"))
    assert len(first) == 1

    g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    second = list(tdir.glob("*.txt"))
    assert len(second) == 1
    assert second[0] == first[0]


def test_internal_folder_routes_to_internal_customer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GRANOLA_INTERNAL_CUSTOMER_NAME", raising=False)
    cache = tmp_path / "c.json"
    cache.write_text(
        json.dumps(_minimal_cache(meeting_id="m2", folder_name="internal", title="Standup")),
        encoding="utf-8",
    )
    mynotes = tmp_path / "MyNotes"
    r = g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    assert len(r["written"]) == 1
    assert "Customers/Internal/Transcripts" in r["written"][0]["path"].replace("\\", "/")


def test_collision_distinct_meetings_same_title_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inner = {
        "documents": {
            "m-a": {
                "title": "Weekly Sync",
                "created_at": "2026-04-01T10:00:00Z",
                "folders": [{"id": "f1", "name": "BetaCo"}],
            },
            "m-b": {
                "title": "Weekly Sync",
                "created_at": "2026-04-01T14:00:00Z",
                "folders": [{"id": "f1", "name": "BetaCo"}],
            },
        },
        "transcripts": {
            "m-a": [{"text": "First", "source": "A"}],
            "m-b": [{"text": "Second", "source": "B"}],
        },
    }
    cache = tmp_path / "c.json"
    cache.write_text(json.dumps({"state": inner}), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    r = g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    assert len(r["written"]) == 2
    paths = {Path(x["path"]) for x in r["written"]}
    assert len(paths) == 2


def test_cli_json_exit_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(json.dumps(_minimal_cache()), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(mynotes))
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--cache",
            str(cache),
            "--customers-base",
            str(mynotes),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["written"]


def test_main_missing_gdrive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GDRIVE_BASE_PATH", raising=False)
    assert g.main(argv=[]) == 1
