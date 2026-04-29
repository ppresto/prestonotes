# Playbook: Tester E2E — UCN vs GDoc debug (staged, two phases)

**Purpose:** A **live Cursor session** with an agent that runs the `_TEST_CUSTOMER` pipeline **in stages**, **pauses for your approval** between stages, and **investigates gaps** between what the transcripts and call records contain vs what landed in **`_TEST_CUSTOMER Notes`** (Google Doc) and in on-disk artifacts. This is **not** a lint script; the agent uses MCP, `gcloud`/Drive API as needed, file reads, tests, and code tracing.

**When to use:** You see missing sections, wrong challenge rows, empty DAL lines, or metadata drift after UCN. You want a **partner** that diffs **ground truth → pipeline → GDoc**, then narrows **which layer** dropped or altered data.

**Canonical background flow** (unchanged): [`tester-e2e-ucn.md`](tester-e2e-ucn.md) and [`scripts/lib/e2e-catalog.txt`](../../scripts/lib/e2e-catalog.txt) (harness SSoT). **Cursor subagent** for this style of run: [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) (invoke **`/tester`**) — read the agent file for playbooks vs rules. This playbook **replaces** any ad-hoc “validation script only” workflow; it **supplements** the default E2E with **explicit pause and diff** semantics.

**Contract:**

- `_TEST_CUSTOMER` only; follow E2E approval bypass rules in **`.cursor/rules/11-e2e-test-customer-trigger.mdc`**, **20-orchestrator**, **21-extractor**, **core**.
- **Do not** treat a green `call_records lint` as proof the GDoc is complete; lint is one gate among many.
- **State discipline:** Prefer **no long-lived file edits** while isolating a bug (use env vars, one-off flags, or a throwaway branch). If you **do** change contracts, schemas, or prompts, **revert or branch-merge** before the final summary, or document each change explicitly in the session recap.
- **Operator approval:** Phase 2 starts only after the operator says to continue (see **Handoff** below).

---

## Session setup (agent + operator)

1. `source ./setEnv.sh` (or equivalent) so `PRESTONOTES_REPO_ROOT`, `GDRIVE_BASE_PATH`, and `MYNOTES_ROOT_FOLDER_ID` match **`.cursor/mcp.env`**.
2. Confirm `gcloud` Drive access: MCP **`check_google_auth`** if available, or `gcloud auth print-access-token` in terminal.
3. Open this playbook in the same Cursor chat you use for the run (so the model can follow it step-by-step).

**Repo and Drive:** use **[`extract-call-records.md`](extract-call-records.md)** — **Step 1 of 9 — Optional sync (canonical Drive and repo ordering)** — for pull vs push ordering (canonical for all Extract runs; do not duplicate that content here).

**Ground truth sources the agent should use in diffs**

| Source | What it is |
|--------|------------|
| **Transcripts** | `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/*.txt` (after prep/materialize) — *what was said*. |
| **Call records** | `MyNotes/Customers/_TEST_CUSTOMER/call-records/*.json` — *what Extract produced*. |
| **Lifecycle file** | `.../AI_Insights/challenge-lifecycle.json` — *structured challenge state* (when present). |
| **GDoc** | **`*_TEST_CUSTOMER Notes*`** in Drive — *what UCN wrote* (read via API/MCP, not only local `.md` export if the export is stale). |
| **History Ledger** | `.../AI_Insights/*-History-Ledger.md` — *append history for UCN runs* (when present). |

**MCP tools the agent will typically use** (names may evolve — confirm in `prestonotes_mcp/server.py` if a call fails)

- `discover_doc` → resolve the Notes **document id** for `_TEST_CUSTOMER` using `MYNOTES_ROOT_FOLDER_ID`.
- `read_doc` → fetch GDoc **content** (and internal markers if needed for debugging).
- `read_transcripts`, `read_call_records`, `read_challenge_lifecycle`, `read_ledger` / `read_audit_log` as needed for **side-by-side** comparison with the GDoc.

**Terminal the agent may use**

- `uv run pytest` with a **targeted** path (e.g. `prestonotes_mcp/tests/...`, `prestonotes_gdoc/...`) after identifying a suspect module.
- `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` when testing extract/JSON validity.
- **Auth working?** `gcloud auth print-access-token` then (with `MYNOTES_ROOT_FOLDER_ID` from **`.cursor/mcp.env`**):  
  `uv run python prestonotes_gdoc/update-gdoc-customer-notes.py discover --customer _TEST_CUSTOMER --root-folder-id "$MYNOTES_ROOT_FOLDER_ID"`  
  and **`read`** with `--doc-id <id>` and `--config prestonotes_gdoc/config/doc-schema.yaml` so the live GDoc matches what **`read_doc`** returns in MCP.
