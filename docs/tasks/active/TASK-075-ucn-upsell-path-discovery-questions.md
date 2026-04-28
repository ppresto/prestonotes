# TASK-075 — UCN: Post-mutation enrichment and discovery-question generation for Upsell Path

**Status:** [ ] not started (detailed follow-up spec ready; execute after **TASK-074**)  
**Opened:** 2026-04-26  
**Updated:** 2026-04-27

**Depends on:** **TASK-074** (Upsell rubric, local Wiz snapshot prereq in Product Intelligence, and final mutation review pattern)

## Problem

`TASK-074` establishes baseline product truth and initial mutation generation. After that baseline exists, UCN still needs a second pass that:

1. Mines transcripts + notes for unresolved security themes and customer-specific gap signals.
2. Converts those signals into prioritized ad hoc `wiz_docs_knowledge_base` queries.
3. Pulls additional product and industry context.
4. Re-reviews the existing `mutation.json` to decide whether Upsell Path (and future Recommendations) should change.

Without this follow-up pass, UCN risks either:
- stopping at generic upsell language when high-value context exists but was not queried, or
- skipping discovery guidance when evidence is thin but actionable next-call questions are possible.

## Confirmed Direction from Current Session

- Wiz snapshot prereq remains in the Product Intelligence playbook path (from `TASK-074` decisions).
- Post-initial-mutation enrichment should run **always** (not optional/conditional).
- Final review should update `mutation.json` **in place** for speed, with mandatory pre/post review traceability.
- Recommendations are not fully designed yet; `TASK-075` must carry that design as an explicit follow-up stream without blocking core Upsell improvements.

## Goals

- Build a deterministic post-mutation enrichment step that converts account evidence into prioritized ad hoc Wiz MCP queries.
- Produce a high-signal, ranked term/query list from transcripts and notes (not a flat keyword dump).
- Generate 3-7 discovery questions when the corpus cannot support high-confidence upsell claims.
- Re-review and update `mutation.json` in place only when added context materially improves accuracy or relevance.
- Emit an operator-readable audit artifact capturing what changed and why.

## Non-goals

- Replacing `TASK-074` Product Intelligence prereq or seed snapshot refresh behavior.
- Running full recursive product-intelligence corpus loads in this phase.
- Finalizing a broad, customer-facing Recommendations framework across all tabs; this task scopes Recommendations to an optional, controlled extension point.

## File-Minimization Strategy

- Reuse existing files first:
  - `docs/ai/playbooks/load-product-intelligence.md`
  - `docs/ai/playbooks/update-customer-notes.md`
  - `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md`
  - `prestonotes_gdoc/update-gdoc-customer-notes.py` and existing tests
- Prefer extending existing scripts over adding new ones.
- New script files are allowed only when they reduce repeated manual MCP-query and review work.
- New markdown files are discouraged unless a new standalone operator workflow cannot fit in existing task/playbook docs.
- If a new skill is introduced, justify it by repetitive operator friction that cannot be solved by playbook/script updates.

## Detailed Flow (Post-TASK-074)

1. **Input state**
   - Initial `mutation.json` already exists from standard UCN flow.
   - Product-intelligence prereq snapshots/ext links are already preseeded per `TASK-074`.

2. **Evidence mining**
   - Parse in-window transcripts, call-records, notes mirror, and AI insights for:
     - explicit pain points (security operations, compliance, cloud risk, AppSec, AI exposure),
     - implicit blockers (ownership ambiguity, process gaps, tooling overlap),
     - commercial signals (expansion constraints, decommission motion, urgency).

3. **Term generation and prioritization**
   - Build candidate query terms from evidence clusters.
   - Rank by weighted factors:
     - customer relevance,
     - upsell decision impact,
     - confidence from source evidence,
     - expected documentation precision.
   - Produce a bounded ranked set (for example top N, with low-priority overflow truncated).

4. **Ad hoc Wiz MCP enrichment**
   - Run targeted `wiz_docs_knowledge_base` calls using ranked terms.
   - Persist ad hoc context in the same snapshot style used in `TASK-074`.
   - Flag stale/missing responses; do not fabricate.

5. **Final mutation review**
   - Create a pre-review snapshot/diff artifact of `mutation.json`.
   - Re-evaluate Upsell Path claims against new context.
   - Optionally annotate a future Recommendations candidate area (if schema placeholder exists).
   - Update `mutation.json` in place when evidence justifies change.
   - Emit post-review rationale artifact (`retain`, `adjust`, `add`, `remove` decisions).

6. **Discovery-question fallback**
   - When confidence is insufficient for direct upsell statements, output 3-7 targeted discovery questions.
   - Questions must be role-aware (for example SOC/IR, Cloud/Vuln, Product/AppSec, AI owner) and next-call actionable.

## Deliverables

- Playbook/task guidance describing:
  - evidence-mining inputs,
  - query-term ranking method,
  - ad hoc query execution pattern,
  - final in-place review with audit output.
- Example artifacts for at least one `_TEST_CUSTOMER` or controlled dry run:
  - ranked term/query list,
  - ad hoc query results summary,
  - mutation pre/post review rationale,
  - discovery-question output when evidence is thin.

## Acceptance

- [ ] A1 — `TASK-075` is explicitly linked from the UCN flow as a post-initial-mutation enrichment stage (execute after `TASK-074` baseline path).
- [ ] A2 — One run demonstrates ranked ad hoc query term generation from transcript/note evidence (not hardcoded static list).
- [ ] A3 — One run demonstrates targeted `wiz_docs_knowledge_base` enrichment and snapshot persistence using `TASK-074` conventions.
- [ ] A4 — Final mutation re-review performs in-place update only with pre/post review artifact and explicit change rationale.
- [ ] A5 — When evidence is thin, output includes 3-7 concrete discovery questions instead of speculative upsell claims.
- [ ] A6 — If no new credible evidence is found, final review records a no-change decision (prevents mutation churn).

## Verification

- Doc-only phase: peer review task clarity, sequencing, and acceptance precision.
- Implementation phase (after build starts):
  - `bash .cursor/skills/lint.sh`
  - `bash .cursor/skills/test.sh`
  - `bash scripts/ci/check-repo-integrity.sh` if manifests/rules/playbook routing change.
- Scenario checks:
  - strong-evidence case (upsell refinement),
  - weak-evidence case (discovery questions),
  - no-new-evidence case (no mutation change).

## Open Design Item (Intentionally Carried)

- **Recommendations schema and placement** remain not fully designed.
  - For this task, treat Recommendations as a non-blocking extension point.
  - Core success criteria stay focused on Upsell enrichment + discovery-question quality + controlled mutation review.

## Sequencing

1. Complete and merge `TASK-074` baseline wiring.
2. Start `TASK-075` implementation using this detailed scope.
3. Validate on `_TEST_CUSTOMER` / dry-run fixtures.
4. Decide whether to split Recommendations schema into a dedicated follow-up task if complexity grows.
