# TASK-036 — Tutorial: Wiz cache → Chroma → `wiz_knowledge_search`

**Status:** [x] COMPLETE  
**Opened:** 2026-04-21  
**Audience:** Operator (you) learning the full pipeline.

## Goal

Add **`docs/tutorials/wiz-rag-from-cache-to-search.md`** (new folder **`docs/tutorials/`**) that walks **every step**, in order, with copy-paste commands:

1. Preconditions: **`.cursor/mcp.env`** (`WIZ_*`, `GOOGLE_API_KEY` or `GEMINI_API_KEY`), optional **`prestonotes-mcp.yaml`**.
2. **Refresh text:** `mcp-materialize` (WIN) + optional `spider-ext` (external).
3. **Build index:** `uv run python -m prestonotes_mcp.ingestion.build_vector_db --dry-run` then `--reset` when ready.
4. **Verify in Cursor:** call **`wiz_knowledge_search`** with a sample query; interpret `include_staleness`.
5. **Troubleshooting:** empty collection, wrong repo root, missing embedding key.

## Acceptance

- [x] Tutorial exists; linked from **`README.md`** and **`load-product-intelligence.md`**.
- [x] **`### Activity recap`** at top per **TASK-033**.

## Output / Evidence

- Path: `docs/tutorials/wiz-rag-from-cache-to-search.md`
- Link updates:
  - `README.md` (documentation map + Wiz RAG section)
  - `docs/ai/playbooks/load-product-intelligence.md` (vector section reference)
