# prestonotes_gdoc

**Google Docs / Drive execution layer** for PrestoNotes v2.

## What belongs here (runtime)

| Item | Role |
|------|------|
| **`update-gdoc-customer-notes.py`** | Docs/Drive API client: discover, read, write, ledger-append subcommands. |
| **`000-bootstrap-gdoc-customer-notes.py`** | Bootstrap customer folders + Notes doc (used when MCP write tools land). |
| **`config/`** | `doc-schema.yaml`, `section-sequence.yaml`, `task-budgets.yaml`, `sections/*.yaml`, prompts consumed by MCP resources and the client. |
| **`config/tools.json`** | **Minimal stub** — v1 had a richer tool registry; v2 names tools in MCP + playbooks directly. **Stage 3** orchestration may expand this file. |

## What we intentionally do **not** ship in v2

- **`run-main-task.py`** and Python **`sections/*_section.py`** — v1 “pipeline” builders; v2 uses **agent-produced mutation JSON** + **`write_doc`** (see [`docs/ai/references/gdoc-section-changes-v2.md`](../docs/ai/references/gdoc-section-changes-v2.md)). History: `../prestoNotes.orig/custom-notes-agent/`.
- **Committed scratch under `tmp/`** — gitignored; do not store run artifacts here.

## Human / playbook docs

- **Granola meeting summary templates:** [`docs/ai/references/granola-meeting-summary-templates.md`](../docs/ai/references/granola-meeting-summary-templates.md) (legacy reference; revise for v2 as needed).

See [`docs/MIGRATION_GUIDE.md`](../docs/MIGRATION_GUIDE.md) for porting rules.
