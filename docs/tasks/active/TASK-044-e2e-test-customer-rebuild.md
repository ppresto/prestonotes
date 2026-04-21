# TASK-044 — E2E `_TEST_CUSTOMER`: rebuild clean (delete, single script, playbook chain)

**Status:** [ ] IN PROGRESS
**Opened:** 2026-04-21
**Supersedes:** `TASK-042`, `TASK-043` (both left the harness half-automated; this task finishes the job by deleting dead scaffolding and producing a single repeatable flow).
**Related rules:** `.cursor/rules/11-e2e-test-customer-trigger.mdc`, `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc`.

---

## Problem (root-cause of the past 20 failed runs)

The current `_TEST_CUSTOMER` E2E flow is a tangle of overlapping scripts, tests, and docs. The canonical playbook promises a full delete→bootstrap→prep→playbooks→verify chain, but:

1. The "delete + bootstrap" and "restart Drive mount" steps are documented as **operator prerequisites** inside `scripts/e2e-reset-test-customer-drive.sh`. No script actually performs them. `./scripts/e2e-test-customer.sh` rsyncs and **preserves** whatever `_TEST_CUSTOMER` was already on Drive.
2. Half the E2E sequence is **Cursor chat playbooks** (Load Context, Extract, Test Extraction, UCN, Account Summary). They are not callable from a shell script, but the rules / trigger files do not enforce that the agent actually runs them all end-to-end. Agents regularly stop after the shell script completes.
3. There are **multiple parallel harnesses** (`e2e-test-customer.sh`, `e2e-test-customer-prep.sh`, `e2e-reset-test-customer-drive.sh`, `e2e-full-validation.py`/`.sh`, `e2e-test-customer-report.py`, `refresh_test_customer.py`, `seed-test-customer-challenge-lifecycle.py`) plus four+ pytest files validating those scripts against themselves. None of them catch the real failure mode (LLM playbook steps not running).
4. `phase2/` fixtures violate the v1/v2 naming convention everywhere else in the codebase.

---

## Required end-state

One **single shell entry point**, one **short playbook**, zero dead scaffolding. The chain is **10 steps** (3 script invocations + 7 chat-playbook triggers).

- **Script:** `scripts/e2e-test-customer.sh <reset|v1|v2>` — the only script the flow invokes.
- **Playbook:** `docs/ai/playbooks/e2e-test-customer.md` — the only doc the agent needs to follow.
- **Rule:** `.cursor/rules/11-e2e-test-customer-trigger.mdc` — binds the trigger phrases to that playbook, forbids stopping partway.
- **Approval bypass** for `_TEST_CUSTOMER` stays exactly as in `20-orchestrator.mdc`, `21-extractor.mdc`, `core.mdc` (already in place from TASK-043).
- **No** verifier script, **no** pytest coverage of the E2E harness itself (we validate by running the harness end-to-end; the user reviews the artifacts manually).

### Canonical sequence (what the agent runs, in order, with no detours)

1. `./scripts/e2e-test-customer.sh reset`
   Hard-deletes `_TEST_CUSTOMER` on Drive (API trash) and in the repo mirror, restarts Google Drive, waits for the mount to show `_TEST_CUSTOMER` absent. Leaves a clean slate.
2. **Chat trigger:** `Bootstrap Customer for _TEST_CUSTOMER`
   Exercises the **bootstrap playbook** via MCP `bootstrap_customer` (dry_run=false, bypassed approvals for `_TEST_CUSTOMER`). Produces the fresh Drive folder, `AI_Insights/`, `Transcripts/`, `_TEST_CUSTOMER Notes.gdoc` copied from template.
3. `./scripts/e2e-test-customer.sh v1`
   Materializes `tests/fixtures/e2e/_TEST_CUSTOMER/v1/` (transcripts + starter call-records) into the fresh customer folder, rolls dates forward into the 30-day lookback window, and pushes to Drive so `sync_notes` / `sync_transcripts` see the corpus.
4. **Chat:** `Load Customer Context for _TEST_CUSTOMER`
5. **Chat:** `Extract Call Records for _TEST_CUSTOMER`
6. **Chat:** `Update Customer Notes for _TEST_CUSTOMER`
7. `./scripts/e2e-test-customer.sh v2`
   Merges `tests/fixtures/e2e/_TEST_CUSTOMER/v2/` (commercial expansion transcripts only) on top of v1, rolls dates, pushes to Drive.
