# PHASE3-PLAN — Stage 3 execution plan (TASK-015–019 + close-out)

**Status:** **Complete** (waves A–G). Canonical specs: [`docs/project_spec.md` §9](../../../project_spec.md#9-master-task-backlog) Stage 3 subsection.

### Wave A (TASK-015 + TASK-016) — done

- [x] **TASK-015** — `.cursor/rules/23-domain-advisor-soc.mdc`
- [x] **TASK-016** — `.cursor/rules/24-domain-advisor-app.mdc`, `25-domain-advisor-vuln.mdc`, `26-domain-advisor-asm.mdc`, `27-domain-advisor-ai.mdc`
- [x] Optional reference — `docs/ai/references/customer-state-update-delta.md`
- [x] `scripts/ci/required-paths.manifest` updated for new paths

**Verification (Wave A / coder):** `bash .cursor/skills/test.sh` (36 passed), `bash .cursor/skills/lint.sh` (all checks passed), `bash scripts/ci/check-repo-integrity.sh` (Repo integrity OK) — all exit code 0.

### Wave B (TASK-017) — done

- [x] **TASK-017** — `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/10-task-router.mdc` (route **`Update Customer Notes for [CustomerName]`** to orchestrator per §9; **`alwaysApply: false`** + globs so rules do not fight **`workflow.mdc`**)
- [x] Playbook **`docs/ai/playbooks/update-customer-notes.md`** — routing blurb: prefer orchestrator for multi-advisor flow; keep monolithic steps as fallback until TASK-019
- [x] `scripts/ci/required-paths.manifest` updated for new rule paths

**Verification (Wave B / coder):** `bash .cursor/skills/test.sh` (37 passed), `bash .cursor/skills/lint.sh` (all checks passed), `bash scripts/ci/check-repo-integrity.sh` (Repo integrity OK) — all exit code 0.

### Wave C (TASK-018) — done

- [x] **TASK-018** — **`docs/ai/playbooks/run-exec-briefing.md`** (trigger **`Run Exec Briefing for [CustomerName]`** per §9; links **`exec-summary-template.md`**)
- [x] **`docs/project_spec.md` §11** — `Run Exec Briefing` row aligned to **`[CustomerName]`** and playbook path; **`README.md`** MVP table row added
- [x] **`scripts/ci/required-paths.manifest`** — **`run-exec-briefing.md`**

**Verification (Wave C / coder):** `bash .cursor/skills/test.sh` (38 passed), `bash .cursor/skills/lint.sh` (all checks passed), `bash scripts/ci/check-repo-integrity.sh` (Repo integrity OK) — all exit code 0.

### Wave D (TASK-019) — done

- [x] **TASK-019** — **`docs/ai/playbooks/debug-pipeline.md`** (numbered checklist: orchestrator steps, monolithic **`update-customer-notes.md`** fallback, **`read_doc`** diff, ledger row, audit log, quality compare)
- [x] **`update-customer-notes.md`** — **kept** as canonical monolithic fallback (no archive); **`debug-pipeline.md`** states this explicitly
- [x] **`scripts/ci/required-paths.manifest`** — **`debug-pipeline.md`**

**Verification (Wave D / coder):** `bash .cursor/skills/test.sh` (38 passed), `bash .cursor/skills/lint.sh` (all checks passed), `bash scripts/ci/check-repo-integrity.sh` (Repo integrity OK) — all exit code 0.

### Wave G (Phase 3 close-out) — done

- [x] **Apps Script source** — **`scripts/syncNotesToMarkdown.js`** stays **as deployed** (mirrors Apps Script; **no** rename to `.gs.txt`).
- [x] **`99-migration-mode.mdc`** — removed from **`.cursor/rules/`**; copy preserved at **`docs/archive/cursor-rules-retired/99-migration-mode.mdc`** (see README in that folder). Ongoing migration: **`docs/MIGRATION_GUIDE.md`**, **`workflow.mdc`**.
- [x] **Historical archive docs** — task archive lines that cited **`biome.json`** annotated for **2026-04** Biome / root npm removal (see **`docs/tasks/INDEX.md`** Phase 3 close-out).

## Execution waves (subagent sessions)

| Wave | Task(s) | Subagent | Deliverables (from §9) |
|------|---------|----------|-------------------------|
| **A** | **TASK-015** + **TASK-016** | **`/coder`** | `.cursor/rules/23-domain-advisor-soc.mdc` … `27-domain-advisor-ai.mdc`; optional **`docs/ai/references/customer-state-update-delta.md`** (contract for `CustomerStateUpdate.json` consumed by advisors). |
| **B** | **TASK-017** | **`/coder`** | `.cursor/rules/20-orchestrator.mdc`, **new** `.cursor/rules/10-task-router.mdc` (route **`Update Customer Notes for [Name]`** to orchestrator per §9). Wire `alwaysApply` / `globs` so router + orchestrator do not fight **`workflow.mdc`**. |
| **C** | **TASK-018** | **`/coder`** | `docs/ai/playbooks/run-exec-briefing.md` + trigger **`Run Exec Briefing for [CustomerName]`** in [`project_spec.md` §11](../../../project_spec.md#11-trigger-phrase-reference-mvp) if missing. |
| **D** | **TASK-019** | **`/coder`** | `docs/ai/playbooks/debug-pipeline.md`; **`scripts/ci/required-paths.manifest`** entries for new playbooks/rules; note in plan when **`update-customer-notes.md`** stays canonical vs orchestrator-only (§9 says “Modified: archived old” — prefer **keep** playbook as fallback until manual archive). |
| **E** | **`/tester`** | After each wave | `bash .cursor/skills/test.sh`, `bash .cursor/skills/lint.sh`, `bash scripts/ci/check-repo-integrity.sh`. |
| **F** | **`/doc`** | After tester green | README “MVP playbooks” table + [`docs/tasks/INDEX.md`](../../INDEX.md) Stage 3 checkboxes; [`docs/V2_MVP_BUILD_PLAN.md`](../../../V2_MVP_BUILD_PLAN.md) §11 pointer. |
| **G** | **Phase 3 close-out cleanup** | **`/coder`** | Keep **`syncNotesToMarkdown.js`** name aligned with deployed Apps Script; archive **`99-migration-mode.mdc`** to **`docs/archive/cursor-rules-retired/`**; refresh historical **biome** mentions in task archive. |

## Constraints (non-negotiable)

- **Wiz lookup:** Advisors use **wiz-local** (or configured) MCP tool names as in **`21-extractor` / playbooks** — do not hardcode API keys.
- **Writes:** Orchestrator **step 9** only after explicit user approval in chat; same contract as existing **`write_doc`** / **`append_ledger_v2`** rules in **`core.mdc`**.
- **ASM (TASK-016):** Rule text must describe **`architecture_diagram_paths`** and image read (base64) **without** implementing MCP binary read unless already available — prefer “use **`read_doc`** / file tools for paths under repo **`MyNotes/`**” pattern.

### Wave E (`/tester`) — done

**Verification:** `test.sh`, `lint.sh`, `check-repo-integrity.sh`, `uv run pre-commit run --all-files` — exit 0 (see tester Output Contract).

### Wave F (`/doc`) — done

**Files:** `docs/tasks/INDEX.md`, `README.md`, `docs/V2_MVP_BUILD_PLAN.md` §11 (see doc Output Contract).

## Archive note

This file lived under **`docs/tasks/active/`** until Phase 3 Wave G close-out (**2026-04**). Use this copy as the batch log for **TASK-015–019** + close-out.
