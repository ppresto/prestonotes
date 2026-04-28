#!/usr/bin/env python3
import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "docs" / "ai" / "cache" / "wiz_mcp_server"
MANIFEST_PATH = CACHE_DIR / "manifest.json"
INDEX_PATH = CACHE_DIR / "win_apis_doc_index.json"
DOCS_SNAPSHOT_DIR = CACHE_DIR / "docs"
KB_SNAPSHOTS_DIR = CACHE_DIR / "mcp_query_snapshots"
KB_SEED_YAML = CACHE_DIR / "kb_seed_queries.yaml"
KB_SEED_QUERY_SEGMENT_DELIM = " - "
# v2: one_shot + top_k under mcp_query_snapshots/<category>/ (v1 was legacy BFS depth drill)


def _today() -> str:
    return date.today().isoformat()


def _due(ttl_days: int) -> str:
    return (date.today() + timedelta(days=ttl_days)).isoformat()


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify_query(query: str, max_len: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (query or "").lower()).strip("-")
    if not slug:
        return "query"
    return slug[:max_len]


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    txt = str(raw).strip()
    if not txt:
        return None
    txt = txt[:10]
    try:
        return date.fromisoformat(txt)
    except ValueError:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object JSON: {path}")
    return data


def _seed_dir(initial_slug: str) -> Path:
    return KB_SNAPSHOTS_DIR / initial_slug


def _query_chain_basename(initial_slug: str, query: str, chain_prefix: str | None) -> str:
    if chain_prefix:
        return f"{chain_prefix}-{slugify_query(query)}"
    if initial_slug == "_adhoc":
        return slugify_query(query)
    return initial_slug


def kb_query_split_segments(query: str) -> list[str]:
    """Non-empty segments split on ``KB_SEED_QUERY_SEGMENT_DELIM`` (space-hyphen-space)."""
    return [p.strip() for p in (query or "").split(KB_SEED_QUERY_SEGMENT_DELIM) if p.strip()]


def kb_query_category_dir(query: str) -> str:
    """First segment, slugified — directory under ``mcp_query_snapshots/`` (e.g. ``licensing``)."""
    segs = kb_query_split_segments(query)
    if not segs:
        return "query"
    return slugify_query(segs[0])


def kb_query_snapshot_basename(query: str) -> str:
    """Stem for ``<stem>.json``: slugify remainder after first segment (or whole query if one segment)."""
    segs = kb_query_split_segments(query)
    if len(segs) <= 1:
        return slugify_query(segs[0] if segs else query)
    remainder = KB_SEED_QUERY_SEGMENT_DELIM.join(segs[1:])
    return slugify_query(remainder)


def kb_top_results(results: list[Any], top_k: int) -> list[Any]:
    """Keep the top ``top_k`` dict rows by ``Score`` (descending)."""
    k = int(top_k)
    if k < 1:
        return []
    rows = [r for r in results if isinstance(r, dict)]
    rows.sort(key=lambda r: float(r.get("Score") or 0.0), reverse=True)
    return rows[:k]


def expected_kb_snapshot_paths_from_yaml(
    initial_slug: str, seed_yaml: Path = KB_SEED_YAML
) -> dict[str, str]:
    """Map ``<stem>.json`` (relative to category dir) -> ``initial_query`` for seeds in that category."""
    out: dict[str, str] = {}
    for seed in _parse_seed_yaml(seed_yaml):
        q = str(seed.get("initial_query") or "").strip()
        if not q:
            continue
        if kb_query_category_dir(q) != initial_slug:
            continue
        rel = f"{kb_query_snapshot_basename(q)}.json"
        out[rel] = q
    return out


def _build_envelope(query: str, payload: dict[str, Any], saved_at: str) -> dict[str, Any]:
    def _extract_wrapped_results(mcp_payload: dict[str, Any]) -> list[Any] | None:
        """Handle MCP wrappers where tool JSON is embedded in content[].text."""
        content = mcp_payload.get("content")
        if not isinstance(content, list):
            return None
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if not isinstance(text, str) or not text.strip():
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
                return parsed["results"]
        return None

    results: list[Any] | None = None
    if "results" in payload:
        raw = payload.get("results")
        if raw is None:
            results = []
        elif isinstance(raw, list):
            results = raw
        else:
            raise ValueError("payload.results must be a list")
    else:
        results = _extract_wrapped_results(payload)

    if results is None:
        raise ValueError(
            "payload missing results list (expected top-level results or MCP content[].text JSON)"
        )

    return {
        "query": query,
        "saved_at": saved_at,
        "source_tool": "wiz_docs_knowledge_base",
        "result_count": len(results),
        "results": results,
    }


