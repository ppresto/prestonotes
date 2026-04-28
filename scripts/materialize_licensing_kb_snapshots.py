#!/usr/bin/env python3
"""Rebuild TASK-074 licensing KB envelopes from committed seed bodies + meta.

Each body file is **verbatim** ``Content`` from the top ``wiz_docs_knowledge_base`` hit for the
matching ``kb_seed_queries.yaml`` seed (captured when the seed was last refreshed). This is the
offline equivalent of: MCP → ``kb-snapshot save`` (stdin payload ``{"results":[<top row>]}``).

**Primary design (no extra files):** in Cursor, call ``wiz_docs_knowledge_base``, then pipe the
full MCP JSON into ``wiz_cache_manager.py kb-snapshot save`` (see playbook §2.595). This script is
only for **offline / CI** when you keep verbatim bodies under ``kb_licensing_seed_sources/``.

Optional ``--ingest-incoming`` reads ``<seed-root>/_incoming/*.mcp.json`` (each file:
``{ "query", "results" }``) and regenerates ``bodies/*.md`` + ``meta.json`` before materializing.

See ``docs/ai/cache/wiz_mcp_server/kb_licensing_seed_sources/README.md``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _load_wdc():
    scripts = Path(__file__).resolve().parent
    path = scripts / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ingest_incoming(seed_root: Path, wdc) -> int:
    """Write bodies/*.md and meta.json from _incoming/*.mcp.json. Returns 0 on success."""
    incoming = seed_root / "_incoming"
    if not incoming.is_dir():
        print(f"missing {incoming}", file=sys.stderr)
        return 1
    paths = sorted(incoming.glob("*.mcp.json"))
    if not paths:
        print(f"no *.mcp.json under {incoming}", file=sys.stderr)
        return 1
    bodies = seed_root / "bodies"
    bodies.mkdir(parents=True, exist_ok=True)
    meta: list[dict[str, str | float]] = []
    for path in paths:
        stem = path.name[: -len(".mcp.json")]
        bundle = json.loads(path.read_text(encoding="utf-8"))
        query = str(bundle.get("query") or "").strip()
        rows = bundle.get("results")
        if not query or not isinstance(rows, list) or not rows:
            print(f"skip (need query + results[]): {path}", file=sys.stderr)
            continue
        expect_stem = wdc.kb_query_snapshot_basename(query)
        if stem != expect_stem:
            print(
                f"stem/filename mismatch for {path}: file stem {stem!r} != "
                f"kb_query_snapshot_basename {expect_stem!r}",
                file=sys.stderr,
            )
            return 1
        top = wdc.kb_top_results(rows, 1)[0]
        body_file = f"bodies/{stem}.md"
        (seed_root / body_file).write_text(str(top.get("Content") or ""), encoding="utf-8")
        meta.append(
            {
                "query": query,
                "title": str(top.get("Title") or ""),
                "href": str(top.get("Href") or ""),
                "score": float(top.get("Score") or 0.0),
                "body_file": body_file,
            }
        )
    if not meta:
        print("no meta rows produced from _incoming", file=sys.stderr)
        return 1
    (seed_root / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"ingest_incoming_done seeds={len(meta)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--seed-root",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "docs/ai/cache/wiz_mcp_server/kb_licensing_seed_sources",
        help="Directory containing meta.json and body .md files",
    )
    p.add_argument(
        "--ingest-incoming",
        action="store_true",
        help="First rebuild bodies/*.md + meta.json from _incoming/*.mcp.json, then materialize",
    )
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    seed_root: Path = args.seed_root.resolve()
    wdc = _load_wdc()

    if args.ingest_incoming:
        rc = ingest_incoming(seed_root, wdc)
        if rc != 0:
            return rc

    meta_path = seed_root / "meta.json"
    if not meta_path.is_file():
        print(f"missing {meta_path}", file=sys.stderr)
        return 1

    rows = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        print("meta.json must be a non-empty JSON array", file=sys.stderr)
        return 1

    cat: str | None = None
    for row in rows:
        q = str(row.get("query") or "").strip()
        c = wdc.kb_query_category_dir(q)
        if cat is None:
            cat = c
        elif c != cat:
            print(
                f"meta.json seeds must share one category (got {cat!r} vs {c!r} for {q!r})",
                file=sys.stderr,
            )
            return 1

    for row in rows:
        q = str(row.get("query") or "").strip()
        title = str(row.get("title") or "").strip()
        href = str(row.get("href") or "").strip()
        body_name = str(row.get("body_file") or "").strip()
        try:
            score = float(row.get("score"))
        except (TypeError, ValueError):
            print(f"bad score for {q!r}", file=sys.stderr)
            return 1
        if not q or not body_name:
            print(f"bad row (missing query or body_file): {row!r}", file=sys.stderr)
            return 1
        body_path = seed_root / body_name
        if not body_path.is_file():
            print(f"missing body file: {body_path}", file=sys.stderr)
            return 1
        body = body_path.read_text(encoding="utf-8").strip("\n") + "\n"
        payload = {"results": [{"Content": body, "Title": title, "Href": href, "Score": score}]}
        stdin = json.dumps(payload, ensure_ascii=False)
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "wiz_cache_manager.py"),
                "kb-snapshot",
                "save",
                "--query",
                q,
                "--top-k",
                "1",
            ],
            cwd=str(root),
            input=stdin.encode("utf-8"),
            check=True,
        )

    assert cat is not None
    print(f"materialize_licensing_kb_snapshots_done category={cat} seeds={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
