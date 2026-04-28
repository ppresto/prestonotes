#!/usr/bin/env python3
"""DEPRECATED (2026-04): archived headless refresh for TASK-074 KB snapshots.

**Do not use from playbooks.** The supported path is **Cursor ``wiz-remote`` MCP** →
``wiz_docs_knowledge_base`` → ``wiz_cache_manager.py kb-snapshot save`` (pipe full MCP JSON; use
``--slice-top-k`` when the payload has multiple hits). See ``docs/ai/playbooks/load-product-intelligence.md`` §2.59.

This copy is kept only for reference or emergency debugging. It does **not** read Cursor’s MCP session token;
``https://mcp.demo.wiz.io`` returns **401** without ``--oauth`` or ``WIZ_REMOTE_MCP_BEARER``.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load_wiz_doc_cache_manager():
    path = SCRIPTS / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_dotenv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        if key:
            out[key] = val
    return out


def _call_tool_result_to_payload(obj: Any) -> dict[str, Any]:
    sc = getattr(obj, "structuredContent", None)
    if isinstance(sc, dict):
        return sc
    content = getattr(obj, "content", None)
    if isinstance(content, list):
        blocks: list[dict[str, Any]] = []
        for item in content:
            if hasattr(item, "model_dump"):
                blocks.append(item.model_dump(mode="json"))  # type: ignore[no-untyped-call]
            elif isinstance(item, dict):
                blocks.append(item)
            else:
                t = getattr(item, "type", "text")
                txt = getattr(item, "text", None)
                blocks.append({"type": str(t), "text": txt if isinstance(txt, str) else str(item)})
        return {"content": blocks}
    raise ValueError("MCP tool result has no structuredContent or content")


async def _call_kb(
    client: Any,
    query: str,
    *,
    timeout: float,
    retries: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            async with semaphore:
                return await client.call_tool(
                    "wiz_docs_knowledge_base",
                    {"query": query},
                    timeout=timeout,
                    raise_on_error=True,
                )
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= retries:
                break
            await asyncio.sleep(delay)
            delay = min(delay * 2.0, 8.0)
    assert last_exc is not None
    raise last_exc


def _unwrap_call_tool_result(res: Any) -> dict[str, Any]:
    if isinstance(res, dict):
        return res
    return _call_tool_result_to_payload(res)


def _is_snapshot_fresh(wdc: Any, path: Path, *, max_age_days: int, today: date) -> bool:
    if not path.is_file():
        return False
    try:
        data = wdc._read_json(path)
        saved = wdc._parse_iso_date(str(data.get("saved_at") or ""))
        if saved is None:
            return False
        return (today - saved).days <= max_age_days
    except Exception:
        return False


async def _refresh_one_seed(
    *,
    wdc: Any,
    client: Any | None,
    initial_query: str,
    top_k: int,
    semaphore: asyncio.Semaphore,
    timeout: float,
    retries: int,
    dry_run: bool,
    force: bool,
    raw_sidecar: bool,
    dedup_inline: bool,
) -> None:
    q = initial_query.strip()
    category = wdc.kb_query_category_dir(q)
    stem = wdc.kb_query_snapshot_basename(q)
    seed_root = wdc._seed_dir(category)
    out_path = seed_root / f"{stem}.json"
    today = date.today()
    max_age_days = 7

    if dry_run:
        print(f"dry_run\t{category}\t{stem}.json\t{q}\ttop_k={top_k}")
        return

    if not force and _is_snapshot_fresh(wdc, out_path, max_age_days=max_age_days, today=today):
        print(f"skip_fresh\t{out_path}")
        return

    assert client is not None
    raw_res = await _call_kb(client, q, timeout=timeout, retries=retries, semaphore=semaphore)
    payload = _unwrap_call_tool_result(raw_res)
    saved_at = date.today().isoformat()
    envelope_full = wdc._build_envelope(q, payload, saved_at)
    raw_rows = envelope_full.get("results")
    if not isinstance(raw_rows, list):
        raw_rows = []
    sliced = wdc.kb_top_results(raw_rows, top_k)
    if not sliced:
        print(f"skip_empty\t{out_path}\t(query returned no usable rows)")
        return

    envelope = {
        **envelope_full,
        "results": sliced,
        "result_count": len(sliced),
        "top_k": int(top_k),
    }
    if dedup_inline:
        wdc.envelope_apply_dedup_fields(envelope)

    seed_root.mkdir(parents=True, exist_ok=True)
    if raw_sidecar:
        (seed_root / f"{stem}.raw.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    out_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote\t{out_path}")


async def _async_main(args: argparse.Namespace) -> int:
    wdc = _load_wiz_doc_cache_manager()
    env = _load_dotenv(Path(args.dotenv).resolve())
    url = (args.mcp_url or env.get("WIZ_REMOTE_MCP_URL") or "https://mcp.demo.wiz.io").strip()
    bearer = (args.bearer or env.get("WIZ_REMOTE_MCP_BEARER") or "").strip()
    auth: Any
    if bearer:
        auth = f"Bearer {bearer}"
    elif bool(args.oauth):
        auth = "oauth"
    else:
        auth = None

    seeds = wdc._parse_seed_yaml(Path(args.seed_file).resolve())
    if args.max_seeds is not None:
        seeds = seeds[: int(args.max_seeds)]

    sem = asyncio.Semaphore(max(1, min(10, int(args.concurrency))))
    t0 = time.perf_counter()

    if args.dry_run:
        for seed in seeds:
            q = str(seed.get("initial_query") or "").strip()
            top_k = int(seed.get("results") or 1)
            if not q:
                continue
            await _refresh_one_seed(
                wdc=wdc,
                client=None,
                initial_query=q,
                top_k=top_k,
                semaphore=sem,
                timeout=float(args.timeout_seconds),
                retries=int(args.retries),
                dry_run=True,
                force=bool(args.force),
                raw_sidecar=bool(args.raw_sidecar),
                dedup_inline=bool(args.dedup_inline),
            )
        print(
            f"lpi_kb_seed_refresh_done dry_run seeds={len(seeds)} elapsed_s={time.perf_counter() - t0:.1f}"
        )
        return 0

    from fastmcp import Client

    async with Client(url, auth=auth, timeout=float(args.timeout_seconds)) as client:
        for seed in seeds:
            q = str(seed.get("initial_query") or "").strip()
            top_k = int(seed.get("results") or 1)
            if not q:
                continue
            await _refresh_one_seed(
                wdc=wdc,
                client=client,
                initial_query=q,
                top_k=top_k,
                semaphore=sem,
                timeout=float(args.timeout_seconds),
                retries=int(args.retries),
                dry_run=False,
                force=bool(args.force),
                raw_sidecar=bool(args.raw_sidecar),
                dedup_inline=bool(args.dedup_inline),
            )
    print(f"lpi_kb_seed_refresh_done seeds={len(seeds)} elapsed_s={time.perf_counter() - t0:.1f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--seed-file", type=Path, default=REPO / "docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml"
    )
    p.add_argument("--dotenv", type=Path, default=REPO / ".cursor/mcp.env")
    p.add_argument("--mcp-url", default=None, help="Override WIZ_REMOTE_MCP_URL")
    p.add_argument("--bearer", default=None, help="Override WIZ_REMOTE_MCP_BEARER")
    p.add_argument(
        "--oauth",
        action="store_true",
        help="Use fastmcp OAuth (auth='oauth') for Streamable HTTP when Bearer is not set (may open a browser once).",
    )
    p.add_argument("--timeout-seconds", type=float, default=60.0)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--max-seeds", type=int, default=None)
    p.add_argument(
        "--force", action="store_true", help="Ignore per-file freshness (saved_at <= 7d)"
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--raw-sidecar", action="store_true")
    p.add_argument("--dedup-inline", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(_async_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
