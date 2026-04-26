# TASK-065 — Rules cleanup: remove duplication and stale references (non-E2E)

**Status:** [ ] TODO  
**Opened:** 2026-04-24  
**Depends on:** TASK-063 (docs structure); coordinate with TASK-032 for backlog hygiene.  
**Constraint:** Do **not** modify tester or `_TEST_CUSTOMER` E2E surfaces in this task (`.cursor/agents/tester.md`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`, `docs/ai/playbooks/tester-e2e-ucn*.md`).

## Problem

The rules stack under `.cursor/rules/` is carrying duplicated operational detail across:

- rule-to-rule overlap (`core.mdc`, `20-orchestrator.mdc`, `21-extractor.mdc`, `10-task-router.mdc`, domain advisors),
- rule-to-playbook overlap (`update-customer-notes.md`, `extract-call-records.md`),
- rule-to-reference/spec overlap (`docs/ai/references/*`, `docs/project_spec.md`).

This makes maintenance slower and creates drift risk when one copy updates but others do not.

## Goal

Keep rules focused on **execution boundaries** and **routing**, while moving stable domain/process detail to canonical references or playbooks that rules point to.

## Scope (this task)

1. Audit `.cursor/rules/` for duplicated paragraphs, repeated checklists, and stale compatibility notes.
2. Define canonical ownership per topic:
   - routing and approval gates (rules),
   - long procedural step lists (playbooks),
   - domain schema/taxonomy/reference semantics (`docs/ai/references/*`),
   - architecture/task history (`docs/project_spec.md`).
3. Reduce duplication in non-E2E rules first:
   - `10-task-router.mdc`
   - `20-orchestrator.mdc`
   - `21-extractor.mdc`
   - `core.mdc`
   - `23`–`27` domain-advisor rules
   - `ai_learnings.mdc`
4. Keep behavior unchanged while shortening repeated prose into references.

## Non-goals

- No change to tester/E2E behavior or docs.
- No MCP tool behavior changes.
- No refactor of task-index policy beyond links needed for this cleanup.

## Acceptance

- [ ] A duplication matrix exists (source file -> duplicate target -> canonical owner -> action).
- [ ] Non-E2E rules above are trimmed to remove repeated procedural prose where a canonical doc already exists.
- [ ] Any removed/retired references in non-E2E rules are either deleted or clearly marked as historical with one pointer.
- [ ] `docs/ai/playbooks/update-customer-notes.md`, `docs/ai/playbooks/extract-call-records.md`, and `docs/ai/references/customer-state-update-delta.md` remain the canonical long-form procedure/reference targets for their domains.
- [ ] `docs/project_spec.md` remains architecture/task-history source of truth; rules keep only the minimum needed pointers.

## Verification

- [ ] `rg "\.cursor/rules/.*\.mdc" docs/ai/playbooks docs/ai/references .cursor/agents` shows expected links and no broken renamed paths.
- [ ] Spot check: run one non-E2E flow prompt (`Update Customer Notes for <customer>`) in dry-run mode and confirm routing/gates still match rule intent.
- [ ] `bash scripts/ci/check-repo-integrity.sh` passes.

## Suggested sequencing

1. Build duplication matrix (rules vs playbooks/references/spec).
2. Trim non-E2E rules in smallest-risk order: advisor rules -> router -> orchestrator/extractor/core.
3. Re-run link checks and integrity script.
4. Land docs summary of what was consolidated and where canonical ownership now lives.
