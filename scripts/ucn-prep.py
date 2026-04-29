#!/usr/bin/env python3
"""UCN prep: emit notes-lite.md + handoff.json for bounded Update Customer Notes context.

Implements `.cursor/plans/ucn-lookback-batch-ucn-prep.md` (single-script deliverable).

Modes:
  default (default subcommand) — notes-lite + ledger path + newest transcript + N priors; no migration state.
  bundle — optional _MASTER_* split, time buckets, migration-state.json + per-bundle handoff.

Examples:
  uv run python scripts/ucn-prep.py --customer "_TEST_CUSTOMER" --out MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/run1
  uv run python scripts/ucn-prep.py bundle --customer "_TEST_CUSTOMER" --window 1m --out .../batch-1m/run1
  uv run python scripts/ucn-prep.py bundle --customer "_TEST_CUSTOMER" --window 1m --out .../run1 --advance

Tests may set ``PRESTONOTES_REPO_ROOT`` to a temp tree so ``MyNotes/Customers/...`` resolves under that root.
``PRESTONOTES_UCN_PREP_OUT`` overrides ``--out`` when ``--out`` is omitted (same as default mode).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

_scripts_dir = Path(__file__).resolve().parent


def _load_granola_sync_module() -> Any:
    """``granola-sync.py`` is not a valid ``import`` module name; load by path."""
    path = _scripts_dir / "granola-sync.py"
    spec = importlib.util.spec_from_file_location("granola_sync_ucn_prep", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_gs = _load_granola_sync_module()
build_file_body = _gs.build_file_body
slugify_title = _gs.slugify_title
unique_filename = _gs.unique_filename

_SCRIPT_FILE = Path(__file__).resolve()
_REPO_ROOT = _SCRIPT_FILE.parents[1]
_MAX_LINE_LEN = 10_000
_HEAD_ACC = "# Account Summary"
_HEAD_DAL = "# Daily Activity Logs"
_HEAD_META = "# Account Metadata"
_PER_CALL_STEM = re.compile(r"^(\d{4}-\d{2}-\d{2})-.+\.txt$", re.IGNORECASE)
_MASTER_GLOB = "_MASTER_*.txt"


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _repo_root() -> Path:
    env = os.environ.get("PRESTONOTES_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return _REPO_ROOT


def customer_dir(repo: Path, customer: str) -> Path:
    return (repo / "MyNotes" / "Customers" / customer).resolve()


def discover_notes_md(cdir: Path, customer: str) -> Path | None:
    candidates = [
        cdir / f"{customer} Notes.md",
        cdir / f"{customer}-Notes.md",
    ]
    for p in candidates:
        if p.is_file():
            return p
    for p in sorted(cdir.glob("*Notes*.md")):
        if not p.is_file():
            continue
        if "History-Ledger" in p.name or "Full-Context" in p.name:
            continue
        return p
    return None


def ledger_path_default(cdir: Path, customer: str) -> Path:
    return (cdir / "AI_Insights" / f"{customer}-History-Ledger.md").resolve()


def filter_body_line(line: str) -> bool:
    if len(line) > _MAX_LINE_LEN:
        return False
    if "data:image/" in line:
        return False
    s = line.strip()
    if s.startswith("![") and "](" in s:
        return False
    return True


def splice_notes_lite(text: str) -> tuple[str, dict[str, Any]]:
    """Region A (Account Summary … before DAL) + Region C (Account Metadata … EOF); drop DAL."""
    lines = text.splitlines(keepends=True)
    dal_idx: int | None = None
    meta_idx: int | None = None
    acc_idx: int | None = None
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped == _HEAD_ACC and acc_idx is None:
            acc_idx = i
        if stripped == _HEAD_DAL and dal_idx is None:
            dal_idx = i
        if stripped == _HEAD_META and meta_idx is None:
            meta_idx = i

    region_a_start = acc_idx if acc_idx is not None else 0
    region_a_end = dal_idx if dal_idx is not None else len(lines)
    region_c_start = meta_idx if meta_idx is not None else len(lines)

    a_lines = lines[region_a_start:region_a_end]
    c_lines = lines[region_c_start:] if meta_idx is not None else []

    def apply_filters(chunk: list[str]) -> list[str]:
        return [ln for ln in chunk if filter_body_line(ln)]

    a_f = apply_filters(a_lines)
    c_f = apply_filters(c_lines)

    sep = (
        "\n\n---\n\n"
        "<!-- ucn-prep: above = Account Summary region (DAL omitted); below = Account Metadata region -->\n\n"
    )
    body = "".join(a_f).rstrip() + (sep + "".join(c_f).rstrip() if c_f else "")
    meta = {
        "had_daily_activity_heading": dal_idx is not None,
        "had_account_metadata_heading": meta_idx is not None,
        "had_account_summary_heading": acc_idx is not None,
        "region_a_lines": len(a_f),
        "region_c_lines": len(c_f),
    }
    return body, meta


def window_delta(window: str) -> timedelta:
    w = window.lower().strip()
    if w == "1w":
        return timedelta(days=7)
    if w == "1m":
        return timedelta(days=30)
    if w == "3m":
        return timedelta(days=90)
    if w == "1y":
        return timedelta(days=365)
    raise ValueError(f"unsupported --window {window!r}; use 1w|1m|3m|1y")


class MasterCall:
    __slots__ = ("title", "date_raw", "meeting_id", "body")

    def __init__(self, title: str, date_raw: str, meeting_id: str, body: str) -> None:
        self.title = title
        self.date_raw = date_raw
        self.meeting_id = meeting_id
        self.body = body


def parse_master_blocks(text: str) -> tuple[list[MasterCall], list[str]]:
    """Parse _MASTER_* Granola export blocks; return calls + warnings."""
    warnings: list[str] = []
    lines = text.splitlines()
    calls: list[MasterCall] = []
    i = 0

    def _sl(s: str) -> str:
        return s.strip()

    while i < len(lines):
        if not _sl(lines[i]).startswith("MEETING:"):
            i += 1
            continue
        title = _sl(lines[i])[len("MEETING:") :].strip()
        i += 1
        date_raw = ""
        meeting_id = ""
        if i < len(lines) and _sl(lines[i]).startswith("DATE:"):
            date_raw = _sl(lines[i])[len("DATE:") :].strip()
            i += 1
        if i < len(lines) and _sl(lines[i]).startswith("ID:"):
            meeting_id = _sl(lines[i])[len("ID:") :].strip()
            i += 1
        while i < len(lines) and lines[i].strip() and set(lines[i].strip()) <= {"="}:
            i += 1
        body_lines: list[str] = []
        while i < len(lines):
            if _sl(lines[i]).startswith("MEETING:"):
                break
            body_lines.append(lines[i])
            i += 1
        body = "\n".join(body_lines).strip()
        if not meeting_id or not date_raw:
            warnings.append(f"skip_master_block title={title[:80]!r}: missing DATE or ID")
            continue
        try:
            date.fromisoformat(date_raw[:10])
        except ValueError:
            warnings.append(f"skip_master_block title={title[:80]!r}: bad DATE {date_raw!r}")
            continue
        calls.append(MasterCall(title=title, date_raw=date_raw, meeting_id=meeting_id, body=body))
    return calls, warnings


def split_master_files(
    transcripts_dir: Path,
    *,
    dry_run: bool,
) -> tuple[list[Path], list[str]]:
    """Write per-call YYYY-MM-DD-<slug>.txt for each _MASTER_*.txt; return new paths + warnings."""
    written: list[Path] = []
    warnings: list[str] = []
    synced_iso = _utc_now_iso()
    for master in sorted(transcripts_dir.glob(_MASTER_GLOB)):
        if not master.is_file():
            continue
        raw = master.read_text(encoding="utf-8", errors="replace")
        blocks, w = parse_master_blocks(raw)
        warnings.extend(w)
        for b in blocks:
            date_str = b.date_raw[:10]
            slug = slugify_title(b.title, b.meeting_id)
            fname = unique_filename(transcripts_dir, date_str, slug, b.meeting_id)
            out_p = transcripts_dir / fname
            content = build_file_body(b.meeting_id, b.title, b.body, synced_iso=synced_iso)
            if dry_run:
                written.append(out_p)
                continue
            out_p.write_text(content, encoding="utf-8")
            written.append(out_p)
    return written, warnings


def list_per_call_transcripts(transcripts_dir: Path) -> list[Path]:
    out: list[Path] = []
    for p in transcripts_dir.glob("*.txt"):
        if not p.is_file():
            continue
        if p.name.startswith("_MASTER_"):
            continue
        if _PER_CALL_STEM.match(p.name):
            out.append(p)
    return out


def transcript_meeting_date(p: Path) -> date | None:
    m = _PER_CALL_STEM.match(p.name)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def sort_transcripts_chrono(paths: Iterable[Path]) -> list[Path]:
    dated: list[tuple[date, Path]] = []
    undated: list[Path] = []
    for p in paths:
        d = transcript_meeting_date(p)
        if d is None:
            undated.append(p)
        else:
            dated.append((d, p))
    dated.sort(key=lambda x: (x[0], x[1].name))
    undated.sort(key=lambda x: x.name)
    return [p for _, p in dated] + undated


def sort_transcripts_newest_first(paths: Iterable[Path]) -> list[Path]:
    chrono = sort_transcripts_chrono(paths)
    return list(reversed(chrono))


def corpus_fingerprint(paths: list[Path]) -> str:
    stems = sorted(p.resolve().as_posix() for p in paths)
    h = hashlib.sha256("\n".join(stems).encode("utf-8")).hexdigest()
    return h


def partition_bundles(
    sorted_chrono: list[Path],
    window: str,
) -> list[dict[str, Any]]:
    """Non-overlapping [start,end) buckets along timeline from oldest meeting date."""
    if not sorted_chrono:
        return []
    delta = window_delta(window)
    dates = [transcript_meeting_date(p) for p in sorted_chrono]
    real_dates = [d for d in dates if d is not None]
    if not real_dates:
        return [
            {
                "id": "b0",
                "date_start": "",
                "date_end": "",
                "transcript_paths": [str(p.resolve()) for p in sorted_chrono],
            }
        ]
    cursor_start = min(real_dates)
    max_d = max(real_dates)
    bundles: list[dict[str, Any]] = []
    bid = 0
    while cursor_start <= max_d:
        cursor_end = cursor_start + delta
        in_bucket: list[Path] = []
        for p in sorted_chrono:
            d = transcript_meeting_date(p)
            if d is None:
                continue
            if cursor_start <= d < cursor_end:
                in_bucket.append(p)
        if in_bucket:
            paths_str = [str(p.resolve()) for p in in_bucket]
            bundles.append(
                {
                    "id": f"b{bid}",
                    "date_start": cursor_start.isoformat(),
                    "date_end": (cursor_end - timedelta(days=1)).isoformat(),
                    "transcript_paths": paths_str,
                }
            )
            bid += 1
        cursor_start = cursor_end
    undated = [p for p in sorted_chrono if transcript_meeting_date(p) is None]
    if undated and bundles:
        extra = [str(p.resolve()) for p in undated]
        bundles[0]["transcript_paths"] = extra + list(bundles[0]["transcript_paths"])
    elif undated and not bundles:
        bundles.append(
            {
                "id": "b0",
                "date_start": "",
                "date_end": "",
                "transcript_paths": [str(p.resolve()) for p in undated],
            }
        )
    return bundles


def pick_default_transcripts(transcripts_dir: Path, priors: int) -> tuple[list[Path], list[str]]:
    warnings: list[str] = []
    masters = list(transcripts_dir.glob(_MASTER_GLOB))
    if masters:
        warnings.append(
            "_MASTER_*.txt present: default mode does not split; use `bundle` or split manually."
        )
    ranked = sort_transcripts_newest_first(list_per_call_transcripts(transcripts_dir))
    if not ranked:
        return [], warnings
    take = min(len(ranked), 1 + max(0, priors))
    return ranked[:take], warnings


def write_handoff_and_notes(
    *,
    out_dir: Path,
    customer: str,
    mode: str,
    notes_lite_text: str,
    ledger_p: Path,
    transcript_paths: list[Path],
    bundle_id: str | None,
    extra_warnings: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
    notes_path = out_dir / "notes-lite.md"
    handoff_path = out_dir / "handoff.json"
    warnings = list(extra_warnings)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "customer": customer,
        "generated_at": _utc_now_iso(),
        "mode": mode,
        "notes_lite_path": str(notes_path.resolve()),
        "ledger_path": str(ledger_p),
        "transcript_paths": [str(p.resolve()) for p in transcript_paths],
        "bundle_id": bundle_id,
        "warnings": warnings,
    }
    if dry_run:
        payload["dry_run"] = True
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return payload
    notes_path.write_text(notes_lite_text, encoding="utf-8")
    handoff_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return payload


def cmd_default(args: argparse.Namespace) -> int:
    repo = _repo_root()
    cdir = customer_dir(repo, args.customer)
    if not cdir.is_dir():
        print(json.dumps({"error": "customer_dir_not_found", "path": str(cdir)}), file=sys.stderr)
        return 2
    tdir = cdir / "Transcripts"
    if not tdir.is_dir():
        print(
            json.dumps({"error": "transcripts_dir_not_found", "path": str(tdir)}), file=sys.stderr
        )
        return 2

    if args.out and str(args.out).strip():
        out = Path(args.out).expanduser().resolve()
    else:
        env_out = os.environ.get("PRESTONOTES_UCN_PREP_OUT", "").strip()
        out = (
            Path(env_out).expanduser().resolve()
            if env_out
            else Path(tempfile.mkdtemp(prefix=f"prestonotes-ucn-prep-{args.customer}-"))
        )

    notes_p = discover_notes_md(cdir, args.customer)
    if not notes_p:
        print(
            json.dumps({"error": "notes_md_not_found", "customer": args.customer}), file=sys.stderr
        )
        return 2
    raw_notes = notes_p.read_text(encoding="utf-8", errors="replace")
    lite, splice_meta = splice_notes_lite(raw_notes)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "notes_lite_line_count": len(lite.splitlines()),
                    "splice": splice_meta,
                },
                indent=2,
            ),
            file=sys.stderr,
        )

    ledger_p = ledger_path_default(cdir, args.customer)
    priors = int(getattr(args, "priors", 2))
    tpaths, warns = pick_default_transcripts(tdir, priors)
    if not tpaths:
        warns.append("no_per_call_transcripts_YyyyMmDd_found")

    write_handoff_and_notes(
        out_dir=out,
        customer=args.customer,
        mode="default",
        notes_lite_text=lite,
        ledger_p=ledger_p,
        transcript_paths=tpaths,
        bundle_id=None,
        extra_warnings=warns,
        dry_run=bool(args.dry_run),
    )
    return 0


def load_migration_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_migration_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_bundle(args: argparse.Namespace) -> int:
    repo = _repo_root()
    cdir = customer_dir(repo, args.customer)
    if not cdir.is_dir():
        print(json.dumps({"error": "customer_dir_not_found", "path": str(cdir)}), file=sys.stderr)
        return 2
    tdir = cdir / "Transcripts"
    if not tdir.is_dir():
        print(
            json.dumps({"error": "transcripts_dir_not_found", "path": str(tdir)}), file=sys.stderr
        )
        return 2

    if args.out and str(args.out).strip():
        out = Path(args.out).expanduser().resolve()
    else:
        env_out = os.environ.get("PRESTONOTES_UCN_PREP_OUT", "").strip()
        out = (
            Path(env_out).expanduser().resolve()
            if env_out
            else Path(tempfile.mkdtemp(prefix=f"prestonotes-ucn-prep-bundle-{args.customer}-"))
        )

    split_warns: list[str] = []
    if list(tdir.glob(_MASTER_GLOB)):
        _, split_warns = split_master_files(tdir, dry_run=bool(args.dry_run))

    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)

    per_call = list_per_call_transcripts(tdir)
    sorted_chrono = sort_transcripts_chrono(per_call)
    bundles = partition_bundles(sorted_chrono, args.window)
    corpus_hash = corpus_fingerprint(per_call)
    state_path = out / "migration-state.json"

    prior_state = load_migration_state(state_path)
    rebuilt = (
        prior_state is None
        or prior_state.get("corpus_hash") != corpus_hash
        or prior_state.get("window") != args.window
    )
    if rebuilt:
        state: dict[str, Any] = {
            "version": 1,
            "customer": args.customer,
            "window": args.window,
            "corpus_hash": corpus_hash,
            "updated_at": _utc_now_iso(),
            "bundles": bundles,
            "current_bundle_id": bundles[0]["id"] if bundles else None,
            "completed_bundle_ids": [],
        }
        if not args.dry_run:
            save_migration_state(state_path, state)
    else:
        state = prior_state  # type: ignore[assignment]

    if args.advance and not rebuilt and not args.dry_run:
        cur = state.get("current_bundle_id")
        completed = list(state.get("completed_bundle_ids") or [])
        if cur and cur not in completed:
            completed.append(cur)
        ids_in_order = [b["id"] for b in state.get("bundles") or []]
        next_id: str | None = None
        if cur in ids_in_order:
            idx = ids_in_order.index(cur)
            if idx + 1 < len(ids_in_order):
                next_id = ids_in_order[idx + 1]
        else:
            next_id = ids_in_order[0] if ids_in_order else None
        state["completed_bundle_ids"] = completed
        state["current_bundle_id"] = next_id
        state["updated_at"] = _utc_now_iso()
        save_migration_state(state_path, state)

    cur_id = state.get("current_bundle_id")
    bundle_paths: list[Path] = []
    for b in state.get("bundles") or []:
        if b.get("id") == cur_id:
            bundle_paths = [Path(p) for p in (b.get("transcript_paths") or [])]
            break

    notes_p = discover_notes_md(cdir, args.customer)
    if not notes_p:
        print(
            json.dumps({"error": "notes_md_not_found", "customer": args.customer}), file=sys.stderr
        )
        return 2
    lite, _ = splice_notes_lite(notes_p.read_text(encoding="utf-8", errors="replace"))
    ledger_p = ledger_path_default(cdir, args.customer)
    warns = list(split_warns)
    if not bundles:
        warns.append("empty_transcript_corpus_after_split")

    write_handoff_and_notes(
        out_dir=out,
        customer=args.customer,
        mode="bundle",
        notes_lite_text=lite,
        ledger_p=ledger_p,
        transcript_paths=bundle_paths,
        bundle_id=cur_id,
        extra_warnings=warns,
        dry_run=bool(args.dry_run),
    )
    if args.dry_run:
        print(
            json.dumps({"migration_state_preview": state}, indent=2, ensure_ascii=False),
            file=sys.stderr,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="UCN prep — notes-lite + handoff.json")
    p.add_argument(
        "--customer", required=True, help="Customer folder name under MyNotes/Customers/"
    )
    p.add_argument(
        "--out", default="", help="Output directory (default: temp dir or PRESTONOTES_UCN_PREP_OUT)"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Print plans; skip writing files when set"
    )
    p.add_argument(
        "--priors",
        type=int,
        default=2,
        help="With implicit default mode: older per-call transcripts after newest (default: 2)",
    )
    sub = p.add_subparsers(dest="command", required=False)

    d = sub.add_parser(
        "default",
        help="Steady-state UCN prep (notes-lite + ledger + newest + N priors); same as top-level with no subcommand",
    )
    d.set_defaults(func=cmd_default)

    b = sub.add_parser("bundle", help="Migration-style bundles + optional _MASTER_ split")
    b.add_argument(
        "--window",
        required=True,
        choices=["1w", "1m", "3m", "1y"],
        help="Bucket size along timeline",
    )
    b.add_argument(
        "--advance",
        action="store_true",
        help="Mark current bundle complete and move to next (updates migration-state.json); no-op on fresh state",
    )
    b.set_defaults(func=cmd_bundle)

    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        return cmd_default(args)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
