#!/usr/bin/env python3
"""Export Granola (macOS) local cache into per-call MyNotes Transcripts/*.txt files.

Reads ~/Library/Application Support/Granola/cache-v*.json (newest first; v6+ uses object ``cache``), or GRANOLA_CACHE_PATH.
Writes: {GDRIVE_BASE_PATH}/Customers/<folder-name>/Transcripts/YYYY-MM-DD-<slug>.txt

Granola v6 often keeps **few** entries in ``state.transcripts`` (only meetings with cached
segment lists). Most meetings still have **notes_plain** / **notes_markdown** when
``transcribe`` is off or the transcript has not landed in the JSON yet. By default this
script **falls back to notes** so those meetings export; use ``--transcript-only`` to
require segment-based transcript text only.

See scripts/README.md and docs/project_spec.md (Transcript files / §2) for layout and Internal-folder routing.
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
# Keep aligned with `prestonotes_mcp.security.validate_customer_name` defaults:
# allow a leading underscore for fixture customers like `_TEST_CUSTOMER`.
_SAFE_CUSTOMER = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9 _\-]{0,63}$")


def unwrap_granola_cache(raw: dict[str, Any]) -> dict[str, Any]:
    if "cache" in raw and isinstance(raw["cache"], str):
        inner = json.loads(raw["cache"])
        return inner.get("state", inner) if isinstance(inner, dict) else {}
    # cache-v6+: `cache` is a JSON object (see theantichris/granola#21), not a string blob.
    if "cache" in raw and isinstance(raw["cache"], dict):
        inner = raw["cache"]
        return inner.get("state", inner) if isinstance(inner, dict) else {}
    if "state" in raw and isinstance(raw["state"], dict):
        return raw["state"]
    return raw


def load_cache_path(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return unwrap_granola_cache(raw)


def _transcript_segment_text(segment: dict[str, Any]) -> str:
    """Granola segment text field varies by client/version."""
    for key in ("text", "content", "body", "value"):
        v = segment.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def parse_transcript_segments(data: Any, *, _unwrap_depth: int = 0) -> str:
    """Turn Granola transcript payload into plain text.

    Newer caches (including v6) sometimes store ``transcripts[meeting_id]`` as a **JSON string**
    holding the segment array (Go ``json.RawMessage`` style), not as a parsed list.
    """
    if data is None:
        return ""
    if _unwrap_depth > 8:
        return ""
    if isinstance(data, str):
        s = data.strip()
        if not s:
            return ""
        try:
            nested: Any = json.loads(s)
        except json.JSONDecodeError:
            return s
        return parse_transcript_segments(nested, _unwrap_depth=_unwrap_depth + 1)

    parts: list[str] = []
    if isinstance(data, list):
        for segment in data:
            if isinstance(segment, dict):
                t = _transcript_segment_text(segment)
                if t:
                    parts.append(t)
            elif isinstance(segment, str) and segment.strip():
                parts.append(segment.strip())
    elif isinstance(data, dict):
        for key in ("segments", "content", "text", "transcript"):
            val = data.get(key)
            if val is None:
                continue
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
                break
            if not isinstance(val, str):
                inner = parse_transcript_segments(val, _unwrap_depth=_unwrap_depth)
                if inner.strip():
                    parts.append(inner)
                    break
        if not parts:
            t = _transcript_segment_text(data)
            if t:
                parts.append(t)
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


def pick_customer_from_title_prefix(doc: dict[str, Any]) -> str | None:
    """When ``folders`` is missing in cache (common Granola v6), derive customer from ``title``.

    Uses the segment before the first ``" - "``, ``" – "``, em dash, ``":"``, or ``"|"`` when that
    segment passes the same safe-name rules as folder names. ``Internal`` (case-insensitive)
    maps to the Internal customer directory like folder-based routing.
    """
    title = str(doc.get("title") or "").strip()
    if not title:
        return None
    for sep in (" – ", " - ", "—", ":", "|"):
        if sep not in title:
            continue
        left = title.split(sep, 1)[0].strip()
        if not left or not _SAFE_CUSTOMER.match(left):
            return None
        if ".." in left or "/" in left or "\\" in left:
            return None
        if left.lower() in _internal_folder_names():
            return os.environ.get("GRANOLA_INTERNAL_CUSTOMER_NAME", "Internal")
        return left
    return None


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


def _granola_cache_version_rank(path: Path) -> int:
    m = re.match(r"^cache-v(\d+)\.json$", path.name, re.IGNORECASE)
    return int(m.group(1)) if m else -1


def default_cache_candidates() -> list[Path]:
    """Prefer newest ``cache-v*.json`` under Granola app support (v5+), else legacy v4/v3 paths."""
    home = Path.home()
    base = home / "Library/Application Support/Granola"
    if base.is_dir():
        found = sorted(
            (p for p in base.glob("cache-v*.json") if p.is_file()),
            key=_granola_cache_version_rank,
            reverse=True,
        )
        if found:
            return found
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


def _utc_log_ts() -> str:
    """UTC timestamp for log lines (minute resolution, ``…THH:MMZ``)."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


