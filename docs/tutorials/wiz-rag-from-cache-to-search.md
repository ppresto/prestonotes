# Tutorial: Wiz cache -> Chroma -> wiz_knowledge_search

## Activity recap

- Covers the full operator path from env setup to a verified `wiz_knowledge_search` query.
- Separates cache **refresh** from cache **read** so freshness claims stay accurate.
- Includes copy-paste commands, expected outputs, and troubleshooting for common blockers.

---

## 1) Preconditions

From repo root, confirm required env is available in `.cursor/mcp.env`:

- `WIZ_CLIENT_ID`, `WIZ_CLIENT_SECRET`, `WIZ_ENV` (for materialization through Wiz APIs)
- `GOOGLE_API_KEY` or `GEMINI_API_KEY` (for embeddings)
- optional: `PRESTONOTES_GEMINI_EMBEDDING_MODEL` (default is usually `text-embedding-004`)

Optional config file:

- `prestonotes_mcp/prestonotes-mcp.yaml` (copy from `.example` if you need local overrides)

Quick checks:

```bash
pwd
uv run python --version
uv run python scripts/wiz_doc_cache_manager.py status
```

---

## 2) Refresh text cache (WIN + optional external)

Refresh WIN/tenant GraphQL materializations:

```bash
uv run python scripts/wiz_doc_cache_manager.py mcp-materialize --min-age-days 7 --delay-seconds 2.5
```

Optional targeted refresh for one doc:

```bash
uv run python scripts/wiz_doc_cache_manager.py mcp-materialize --doc-name projects-tutorial --force --delay-seconds 0.5
```

Optional external pages refresh:

```bash
uv run python scripts/wiz_doc_cache_manager.py spider-ext --max-pages 20
```

Notes:

- `mcp-materialize` writes to `docs/ai/cache/wiz_mcp_server/mcp_materializations/`.
- This is the refresh step. Loading these files into LLM context is a separate read step.

---

## 3) Build vectors in Chroma

Dry-run first (counts ingest candidates without rewriting index):

```bash
uv run python -m prestonotes_mcp.ingestion.build_vector_db --dry-run
```

Reset and rebuild when ready:

```bash
uv run python -m prestonotes_mcp.ingestion.build_vector_db --reset
```

Optional status check:

```bash
uv run python scripts/wiz_doc_cache_manager.py vector-index-status --repo-root .
```

---

## 4) Verify with wiz_knowledge_search

In Cursor chat (with prestonotes MCP enabled), run:

```text
Use wiz_knowledge_search for: "How should I explain Wiz projects and segmentation strategy to a cloud security lead?" max_results=5 include_staleness=true
```

What to inspect in results:

- Snippets map to relevant product docs.
- `include_staleness` metadata shows whether source cache entries may be stale.
- Returned docs align with recently materialized content.

---

## 5) Troubleshooting

- **No rows ingested / empty collection**
  - Run `--dry-run` to verify source counts.
  - Confirm `mcp_materializations/` and `docs/` paths contain markdown files.
- **Embedding/auth failure**
  - Ensure `GOOGLE_API_KEY` or `GEMINI_API_KEY` is set in `.cursor/mcp.env`.
  - Reload Cursor or shell after editing env.
- **Wrong repo root**
  - Run commands from repository root (`prestoNotes`).
- **Search results look stale**
  - Re-run `mcp-materialize` (use `--force` for targeted docs), then rebuild with `--reset`.
- **MCP tool unavailable in chat**
  - Verify prestonotes MCP server is enabled and healthy in Cursor, then retry.
