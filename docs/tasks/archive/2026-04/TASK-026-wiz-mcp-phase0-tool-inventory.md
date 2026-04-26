> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-026 — Wiz MCP phase 0: tool inventory (wiz-local vs tenant GraphQL)

**Status:** `[x] COMPLETE` (2026-04-20)  
**Opened:** 2026-04-20  
**Slug:** `task-wiz-mcp-phase0-tool-inventory`

---

## Legacy Reference

- **Upstream MCP:** [wiz-sec/wiz-mcp](https://github.com/wiz-sec/wiz-mcp) (`search_wiz_docs`, WIN indexes). Pack in-repo: [`wiz-mcp/README.md`](../../../../wiz-mcp/README.md).
- **Tenant GraphQL parity:** [`scripts/wiz_docs_client.py`](../../../../scripts/wiz_docs_client.py) — `aiAssistantQuery` / DOCS (same contract as wiz-local `search_wiz_docs`).
- **Old tree (read-only):** `../prestoNotes.orig` — use only to confirm prior behavior; v2 source of truth is this repo.

---

## Goal

Document how **wiz-local MCP tools** relate to **tenant GraphQL** (official docs / WIN paths), so agents do not assume they can crawl **https://docs.wiz.io** like a normal site.

### Critical constraint

- **`docs.wiz.io` is not spiderable** from typical environments (firewall / access control). Offline cache and **GraphQL-backed** flows are the supported path; do not document a “wget the whole docs site” workflow.

---

## Deliverable

- [x] **`docs/ai/references/wiz-mcp-tools-inventory.md`** (new, short reference) including at minimum:
  - [x] **Table row:** `search_wiz_docs` ↔ tenant **`aiAssistantQuery`** (DOCS channel).
  - [x] **WIN index path:** `docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`.
  - [x] **External-only HTTP:** **www.wiz.io** / allowlisted hosts → **`spider_wiz_external_pages.py`** (long TTL).

---

## Checklist

- [x] Cross-check `scripts/wiz_docs_client.py` and `scripts/wiz_docs_search_cli.py`.
- [x] Firewall / non-spiderable **`docs.wiz.io`** called out in the reference.
- [x] Link from `wiz-doc-lookup-protocol.md` and `docs/ai/cache/wiz_mcp_server/README.md`.

---

## Acceptance criteria

- [x] `wiz-mcp-tools-inventory.md` exists and is linked from protocol + cache README.
- [x] No bulk-spider claim for **`docs.wiz.io`** without firewall caveat.

---

## Output / Evidence

- **Doc path (when done):** `docs/ai/references/wiz-mcp-tools-inventory.md`
- **Proof:** PR link or commit hash; optional paste of the table footer in task comments.
- **Commands (optional verification):**

```bash
# Example: local docs search equals MCP contract (requires WIZ_* in .cursor/mcp.env)
python scripts/wiz_docs_search_cli.py --help
```