8. **Chat:** `Extract Call Records for _TEST_CUSTOMER`
9. **Chat:** `Update Customer Notes for _TEST_CUSTOMER`
10. **Chat:** `Run Account Summary for _TEST_CUSTOMER`

Validation for now is **manual** — operator reviews the GDoc + on-disk artifacts. Automated verification can be added in a later task if desired; it is out of scope here.

---

## Scope

### A) Delete: remove dead scaffolding first (clean slate before building)

Remove (script-level `rm`, not hidden behind flags):

- `scripts/e2e-test-customer-prep.sh` — compat wrapper, no value.
- `scripts/e2e-reset-test-customer-drive.sh` — logic folds into the new single script.
- `scripts/e2e-full-validation.py`, `scripts/e2e-full-validation.sh` — parallel older harness.
- `scripts/e2e-test-customer-report.py` — old run-sheet generator (TASK-043 already says it is not required).
- `scripts/e2e-test-customer-verify.py` — validation is manual for now.
- `scripts/seed-test-customer-challenge-lifecycle.py` — lifecycle must be produced by the real UCN playbook, not a shortcut.
- `scripts/refresh_test_customer.py` — replaced by `reset` (hard delete) + `bootstrap_customer` playbook.

Tests to remove (user explicitly called these out as noise):

- `scripts/tests/test_e2e_reset_test_customer_drive.py`
- `scripts/tests/test_e2e_test_customer_bump_dates.py`
- `scripts/tests/test_e2e_test_customer_materialize.py`
- `scripts/tests/test_e2e_test_customer_verify.py`
- `scripts/tests/manual_e2e/test_refresh_test_customer.py`
- `scripts/tests/manual_e2e/test_seed_challenge_lifecycle.py`
- Remove `scripts/tests/manual_e2e/` if it is empty after the two deletes.

Remove every import / reference of the deleted files from:

- `docs/MIGRATION_GUIDE.md`
- `scripts/README.md`
- `scripts/ci/required-paths.manifest`
- `docs/tasks/active/TASK-042-e2e-playbook-refresh-first-drive-reset.md` (move to `docs/tasks/archive/2026-04/` — superseded)
- `docs/tasks/active/TASK-043-e2e-test-customer-full-automation.md` (move to `docs/tasks/archive/2026-04/` — superseded by this task)
- Anywhere else grep finds them.

Other cleanup:

- Delete `docs/e2e-test-customer.md` (its only purpose is a duplicate of the playbook; we keep the playbook as the single source of truth).
- Rename `tests/fixtures/e2e/_TEST_CUSTOMER/phase2/` → `v2/`. Update `tests/fixtures/e2e/_TEST_CUSTOMER/README.md` and any references that still say `phase2`.

After cleanup, commit/verify the repo is in a stable state (still builds, remaining pytest still passes) before building.

### B) Build: one script, one playbook, one rule

#### B1. `scripts/e2e-test-customer.sh` (single entry, subcommands)

```text
./scripts/e2e-test-customer.sh reset
./scripts/e2e-test-customer.sh v1
./scripts/e2e-test-customer.sh v2
```

Shared behavior:

- Source `./setEnv.sh` so `GDRIVE_BASE_PATH` + `.venv` + gcloud auth hints are loaded.
- `set -euo pipefail`; fail loudly with an actionable error when a prerequisite is missing (mount absent, gcloud unauthenticated, `.cursor/mcp.env` incomplete).
- All three subcommands are **idempotent** (safe to re-run).

`reset`:

- Trash the Drive `_TEST_CUSTOMER` folder via Drive API (new helper `prestonotes_gdoc/drive-trash-customer.py` using the same auth pattern as `000-bootstrap-gdoc-customer-notes.py`; sends `PATCH /files/{id}` with `{"trashed": true}`; idempotent — no-op when the folder is already absent).
- Remove the local `MyNotes/Customers/_TEST_CUSTOMER/` tree.
- Run `./scripts/restart-google-drive.sh 5` and poll the mount until `_TEST_CUSTOMER` disappears (bounded timeout, clear error on timeout).
- Print one line that tells the operator (or agent) the next trigger: `Bootstrap Customer for _TEST_CUSTOMER`.

`v1`:

