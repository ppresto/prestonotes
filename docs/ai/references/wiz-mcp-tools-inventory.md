# Wiz MCP + tenant APIs (inventory)

**Last updated:** 2026-04-20

PrestoNotes loads **Wiz product documentation** without crawling **`docs.wiz.io`** from the workstation (that site is typically **not directly reachable** behind customer controls). Use **tenant-authenticated** paths instead.

## wiz-local (Cursor MCP server)

| Capability | Mechanism | Local mirror |
|------------|-----------|----------------|
| Natural-language product docs | GraphQL `aiAssistantQuery` with `type: DOCS` (same as **`search_wiz_docs`**) | `scripts/materialize_wiz_mcp_docs.py` → `docs/ai/cache/wiz_mcp_server/mcp_materializations/<doc_name>.md` |
| WIN / API tutorial inventory | MCP **`win_apis`** (category doc lists) | `docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json` |
| Operational Wiz data (issues, etc.) | Other wiz-local tools | Out of scope for doc cache |

## CLI (no Cursor stdio)

- **`uv run python scripts/wiz_docs_search_cli.py --query "…"`** — one-off DOCS search; prints JSON.
- **`uv run python scripts/wiz_doc_cache_manager.py mcp-materialize …`** — batch MCP materialization + manifest upsert.
- **`uv run python scripts/wiz_doc_cache_manager.py spider-ext …`** — **external** pages only (`www.wiz.io`, allowlisted hosts).

## External marketing / blogs

- **Allowed:** `https://www.wiz.io/...`, `https://wiz.io/...` (non-docs hosts), `genai.owasp.org` (allowlisted).
- **Not used for product docs:** `docs.wiz.io` — use MCP/GraphQL paths above.

See also: **`docs/ai/references/wiz-doc-lookup-protocol.md`**, **`docs/ai/playbooks/refresh-wiz-doc-cache.md`**.
