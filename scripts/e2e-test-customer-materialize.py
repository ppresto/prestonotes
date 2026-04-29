#!/usr/bin/env python3
"""Materialize `_TEST_CUSTOMER` E2E transcript corpus from `tests/fixtures/e2e/` into `MyNotes/`.

Subcommands:
  to-fixtures   Copy current MyNotes Transcripts → tests/fixtures/e2e/_TEST_CUSTOMER/v1/ (no call-records in fixtures)
  apply         Copy v1 (and optional v2) Transcripts from fixtures; optionally clear call-records on v1 only (never copy JSON from v1)

Environment:
  PRESTONOTES_REPO_ROOT  optional; defaults to cwd.

Typical flow:
  1. uv run python scripts/e2e-test-customer-materialize.py to-fixtures   # snapshot transcripts into tests/ (v1/Transcripts only)
  2. uv run python scripts/e2e-test-customer-materialize.py apply --v2 # v2 merge (transcripts only)
  3. ./scripts/e2e-test-customer.sh prep-v1 / prep-v2   # bump dates + push as implemented in the shell
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

CUSTOMER = "_TEST_CUSTOMER"


def _repo_root() -> Path:
    import os

    r = os.environ.get("PRESTONOTES_REPO_ROOT", "").strip()
    if r:
        return Path(r).expanduser().resolve()
    return Path.cwd().resolve()


def _customer_dir(root: Path) -> Path:
    return root / "MyNotes" / "Customers" / CUSTOMER


def _fixture_v1(root: Path) -> Path:
    return root / "tests" / "fixtures" / "e2e" / CUSTOMER / "v1"


def _fixture_v2(root: Path) -> Path:
    return root / "tests" / "fixtures" / "e2e" / CUSTOMER / "v2"


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.is_dir():
        raise FileNotFoundError(f"Missing directory: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def _copy_files_only(src: Path, dst: Path, pattern: str) -> int:
    n = 0
    if not src.is_dir():
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob(pattern)):
        if p.is_file():
            shutil.copy2(p, dst / p.name)
            n += 1
    return n


def _clear_per_call_corpus(
    transcripts_dir: Path, call_records_dir: Path, *, clear_call_records: bool = True
) -> None:
    """Remove prior per-call transcripts (and optionally JSON call records) so ``apply`` is idempotent.

    v1 ``apply`` clears both dirs, then copies only transcripts from the v1 fixture (no JSON from tests/). v2 ``apply`` clears **only** transcripts, then merges
    v1+v2 fixture transcripts while **preserving** round-1 ``call-records/*.json`` when present (TASK-052).
    """
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    call_records_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(transcripts_dir.glob("*.txt")):
        if p.is_file():
            p.unlink()
    if not clear_call_records:
        return
    for p in sorted(call_records_dir.glob("*.json")):
        if p.is_file():
            p.unlink()


def cmd_to_fixtures(root: Path) -> int:
    cdir = _customer_dir(root)
    t_src = cdir / "Transcripts"
    v1 = _fixture_v1(root)
    if v1.exists():
        shutil.rmtree(v1)
    v1.mkdir(parents=True)
    _copy_tree(t_src, v1 / "Transcripts")
    print(f"Wrote fixture v1 baseline (Transcripts only) under {v1}")
    return 0


def cmd_apply(root: Path, *, v2: bool) -> int:
    cdir = _customer_dir(root)
    v1 = _fixture_v1(root)
    if not v1.is_dir():
        raise FileNotFoundError(f"Run to-fixtures first; missing {v1}")

    t_dst, cr_dst = cdir / "Transcripts", cdir / "call-records"
    # v2: keep existing call-records (round-1 extract output). v1: clear both dirs.
    _clear_per_call_corpus(t_dst, cr_dst, clear_call_records=not v2)

    n_tx = _copy_files_only(v1 / "Transcripts", t_dst, "*.txt")
    if v2:
        print(f"Applied v1 (transcripts only, call-records preserved): {n_tx} transcript(s)")
    else:
        print(
            f"Applied v1: {n_tx} transcript(s); call-records/ cleared "
            "(optional JSON via Extract Call Records playbook outside default E2E)"
        )

    if v2:
        p2 = _fixture_v2(root)
        if not p2.is_dir():
            raise FileNotFoundError(f"--v2 requested but missing {p2}")
        n_tx2 = _copy_files_only(p2 / "Transcripts", t_dst, "*.txt")
        print(
            "Applied v2: "
            f"{n_tx2} transcript(s); call-record JSON unchanged (optional Extract outside E2E)"
        )

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "to-fixtures",
        help="Snapshot MyNotes/Transcripts into tests/fixtures/.../v1/ (no call-records)",
    )

    p_ap = sub.add_parser("apply", help="Copy v1 (+ optional v2) into MyNotes")
    p_ap.add_argument(
        "--v2",
        action="store_true",
        help="Also merge tests/fixtures/e2e/_TEST_CUSTOMER/v2/ transcripts only (call-records are runtime-extracted)",
    )

    args = ap.parse_args()
    root = _repo_root()
    if args.cmd == "to-fixtures":
        return cmd_to_fixtures(root)
    if args.cmd == "apply":
        return cmd_apply(root, v2=args.v2)
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