- **UCN is not a one-liner:** `update-gdoc-customer-notes.py write` requires a **valid mutations JSON** from the UCN planner; an empty plan can fail **planner coverage** (required sections need a mutating action or `no_evidence`). Run the [**`update-customer-notes.md`**](update-customer-notes.md) flow in chat (or MCP **`write_doc`**) for a real first UCN — do not expect a shell-only substitute.
- `rg` / codebase search in **`update-gdoc-customer-notes.py`**, **`call_records.py`**, planner/reconciler code paths **after** a gap is named (not before).

---

## Phase A — First UCN (`prep-v1` → context → extract → UCN) then **pause and diff**

**Goal:** Establish what the **first** UCN run wrote vs what **should** have been representable from v1 transcripts + call records.

### A1. Run the pipeline to first UCN (stop before `prep-v2`)

Execute **in order**, in this session (same triggers as the main E2E playbook’s steps **1–4**):

1. **Shell** — `./scripts/e2e-test-customer.sh prep-v1` (or `prep-v1 --skip-rebaseline` / `prep-v1 --skip-clean` if you are only debugging fixtures; say so in the recap).
2. **Chat** — *Load Customer Context for _TEST_CUSTOMER* (per [`load-customer-context.md`](load-customer-context.md) or project convention).
3. **Chat** — *Extract Call Records for _TEST_CUSTOMER* (per [`extract-call-records.md`](extract-call-records.md)). Do not proceed to UCN until **lint** is acceptable for your investigation (`uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` exits 0 unless you are explicitly debugging a bad extract).
4. **Chat** — *Update Customer Notes for _TEST_CUSTOMER* (first UCN; per [`update-customer-notes.md`](update-customer-notes.md)).

**🛑 CHECKPOINT A — stop for analysis**

- Do **not** run `prep-v2` until Phase B is **explicitly** started by the operator (see **Handoff**).

### A2. Build the diff (ground truth vs GDoc)

1. **Read transcripts** (paths above). Summarize *per call* the facts that *should* affect GDoc sections (stakeholders, products, challenges, deal motion — whatever the project’s UCN contract says).
2. **Read `call-records/*.json`**. For each file, note fields that must flow to **Daily Activity**, **Challenge Tracker**, **Risk**, **Account metadata**, etc. Flag **empty** or **stub** fields that could explain a miss.
3. **Fetch the GDoc** with `discover_doc` + `read_doc` (or equivalent Drive read). If local ` ... Notes.md` is used as a *mirror*, state whether rsync was run and whether the file might lag the live doc.
4. **Produce a structured gap list:** *Expected (from 1–2)* | *Observed in GDoc (3)* | *First hypothesis (which subsystem)*. Subsystems might include: **extractor**, **UCN planner**, **GDoc section writer**, **reconciler**, **approval/tool filter**, **schema validation dropping fields**.

### A3. Root-cause pass (iterate until narrow)

1. For each **gap row**, work **backward** along the data path: **Transcript line → call-record field → UCN input bundle → GDoc write**. Cite **file:region** or **function** when you have a line.
2. **Run tests** targeted at the suspected area (`pytest` on `prestonotes_mcp`, `prestonotes_gdoc`, or parity tests such as `test_challenge_lifecycle_parity` if the gap is challenge-related).
3. If you need **temporary** changes (schema, prompt, feature flag), either: use a **throwaway branch** or a **revert** plan at the end of the session. **Do not** leave experimental prompts in `main` without operator agreement.
4. If the fix is **re-run UCN** with the *same* inputs to confirm idempotence or fill-in, say so; operator may re-invoke the UCN chat step only.

### A4. Phase A closeout

Deliver in the thread:

- **What matched** (short).
- **What was missing or wrong** (table).
- **Root cause** (one paragraph) or **open branches** (if still ambiguous).
- **Files touched** (or “none” if read-only).
- **Recommendation** (fix in code vs data vs runbook vs prompt).
- If anything remains **fuzzy**, list **one** next experiment.

---

## Handoff — operator approval for Phase B

