#!/usr/bin/env python3
"""Export Granola (macOS) local cache into per-call MyNotes Transcripts/*.txt files.

Reads ~/Library/Application Support/Granola/cache-v4.json (or v3), or GRANOLA_CACHE_PATH.
Writes: {GDRIVE_BASE_PATH}/Customers/<folder-name>/Transcripts/YYYY-MM-DD-<slug>.txt

See docs/MIGRATION_GUIDE.md for cache format notes and Internal-folder routing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SLUG_MAX = 80
_SAFE_CUSTOMER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _\-]{0,63}$")


def unwrap_granola_cache(raw: dict[str, Any]) -> dict[str, Any]:
    if "cache" in raw and isinstance(raw["cache"], str):
        inner = json.loads(raw["cache"])
        return inner.get("state", inner) if isinstance(inner, dict) else {}
    if "state" in raw and isinstance(raw["state"], dict):
        return raw["state"]
    return raw


def load_cache_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return unwrap_granola_cache(raw)


def parse_transcript_segments(data: Any) -> str:
    parts: list[str] = []
    if isinstance(data, list):
        for segment in data:
            if isinstance(segment, dict) and segment.get("text"):
                t = str(segment["text"]).strip()
                if t:
                    parts.append(t)
    elif isinstance(data, dict):
        for key in ("content", "text", "transcript"):
            if data.get(key):
                parts.append(str(data[key]))
                break
    return "\n\n".join(parts) if parts else ""


def extract_notes_plain(doc: dict[str, Any]) -> str:
    if doc.get("notes_plain"):
        return str(doc["notes_plain"]).strip()
    if doc.get("notes_markdown"):
        return str(doc["notes_markdown"]).strip()
    notes = doc.get("notes")
    if isinstance(notes, dict):
        return _extract_structured_notes(notes).strip()
    return ""


def _extract_structured_notes(notes_data: dict[str, Any]) -> str:
    if "content" not in notes_data:
        return ""

    def _walk(content_list: Any) -> list[str]:
        parts: list[str] = []
        if isinstance(content_list, list):
            for item in content_list:
                if isinstance(item, dict):
                    if item.get("type") == "text" and "text" in item:
                        parts.append(str(item["text"]))
                    elif "content" in item:
                        parts.append(_walk(item["content"]))
        return parts

    try:
        return " ".join(_walk(notes_data["content"]))
    except Exception:
        return ""


def meeting_date_from_doc(doc: dict[str, Any]) -> datetime:
    raw = doc.get("created_at") or doc.get("updated_at")
    if isinstance(raw, str) and raw:
        s = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            pass
    return datetime.now(tz=timezone.utc)


def slugify_title(title: str, meeting_id: str) -> str:
    base = (title or "meeting").strip().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if not base:
        base = "meeting"
    if len(base) > _SLUG_MAX:
        base = base[:_SLUG_MAX].rstrip("-")
    return base or meeting_id[:12]


def _internal_folder_names() -> frozenset[str]:
    raw = os.environ.get("GRANOLA_INTERNAL_FOLDER_NAMES", "internal")
    return frozenset(x.strip().lower() for x in raw.split(",") if x.strip())


def pick_customer_from_folders(
    doc: dict[str, Any],
    *,
    default_customer: str | None,
) -> str | None:
    folders = doc.get("folders")
    if not isinstance(folders, list) or not folders:
        return default_customer
    first = folders[0]
    if not isinstance(first, dict):
        return default_customer
    name = str(first.get("name", "") or "").strip()
    if not name:
        return default_customer
    if name.lower() in _internal_folder_names():
        return os.environ.get("GRANOLA_INTERNAL_CUSTOMER_NAME", "Internal")
    if not _SAFE_CUSTOMER.match(name):
        return None
    if ".." in name or "/" in name or "\\" in name:
        return None
    return name


def _existing_meeting_id(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return None
    for line in head.splitlines():
        if line.startswith("granola_meeting_id:"):
            rest = line.split(":", 1)[1].strip().strip('"')
            return rest or None
    return None


def unique_filename(out_dir: Path, date_str: str, slug: str, meeting_id: str) -> str:
    """Prefer `DATE-slug.txt`; overwrite if same meeting_id. If name taken by another meeting, disambiguate."""
    base = f"{date_str}-{slug}.txt"
    path = out_dir / base
    if not path.exists():
        return base
    prev = _existing_meeting_id(path)
    if prev == meeting_id:
        return base
    short = meeting_id[:8] if len(meeting_id) >= 8 else meeting_id
    return f"{date_str}-{slug}-{short}.txt"


def build_file_body(meeting_id: str, title: str, body: str, *, synced_iso: str) -> str:
    header = (
        "---\n"
        f'granola_meeting_id: "{meeting_id}"\n'
        f"title: {json.dumps(title)}\n"
        f"granola_synced_at: {synced_iso}\n"
        "---\n\n"
    )
    return header + body


def default_cache_candidates() -> list[Path]:
    home = Path.home()
    return [
        home / "Library/Application Support/Granola/cache-v4.json",
        home / "Library/Application Support/Granola/cache-v3.json",
    ]


def resolve_cache_path(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit if explicit.is_file() else None
    env = os.environ.get("GRANOLA_CACHE_PATH", "").strip()
    if env:
        p = Path(env)
        return p if p.is_file() else None
    for c in default_cache_candidates():
        if c.is_file():
            return c
    return None


def sync_granola_to_mynotes(
    *,
    cache_path: Path,
    customers_base: Path,
    dry_run: bool,
    emit_notes_without_transcript: bool,
    default_customer: str | None,
) -> dict[str, Any]:
    state = load_cache_path(cache_path)
    documents: dict[str, Any] = state.get("documents") or {}
    transcripts: dict[str, Any] = state.get("transcripts") or {}
    synced_iso = datetime.now(tz=timezone.utc).isoformat()

    written: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for meeting_id in sorted(documents.keys()):
        doc = documents.get(meeting_id)
        if not isinstance(doc, dict):
            continue
        title = str(doc.get("title") or "Untitled Meeting")
        tr_raw = transcripts.get(meeting_id)
        transcript = parse_transcript_segments(tr_raw) if tr_raw is not None else ""
        if not transcript and emit_notes_without_transcript:
            transcript = extract_notes_plain(doc)
        if not transcript.strip():
            skipped.append(
                {
                    "meeting_id": meeting_id,
                    "reason": "no_transcript_or_notes",
                }
            )
            continue

        customer = pick_customer_from_folders(doc, default_customer=default_customer)
        if not customer:
            skipped.append({"meeting_id": meeting_id, "reason": "no_customer_for_folder"})
            continue

        dt = meeting_date_from_doc(doc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        date_str = dt.date().isoformat()
        slug = slugify_title(title, meeting_id)

        cust_dir = (customers_base / "Customers" / customer / "Transcripts").resolve()
        try:
            cust_dir.relative_to(customers_base.resolve())
        except ValueError:
            errors.append({"meeting_id": meeting_id, "error": "invalid customer path"})
            continue

        if not dry_run:
            cust_dir.mkdir(parents=True, exist_ok=True)
        fname = unique_filename(cust_dir, date_str, slug, meeting_id)
        out_path = cust_dir / fname
        content = build_file_body(meeting_id, title, transcript, synced_iso=synced_iso)

        if dry_run:
            written.append(
                {
                    "meeting_id": meeting_id,
                    "path": str(out_path),
                    "bytes": len(content.encode("utf-8")),
                    "dry_run": True,
                }
            )
        else:
            out_path.write_text(content, encoding="utf-8")
            written.append(
                {
                    "meeting_id": meeting_id,
                    "path": str(out_path),
                    "bytes": out_path.stat().st_size,
                    "dry_run": False,
                }
            )

    return {
        "cache_path": str(cache_path),
        "customers_base": str(customers_base),
        "written": written,
        "skipped": skipped,
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Granola cache → MyNotes per-call transcripts.")
    p.add_argument(
        "--cache",
        type=Path,
        default=None,
        help="Path to cache-v4.json (default: GRANOLA_CACHE_PATH or ~/Library/.../cache-v4.json)",
    )
    p.add_argument(
        "--customers-base",
        type=Path,
        default=None,
        help="MyNotes root (contains Customers/). Default: GDRIVE_BASE_PATH env.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; report planned paths.",
    )
    p.add_argument(
        "--emit-notes-without-transcript",
        action="store_true",
        help="If set, use Granola notes when transcript segments are empty.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = _parse_args(argv)
    base = args.customers_base
    if base is None:
        gb = os.environ.get("GDRIVE_BASE_PATH", "").strip()
        if not gb:
            print(
                json.dumps(
                    {
                        "error": "GDRIVE_BASE_PATH is not set",
                        "hint": "Set to your local MyNotes root (see .cursor/mcp.env GDRIVE_BASE_PATH).",
                    }
                ),
                file=sys.stderr,
            )
            return 1
        base = Path(gb)
    cache = resolve_cache_path(args.cache)
    if cache is None:
        print(
            json.dumps(
                {
                    "error": "Granola cache file not found",
                    "hint": "Install Granola on macOS, open a meeting, or set GRANOLA_CACHE_PATH.",
                    "tried": [
                        str(p) for p in ([args.cache] if args.cache else default_cache_candidates())
                    ],
                }
            ),
            file=sys.stderr,
        )
        return 1

    default_customer = os.environ.get("GRANOLA_DEFAULT_CUSTOMER", "").strip() or None
    result = sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=base,
        dry_run=bool(args.dry_run),
        emit_notes_without_transcript=bool(args.emit_notes_without_transcript),
        default_customer=default_customer,
    )
    print(json.dumps(result, indent=2))
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