def _normalize_href_key(href: str) -> str:
    """Stable key for dedupe: scheme + host + path (no fragment), lowercased."""
    raw = (href or "").strip()
    if not raw:
        return ""
    try:
        p = urllib.parse.urlparse(raw)
    except ValueError:
        return raw.lower()
    if p.scheme and p.netloc:
        path = p.path or ""
        return f"{p.scheme.lower()}://{p.netloc.lower()}{path.lower()}"
    return raw.lower()


def dedupe_kb_results(results: list[Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Dedupe hosted-KB hit rows **after** raw capture.

    Policy: keep the **highest-Score** row per normalized ``Href``; if ``Href`` is empty,
    fall back to ``Title`` (lowered, stripped) as a last-resort key so FAQ-only rows still dedupe.
    """
    rows = [r for r in results if isinstance(r, dict)]
    scored = sorted(rows, key=lambda r: float(r.get("Score") or 0.0), reverse=True)
    kept: dict[str, dict[str, Any]] = {}
    key_order: list[str] = []
    for r in scored:
        href = str(r.get("Href") or "").strip()
        title = str(r.get("Title") or "").strip()
        key = _normalize_href_key(href)
        if not key:
            key = f"title:{title.lower()}" if title else ""
        if not key:
            continue
        if key in kept:
            continue
        kept[key] = r
        key_order.append(key)
    out = [kept[k] for k in key_order]
    out.sort(key=lambda r: float(r.get("Score") or 0.0), reverse=True)
    meta: dict[str, Any] = {
        "input_count": len(rows),
        "output_count": len(out),
        "removed_count": len(rows) - len(out),
        "dedupe_key": "normalized_href_else_title",
    }
    return out, meta


def envelope_apply_dedup_fields(envelope: dict[str, Any]) -> dict[str, Any]:
    """Mutate envelope dict in-place: add ``results_deduped`` + counts/meta; preserve raw ``results``."""
    raw = envelope.get("results") or []
    if not isinstance(raw, list):
        raise ValueError("envelope.results must be a list")
    deduped, meta = dedupe_kb_results(raw)
    envelope["results_deduped"] = deduped
    envelope["result_count_deduped"] = len(deduped)
    envelope["dedup_meta"] = meta
    return envelope


def _collect_seed_files(initial_slug: str) -> list[Path]:
    seed_root = _seed_dir(initial_slug)
    if not seed_root.exists():
        return []
    files: list[Path] = []
    for p in seed_root.glob("*.json"):
        if p.name == "seed-run-manifest.json":
            continue
        files.append(p)
    return sorted(files)


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


def _manifest_entry_stats(manifest: dict) -> tuple[int, dict[str, int], int]:
    entries = manifest.get("entries", [])
    total = len(entries)
    by_status: dict[str, int] = {}
    stale = 0
    today = date.today()
    for e in entries:
        st = e.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        due = e.get("next_refresh_due")
        if due:
            try:
                if date.fromisoformat(str(due)) <= today:
                    stale += 1
            except ValueError:
                pass
    return total, by_status, stale


def cmd_status(_: argparse.Namespace) -> None:
    manifest = load_manifest()
    total, by_status, stale = _manifest_entry_stats(manifest)

    print(f"manifest: {MANIFEST_PATH}")
    print(f"entries: {total}")
    print("status_counts:")
    for st, count in sorted(by_status.items()):
        print(f"  {st}: {count}")
    print(f"stale_or_due: {stale}")


def _load_wiz_vector_coverage_module():
    path = _SCRIPTS_DIR / "wiz_vector_coverage_report.py"
    spec = importlib.util.spec_from_file_location("wiz_vector_coverage_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_vector_index_status(args: argparse.Namespace) -> None:
    """Manifest stale counts + Chroma wiz_docs stats (TASK-024)."""
    repo = Path(args.repo_root).resolve()
    manifest_path = repo / "docs" / "ai" / "cache" / "wiz_mcp_server" / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"entries": []}
    total, by_status, stale = _manifest_entry_stats(manifest)

    print("=== vector-index-status (manifest + Chroma) ===")
    print(f"repo_root: {repo}")
    print(f"manifest: {manifest_path}")
    print(f"manifest_entries: {total}")
    print(f"manifest_stale_or_due: {stale}")
    if by_status:
        print("manifest_status_counts:")
        for st, count in sorted(by_status.items()):
            print(f"  {st}: {count}")

    try:
        wvc = _load_wiz_vector_coverage_module()
    except Exception as exc:
        print(f"\nchroma: unavailable ({exc})")
        print(
            "hint: run `uv run python -m prestonotes_mcp.ingestion.build_vector_db` after cache markdown exists."
        )
        return

    chroma_rel = wvc._chroma_path_from_config(repo)
    stats = wvc._read_chroma(repo, chroma_rel)
    print()
    if stats is None:
        print("chroma_wiz_docs: unavailable (import or collection missing)")
        print(
            "hint: if markdown exists under docs/ai/cache/wiz_mcp_server/docs/, "
            "run `uv run python -m prestonotes_mcp.ingestion.build_vector_db` from repo root."
        )
        return

    print(f"chroma_path: {chroma_rel}")
    print(f"chroma_chunks_total: {stats['chunks']}")
    print(f"chroma_unique_source_paths: {stats['unique_source_paths']}")
    print(f"chroma_unique_under_wiz_docs_md: {stats['unique_under_wiz_docs']}")
    if stale > 0 or (stats["chunks"] == 0 and total > 0):
        print(
            "\nnext_step: refresh WIN markdown cache + manifest (playbook: docs/ai/playbooks/refresh-wiz-doc-cache.md), "
            "then rebuild vectors if content changed."
        )


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


def cmd_spider_ext(args: argparse.Namespace) -> None:
    """Refresh ``ext/pages`` from ``tier_manifest.json`` (public hosts only)."""
    import importlib.util

    path = _SCRIPTS_DIR / "spider_wiz_external_pages.py"
    spec = importlib.util.spec_from_file_location("spider_wiz_external_pages", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rc = mod.run_spider(
        repo=Path(args.repo_root).resolve(),
        dry_run=bool(args.dry_run),
        max_pages=args.max_pages,
        delay_seconds=float(args.delay_seconds),
        min_age_days=int(args.min_age_days),
        force=bool(args.force),
        timeout=int(args.timeout),
    )
    if rc != 0:
        raise SystemExit(rc)


def cmd_mcp_materialize(args: argparse.Namespace) -> None:
    """Delegate to ``materialize_wiz_mcp_docs`` (tenant GraphQL snapshots; no docs.wiz.io HTTP)."""
    import importlib.util

    path = _SCRIPTS_DIR / "materialize_wiz_mcp_docs.py"
    spec = importlib.util.spec_from_file_location("materialize_wiz_mcp_docs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rc = mod.run_materialize(
        repo=Path(args.repo_root).resolve(),
        dry_run=bool(args.dry_run),
        min_age_days=int(args.min_age_days),
        force=bool(args.force),
        delay_seconds=float(args.delay_seconds),
        max_docs=args.max_docs,
        doc_name_filter=(args.doc_name or "").strip() or None,
        dotenv=Path(args.dotenv).resolve() if args.dotenv else None,
    )
    if rc != 0:
        raise SystemExit(rc)


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


def _parse_seed_yaml(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    seeds: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current:
                seeds.append(current)
            current = {}
            line = line[2:].strip()
            if line.startswith("initial_query:"):
                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                current["initial_query"] = val
            continue
        if current is None:
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        value = v.strip().strip('"').strip("'")
        if key == "results":
            try:
                current[key] = int(value)
            except ValueError:
                current[key] = 1
        elif key == "depth":
            continue
        else:
            current[key] = value
    if current:
        seeds.append(current)
    return seeds


def _read_input_payload(json_file: Path | None) -> dict[str, Any]:
    if json_file:
        return _read_json(json_file)
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        raise ValueError("stdin JSON must be an object")
    return data


def cmd_kb_snapshot_save(args: argparse.Namespace) -> None:
    saved_at = args.saved_at or date.today().isoformat()
    q = (args.query or "").strip()
    chain_prefix = (args.chain_prefix or "").strip() or None
    slug_arg = (args.initial_slug or "").strip()

    if slug_arg == "_adhoc":
        seed_root = _seed_dir("_adhoc")
        basename = _query_chain_basename("_adhoc", q, chain_prefix)
    elif chain_prefix:
        seed_root = _seed_dir(slug_arg or slugify_query(q))
        basename = f"{chain_prefix}-{slugify_query(q)}"
    else:
        seed_root = _seed_dir(kb_query_category_dir(q))
        basename = kb_query_snapshot_basename(q)

    seed_root.mkdir(parents=True, exist_ok=True)
    out_path = seed_root / f"{basename}.json"

    payload = _read_input_payload(args.json_file)
    if bool(args.raw_sidecar):
        raw_path = seed_root / f"{basename}.raw.json"
        raw_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"raw_sidecar={raw_path}", file=sys.stderr)
    slice_k = getattr(args, "slice_top_k", None)
    if slice_k is not None:
        sk = int(slice_k)
        raw_rows = payload.get("results")
        if not isinstance(raw_rows, list):
            raise SystemExit("payload.results must be a list when using --slice-top-k")
        sliced = kb_top_results(raw_rows, sk)
        payload = {**payload, "results": sliced}
    envelope = _build_envelope(q, payload, saved_at)
    top_k = getattr(args, "top_k", None)
    if top_k is None and slice_k is not None:
        top_k = int(slice_k)
    if top_k is not None:
        envelope["top_k"] = int(top_k)
    if bool(args.dedup_inline):
        envelope_apply_dedup_fields(envelope)
    out_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))


def cmd_kb_snapshot_dedup_seed(args: argparse.Namespace) -> None:
    """Add ``results_deduped`` / ``dedup_meta`` to each envelope JSON in a seed directory."""
    initial_slug = args.initial_slug
    seed_root = _seed_dir(initial_slug)
    if not seed_root.is_dir():
        raise SystemExit(f"missing seed dir: {seed_root}")
    updated = 0
    for path in sorted(seed_root.glob("*.json")):
        if path.name == "seed-run-manifest.json" or path.name.endswith(".raw.json"):
            continue
        data = _read_json(path)
        if str(data.get("source_tool") or "") != "wiz_docs_knowledge_base":
            continue
        envelope_apply_dedup_fields(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated += 1
    print(f"dedup_updated_files={updated} seed={initial_slug}")


def cmd_kb_snapshot_status(args: argparse.Namespace) -> None:
    initial_slug = args.initial_slug
    max_age_days = int(args.max_age_days)
    today = date.today()
    seed_root = _seed_dir(initial_slug)
    status_rows: list[dict[str, Any]] = []

    if not seed_root.exists():
        result = {
            "category": initial_slug,
            "initial_slug": initial_slug,
            "state": "COLD",
            "reason": "seed directory missing",
            "files": [],
        }
        print(
            json.dumps(result, ensure_ascii=False, indent=2)
            if args.json
            else "COLD: seed directory missing"
        )
        raise SystemExit(2)

    seed_yaml = args.seed_file if args.seed_file is not None else KB_SEED_YAML
    expected_by_relpath = expected_kb_snapshot_paths_from_yaml(initial_slug, seed_yaml)

    seen_relpaths: set[str] = set()
    for path in _collect_seed_files(initial_slug):
        rel = str(path.relative_to(seed_root))
        seen_relpaths.add(rel)
        try:
            data = _read_json(path)
        except Exception as exc:  # noqa: BLE001
            status_rows.append({"path": rel, "status": "ERROR", "reason": str(exc)})
            continue
        saved_at = _parse_iso_date(str(data.get("saved_at") or ""))
        if saved_at is None:
            status_rows.append({"path": rel, "status": "STALE", "reason": "invalid saved_at"})
            continue
        age = (today - saved_at).days
        if age > max_age_days:
            status_rows.append(
                {"path": rel, "status": "STALE", "age_days": age, "query": data.get("query")}
            )
        else:
            status_rows.append(
                {"path": rel, "status": "FRESH", "age_days": age, "query": data.get("query")}
            )

    for rel, query in expected_by_relpath.items():
        if rel not in seen_relpaths:
            status_rows.append({"path": rel, "status": "MISSING", "query": query})

    stale = [r for r in status_rows if r.get("status") in {"STALE", "MISSING", "ERROR"}]
    state = "FRESH" if not stale else "STALE"
    result = {
        "category": initial_slug,
        "initial_slug": initial_slug,
        "state": state,
        "max_age_days": max_age_days,
        "seed_yaml": str(seed_yaml),
        "expected_from_yaml": len(expected_by_relpath),
        "files": status_rows,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{state}: {initial_slug}")
        for row in status_rows:
            print(f"{row.get('status')}\t{row.get('path')}")
    if stale:
        raise SystemExit(1)


def cmd_kb_snapshot_list_seeds(args: argparse.Namespace) -> None:
    seeds = _parse_seed_yaml(args.seed_file)
    for seed in seeds:
        q = str(seed.get("initial_query") or "").strip()
        rk = int(seed.get("results") or 1)
        if q:
            print(f"{q}\t{rk}")


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


def _days_since_cached(entry: dict) -> int | None:
    """Return days since ``last_cached`` (date-only), or None if missing/unparseable."""
    raw = entry.get("last_cached")
    if not raw:
        return None
    try:
        cached = date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None
    return (date.today() - cached).days


def cmd_refresh_loop(args: argparse.Namespace) -> None:
    """
    Adaptive refresh loop:
    - URL entries: performs direct HTTP checks and updates status with backoff.
    - WIN doc entries: marks cached when local snapshot exists; otherwise keeps indexed/error.

    Note: for ``win_doc`` entries this updates **manifest freshness only** (and re-checks that
    the local ``docs/<doc_name>.md`` snapshot still exists). It does **not** re-download full WIN
    tutorial bodies from Wiz; use MCP / WIN export or a dedicated fetch pipeline for that.
    """
    manifest = load_manifest()
    entries = manifest.get("entries", [])
    today = date.today()
    min_age = getattr(args, "last_cached_older_than_days", None)

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
            if min_age is not None:
                d = _days_since_cached(e)
                age_ok = d is None or d >= int(min_age)
                if age_ok:
                    targets.append(e)
            elif args.include_all or is_due:
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

    p_vis = sub.add_parser(
        "vector-index-status",
        help="Manifest stale counts + Chroma wiz_docs collection stats (TASK-024)",
    )
    p_vis.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root (default: this script's parent)",
    )
    p_vis.set_defaults(func=cmd_vector_index_status)

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

    p_mat = sub.add_parser(
        "mcp-materialize",
        help="Fetch WIN doc text via tenant GraphQL (DOCS) into mcp_materializations/*.md",
    )
    p_mat.add_argument("--repo-root", type=Path, default=ROOT)
    p_mat.add_argument("--dry-run", action="store_true")
    p_mat.add_argument("--min-age-days", type=int, default=7)
    p_mat.add_argument("--force", action="store_true")
    p_mat.add_argument("--delay-seconds", type=float, default=2.0)
    p_mat.add_argument("--max-docs", type=int, default=None)
    p_mat.add_argument("--doc-name", type=str, default=None)
    p_mat.add_argument("--dotenv", type=Path, default=None)
    p_mat.set_defaults(func=cmd_mcp_materialize)

    p_spider = sub.add_parser(
        "spider-ext",
        help="Fetch www.wiz.io (and allowlisted) pages from ext/indexes/tier_manifest.json",
    )
    p_spider.add_argument("--repo-root", type=Path, default=ROOT)
    p_spider.add_argument("--dry-run", action="store_true")
    p_spider.add_argument("--max-pages", type=int, default=None)
    p_spider.add_argument("--delay-seconds", type=float, default=1.5)
    p_spider.add_argument("--min-age-days", type=int, default=365)
    p_spider.add_argument("--force", action="store_true")
    p_spider.add_argument("--timeout", type=int, default=30)
    p_spider.set_defaults(func=cmd_spider_ext)

    p_loop = sub.add_parser("refresh-loop", help="Run adaptive refresh waves for cache entries")
    p_loop.add_argument("--max-waves", type=int, default=20)
    p_loop.add_argument(
        "--include-all",
        action="store_true",
        help="Refresh all entries, not only due/stale",
    )
    p_loop.add_argument(
        "--last-cached-older-than-days",
        type=int,
        default=None,
        metavar="N",
        help=(
            "If set, only process entries whose last_cached is missing or at least N days old "
            "(still combined with due-date filter unless --include-all)."
        ),
    )
    p_loop.add_argument("--base-delay-seconds", type=float, default=8.0)
    p_loop.add_argument("--min-delay-seconds", type=float, default=4.0)
    p_loop.add_argument("--max-delay-seconds", type=float, default=60.0)
    p_loop.add_argument("--backoff-multiplier", type=float, default=1.5)
    p_loop.add_argument("--recovery-multiplier", type=float, default=0.9)
    p_loop.add_argument("--sleep-between-waves-seconds", type=float, default=20.0)
    p_loop.add_argument("--timeout-seconds", type=int, default=20)
    p_loop.set_defaults(func=cmd_refresh_loop)

    p_kb = sub.add_parser("kb-snapshot", help="Manage wiz-remote KB snapshot cache files")
    kb_sub = p_kb.add_subparsers(dest="kb_cmd", required=True)

    p_kb_save = kb_sub.add_parser(
        "save", help="Save one wiz_docs_knowledge_base payload as envelope JSON"
    )
    p_kb_save.add_argument(
        "--query", required=True, help="Exact query string used for this MCP call"
    )
    p_kb_save.add_argument(
        "--initial-slug",
        default=None,
        help="Use _adhoc for ad hoc snapshots; with --chain-prefix, parent directory slug; else derived from query",
    )
    p_kb_save.add_argument(
        "--chain-prefix",
        default=None,
        help="Parent basename without .json when saving child rounds",
    )
    p_kb_save.add_argument(
        "--json-file",
        type=Path,
        default=None,
        help="Read payload from this file; otherwise read stdin",
    )
    p_kb_save.add_argument("--saved-at", default=None, help="ISO date (defaults to today)")
    p_kb_save.add_argument(
        "--raw-sidecar",
        action="store_true",
        help="Also write <basename>.raw.json with the exact input payload (audit / diff vs envelope).",
    )
    p_kb_save.add_argument(
        "--dedup-inline",
        action="store_true",
        help="After building results[], add results_deduped + dedup_meta (see kb-snapshot dedup-seed).",
    )
    p_kb_save.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Optional: record top_k on the envelope JSON",
    )
    p_kb_save.add_argument(
        "--slice-top-k",
        type=int,
        default=None,
        metavar="K",
        help=(
            "Before building the envelope, replace payload.results with the top K rows by Score "
            "(same ordering as kb_seed_queries.yaml / kb_top_results). Use when stdin or --json-file "
            "contains the full wiz_docs_knowledge_base response. If --top-k is omitted, it defaults to this K."
        ),
    )
    p_kb_save.set_defaults(func=cmd_kb_snapshot_save)

    p_kb_dedup = kb_sub.add_parser(
        "dedup-seed",
        help="Recompute results_deduped + dedup_meta on each envelope JSON in a seed directory",
    )
    p_kb_dedup.add_argument(
        "--initial-slug",
        required=True,
        help="Category directory under mcp_query_snapshots/ (e.g. licensing)",
    )
    p_kb_dedup.set_defaults(func=cmd_kb_snapshot_dedup_seed)

    p_kb_status = kb_sub.add_parser(
        "status", help="Report per-file FRESH/STALE/MISSING for a seed dir"
    )
    p_kb_status.add_argument(
        "--initial-slug",
        required=True,
        help="Category directory under mcp_query_snapshots/",
    )
    p_kb_status.add_argument("--max-age-days", type=int, default=7)
    p_kb_status.add_argument("--json", action="store_true")
    p_kb_status.add_argument(
        "--seed-file",
        type=Path,
        default=None,
        help=f"Seed YAML (default: {KB_SEED_YAML})",
    )
    p_kb_status.set_defaults(func=cmd_kb_snapshot_status)

    p_kb_list = kb_sub.add_parser(
        "list-seeds", help="Print initial_query and results (top-K) from kb_seed_queries.yaml"
    )
    p_kb_list.add_argument("--seed-file", type=Path, default=KB_SEED_YAML)
    p_kb_list.set_defaults(func=cmd_kb_snapshot_list_seeds)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
