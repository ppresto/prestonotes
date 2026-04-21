# TASK-042 — E2E playbook: refresh-first `_TEST_CUSTOMER` with deterministic Drive reset

> **Archived 2026-04-21:** Superseded by **`docs/tasks/active/TASK-044-e2e-test-customer-rebuild.md`**. The refresh-first reset approach here was kept only partially automated; TASK-044 replaces the whole harness with a single entry script + a rewritten playbook and removes the overlapping scripts/tests cited below.

**Status:** [x] COMPLETE (superseded)  
**Opened:** 2026-04-21  
**Depends on:** `scripts/e2e-test-customer.sh`, `scripts/e2e-test-customer-prep.sh`, `scripts/e2e-test-push-gdrive-notes.sh`, fixture corpus under `tests/fixtures/e2e/_TEST_CUSTOMER/`.

## Problem

The E2E flow can silently miss the intended `_TEST_CUSTOMER` refresh baseline when `_TEMPLATE` is unavailable locally (or when operators run the two-phase helper out of order). This creates confusion about whether test state was truly reset before running Cursor playbooks.

Current operator expectations:

- Start from a clean `_TEST_CUSTOMER` on Drive.
- Ensure fixture corpus (v1 first, then phase2) is what Drive and local mirror use.
- Run playbooks and observe GDoc writes in order.

## Goal

Make the first step of E2E explicit and verifiable: `_TEST_CUSTOMER` is refreshed/reset before playbooks, with a deterministic Drive baseline derived from fixtures and template artifacts.

## Key clarifications

- Copying `"_TEMPLATE/_notes-template"` into `_TEST_CUSTOMER` does **not** reset the live Google Doc object; it only copies local files.
- The existing automation resets **mirror files** and pushes customer folder contents to Drive. It does not clone/replace the underlying Google Doc ID.
- We should avoid ad-hoc `rm` commands on Drive paths and instead use scoped rsync push (`--delete`) from a known local fixture state.

## Proposed implementation

1. Add a new script: `scripts/e2e-reset-test-customer-drive.sh`
   - Pull `_TEMPLATE` + `_TEST_CUSTOMER` from Drive (`rsync-gdrive-notes.sh`).
   - Materialize fixture v1 locally (`e2e-test-customer-materialize.py apply`).
   - Run `refresh_test_customer.py --keep-call-artifacts` (or fail with clear action if `_TEMPLATE` ledger missing).
   - Run `e2e-test-customer-bump-dates.py --customer "_TEST_CUSTOMER" --incremental-gap`.
   - Run `seed-test-customer-challenge-lifecycle.py --force-reset`.
   - Push local `_TEST_CUSTOMER` to Drive via `e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"` (rsync `--delete` makes Drive match local deterministic state).
   - Regenerate `docs/ai/playbooks/e2e-test-customer-run.md`.

2. Integrate that reset script into `scripts/e2e-test-customer-prep.sh` as the first required stage (or call it from `e2e-test-customer.sh` when Drive is available).

3. Add explicit fallback behavior for missing `_TEMPLATE` ledger in the full path:
   - Use `refresh_test_customer.py --ledger greenfield` when template ledger is absent.
   - Print a warning that first ledger row will be created on the first approved ledger write.

4. Update docs:
   - `docs/ai/playbooks/e2e-test-customer.md`
   - `docs/e2e-test-customer.md`
   - `scripts/README.md`
   to reflect refresh-first contract and phase ordering (Phase 1 playbooks before Phase 2 disk re-materialize).

## Acceptance

- [ ] Running full E2E entrypoint with Drive available performs a verifiable refresh-first reset before any playbook triggers are run.
- [x] Missing `_TEMPLATE` ledger no longer fails prep; Drive reset falls back to `refresh_test_customer.py --ledger greenfield` and proceeds.
- [ ] Generated report clearly states whether refresh-first baseline was executed.
- [ ] Manual Drive `rm`/`cp` steps are no longer required in operator docs.
- [ ] Phase sequencing is explicit: Phase 1 disk reset -> Phase 1 playbooks -> Phase 2 disk merge -> Phase 2/3 playbooks.

## Verification

- [ ] `./scripts/e2e-test-customer.sh` with valid `GDRIVE_BASE_PATH` logs refresh-first stages and writes report.
- [x] `./scripts/e2e-test-customer.sh` with missing `_TEMPLATE` ledger continues using greenfield ledger mode and emits a warning.
- [ ] `uv run pytest scripts/tests/manual_e2e -q` passes.
- [ ] Add/adjust focused tests for new reset script behavior (dry-run and happy path where feasible).

## Operator runbook target (post-fix)

1. `./scripts/e2e-test-customer.sh` (Drive path)  
2. Open `docs/ai/playbooks/e2e-test-customer-run.md` and run steps 1-8 in order.  
3. Run phase2 disk merge (single command surfaced in report).  
4. Re-run Extract + UCN, then run Account Summary last.

## Notes

- This task intentionally does **not** attempt to "clone the actual Google Doc" from template; that is a separate capability and should be modeled as a distinct MCP/docs operation if needed later.
