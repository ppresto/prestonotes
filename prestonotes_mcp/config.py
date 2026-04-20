"""Load prestonotes-mcp.yaml and expand ${VAR} from the environment."""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Any

import yaml

_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _expand(obj: Any) -> Any:
    if isinstance(obj, str):

        def repl(m: re.Match[str]) -> str:
            return os.environ.get(m.group(1), "")

        return _VAR.sub(repl, obj)
    if isinstance(obj, dict):
        return {k: _expand(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand(x) for x in obj]
    return obj


def repo_root_from_env_or_file() -> Path:
    env = os.environ.get("PRESTONOTES_REPO_ROOT", "").strip()
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def load_config(repo_root: Path) -> dict[str, Any]:
    cfg_path = repo_root / "prestonotes_mcp" / "prestonotes-mcp.yaml"
    if not cfg_path.is_file():
        example = repo_root / "prestonotes_mcp" / "prestonotes-mcp.yaml.example"
        if example.is_file():
            cfg_path = example
        else:
            raise FileNotFoundError(
                f"Missing {repo_root / 'prestonotes_mcp' / 'prestonotes-mcp.yaml'}. "
                "Copy prestonotes-mcp.yaml.example to prestonotes-mcp.yaml and edit paths."
            )
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return _expand(raw)


def gdrive_base_from_config(cfg: dict[str, Any]) -> str:
    paths = cfg.get("paths", {})
    if not isinstance(paths, dict):
        return ""
    base = str(paths.get("gdrive_base", "") or "").strip()
    if base:
        return base
    return os.environ.get("GDRIVE_BASE_PATH", "").strip()


def mynotes_root_folder_id(cfg: dict[str, Any]) -> str:
    env = os.environ.get("MYNOTES_ROOT_FOLDER_ID", "").strip()
    if env:
        return env
    s = cfg.get("google", {})
    if isinstance(s, dict):
        return str(s.get("mynotes_root_folder_id", "") or "").strip()
    return ""


def gcloud_account_for_auth(cfg: dict[str, Any]) -> str:
    """Preferred Google account for gcloud (Docs/Drive API). Env wins over YAML."""
    env = os.environ.get("GCLOUD_ACCOUNT", "").strip()
    if env:
        return env
    g = cfg.get("google", {})
    if isinstance(g, dict):
        return str(g.get("auth_account", "") or "").strip()
    return ""


def auth_login_command_for_user(cfg: dict[str, Any]) -> str:
    """
    Full command the user should run in Terminal when Google API auth fails.

    Central config:
    - If GCLOUD_AUTH_LOGIN_COMMAND is set in the environment (e.g. Cursor .cursor/mcp.env), use it verbatim.
    - Else build: gcloud auth login --account=<GCLOUD_ACCOUNT> --enable-gdrive-access --force
      (omit --account if GCLOUD_ACCOUNT / yaml auth_account is empty).
    """
    override = os.environ.get("GCLOUD_AUTH_LOGIN_COMMAND", "").strip()
    if override:
        return override
    acct = gcloud_account_for_auth(cfg)
    if acct:
        return f"gcloud auth login --account={shlex.quote(acct)} --enable-gdrive-access --force"
    return "gcloud auth login --enable-gdrive-access --force"


def google_auth_terminal_fix_fields(cfg: dict[str, Any]) -> dict[str, Any]:
    """Fields to merge into MCP JSON when Google API / gcloud auth may be the issue."""
    return {
        "run_in_terminal_to_fix": auth_login_command_for_user(cfg),
        "gcloud_account_configured": gcloud_account_for_auth(cfg) or None,
    }