- Require that `MyNotes/Customers/_TEST_CUSTOMER/` exists and has the bootstrap-produced skeleton (fail fast otherwise — "run reset + Bootstrap Customer first").
- Copy `tests/fixtures/e2e/_TEST_CUSTOMER/v1/Transcripts/*.txt` into `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/`.
- Copy `tests/fixtures/e2e/_TEST_CUSTOMER/v1/call-records/*.json` into `MyNotes/Customers/_TEST_CUSTOMER/call-records/`.
- Roll dates forward using the existing date-bump helper (ported into a small library module under `scripts/_e2e_lib/` since its stand-alone script is being removed; or keep the script file and delete only the CLI wrapper — decision in implementation, but exposed only through `e2e-test-customer.sh`).
- Push to Drive via `scripts/e2e-test-push-gdrive-notes.sh _TEST_CUSTOMER` (kept).

`v2`:

- Require v1 has already been applied (call-records present, index non-empty).
- Copy `tests/fixtures/e2e/_TEST_CUSTOMER/v2/Transcripts/*.txt` on top (transcripts only; call-records come from the round-2 Extract playbook).
- Re-roll dates (no incremental gap — round-2 is additive).
- Push to Drive.

#### B2. `docs/ai/playbooks/e2e-test-customer.md`

Rewrite as a short, numbered, zero-ambiguity playbook that lists exactly the 10 steps above. Keep the contract:

- `_TEST_CUSTOMER` is test data; no approval pauses.
- The playbook **is** the single source of truth; there is no generated run-sheet, no verifier gate.
- If any step fails, stop, fix, and resume from that step.

#### B3. `.cursor/rules/11-e2e-test-customer-trigger.mdc`

- Keep trigger phrases (`Run E2E Test Customer`, `run e2e test customer`, `E2E Test Customer _TEST_CUSTOMER`).
- Add an explicit instruction that the agent must execute all 10 steps in one session without stopping for approval, without substituting session context for verification, and without skipping chat playbook steps. Any deviation is a failure.

#### B4. Approval bypass (already in place — confirm)

Leave the TASK-043 override paragraphs in `20-orchestrator.mdc`, `21-extractor.mdc`, `core.mdc` as-is, but update the cross-reference from "TASK-043" to "TASK-044" so future readers find this task.

---

## Acceptance

- [ ] All files listed in **Scope A** are deleted and no references remain (grep-verified).
- [ ] `tests/fixtures/e2e/_TEST_CUSTOMER/phase2/` renamed to `v2/`; every reference updated.
- [ ] `scripts/e2e-test-customer.sh` is the **only** E2E shell entry point and supports `reset`, `v1`, `v2` with idempotent behavior.
- [ ] New helper `prestonotes_gdoc/drive-trash-customer.py` (or equivalent) trashes the Drive folder via API and is wired into `reset`.
- [ ] `docs/ai/playbooks/e2e-test-customer.md` lists the canonical 10-step sequence and nothing else.
- [ ] `.cursor/rules/11-e2e-test-customer-trigger.mdc` forbids stopping partway and pins the playbook.
- [ ] Approval-bypass rule overrides in `20-orchestrator.mdc`, `21-extractor.mdc`, `core.mdc` still present and reference TASK-044.
- [ ] TASK-042 and TASK-043 moved to `docs/tasks/archive/2026-04/` with a one-line note pointing to TASK-044.

## Verification

- [ ] `bash .cursor/skills/lint.sh` clean for touched files.
- [ ] `bash .cursor/skills/test.sh` green for remaining suites (the E2E test files are **gone**, so this should be faster/greener than before).
- [ ] `bash scripts/ci/check-repo-integrity.sh` green (manifest updated for deletions).
- [ ] End-to-end validation run:
  - Start a fresh Cursor chat, issue only the trigger `Run E2E Test Customer` (no other context).
  - Observe that the agent executes all 10 steps in order, bypasses approvals for `_TEST_CUSTOMER`, and produces the expected artifacts (bootstrapped folder, v1 corpus, extracted call records, updated GDoc, journey timeline, v2 corpus, round-2 extract + UCN, account summary).
  - Any skipped step or error is a failure — fix the script / playbook / rule and re-run. Fixes must live in the repo (never in session context).

## Explicit non-goals (keep the scope small)

- **No** automated verifier — manual artifact review only.
- **No** unit tests covering the new E2E script — the validation run is the test.
- **No** rewriting of `bootstrap-customer.md`, UCN, Extract, or Account Summary playbooks. They are consumed as-is; this task only orchestrates them.
- **No** new MCP tools beyond the tiny Drive-trash helper needed by `reset`.

## Output / Evidence

### Phase 1 — cleanup (complete 2026-04-21)

