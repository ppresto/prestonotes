# prestonotes_gdoc

**Google Docs / Drive execution layer** for PrestoNotes v2.

## What belongs here (runtime)

| Item | Role |
|------|------|
| **`update-gdoc-customer-notes.py`** | Docs/Drive API client: discover, read, write, ledger-append subcommands. |
| **`000-bootstrap-gdoc-customer-notes.py`** | Bootstrap customer folders + Notes doc (used when MCP write tools land). |
| **`config/`** | `doc-schema.yaml`, `section-sequence.yaml`, `task-budgets.yaml`, `sections/*.yaml`, prompts consumed by MCP resources and the client. |
| **`config/tools.json`** | **Minimal stub** — v1 had a richer tool registry; v2 names tools in MCP + playbooks directly. **Stage 3** orchestration may expand this file. |

## What we intentionally do **not** ship in v2

- **`run-main-task.py`** and Python **`sections/*_section.py`** — v1 “pipeline” builders; v2 uses **agent-produced mutation JSON** + **`write_doc`** (see [`docs/ai/references/gdoc-section-changes-v2.md`](../docs/ai/references/gdoc-section-changes-v2.md)). History: `../prestoNotes.orig/custom-notes-agent/`.
- **Committed scratch under `tmp/`** — gitignored; do not store run artifacts here.

## Human / playbook docs

- **Granola meeting summary templates:** [`docs/ai/references/granola-meeting-summary-templates.md`](../docs/ai/references/granola-meeting-summary-templates.md) (legacy reference; revise for v2 as needed).

For porting from v1, see **`docs/project_spec.md`** **§8** (legacy → v2 table).

## Full E2E `_TEST_CUSTOMER` flow (runbook + scripts)

Canonical procedure for the full harness is:
- Agent SSoT: [`.cursor/agents/tester.md`](../.cursor/agents/tester.md)
- Step order SSoT: [`docs/ai/playbooks/tester-e2e-ucn.md`](../docs/ai/playbooks/tester-e2e-ucn.md)

Use this section as the execution map for scripts and CLI calls that touch this package.

### 0) Session prerequisites (must pass first)

1. `source ./setEnv.sh`
2. MCP auth/smoke in order:
   - `check_google_auth` (prestonotes MCP)
   - `wiz_docs_knowledge_base` (wiz-remote MCP)
3. Drive mount/access healthy (`GDRIVE_BASE_PATH` available)

If any prerequisite fails, stop and recover auth/mount before running E2E steps.

### 1) Harness step map (what runs where)

From repo root:

```bash
./scripts/e2e-test-customer.sh list-catalog
./scripts/e2e-test-customer.sh list-steps
```

For `v1_full`, use `prep-v1` then **Load Customer Context** + first **Update Customer Notes** + `read_doc` / diff per `tester-e2e-ucn.md` (default harness is five catalog steps; no mandatory Extract).

### 2) Step 1 shell prep (`prep-v1`)

```bash
./scripts/e2e-test-customer.sh prep-v1
```

This orchestrates:
- GDoc rebaseline (`prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py`) unless skipped
- fixture materialization (`scripts/e2e-test-customer-materialize.py apply`)
- date bump (`scripts/e2e-test-customer-bump-dates.py`)
- repo -> Drive mirror (`scripts/e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"`)

After rebaseline, always use the newly discovered doc id (do not trust a stale id).

### 3) Chat: Load Customer Context + first Update Customer Notes (UCN)

- Follow **`docs/ai/playbooks/tester-e2e-ucn.md`** (steps 2–3). Optional: run **Extract Call Records** + `call_records lint` only when debugging extraction; not part of the default five-step harness.

**Full `e2e_default` harness:** then `./scripts/e2e-test-customer.sh prep-v2` and a second **Update Customer Notes** (catalog steps 4–5 in `tester-e2e-ucn.md`).

### 4) UCN mutation JSON → preflight → write (this package)

**UCN policy** (when to run preflight, full TASK-072 / DAL / Deal Stage matrix, Step 10 write order): **[`docs/ai/playbooks/update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md)** — do **not** treat this README as a second copy of that contract.

Create approved mutation JSON under the customer folder (not `/tmp` only), e.g. `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/ucn-approved-mutations.json`.

```bash
uv run python scripts/ucn-planner-preflight.py \
  --mutations "./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json" \
  --json-output

uv run prestonotes_gdoc/update-gdoc-customer-notes.py write \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml \
  --mutations "./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json" \
  --customer-name "[CustomerName]"
```

Optional **`write --dry-run`** / MCP **`dry_run=true`** for Doc preview: **`_TEST_CUSTOMER` E2E only**, after preflight — [`docs/ai/playbooks/tester-e2e-ucn.md`](../docs/ai/playbooks/tester-e2e-ucn.md) (**Optional writer dry-run**).

Post-write readback:

```bash
uv run prestonotes_gdoc/update-gdoc-customer-notes.py read \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml
```

### 5) Step 11 ledger + sync completion

After successful write:
- append v3 ledger row (`append_ledger_row` MCP tool)
- push customer folder back to Drive:

```bash
./scripts/e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"
```

Run is not complete until ledger outcome is reported and Drive mirror is up to date.

### 6) Required post-write quality checks

For `v1_full` / `e2e_default`:
- `read_doc` + tester §6 delta table including:
  - Exec Account Summary
  - Contacts
  - Challenge Tracker
  - Cloud Environment
  - Account Metadata
  - Daily Activity
- TASK-071 DAL rule: compare transcript count (N) vs DAL meeting blocks (M), not `free_text.entries` length.

### 7) Recommended quick command set (repo-local verification)

```bash
uv run pytest scripts/tests/test_ucn_planner_preflight.py
bash scripts/ci/check-repo-integrity.sh
```
