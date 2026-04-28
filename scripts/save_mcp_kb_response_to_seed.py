#!/usr/bin/env python3
"""Read wiz_docs_knowledge_base JSON from stdin, write minified to --out (for TASK-074 _seeds_json)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(
        description="Read MCP JSON (stdin), write one-line UTF-8 JSON to --out.",
    )
    p.add_argument("out", type=Path, help="Output .json path")
    args = p.parse_args()
    d = json.load(sys.stdin)
    if not isinstance(d, dict) or "results" not in d:
        print("Error: top-level {results: [...] } required", file=sys.stderr)
        return 1
    n = len(d.get("results") or [])
    text = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out} ({n} results)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
