"""Optional live check that Wiz OAuth client credentials work (wiz-local / APIs).

Skipped in CI when WIZ_CLIENT_ID / WIZ_CLIENT_SECRET / WIZ_ENV are unset.
To run locally: export vars from `.cursor/mcp.env` or rely on env already set in shell.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _wiz_creds_from_env() -> tuple[str, str, str] | None:
    cid = (os.environ.get("WIZ_CLIENT_ID") or "").strip()
    secret = (os.environ.get("WIZ_CLIENT_SECRET") or "").strip()
    env = (os.environ.get("WIZ_ENV") or "app").strip()
    if not cid or not secret:
        return None
    return cid, secret, env


def _load_dotenv_keys(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        key = k.strip()
        if key in ("WIZ_CLIENT_ID", "WIZ_CLIENT_SECRET", "WIZ_ENV"):
            out[key] = v.strip().strip('"').strip("'")
    return out


@pytest.mark.skipif(_wiz_creds_from_env() is None, reason="WIZ OAuth env not configured")
def test_wiz_client_credentials_returns_access_token() -> None:
    cid, secret, wiz_env = _wiz_creds_from_env()  # type: ignore[misc]
    token_url = f"https://auth.{wiz_env}.wiz.io/oauth/token"
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": cid,
            "client_secret": secret,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        token_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise AssertionError(f"OAuth HTTP {exc.code}: {exc.read()[:500]!r}") from exc

    data = json.loads(raw)
    assert "access_token" in data and len(str(data["access_token"])) > 20


def test_wiz_oauth_skipped_in_ci_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sanity: when creds missing, skip path does not require network."""
    monkeypatch.delenv("WIZ_CLIENT_ID", raising=False)
    monkeypatch.delenv("WIZ_CLIENT_SECRET", raising=False)
    assert _wiz_creds_from_env() is None


def test_mcp_env_example_documents_wiz_keys() -> None:
    example = REPO_ROOT / ".cursor" / "mcp.env.example"
    text = example.read_text(encoding="utf-8")
    assert "WIZ_CLIENT_ID" in text
    assert "WIZ_ENV" in text


def test_dotenv_parser_reads_wiz_keys_from_example_shape(tmp_path: Path) -> None:
    p = tmp_path / "mcp.env"
    p.write_text("WIZ_CLIENT_ID=a\nWIZ_CLIENT_SECRET=b\nWIZ_ENV=app\n", encoding="utf-8")
    keys = _load_dotenv_keys(p)
    assert keys == {"WIZ_CLIENT_ID": "a", "WIZ_CLIENT_SECRET": "b", "WIZ_ENV": "app"}
