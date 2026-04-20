# Task Index

Master backlog status for PrestoNotes v2. **Canonical task definitions:** [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **How to run migration work:** [`V2_MVP_BUILD_PLAN.md`](../V2_MVP_BUILD_PLAN.md).

## Current active task

- **Phase 3 close-out cleanup** — optional repo hygiene + migration-mode decision — see [Backlog — Phase 3 close-out cleanup](#phase-3-close-out-cleanup-after-task-019). Implementation batch (TASK-015–019) is recorded in [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) until the orchestrator archives it.

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

- [x] **TASK-015** — SOC domain advisor — [`.cursor/rules/23-domain-advisor-soc.mdc`](../../.cursor/rules/23-domain-advisor-soc.mdc) · batch [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (Wave A)
- [x] **TASK-016** — APP, VULN, ASM, AI advisors — [`.cursor/rules/24-domain-advisor-app.mdc`](../../.cursor/rules/24-domain-advisor-app.mdc), [`25-domain-advisor-vuln.mdc`](../../.cursor/rules/25-domain-advisor-vuln.mdc), [`26-domain-advisor-asm.mdc`](../../.cursor/rules/26-domain-advisor-asm.mdc), [`27-domain-advisor-ai.mdc`](../../.cursor/rules/27-domain-advisor-ai.mdc) · optional [`docs/ai/references/customer-state-update-delta.md`](../ai/references/customer-state-update-delta.md) · batch [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (Wave A)
- [x] **TASK-017** — Orchestrator + task router — [`.cursor/rules/20-orchestrator.mdc`](../../.cursor/rules/20-orchestrator.mdc), [`.cursor/rules/10-task-router.mdc`](../../.cursor/rules/10-task-router.mdc) · routing note in [`docs/ai/playbooks/update-customer-notes.md`](../ai/playbooks/update-customer-notes.md) · batch [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (Wave B)
- [x] **TASK-018** — Exec briefing playbook — [`docs/ai/playbooks/run-exec-briefing.md`](../ai/playbooks/run-exec-briefing.md) · batch [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (Wave C)
- [x] **TASK-019** — Stage 3 integration validation (manual checklist) — [`docs/ai/playbooks/debug-pipeline.md`](../ai/playbooks/debug-pipeline.md) · batch [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (Wave D)

## Phase 3 close-out cleanup (after TASK-019)

**Done (2026-04):** Removed **Biome** from **`.pre-commit-config.yaml`** and deleted root **`package.json`**, **`package-lock.json`**, **`biome.json`**, **`npm ci`** in CI, and **`npm install`** in **`setEnv.sh`**. In practice Biome had only been checking a few JSON config files. The old **`biomejs/pre-commit`** hook downloaded its own Biome binary, so **`npm ci` was never required** for pre-commit to run that hook — **`npm ci` only fed** local **`node_modules/.bin/biome`** / **`lint.sh`**. **`scripts/syncNotesToMarkdown.js`** stays Apps Script source (not Node-run here).

**Optional later** (after **TASK-019** or when adding a real front-end):

- [ ] Reintroduce a **JS/TS linter** (Biome, ESLint, etc.) **only if** the repo gains maintained JS/TS beyond the Apps Script artifact.
- [ ] Optionally **rename** `syncNotesToMarkdown.js` → e.g. **`syncNotesToMarkdown.gs.txt`** to signal “not Node” (update references).

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
- **Stage 3 (TASK-015–019)** — Advisors, router, orchestrator, exec briefing + debug playbooks — [`active/PHASE3-PLAN.md`](active/PHASE3-PLAN.md) (2026-04-19)

## Conventions

- **Active file:** `docs/tasks/active/<TASK-XXX-short-slug>.md` — include **Legacy Reference** when porting from `../prestoNotes.orig`.
- **Archive:** `docs/tasks/archive/YYYY-MM/` when done.
- **Status markers** inside task files: `[ ] TODO` / `[x] COMPLETE`.
