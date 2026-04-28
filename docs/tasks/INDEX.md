# Task Index

Master backlog status for PrestoNotes v2. **Canonical task definitions:** [`project_spec.md` §9](../project_spec.md#9-master-task-backlog). **How to run migration work:** [`V2_MVP_BUILD_PLAN.md`](../V2_MVP_BUILD_PLAN.md).

**E2E / `_TEST_CUSTOMER` context:** **E2E tester SSoT** [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) — procedure [`tester-e2e-ucn.md`](../ai/playbooks/tester-e2e-ucn.md) · debug [`tester-e2e-ucn-debug.md`](../ai/playbooks/tester-e2e-ucn-debug.md). **TASK-053** (quality TOC). Harness history: archived **TASK-044** / **TASK-052** / **TASK-064**. **Prompt:** [`ai/prompts/e2e-task-execution-prompt.md`](../ai/prompts/e2e-task-execution-prompt.md). **E2E subagent:** invoke **`/tester`**. **Unit / CI after `/coder`:** [`.cursor/agents/code-tester.md`](../../.cursor/agents/code-tester.md) (**`/code-tester`**).

## Current active task

- [x] **TASK-069** — E2E tester: **post-write diff accuracy** (Account Summary + tab parity; encode “second pass” method in `tester.md` §6; planner guard ≠ full tab review) — [`active/TASK-069-e2e-tester-post-write-diff-accuracy.md`](active/TASK-069-e2e-tester-post-write-diff-accuracy.md) · **complete 2026-04-24** (landed in `tester.md` §6, `tester-e2e-ucn.md`, `11-e2e`, `e2e-task-execution-prompt.md`)
- [x] **TASK-070** — UCN: **Account Summary + Account Metadata** write completeness for **`_TEST_CUSTOMER` v1** — **complete 2026-04-24** (`v1_full` proof: contacts ≥2, challenges ≥2 + lifecycle parity, Cloud ≥3 field groups rubric-based, Metadata ≥4 fields with evidence, DAL prepend, ledger row) — [`active/TASK-070-ucn-account-summary-metadata-write-completeness.md`](active/TASK-070-ucn-account-summary-metadata-write-completeness.md)
- [x] **TASK-071** — E2E tester: post-write diff must compare **DAL meeting-block count (M)** vs **transcript lookback count (N)**; do not use `free_text.entries` length as meeting count — **complete 2026-04-24** (`tester.md` §6.1 + playbook/prompt pointers landed) — [`active/TASK-071-e2e-tester-dal-meeting-count-parity-in-post-write-diff.md`](active/TASK-071-e2e-tester-dal-meeting-count-parity-in-post-write-diff.md)
- [x] **TASK-072** — UCN deterministic planner contract: enforce **DAL parity** (`missing_meetings` ↔ prepends) and **Deal Stage trigger path** (commercial SKU token or explicit table mutation) before write — **complete 2026-04-25** (docs + preflight validator + tests + `_TEST_CUSTOMER` `v1_full` runtime proof) — [`active/TASK-072-ucn-deterministic-dal-and-deal-stage-planner-contract.md`](active/TASK-072-ucn-deterministic-dal-and-deal-stage-planner-contract.md)
- [ ] **TASK-073** — UCN: full pre-write coverage gate for **all** GDoc sections/subsections (canonical matrix + planner decisions + strict validator checks, simplification-first using existing files) — [`active/TASK-073-ucn-full-prewrite-section-subsection-coverage-gate.md`](active/TASK-073-ucn-full-prewrite-section-subsection-coverage-gate.md)
- [ ] **TASK-074** — UCN: **Accomplishments** (vendor / competitive decommission wins) + **Upsell Path** (Wiz Cloud vs Defend/Code/Sensor licensing, gap analysis, local Wiz MCP → sync cache, external references, optional discovery questions / **TASK-075** handoff) — [`active/TASK-074-ucn-accomplishments-vendor-wins-and-upsell-path-sku-gaps.md`](active/TASK-074-ucn-accomplishments-vendor-wins-and-upsell-path-sku-gaps.md)
- [ ] **TASK-075** — UCN: **Discovery questions** for **Upsell Path** (AI, org/gaps, commercial follow-up) — depends **TASK-074** — [`active/TASK-075-ucn-upsell-path-discovery-questions.md`](active/TASK-075-ucn-upsell-path-discovery-questions.md)
- [ ] **TASK-076** — **PyYAML** `safe_load` for `kb_seed_queries.yaml`; remove hand parser; tests — supports KB seed cache redesign; `pyyaml` already in `pyproject.toml` — [`active/TASK-076-pyyaml-kb-seed-queries-loader.md`](active/TASK-076-pyyaml-kb-seed-queries-loader.md)
- [ ] **TASK-068** — UCN/E2E **honesty**: **planner checklist** (no silent skips), **ledger** after write, **E2E vs prod** (7/9), **`v1_full` vs `v1_partial`**, optional **`e2e-debug`** bundle, **`e2e-catalog.txt` maintainer contract** (playbook + `tester.md` pointer) — [`active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md`](active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md)
- [ ] **TASK-032** — Follow-ups, gaps, and recommendations (Stage 4 backlog) — [`active/TASK-032-followups-and-cleanup.md`](active/TASK-032-followups-and-cleanup.md)
- [ ] **TASK-065** — Rules cleanup: remove duplication and stale references (non-E2E) — [`active/TASK-065-rules-cleanup-unused-and-duplication.md`](active/TASK-065-rules-cleanup-unused-and-duplication.md)
- [ ] **TASK-053** — UCN E2E: **GDoc v1/v2 fill gaps, `sync_notes` / Drive order, manual test recipes** (DAL for v2, metadata, `agent_run_log` verification, per-gap sub-tasks **+ T053-G call-record runtime quality** — **TOC** for quality work **T053-A–G**) — [`active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md`](active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) · push-before-pull discipline in archived **TASK-052** §0; qualitative acceptance from completed **TASK-051** → **§T053-G**.

### TASK-044 E2E fact-check follow-ups (2026-04-21)

Land **in this order** — each builds on the prior:

1. [x] **TASK-046** — Retire `transcript-index.json` and its MCP tools — [`archive/2026-04/TASK-046-retire-transcript-index.md`](archive/2026-04/TASK-046-retire-transcript-index.md) · removes a redundant artifact no current playbook depends on; unblocks Account Summary input tightening.
2. [x] **TASK-047** — Retire Journey Timeline; scrub harness vocab; enrich Account Summary — [`archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md`](archive/2026-04/TASK-047-retire-journey-timeline-into-account-summary.md) · deletes a write-only artifact, folds narrative into Account Summary, defines `FORBIDDEN_EVIDENCE_TERMS` reused by 048/049/050.
3. [x] **TASK-048** — Challenge lifecycle write discipline (+ Challenge Tracker row date bullet) — [`archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md`](archive/2026-04/TASK-048-challenge-lifecycle-write-discipline.md) · fixes call-date vs run-date bug across **both** `update_challenge_state` and GDoc Challenge Tracker row writes; forbids stub / harness evidence at MCP write time.
4. [x] **TASK-049** — History Ledger schema v3 (rationalized, no legacy) — [`archive/2026-04/TASK-049-history-ledger-schema-v3-rationalized.md`](archive/2026-04/TASK-049-history-ledger-schema-v3-rationalized.md) · collapsed 24→20 columns, dropped dup `Value Realized` / `Open Challenges` / `Aging Blockers` / `Resolved Issues` / `New Blockers` / `Key Drivers`; deleted the legacy v1→v2 migration helper outright (no legacy data).
5. [x] **TASK-050** — UCN GDoc write completeness + internal consistency — [`archive/2026-04/TASK-050-ucn-gdoc-write-completeness-consistency.md`](archive/2026-04/TASK-050-ucn-gdoc-write-completeness-consistency.md) · fixed `timestamp: null` writer bug, landed the cross-section reconciler (Risk ↔ Challenge Tracker ↔ lifecycle), Deal Stage Tracker motion capture, `agent_run_log` append contract; 15 new unit tests green. §C 15-field planner enumeration and §D DAL prepend-per-call are documented in UCN Steps 6–10 + `21-extractor.mdc`; fill-rate / DAL-count / cross-artifact bullets remain runtime-deferred until next `Run E2E Test Customer`.
6. [x] **TASK-051** — Call-record context quality (lookback-split design) — [`archive/2026-04/TASK-051-call-record-context-quality.md`](archive/2026-04/TASK-051-call-record-context-quality.md) · **COMPLETE 2026-04-23** — schema v2, MCP guardrails, goldens, `lint` gate; qualitative runtime checks → **TASK-053 § T053-G**. _Renumbered from TASK-045 on 2026-04-21 to resolve the ID collision with archived `TASK-045-mcp-audit-log-under-logs-dir.md` — see "Conventions" note below._

**Implementation approach:** new Cursor session per task; default work is **inline in the main chat** (see [`.cursor/rules/core.mdc`](../../.cursor/rules/core.mdc)). Subagents are **optional**; historical subagent packet templates are archived in [`docs/archive/cursor-rules-retired/workflow.mdc`](../archive/cursor-rules-retired/workflow.mdc). Task files are self-contained — Problem, Goals, Scope, Non-goals, Acceptance, Verification, Sequencing. Steps **046–051** of the TASK-044 follow-up sequence are **archived complete** (051 finished 2026-04-23).

**MVP / UX close-out complete:** **TASK-033**, **TASK-034**, **TASK-035**, **TASK-036**, **TASK-037** (approach B manual save), **TASK-038**, **TASK-040**, **TASK-027**, **TASK-041** (MCP customer-name pattern for `_TEST_CUSTOMER`). TASK-043 (prior E2E automation contract) superseded by TASK-044.

**Recently shipped (Wiz MCP cache, 2026-04-20):** **TASK-026**–**TASK-031** — MCP materialization pipeline, external spider, vector ingest root, playbooks + **`wiz-mcp-tools-inventory.md`**. Task files: [`docs/tasks/archive/2026-04/`](archive/2026-04/) (search by `TASK-026` … `TASK-031`).

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
- [x] **TASK-011** — `append_ledger_row` + migration (superseded by TASK-049 schema v3) — [archive](archive/2026-04/TASK-011-append-ledger-v2.md)
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

- [x] **TASK-026** — Tool inventory + firewall note — [`archive/2026-04/TASK-026-wiz-mcp-phase0-tool-inventory.md`](archive/2026-04/TASK-026-wiz-mcp-phase0-tool-inventory.md) · [`../ai/references/wiz-mcp-tools-inventory.md`](../ai/references/wiz-mcp-tools-inventory.md)
- [x] **TASK-027** — Discovery catalog / two-wave stop — [`archive/2026-04/TASK-027-wiz-discovery-catalog.md`](archive/2026-04/TASK-027-wiz-discovery-catalog.md)
- [x] **TASK-028** — MCP materialize — [`archive/2026-04/TASK-028-wiz-mcp-materialize-pipeline.md`](archive/2026-04/TASK-028-wiz-mcp-materialize-pipeline.md)
- [x] **TASK-029** — External spider + 365d TTL — [`archive/2026-04/TASK-029-external-spider-ttl.md`](archive/2026-04/TASK-029-external-spider-ttl.md)
- [x] **TASK-030** — Playbooks MCP-only — [`archive/2026-04/TASK-030-playbooks-mcp-only-docs.md`](archive/2026-04/TASK-030-playbooks-mcp-only-docs.md)
- [x] **TASK-031** — Vector third ingest root — [`archive/2026-04/TASK-031-vector-mcp-ingest-root.md`](archive/2026-04/TASK-031-vector-mcp-ingest-root.md)
- [x] **TASK-033** — LLM response format + activity recap playbook audit — [`archive/2026-04/TASK-033-llm-response-format-and-activity-recap.md`](archive/2026-04/TASK-033-llm-response-format-and-activity-recap.md)
- [x] **TASK-034** — MVP five flows readiness (matrix + prerequisites) — [`archive/2026-04/TASK-034-mvp-five-flows-readiness.md`](archive/2026-04/TASK-034-mvp-five-flows-readiness.md)
- [x] **TASK-035** — Product intelligence read-vs-refresh proof — [`archive/2026-04/TASK-035-product-intelligence-discovery-and-sync-proof.md`](archive/2026-04/TASK-035-product-intelligence-discovery-and-sync-proof.md)
- [x] **TASK-036** — Tutorial cache -> vector -> search — [`archive/2026-04/TASK-036-tutorial-wiz-cache-to-vector-search.md`](archive/2026-04/TASK-036-tutorial-wiz-cache-to-vector-search.md)
- [x] **TASK-037** — Persist AI account summary path (manual save mode) — [`archive/2026-04/TASK-037-persist-ai-account-summary-file.md`](archive/2026-04/TASK-037-persist-ai-account-summary-file.md)
- [x] **TASK-038** — Update Customer Notes source tuning — [`archive/2026-04/TASK-038-update-customer-notes-source-tuning.md`](archive/2026-04/TASK-038-update-customer-notes-source-tuning.md)
- [x] **TASK-040** — Doc README readability pass — [`archive/2026-04/TASK-040-doc-readme-readability-pass.md`](archive/2026-04/TASK-040-doc-readme-readability-pass.md)
- [x] **TASK-041** — MCP customer-name pattern `_TEST_CUSTOMER` compatibility — [`archive/2026-04/TASK-041-mcp-customer-name-pattern-e2e.md`](archive/2026-04/TASK-041-mcp-customer-name-pattern-e2e.md)

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
- **TASK-011** — `append_ledger_row` + migration (superseded by TASK-049 schema v3) — [`archive/2026-04/TASK-011-append-ledger-v2.md`](archive/2026-04/TASK-011-append-ledger-v2.md) (2026-04-19)
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
- **TASK-049** — History Ledger schema v3 (rationalized, no legacy); 24→20 columns, single `LEDGER_V3_COLUMNS` (snake_case), `append_ledger_row` with write-time validation + `LedgerValidationError` payload parity to TASK-048, `FORBIDDEN_EVIDENCE_TERMS` reused from `prestonotes_mcp/journey.py`, `migrate_ledger.py` deleted outright (step 4 of TASK-044 E2E fact-check follow-ups; runtime-only acceptance bullets deferred to next `Run E2E Test Customer`) — [`archive/2026-04/TASK-049-history-ledger-schema-v3-rationalized.md`](archive/2026-04/TASK-049-history-ledger-schema-v3-rationalized.md) (2026-04-21)
- **TASK-050** — UCN GDoc write completeness + internal consistency; `append_with_history` timestamp emission, lifecycle-authoritative Challenge Tracker reconciler (`identified→Open` / `in_progress→In Progress` / `stalled→Stalled` / `resolved→Resolved`), Deal Stage Tracker motion capture (`COMMERCIAL_SKUS` / `DEAL_STAGE_POV_PHRASES` / `DEAL_STAGE_WIN_PHRASES` → `discovery` / `pov` / `win`), one `appendix.agent_run_log` entry per successful UCN run; 15 new unit tests in `prestonotes_gdoc/tests/` (step 5 of TASK-044 E2E fact-check follow-ups; fill-rate / DAL-count / cross-artifact acceptance bullets runtime-deferred) — [`archive/2026-04/TASK-050-ucn-gdoc-write-completeness-consistency.md`](archive/2026-04/TASK-050-ucn-gdoc-write-completeness-consistency.md) (2026-04-21)
- **TASK-051** — Call-record schema v2 + MCP write guardrails + `call_records lint` + UCN / Account Summary lookback-split wiring + golden corpus (step 6 of TASK-044 E2E fact-check follow-ups; **runtime qualitative acceptance** → **TASK-053 § T053-G**) — [`archive/2026-04/TASK-051-call-record-context-quality.md`](archive/2026-04/TASK-051-call-record-context-quality.md) (2026-04-23)
- **TASK-052** — E2E `_TEST_CUSTOMER` harness: `prep-v1` / `prep-v2`, `e2e_rebaseline_customer_gdoc.py`, push-before-pull, `materialize --v2`, playbook + CI parity; **deferred** full uninterrupted 8-step proof + §J.3+ → **TASK-053** / **TASK-044** — [`archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md`](archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) (2026-04-23)
- **Batch (moved `active/` → `archive/2026-04/`, 2026-04-23):** TASK-026, TASK-027, TASK-028, TASK-029, TASK-030, TASK-031, TASK-033, TASK-034, TASK-035, TASK-036, TASK-037, TASK-038, TASK-040, TASK-041 — files live alongside other **2026-04** archives; **INDEX** “Wiz MCP cache pipeline” links above point at these paths.
- **TASK-066** — GDrive session: `setEnv`, `MYNOTES_ROOT_FOLDER_ID`, `GCLOUD_AUTH_LOGIN_COMMAND` + `./setEnv.sh --print-gdrive-auth`; shared `scripts/lib/gdrive-auth-hint.sh`; E2E shell + **`/tester`** blocked `handoff_for_next` — [`archive/2026-04/TASK-066-gdrive-setenv-auth-recovery-and-tester-prereq.md`](archive/2026-04/TASK-066-gdrive-setenv-auth-recovery-and-tester-prereq.md) (2026-04-24)
- **TASK-063** — GDoc mutation docs structure (Customer Notes hub + per-tab packs) — [`archive/2026-04/TASK-063-gdoc-mutation-docs-structure.md`](archive/2026-04/TASK-063-gdoc-mutation-docs-structure.md) (2026-04-24)
- **TASK-064** — E2E / lean-tester doc consolidation (`/tester` doctrine, `tester-e2e-ucn.md`, `docs/e2e/` retired) — [`archive/2026-04/TASK-064-e2e-tester-subagent-redesign.md`](archive/2026-04/TASK-064-e2e-tester-subagent-redesign.md) (2026-04-24)
- **TASK-044** — E2E `_TEST_CUSTOMER` harness rebuild (closed outside file; eight-step SSoT is `tester-e2e-ucn.md`) — [`archive/2026-04/TASK-044-e2e-test-customer-rebuild.md`](archive/2026-04/TASK-044-e2e-test-customer-rebuild.md) (archived 2026-04-24)
- **TASK-067** — E2E `/tester` MCP prereq smokes (prestonotes + wiz-remote fail-fast) — [`archive/2026-04/TASK-067-e2e-tester-mcp-prereq-fail-fast.md`](archive/2026-04/TASK-067-e2e-tester-mcp-prereq-fail-fast.md) (2026-04-24)

## Conventions

- **Active file:** `docs/tasks/active/<TASK-XXX-short-slug>.md` — include **Legacy Reference** when porting from `../prestoNotes.orig`.
- **Archive:** `docs/tasks/archive/YYYY-MM/` when done.
- **Status markers** inside task files: `[ ] TODO` / `[x] COMPLETE`.

### Resolved ID collision — TASK-045 → TASK-051 (2026-04-21); TASK-051 archived (2026-04-23)

**Status:** renumbering resolved 2026-04-21. **TASK-051** (call-record context quality) **completed and archived 2026-04-23** — canonical file: [`archive/2026-04/TASK-051-call-record-context-quality.md`](archive/2026-04/TASK-051-call-record-context-quality.md). **Live E2E / manual call-record quality checklist:** [`active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md`](active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) § **T053-G**.

- **TASK-045 (archived, unrelated audit-log task):** [`archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md`](archive/2026-04/TASK-045-mcp-audit-log-under-logs-dir.md) — MCP audit log relocation under `./logs/`; completed 2026-04-21. The `TASK-045` ID refers unambiguously to this item (not call-record quality).

**Rename trail** (for anyone searching history): the call-record task was originally `TASK-045-call-record-context-quality` and renumbered to **TASK-051** to eliminate a duplicate ID with the audit-log **TASK-045**. Archived follow-ups **046–050** reference **TASK-051** in prose; **active** docs should link to **`archive/2026-04/TASK-051-call-record-context-quality.md`** (or to **TASK-053 § T053-G** for runtime-only bullets).
