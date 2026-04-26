> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-029 — External spider (`spider-ext`, long TTL for ext URLs)

**Status:** `[x] COMPLETE` (2026-04-20)  
**Slug:** `task-external-spider-ttl`

---

## Legacy Reference

- **Spider script:** [`scripts/spider_wiz_external_pages.py`](../../../../scripts/spider_wiz_external_pages.py) — www.wiz.io / allowlisted pages → `ext/pages/`.
- **Manifest / tiers:** `docs/ai/cache/wiz_mcp_server/ext/indexes/tier_manifest.json` (see cache README).
- **Manager subcommand:** [`scripts/wiz_doc_cache_manager.py`](../../../../scripts/wiz_doc_cache_manager.py) **`spider-ext`**.

---

## Goal (original)

Fetch **external** (non-tenant) web pages used for RAG / citations, separate from **`docs.wiz.io`** GraphQL flows, with a **long TTL** so blog and marketing pages are not hammered.

---

## Shipped summary

- [x] **`scripts/spider_wiz_external_pages.py`** — tier-based external fetch pipeline.
- [x] **`wiz_doc_cache_manager spider-ext`** subcommand — operational wrapper (`--min-age-days`, delays, `--max-pages`, etc.).
- [x] **365-day default** **`--min-age-days`** for ext URL refresh (re-fetch floor; override with `--force` as needed).

---

## Checklist

- [x] Spider script committed and wired to **`ext/pages/`** output layout.
- [x] **`spider-ext`** registered on the cache manager CLI.
- [x] Default TTL story matches **365** days for external URLs (per script + subcommand defaults).

---

## Output / Evidence

- **Code:** [`scripts/spider_wiz_external_pages.py`](../../../../scripts/spider_wiz_external_pages.py); [`scripts/wiz_doc_cache_manager.py`](../../../../scripts/wiz_doc_cache_manager.py) (`spider-ext`).
- **Cache:** `docs/ai/cache/wiz_mcp_server/ext/pages/`
- **Verify:**

```bash
python scripts/wiz_doc_cache_manager.py spider-ext --help
python scripts/spider_wiz_external_pages.py --help
```
