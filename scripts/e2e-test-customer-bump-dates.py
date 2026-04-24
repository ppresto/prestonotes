#!/usr/bin/env python3
"""Roll per-call transcript filenames + §7.1 call records forward so E2E stays inside a lookback window.

Rewrites ``MyNotes/Customers/<customer>/Transcripts/YYYY-MM-DD-*.txt`` basenames to fresh dates
(UTC calendar math), updates the ``DATE:`` header line when present, and updates matching
``call-records/*.json`` (``call_id``, ``date``, ``raw_transcript_ref``).

Optional ``--incremental-gap`` deletes **one** call record JSON (default: lexicographically last
``call_id``) so **Extract Call Records** can prove incremental repair."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_PER_CALL_TXT = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.txt$")


def _repo_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    import os

    r = os.environ.get("PRESTONOTES_REPO_ROOT", "").strip()
    if r:
        return Path(r).expanduser().resolve()
    return Path.cwd().resolve()


@dataclass(frozen=True)
class PerCallTxt:
    path: Path
    old_date: date
    slug: str

    @property
    def old_stem(self) -> str:
        return f"{self.old_date.isoformat()}-{self.slug}"


def _spacing_days(n: int) -> list[int]:
    """Return ``n`` day-offsets in (1, 30], oldest → newest spacing."""
    if n <= 0:
        return []
    if n == 1:
        return [3]
    out: list[int] = []
    for i in range(n):
        # Spread between ~3d and ~28d ago.
        out.append(3 + int((25 * i) / max(n - 1, 1)))
    return out


def _assign_target_dates(files: list[PerCallTxt], *, today: date) -> dict[str, date]:
    """Map old stem (YYYY-MM-DD-slug) -> new date (same slug)."""
    ordered = sorted(files, key=lambda p: (p.old_date, p.slug))
    offs = _spacing_days(len(ordered))
    mapping: dict[str, date] = {}
    for p, off in zip(ordered, offs, strict=True):
        mapping[p.old_stem] = today - timedelta(days=int(off))
    return mapping


def _update_transcript_date_header(text: str, new_day: date) -> str:
    """Replace first ``DATE: ...`` line (if any) with noon UTC ISO timestamp on ``new_day``."""
    iso = f"{new_day.isoformat()}T12:00:00.000Z"
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    replaced = False
    for line in lines:
        if not replaced and line.startswith("DATE:"):
            out.append(f"DATE: {iso}\n" if line.endswith("\n") else f"DATE: {iso}")
            replaced = True
        else:
            out.append(line)
    return "".join(out)


def bump_fixture_dates(
    root: Path,
    *,
    customer: str,
    incremental_gap: bool,
    gap_call_id: str | None,
    dry_run: bool,
) -> dict[str, object]:
    cdir = root / "MyNotes" / "Customers" / customer
    tdir = cdir / "Transcripts"
    if not tdir.is_dir():
        raise FileNotFoundError(f"Missing Transcripts dir: {tdir}")

    today = datetime.now(timezone.utc).date()
    files: list[PerCallTxt] = []
    for p in sorted(tdir.glob("*.txt")):
        m = _PER_CALL_TXT.match(p.name)
        if not m:
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        files.append(PerCallTxt(path=p, old_date=d, slug=m.group(2)))

    if not files:
        raise FileNotFoundError(f"No per-call transcripts matching YYYY-MM-DD-*.txt under {tdir}")

    stem_to_new_date = _assign_target_dates(files, today=today)

    # Two-phase renames to avoid collisions.
    tmp_suffix = ".__bump_tmp__"
    plan: list[tuple[Path, Path, date]] = []
    for p in files:
        new_day = stem_to_new_date[p.old_stem]
        new_path = tdir / f"{new_day.isoformat()}-{p.slug}.txt"
        plan.append((p.path, new_path, new_day))

    if dry_run:
        return {
            "dry_run": True,
            "customer": customer,
            "today": today.isoformat(),
            "transcript_moves": [f"{a.name} -> {b.name}" for a, b, _ in plan],
        }

    phase1: list[tuple[Path, Path]] = []
    for src, dst, _ in plan:
        if src.resolve() == dst.resolve():
            continue
        tmp = src.with_name(src.name + tmp_suffix)
        src.rename(tmp)
        phase1.append((tmp, dst))

    for tmp, dst in phase1:
        tmp.rename(dst)

    stem_map: dict[str, str] = {}
    for p in files:
        new_day = stem_to_new_date[p.old_stem]
        old_stem = p.old_stem
        new_stem = f"{new_day.isoformat()}-{p.slug}"
        stem_map[old_stem] = new_stem

    # Refresh transcript headers for every per-call transcript (even if basename did not change).
    for _, dst, new_day in plan:
        text = dst.read_text(encoding="utf-8")
        dst.write_text(_update_transcript_date_header(text, new_day), encoding="utf-8")

    crdir = cdir / "call-records"
    json_updates = 0
    if crdir.is_dir():
        record_paths = sorted(crdir.glob("*.json"))
        for jp in record_paths:
            try:
                data = json.loads(jp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue

            old_stem = str(data.get("call_id", jp.stem)).strip()
            if old_stem not in stem_map:
                ref = str(data.get("raw_transcript_ref", "")).strip()
                if ref.endswith(".txt"):
                    old_stem = ref[: -len(".txt")]
            new_stem = stem_map.get(old_stem)
            if not new_stem:
                continue

            new_day = date.fromisoformat(new_stem[:10])
            changed = False
            if str(data.get("call_id", "")).strip() != new_stem:
                data["call_id"] = new_stem
                changed = True
            if str(data.get("date", "")).strip() != new_day.isoformat():
                data["date"] = new_day.isoformat()
                changed = True
            if str(data.get("raw_transcript_ref", "")).strip() != f"{new_stem}.txt":
                data["raw_transcript_ref"] = f"{new_stem}.txt"
                changed = True
            if str(data.get("extraction_date", "")).strip():
                data["extraction_date"] = today.isoformat()
                changed = True

            payload = json.dumps(data, indent=2) + "\n"
            new_jp = crdir / f"{new_stem}.json"
            if new_jp.resolve() != jp.resolve():
                if new_jp.exists():
                    raise RuntimeError(f"Refusing to overwrite existing call record: {new_jp}")
                jp.write_text(payload, encoding="utf-8")
                jp.rename(new_jp)
                json_updates += 1
            elif changed:
                jp.write_text(payload, encoding="utf-8")
                json_updates += 1

    removed: str | None = None
    if incremental_gap:
        cr2 = cdir / "call-records"
        if not cr2.is_dir():
            raise FileNotFoundError(f"Missing call-records dir: {cr2}")
        candidates = sorted(cr2.glob("*.json"))
        if not candidates:
            raise FileNotFoundError("incremental-gap requested but call-records/*.json is empty")
        if gap_call_id:
            victim = cr2 / f"{gap_call_id}.json"
            if not victim.is_file():
                raise FileNotFoundError(f"--gap-call-id not found: {victim}")
        else:
            # Default: delete lexicographically last call_id (matches YYYY-MM-DD-* sort).
            parsed_ids: list[tuple[str, Path]] = []
            for p in candidates:
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if isinstance(d, dict) and d.get("call_id"):
                    parsed_ids.append((str(d["call_id"]), p))
            if not parsed_ids:
                victim = candidates[-1]
            else:
                victim = max(parsed_ids, key=lambda t: t[0])[1]
        removed = victim.name
        victim.unlink()

    return {
        "dry_run": False,
        "customer": customer,
        "today": today.isoformat(),
        "per_call_transcripts": len(files),
        "json_objects_touched": json_updates,
        "incremental_gap_removed": removed,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=None)
    p.add_argument("--customer", default="_TEST_CUSTOMER")
    p.add_argument(
        "--incremental-gap",
        action="store_true",
        help="Delete one call record JSON after bumping (default target: max call_id).",
    )
    p.add_argument(
        "--gap-call-id",
        default=None,
        help="When combined with --incremental-gap, delete call-records/<id>.json (no .json suffix).",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true", help="Print machine-readable summary to stdout")
    args = p.parse_args()

    root = _repo_root(args.repo_root)
    try:
        out = bump_fixture_dates(
            root,
            customer=args.customer,
            incremental_gap=args.incremental_gap,
            gap_call_id=args.gap_call_id,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
