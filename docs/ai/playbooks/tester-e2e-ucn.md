# Playbook: Tester E2E — `_TEST_CUSTOMER` harness (eight steps)

Canonical **eight-step** end-to-end validation for the `_TEST_CUSTOMER` fixture customer. **Cursor subagent:** [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) (invoke **`/tester`**). **Quality + diff + task rules:** same file (**E2E tester doctrine** §1–§13). **Harness history:** [`TASK-052`](../../tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md). This playbook is the **single source of truth for step order**; **`.cursor/agents/tester.md`** is the SSoT for **what “good” means** after each write.

**Contract:**

- `_TEST_CUSTOMER` is test data. Approval pauses for customer-data write tools are bypassed under the `_TEST_CUSTOMER` E2E override (see `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`).
- On the reserved triggers (see below), the agent **must execute all eight steps in a single session, in order, without stopping** for confirmation or substituting session context for the actual playbook work. Any skipped step, reordering, or shortcut is a defect — stop, fix the script / playbook / rule, and re-run.
- For **live troubleshooting** (first UCN vs GDoc, pause, diff, then optional **prep-v2** / second UCN and lifecycle + metadata), use [`tester-e2e-ucn-debug.md`](tester-e2e-ucn-debug.md) — a **staged agent playbook** with handoff, not a lint script.
- **GDoc and artifact** nuance (wording, hygiene, cross-section truth) is reviewed by the **agent + operator** using that playbook (or the checklist below) — there is no substitute for `read_doc` and transcript `call_record` side-by-sides.
- If a step fails, stop, fix, and **resume from that step** — do not restart from step 1 unless the failure corrupted state.
- **Artifact hygiene:** customer-facing artifacts produced by this flow (GDoc sections, History Ledger, `challenge-lifecycle.json`, Account Summary, call records) must be indistinguishable from a real-customer run. See **`.cursor/rules/11-e2e-test-customer-trigger.mdc` — Artifact hygiene**.
- **Call-records / sync order:** After **Extract Call Records** (steps 3 or 6) creates or updates `call-records/*.json`, run **`./scripts/e2e-test-push-gdrive-notes.sh _TEST_CUSTOMER`** (push local changes to Drive) **before** any **`sync_notes`** pull or other pull that mirrors from Drive — otherwise `rsync` delete-on-receive can remove JSON that exists only in the repo until it is pushed.

## Prerequisites (one-time per machine)

- **MCP servers enabled in Cursor (fail-fast before the harness):** Chat steps **2–4** and **6–8** require the **prestonotes** MCP server; Wiz product-doc adjacency expects **wiz-remote** (see **`.cursor/mcp.json`** keys). The **`/tester`** agent runs **read-only smokes** in **Session init** (`.cursor/agents/tester.md`) — **`check_google_auth`** on **prestonotes** and **`wiz_docs_knowledge_base`** on **wiz-remote** — and returns **`blocked`** if either is down, so you do not get a shell-only “green” with MCP missing.
- **`.cursor/mcp.env`** exists (from **`.cursor/mcp.env.example`**) with **`MYNOTES_ROOT_FOLDER_ID`** (for **`discover_doc`**) and **`GCLOUD_AUTH_LOGIN_COMMAND`** (your copy/paste **`gcloud auth login --account=... --enable-gdrive-access --force`**). After editing **`mcp.env`**, run **`source ./setEnv.sh`** in the terminal (or rely on Cursor loading **`mcp.env`** for MCP). To print the saved re-auth line without opening the file: **`./setEnv.sh --print-gdrive-auth`** (run as a command; not `source`).
- **`gcloud`** must be authenticated for Drive API when step 1 runs **`prep-v1`** without **`--skip-rebaseline`** (same account / flags as **`GCLOUD_AUTH_LOGIN_COMMAND`**).
- Google Drive for Desktop must be running and mounted at **`$GDRIVE_BASE_PATH`** (default `~/Google Drive/My Drive/MyNotes`).
- Repo has been bootstrapped (`./setEnv.sh --bootstrap`) and Python deps are available (`uv`).
- **Folder and first Notes doc on Drive:** `Customers/_TEST_CUSTOMER/` must exist with a `_TEST_CUSTOMER Notes` Google Doc. If it does not, run **one** `Bootstrap Customer for _TEST_CUSTOMER` (MCP `bootstrap_customer`) **before** step 1. You only need a full **nuclear** `reset` + bootstrap when you want to delete the entire customer tree (rare).

## Full automation (no prompts)

Use the trigger **Run E2E Test Customer** (or the phrases in `.cursor/rules/11-e2e-test-customer-trigger.mdc`). The agent runs shell steps **1** and **5** and the chat playbooks **2–4** and **6–8** in order with the `_TEST_CUSTOMER` approval bypass so there are **no** write-approval stops for that customer.

## Debugger mode (one step at a time)

