"""Run repo scripts via uv from the repository root."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from prestonotes_mcp.runtime import get_ctx


def repo_root() -> Path:
    return get_ctx().repo_root


def run_uv_script(
    script_rel: str,
    *args: str,
    timeout: int = 600,
) -> subprocess.CompletedProcess[str]:
    """Run `uv run <script_rel> ...` with cwd = repo root."""
    root = repo_root()
    cmd = ["uv", "run", script_rel, *args]
    env = os.environ.copy()
    gdrive = get_ctx().config.get("paths", {})
    if isinstance(gdrive, dict):
        gb = str(gdrive.get("gdrive_base", "") or "").strip()
        if gb:
            env.setdefault("GDRIVE_BASE_PATH", gb)
    return subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def run_shell_script(
    script_rel: str, *args: str, timeout: int = 600
) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    script_path = root / script_rel
    if not script_path.is_file():
        raise FileNotFoundError(f"Script not found: {script_path}")
    cmd = ["bash", str(script_path), *args]
    env = os.environ.copy()
    paths = get_ctx().config.get("paths", {})
    if isinstance(paths, dict):
        gb = str(paths.get("gdrive_base", "") or "").strip()
        if gb:
            env["GDRIVE_BASE_PATH"] = gb
    return subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        shell=False,
    )
