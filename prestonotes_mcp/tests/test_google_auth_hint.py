"""google_auth_terminal_fix_fields builds login hint from config/env."""

from __future__ import annotations

import pytest

from prestonotes_mcp.config import google_auth_terminal_fix_fields


def test_google_auth_terminal_fix_respects_login_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "GCLOUD_AUTH_LOGIN_COMMAND", "gcloud auth login --account=test@example.com --force"
    )
    monkeypatch.delenv("GCLOUD_ACCOUNT", raising=False)
    d = google_auth_terminal_fix_fields({})
    assert d["run_in_terminal_to_fix"] == "gcloud auth login --account=test@example.com --force"
    assert d["gcloud_account_configured"] is None


def test_google_auth_terminal_fix_builds_from_account(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GCLOUD_AUTH_LOGIN_COMMAND", raising=False)
    monkeypatch.setenv("GCLOUD_ACCOUNT", "alice@corp.test")
    d = google_auth_terminal_fix_fields({})
    assert "alice@corp.test" in d["run_in_terminal_to_fix"]
    assert "gcloud auth login" in d["run_in_terminal_to_fix"]
    assert d["gcloud_account_configured"] == "alice@corp.test"