# Printed after the hash banner in ``granola-sync.log`` so long files stay self-documenting.
_LOG_APPEND_STATUS_LEGEND: tuple[str, ...] = (
    "# Status meanings (each data line is `YYYY-MM-DDTHH:MMZ STATUS: details`):",
    "#   RUN_START: — Start of this append block: Granola cache path, Drive customers root, notes_fb.",
    "#   RUN: — Run summary: exit, new/updated/skipped counts, cache doc counts, body=transcript|notes tallies, skip_reasons.",
    "#   SYNC_NEW: — Created a new file under …/Transcripts/.",
    "#   SYNC_UPD: — Rewrote an existing Transcripts file in place.",
    "#   SKIP: — Meeting not exported; reason/id/folder/title on the line.",
    "#   END: — End of this append block; repeats exit and new/updated/written/skipped counts.",
    "#   HINT: — Optional note (e.g. transcript index smaller than document count on Granola v6).",
    "#   SYNC: — No transcript files written this run (placeholder when the written list is empty).",
    "#   TRUNC: — SYNC or SKIP per-meeting lines were capped; see --log-max-lines.",
    "#   ERR: — Error detail recorded for this run.",
)


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\r", " ").replace("\n", " ")).strip()


def _log_line(status: str, detail: str) -> str:
    """One log line: ``{timestamp} {status}: {detail}`` (status examples: RUN, SYNC_NEW, SKIP)."""
    return f"{_utc_log_ts()} {status}: {_collapse_ws(detail)}"


def _written_label(w: dict[str, Any]) -> str:
    title = str(w.get("title") or "Untitled").strip()
    customer = str(w.get("customer") or "").strip()
    fname = str(w.get("filename") or "").strip()
    if customer and title:
        return f"{title} ({customer})"
    if fname:
        return fname
    return title or "meeting"


def _first_folder_name(doc: dict[str, Any]) -> str:
    folders = doc.get("folders")
    if not isinstance(folders, list) or not folders:
        return ""
    first = folders[0]
    if not isinstance(first, dict):
        return ""
    return str(first.get("name", "") or "").strip()


