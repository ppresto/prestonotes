#!/usr/bin/env python3
"""Fetch public Wiz marketing pages (``www.wiz.io``) listed in the local tier manifest.

Does **not** call ``docs.wiz.io`` (firewall). Use this to refresh **external** markdown under
``docs/ai/cache/wiz_mcp_server/ext/pages/`` on a long TTL (default **365** days in manifest via
``upsert-url``).

Requires network access to ``https://www.wiz.io/``. Respects ``--max-pages`` and
``--delay-seconds`` for politeness.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]


def _paths(repo: Path) -> tuple[Path, Path, Path]:
    cache = repo / "docs" / "ai" / "cache" / "wiz_mcp_server"
    return cache, cache / "ext" / "indexes" / "tier_manifest.json", cache / "ext" / "pages"


def _today() -> str:
    return date.today().isoformat()


def _due(ttl_days: int) -> str:
    return (date.today() + timedelta(days=ttl_days)).isoformat()


def _load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        return {
            "cache_version": "1.0",
            "last_updated": _today(),
            "default_ttl_days": 14,
            "entries": [],
        }
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _save_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest["last_updated"] = _today()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _upsert_url_entry(manifest: dict, url: str, category: str, status: str, ttl_days: int) -> None:
    entry_id = f"url:{url}"
    entries = manifest.setdefault("entries", [])
    current = next((e for e in entries if e.get("id") == entry_id), None)
    if current is None:
        entries.append(
            {
                "id": entry_id,
                "type": "docs_url",
                "category": category,
                "status": status,
                "last_checked": _today(),
                "last_cached": _today() if status == "cached" else None,
                "ttl_days": ttl_days,
                "next_refresh_due": _due(ttl_days),
                "attempt_count": 1,
                "notes": "spider_wiz_external_pages",
            }
        )
        return
    current["category"] = category
    current["status"] = status
    current["last_checked"] = _today()
    if status == "cached":
        current["last_cached"] = _today()
    current["ttl_days"] = ttl_days
    current["next_refresh_due"] = _due(ttl_days)
    current["attempt_count"] = int(current.get("attempt_count", 0)) + 1


def _allowed_public_blog_url(url: str) -> bool:
    try:
        p = urlparse(url)
    except ValueError:
        return False
    host = (p.netloc or "").lower()
    if host.endswith("wiz.io") and not host.startswith("docs."):
        return True
    if host == "genai.owasp.org":
        return True
    return False


def _html_to_markdownish(raw: bytes, url: str) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", "", text)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", "", text)
    text = re.sub(r"(?is)<(br|p|div|h1|h2|h3|li|tr)[^>]*>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return (
        "---\n"
        f"source_url: {url}\n"
        f"fetched_at: {date.today().isoformat()}\n"
        "spider: scripts/spider_wiz_external_pages.py\n"
        "---\n\n"
        "# External page (spider)\n\n" + text.strip()[:200000]
    )


def _fetch(url: str, timeout: int) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PrestoNotesWizExtSpider/1.1 (+https://github.com/prestoNotes)"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as e:
        return int(e.code), e.read() if e.fp else b""


def run_spider(
    *,
    repo: Path,
    dry_run: bool,
    max_pages: int | None,
    delay_seconds: float,
    min_age_days: int,
    force: bool,
    timeout: int,
) -> int:
    _, tier_manifest, pages_dir = _paths(repo)
    if not tier_manifest.is_file():
        print(f"missing {tier_manifest}", file=sys.stderr)
        return 1
    data = json.loads(tier_manifest.read_text(encoding="utf-8"))
    items = data.get("items") or []
    manifest_path = repo / "docs" / "ai" / "cache" / "wiz_mcp_server" / "manifest.json"
    manifest = _load_manifest(manifest_path)
    written = 0
    skipped = 0
    errors = 0

    for item in items:
        if max_pages is not None and written >= max_pages:
            break
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        fname = str(item.get("file") or "").strip()
        if not url or not fname or not fname.endswith(".md"):
            continue
        if not _allowed_public_blog_url(url):
            skipped += 1
            continue
        dest = pages_dir / fname
        if not dry_run and dest.is_file() and not force:
            try:
                mtime = date.fromtimestamp(dest.stat().st_mtime)
                if (date.today() - mtime).days < min_age_days:
                    skipped += 1
                    continue
            except OSError:
                pass

        if dry_run:
            print(f"dry-run: would fetch {url} -> ext/pages/{fname}")
            written += 1
            continue

        status, body = _fetch(url, timeout)
        if status != 200:
            print(f"WARN {url} HTTP {status}", file=sys.stderr)
            errors += 1
            _upsert_url_entry(
                manifest,
                url,
                str(item.get("source_name") or "ext"),
                "error",
                365,
            )
            _save_manifest(manifest_path, manifest)
            manifest = _load_manifest(manifest_path)
            time.sleep(delay_seconds)
            continue

        pages_dir.mkdir(parents=True, exist_ok=True)
        md = _html_to_markdownish(body, url)
        dest.write_text(md, encoding="utf-8")
        _upsert_url_entry(
            manifest,
            url,
            str(item.get("source_name") or "ext"),
            "cached",
            365,
        )
        _save_manifest(manifest_path, manifest)
        manifest = _load_manifest(manifest_path)
        print(f"ok {fname} <- {url}")
        written += 1
        time.sleep(delay_seconds)

    print(f"summary: written={written} skipped={skipped} errors={errors} dry_run={dry_run}")
    return 0 if errors == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=REPO, help="Repository root")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-pages", type=int, default=None)
    p.add_argument("--delay-seconds", type=float, default=1.5)
    p.add_argument("--min-age-days", type=int, default=365)
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=30)
    args = p.parse_args(argv)
    return run_spider(
        repo=args.repo_root.resolve(),
        dry_run=bool(args.dry_run),
        max_pages=args.max_pages,
        delay_seconds=float(args.delay_seconds),
        min_age_days=int(args.min_age_days),
        force=bool(args.force),
        timeout=int(args.timeout),
    )


if __name__ == "__main__":
    raise SystemExit(main())
