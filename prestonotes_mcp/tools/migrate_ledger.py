"""Migrate History Ledger standard markdown table from 19 to 24 columns (TASK-011)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from prestonotes_mcp.ledger_v2 import migrate_standard_table_to_v2


def _repo_root() -> Path:
    r = os.environ.get("PRESTONOTES_REPO_ROOT", "").strip()
    if r:
        return Path(r).expanduser().resolve()
    return Path.cwd().resolve()


def ledger_path_for_customer(root: Path, customer: str) -> Path:
    c = customer.strip()
    return root / "MyNotes" / "Customers" / c / "AI_Insights" / f"{c}-History-Ledger.md"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Migrate History Ledger standard table from 19 columns to v2 (24 columns)."
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture", type=Path, metavar="PATH", help="Path to a History-Ledger.md file")
    g.add_argument(
        "--customer", type=str, metavar="NAME", help="Customer folder name under MyNotes/Customers"
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print migrated content to stdout instead of writing the file",
    )
    args = p.parse_args(argv)

    root = _repo_root()
    if args.fixture is not None:
        path = args.fixture.expanduser().resolve()
    else:
        path = ledger_path_for_customer(root, args.customer)

    if not path.is_file():
        print(f"ERROR: ledger file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    out = migrate_standard_table_to_v2(text)
    if args.dry_run:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    path.write_text(out, encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
