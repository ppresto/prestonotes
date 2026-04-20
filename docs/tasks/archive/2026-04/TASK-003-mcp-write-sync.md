# TASK-003 — Port write/sync MCP tools

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-17) |
| **Spec reference** | [`project_spec.md` §9 — TASK-003](../../project_spec.md#task-003--port-the-write-sync-tools-to-mcp-server) |

## What shipped

- MCP tools: **`write_doc`**, **`append_ledger`**, **`log_run`**, **`sync_notes`**, **`sync_transcripts`**, **`bootstrap_customer`** in [`prestonotes_mcp/server.py`](../../../prestonotes_mcp/server.py), targeting **`prestonotes_gdoc/`** scripts per v2 paths.
- **`run_pipeline`** not registered (v2).
- **`sync_notes`**: if `scripts/rsync-gdrive-notes.sh` is absent, returns JSON with **`error`** + hint (**TASK-006**).
- Tests: [`prestonotes_mcp/tests/test_server_write_tools.py`](../../../prestonotes_mcp/tests/test_server_write_tools.py) (mocks for `uv run` / dry_run; `log_run` filesystem; missing sync script).

## Follow-up

- **TASK-006** — Port `scripts/rsync-gdrive-notes.sh`, `scripts/granola-sync.py`, etc., so **`sync_*`** tools run end-to-end.
