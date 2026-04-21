# Task Index

Master backlog status for PrestoNotes v2. **Canonical task definitions:** [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **How to run migration work:** [`V2_MVP_BUILD_PLAN.md`](../V2_MVP_BUILD_PLAN.md).

## Current active task

- [ ] **TASK-032** — Follow-ups, gaps, and recommendations (Stage 4 backlog) — [`active/TASK-032-followups-and-cleanup.md`](active/TASK-032-followups-and-cleanup.md)
- [ ] **TASK-044** — E2E `_TEST_CUSTOMER` rebuild (single script + playbook chain) — [`active/TASK-044-e2e-test-customer-rebuild.md`](active/TASK-044-e2e-test-customer-rebuild.md) · supersedes TASK-042 + TASK-043

### TASK-044 E2E fact-check follow-ups (2026-04-21)

Land **in this order** — each builds on the prior:

1. [x] **TASK-046** — Retire `transcript-index.json` and its MCP tools — [`archive/2026-04/TASK-046-retire-transcript-index.md`](archive/2026-04/TASK-046-retire-transcript-index.md) · removes a redundant artifact no current playbook depends on; unblocks Account Summary input tightening.
2. [x] **TASK-047** — Retire Journey Timeline; scrub harness vocab; enrich Account Summary — [`archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md`](archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md) · deletes a write-only artifact, folds narrative into Account Summary, defines `FORBIDDEN_EVIDENCE_TERMS` reused by 048/049/050.
3. [x] **TASK-048** — Challenge lifecycle write discipline (+ Challenge Tracker row date bullet) — [`archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md`](archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md) · fixes call-date vs run-date bug across **both** `update_challenge_state` and GDoc Challenge Tracker row writes; forbids stub / harness evidence at MCP write time.
4. [ ] **TASK-049** — History Ledger schema v3 (rationalized, no legacy) — [`active/TASK-049-history-ledger-schema-v3-rationalized.md`](active/TASK-049-history-ledger-schema-v3-rationalized.md) · collapses 24→20 columns, drops dup `Value Realized` / `Open Challenges` / `Aging Blockers` / `Resolved Issues` / `New Blockers` / `Key Drivers`; deletes `migrate_ledger.py` outright (no legacy data).
5. [ ] **TASK-050** — UCN GDoc write completeness + internal consistency — [`active/TASK-050-ucn-gdoc-write-completeness-consistency.md`](active/TASK-050-ucn-gdoc-write-completeness-consistency.md) · fixes `timestamp: null` writer bug, enforces cross-section reconciliation (Risk ↔ Challenge Tracker ↔ lifecycle), ≥ 80% section fill rate, DAL prepend per call, Deal Stage Tracker motion capture, `agent_run_log` populated.
6. [ ] **TASK-051** — Call-record context quality (lookback-split design) — [`active/TASK-051-call-record-context-quality.md`](active/TASK-051-call-record-context-quality.md) · dense LLM-grounded schema v2; UCN reads raw transcripts inside 1-month lookback, targeted call-records outside. Lands last so it inherits clean lifecycle + ledger + GDoc state. _Renumbered from TASK-045 on 2026-04-21 to resolve the ID collision with archived `TASK-045-mcp-audit-log-under-logs-dir.md` — see "Conventions" note below._

**Implementation approach:** new Cursor session per task, use `coder` → `tester` → `doc` subagent workflow per [`.cursor/rules/workflow.mdc`](../../.cursor/rules/workflow.mdc). Task files are self-contained — Problem, Goals, Scope, Non-goals, Acceptance, Verification, Sequencing. Do not parallelize 046–050. (TASK-051 lands after 050.)

**MVP / UX close-out complete:** **TASK-033**, **TASK-034**, **TASK-035**, **TASK-036**, **TASK-037** (approach B manual save), **TASK-038**, **TASK-040**, **TASK-027**, **TASK-041** (MCP customer-name pattern for `_TEST_CUSTOMER`). TASK-043 (prior E2E automation contract) superseded by TASK-044.

**Recently shipped (Wiz MCP cache, 2026-04-20):** **TASK-026**–**TASK-031** — MCP materialization pipeline, external spider, vector ingest root, playbooks + **`wiz-mcp-tools-inventory.md`**. See active files for evidence.

**Also recently shipped:** **TASK-023** / **TASK-024** / **TASK-025** (2026-04-20); optional follow-ups remain in archived task files.

**Recently complete:** Phase 3 (TASK-015–019 + Wave G close-out); batch log [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md). Next MVP backlog: [Stage 4](#backlog--stage-4-post-mvp).

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

- [x] **TASK-015** — SOC domain advisor — [`.cursor/rules/23-domain-advisor-soc.mdc`](../../.cursor/rules/23-domain-advisor-soc.mdc) · batch [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md) (Wave A)
- [x] **TASK-016** — APP, VULN, ASM, AI advisors — [`.cursor/rules/24-domain-advisor-app.mdc`](../../.cursor/rules/24-domain-advisor-app.mdc), [`25-domain-advisor-vuln.mdc`](../../.cursor/rules/25-domain-advisor-vuln.mdc), [`26-domain-advisor-asm.mdc`](../../.cursor/rules/26-domain-advisor-asm.mdc), [`27-domain-advisor-ai.mdc`](../../.cursor/rules/27-domain-advisor-ai.mdc) · optional [`docs/ai/references/customer-state-update-delta.md`](../ai/references/customer-state-update-delta.md) · batch [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md) (Wave A)
- [x] **TASK-017** — Orchestrator + task router — [`.cursor/rules/20-orchestrator.mdc`](../../.cursor/rules/20-orchestrator.mdc), [`.cursor/rules/10-task-router.mdc`](../../.cursor/rules/10-task-router.mdc) · routing note in [`docs/ai/playbooks/update-customer-notes.md`](../ai/playbooks/update-customer-notes.md) · batch [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md) (Wave B)
- [x] **TASK-018** — Exec briefing playbook — **retired** (use **Account Summary** §1); Wave C log [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md)
- [x] **TASK-019** — Stage 3 integration checklist playbook — **retired** (ad-hoc UCN regression); Wave D log [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md)

## Phase 3 close-out cleanup (after TASK-019)

**Done (2026-04):** Removed **Biome** from **`.pre-commit-config.yaml`** and deleted root **`package.json`**, **`package-lock.json`**, **`biome.json`**, **`npm ci`** in CI, and **`npm install`** in **`setEnv.sh`**. In practice Biome had only been checking a few JSON config files. The old **`biomejs/pre-commit`** hook downloaded its own Biome binary, so **`npm ci` was never required** for pre-commit to run that hook — **`npm ci` only fed** local **`node_modules/.bin/biome`** / **`lint.sh`**. **`scripts/syncNotesToMarkdown.js`** stays **named and shaped like the deployed Apps Script** (not Node-run here; **no** rename).

**Wave G (2026-04):** [x] **`99-migration-mode.mdc`** retired from **`.cursor/rules/`** → read-only **[`docs/archive/cursor-rules-retired/99-migration-mode.mdc`](../archive/cursor-rules-retired/99-migration-mode.mdc)**. [x] Historical task-archive lines that cited **`biome.json`** annotated (TASK-002 / TASK-006).

**Optional later** (when adding a real front-end):

- [ ] Reintroduce a **JS/TS linter** (Biome, ESLint, etc.) **only if** the repo gains maintained JS/TS beyond the Apps Script artifact.

## Backlog — Stage 4 (post-MVP)

- [ ] **TASK-020** — Vector DB ingestion
- [ ] **TASK-021** — `wiz_knowledge_search` MCP tool
- [ ] **TASK-022** — Advisors use vector search

## Wiz MCP cache pipeline (2026-04-20)

- [x] **TASK-026** — Tool inventory + firewall note — [`active/TASK-026-wiz-mcp-phase0-tool-inventory.md`](active/TASK-026-wiz-mcp-phase0-tool-inventory.md) · [`../ai/references/wiz-mcp-tools-inventory.md`](../ai/references/wiz-mcp-tools-inventory.md)
- [x] **TASK-027** — Discovery catalog / two-wave stop — [`active/TASK-027-wiz-discovery-catalog.md`](active/TASK-027-wiz-discovery-catalog.md)
- [x] **TASK-028** — MCP materialize — [`active/TASK-028-wiz-mcp-materialize-pipeline.md`](active/TASK-028-wiz-mcp-materialize-pipeline.md)
- [x] **TASK-029** — External spider + 365d TTL — [`active/TASK-029-external-spider-ttl.md`](active/TASK-029-external-spider-ttl.md)
- [x] **TASK-030** — Playbooks MCP-only — [`active/TASK-030-playbooks-mcp-only-docs.md`](active/TASK-030-playbooks-mcp-only-docs.md)
- [x] **TASK-031** — Vector third ingest root — [`active/TASK-031-vector-mcp-ingest-root.md`](active/TASK-031-vector-mcp-ingest-root.md)
- [x] **TASK-033** — LLM response format + activity recap playbook audit — [`active/TASK-033-llm-response-format-and-activity-recap.md`](active/TASK-033-llm-response-format-and-activity-recap.md)
- [x] **TASK-034** — MVP five flows readiness (matrix + prerequisites) — [`active/TASK-034-mvp-five-flows-readiness.md`](active/TASK-034-mvp-five-flows-readiness.md)
- [x] **TASK-035** — Product intelligence read-vs-refresh proof — [`active/TASK-035-product-intelligence-discovery-and-sync-proof.md`](active/TASK-035-product-intelligence-discovery-and-sync-proof.md)
- [x] **TASK-036** — Tutorial cache -> vector -> search — [`active/TASK-036-tutorial-wiz-cache-to-vector-search.md`](active/TASK-036-tutorial-wiz-cache-to-vector-search.md)
- [x] **TASK-037** — Persist AI account summary path (manual save mode) — [`active/TASK-037-persist-ai-account-summary-file.md`](active/TASK-037-persist-ai-account-summary-file.md)
- [x] **TASK-038** — Update Customer Notes source tuning — [`active/TASK-038-update-customer-notes-source-tuning.md`](active/TASK-038-update-customer-notes-source-tuning.md)
- [x] **TASK-041** — MCP customer-name pattern `_TEST_CUSTOMER` compatibility — [`active/TASK-041-mcp-customer-name-pattern-e2e.md`](active/TASK-041-mcp-customer-name-pattern-e2e.md)

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
- **Stage 3 (TASK-015–019 + Wave G)** — Advisors, router, orchestrator, exec briefing + debug playbooks; migration rule retired — [`archive/2026-04/PHASE3-PLAN.md`](archive/2026-04/PHASE3-PLAN.md) (2026-04-19)
- **TASK-023** — History Ledger lazy bootstrap — [`archive/2026-04/TASK-023-history-ledger-lazy-bootstrap.md`](archive/2026-04/TASK-023-history-ledger-lazy-bootstrap.md) (2026-04-20)
- **TASK-024** — Wiz cache ↔ Chroma (full pipeline + docs + MCP) — [`archive/2026-04/TASK-024-wiz-cache-vector-pipeline.md`](archive/2026-04/TASK-024-wiz-cache-vector-pipeline.md) (2026-04-20)
- **TASK-025** — Migrate wiz-local MCP pack — [`archive/2026-04/TASK-025-migrate-wiz-mcp.md`](archive/2026-04/TASK-025-migrate-wiz-mcp.md) (2026-04-20)
- **TASK-042** — E2E refresh-first Drive reset (superseded by TASK-044) — [`archive/2026-04/TASK-042-e2e-playbook-refresh-first-drive-reset.md`](archive/2026-04/TASK-042-e2e-playbook-refresh-first-drive-reset.md) (archived 2026-04-21)
- **TASK-043** — E2E `_TEST_CUSTOMER` full-automation contract (superseded by TASK-044) — [`archive/2026-04/TASK-043-e2e-test-customer-full-automation.md`](archive/2026-04/TASK-043-e2e-test-customer-full-automation.md) (archived 2026-04-21)
- **TASK-045** — MCP audit log under `./logs` — [`archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md`](archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md) (2026-04-21)
- **TASK-046** — Retire `transcript-index.json` and its MCP tools (step 1 of TASK-044 E2E fact-check follow-ups) — [`archive/2026-04/TASK-046-retire-transcript-index.md`](archive/2026-04/TASK-046-retire-transcript-index.md) (2026-04-21)
- **TASK-047** — Retire Journey Timeline; add `read_challenge_lifecycle`; enrich Account Summary; scrub harness vocab (step 2 of TASK-044 E2E fact-check follow-ups) — [`archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md`](archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md) (2026-04-21)
- **TASK-048** — Challenge lifecycle write discipline + Challenge Tracker row date bullet; required `transitioned_at`, MCP hard rejections (future date / history regression / forbidden evidence vocab); `FORBIDDEN_EVIDENCE_TERMS` code SSoT in `prestonotes_mcp/journey.py` (step 3 of TASK-044 E2E fact-check follow-ups) — [`archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md`](archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md) (2026-04-21)

## Conventions

- **Active file:** `docs/tasks/active/<TASK-XXX-short-slug>.md` — include **Legacy Reference** when porting from `../prestoNotes.orig`.
- **Archive:** `docs/tasks/archive/YYYY-MM/` when done.
- **Status markers** inside task files: `[ ] TODO` / `[x] COMPLETE`.

### Resolved ID collision — TASK-045 → TASK-051 (2026-04-21)

**Status:** resolved 2026-04-21. The active E2E fact-check follow-up originally numbered `TASK-045-call-record-context-quality.md` was renumbered to **TASK-051** to eliminate a duplicate ID with the completed audit-log task.

- **Canonical (active, call-record quality):** [`active/TASK-051-call-record-context-quality.md`](active/TASK-051-call-record-context-quality.md) — dense LLM-grounded call-record schema v2 + UCN lookback-split wiring; step 6 of the TASK-044 follow-up sequence above.
- **TASK-045 (archived, unrelated):** [`archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md`](archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md) — MCP audit log relocation under `./logs/`; completed 2026-04-21. The `TASK-045` ID now refers unambiguously to this archived item.

**Rename trail** (for anyone searching history): the renumbered file carries a header note pointing back to the original `TASK-045` ID, and all cross-references in `TASK-046` / `TASK-047` / `TASK-048` / `TASK-049` / `TASK-050` have been updated to point at `TASK-051`. Any lingering text match for "TASK-045" in `docs/tasks/active/` outside that rename-trail note is a stale reference and should be updated to `TASK-051`.
