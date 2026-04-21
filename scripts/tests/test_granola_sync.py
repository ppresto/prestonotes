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


def test_sync_v6_cache_object_wrapper_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """cache-v6 stores ``cache`` as a JSON object (not a string), same shape as legacy ``state``."""
    inner = _minimal_cache()["state"]
    cache = tmp_path / "cache-v6.json"
    cache.write_text(json.dumps({"cache": inner}), encoding="utf-8")
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
    assert Path(r["written"][0]["path"]).is_file()


def test_parse_transcript_json_string_payload() -> None:
    """Caches may store the segment array as a JSON string (v6-style)."""
    payload = json.dumps(
        [{"text": "Line one", "source": "mic"}, {"text": "Line two", "source": "sys"}]
    )
    assert "Line one" in g.parse_transcript_segments(payload)
    assert "Line two" in g.parse_transcript_segments(payload)


def test_sync_transcript_value_as_json_string_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    doc = _minimal_cache()["state"]
    mid = "meet-aaa"
    segs = doc["transcripts"][mid]
    doc["transcripts"][mid] = json.dumps(segs)
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({"state": doc}), encoding="utf-8")
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


def test_sync_v6_cache_object_nested_state_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``cache`` may wrap the same ``{state: …}`` envelope as the legacy string payload."""
    cache = tmp_path / "cache-v6.json"
    cache.write_text(json.dumps({"cache": _minimal_cache()}), encoding="utf-8")
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
    assert r["written"][0].get("is_new") is True
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

    r2 = g.sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=mynotes,
        dry_run=False,
        emit_notes_without_transcript=False,
        default_customer=None,
    )
    second = list(tdir.glob("*.txt"))
    assert len(second) == 1
    assert second[0] == first[0]
    assert r2["written"][0].get("is_new") is False


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


def test_fixture_customer_name_with_leading_underscore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(
        json.dumps(
            _minimal_cache(
                meeting_id="meet-fixture",
                title="Weekly Sync",
                folder_name="_TEST_CUSTOMER",
                transcript_lines=[("Alice", "Fixture customer transcript line.")],
            )
        ),
        encoding="utf-8",
    )
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
    assert "Customers/_TEST_CUSTOMER/Transcripts" in r["written"][0]["path"].replace("\\", "/")


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


def test_cli_notify_writes_log_and_stdout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(json.dumps(_minimal_cache()), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    log_dir = tmp_path / "logs"
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(mynotes))
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--no-human-summary",
            "--stdout-format",
            "notify",
            "--log-dir",
            str(log_dir),
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
    assert "Granola sync" in proc.stdout
    assert "Discovery Call" in proc.stdout
    assert (log_dir / "granola-sync.log").is_file()
    assert "Discovery Call" in (log_dir / "granola-sync.log").read_text(encoding="utf-8")
    assert "[NEW]" in (log_dir / "granola-sync.log").read_text(encoding="utf-8")
    last = json.loads((log_dir / "granola-sync-last.json").read_text(encoding="utf-8"))
    assert last["written"] and last["written"][0].get("is_new") is True


def test_cli_json_exit_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = tmp_path / "cache-v4.json"
    cache.write_text(json.dumps(_minimal_cache()), encoding="utf-8")
    mynotes = tmp_path / "MyNotes"
    monkeypatch.setenv("GDRIVE_BASE_PATH", str(mynotes))
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--no-human-summary",
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


def test_default_cache_candidates_prefers_newest_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    granola = tmp_path / "Library/Application Support/Granola"
    granola.mkdir(parents=True)
    (granola / "cache-v3.json").write_text("{}", encoding="utf-8")
    (granola / "cache-v5.json").write_text("{}", encoding="utf-8")
    names = [p.name for p in g.default_cache_candidates()]
    assert names == ["cache-v5.json", "cache-v3.json"]


def test_default_cache_candidates_legacy_paths_when_no_granola_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    cands = g.default_cache_candidates()
    assert [p.name for p in cands] == ["cache-v4.json", "cache-v3.json"]
    assert str(cands[0]).endswith("Library/Application Support/Granola/cache-v4.json")
