# TASK-030 — Playbooks: MCP-only Wiz docs + external spider

**Status:** [x] COMPLETE (2026-04-20)  
**Legacy Reference:** `../prestoNotes.orig/docs/ai/playbooks/` (v1 patterns); this repo `docs/ai/playbooks/`.

## Goal

Ensure **Load Product Intelligence** and **Refresh Wiz Doc Cache** describe the split:

- **Product / WIN text:** tenant GraphQL (`aiAssistantQuery` / DOCS) via `materialize_wiz_mcp_docs.py` — **no** `docs.wiz.io` HTTP.
- **External blogs:** `spider_wiz_external_pages.py` for `www.wiz.io` / allowlisted hosts only.

## Checklist

- [x] `docs/ai/playbooks/load-product-intelligence.md` — §2.5 / cache paths mention `mcp_materializations/`.
- [x] `docs/ai/playbooks/refresh-wiz-doc-cache.md` — materialize + spider + TTL table.
- [x] `docs/ai/references/wiz-doc-lookup-protocol.md` — firewall constraint.

## Output / Evidence

- Grep playbooks for `mcp_materializations` and `mcp-materialize`.