1. Run **`./scripts/e2e-test-customer.sh list-steps`** for the eight steps only, or **`./scripts/e2e-test-customer.sh list-catalog`** (alias **`list-all`**) for **triggers, eight steps, and `e2e_workflow` modes** (same text: **`scripts/lib/e2e-catalog.txt`**).
2. **Shell steps** (1 and 5 only):  
   `./scripts/e2e-test-customer.sh run-step 1`  
   `./scripts/e2e-test-customer.sh run-step 1 --skip-rebaseline`  
   `./scripts/e2e-test-customer.sh run-step 5`  
   (Or invoke `./scripts/e2e-test-customer.sh prep-v1` with the same flags directly.)
3. **Chat steps** (2–4, 6–8): `run-step <n>` prints the exact chat trigger; paste that into a new agent message, fix issues, repeat the **same** step until it succeeds, then move on.
4. To re-run only the first shell block with a faster path: **`./scripts/e2e-test-customer.sh prep-v1 --skip-rebaseline`** (skips GDoc file replace; use when you are debugging fixtures only).

### Optional: debug bundle (TASK-068)

Set **`PRESTONOTES_E2E_DEBUG=1`** before shell harness commands to emit a debug bundle under `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/e2e-debug/<ISO-datetime>/`. The shell helper seeds:

- `harness-steps-1-8.checklist.md`
- `ucn-steps-1-11.checklist.md`
- `mutations.json`
- `read-doc-pointers.json`
- `ledger-attempt.json`

Use **`./scripts/e2e-test-customer.sh debug-path`** to print the active bundle path. Default is off.

## The eight steps

### 1. Shell: `prep-v1` (GDoc from template + local seed + push)

```bash
./scripts/e2e-test-customer.sh prep-v1
```

Replaces the Notes Google Doc in Drive with a **full copy** of `_TEMPLATE/_notes-template` (Drive API; see `prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py`), pulls the mount into the repo, **removes** `pnotes_agent_log.md` / archive and **clears** `AI_Insights/` for a greenfield, materializes **v1 Transcripts** from `tests/fixtures/e2e/_TEST_CUSTOMER/v1/` (clears `call-records/*.json` but does **not** copy JSON from git — run **Extract** in step 3), runs `e2e-test-customer-bump-dates.py`, and pushes to Drive.

Options: `prep-v1 --skip-rebaseline` (no GDoc replace), `prep-v1 --skip-clean` (keep logs and `AI_Insights`).

**Legacy (no GDoc replace, no clean):** `./scripts/e2e-test-customer.sh v1`

**Parity with `e2e-test-customer.sh` (TASK-052 Section 0):** Step 1 is implemented in `cmd_prep_v1` in this order: (1) unless `--skip-rebaseline`, run `e2e_rebaseline_customer_gdoc.py` (Drive **copy** of the template Notes doc into the customer folder, then trash/rename — the Notes **file id may change**; bookmarks to the old URL need updating. This is unlike `Transcripts/` / `call-records/` / `AI_Insights/`, which sync through the Drive mount + rsync); (2) `ensure_bootstrapped` (restart Drive if mount missing, then `rsync-gdrive-notes.sh` pull); (3) unless `--skip-clean`, remove logs and clear `AI_Insights/*`; (4) `e2e-test-customer-materialize.py apply` (v1), `e2e-test-customer-bump-dates.py`, `e2e-test-push-gdrive-notes.sh`. Do not hand-roll a different order in docs or chat.

### 2. Chat: `Load Customer Context for _TEST_CUSTOMER`

### 3. Chat: `Extract Call Records for _TEST_CUSTOMER`

After a successful extract, the gate **`uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER`** must exit 0 before UCN (step 4).

### 4. Chat: `Update Customer Notes for _TEST_CUSTOMER`

First UCN. Persists `challenge-lifecycle.json`, updates the GDoc, appends History Ledger, etc. Run [`update-customer-notes.md`](update-customer-notes.md) end-to-end (especially Step 6 **Upsell Path** routing for **`Wiz DSPM`** / **`Wiz CIEM`** vs a single generic **`Wiz Cloud`** line, and **Contacts** built in Step 8 from transcripts + `call-records` per that playbook — no `/tmp` mutation files, no fixture-only mutation scripts) so the mutation plan is **playbook-LLM-driven** the same way it must be for real customers. For `_TEST_CUSTOMER` E2E, Step 7 clarification and Step 9 approval are logged as bypass outcomes (no user pause) per `.cursor/rules/11-e2e-test-customer-trigger.mdc`; for non-E2E customers, normal pauses remain required.

### 5. Shell: `prep-v2` (push, merge expansion transcripts, push)

```bash
./scripts/e2e-test-customer.sh prep-v2
```

