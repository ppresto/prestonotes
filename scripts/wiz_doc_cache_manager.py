#!/usr/bin/env python3
import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "docs" / "ai" / "cache" / "wiz_mcp_server"
MANIFEST_PATH = CACHE_DIR / "manifest.json"
INDEX_PATH = CACHE_DIR / "win_apis_doc_index.json"
DOCS_SNAPSHOT_DIR = CACHE_DIR / "docs"


def _today() -> str:
    return date.today().isoformat()


def _due(ttl_days: int) -> str:
    return (date.today() + timedelta(days=ttl_days)).isoformat()


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "cache_version": "1.0",
        "last_updated": _today(),
        "default_ttl_days": 14,
        "entries": [],
    }


def save_manifest(manifest: dict) -> None:
    manifest["last_updated"] = _today()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def upsert_entry(
    manifest: dict, entry_id: str, kind: str, category: str, status: str, ttl_days: int
) -> None:
    entries = manifest.get("entries", [])
    current = next((e for e in entries if e.get("id") == entry_id), None)
    if current is None:
        entries.append(
            {
                "id": entry_id,
                "type": kind,
                "category": category,
                "status": status,
                "last_checked": _today(),
                "last_cached": _today() if status == "cached" else None,
                "ttl_days": ttl_days,
                "next_refresh_due": _due(ttl_days),
                "attempt_count": 1,
            }
        )
        return

    current["type"] = kind
    current["category"] = category
    current["status"] = status
    current["last_checked"] = _today()
    if status == "cached":
        current["last_cached"] = _today()
    current["ttl_days"] = ttl_days
    current["next_refresh_due"] = _due(ttl_days)
    current["attempt_count"] = int(current.get("attempt_count", 0)) + 1


def cmd_status(_: argparse.Namespace) -> None:
    manifest = load_manifest()
    entries = manifest.get("entries", [])
    total = len(entries)
    by_status = {}
    stale = 0
    today = date.today()
    for e in entries:
        st = e.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        due = e.get("next_refresh_due")
        if due:
            try:
                if date.fromisoformat(due) <= today:
                    stale += 1
            except ValueError:
                pass

    print(f"manifest: {MANIFEST_PATH}")
    print(f"entries: {total}")
    print("status_counts:")
    for st, count in sorted(by_status.items()):
        print(f"  {st}: {count}")
    print(f"stale_or_due: {stale}")


