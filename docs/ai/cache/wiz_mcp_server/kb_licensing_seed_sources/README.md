# TASK-074 licensing — optional offline seed mirror

This folder is **not** required for the normal flow. Use it only when you want **git-tracked**
verbatim top-hit bodies so CI or a machine **without** `wiz-remote` can rebuild the same envelopes.

## Two paths (pick one)

| Situation | What to do |
|-----------|------------|
| **You have MCP** (Cursor + bearer) | Call `wiz_docs_knowledge_base`, then pipe full JSON into `wiz_cache_manager.py kb-snapshot save` (optionally `--slice-top-k`). Writes straight to `mcp_query_snapshots/licensing/*.json`. **No files here required.** |
| **Offline / reproducible** | Keep `meta.json` + `bodies/*.md` (literal MCP `Content`). Run `uv run python scripts/materialize_licensing_kb_snapshots.py`. Or drop `_incoming/*.mcp.json` and run the same script with `--ingest-incoming` to regenerate bodies + meta, then materialize. |

## Rules

- **No stub `Content`.** Each `bodies/<stem>.md` must match the literal top MCP row for that seed.
- **`meta.json`:** JSON array of `{ "query", "title", "href", "score", "body_file" }` per seed. `body_file` is relative to this directory (e.g. `bodies/wiz-cloud-billable-units.md`).
- After changing bodies or meta, run `materialize_licensing_kb_snapshots.py` so `mcp_query_snapshots/licensing/*.json` stay aligned with `kb_seed_queries.yaml`.

## `_incoming/*.mcp.json` (optional)

Each file: `{ "query": "<exact kb_seed_queries initial_query>", "results": [ ... ] }` (full MCP `results` array). The basename without `.mcp.json` must match `kb_query_snapshot_basename(query)`.

```bash
uv run python scripts/materialize_licensing_kb_snapshots.py --ingest-incoming
```

That step writes `bodies/*.md` + `meta.json` from the top `Score` row per file, then runs `kb-snapshot save` per row to refresh envelopes.
