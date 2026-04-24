#!/usr/bin/env python3
"""Run Wiz official docs search (same GraphQL contract as wiz-local ``search_wiz_docs``).

Loads ``WIZ_CLIENT_ID``, ``WIZ_CLIENT_SECRET``, ``WIZ_ENV`` from a dotenv file (default:
``<repo>/.cursor/mcp.env``). Usable from CI shells and agent terminals where Cursor MCP stdio
is not attached — same API the local MCP server calls.

Example::

    uv run python scripts/wiz_docs_search_cli.py --query \"How do I install the Wiz sensor?\"
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

import wiz_docs_client


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Wiz docs search via tenant GraphQL (search_wiz_docs equivalent)."
    )
    p.add_argument("--query", required=True, help="Natural-language docs question")
    p.add_argument(
        "--dotenv",
        type=Path,
        default=None,
        help="Path to dotenv with WIZ_* (default: <repo>/.cursor/mcp.env)",
    )
    args = p.parse_args(argv)

    repo = Path(__file__).resolve().parents[1]
    dotenv = args.dotenv or (repo / ".cursor" / "mcp.env")

    try:
        wiz_docs_client.load_wiz_dotenv(dotenv)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    try:
        result = wiz_docs_client.docs_search(args.query, dotenv=dotenv, repo=repo)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read()[:2000]!r}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False)[:24000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
