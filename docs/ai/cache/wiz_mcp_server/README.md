# Wiz MCP Local Doc Cache

Local cache for Wiz documentation: **WIN inventory**, **tenant GraphQL snapshots**, optional **external** pages, and **`manifest.json`**.

**Inventory:** **`docs/ai/references/wiz-mcp-tools-inventory.md`** (how MCP maps to GraphQL; **`docs.wiz.io`** firewall note).

## Structure

| Path | Role |
|------|------|
| `manifest.json` | Freshness: `last_cached`, `ttl_days`, `next_refresh_due`, `status` |
| `win_apis_doc_index.json` | WIN `doc_name` list per category (from **`win_apis`** discovery) |
| `docs/<doc_name>.md` | Optional **static** WIN exports (legacy / copy-from-partner) |
| **`mcp_materializations/<doc_name>.md`** | **Latest** text from **tenant `aiAssistantQuery` / DOCS** (same contract as **`search_wiz_docs`**) |
| `ext/pages/*.md` | External **`www.wiz.io`** pages (see `ext/indexes/tier_manifest.json`) |
| `queries/` | Optional saved search traces |
| `mcp_query_snapshots/<category>/*.json` | **wiz-remote** hosted-KB envelope cache (**one shot + top-K** per `kb_seed_queries.yaml`) — **TASK-074** §G3 / §G8. |

**Repeatable E2E (snapshots + §G4 ext pages):** **`docs/ai/playbooks/load-product-intelligence.md`** → **§2.595** (reset → MCP smoke → refresh-path LPI → ad hoc snapshot skill → second read-only LPI).

## Scripts (repo root)

```bash
uv run python scripts/wiz_cache_manager.py status
uv run python scripts/wiz_cache_manager.py mcp-materialize --min-age-days 7 --delay-seconds 2.5
uv run python scripts/wiz_cache_manager.py spider-ext --dry-run --max-pages 3
uv run python scripts/wiz_docs_search_cli.py --query "Wiz CLI prerequisites"
# TASK-074 §G8: wiz-remote JSON → envelope snapshot (paths derived from --query: first segment = category dir)
# Full multi-hit MCP payload: use --slice-top-k to persist top rows by Score before building the envelope.
uv run python scripts/wiz_cache_manager.py kb-snapshot save \
  --query "licensing - wiz cloud - billable units" \
  --slice-top-k 1 \
  --top-k 1 \
  --json-file path/to/wiz_docs_knowledge_base_full_response.json
```

## Adaptive `refresh-loop`

- **`refresh-loop`** updates **manifest** metadata and probes **`docs_url`** rows with HTTP; for **`win_doc`** it only checks that **`docs/<doc_name>.md`** exists — it does **not** call GraphQL. Use **`mcp-materialize`** for fresh MCP bodies.

## Discovery depth

- Policy: **`crawl_policy.json`** (if present).
- MCP link discovery: default depth **5**; audit **9** sparingly.
- Stop after **two** consecutive waves with **no new** `docs.wiz.io` links discovered (search-driven; no bulk crawl of docs.wiz.io).
