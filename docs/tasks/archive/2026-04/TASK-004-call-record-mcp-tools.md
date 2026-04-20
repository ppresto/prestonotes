# TASK-004 — Add call record MCP tools

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-17) |
| **Spec reference** | [`project_spec.md` §9 — TASK-004](../../project_spec.md#task-004--add-the-call-record-mcp-tools) · schemas **§7.1–7.2** |

## What shipped

- **`prestonotes_mcp/call_records.py`** — JSON Schema (Draft 2020-12) for §7.1 records, `validate_call_id` / `validate_call_record_object`, `read_call_record_files`, `rebuild_transcript_index`, filters for `since_date` and `call_type`.
- **`prestonotes_mcp/security.py`** — `check_call_record_json_size` (default 2 MiB; optional `max_call_record_json_bytes` in security config).
- MCP tools in [`prestonotes_mcp/server.py`](../../../prestonotes_mcp/server.py): **`write_call_record`**, **`read_call_records`**, **`update_transcript_index`**, **`read_transcript_index`** (after `bootstrap_customer`).
- Tests: [`prestonotes_mcp/tests/test_call_record_tools.py`](../../../prestonotes_mcp/tests/test_call_record_tools.py).

## Follow-up

- **TASK-005** — Granola sync and per-call transcript files to populate real data alongside these records.
