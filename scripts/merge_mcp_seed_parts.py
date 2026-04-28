#!/usr/bin/env python3
"""Merge multiple TASK-074 seed JSONs (each {results: [one+]} ) into one file (stdin-style merge)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(
        description="Merge seed JSONs; outputs merged {results: [...] } to stdout (UTF-8).",
    )
    p.add_argument("parts", nargs="+", type=Path, help="Path to .json (each with results list)")
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Write merged JSON here instead of stdout",
    )
    args = p.parse_args()
    merged: list[dict] = []
    for path in args.parts:
        d = json.loads(path.read_text(encoding="utf-8"))
        merged.extend(d.get("results") or [])
    out = {"results": merged}
    text = json.dumps(out, ensure_ascii=False, indent=0)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out} ({len(merged)} results)", file=sys.stderr)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
