#!/usr/bin/env python3
"""Shim: ``lpi_kb_seed_refresh`` moved to ``scripts/deprecated/`` — do not use from playbooks."""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "lpi_kb_seed_refresh.py is retired.\n\n"
        "Use Cursor wiz-remote MCP (wiz_docs_knowledge_base) and:\n"
        '  uv run python scripts/wiz_cache_manager.py kb-snapshot save --query "<seed>" '
        "--slice-top-k <K> --top-k <K>   # stdin or --json-file = full MCP JSON\n\n"
        "Or (offline): uv run python scripts/materialize_licensing_kb_snapshots.py\n"
        "    [--ingest-incoming]   # optional: from kb_licensing_seed_sources/_incoming/*.mcp.json\n\n"
        "See docs/ai/playbooks/load-product-intelligence.md §2.59 / §2.595.\n\n"
        "Archived implementation: scripts/deprecated/lpi_kb_seed_refresh.py",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
