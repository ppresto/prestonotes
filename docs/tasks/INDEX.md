# Task Index

Master backlog status for PrestoNotes v2. **Canonical task definitions:** [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **How to run migration work:** [`V2_MVP_BUILD_PLAN.md`](../V2_MVP_BUILD_PLAN.md).

## Current active task

- **None** — next backlog item: **TASK-015** (SOC domain advisor), see [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **phase2-cleanup** done — [`archive/2026-04/phase2-cleanup.md`](archive/2026-04/phase2-cleanup.md).

## Backlog (not started) — Stage 1

- [x] **TASK-001** — Scaffold repo — [archive](archive/2026-04/TASK-001-scaffold-repo.md)
- [x] **TASK-002** — MCP read tools + resources — [archive](archive/2026-04/TASK-002-mcp-read-tools.md)
- [x] **TASK-003** — MCP write/sync — [archive](archive/2026-04/TASK-003-mcp-write-sync.md)
- [x] **TASK-004** — Call record MCP tools — [archive](archive/2026-04/TASK-004-call-record-mcp-tools.md)
- [x] **TASK-005** — `granola-sync.py` + per-call transcripts — [archive](archive/2026-04/TASK-005-granola-sync-per-call-transcripts.md)
- [x] **TASK-006** — rsync / GDrive / markdown scripts — [archive](archive/2026-04/TASK-006-rsync-gdrive-markdown-sync.md)
- [x] **TASK-007** — Cursor rules + MVP playbooks — [archive](archive/2026-04/TASK-007-cursor-rules-mvp-playbooks.md)

## Backlog — Stage 1 close-out

- [x] **TASK-008** — Extractor `.mdc` + playbook — [archive](archive/2026-04/TASK-008-extractor-mdc-playbook.md)
- [x] **TASK-009** — Stage 1 validation runbook — [archive](archive/2026-04/TASK-009-stage-1-validation-runbook.md)

## Backlog — Stage 2

- [x] **TASK-010** — Journey + challenge MCP tools — [archive](archive/2026-04/TASK-010-journey-challenge-mcp-tools.md)
- [x] **TASK-011** — `append_ledger_v2` + migration — [archive](archive/2026-04/TASK-011-append-ledger-v2.md)
- [x] **TASK-012** — Journey synthesizer — [archive](archive/2026-04/TASK-012-journey-synthesizer.md)
- [x] **TASK-013** — Exec summary template + account summary — [archive](archive/2026-04/TASK-013-exec-summary-account-summary.md)
- [x] **TASK-014** — Challenge review playbook — [archive](archive/2026-04/TASK-014-challenge-review-playbook.md)

## Backlog — Stage 3

- [ ] **TASK-015** — SOC domain advisor
- [ ] **TASK-016** — APP, VULN, ASM, AI advisors
- [ ] **TASK-017** — Orchestrator + task router
- [ ] **TASK-018** — Exec briefing playbook
- [ ] **TASK-019** — Stage 3 integration test

## Phase 3 close-out cleanup (after TASK-019)

**Node / npm today:** The repo is **Python-first**. The only tracked **`.js`** file is **`scripts/syncNotesToMarkdown.js`** (Google **Apps Script**, not executed with Node in this tree) and it is **excluded** from Biome in **`biome.json`**. **`package.json`** / **`package-lock.json`** / **`node_modules`** exist **only** to install **[@biomejs/biome](https://biomejs.dev/)** for:

- **`.pre-commit-config.yaml`** → `biomejs/pre-commit` → **`biome-check`**
- **`.cursor/skills/lint.sh`** (runs `node_modules/.bin/biome` when `*.js` exists — currently only the excluded file, but Biome may still touch other file types per config)

**`setEnv.sh --bootstrap`** runs **`npm install`** at the repo root when **`package.json`** is present. **CI** (`.github/workflows/ci.yml`) runs **`npm ci`** for the same reason.

**Phase 3 close-out candidates** (pick up after **TASK-019** or when adding real front-end work):

- [ ] **Drop or replace Biome** so **Node is not a hard prerequisite**: e.g. remove the Biome hook and rely on **Ruff + yamllint + ShellCheck** only; or switch to a **pre-commit hook** that installs Biome without a committed **`package-lock.json`** (if a supported pattern exists); or reintroduce Node only when there is **real** JS/TS in-repo.
- [ ] **Clarify docs**: README “Install Node” becomes optional once Biome is optional; **`Dependencies`** section should match reality.
- [ ] Optionally **rename** `syncNotesToMarkdown.js` → e.g. **`syncNotesToMarkdown.gs.txt`** and adjust references, if that reduces confusion (still not run by Node).

## Backlog — Stage 4 (post-MVP)

- [ ] **TASK-020** — Vector DB ingestion
- [ ] **TASK-021** — `wiz_knowledge_search` MCP tool
- [ ] **TASK-022** — Advisors use vector search

## Completed

- **TASK-001** — Scaffold repo — [`archive/2026-04/TASK-001-scaffold-repo.md`](archive/2026-04/TASK-001-scaffold-repo.md) (2026-04-17)
- **TASK-002** — MCP read tools + resources — [`archive/2026-04/TASK-002-mcp-read-tools.md`](archive/2026-04/TASK-002-mcp-read-tools.md) (2026-04-17)
- **TASK-003** — MCP write/sync — [`archive/2026-04/TASK-003-mcp-write-sync.md`](archive/2026-04/TASK-003-mcp-write-sync.md) (2026-04-17)
- **TASK-004** — Call record MCP tools — [`archive/2026-04/TASK-004-call-record-mcp-tools.md`](archive/2026-04/TASK-004-call-record-mcp-tools.md) (2026-04-17)
- **TASK-005** — Granola sync + per-call transcripts — [`archive/2026-04/TASK-005-granola-sync-per-call-transcripts.md`](archive/2026-04/TASK-005-granola-sync-per-call-transcripts.md) (2026-04-17)
- **TASK-006** — rsync / GDrive / markdown sync — [`archive/2026-04/TASK-006-rsync-gdrive-markdown-sync.md`](archive/2026-04/TASK-006-rsync-gdrive-markdown-sync.md) (2026-04-19)
- **TASK-007** — Cursor rules + MVP playbooks — [`archive/2026-04/TASK-007-cursor-rules-mvp-playbooks.md`](archive/2026-04/TASK-007-cursor-rules-mvp-playbooks.md) (2026-04-19)
- **TASK-008** — Extractor `.mdc` + playbook — [`archive/2026-04/TASK-008-extractor-mdc-playbook.md`](archive/2026-04/TASK-008-extractor-mdc-playbook.md) (2026-04-19)
- **TASK-009** — Stage 1 validation runbook — [`archive/2026-04/TASK-009-stage-1-validation-runbook.md`](archive/2026-04/TASK-009-stage-1-validation-runbook.md) (2026-04-19)
- **TASK-010** — Journey + challenge MCP tools — [`archive/2026-04/TASK-010-journey-challenge-mcp-tools.md`](archive/2026-04/TASK-010-journey-challenge-mcp-tools.md) (2026-04-19)
- **TASK-011** — `append_ledger_v2` + migration — [`archive/2026-04/TASK-011-append-ledger-v2.md`](archive/2026-04/TASK-011-append-ledger-v2.md) (2026-04-19)
- **TASK-012** — Journey synthesizer — [`archive/2026-04/TASK-012-journey-synthesizer.md`](archive/2026-04/TASK-012-journey-synthesizer.md) (2026-04-19)
- **TASK-013** — Exec summary + account summary — [`archive/2026-04/TASK-013-exec-summary-account-summary.md`](archive/2026-04/TASK-013-exec-summary-account-summary.md) (2026-04-19)
- **TASK-014** — Challenge review playbook — [`archive/2026-04/TASK-014-challenge-review-playbook.md`](archive/2026-04/TASK-014-challenge-review-playbook.md) (2026-04-19)
- **Stage 2 batch plan** — [`archive/2026-04/STAGE2-PLAN-TASK-011-014.md`](archive/2026-04/STAGE2-PLAN-TASK-011-014.md) (2026-04-19)
- **phase2-cleanup** — Repo hygiene + MCP secrets pattern + CI — [`archive/2026-04/phase2-cleanup.md`](archive/2026-04/phase2-cleanup.md) (2026-04-19)

## Conventions

- **Active file:** `docs/tasks/active/<TASK-XXX-short-slug>.md` — include **Legacy Reference** when porting from `../prestoNotes.orig`.
- **Archive:** `docs/tasks/archive/YYYY-MM/` when done.
- **Status markers** inside task files: `[ ] TODO` / `[x] COMPLETE`.
