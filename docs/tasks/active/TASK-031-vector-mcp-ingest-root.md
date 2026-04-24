# TASK-031 — Vector ingest: third root for MCP materializations

**Status:** [x] COMPLETE (2026-04-20)  
**Legacy Reference:** `docs/project_spec.md` §9 TASK-020; `prestonotes_mcp/ingestion/build_vector_db.py`.

## Goal

Chroma ingest includes **`mcp_materializations/`** so `wiz_knowledge_search` returns latest MCP-sourced text alongside static WIN exports.

## Delivered

- [x] `prestonotes_mcp/ingestion/wiz_rag.py` — `wiz_mcp_materializations_rel`, `manifest_meta_for_source_path` maps `mcp_materializations/*.md` → `doc:{stem}`.
- [x] `prestonotes_mcp/ingestion/build_vector_db.py` — `--ingest-mcp` / `--no-ingest-mcp`, third ingest tag `mcp`.
- [x] `prestonotes_mcp/prestonotes-mcp.yaml.example` — `rag.wiz_mcp_materializations`.

## Output / Evidence

```bash
uv run python -m prestonotes_mcp.ingestion.build_vector_db --dry-run
```

Expect markdown count includes `mcp_materializations` when that directory exists.