def cmd_upsert_doc(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    entry_id = f"doc:{args.doc_name}"
    upsert_entry(
        manifest,
        entry_id=entry_id,
        kind="win_doc",
        category=args.category,
        status=args.status,
        ttl_days=args.ttl_days,
    )
    save_manifest(manifest)
    print(f"upserted {entry_id}")


def cmd_upsert_url(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    entry_id = f"url:{args.url}"
    upsert_entry(
        manifest,
        entry_id=entry_id,
        kind="docs_url",
        category=args.category,
        status=args.status,
        ttl_days=args.ttl_days,
    )
    save_manifest(manifest)
    print(f"upserted {entry_id}")


def cmd_seed_from_index(_: argparse.Namespace) -> None:
    manifest = load_manifest()
    if not INDEX_PATH.exists():
        raise SystemExit(f"missing index: {INDEX_PATH}")
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    categories = index.get("categories", {})
    added = 0
    for category, docs in categories.items():
        for doc_name in docs:
            entry_id = f"doc:{doc_name}"
            existing = next((e for e in manifest["entries"] if e.get("id") == entry_id), None)
            if existing is not None:
                continue
            manifest["entries"].append(
                {
                    "id": entry_id,
                    "type": "win_doc",
                    "category": category,
                    "status": "indexed_only",
                    "last_checked": _today(),
                    "last_cached": None,
                    "ttl_days": 14,
                    "next_refresh_due": _due(14),
                    "attempt_count": 0,
                }
            )
            added += 1
    save_manifest(manifest)
    print(f"seeded {added} new entries from index")


def _fetch_url_status(url: str, timeout_seconds: int = 20) -> int | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WizCacheRefresher/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as err:
        return int(err.code)
    except Exception:
        return None


def _doc_snapshot_exists(doc_name: str) -> bool:
    return (DOCS_SNAPSHOT_DIR / f"{doc_name}.md").exists()


def cmd_refresh_loop(args: argparse.Namespace) -> None:
    """
    Adaptive refresh loop:
    - URL entries: performs direct HTTP checks and updates status with backoff.
    - WIN doc entries: marks cached when local snapshot exists; otherwise keeps indexed/error.
    """
    manifest = load_manifest()
    entries = manifest.get("entries", [])
    today = date.today()

    adaptive_delay = float(args.base_delay_seconds)
    waves_completed = 0
    total_processed = 0
    total_rate_limited = 0
    total_timeouts = 0

    while waves_completed < args.max_waves:
        # Build wave targets: stale/due entries first, else all if --include-all
        targets = []
        for e in entries:
            due_str = e.get("next_refresh_due")
            is_due = False
            if due_str:
                try:
                    is_due = date.fromisoformat(due_str) <= today
                except ValueError:
                    is_due = True
            if args.include_all or is_due:
                targets.append(e)

        # Stop if nothing to refresh
        if not targets:
            break

        wave_rate_limited = 0
        wave_timeouts = 0
        wave_processed = 0

        for entry in targets:
            entry_id = entry.get("id", "")
            entry_type = entry.get("type")
            category = entry.get("category", "Other")
            ttl_days = int(entry.get("ttl_days", manifest.get("default_ttl_days", 14)))

            # Refresh WIN docs from local snapshots (MCP retrieval is external to this script)
            if entry_type == "win_doc" and entry_id.startswith("doc:"):
                doc_name = entry_id.split("doc:", 1)[1]
                status = (
                    "cached"
                    if _doc_snapshot_exists(doc_name)
                    else entry.get("status", "indexed_only")
                )
                upsert_entry(
                    manifest,
                    entry_id=entry_id,
                    kind="win_doc",
                    category=category,
                    status=status,
                    ttl_days=ttl_days,
                )
                wave_processed += 1
                total_processed += 1
                time.sleep(adaptive_delay)
                continue

            # Refresh docs URLs directly with adaptive pacing
            if entry_type == "docs_url" and entry_id.startswith("url:"):
                url = entry_id.split("url:", 1)[1]
                status_code = _fetch_url_status(url, timeout_seconds=args.timeout_seconds)
                if status_code == 200:
                    status = "cached"
                elif status_code == 429:
                    status = "rate_limited"
                    wave_rate_limited += 1
                    total_rate_limited += 1
                elif status_code is None:
                    status = "error"
                    wave_timeouts += 1
                    total_timeouts += 1
                else:
                    status = "error"

                upsert_entry(
                    manifest,
                    entry_id=entry_id,
                    kind="docs_url",
                    category=category,
                    status=status,
                    ttl_days=ttl_days,
                )
                wave_processed += 1
                total_processed += 1
                time.sleep(adaptive_delay)
                continue

        save_manifest(manifest)
        waves_completed += 1

        # Adaptive backoff based on current wave health
        if wave_rate_limited > 0 or wave_timeouts > 0:
            adaptive_delay = min(adaptive_delay * args.backoff_multiplier, args.max_delay_seconds)
        else:
            adaptive_delay = max(adaptive_delay * args.recovery_multiplier, args.min_delay_seconds)

        # Stop early if all cached
        remaining = [e for e in manifest.get("entries", []) if e.get("status") != "cached"]
        print(
            f"wave={waves_completed} processed={wave_processed} rate_limited={wave_rate_limited} "
            f"timeouts={wave_timeouts} next_delay_seconds={adaptive_delay:.2f} remaining_non_cached={len(remaining)}"
        )
        if len(remaining) == 0:
            break

        time.sleep(args.sleep_between_waves_seconds)

    remaining = [e for e in manifest.get("entries", []) if e.get("status") != "cached"]
    print(
        f"refresh_complete waves={waves_completed} processed={total_processed} "
        f"rate_limited={total_rate_limited} timeouts={total_timeouts} remaining_non_cached={len(remaining)}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local Wiz MCP docs cache metadata.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Show cache summary and stale counts")
    p_status.set_defaults(func=cmd_status)

    p_doc = sub.add_parser("upsert-doc", help="Upsert a WIN doc cache entry")
    p_doc.add_argument("--doc-name", required=True)
    p_doc.add_argument("--category", required=True)
    p_doc.add_argument(
        "--status",
        default="cached",
        choices=["cached", "indexed_only", "rate_limited", "error"],
    )
    p_doc.add_argument("--ttl-days", type=int, default=14)
    p_doc.set_defaults(func=cmd_upsert_doc)

    p_url = sub.add_parser("upsert-url", help="Upsert a docs URL cache entry")
    p_url.add_argument("--url", required=True)
    p_url.add_argument("--category", default="Other")
    p_url.add_argument(
        "--status",
        default="indexed_only",
        choices=["cached", "indexed_only", "rate_limited", "error"],
    )
    p_url.add_argument("--ttl-days", type=int, default=7)
    p_url.set_defaults(func=cmd_upsert_url)

    p_seed = sub.add_parser(
        "seed-from-index",
        help="Seed manifest with indexed-only entries from win_apis index",
    )
    p_seed.set_defaults(func=cmd_seed_from_index)

    p_loop = sub.add_parser("refresh-loop", help="Run adaptive refresh waves for cache entries")
    p_loop.add_argument("--max-waves", type=int, default=20)
    p_loop.add_argument(
        "--include-all",
        action="store_true",
        help="Refresh all entries, not only due/stale",
    )
    p_loop.add_argument("--base-delay-seconds", type=float, default=8.0)
    p_loop.add_argument("--min-delay-seconds", type=float, default=4.0)
    p_loop.add_argument("--max-delay-seconds", type=float, default=60.0)
    p_loop.add_argument("--backoff-multiplier", type=float, default=1.5)
    p_loop.add_argument("--recovery-multiplier", type=float, default=0.9)
    p_loop.add_argument("--sleep-between-waves-seconds", type=float, default=20.0)
    p_loop.add_argument("--timeout-seconds", type=int, default=20)
    p_loop.set_defaults(func=cmd_refresh_loop)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
