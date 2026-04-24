#!/usr/bin/env python3
"""Materialize Wiz + WIN tutorial text from tenant GraphQL (``aiAssistantQuery`` / DOCS).

``docs.wiz.io`` is not fetched directly (firewall). This script is the **authoritative refresh**
path for latest product text available through MCP-equivalent APIs.

Writes one markdown file per ``doc_name`` under:

    docs/ai/cache/wiz_mcp_server/mcp_materializations/<doc_name>.md

Each file includes YAML front matter plus the assistant ``text`` and a **Links** table from the
GraphQL response. Existing long-form WIN exports under ``docs/`` are **not** overwritten; they
can remain as static reference while RAG and playbooks prefer ``mcp_materializations/`` when
configured (see ``prestonotes-mcp.yaml`` ``rag.wiz_mcp_materializations``).

Examples::

    uv run python scripts/materialize_wiz_mcp_docs.py --dry-run
    uv run python scripts/materialize_wiz_mcp_docs.py --min-age-days 7 --delay-seconds 2.5
    uv run python scripts/materialize_wiz_mcp_docs.py --doc-name set-up-wiz-cli --force
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import wiz_docs_client  # noqa: E402


def _paths(repo: Path) -> tuple[Path, Path, Path, Path]:
    cache = repo / "docs" / "ai" / "cache" / "wiz_mcp_server"
    return (
        cache,
        cache / "win_apis_doc_index.json",
        cache / "mcp_materializations",
        cache / "manifest.json",
    )


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


def _upsert_win_cached(manifest: dict, doc_name: str, category: str, *, ttl_days: int = 7) -> None:
    entry_id = f"doc:{doc_name}"
    entries = manifest.setdefault("entries", [])
    current = next((e for e in entries if e.get("id") == entry_id), None)
    if current is None:
        entries.append(
            {
                "id": entry_id,
                "type": "win_doc",
                "category": category,
                "status": "cached",
                "last_checked": _today(),
                "last_cached": _today(),
                "ttl_days": ttl_days,
                "next_refresh_due": _due(ttl_days),
                "attempt_count": 1,
                "notes": "mcp_materialize (tenant GraphQL DOCS)",
            }
        )
        return
    current["category"] = category
    current["status"] = "cached"
    current["last_checked"] = _today()
    current["last_cached"] = _today()
    current["ttl_days"] = ttl_days
    current["next_refresh_due"] = _due(ttl_days)
    current["attempt_count"] = int(current.get("attempt_count", 0)) + 1


def _index_pairs(index_path: Path) -> list[tuple[str, str]]:
    data = json.loads(index_path.read_text(encoding="utf-8"))
    cats = data.get("categories") or {}
    out: list[tuple[str, str]] = []
    for category, names in cats.items():
        if not isinstance(names, list):
            continue
        for name in names:
            if isinstance(name, str) and name.strip():
                out.append((category, name.strip()))
    return out


def _manifest_last_cached(manifest: dict, doc_name: str) -> date | None:
    eid = f"doc:{doc_name}"
    for e in manifest.get("entries", []):
        if e.get("id") != eid:
            continue
        raw = e.get("last_cached")
        if not raw:
            return None
        try:
            return date.fromisoformat(str(raw)[:10])
        except ValueError:
            return None
    return None


def _should_skip(
    manifest: dict,
    doc_name: str,
    *,
    min_age_days: int,
    force: bool,
) -> bool:
    if force:
        return False
    lc = _manifest_last_cached(manifest, doc_name)
    if lc is None:
        return False
    age = (date.today() - lc).days
    return age < min_age_days


def _build_query(doc_name: str) -> str:
    human = doc_name.replace("-", " ")
    return (
        f'Wiz official documentation for the partner or WIN tutorial "{human}" ({doc_name}). '
        "Include prerequisites, main procedures, any API or schema fields, limitations, "
        "and links to related docs. Answer using current product terminology."
    )


def _write_markdown(
    repo: Path,
    out_dir: Path,
    doc_name: str,
    category: str,
    query_used: str,
    payload: dict[str, str],
) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = payload.get("text") or ""
    links = payload.get("links") or []
    lines = [
        "---",
        f"doc_name: {doc_name}",
        f"category: {category}",
        f"materialized_at: {now}",
        "source: wiz_tenant_graphql_aiAssistantQuery_DOCS",
        "note: >",
        "  Full HTML from docs.wiz.io is not fetched (network). This file is the latest",
        "  text returned by the tenant Docs assistant API — use for RAG and freshness.",
        "---",
        "",
        f"# MCP docs snapshot: `{doc_name}`",
        "",
        "## Query",
        "",
        "```text",
        query_used,
        "```",
        "",
        "## Assistant text",
        "",
        text.strip() or "_(empty)_",
        "",
        "## Links from API",
        "",
        "| Title | URL |",
        "| --- | --- |",
    ]
    for link in links:
        t = str(link.get("text") or "").replace("|", "\\|")
        h = str(link.get("href") or "").replace("|", "\\|")
        lines.append(f"| {t} | {h} |")
    lines.append("")
    body = "\n".join(lines)
    path = out_dir / f"{doc_name}.md"
    path.write_text(body, encoding="utf-8")
    return str(path.relative_to(repo))


def run_materialize(
    *,
    repo: Path,
    dry_run: bool,
    min_age_days: int,
    force: bool,
    delay_seconds: float,
    max_docs: int | None,
    doc_name_filter: str | None,
    dotenv: Path | None,
) -> int:
    _, index_path, out_dir, manifest_path = _paths(repo)
    if not index_path.is_file():
        print(f"missing index: {index_path}", file=sys.stderr)
        return 1
    pairs = _index_pairs(index_path)
    if doc_name_filter:
        pairs = [(c, n) for c, n in pairs if n == doc_name_filter]
        if not pairs:
            print(f"unknown doc_name: {doc_name_filter}", file=sys.stderr)
            return 1

    manifest = _load_manifest(manifest_path)
    done = 0
    skipped = 0
    errors = 0

    for category, doc_name in pairs:
        if max_docs is not None and done >= max_docs:
            break
        if not dry_run and _should_skip(manifest, doc_name, min_age_days=min_age_days, force=force):
            skipped += 1
            continue
        query = _build_query(doc_name)
        if dry_run:
            print(f"dry-run: would materialize doc:{doc_name} category={category}")
            done += 1
            continue
        try:
            raw = wiz_docs_client.docs_search(query, dotenv=dotenv, repo=repo)
        except (urllib.error.HTTPError, OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR {doc_name}: {exc}", file=sys.stderr)
            errors += 1
            time.sleep(delay_seconds)
            continue
        block = wiz_docs_client.extract_docs_block(raw)
        if block is None:
            print(f"WARN {doc_name}: no docs block in response", file=sys.stderr)
            errors += 1
            time.sleep(delay_seconds)
            continue
        rel = _write_markdown(repo, out_dir, doc_name, category, query, block)
        _upsert_win_cached(manifest, doc_name, category, ttl_days=7)
        _save_manifest(manifest_path, manifest)
        manifest = _load_manifest(manifest_path)
        print(f"ok {doc_name} -> {rel}")
        done += 1
        time.sleep(delay_seconds)

    print(
        f"summary: materialized={done} skipped_age={skipped} errors={errors} "
        f"min_age_days={min_age_days} dry_run={dry_run}"
    )
    return 0 if errors == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=REPO, help="Repository root")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--min-age-days", type=int, default=7)
    p.add_argument("--force", action="store_true", help="Ignore manifest age / always fetch")
    p.add_argument("--delay-seconds", type=float, default=2.0, help="Pace between GraphQL calls")
    p.add_argument("--max-docs", type=int, default=None)
    p.add_argument("--doc-name", type=str, default=None, help="Only this WIN doc slug")
    p.add_argument(
        "--dotenv",
        type=Path,
        default=None,
        help="Dotenv with WIZ_* (default: <repo>/.cursor/mcp.env)",
    )
    args = p.parse_args(argv)
    return run_materialize(
        repo=args.repo_root.resolve(),
        dry_run=bool(args.dry_run),
        min_age_days=int(args.min_age_days),
        force=bool(args.force),
        delay_seconds=float(args.delay_seconds),
        max_docs=args.max_docs,
        doc_name_filter=(args.doc_name or "").strip() or None,
        dotenv=args.dotenv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
