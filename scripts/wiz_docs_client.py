"""Shared Wiz tenant GraphQL client for official docs search (``aiAssistantQuery`` / DOCS).

Used by ``wiz_docs_search_cli.py`` and ``materialize_wiz_mcp_docs.py``. This is the same
contract as wiz-local ``search_wiz_docs`` — required when ``docs.wiz.io`` is not directly
reachable and all Wiz product text must come through the tenant API.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

GQL = """
query QueryDocs($input: AiAssistantQueryInput!) {
  aiAssistantQuery(input: $input) {
    aiAssistantQueryResult {
      docs {
        text
        links {
          text
          href
        }
      }
    }
  }
}
"""


def load_wiz_dotenv(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"missing env file: {path}")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        key = k.strip()
        if not key.startswith("WIZ_"):
            continue
        val = v.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def oauth_token(env: str, client_id: str, client_secret: str) -> str:
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    url = f"https://auth.{env}.wiz.io/oauth/token"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["access_token"])


def dc_from_jwt(token: str) -> str:
    parts = token.split(".")
    if len(parts) < 2:
        return "us1"
    payload = parts[1]
    padded = payload + "=" * (-len(payload) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    pl = json.loads(raw.decode("utf-8"))
    return str(pl.get("dc") or "us1")


def graphql_docs_search(env: str, dc: str, token: str, query_text: str) -> dict[str, Any]:
    url = f"https://api.{dc}.{env}.wiz.io/graphql"
    variables = {"input": {"query": query_text, "type": "DOCS"}}
    payload = json.dumps({"query": GQL, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_docs_block(result: dict[str, Any]) -> dict[str, Any] | None:
    """Return ``{"text": str, "links": [{"text","href"}, ...]}`` or None if missing."""
    try:
        block = result["data"]["aiAssistantQuery"]["aiAssistantQueryResult"]["docs"]
    except (KeyError, TypeError):
        return None
    if not isinstance(block, dict):
        return None
    text = block.get("text") or ""
    raw_links = block.get("links") or []
    links: list[dict[str, str]] = []
    if isinstance(raw_links, list):
        for item in raw_links:
            if not isinstance(item, dict):
                continue
            t = str(item.get("text") or "").strip()
            h = str(item.get("href") or "").strip()
            if h:
                links.append({"text": t, "href": h})
    return {"text": str(text), "links": links}


def docs_search(
    query_text: str,
    *,
    dotenv: Path | None = None,
    repo: Path | None = None,
) -> dict[str, Any]:
    """OAuth + GraphQL DOCS search; returns full JSON response dict."""
    root = repo or Path(__file__).resolve().parents[1]
    env_path = dotenv or (root / ".cursor" / "mcp.env")
    load_wiz_dotenv(env_path)
    env = (os.environ.get("WIZ_ENV") or "app").strip()
    cid = (os.environ.get("WIZ_CLIENT_ID") or "").strip()
    secret = (os.environ.get("WIZ_CLIENT_SECRET") or "").strip()
    if not cid or not secret:
        raise ValueError("Set WIZ_CLIENT_ID and WIZ_CLIENT_SECRET in the dotenv file.")
    token = oauth_token(env, cid, secret)
    dc = dc_from_jwt(token)
    return graphql_docs_search(env, dc, token, query_text)