def sync_granola_to_mynotes(
    *,
    cache_path: Path,
    customers_base: Path,
    dry_run: bool,
    notes_fallback: bool = True,
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
        folder_dbg = _first_folder_name(doc)
        tr_raw = transcripts.get(meeting_id)
        if tr_raw is None and isinstance(doc, dict):
            tr_raw = doc.get("transcript")
        segment_text = parse_transcript_segments(tr_raw) if tr_raw is not None else ""
        body_source = "transcript"
        transcript = segment_text
        if not transcript.strip() and notes_fallback:
            transcript = extract_notes_plain(doc)
            if transcript.strip():
                body_source = "notes"
        if not transcript.strip():
            skipped.append(
                {
                    "meeting_id": meeting_id,
                    "reason": "no_transcript_or_notes",
                    "title": title[:200],
                    "folder": folder_dbg[:120],
                }
            )
            continue

        customer = pick_customer_from_folders(doc, default_customer=default_customer)
        if not customer and os.environ.get(
            "GRANOLA_TITLE_PREFIX_CUSTOMER", "1"
        ).strip().lower() not in {
            "0",
            "false",
            "no",
        }:
            customer = pick_customer_from_title_prefix(doc)
        if not customer:
            skipped.append(
                {
                    "meeting_id": meeting_id,
                    "reason": "no_customer_for_folder",
                    "title": title[:200],
                    "folder": folder_dbg[:120],
                }
            )
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
        is_new = not out_path.is_file()
        content = build_file_body(meeting_id, title, transcript, synced_iso=synced_iso)

        if dry_run:
            written.append(
                {
                    "meeting_id": meeting_id,
                    "path": str(out_path),
                    "filename": fname,
                    "title": title,
                    "customer": customer,
                    "is_new": is_new,
                    "bytes": len(content.encode("utf-8")),
                    "dry_run": True,
                    "body_source": body_source,
                }
            )
        else:
            out_path.write_text(content, encoding="utf-8")
            written.append(
                {
                    "meeting_id": meeting_id,
                    "path": str(out_path),
                    "filename": fname,
                    "title": title,
                    "customer": customer,
                    "is_new": is_new,
                    "bytes": out_path.stat().st_size,
                    "dry_run": False,
                    "body_source": body_source,
                }
            )

    body_counts: dict[str, int] = {}
    for w in written:
        src = str(w.get("body_source") or "unknown")
        body_counts[src] = body_counts.get(src, 0) + 1

    return {
        "cache_path": str(cache_path),
        "customers_base": str(customers_base),
        "written": written,
        "skipped": skipped,
        "errors": errors,
        "stats": {
            "documents_in_cache": len(documents),
            "transcript_index_size": len(transcripts),
            "notes_fallback_enabled": notes_fallback,
            "written_body_source": body_counts,
        },
    }


def _append_sync_logs(
    log_dir: Path,
    result: dict[str, Any],
    *,
    exit_code: int,
    write_last_json: bool,
    log_max_lines: int = 5000,
) -> None:
    """Append human-readable lines to ``granola-sync.log``.

    Each line is ``{timestamp} {STATUS}: {details}`` (``timestamp`` is UTC minute ``YYYY-MM-DDTHH:MMZ``).
    A hash-comment banner, a short status legend, then ``RUN_START`` mark each append block.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=timezone.utc).isoformat()
    payload = dict(result)
    payload["exit_code"] = exit_code
    payload["logged_at"] = stamp
    if write_last_json:
        (log_dir / "granola-sync-last.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    stats = result.get("stats") or {}
    written = result.get("written") or []
    skipped = result.get("skipped") or []
    errors = result.get("errors") or []
    n_new = sum(1 for w in written if w.get("is_new"))
    n_upd = len(written) - n_new

    reason_counts: dict[str, int] = {}
    for s in skipped:
        r = str(s.get("reason") or "unknown")
        reason_counts[r] = reason_counts.get(r, 0) + 1

    body_src = stats.get("written_body_source") or {}
    src_bits = ",".join(f"{k}={v}" for k, v in sorted(body_src.items())) if body_src else "none"

    lines: list[str] = [
        "# " + "=" * 78,
        "# Granola sync — new log append (scripts/granola-sync.py)",
        "# " + "=" * 78,
        "",
    ]
    lines.extend(_LOG_APPEND_STATUS_LEGEND)
    lines.append("")
    lines.append(
        _log_line(
            "RUN_START",
            "cache="
            + str(result.get("cache_path", "") or "")
            + " dest="
            + str(result.get("customers_base", "") or "")
            + f" notes_fb={stats.get('notes_fallback_enabled', '?')}",
        )
    )
    lines.append(
        _log_line(
            "RUN",
            f"exit={exit_code} new={n_new} updated={n_upd} skipped={len(skipped)} "
            f"written_total={len(written)} "
            f"docs={stats.get('documents_in_cache', '?')} "
            f"tr_index={stats.get('transcript_index_size', '?')} "
            f"bodies={{{src_bits}}} "
            f"skip_reasons={json.dumps(reason_counts, separators=(',', ':'), sort_keys=True)}",
        )
    )
    if stats.get("transcript_index_size") not in (None, "?") and int(
        stats["transcript_index_size"] or 0
    ) < int(stats.get("documents_in_cache") or 0):
        lines.append(
            _log_line(
                "HINT",
                "tr_index<<docs is common on Granola v6; body=notes uses notes_plain/markdown. "
                "Use --transcript-only for segment transcripts only.",
            )
        )

    w_cap = min(len(written), max(0, log_max_lines))
    for w in written[:w_cap]:
        st = "SYNC_NEW" if w.get("is_new") else "SYNC_UPD"
        src = str(w.get("body_source") or "?")
        mid = str(w.get("meeting_id", ""))
        cust = str(w.get("customer", "") or "")
        ttl = str(w.get("title", "") or "")
        fn = str(w.get("filename", "") or "")
        pth = str(w.get("path", "") or "")
        lines.append(
            _log_line(
                st,
                f"title={ttl!r}, file={fn!r}, path={pth}, customer={cust!r}, body={src}, "
                f"bytes={w.get('bytes', 0)}, id={mid}",
            )
        )
    if len(written) > w_cap:
        lines.append(_log_line("TRUNC", f"scope=SYNC shown={w_cap} total_written={len(written)}"))

    if not written:
        lines.append(_log_line("SYNC", "none (0 files written this run)"))

    s_cap = min(len(skipped), max(0, log_max_lines))
    for s in skipped[:s_cap]:
        mid = str(s.get("meeting_id", ""))
        reason = str(s.get("reason", ""))
        fld = str(s.get("folder", "") or "")
        ttl = str(s.get("title", "") or "")
        lines.append(
            _log_line(
                "SKIP",
                f"reason={reason}, id={mid}, folder={fld!r}, title={ttl!r}",
            )
        )
    if len(skipped) > s_cap:
        lines.append(_log_line("TRUNC", f"scope=SKIP shown={s_cap} total_skipped={len(skipped)}"))

    for e in errors:
        lines.append(_log_line("ERR", repr(e)))

    lines.append(
        _log_line(
            "END",
            f"exit={exit_code} new={n_new} updated={n_upd} written={len(written)} skipped={len(skipped)}",
        )
    )
    lines.append("")

    with (log_dir / "granola-sync.log").open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _format_notify_stdout(result: dict[str, Any], *, max_chars: int = 280) -> str:
    """Single-line (or short) summary for macOS Shortcuts / desktop notifications."""
    errors = result.get("errors") or []
    if errors:
        msg = (
            f"Granola sync: failed with {len(errors)} error(s). "
            "See logs/granola-sync.log (and stderr)."
        )
        return msg if len(msg) <= max_chars else msg[: max_chars - 1].rstrip() + "…"
    written = result.get("written") or []
    if not written:
        skipped = len(result.get("skipped") or [])
        if skipped:
            return f"Granola sync: nothing written ({skipped} meeting(s) skipped)."
        return "Granola sync: no meetings exported."
    new = [w for w in written if w.get("is_new")]
    updated = [w for w in written if not w.get("is_new")]
    if not new and updated:
        return f"Granola sync: {len(updated)} file(s) updated in place, 0 new."
    if new and not updated:
        body = "Granola sync — New: " + "; ".join(_written_label(w) for w in new)
        if len(body) <= max_chars:
            return body
        return body[: max_chars - 1].rstrip() + "…"
    if new and updated:
        return f"Granola sync: {len(new)} new, {len(updated)} updated in place."
    return "Granola sync: done."


def _emit_human_sync_summary(result: dict[str, Any], *, max_paths: int = 40) -> None:
    """stderr lines for operators; stdout stays JSON-only.

    When every write is an in-place update (no new files), print one short line instead of
    listing every path — details are in ``granola-sync.log``.
    """
    written = result.get("written") or []
    skipped = result.get("skipped") or []
    errors = result.get("errors") or []
    if written:
        new = [w for w in written if w.get("is_new")]
        upd = [w for w in written if not w.get("is_new")]
        print("", file=sys.stderr)
        if new:
            for i, w in enumerate(new):
                if i >= max_paths:
                    print(f"… and {len(new) - max_paths} more new file(s).", file=sys.stderr)
                    break
                prefix = "(dry-run) " if w.get("dry_run") else ""
                print(f"{prefix}Wrote (new): {w['path']}", file=sys.stderr)
        if upd and not new:
            prefix = "(dry-run) " if upd[0].get("dry_run") else ""
            print(
                f"{prefix}Refreshed {len(upd)} transcript file(s) in place (no new files). "
                "See logs/granola-sync.log for per-file SYNC_UPD lines.",
                file=sys.stderr,
            )
        elif upd and new:
            print(
                f"Also refreshed {len(upd)} existing transcript file(s) in place. "
                "See logs/granola-sync.log for SYNC_UPD lines.",
                file=sys.stderr,
            )
        print(f"Done: {len(new)} new, {len(upd)} updated ({len(written)} total).", file=sys.stderr)
    elif errors:
        print("", file=sys.stderr)
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
    elif skipped:
        print(
            f"No files written; {len(skipped)} meeting(s) skipped "
            "(no transcript or notes text, no customer folder, or unsafe folder name). "
            "Default uses notes when segment transcripts are missing; "
            "see logs/granola-sync.log for per-meeting reasons. "
            "Use --transcript-only if you require segment transcripts only.",
            file=sys.stderr,
        )
    else:
        print(
            "No meetings in cache (empty documents). "
            "Open Granola once, or set GRANOLA_CACHE_PATH to a cache file that contains meetings.",
            file=sys.stderr,
        )


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
        "--transcript-only",
        action="store_true",
        help="Only export meetings that have segment transcript text in cache; "
        "do not fall back to notes_plain/notes_markdown (default is to fall back).",
    )
    p.add_argument(
        "--emit-notes-without-transcript",
        action="store_true",
        help="Deprecated: notes fallback is now the default. This flag is a no-op.",
    )
    p.add_argument(
        "--write-last-json",
        action="store_true",
        help="Also write granola-sync-last.json (full last-run payload). Default is log-only.",
    )
    p.add_argument(
        "--no-human-summary",
        action="store_true",
        help="Do not print per-file lines to stderr after the JSON report.",
    )
    p.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Append granola-sync.log (UTC minute timestamps YYYY-MM-DDTHH:MMZ; RUN/SYNC/SKIP/END lines). Use --write-last-json for granola-sync-last.json.",
    )
    p.add_argument(
        "--log-max-lines",
        type=int,
        default=5000,
        metavar="N",
        help="Max SYNC lines and max SKIP lines written per run (default 5000 each).",
    )
    p.add_argument(
        "--stdout-format",
        choices=("json", "notify"),
        default="json",
        help="json: full result on stdout (default). notify: Shortcuts-friendly one-line summary on stdout.",
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
            err_obj = {
                "error": "GDRIVE_BASE_PATH is not set",
                "hint": "Set to your local MyNotes root (see .cursor/mcp.env GDRIVE_BASE_PATH).",
            }
            if args.stdout_format == "notify":
                print(f"Granola sync: {err_obj['error']}", file=sys.stdout)
            else:
                print(json.dumps(err_obj, indent=2), file=sys.stderr)
            if args.log_dir:
                try:
                    _append_sync_logs(
                        Path(args.log_dir),
                        {
                            "cache_path": "",
                            "customers_base": "",
                            "written": [],
                            "skipped": [],
                            "errors": [{"error": err_obj["error"]}],
                            "stats": {},
                        },
                        exit_code=1,
                        write_last_json=bool(args.write_last_json),
                        log_max_lines=max(0, int(args.log_max_lines)),
                    )
                except OSError:
                    pass
            return 1
        base = Path(gb)
    cache = resolve_cache_path(args.cache)
    if cache is None:
        err_obj = {
            "error": "Granola cache file not found",
            "hint": "Install Granola on macOS, open a meeting, or set GRANOLA_CACHE_PATH.",
            "tried": [str(p) for p in ([args.cache] if args.cache else default_cache_candidates())],
        }
        if args.stdout_format == "notify":
            print(f"Granola sync: {err_obj['error']}", file=sys.stdout)
        else:
            print(json.dumps(err_obj, indent=2), file=sys.stderr)
        if args.log_dir:
            try:
                _append_sync_logs(
                    Path(args.log_dir),
                    {
                        "cache_path": "",
                        "customers_base": str(base),
                        "written": [],
                        "skipped": [],
                        "errors": [{"error": err_obj["error"], "tried": err_obj["tried"]}],
                        "stats": {},
                    },
                    exit_code=1,
                    write_last_json=bool(args.write_last_json),
                    log_max_lines=max(0, int(args.log_max_lines)),
                )
            except OSError:
                pass
        return 1

    default_customer = os.environ.get("GRANOLA_DEFAULT_CUSTOMER", "").strip() or None
    env_fb = os.environ.get("GRANOLA_NOTES_FALLBACK", "").strip().lower()
    if env_fb in {"0", "false", "no"}:
        notes_fallback = False
    elif env_fb in {"1", "true", "yes"}:
        notes_fallback = True
    else:
        notes_fallback = not bool(args.transcript_only)
    result = sync_granola_to_mynotes(
        cache_path=cache,
        customers_base=base,
        dry_run=bool(args.dry_run),
        notes_fallback=notes_fallback,
        default_customer=default_customer,
    )
    exit_code = 0 if not result["errors"] else 2
    if args.log_dir:
        try:
            _append_sync_logs(
                Path(args.log_dir),
                result,
                exit_code=exit_code,
                write_last_json=bool(args.write_last_json),
                log_max_lines=max(0, int(args.log_max_lines)),
            )
        except OSError as exc:
            print(f"granola-sync: could not write --log-dir: {exc}", file=sys.stderr)

    if args.stdout_format == "notify":
        print(_format_notify_stdout(result))
    else:
        print(json.dumps(result, indent=2))
    if not args.no_human_summary:
        _emit_human_sync_summary(result)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
