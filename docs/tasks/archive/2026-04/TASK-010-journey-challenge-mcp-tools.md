# TASK-010 — Journey timeline + challenge lifecycle MCP tools

## Status

| Field | Value |
|--------|--------|
| **Phase** | **Complete** (2026-04-19) |
| **Spec reference** | [`project_spec.md` §9 — TASK-010](../../project_spec.md#task-010--add-journey-timeline-and-challenge-lifecycle-mcp-tools) |
| **Execution** | **`/coder` → `/tester` → `/doc`** subagent pipeline (isolated context per step) |

## Goal

Two MCP tools: **`write_journey_timeline`**, **`update_challenge_state`** — see spec §9.

## What shipped

- **`prestonotes_mcp/journey.py`** — timeline path, **`challenge-lifecycle.json`**, validators, append-only transitions.
- **`prestonotes_mcp/security.py`** — **`check_journey_timeline_size`** (`max_journey_timeline_bytes`).
- **`prestonotes_mcp/server.py`** — MCP tool registration + **`tool_scope`** + instructions.
- **`prestonotes_mcp/tests/test_journey_tools.py`** — round-trip, **`identified` → `in_progress`**, illegal jump rejection.
- **`prestonotes_mcp/prestonotes-mcp.yaml.example`** — **`max_journey_timeline_bytes`** note.
- **Docs:** **`README.md`**, **`docs/MIGRATION_GUIDE.md`**, **`docs/project_spec.md`** (§3 / §11 customer-local writes).

## Verification

| Check | Result |
|-------|--------|
| **`pytest`** | **31 passed** |
| **`lint.sh`** | OK |
| **`check-repo-integrity.sh`** | OK |

---

**Planner:** Archived after subagent **`/doc`** success.
