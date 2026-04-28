---
name: wiz-kb-adhoc-snapshot
description: >-
  Runs wiz-remote wiz_docs_knowledge_base for an ad hoc query and writes
  TASK-074 §G8 envelope JSON under
  docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/_adhoc/.
  Use when the user asks for a one-off Wiz docs KB search materialized to disk,
  ad hoc snapshot refresh, or phrases like "wiz kb snapshot", "materialize KB
  query", or "setup output in AWS" style probes.
---

# Wiz KB ad hoc snapshot (wiz-remote -> disk)

## Preconditions

- **Cursor MCP `wiz-remote`** is enabled and healthy (same fail-fast as `.cursor/agents/tester.md` — one cheap `wiz_docs_knowledge_base` call).
- Repo root is the **prestoNotes** workspace (`scripts/wiz_cache_manager.py` resolves paths from repo root).

## Steps

1. **Get the exact query string** from the user (verbatim). Example: `setup output in AWS`.

2. **Call MCP tool** on server **`wiz-remote`**, tool **`wiz_docs_knowledge_base`**, with JSON arguments:

   ```json
   { "query": "<exact query from user>" }
   ```

   Read the tool schema first if the environment requires it (`wiz_docs_knowledge_base.json` under the wiz-remote MCP descriptors).

3. **Persist raw JSON** for audit and for the cache save command. Write the **entire** tool response body to a temp file under the repo, e.g.:

   - `tmp/wiz-kb-adhoc-<slug>.json`

   The JSON must be parseable as an object with top-level **`results`** (list of hits with `Title`, `Href`, `Score`, `Content`) per **TASK-074 §G8**.

4. **Save §G8 envelope JSON** (ad hoc path, one file per query):

   ```bash
   cd /path/to/prestoNotes
   uv run python scripts/wiz_cache_manager.py kb-snapshot save \
     --query "<exact query from user>" \
     --initial-slug "_adhoc" \
     --json-file tmp/wiz-kb-adhoc-<slug>.json
   ```

   The command prints the output path and writes:

   `docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/_adhoc/<slug>.json`

5. **Confirm** the output file exists; report the **absolute path** back to the user.

## Notes

- This skill is **not** a substitute for the full **Load Product Intelligence** §2.59 seed refresh (§G3.a list). Use it for **ad hoc** queries and one-off proofs.
- Do not paste long doc chunks into customer Google Docs; this output is **internal cache** only.
