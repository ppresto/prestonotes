"""Smoke tests for scripts/rsync-gdrive-notes.sh (TASK-006)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RSYNC_SCRIPT = REPO_ROOT / "scripts" / "rsync-gdrive-notes.sh"
PUSH_SCRIPT = REPO_ROOT / "scripts" / "e2e-test-push-gdrive-notes.sh"


@pytest.fixture
def mirror_layout(tmp_path: Path) -> tuple[Path, Path]:
    """Fake Drive mount (MyNotes root) and empty repo root."""
    gdrive = tmp_path / "gdrive_mynotes"
    (gdrive / "Customers" / "Acme").mkdir(parents=True)
    (gdrive / "Customers" / "Acme" / "note.txt").write_text("hello", encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    return gdrive, repo


def test_rsync_script_exists() -> None:
    assert RSYNC_SCRIPT.is_file()
    assert PUSH_SCRIPT.is_file()


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_rsync_dry_run_customer_scope(mirror_layout: tuple[Path, Path]) -> None:
    gdrive, repo = mirror_layout
    env = {
        **os.environ,
        "GDRIVE_BASE_PATH": str(gdrive),
        "PRESTONOTES_REPO_ROOT": str(repo),
    }
    proc = subprocess.run(
        ["bash", str(RSYNC_SCRIPT), "--dry-run", "Acme"],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    out = proc.stdout + proc.stderr
    assert "Acme" in out or "note.txt" in out


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_rsync_applies_customer_scope(mirror_layout: tuple[Path, Path]) -> None:
    gdrive, repo = mirror_layout
    env = {
        **os.environ,
        "GDRIVE_BASE_PATH": str(gdrive),
        "PRESTONOTES_REPO_ROOT": str(repo),
    }
    proc = subprocess.run(
        ["bash", str(RSYNC_SCRIPT), "Acme"],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    local = repo / "MyNotes" / "Customers" / "Acme" / "note.txt"
    assert local.is_file()
    assert local.read_text(encoding="utf-8") == "hello"


@pytest.mark.skipif(not shutil.which("rsync"), reason="rsync not installed")
def test_push_applies_customer_scope(mirror_layout: tuple[Path, Path]) -> None:
    gdrive, repo = mirror_layout
    local_customer = repo / "MyNotes" / "Customers" / "Acme"
    local_customer.mkdir(parents=True)
    (local_customer / "note.txt").write_text("from-repo", encoding="utf-8")

    env = {
        **os.environ,
        "GDRIVE_BASE_PATH": str(gdrive),
        "PRESTONOTES_REPO_ROOT": str(repo),
    }
    proc = subprocess.run(
        ["bash", str(PUSH_SCRIPT), "Acme"],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    remote = gdrive / "Customers" / "Acme" / "note.txt"
    assert remote.is_file()
    assert remote.read_text(encoding="utf-8") == "from-repo"