**Pushes the repo to Drive first** (so round-1 UCN and call-records are on Drive before pull), pulls, materializes v1 + v2 **transcripts** only (does **not** delete existing `call-records/*.json` from round 1), bumps dates, pushes again. No new call-record JSON is added here; those come from step 6.

**Parity with the script (TASK-052 Section B):** `cmd_prep_v2` always runs `e2e-test-push-gdrive-notes.sh` **before** `ensure_bootstrapped` (which pulls from Drive). The script also requires existing `call-records/*.json` (round-1 extract completed); if missing, `prep-v2` exits with an error.

**Alias:** `./scripts/e2e-test-customer.sh v2` (same as `prep-v2`).

### 6. Chat: `Extract Call Records for _TEST_CUSTOMER`

Second extraction. Produces new JSON in `call-records/` for the two v2 expansion transcripts. Run **`call_records lint`** before step 7.

### 7. Chat: `Update Customer Notes for _TEST_CUSTOMER`

Second UCN. Same playbook contract as step 4 (Step 6 coverage table → Step 8 mutations, including distinct upsell lead-ins when transcripts support them). Use the same E2E bypass logging (`clarification_gate: none`, `approval: bypassed per 11-e2e`) while keeping production behavior unchanged.

### 8. Chat: `Run Account Summary for _TEST_CUSTOMER`

Read-only final summary; must not mention the E2E flow in customer-facing text.

## Post-UCN diff (tester **§6** — TASK-069)

After each **`read_doc`** that closes a UCN round, the **`/tester`** agent (or orchestrator) must run **`.cursor/agents/tester.md` §6** *before* calling the run successful for **`v1_full`** / **`full`**.

- **Not the same as the writer’s planner guard:** the code only requires coverage for four fields (`top_goal`, `risk`, `use_cases`, `workflows`). The **tester** must still diff **Contacts**, **Challenge Tracker**, **Cloud Environment**, and **Account Metadata** against transcripts + `call-records`, and **score** empty sections when the corpus is rich (see §6 “mandatory rows”).
- **Daily Activity (TASK-071):** compare **transcript count in lookback (N)** to **meeting-block count in DAL (M)** — not `len(free_text.entries)`; see **tester.md §6.1**.
- **Pointer only** — full table template, severity rules, and anti-false-green language live in **tester.md §6** (do not duplicate here).

## Maintaining the E2E harness

When you add or rename a user-visible E2E trigger phrase, harness step, or `e2e_workflow` mode:

1. Update `scripts/lib/e2e-catalog.txt` first (header + catalog body are the operator SSoT).
2. Run `./scripts/e2e-test-customer.sh list-catalog` and verify wording/modes are correct.
3. Sync references in `.cursor/rules/11-e2e-test-customer-trigger.mdc` (triggers/order) and `.cursor/agents/tester.md` (§4 modes and execution contract).
4. Keep this playbook focused on step procedure; do not duplicate long policy prose from `tester.md`.

## Optional: nuclear reset (not part of the default eight)

Use only when the Drive folder is corrupt or you need a true greenfield tree:

```bash
./scripts/e2e-test-customer.sh reset
```

Then: **Bootstrap Customer for _TEST_CUSTOMER**, then **`./scripts/e2e-test-customer.sh prep-v1`** (or `prep-v1 --skip-rebaseline` if the GDoc was just created by bootstrap and already matches the template).

## Manual verification checklist (after step 8)

If you are **debugging UCN vs GDoc** rather than a clean linear run, use [`tester-e2e-ucn-debug.md`](tester-e2e-ucn-debug.md). Otherwise, review:

- `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/` contains:
    - `challenge-lifecycle.json` with the expected state transitions across both seeds.
    - `_TEST_CUSTOMER-History-Ledger.md` with two UCN rows.
    - `_TEST_CUSTOMER-AI-AcctSummary.md` if the operator saved the Account Summary manually.
- `call-records/*.json` has **8 files** total (6 from the initial seed + 2 extracted after the expansion seed).
- `_TEST_CUSTOMER Notes` on Drive shows:
    - Challenge Tracker with lifecycle-linked anchors.
    - Deal Stage Tracker advanced for Cloud / Sensor entries.
    - Daily Activity with recap coverage for every transcript date.
- The Account Summary chat output (step 8) contains **no** references to `TASK-NNN`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, or `fixture`.
- [ ] Every populated `append_with_history` entry has a non-null `timestamp`.
- [ ] Challenge Tracker row `status` matches `challenge-lifecycle.json` `current_state` for every row referencing a lifecycle id.
- [ ] `appendix.agent_run_log` has exactly 2 new entries (one per UCN round) after the E2E completes.

## Triggers reserved by `.cursor/rules/11-e2e-test-customer-trigger.mdc`

- `Run E2E Test Customer`
- `run e2e test customer`
- `E2E Test Customer _TEST_CUSTOMER`

On any of these, the agent executes the eight steps above **without pause** (for `_TEST_CUSTOMER` only).
