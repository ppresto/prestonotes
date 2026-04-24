"""Default MCP tool-call audit log path (TASK-045)."""

from __future__ import annotations

from pathlib import Path

import pytest

from prestonotes_mcp.runtime import init_ctx
from prestonotes_mcp.security import _audit_path


def test_audit_path_defaults_to_logs_mcp_audit_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no paths.audit_log_rel, JSON audit lines go under logs/mcp-audit.log."""
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    cfg: dict = {
        "paths": {"gdrive_base": ""},
        "server": {"name": "prestonotes", "version": "2.0.0"},
    }
    init_ctx(tmp_path, cfg)
    assert _audit_path() == tmp_path / "logs" / "mcp-audit.log"
