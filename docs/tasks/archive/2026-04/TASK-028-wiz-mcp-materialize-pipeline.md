> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-028 — Wiz MCP materialize pipeline (WIN → `mcp_materializations/`)

**Status:** `[x] COMPLETE` (2026-04-20)  
**Slug:** `task-wiz-mcp-materialize-pipeline`

---

## Legacy Reference

- **Materializer:** [`scripts/materialize_wiz_mcp_docs.py`](../../../../scripts/materialize_wiz_mcp_docs.py) (tenant GraphQL DOCS / `aiAssistantQuery`).
- **Shared client:** [`scripts/wiz_docs_client.py`](../../../../scripts/wiz_docs_client.py).
- **CLI wrapper:** [`scripts/wiz_doc_cache_manager.py`](../../../../scripts/wiz_doc_cache_manager.py) subcommand **`mcp-materialize`**.
- **Cache root:** `docs/ai/cache/wiz_mcp_server/mcp_materializations/` (per script defaults).

---

## Goal (original)

Materialize Wiz **WIN / tutorial** markdown snapshots via **tenant GraphQL** into **`mcp_materializations/*.md`**, with TTL-driven refresh for WIN rows and integration with the cache manifest.

---

## Shipped summary

- [x] **`scripts/materialize_wiz_mcp_docs.py`** — fetch path for WIN doc text via **`aiAssistantQuery` / DOCS**.
- [x] **`scripts/wiz_docs_client.py`** — shared GraphQL client for docs search / materialization contract.
- [x] **`wiz_doc_cache_manager mcp-materialize`** — operational entry (dry-run, `--min-age-days`, force, delays).
- [x] **`mcp_materializations/`** output directory under **`docs/ai/cache/wiz_mcp_server/`**.
- [x] **7-day default** refresh floor for WIN materializations via **`--min-age-days`** default **7** on `mcp-materialize`.

---

## Checklist

- [x] Scripts present and documented in cache README / playbooks.
- [x] TTL default **7** days for mcp-materialize churn (operator may override `--force` / `--min-age-days`).
- [x] Secret-free CI coverage for dry-run materialize path (see [`scripts/tests/test_materialize_dry_run.py`](../../../../scripts/tests/test_materialize_dry_run.py)).

---

## Output / Evidence

- **Code:** [`scripts/materialize_wiz_mcp_docs.py`](../../../../scripts/materialize_wiz_mcp_docs.py), [`scripts/wiz_docs_client.py`](../../../../scripts/wiz_docs_client.py), [`scripts/wiz_doc_cache_manager.py`](../../../../scripts/wiz_doc_cache_manager.py) (`mcp-materialize`).
- **Output dir:** `docs/ai/cache/wiz_mcp_server/mcp_materializations/`
- **Verify:**

```bash
python scripts/wiz_doc_cache_manager.py mcp-materialize --help
python scripts/materialize_wiz_mcp_docs.py --help
```
