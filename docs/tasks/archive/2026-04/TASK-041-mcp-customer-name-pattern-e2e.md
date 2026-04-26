> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-041 — MCP customer name pattern: allow `_TEST_CUSTOMER`

**Status:** [x] COMPLETE  
**Opened:** 2026-04-20  
**Depends on:** E2E harness `_TEST_CUSTOMER` playbook flow.

## Goal

Allow MCP tools to accept the fixture customer name `_TEST_CUSTOMER` so E2E playbooks can run through MCP (not only terminal fallback).

## Acceptance

- [x] Update default `validate_customer_name` regex to allow leading underscore.
- [x] Update config example `customer_name_pattern` to match runtime default.
- [x] Add/adjust tests proving underscore-prefixed names work in MCP read/write paths.
- [x] Run targeted tests and lints for changed files.

## Output / Evidence

- Code updates:
  - `prestonotes_mcp/security.py`
  - `prestonotes_mcp/prestonotes-mcp.yaml.example`
- Tests:
  - `prestonotes_mcp/tests/test_server_read_tools.py`
  - `prestonotes_mcp/tests/test_server_write_tools.py`
- Verification commands:
  - `uv run pytest prestonotes_mcp/tests/test_server_read_tools.py prestonotes_mcp/tests/test_server_write_tools.py`
  - `uv run ruff check prestonotes_mcp scripts`
  - `uv run pytest` (full suite; 59 passed on 2026-04-20)

## Operator note (Cursor MCP)

If Cursor still shows `Invalid customer_name (pattern): '_TEST_CUSTOMER'`, restart the **prestonotes** MCP server (or reload the Cursor window) so it picks up the updated Python code. If you copied `prestonotes-mcp.yaml` from the example earlier, also update `security.customer_name_pattern` there to match the new default.

