# Task Index

Master backlog status for PrestoNotes v2. **Canonical task definitions:** [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **How to run migration work:** [`V2_MVP_BUILD_PLAN.md`](../V2_MVP_BUILD_PLAN.md).

## Current active task

- _(none — create `docs/tasks/active/TASK-XXX-slug.md` when you start the next §9 task)_

## Backlog (not started) — Stage 1

- [ ] **TASK-001** — Scaffold repo (`prestonotes_mcp/`, `MIGRATION_GUIDE`, CI scripts, pyproject 2.x)
- [ ] **TASK-002** — MCP read tools + resources
- [ ] **TASK-003** — MCP write/sync + port GDoc stack into **`prestonotes_gdoc/`**
- [ ] **TASK-004** — Call record MCP tools
- [ ] **TASK-005** — `granola-sync.py` + per-call transcripts
- [ ] **TASK-006** — rsync / GDrive / markdown scripts
- [ ] **TASK-007** — Cursor rules + MVP playbooks

## Backlog — Stage 1 close-out

- [ ] **TASK-008** — Extractor `.mdc` + playbook
- [ ] **TASK-009** — Stage 1 validation runbook (**gate:** before Stage 2)

## Backlog — Stage 2

- [ ] **TASK-010** — Journey + challenge MCP tools
- [ ] **TASK-011** — `append_ledger_v2` + migration
- [ ] **TASK-012** — Journey synthesizer
- [ ] **TASK-013** — Exec summary template + account summary
- [ ] **TASK-014** — Challenge review playbook

## Backlog — Stage 3

- [ ] **TASK-015** — SOC domain advisor
- [ ] **TASK-016** — APP, VULN, ASM, AI advisors
- [ ] **TASK-017** — Orchestrator + task router
- [ ] **TASK-018** — Exec briefing playbook
- [ ] **TASK-019** — Stage 3 integration test

## Backlog — Stage 4 (post-MVP)

- [ ] **TASK-020** — Vector DB ingestion
- [ ] **TASK-021** — `wiz_knowledge_search` MCP tool
- [ ] **TASK-022** — Advisors use vector search

## Completed

_(Move entries here with a link to `docs/tasks/archive/YYYY-MM/...` when a task finishes.)_

## Conventions

- **Active file:** `docs/tasks/active/<TASK-XXX-short-slug>.md` — include **Legacy Reference** when porting from `../prestoNotes.orig`.
- **Archive:** `docs/tasks/archive/YYYY-MM/` when done.
- **Status markers** inside task files: `[ ] TODO` / `[x] COMPLETE`.
