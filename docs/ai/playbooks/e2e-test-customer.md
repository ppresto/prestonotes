# Playbook: E2E test customer (`_TEST_CUSTOMER`)

Canonical 10-step end-to-end validation for the `_TEST_CUSTOMER` fixture customer. This playbook is the **single source of truth** for the flow.

**Contract:**

- `_TEST_CUSTOMER` is test data. Approval pauses for customer-data write tools are bypassed under the `_TEST_CUSTOMER` E2E override (see `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`).
- The agent **must execute all 10 steps in a single session, in order, without stopping** for confirmation or substituting session context for the actual playbook work. Any skipped step, reordering, or shortcut is a defect — stop, fix the script / playbook / rule, and re-run.
- There is no automated verifier. Validation is **manual artifact review** (GDoc + on-disk `AI_Insights/` + `call-records/`).
- If a step fails, stop, fix, and **resume from that step** — do not restart from step 1 unless the failure corrupted state.
- **Artifact hygiene:** customer-facing artifacts produced by this flow (GDoc sections, History Ledger, `challenge-lifecycle.json`, Account Summary, call records) must be indistinguishable from a real-customer run. See **`.cursor/rules/11-e2e-test-customer-trigger.mdc` — Artifact hygiene**.

## Prerequisites (one-time per machine)

- `gcloud auth login --account=<your-account> --enable-gdrive-access --force` must be valid.
- Google Drive for Desktop must be running and mounted at `$GDRIVE_BASE_PATH` (default `~/Google Drive/My Drive/MyNotes`).
- Repo has been bootstrapped (`./setEnv.sh --bootstrap`) and `.cursor/mcp.env` exists.

## The 10 steps

### 1. Hard reset

```bash
./scripts/e2e-test-customer.sh reset
```

Trashes the Drive `Customers/_TEST_CUSTOMER` folder via the Drive API (`PATCH /files/{id} {"trashed": true}`), deletes the local repo mirror at `MyNotes/Customers/_TEST_CUSTOMER/`, restarts Google Drive for Desktop, and polls the mount until the folder is confirmed absent. Idempotent.

### 2. Chat: `Bootstrap Customer for _TEST_CUSTOMER`

Runs the bootstrap playbook (`docs/ai/playbooks/bootstrap-customer.md`) via MCP `bootstrap_customer` with `dry_run=false`. Creates a fresh `Customers/_TEST_CUSTOMER/` folder on Drive with `AI_Insights/`, `Transcripts/`, and a `_TEST_CUSTOMER Notes.gdoc` copied from the template. Expect the approval bypass from the `_TEST_CUSTOMER` E2E override on `20-orchestrator.mdc`.

### 3. Apply the initial seed

```bash
./scripts/e2e-test-customer.sh v1
```

Pulls the bootstrap skeleton from Drive into the repo mirror, materializes `tests/fixtures/e2e/_TEST_CUSTOMER/v1/` (6 transcripts + starter call-records) into `MyNotes/Customers/_TEST_CUSTOMER/`, rolls fixture dates into the rolling 30-day window via `e2e-test-customer-bump-dates.py`, and pushes the mirror back to Drive.

### 4. Chat: `Load Customer Context for _TEST_CUSTOMER`

### 5. Chat: `Extract Call Records for _TEST_CUSTOMER`

First extraction. With the initial seed, `call-records/*.json` already exist; the extractor should detect no gaps and exit cleanly (or perform incremental repair if the corpus drifted).

### 6. Chat: `Update Customer Notes for _TEST_CUSTOMER`

First UCN. Runs Phase 0 Challenge Review → Blocks A+B in a single combined approval (auto-approved under the `_TEST_CUSTOMER` E2E override), persists `challenge-lifecycle.json`, updates the GDoc, and writes `*-History-Ledger.md`.

### 7. Merge the expansion seed

```bash
./scripts/e2e-test-customer.sh v2
```

Merges `tests/fixtures/e2e/_TEST_CUSTOMER/v2/` (commercial-expansion transcripts only — `2026-04-28-wiz-cloud-sku-purchase.txt`, `2026-05-05-wiz-sensor-pov-kickoff.txt`) on top of the initial seed, re-rolls dates, and pushes to Drive. No new call-record JSON is seeded — those come from step 8.

### 8. Chat: `Extract Call Records for _TEST_CUSTOMER`

Second extraction. Produces new JSON in `call-records/` for the two expansion-seed transcripts.

### 9. Chat: `Update Customer Notes for _TEST_CUSTOMER`

Second UCN. Expected to advance **Deal Stage Tracker** (Cloud SKU PO, Sensor POV kickoff) and update the Splunk-renewal / SOC challenges lifecycle based on the new evidence.

### 10. Chat: `Run Account Summary for _TEST_CUSTOMER`

Generates the final account-summary artifact (chat output; optional manual save per `docs/ai/playbooks/run-account-summary.md`) using the latest GDoc + lifecycle state. The summary is read-only and must not mention the E2E flow in its content.

## Manual verification checklist (after step 10)

- `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/` contains:
    - `challenge-lifecycle.json` with the expected state transitions across both seeds.
    - `_TEST_CUSTOMER-History-Ledger.md` with two UCN rows.
    - `_TEST_CUSTOMER-AI-AcctSummary.md` if the operator saved the Account Summary manually.
- `call-records/*.json` has **8 files** total (6 from the initial seed + 2 extracted after the expansion seed).
- `_TEST_CUSTOMER Notes.gdoc` on Drive shows:
    - Challenge Tracker with lifecycle-linked anchors.
    - Deal Stage Tracker advanced for Cloud / Sensor entries.
    - Daily Activity with recap coverage for every transcript date.
- The Account Summary chat output (step 10) contains **no** references to `TASK-NNN`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, or `fixture`.
- [ ] Every populated `append_with_history` entry has a non-null `timestamp`.
- [ ] Challenge Tracker row `status` matches `challenge-lifecycle.json` `current_state` for every row referencing a lifecycle id.
- [ ] `appendix.agent_run_log` has exactly 2 new entries (one per UCN round) after the E2E completes.

## Triggers reserved by `.cursor/rules/11-e2e-test-customer-trigger.mdc`

- `Run E2E Test Customer`
- `run e2e test customer`
- `E2E Test Customer _TEST_CUSTOMER`

On any of these, the agent executes the 10 steps above **without pause**.