- Deleted scripts: `scripts/e2e-test-customer.sh` (old broken entry), `scripts/e2e-test-customer-prep.sh`, `scripts/e2e-reset-test-customer-drive.sh`, `scripts/e2e-full-validation.py`, `scripts/e2e-full-validation.sh`, `scripts/e2e-test-customer-report.py`, `scripts/e2e-test-customer-verify.py`, `scripts/seed-test-customer-challenge-lifecycle.py`, `scripts/refresh_test_customer.py`.
- Deleted tests: `scripts/tests/test_e2e_reset_test_customer_drive.py`, `scripts/tests/test_e2e_test_customer_bump_dates.py`, `scripts/tests/test_e2e_test_customer_materialize.py`, `scripts/tests/test_e2e_test_customer_verify.py`, `scripts/tests/manual_e2e/test_refresh_test_customer.py`, `scripts/tests/manual_e2e/test_seed_challenge_lifecycle.py`, plus the empty `scripts/tests/manual_e2e/` directory.
- Deleted doc: `docs/e2e-test-customer.md` (duplicate).
- Renamed fixture: `tests/fixtures/e2e/_TEST_CUSTOMER/phase2/` → `tests/fixtures/e2e/_TEST_CUSTOMER/v2/` (also dropped empty `call-records/` subdir — v2 is transcripts-only).
- Archived: `TASK-042` and `TASK-043` moved to `docs/tasks/archive/2026-04/` with superseded-by headers; `docs/tasks/INDEX.md` updated.
- Reference cleanups: `scripts/ci/required-paths.manifest`, `scripts/README.md`, `tests/fixtures/e2e/_TEST_CUSTOMER/README.md`, `docs/MIGRATION_GUIDE.md`, `docs/ai/playbooks/bootstrap-customer.md`, `docs/ai/playbooks/run-journey-timeline.md`, `.gitignore`.
- Fixture-script rename: `scripts/e2e-test-customer-materialize.py` — `phase2`/`--phase2` → `v2`/`--v2` throughout.

### Phase 2 — build (complete 2026-04-21)

- New: `prestonotes_gdoc/drive-trash-customer.py` — API-trash helper. Resolves the Customers folder id via the `_TEMPLATE` `.gdoc` stub (same path as `000-bootstrap-gdoc-customer-notes.py`), then `PATCH /files/{id} {"trashed": true}`. Idempotent; supports `--dry-run` and `--json`.
- New: `scripts/e2e-test-customer.sh` — single entry, three subcommands:
  - `reset`: invokes `drive-trash-customer.py`, removes local `MyNotes/Customers/_TEST_CUSTOMER/`, runs `restart-google-drive.sh`, polls mount until absent.
  - `v1`: rsyncs bootstrap skeleton from Drive, runs `e2e-test-customer-materialize.py apply`, runs `e2e-test-customer-bump-dates.py`, pushes mirror via `e2e-test-push-gdrive-notes.sh`.
  - `v2`: same as v1 with `--v2` flag for materialize (transcripts only) + guard that round-1 call-records exist.
  - All three load `.cursor/mcp.env` via `setEnv.sh` (with arg shielding so `--help` does not collide).
  - Each subcommand prints the next expected action (shell command or chat trigger).
- Rewritten: `docs/ai/playbooks/e2e-test-customer.md` — canonical 10-step sequence, contract, prerequisites, manual verification checklist.
- Rewritten: `.cursor/rules/11-e2e-test-customer-trigger.mdc` — hard rules forbidding skips, reorder, "context substitution", or old-script calls; mandates surfacing progress after each step.
- Cross-references updated: `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc` — all "TASK-043 override" annotations now read "TASK-044 override" and point at the new trigger rule + playbook.
- Manifest: `scripts/ci/required-paths.manifest` updated with the four retained helpers + new trash helper.

### Verification (pre-flight)

- `bash .cursor/skills/lint.sh` — clean.
- `bash .cursor/skills/test.sh` — 72 passed.
- `bash scripts/e2e-test-customer.sh` (no args) — prints the correct usage without colliding with `setEnv.sh`.
- `bash -n scripts/e2e-test-customer.sh` — valid shell syntax.
- `bash scripts/ci/check-repo-integrity.sh` — reports only **pre-existing drift** unrelated to this task (`docs/archive/cursor-rules-retired/*` missing from the start of the session; see git status `D .cursor/rules/99-migration-mode.mdc`).

### Phase 3 — validation (pending live run)

- Validation transcript: the chat in which the 10-step run executes cleanly without manual intervention (TBD after operator runs it).
