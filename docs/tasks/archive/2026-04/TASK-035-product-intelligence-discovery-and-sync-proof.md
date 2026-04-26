> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-035 — Load Product Intelligence: prove MCP sync beyond copied cache

**Status:** [x] COMPLETE  
**Opened:** 2026-04-21  
**Depends on:** **TASK-027** (discovery waves), **TASK-028** (materialize).

## Goal

Demonstrate—and document in **`load-product-intelligence.md`**—that the repo can:

1. **Refresh** WIN text via **tenant GraphQL** (`mcp-materialize`), not only read stale files copied from another tree.
2. **Optionally expand** the known doc set (MCP / `win_apis` discovery + link ledger waves) so “full sync” means **enumerated coverage**, not infinite `docs.wiz.io` crawl.
3. State clearly: **default playbook step** is **read local cache into LLM**; **refresh** is a separate operator/agent step before load.

## Acceptance

- [x] One **evidence run** logged in this task file (or archive appendix): `mcp-materialize --doc-name <x> --force` + file hash before/after.
- [x] Playbook §2.5 updated with **Read vs refresh** decision tree and TTLs (**7d** / **365d**).

## Output / Evidence

- Playbook updates:
  - `docs/ai/playbooks/load-product-intelligence.md`:
    - Added **Read vs refresh** decision tree section.
    - Added explicit **full sync = finite WIN catalog + discovery waves**, not infinite crawl.
    - Added TTL reminders and TASK-027 linkage.
- Evidence run (repo root):
  - `uv run python scripts/wiz_doc_cache_manager.py mcp-materialize --doc-name projects-tutorial --force --delay-seconds 0.5`
  - Before hash: `506acda954c4da7600f74bddc3d0bfe375df5912c41d0c5ffbb41977435eccf9`
  - After hash: `b4da581de70dd572da641be67938d2ca838a9f7f644dc7878bed6eac01acfff7`
  - Output summary: `materialized=1 skipped_age=0 errors=0 min_age_days=7 dry_run=False`
