# TASK-043 — E2E `_TEST_CUSTOMER`: single-playbook full automation (no generated run-sheet dependency)

> **Archived 2026-04-21:** Superseded by **`docs/tasks/archive/2026-04/TASK-044-e2e-test-customer-rebuild.md`** (archived 2026-04-24). This task documented the "single playbook, no run-sheet" contract but left the shell script incapable of doing delete+bootstrap+restart-Drive, and never enforced that the agent chain through the Cursor playbook steps. TASK-044 fixes both problems by replacing the harness.

**Status:** [x] COMPLETE (superseded)  
**Opened:** 2026-04-21  
**Depends on:** `docs/ai/playbooks/tester-e2e-ucn.md`, `scripts/e2e-test-customer.sh`, `scripts/e2e-reset-test-customer-drive.sh`, `scripts/e2e-test-customer-verify.py`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`.  
**Supersedes scope in:** `TASK-042` (refresh-first reset is kept, operator/checklist complexity is removed).

## Problem

The current E2E flow is split between:

- `docs/ai/playbooks/tester-e2e-ucn.md` (operator intent), and
- generated `docs/ai/playbooks/e2e-test-customer-run.md` (checklist + pass/fail table).

That split is adding friction and hiding the real requirement: `_TEST_CUSTOMER` is deterministic test data, so the run should be one end-to-end automated harness with explicit sequencing and no approval pauses.

## Required end-state

1. **Single source of truth:** `docs/ai/playbooks/tester-e2e-ucn.md` fully defines the run order. No dependency on generated run-sheet files.
2. **Full reset every Drive run:** delete + bootstrap `_TEST_CUSTOMER`, restart Drive mount, confirm visibility, then rsync/materialize/refresh/push.
3. **No approval gates in this E2E path:** `_TEST_CUSTOMER` E2E runs end-to-end without per-write chat approvals.
4. **Fully automated phase2:** add phase2 transcripts, run extract, run UCN, continue to account summary.
5. **Validation via code, not checklists:** move validaton checks into `scripts/e2e-test-customer-verify.py` (or companion verifier checks), not manual pass/fail markdown tables.

## Scope

### A) Replace generated run-sheet contract

- Remove requirement to generate/read `docs/ai/playbooks/e2e-test-customer-run.md` for execution.
- Keep optional report output only for diagnostics (if retained), not as execution control-plane.
- Update `.cursor/rules/11-e2e-test-customer-trigger.mdc` to route directly to the main playbook sequence.

### B) Harden deterministic reset flow

Drive path in canonical sequence:

1. Delete Drive `_TEST_CUSTOMER` folder.
2. Bootstrap new `_TEST_CUSTOMER` tree.
3. Run `./scripts/restart-google-drive.sh` and wait for mount visibility.
4. Run `./scripts/e2e-test-customer.sh` (rsync pull -> v1 materialize -> refresh -> bump+gap -> seed -> push).

Local-only path remains supported when `GDRIVE_BASE_PATH` is absent.

### C) Implement E2E approval bypass for test customer

Add a narrowly scoped execution mode for `_TEST_CUSTOMER` E2E runs that bypasses normal approval pauses for write operations.

Guardrails:

- Only for customer name exactly `_TEST_CUSTOMER`.
- Only when explicit E2E flag is set (e.g. `E2E_AUTO_APPROVE_TEST_CUSTOMER=1`).
- Never changes default approval behavior for non-test customers.
- All writes still logged/auditable.

### D) Automate full playbook chain in one command

Provide a single command/script entrypoint that runs the full sequence (prep + round1 + phase2 + round2 + summary + verifier) without operator intervention except external auth/login blockers.

### E) Move assertions into verifier

Expand `scripts/e2e-test-customer-verify.py` so it becomes the validation gate.  this does not pass/fail the test yet. it provides visibility into the results so I can see what is working well or not.

- challenge tracker/lifecycle consistency
- daily activity coverage
- deal stage progression evidence checks (without hardcoding mutation instructions)
- extraction/index integrity across both phases

## Acceptance

- [x] Canonical sequence documented as delete -> bootstrap -> mount refresh -> prep -> round1 -> phase2 -> round2 -> summary -> verify.
- [x] `docs/ai/playbooks/tester-e2e-ucn.md` is the single execution source; no generated run-sheet dependency in default flow.
- [x] `_TEST_CUSTOMER` E2E path is documented/routed as no-approval pause in dedicated rule overrides.
- [x] Approval behavior remains unchanged for non-test customers (override scoped to `_TEST_CUSTOMER` E2E trigger).
- [ ] `scripts/e2e-test-customer-verify.py` returns a report with actionable failure reasons I can investigate.
- [x] Docs no longer describe this flow as “not fully automated.”

## Verification

- [ ] Add/adjust tests for new E2E orchestrator flow.
- [ ] Add/adjust tests for approval-bypass gating (`_TEST_CUSTOMER` + explicit flag only).
- [ ] Add/adjust tests for enhanced verifier checks.
- [x] Run targeted test suite for touched scripts/rules/docs (`uv run pytest scripts/tests/test_e2e_reset_test_customer_drive.py scripts/tests/test_e2e_test_customer_verify.py scripts/tests/manual_e2e/test_refresh_test_customer.py -q`).

## Notes

- This task intentionally creates a test-only execution contract for `_TEST_CUSTOMER` and does not change production-customer safety defaults.
- If platform-level MCP policy cannot be bypassed in-process, implement the E2E harness through script-level execution paths that avoid interactive approval prompts while preserving write logs.
- ./tests/fixtures/e2e/_TEST_CUSTOMER needs some cleanup.  Rename phase2 directory to v2 for consistency.  its purpose stays the same it is the second stage of the e2e test customer flow.  Remove the call-records directory from both v1, and v2 because these will be created by the extraction playbook during the e2e test.  Update all scripts, playbooks, rules, and docs to reflect these changes

## Output / Evidence

- Playbook + docs:
  - `docs/ai/playbooks/e2e-test-customer.md` *(renamed 2026-04 → `tester-e2e-ucn.md`)*
  - `docs/e2e-test-customer.md` *(old duplicate stub at repo root)*
  - `scripts/README.md`
- Scripts:
  - `scripts/e2e-test-customer.sh`
  - `scripts/e2e-reset-test-customer-drive.sh`
- Rules (E2E no-approval carve-out for `_TEST_CUSTOMER`):
  - `.cursor/rules/11-e2e-test-customer-trigger.mdc`
  - `.cursor/rules/21-extractor.mdc`
  - `.cursor/rules/20-orchestrator.mdc`
  - `.cursor/rules/core.mdc`
- Tests:
  - `scripts/tests/test_e2e_reset_test_customer_drive.py`

