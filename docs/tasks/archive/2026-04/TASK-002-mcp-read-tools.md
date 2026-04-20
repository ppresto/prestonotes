# TASK-002 — Port MCP server (read-only tools + resources)

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-17) |
| **Spec reference** | [`project_spec.md` §9 — TASK-002](../../project_spec.md#task-002--port-the-mcp-server-read-only-tools-only) |

## Dependency choice (discover / read / resources)

**Approach (1):** Ported **`../prestoNotes.orig/custom-notes-agent/`** into **`prestonotes_gdoc/`** (rsync, excluding `mutations/` and `test/`), then pointed MCP paths at **`prestonotes_gdoc/...`**. Stripped hardcoded **`GDRIVE_CUSTOMERS_BASE`** in **`update-gdoc-customer-notes.py`** to derive from **`GDRIVE_BASE_PATH`**.

Write/sync tools and **`run_pipeline`** are **not** registered (TASK-003+).

---

## Completion evidence

| Check | Result |
|--------|--------|
| `uv run pytest` | pass (including `prestonotes_mcp/tests/test_server_read_tools.py`) |
| `bash scripts/ci/check-repo-integrity.sh` | pass |
| `bash .cursor/skills/lint.sh` | pass |
| `uv run pre-commit run --all-files` | pass |
| `python -m prestonotes_mcp` bootstrap | covered by `test_main_does_not_block` (patches `mcp.run`) |

**Key files:** `prestonotes_mcp/server.py`, `config.py`, `exec_helper.py`, `runtime.py`, `security.py`, `__main__.py`, `prestonotes-mcp.yaml.example`, `.env.example`, `prestonotes_mcp/tests/`, `prestonotes_gdoc/` tree, `biome.json` (scoped lint), `.yamllint` ignores for vendor + gdoc YAML.

---

## Acceptance

- [x] Read-only tools + MCP resources per §9 TASK-002
- [x] **`read_transcripts`** v2 behavior (per-call `.txt`, deprioritize `_MASTER_*` when others exist)
- [x] No **`run_pipeline`**; no write tools
- [x] Tests + CI checks pass