**Do not** start Phase B until the operator sends a **clear** go-ahead, e.g.:

> *Approved. Continue to Phase B (prep-v2, second extract, second UCN, lifecycle + metadata check).*

If the operator is still iterating on Phase A, stay in A3/A4.

---

## Phase B — `prep-v2` → second extract → second UCN, then **diff + lifecycle + metadata**

**Goal:** Same as Phase A, plus **v2** transcript merge behavior, and **regression** checks on **Challenge Tracker** / **challenge lifecycle** / **account metadata** (where your templates define them).

### B1. Run the next segment of the E2E chain

1. **Shell** — `./scripts/e2e-test-customer.sh prep-v2` (fails if round-1 `call-records` are missing — that means Phase A did not complete extract/UCN as required).
2. **Chat** — *Extract Call Records for _TEST_CUSTOMER* (second time).
3. **Lint** — `call_records lint` before UCN if the playbook requires it.
4. **Chat** — *Update Customer Notes for _TEST_CUSTOMER* (second UCN).

**Optional (after UCN, before deep diff):** *Run Account Summary for [CustomerName]* (see `run-account-summary.md`) is **outside** the E2E harness; include it here **only** if the operator asked for that pass; otherwise Phase B can end after the second UCN for troubleshooting scope.

### B2. Extended diff (same as A2, plus lifecycle and metadata)

Repeat **A2** with the **updated** transcripts/call records and the **new** GDoc read.

**Additionally:**

- **`read_challenge_lifecycle`** vs **Challenge Tracker** table in the GDoc (row ids, `current_state` vs row **status** text, dates). Use **`prestonotes_gdoc/challenge_lifecycle_parity.py`** / `test_challenge_lifecycle_parity` concepts if a parity check is relevant to the gap.
- **Account metadata** section (or your doc’s **Exec Summary / account snapshot**): compare **stakeholder** and **motion** fields against call records + ledger *as designed in* [`update-customer-notes.md`](update-customer-notes.md) and [`gdoc-section-changes-v2.md`](../references/gdoc-section-changes-v2.md) (adjust filename if the reference moved).
- **History Ledger** — if two UCN rounds ran, expect **two** UCN appends (see main E2E manual checklist) unless a task explicitly said otherwise.

### B3. Root-cause and tests (same pattern as A3)

Focus on **deltas** introduced by **v2** (new transcripts, merge policy, not wiping round-1 JSON). Use **`e2e-test-customer`** script comments and `e2e-test-customer-materialize` behavior if “why did v2 drop X?” is the question.

### B4. Phase B closeout

Same deliverable as **A4**, with emphasis on **cross-run consistency** (round 1 vs 2) and **lifecycle**/**metadata** if those were the failing area.

---

## Triggers the operator can paste to start or resume

Use a **dedicated** chat (recommended) or continue the same one:

- *Run Phase A only: E2E troubleshoot first UCN GDoc (prep-v1 through first UCN, then pause and diff) per `tester-e2e-ucn-debug.md`*
- *Phase B: continue E2E troubleshoot — prep-v2, second extract, second UCN, lifecycle and metadata diff per `tester-e2e-ucn-debug.md`*

The agent should **open this file** and follow it **in order** unless the operator narrows scope (e.g. “Phase A3 only, skip GDoc read, focus on `call-records`”).

---

## What this playbook is not

- **Not** a replacement for the **full** unattended E2E run in [`tester-e2e-ucn.md`](tester-e2e-ucn.md) / the catalog when you need **end-to-end coverage with no pauses** (e.g. regression guard).
- **Not** a guarantee the model will catch every GDoc edge case; it is a **procedure** so the **same** investigation can be repeated.
- **Not** permission to skip **`gcloud`**/Drive requirements or leave secrets in the repo; follow **`.cursor/mcp.env`** and **`README.md`** setup.

---

## See also

- [`tester-e2e-ucn.md`](tester-e2e-ucn.md) — procedure, `list-steps` / catalog, reset.
- [`update-customer-notes.md`](update-customer-notes.md) — UCN tool order and gdoc id discovery.
- [`extract-call-records.md`](extract-call-records.md) — extract and lint.
- [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](../../.cursor/rules/11-e2e-test-customer-trigger.mdc) — triggers and artifact hygiene.
- `docs/ai/prompts/e2e-task-execution-prompt.md` — long-form execution prompt if you need a **single paste** in addition to this playbook.
