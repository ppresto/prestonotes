# E2E `_TEST_CUSTOMER` Guide — goals, artifacts, schemas, validation

**Audience:** the next Cursor session that picks up E2E-quality work on PrestoNotes v2.
**Purpose:** this is the canonical "where are we / what are we trying to do / why does each file look the way it does" reference. Read this first before touching the E2E harness, any write-path validator, any playbook, or the content-quality guardrails (**TASK-046**–**TASK-052** archived; active UCN/E2E quality **TASK-053** TOC + **TASK-044** on hold). **For every E2E-quality or UCN-vs-GDoc session, follow [§0.3](#03-repeatable-quality-test-loop-start-every-e2e-quality-session-here)** — do not short-circuit with hand-written mutation JSON. **Session learnings and rapid v1 testing:** [§0.5](#05-e2e-learnings--keep-improving-quality-docs-rubric-first-rapid-v1). **After any first UCN or harness write to the Notes doc, run [§0.7](#07-post-write-doc-vs-transcript-diff-full-v1-quality-gate)**.
**Last updated:** 2026-04-24 (**§0.7** added: post-write doc vs transcript diff + delta table as part of full v1. **§0.6** repeatability + multi-customer mutation discipline. **§0.5** rubric-first / rapid v1.)

**Canonical E2E task links:** [task index](tasks/INDEX.md) (active: **TASK-044** (on hold), **TASK-053**; **TASK-051** / **TASK-052** complete — [`tasks/archive/2026-04/`](tasks/archive/2026-04/)). **Ready-made LLM prompt + execution order (053 → 044):** [e2e-task-execution-prompt.md](ai/prompts/e2e-task-execution-prompt.md). Paths below are relative to the `docs/` directory.

---

## 0. Session bootstrap prompt (copy/paste into a new LLM)

```text
Read these files in order before proposing changes:
1) docs/E2E_TEST_CUSTOMER_GUIDE.md (this file, full — **especially §0.3**–**§0.7** for UCN vs GDoc quality work, mutation discipline, rapid v1 testing, and post-write diff)
2) docs/project_spec.md (especially §2 and §9)
3) docs/tasks/INDEX.md
4) Current active task linked in INDEX (E2E: **TASK-053** quality TOC; **TASK-044** on hold; **TASK-051** / **TASK-052** archived)
5) .cursor/rules/workflow.mdc
6) If executing a queued E2E task: `docs/ai/prompts/e2e-task-execution-prompt.md` (copy-paste block + order 052 → 053 → 044)
7) If touching harness or sync history: `docs/tasks/archive/2026-04/TASK-052-*.md`. If touching UCN/DAL/sync order: `docs/tasks/active/TASK-053-*.md`.
8) If debugging Challenge Tracker vs lifecycle vs extract: read **§10–§11** in this file (phased flow + drift task template).

Operating contract:
- `_TEST_CUSTOMER` is a test loop, not special behavior.
- Do not encode fixture-specific logic, thresholds, or required IDs into runtime code.
- Improve general UCN intelligence so it works across all customers and supports no-op updates when no material changes exist.
- **Follow `docs/E2E_TEST_CUSTOMER_GUIDE.md` §0.3** for quality testing: full E2E through first UCN → read inputs → diff vs `read_doc` → tasks → one fix at a time → re-run UCN from **playbook-generated** mutations → API validate.
- **Follow §0.6** for mutation ownership: **repeatability** (next UCN run must be able to recreate the plan from playbooks + rules) and **multi-customer** (no fixture-shaped shortcuts).
- **Do not** patch the live GDoc using ad-hoc `tmp/*.json` mutation files as a substitute for fixing playbooks / `docs/ai/gdoc-customer-notes/` mutation packs / code — that is misleading, single-run, and not reproducible for other customers.
- Keep one active task at a time; keep queued tasks ordered in INDEX.
- When a task is complete and verified, move it to docs/tasks/archive/YYYY-MM/ and update INDEX in the same change.
- Stop and ask before committing.

Execution process:
1) Implement only the current active task scope.
2) Run verification commands listed in the task file.
3) Summarize what changed, what passed, what remains.
4) Ask for approval to archive the task and activate the next queued task.
```

---

## 0.1 Current direction (do not regress)

- `_TEST_CUSTOMER` is used to exercise the same pipeline a real customer run uses.
- The goal is not fixture-specific optimizations; the goal is robust generic behavior across heterogeneous customer data.
- UCN quality improvements must support both:
  - dense updates when real deltas exist, and
  - explicit no-op updates when nothing materially changed.
- Artifact consistency over time matters more than one-off single-run output: call-records, lifecycle, ledger, and GDoc must remain mutually coherent.

---

## 0.2 How scripts, MCP tools, and playbooks fit together

| Layer | What it is | Role in E2E |
| --- | --- | --- |
| **Shell** | `scripts/e2e-test-customer.sh` (`prep-v1`, `prep-v2`, `list-steps`, `run-step`, optional `reset`); `e2e-test-customer-materialize.py`; `e2e-test-customer-bump-dates.py`; `e2e-test-push-gdrive-notes.sh`; `rsync-gdrive-notes.sh`; `restart-google-drive.sh` | Seeded **v1** then **v2** transcripts, date bumps, **push-before-pull** ordering, and optional GDoc **rebaseline** (see [playbook](ai/playbooks/e2e-test-customer.md)). Drives the on-disk tree MCP tools read. |
| **MCP (prestonotes_mcp)** | `bootstrap_customer`, `sync_notes`, `discover_doc` / `read_doc` / `write_doc`, `write_call_record`, `update_challenge_state`, `append_ledger` / `append_ledger_row`, `log_run` | **Writes** are validated at the tool boundary (schemas, forbidden vocab, ledger/lifecycle rules). UCN, Extract, and Run Account Summary map to these calls; [playbooks](ai/playbooks/) are the human-readable **contracts** for the same. |
| **Playbooks** | [e2e-test-customer.md](ai/playbooks/e2e-test-customer.md) (8 steps), [e2e-troubleshoot-ucn-gdoc.md](ai/playbooks/e2e-troubleshoot-ucn-gdoc.md) (staged UCN vs GDoc diffs + handoff), [extract-call-records.md](ai/playbooks/extract-call-records.md), [update-customer-notes.md](ai/playbooks/update-customer-notes.md), [run-account-summary.md](ai/playbooks/run-account-summary.md), [bootstrap-customer.md](ai/playbooks/bootstrap-customer.md) | **Order**, **gates** (e.g. `call_records lint` before UCN), and **approval** rules. [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](../.cursor/rules/11-e2e-test-customer-trigger.mdc) wires the “Run E2E Test Customer” trigger. |
| **This guide + [INDEX](tasks/INDEX.md)** | E2E vision, artifact inventory, validation layers | **Why** we built each guardrail; [active tasks](tasks/INDEX.md) add **per-task** pros/cons and **isolated test** steps. |

**Mental model:** *Transcripts (disk) → call-records (MCP) → UCN / Account Summary (MCP + GDoc) → lifecycle + ledger + GDoc* — see [§4](#4-how-the-write-paths-connect-mental-model). **Pull** (`sync_notes` / rsync) **imports** from Google Drive; it does not **save** un-pushed local work (see [TASK-053](tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) push-first discipline).

**Vision (one paragraph):** deliver a **Google Doc** (Account Summary, DAL, Metadata) and **AI Account Summary** markdown, both **evidence-grounded** and **regression-safe**. `_TEST_CUSTOMER` is a **known eight-transcript corpus** exercising the **same** pipeline as production so we improve **generic** UCN, extraction, and Account Summary without baking fixture expectations into runtime code (see [§0.1](#01-current-direction-do-not-regress) and [§1](#1-what-we-are-actually-trying-to-do)). **Call-record schema v2** shipped under **TASK-051** (archived); **default harness** (`prep-v1` / `prep-v2`, push-before-pull) under **TASK-052** (archived). Active E2E quality: **TASK-053** (**TOC** for **T053-A–G** + **§T053-G**). **TASK-044** (single entry point, on hold).

Human + LLM **quality-test loop** (when debugging UCN vs GDoc, not just ticking the eight steps): [§0.3](#03-repeatable-quality-test-loop-start-every-e2e-quality-session-here).

---

## 0.3 Repeatable quality-test loop (start every E2E-quality session here)

Use this section **whenever** you are validating or improving how **Update Customer Notes** (and related writes) behave for `_TEST_CUSTOMER` — including “the GDoc is missing X that the transcripts clearly say.” It is the default **anti-circle** workflow: **observe → inventory → fix durable surfaces → re-run the same pipeline → validate over the API**, with the **operator in the loop** between tasks.

### Why ad-hoc `tmp/` mutation JSON is forbidden for “fixing” the GDoc

Hand-authoring `tmp/ucn_*.json` (or similar), running `update-gdoc-customer-notes.py write` once, and moving on:

- **Misleads the project** — CI, other agents, and future you assume UCN + playbooks already emit those mutations; they do not.
- **Works once** — the next `prep-v1` / clean E2E run will not recreate that file; the gap returns.
- **Is not transferable** — other customers never see your local JSON; only **git-tracked rules, playbooks, and code** are reproducible.

**Allowed:** committed fixtures under `tests/`, ephemeral debug dumps you delete before merge, or mutation JSON that the **same** UCN playbook run **generated** and you are replaying for an explicit, documented reason (rare).

**Required for a real fix:** change [`docs/ai/gdoc-customer-notes/README.md`](ai/gdoc-customer-notes/README.md) (and the relevant `mutations-*.md` tab file), [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md), `.cursor/rules/20-orchestrator.mdc` / `21-extractor.mdc`, or **code**, then **re-run UCN** so Step 6 → Step 8 produces mutations **without** hand-maintaining `tmp/`.

### Operator prerequisite: Google Drive authN

The **user** must complete whatever **Google Drive / Docs API authentication** this repo expects (tokens, `setEnv.sh`, Drive for Desktop mount, OAuth consent, etc.) so the agent or CLI can **`discover` / `read` / `write`** the Customer Notes doc. If API calls fail, stop and fix auth before claiming GDoc validation.

### Phase 1 — Baseline run (same entry path every time)

1. Confirm Drive/API access (above).
2. Run the **documented eight-step E2E** from the start through **first UCN** at minimum: [`e2e-test-customer.md`](ai/playbooks/e2e-test-customer.md) steps **1–4** (`prep-v1` → Load Customer Context → Extract Call Records → Update Customer Notes), including **`call_records lint`** before UCN.
3. The **LLM reads all UCN inputs** the playbook names: in-lookback transcripts, full Account Summary context from **`read_doc`** / Step 3, `MyNotes/…` customer notes, AI_Insights weights, audit log — see [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md) Steps 3–6 (not a skim of one section).
4. After first UCN, **validate with the API**: `read_doc` / `discover` (MCP or `prestonotes_gdoc/update-gdoc-customer-notes.py read`) so the post-write state is grounded in returned JSON, not memory.
5. Run **[§0.7](#07-post-write-doc-vs-transcript-diff-full-v1-quality-gate)** — delta table + recommendations — before treating the run as “validated.”

### Phase 2 — Diff inventory and task list (no product “patch” yet)

1. **Compare** what landed in the GDoc (and key local artifacts: lifecycle, ledger, call-records) to what the **inputs** support — section by section where gaps matter. Prefer the structured output of §0.7 as the starting inventory.
2. **Create tasks/subtasks** for **every** material gap (e.g. new rows in [`TASK-053`](tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md), or `docs/tasks/active/TASK-*.md` + [`INDEX.md`](tasks/INDEX.md) updates). One gap should not hide inside chat-only bullets.
3. **Deliver to the operator:** a **summary of diffs**, the **numbered task/subtask list**, and a **single recommendation** for **which task to tackle first** (dependency order, customer-visible severity, or unblocker for other tasks).

### Phase 3 — Per-task fix loop (collaborate; then next task)

For each task, in agreed order (skip/defer only after **explicit** operator decision):

1. **Recreate** the E2E environment the task needs (often: clean `prep-v1` + extract + first UCN; sometimes a narrower repro — state that in the task so the next run matches).
2. **Implement the durable fix** (rules, playbook, extractor, writer, MCP — **not** a throwaway `tmp/` mutation file to “paint” the doc).
3. **Re-run `Update Customer Notes`** end-to-end: Step 6 show-your-work table → Step 8 mutation plan **generated by the playbook process** → approved `write`.
4. **Re-validate via the API** (`read_doc` / checks the task defines). Cite artifact paths or JSON fields.
5. **Report in four blocks:** **Problem** | **Change** (files/rules) | **Result** (evidence-linked) | **Recommendation / next steps**.
6. **Pause for the operator:** merge, skip, or steer — then move to the **next** task and repeat Phase 3.

### Compact checklist (copy for session notes)

| Step | Done when |
| --- | --- |
| AuthN | User confirms Drive/Docs API access works |
| Baseline E2E 1→4 | `prep-v1` … first UCN complete; `read_doc` after write |
| Read inputs | Transcripts + Step 3 doc + playbook-weighted sources |
| §0.7 doc vs transcript | Delta table + severity + recommendations logged |
| Diff → tasks | Every gap has a task/subtask; operator has ordered list + “start here” |
| Fix task *n* | Durable diff merged; UCN re-run from playbook; API validates |
| Gate with operator | Explicit go / skip / defer before task *n+1* |

---

## 0.4 Reporting a fix (session output contract)

Whenever an agent **lands a change meant to fix a problem** (docs, rules, code, harness), the **first** material in the reply (before narrative, before “what we tested”) must be:

1. **Full file path(s)** — repo-root form, e.g. `docs/ai/gdoc-customer-notes/README.md` or `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md`, not “the mutation rules file”.
2. **The exact edit** — minimal excerpt: unified diff hunk, or the new/changed markdown/code block, or the precise CLI invocation if the “change” is a one-off command. Enough that another session can **reapply or review** without hunting.

Only **after** that: summary of intent, validation steps, risks, and next actions. This keeps E2E-quality work **auditable** and avoids “it works” without a reproducible paper trail.

---

## 0.5 E2E learnings — keep improving (quality docs, rubric-first, rapid v1)

This section captures **durable habits** discovered while debugging `_TEST_CUSTOMER` so future sessions (and real multi-customer work) do not regress into one-off hacks.

### Where GDoc / UCN “write quality” fixes usually live

Most playbook-level improvements that change **what** gets written (section intent, routing, dedupe, optional web backup) land in **one primary reference** plus the step playbook:

| Role | Canonical file |
| --- | --- |
| **Meaning** — Goals vs Risk vs Use Cases vs Cloud `tools_list` vs Upsell; rubrics; forbidden meta | Hub [`docs/ai/gdoc-customer-notes/README.md`](ai/gdoc-customer-notes/README.md); Account Summary tab [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) |
| **Process** — Step order, Step 6 tables, Step 8 coverage guard, DAL, Challenge Tracker discipline | [`docs/ai/playbooks/update-customer-notes.md`](ai/playbooks/update-customer-notes.md) |
| **Mechanics** — parser, mutation apply, API batching | `prestonotes_gdoc/update-gdoc-customer-notes.py` (only when behavior is wrong, not when the LLM skipped a step) |

When a session “fixes the GDoc,” **start diff review in the relevant `docs/ai/gdoc-customer-notes/mutations-*.md` pack** (see hub `README.md`), then **`update-customer-notes.md`**, then code.

### Rubric-first + optional web (scales past `_TEST_CUSTOMER`)

- **Anti-pattern:** Playbook or task text that says “if you see the exact words *Splunk* / *GitHub* then …” That **does not scale** to 20–100 customers with different stacks; it overfits the fixture corpus.
- **Preferred pattern (Option 1):** **Intent rubrics** — e.g. Cloud Environment `tools_list` routing by **what the tool does in the customer sentence** (CI/CD vs SIEM vs ticketing), documented in [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) → **Cloud Environment — `tools_list` routing**. The LLM applies judgment across arbitrary vendor names **without** a maintained SKU catalog.
- **Backup (Option 2):** If rubric leaves **two** plausible buckets or the product name is unknown, **at most one** bounded public lookup for **category disambiguation only** — see the same mutation-rules section. No sensitive strings in queries; do not invent customer facts from the web.

This is how we **use the model’s full reasoning** to build the best customer dataset while keeping evidence grounded in **transcripts + approved writes**.

### Partial writes vs “full” UCN (Challenge Tracker and friends)

Batches that only touch **Exec Account Summary**, **Cloud Environment `tools_list`**, or similar **do not** populate **Challenge Tracker** rows. Those rows require **lifecycle + tracker** work (`update_challenge_state` + `challenge_tracker` table mutations) in the same **full** UCN flow ([§10](#10-ucn-challenge-tracker-and-lifecycle-how-data-flows-and-where-it-can-drop), [TASK-053](tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) **T053-v1-UCN-05**). If the tracker is empty after narrow CLI tests, that is expected until a **complete** UCN pass.

### Rapid **full v1** test (rebuild GDoc + pipeline through first UCN)

Use this when you want to **re-greenfield the Notes doc** and validate **everything up through v1** (transcripts → call-records → first UCN) **without** `prep-v2` yet.

| Phase | Action | Notes |
| --- | --- | --- |
| **A — Rebuild `_TEST_CUSTOMER` Notes GDoc** | `./scripts/e2e-test-customer.sh prep-v1` | Full path from [`e2e-test-customer.md`](ai/playbooks/e2e-test-customer.md) step **1**: Drive **copy** of template into `Customers/_TEST_CUSTOMER/`, pull, clear `AI_Insights/` + logs, materialize **v1** transcripts, **clear** `call-records/*.json`, bump dates, push. **Doc file id may change** — always `discover` before `read`/`write`. |
| **B — Load context** | Chat: **Load Customer Context for `_TEST_CUSTOMER`** | Playbook step **2** — no writes. |
| **C — Extract** | Chat: **Extract Call Records for `_TEST_CUSTOMER`** | Step **3** — produces **six** v1 `call-records/*.json`. |
| **Gate** | `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` | Must exit **0** before UCN. |
| **D — First UCN** | Chat: **Update Customer Notes for `_TEST_CUSTOMER`** | Step **4** — full playbook (Steps 1–11 internally): lifecycle, Challenge Tracker, ledger, GDoc sections per [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md). |
| **E — Validate** | `read_doc` / `discover` + operator skim | Challenge Tracker non-empty when corpus has challenges; exec/cloud sections align with rubric; no harness vocabulary in customer text. |
| **F — Doc vs transcript diff** | LLM-led review per [§0.7](#07-post-write-doc-vs-transcript-diff-full-v1-quality-gate) | **Required** for a complete “full v1” quality pass: delta table + recommendations before closing the session or archiving a task. |

**Faster loop (no GDoc replace):** `./scripts/e2e-test-customer.sh prep-v1 --skip-rebaseline` — use when debugging **transcripts / extract / lint** only; it **does not** prove template → customer Notes copy behavior.

**Name:** call the table above (phases **A–F**) the **“full v1 test”** for **quality** (includes the doc-vs-transcript diff in phase **F**). That lines up with E2E playbook steps **1–4** before `prep-v2`. The **full eight-step E2E** is still [§2](#2-the-canonical-eight-step-e2e-flow-task-052--archived-harness-spec) (adds `prep-v2`, second extract, second UCN, Account Summary).

### Meta: acting as an E2E expert tester

- Prefer **harness + playbooks** over improvised shell order ([§0.2](#02-how-scripts-mcp-tools-and-playbooks-fit-together)).
- After any fix, use [§0.4](#04-reporting-a-fix-session-output-contract) (path + diff first) and [§0.3](#03-repeatable-quality-test-loop-start-every-e2e-quality-session-here) (baseline → diff → tasks → one durable fix → re-UCN → API validate).
- Treat `_TEST_CUSTOMER` as **example density**, not **special-case wording** in rules ([§10.1](#101-non-negotiable-product-rule-read-first)).

---

## 0.6 Core product principles — repeatability and multi-customer UCN

These two principles override convenience shortcuts (including anything that “fixes the GDoc” once but does not teach the **next** UCN run how to behave).

### Principle 1 — Repeatable means “the playbook run owns the mutations”

**Repeatable** does **not** mean “the same bytes every time.” It means: another operator (or agent) can run **`Update Customer Notes`** for the same customer **following the same playbooks and rules**, and the **same classes of sections** get populated from **current** transcripts + `read_doc` + call-records, without depending on a previous session’s private files.

| Allowed | Not allowed as a substitute for a durable fix |
| --- | --- |
| Mutations emitted **inside** [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md) Step 6 → Step 8, then saved under `MyNotes/Customers/<Name>/AI_Insights/` (e.g. `ucn-approved-mutations.json`) for audit / replay | One-off **`/tmp/*.json`** (or chat-only JSON) that never maps to playbook steps — the next run will not recreate it |
| Durable changes to **rules / playbooks / code** so the **LLM** is guided to build correct `contacts`, Goals, etc. | Repo **“mutation generator”** scripts that replace Step 8 thinking for production UCN — they bypass the same orchestration every real customer uses |
| Replaying a **documented** golden mutation file **in CI** only, with an explicit “fixture replay” label | Checking in `_TEST_CUSTOMER`-only mutation JSON that production agents are expected to copy |

**Contract:** the **canonical** mutation plan for customer-facing writes is whatever **`write_doc`** / `update-gdoc-customer-notes.py write` receives **after** Step 9 approval — produced by the **UCN playbook process** (LLM + gates), not parallel ad-hoc pipelines.

### Principle 2 — Multi-customer means rubric-first, not fixture-shaped logic

We support **20+ real customers** with different stacks, names, and cadence. Anything that only works because `_TEST_CUSTOMER` transcripts always mention the same two names is **harness knowledge**, not product logic.

- **Do:** strengthen [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) (e.g. **Contacts — evidence and mutation shape**) and [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md) Step 6/8 so the **model** knows how to combine **transcripts + `participants` / `stakeholder_signals`** into valid `append_with_history` rows for **any** account.
- **Do not:** add runtime code, CI gates, or playbook rules of the form “if customer is `_TEST_CUSTOMER` then require contact line X” (see already [§10.1](#101-non-negotiable-product-rule-read-first)).

### Where Contacts fit (example of both principles)

- **SSoT for “what to write”:** `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` → **Contacts — evidence and mutation shape**; process in `docs/ai/playbooks/update-customer-notes.md` Step 8 (**Contacts — LLM-built** subsection).
- **E2E validation:** after first UCN, `read_doc` and confirm **non-empty** `contacts` **when** transcripts + call-records name people — if empty, file a **TASK-053** (or active quality task) to fix **extractor/playbook wording**, not hand-apply JSON.

---

## 0.7 Post-write doc vs transcript diff (full v1 quality gate)

This step is the **qualitative tail** of the “full v1 test” ([§0.5](#05-e2e-learnings--keep-improving-quality-docs-rubric-first-rapid-v1) table, phases A–F). It applies whether the write came from **playbook UCN** or from a **bounded harness write** (e.g. replaying a saved mutation JSON for writer validation): the gate is always **evidence in transcripts + call-records vs what landed in the Google Doc** (`read_doc` / `update-gdoc-customer-notes.py read` JSON).

### When to run it

- Immediately **after** first UCN (E2E step **4**) or after any **approved** `write` you are using to judge v1 readiness.
- Before declaring “full v1 green” or moving a **TASK-053** item to done.

### Inputs (read order)

1. **`read_doc`** output (or `read` CLI JSON): full `section_map` — Account Summary tab fields, Challenge Tracker rows, Deal Stage Tracker, Account Metadata, DAL heading inventory if relevant.
2. **All** in-scope **`MyNotes/Customers/_TEST_CUSTOMER/Transcripts/YYYY-MM-DD-*.txt`** files (six per-call files for v1; skip `_MASTER_…` for narrative comparison).
3. Optional: matching **`call-records/*.json`** for structured fields (`key_topics`, `challenges_mentioned`, `stakeholder_signals`, `metrics_cited`) when explaining routing (Goals vs Use Cases vs Accomplishments).

### Method (anti–“vibe only”)

1. **Inventory the doc:** For each material section (Exec summary H3s, Contacts, Company overview, Org, Cloud `tools_list`, Use cases, Workflows, Accomplishments, Challenge Tracker, Deal Stage, Metadata, DAL), record **counts** (e.g. number of `free_text` entries) and **one-line paraphrase** per bullet group — from JSON `entries[].value`, not from memory.
2. **Inventory the corpus:** List themes the transcripts **actually** assert (exec outcomes, risks, tools named, process asks, quantified wins, stakeholder movement).
3. **Build the delta table** (required output for the session): one row per **material** gap, over-coverage, or mis-routing. Use the template below.
4. **Recommendations:** each row maps to **one** of: playbook / `docs/ai/gdoc-customer-notes/mutations-*.md` / extractor rule / writer or router code / **expected** until full UCN (e.g. “Challenge Tracker empty because lifecycle mutations were never in this batch” — not a product bug).
5. **Feed Phase 2 of [§0.3](#03-repeatable-quality-test-loop-start-every-e2e-quality-session-here):** the delta table becomes the **task list** (TASK-053 sub-items or new tasks + INDEX).

### Delta table template (copy into session notes or task file)

| # | Doc section / field | What the doc shows (evidence: `read_doc` path) | What transcripts + call-records support | Δ (gap / surplus / mis-route) | Severity (H/M/L) | Recommendation (single owner: rules / playbook / code / “needs full UCN”) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | … | … | … | … | … | … |

**Severity guide:** **H** = customer-visible wrong or empty where corpus is rich (e.g. Challenge Tracker empty while calls surface multiple themes); **M** = routing / dedupe (Goals vs Use Cases, Splunk risk duplicated); **L** = polish (wording, ordering).

### Example outcome (2026-04-24 harness write — illustrative only)

The following rows are a **real** post-write review against the six bumped v1 transcripts after a **harness-generated** broad `write` (not a substitute for playbook UCN). Use them as an example of **density and honesty** for future sessions — not as fixed expectations for every run.

| # | Doc section / field | What the doc shows | Corpus expectation | Δ | Sev | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `challenge_tracker` | **0** rows | Multiple recurring themes (sensor rollout, Splunk/SOC budget, champion exit, kubelet noise, acquisition / PII) | Tracker empty | **H** | Full UCN must emit `challenge_tracker` + `update_challenge_state` per [§0.5](#05-e2e-learnings--keep-improving-quality-docs-rubric-first-rapid-v1) / [§10](#10-ucn-challenge-tracker-and-lifecycle-how-data-flows-and-where-it-can-drop); harness-only exec/contact batch will not populate tracker. |
| 2 | `accomplishments.free_text` | **0** entries | Quantified wins (900/1000, Wiz Score 92%, 12 toxic combos, PII bucket, Prisma decommission) | Wins not in Accomplishments | **H** | Playbook + rules: ensure accomplishments mutations are not **auto-routed away** from Accomplishments when `metrics_cited` / win language triggers workflow routing; verify `update-gdoc-customer-notes.py` routing for short win lines ([`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) intent). |
| 3 | `workflows.free_text` | Two entries; second reads like a **stray metric line** glued to a workflow heading | One coherent process narrative + optional separate accomplishment | Possible **router** or formatting artifact from accomplishments → workflows path | **M** | Reproduce with minimal mutation; if confirmed, fix writer/router + add regression test. |
| 4 | `company_overview.free_text` | Single line anchored to **one** call’s `summary_one_liner` | Multi-call arc (QBR, DSPM acquisition, shift-left, procurement) | Overview **under-represents** breadth | **M** | UCN Step 6: require ≥1 synthesis bullet **or** explicit skip with reason when only one call’s summary was used. |
| 5 | `exec_account_summary.top_goal` | Six bullets | Mix of strategic outcomes and **procurement / ops asks** | Some lines belong in **Use Cases** per [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) Goals vs Requirements | **M** | Tighten Step 6 “requirement signal” routing in [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md). |
| 6 | `exec_account_summary.risk` | Six bullets; Splunk / budget / champion themes recur | Same commercial themes across calls | **Dedupe** opportunity (same risk, multiple phrasings) | **L** | Mutation rules duplicate-control for Risk theme_key. |
| 7 | `exec_account_summary.upsell_path` | Wiz Cloud, Sensor, DSPM | Transcripts also argue **CIEM**, **Wiz CLI** / Code-adjacent value | Missing distinct upsell lead-ins where separate threads exist | **M** | Enforce Step 6 upsell scan for **CIEM** / **Wiz Code** vs folding into a single “Wiz Cloud” line ([playbook](ai/playbooks/update-customer-notes.md)). |
| 8 | `contacts.free_text` | John + Jane with roles/signals | Named stakeholders + departure + sponsor | **Aligned** | **L** | None for fixture; keep rubric for other customers. |
| 9 | `cloud_environment` `tools_list` | Not expanded in harness batch | GitHub Actions, Okta, Azure, SIEM, Jira named in corpus | Tools not reflected in Cloud Environment | **H** for full realism | Full UCN + `add_tool` routing per rubric; or accept “narrow batch” caveat in harness-only runs. |
| 10 | `daily_activity_logs` | Not exercised | Eight calls exist in full E2E; v1 has six | DAL not updated in this slice | **H** for eight-step E2E | Run DAL prepend pass when Step 6 missing list is non-empty ([`update-customer-notes.md`](ai/playbooks/update-customer-notes.md)). |

---

## 1. What we are actually trying to do

PrestoNotes v2 generates two deliverables for each customer:

1. A **Customer Notes Google Doc** (`MyNotes/Customers/<Name>/<Name> Notes.gdoc`) with three tabs: `Account Summary`, `Daily Activity Logs`, `Account Metadata`.
2. An **AI Account Summary** markdown artifact (`AI_Insights/<Name>-AI-AcctSummary.md`) suitable for exec consumption.

Both are derived, deterministically, from a handful of **source** artifacts that are themselves generated from raw call transcripts. The whole pipeline is agent-orchestrated MCP tool calls + two human-run Python scripts + one rsync.

> **Our job with the `_TEST_CUSTOMER` E2E is to improve the _quality_ of those deliverables** — not the plumbing. The plumbing (TASK-044) works. What we keep hitting is _the LLM producing stub/shortcut extractions_, _the writer silently accepting under-filled sections_, and _the reconciler running on anchor formats nobody emits_. Every task in the 046–052 arc is a write-side or read-side guardrail against one of those failure modes.

Concretely, the E2E test customer workflow exists to:

- **Drive the LLM through the same pipeline a real customer does**, with a fixed 8-transcript corpus whose ground truth we know.
- **Fail loud and early** when a write path emits stub content, a reconciler drops data on the floor, or a playbook step is skipped.
- **Regression-proof** the 046–052 guardrails so a prompt change, a model upgrade, or an agent skipping a step can't silently ship a wave-2-style shortcut extraction again.

If a change to the pipeline does not move the generated GDoc or Account Summary toward "a human wouldn't need to rewrite this", the change is wasted motion.

---

## 2. The canonical eight-step E2E flow ([TASK-052](tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) — archived harness spec)

Authoritative source: `docs/ai/playbooks/e2e-test-customer.md`. Trigger rule: `.cursor/rules/11-e2e-test-customer-trigger.mdc`. Harness: `scripts/e2e-test-customer.sh` (`prep-v1`, `prep-v2`, `list-steps`, `run-step`).

| # | Step | What happens | Artifact(s) touched |
|---|---|---|---|
| 1 | Shell: `prep-v1` | Replaces Notes GDoc from `_TEMPLATE` via Drive **copy + trash/rename** (`prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py`); the Notes **file id may change** (unlike mount-synced `Transcripts/` / `call-records/` / `AI_Insights/`). Then pull, clear logs + `AI_Insights/`, materialize v1 fixture, bump dates, push. | GDoc (possibly new id), `Transcripts/`, `AI_Insights/*` cleared |
| 2 | `Load Customer Context` playbook | Agent reads transcripts + state. No writes. | none |
| 3 | `Extract Call Records` (round 1) | Extraction for v1 corpus → 6 `call-records/*.json`. | `call-records/*.json` |
| 4 | `Update Customer Notes` (round 1) | Lifecycle, ledger, GDoc. | `challenge-lifecycle.json`, `*-History-Ledger.md`, gdoc |
| 5 | Shell: `prep-v2` | **Push local to Drive first**, then pull, materialize v2 **transcripts only** (keeps v1 `call-records/`), bump, push. | `Transcripts/` (+2 files), v1 call-records preserved on disk |
| 6 | `Extract Call Records` (round 2) | 2 new transcripts → 2 new JSON. Total 8. | `call-records/*.json` |
| 7 | `Update Customer Notes` (round 2) | Second UCN. | same as step 4 |
| 8 | `Run Account Summary` | Composes the AI Account Summary. | `AI_Insights/…-AI-AcctSummary.md` (or chat output) |

**`prep-v2` implementation note:** `e2e-test-customer.sh` runs `e2e-test-push-gdrive-notes.sh` *before* the `rsync` pull; if this table and the script ever disagree, use the playbook step-5 [“Parity with the script”](ai/playbooks/e2e-test-customer.md) block as the source of truth.

**Optional (not a numbered step):** nuclear `./scripts/e2e-test-customer.sh reset` + **Bootstrap Customer for _TEST_CUSTOMER** when the Drive tree must be deleted. `prep-v1 --skip-rebaseline` skips the GDoc file replace (faster fixture-only loops).

**Success:** all eight steps complete in one agent session (or in debugger order), `call_records lint` passes after each extract (steps 3 and 6) before the following UCN, no `LIFECYCLE_PARITY` or `transitioned_at` regression errors, artifacts dense and consistent, GDoc and Account Summary read as production-quality.

**Subset — “full v1 test” (steps 1–4 only):** Rebuild Notes via `prep-v1`, then Load Context → Extract → **first** UCN with `call_records lint` before UCN. Documented as a table in [§0.5](#05-e2e-learnings--keep-improving-quality-docs-rubric-first-rapid-v1).

---

## 3. Artifact inventory — purpose, schema, expected content

This section is the cheat-sheet for "what _should_ be in each file after a clean E2E run, and why the schema is shaped that way."

### 3.1 `Transcripts/*.txt`

**Purpose:** raw, append-only record of every customer call. Ground truth for everything downstream.

**Schema:** no schema — plain UTF-8 text. Naming: `YYYY-MM-DD-<slug>.txt`. One file per call.

**For `_TEST_CUSTOMER`, the v1 corpus (6 dated files under `tests/fixtures/e2e/_TEST_CUSTOMER/v1/Transcripts/`) + v2 expansion (2 files under `…/v2/Transcripts/`) = **8 per-call files**.** Re-verify on disk: `ls tests/fixtures/e2e/_TEST_CUSTOMER/v1/Transcripts/2026-*.txt` and `…/v2/Transcripts/2026-*.txt`.

| Date | File (basename) | Notes |
|---|---|---|
| 2026-02-21 | `2026-02-21-test-customer-qbr.txt` | v1 — QBR / exec readout |
| 2026-03-25 | `2026-03-25-runtime-sensor-hardening.txt` | v1 — runtime / sensor / Azure |
| 2026-03-31 | `2026-03-31-shift-left-secrets-ci.txt` | v1 — shift-left, CI, Wiz CLI |
| 2026-04-08 | `2026-04-08-dspm-pii-guardrails.txt` | v1 — DSPM / PII / acquisition context |
| 2026-04-17 | `2026-04-17-exec-sponsor-monthly-readout.txt` | v1 — exec sponsor, budget / Splunk / champion signals |
| 2026-04-22 | `2026-04-22-procurement-siem-review.txt` | v1 — procurement / SIEM / Splunk path |
| 2026-04-28 | `2026-04-28-wiz-cloud-sku-purchase.txt` | v2 — Wiz Cloud commercial close |
| 2026-05-05 | `2026-05-05-wiz-sensor-pov-kickoff.txt` | v2 — sensor POV kickoff |

`v1/Transcripts/_MASTER_TRANSCRIPT__TEST_CUSTOMER.txt` is an **optional aggregate**; it is **not** one of the eight per-call files counted by Extract / E2E.

**Rule of thumb:** if an artifact downstream cannot cite a specific line from one of these eight transcripts, that artifact is hallucinating.

### 3.2 `call-records/*.json` — **schema v2 (TASK-051)**

**Canonical schema:** `prestonotes_mcp/call_records.py::CALL_RECORD_SCHEMA`. Written by `write_call_record`. Validated by `validate_call_record_object` + `validate_call_record_against_transcript`. Linted by `uv run python -m prestonotes_mcp.call_records lint <customer>`.

**Purpose:** dense, LLM-grounded, per-call structured summary. Two downstream readers:
1. `Update Customer Notes` — _outside_ the 1-month lookback window reads call-records (targeted ≤ 5 by id); _inside_ the lookback reads raw transcripts.
2. `Run Account Summary` — aggregates across the whole corpus.

**v2 schema (illustrative):**

```json
{
  "call_id": "2026-04-19-exec-qbr-1",
  "date": "2026-04-19",
  "call_type": "exec_qbr",
  "call_number_in_sequence": 7,
  "duration_minutes": 60,
  "participants": [
    {"name": "John Doe", "role": "Exec Sponsor", "company": "_TEST_CUSTOMER", "is_new": false},
    {"name": "Jane Smith", "role": "Outgoing Champion", "company": "_TEST_CUSTOMER", "is_new": false}
  ],
  "summary_one_liner": "QBR: Wiz Score 92%, 900/1000 workloads scanned, Sensor POV confirmed; Jane departing in a week, John owns continuation.",
  "key_topics": ["Wiz Score", "toxic combinations", "sensor POV", "Prisma decommission"],
  "challenges_mentioned": [
    {"id": "ch-champion-exit", "description": "Jane transitioning out; leadership handoff to John required", "status": "in_progress"}
  ],
  "products_discussed": ["Wiz Cloud", "Wiz Sensor", "Wiz DSPM"],
  "action_items": [{"owner": "SE", "action": "Schedule DaemonSet rollout with platform team", "due": "2026-04-28"}],
  "sentiment": "positive",
  "deltas_from_prior_call": [
    {"kind": "status_change", "challenge_id": "ch-sensor-rollout-stall", "from": "stalled", "to": "resolved", "evidence_quote": "the agent rollout is no longer stalled"}
  ],
  "verbatim_quotes": [
    {"speaker": "Jane Smith", "quote": "900 of our 1000 workloads are scanned — that's a jump from where we were."}
  ],
  "goals_mentioned": [{"description": "Sensor full coverage by end of Q2", "category": "security_posture", "evidence_quote": "we want DaemonSet coverage on the remaining 100 by end of June"}],
  "risks_mentioned": [{"description": "Splunk renewal bundled into Wiz Defend decision", "severity": "med"}],
  "metrics_cited": [
    {"metric": "workloads_scanned", "value": "900/1000", "context": "current Wiz Cloud coverage"},
    {"metric": "wiz_score", "value": "92%", "context": "QBR report card"},
    {"metric": "toxic_combinations", "value": "12", "context": "triage of 10k CVSS criticals down to 12 actionables"}
  ],
  "stakeholder_signals": [
    {"name": "John Doe", "role": "Exec Sponsor", "signal": "sponsor_engaged", "note": "self-identifies as continuity owner post-Jane"},
    {"name": "Jane Smith", "role": "Outgoing Champion", "signal": "champion_exit", "note": "leaving in a week; warm handoff in-flight"}
  ],
  "raw_transcript_ref": "2026-04-19-exec-qbr-*.txt",
  "extraction_date": "2026-04-21",
  "extraction_confidence": "high"
}
```

**Why it's shaped this way:**

- **Four structured-signal arrays (`goals_mentioned`, `risks_mentioned`, `metrics_cited`, `stakeholder_signals`) are v2's reason to exist** (TASK-051). Before v2, Account Summary had to re-read every transcript. After v2, AS aggregates these four arrays + `deltas_from_prior_call` across the corpus and synthesizes from that. That is what makes the Account Summary readable instead of thin.
- `challenges_mentioned[].id` must be a **short thematic kebab** (`^ch-[a-z0-9][a-z0-9-]{1,40}$`). Truncated slug-of-description ids (e.g. `ch-we-want-a-timeboxed-sens`) are the "wave-2 shortcut fingerprint" we explicitly reject in `call_records.py::_check_no_shortcut_fingerprints` (TASK-052 §J.1, landed).
- `key_topics` must be call-specific. A corpus where every record's `key_topics` is `["Wiz platform", "Security posture"]` is the same stub-extraction fingerprint and is banned in `BANNED_CALL_RECORD_DEFAULTS`.
- `verbatim_quotes[].quote` must pass a substring check against the referenced transcript — invented quotes are rejected at write time.
- `summary_one_liner` must **paraphrase**, not echo a quote verbatim — enforced in `_check_no_shortcut_fingerprints`.
- `extraction_confidence` auto-downgrades when ≥ 3 (→ medium) or ≥ 5 (→ low) optional fields are empty. A corpus of all-`low` records is a bug, not a style.
- Size cap: ≤ 2560 bytes serialized per record, ≤ 1536 bytes average across the corpus (checked by lint CLI).

**Example corpus checks (`_TEST_CUSTOMER`):** after a full extract you should see **8** `call-records/*.json` files (one per dated transcript), healthy `extraction_confidence`, varied `key_topics`, populated signal arrays where the transcripts support them, and plausible `stakeholder_signals` / `deltas_from_prior_call` when the calls support those fields — use judgment, not a second hidden schema enforced only for this customer.

### 3.3 `AI_Insights/challenge-lifecycle.json` — **write discipline (TASK-048)**

**Purpose:** authoritative state machine for every customer challenge. Every mutation goes through `update_challenge_state`. The GDoc Challenge Tracker row is a _projection_ of this file; they must agree.

**Schema (implicit from `prestonotes_mcp/journey.py`):**

```json
{
  "ch-soc-budget": {
    "description": "SOC budget for Splunk replacement under procurement review",
    "current_state": "stalled",
    "history": [
      {"at": "2026-04-05", "state": "identified", "evidence": "first mention in weekly sync"},
      {"at": "2026-04-16", "state": "stalled", "evidence": "procurement readout: finance gate delayed"}
    ]
  },
  "ch-champion-exit": {
    "description": "Champion Jane Smith transitioning out; handoff to John Doe in-flight",
    "current_state": "in_progress",
    "history": [
      {"at": "2026-04-16", "state": "identified", "evidence": "procurement readout"},
      {"at": "2026-04-19", "state": "in_progress", "evidence": "QBR: named handoff"}
    ]
  }
}
```

**Write rules (hard-enforced in MCP tool):**

- `id` matches `^ch-[a-z0-9][a-z0-9-]{1,40}$` (same as call-record challenges).
- `transitioned_at` is **required**, ISO `YYYY-MM-DD`, **the call date of the cited evidence** — not the run date.
- Three hard rejections with structured payload: future date (`> today + 1 day` UTC), history regression (`at` older than the newest existing `at` for the id), forbidden evidence vocabulary (substring match against `FORBIDDEN_EVIDENCE_TERMS` in `journey.py` — the SSoT — e.g. `TASK-NNN`, `batch A`, `E2E`, `harness`).
- Old dates of _any_ age are accepted. A transcript pulled 3 weeks late is the common case.

**States:** `identified → acknowledged → in_progress → resolved`, with backward edges `resolved → reopened` and `in_progress → stalled` (60-day no-movement rule).

**Manual quality bar (example corpus only):** for `_TEST_CUSTOMER` tuning sessions you may *compare* lifecycle depth to transcript richness (e.g. several distinct themes across eight calls). **Do not** encode a minimum id set, named challenge ids, or corpus-specific thresholds into **runtime code**, **CI gates**, or **playbook “must list these ids”** rules — real customers differ; hard-coding `_TEST_CUSTOMER` patterns breaks production use. Each `history[].at` you *do* record must still obey TASK-048 (real ISO call dates, no harness vocab, no history regression).

### 3.4 `AI_Insights/<Name>-History-Ledger.md` — **schema v3 (TASK-049)**

**Purpose:** one-row-per-UCN-run historical record of account health, used by Account Summary to narrate trajectory over time.

**Columns (20, snake_case, canonical in `prestonotes_mcp/ledger.py::LEDGER_V3_COLUMNS`):**

1. `run_date`
2. `call_type`
3. `account_health` (red / yellow / green)
4. `wiz_score` (int 0–100)
5. `sentiment` (positive / neutral / negative)
6. `coverage` (free text — concrete: cite 900/1000, Wiz Score %, toxic-combo counts, agent coverage)
7. `challenges_new` (semicolon-separated ids)
8. `challenges_in_progress` (same)
9. `challenges_stalled` (same)
10. `challenges_resolved` (same)
11. `goals_delta`
12. `tools_delta`
13. `stakeholders_delta`
14. `stakeholders_present` (semicolon-separated ids)
15. `value_realized` (concrete quote-backed blurb)
16. `next_critical_event`
17. `wiz_licensed_products` (semicolon-separated Wiz SKU names, e.g. `wiz_cloud;wiz_sensor;wiz_dspm;wiz_ciem;wiz_cli;wiz_code`)
18. `wiz_license_purchases`
19. `wiz_license_renewals`
20. `wiz_license_evidence_quality`

**Write rules (hard-enforced in `append_ledger_row`):**

- Unknown columns → `LedgerValidationError` (no typo drift).
- `run_date` cannot regress older than the newest existing row.
- Forbidden evidence vocabulary rejected per cell (reuses `FORBIDDEN_EVIDENCE_TERMS` SSoT).

**Legacy policy:** v3 deleted v2's migration helper outright. No legacy support. There is no `Value Realized` / `Open Challenges` / `Aging Blockers` / `Resolved Issues` / `New Blockers` / `Key Drivers` column — those v2-era duplicates are gone.

**Open follow-up (TASK-052 §J.7):** minor schema bump 3.1 adding an optional `round` discriminator (`v1` / `v2` / `standalone`) so two UCN passes in a single E2E run can be told apart at a glance. Non-breaking.

**Expected for `_TEST_CUSTOMER`:** exactly **2 rows** after a clean E2E (one per UCN round). `coverage` cells cite concrete numbers (900/1000, Wiz Score 92, 12 toxic combos). `value_realized` row 1 (post-v1) mentions the PII bucket catch; row 2 (post-v2) mentions the Wiz Cloud SKU purchase + Sensor POV kickoff. `wiz_licensed_products` covers the 6 SKUs explicitly discussed by v2 close.

### 3.5 `AI_Insights/<Name>-AI-AcctSummary.md` — **Account Summary (TASK-037 path; TASK-047 expanded)**

**Purpose:** exec-consumable narrative. After TASK-047, it absorbed the retired Journey Timeline's narrative role.

**Shape (sections, top-to-bottom):**

1. **Header** — customer, Wiz Score, coverage %, account health, date.
2. **Goals / Risk / Upsell Path** — 3–5 bullets each, all evidence-anchored.
3. **Challenges → Solutions Map** — every challenge in `challenge-lifecycle.json` (plus any open-but-not-yet-lifecycle'd ones — but those should be rare and indicate a TASK-048 gap).
4. **Journey / Trajectory** — narrative absorbing the retired Journey Timeline: identified themes in chronological order, resolution movement, stakeholder changes.
5. **Stakeholders** — champion / sponsor / owner columns from `stakeholder_signals` aggregated across call-records.
6. **Licensing & Commercial** — from the ledger's Wiz SKU columns + Deal Stage Tracker.

**Hard rule:** no forbidden evidence vocabulary. `FORBIDDEN_EVIDENCE_TERMS` (defined in `journey.py`) catches `TASK-NNN`, `batch A`, `batch B`, `round 1`, `round 2`, `v1 corpus`, `phase`, `E2E`, `harness`, `fixture`. TASK-052 §J.5 (TODO) adds a post-flight that fails the E2E if the generated AcctSummary contains any of these.

**Manual review (example corpus):** for `_TEST_CUSTOMER`, use transcripts + call-records to judge whether the narrative is proportionally complete — **do not** treat a fixed row count or named challenge list as a product requirement.

### 3.6 `<Name> Notes.gdoc` — **UCN completeness + consistency (TASK-050)**

Three tabs. Every `write_doc` mutation passes through `append_with_history` (TASK-050 fix: no more `timestamp: null`) and is reconciled by `challenge_lifecycle_parity.py` before finalize.

#### Tab 1 — `Account Summary`

- **Top:** Goals / Risk / Upsell Path (same shape as the AcctSummary md — these are the section that end up in both places).
- **Challenge Tracker** (Block B) — one row per lifecycle id, `status` column **flipped from lifecycle JSON** (`identified → Open`, `in_progress → In Progress`, `stalled → Stalled`, `resolved → Resolved`). Every row carries a `[lifecycle_id:<id>]` anchor in its notes column so the reconciler can match it.
    - TASK-052 §J.2 (landed) made the reconciler tolerant of the bare `lifecycle:<id>` form too, but the writer is still expected to emit the canonical bracketed form (TASK-052 §D.3, TODO).
- **Company Overview, Contacts, Org Structure, Cloud Environment, Use Cases / Requirements, Workflows / Processes, Accomplishments** — each of these must be ≥ 60 % filled (≥ 80 % for `_TEST_CUSTOMER` E2E) after a clean run (TASK-052 §J.8, TODO). The 22:10 run left all of these empty; that is the primary TODO gap in the content-quality work.
- **Contacts (TASK-052 §J.8.2, generalized):** populate **`contacts.free_text`** using **LLM-authored** `append_with_history` rows per [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) (**Contacts — evidence and mutation shape**) and [`update-customer-notes.md`](ai/playbooks/update-customer-notes.md) Step 8 — combine transcript names with `stakeholder_signals` / `participants` from call-records when present. **Do not** rely on fixture-specific scripts or `/tmp` mutation files; those violate [§0.6](#06-core-product-principles--repeatability-and-multi-customer-ucn).
- **Deal Stage Tracker** — per-SKU row (`cloud`, `sensor`, `defend`, `dspm`, `ciem`, `cli`, `code`). Stage inferred from `products_discussed` per `DEAL_STAGE_*` phrase lists in UCN: `discovery` / `pov` / `win`. **Bump-up only**, never downgrade (TASK-052 §J.10, TODO).

#### Tab 2 — `Daily Activity Logs`

- One date-headed entry per call in the corpus (not per UCN run). 8 calls → 8 entries.
- Entry shape depends on `call_type` (TASK-052 §J.9, TODO): QBR template differs from POV-kickoff differs from procurement-readout. Map will live in `prestonotes_gdoc/dal_templates.yaml`.
- MEDDPICC vocabulary encouraged where the call type supports it (exec, procurement, commercial close).
- No template debris (`- Description` stray rows, etc.) — caught by TASK-052 §J.5.

#### Tab 3 — `Account Metadata`

- 7 fields at the top: `Exec Buyer`, `Champion`, `Technical Owner`, `Sensor Coverage %`, `Critical Issues Open`, `MTTR Days`, `Monthly Reporting Hours`.
- All inferred from `stakeholder_signals` + `metrics_cited` (TASK-052 §J.8.3):
    - Exec Buyer ← latest `signal=sponsor_engaged`.
    - Champion ← latest `signal=champion_active` or `signal=new_contact` marked champion.
    - Sensor Coverage % ← latest `metrics_cited[metric="workloads_scanned"]` → percentage.
    - Critical Issues Open ← latest `metrics_cited[metric ∈ {toxic_combinations, critical_issues}]`.

#### Runtime guardrail: `append_with_history`

- Every mutation records a timestamp + evidence quote.
- `appendix.agent_run_log` gets one entry per successful UCN run (TASK-050 contract). An empty run log after a successful UCN is a bug.

---

## 4. How the write paths connect (mental model)

```
transcripts  ─►  call-records (v2)   ─►  UCN outside-lookback reads
     │                │                        │
     │                ├──►  Account Summary ◄──┤
     │                │                        │
     └──►  UCN inside-lookback reads ──►  Block A mutations
                                             │
                                             ├──►  challenge-lifecycle.json  (update_challenge_state)
                                             ├──►  *-History-Ledger.md       (append_ledger_row)
                                             │
                                             └──►  Block B mutations  ──►  <Name> Notes.gdoc
                                                                              │
                                                                              └──►  reconciler reads
                                                                                    challenge-lifecycle.json,
                                                                                    flips Challenge Tracker
                                                                                    status
```

Key properties this picture encodes:

- **`challenge-lifecycle.json` is authoritative over the GDoc Challenge Tracker.** The reconciler is a one-way sync.
- **Call-records are read-only inputs to UCN.** UCN does not write back to them.
- **The ledger is append-only.** No in-place edits, no row deletion. `run_date` cannot regress.
- **Account Summary is read-only over everything else.** It never writes back to call-records, lifecycle, or ledger.

Every write path is guarded at the MCP tool layer. The three validators we care about:

- `validate_call_record_object` + `validate_call_record_against_transcript` (TASK-051 + TASK-052 §J.1).
- `update_challenge_state` + `append_challenge_transition` hard rejections (TASK-048).
- `append_ledger_row` unknown-column + regression + forbidden-vocab rejection (TASK-049).

---

## 5. How to validate an E2E run

Validation has three layers. Run them in order.

### 5.1 Static checks (no LLM, no Drive)

```bash
bash .cursor/skills/test.sh                         # 115 tests @ 2026-04-21
bash .cursor/skills/lint.sh
bash scripts/ci/check-repo-integrity.sh
bash scripts/ci/check-docs-no-embedded-gdoc-file-ids.sh   # TASK-052 §0.6 — no literal GDoc ids in docs/
```

All of the above must be green before starting an E2E. They will catch schema bugs but not content-quality bugs.

### 5.2 Runtime artifact inspection (by hand, post-E2E)

After **step 8** (eight-step playbook complete), walk through the artifacts in this exact order:

1. **`call-records/*.json`** — all 8 present? `extraction_confidence` ≥ medium on all 8? `key_topics` differ across records? At least one `deltas_from_prior_call` populated? `stakeholder_signals` captures John (sponsor) + Jane (champion exit)?
2. **`challenge-lifecycle.json`** — Does coverage match what transcripts support for *this* customer (qualitative), without demanding a fixed id checklist? Every `history[].at` you rely on matches a real transcript date (not the run date) and passes MCP validators?
3. **`*-History-Ledger.md`** — exactly 2 rows? `coverage` cells name concrete numbers? `wiz_licensed_products` covers all 6 SKUs by row 2?
4. **GDoc Account Summary tab** — Goals / Risk / Upsell populated? Challenge Tracker rows present where lifecycle + transcripts support them, with **`status`** consistent with **`challenge-lifecycle.json`** where `[lifecycle_id:…]` anchors exist? Other sections filled to a credible depth for the corpus (no fixed row-count requirement)?
5. **GDoc Daily Activity Logs tab** — 8 date-headed entries (one per call)? Shape varies by call type? No `- Description` debris?
6. **GDoc Account Metadata tab** — all 7 top fields filled? Deal Stage Tracker has a row per discussed SKU, stages make sense?
7. **`*-AI-AcctSummary.md`** — all 6 sections populated? No forbidden evidence vocab? Stakeholders names John + Jane?

**Scoring:** if ≥ 2 items in the list above fail, the E2E did not succeed regardless of whether all eight steps technically ran.

> **Note (step count):** historical drafts referred to a “10-step” E2E. The [canonical](ai/playbooks/e2e-test-customer.md) flow is **8 steps** (see [§2](#2-the-canonical-eight-step-e2e-flow-task-052)). UCN playbooks can have 11 *internal* steps; that is a different numbering.

### 5.3 LLM-grounded lint (regression sanity)

```bash
uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER
```

Exit 0 = corpus passes v2 schema + size caps + banned-defaults + forbidden-vocab. Run after step 8.

### 5.4 Current validation stance (2026-04-22 reset)

Use existing write-path validators and targeted manual artifact review to evaluate UCN quality. Do not add fixture-specific post-flight gates tied to `_TEST_CUSTOMER` content assumptions.

The E2E loop is used to tune generic extractor/orchestrator behavior, not to hardcode fixture expectations into runtime logic.

---

## 6. What's landed, what's pending (2026-04-22)

### Landed (regression-proofed in CI)

- **TASK-044** — harness rebuild (single script, one playbook chain, approval-bypass scoped to `_TEST_CUSTOMER`).
- **TASK-046** — `transcript-index.json` retired, MCP tools removed.
- **TASK-047** — Journey Timeline retired, narrative absorbed into Account Summary, `FORBIDDEN_EVIDENCE_TERMS` canonicalized.
- **TASK-048** — `update_challenge_state` hard rejections, `FORBIDDEN_EVIDENCE_TERMS` SSoT.
- **TASK-049** — Ledger v3 (20 columns, snake_case, regression + forbidden-vocab guards).
- **TASK-050** — `append_with_history` timestamp, Challenge Tracker reconciler, Deal Stage Tracker motion capture, `agent_run_log` contract.
- **TASK-051** — Call-record schema v2, 4 signal arrays, write-side guardrails, `lint` CLI, extractor + UCN + Account Summary playbook wiring — **complete** → [`tasks/archive/2026-04/TASK-051-call-record-context-quality.md`](tasks/archive/2026-04/TASK-051-call-record-context-quality.md); runtime qualitative checks → **TASK-053 § T053-G**.
- **TASK-052 §J.1** — Call-record validator hardened against wave-2 shortcut fingerprints (hardcoded `key_topics`, truncated challenge id, summary-equals-quote, generic action item).
- **TASK-052 §J.2** — Lifecycle anchor regex accepts both `[lifecycle_id:<id>]` and bare `lifecycle:<id>`.

### TODO (historical TASK-052 backlog)

Ordered by impact at the time TASK-052 was authored:

1. **§A — `ensure-mount --restart`** — unconditional Drive restart + poll after any API folder mutation. User's explicit requirement; prevents the mount-lag stall that caused repeated retries in the #2 run.
2. **§J.5 — Post-flight artifact hygiene** — `scripts/ci/check-e2e-artifact-hygiene.sh` (Journey-Timeline absence, forbidden vocab, low-confidence ban, minimum lifecycle set).
3. **§J.6 — Minimum-lifecycle-challenge-set guard** — enforces ≥ 4 ids including the named `_TEST_CUSTOMER` set.
4. **§F — Positive MCP tool enumeration** in the E2E trigger rule + `rg` guard for retired tool names — **landed** in `scripts/ci/check-repo-integrity.sh` (retired tool name tokens must not appear in active `docs/ai/`, `docs/project_spec.md`, `.cursor/rules/`).
5. **§B — `v2` push-before-pull** + exclude `AI_Insights/*` from `rsync --delete`.
6. **§C — `v2` materialize additive** — scope `_clear_per_call_corpus` to v1 only.
7. **§D.3 — UCN auto-anchor-insertion** — emit canonical `[lifecycle_id:<id>]` at write time.
8. **§E — Transition date guardrail teaching** — playbook/rule text so the extractor doesn't backdate.
9. **§J.3 — Extract-Call-Records playbook sharpening** — self-check block + negative examples.
10. **§J.4 — E2E approval-bypass scope reduction** — do not bypass `write_call_record` approval; auto-approve on validator pass.
11. **§J.7 — Ledger `round` discriminator** (schema 3.1 minor bump).
12. **§J.8 — UCN fill-rate gate + Contacts/Metadata inference + call-type-aware DAL.**
13. **§J.9 — `dal_templates.yaml` config** for DAL shape per call type.
14. **§J.10 — Deal Stage inference from `products_discussed`.**
15. **§G — Account Summary save** explicit in the E2E step 10.
16. **§H — CI regression coverage** for §B, §C, §D.3.

### Active E2E / quality tasks (kept in sync with [INDEX](tasks/INDEX.md))

**Authoritative list:** [`docs/tasks/INDEX.md`](tasks/INDEX.md) (section “Current active task” and TASK-044 follow-ups). The rows below are **not** a second backlog — if they disagree with INDEX, **INDEX wins**.

| Task | Role |
| --- | --- |
| [TASK-044](tasks/active/TASK-044-e2e-test-customer-rebuild.md) | E2E harness + eight-step contract (playbook + script); **on hold** until **053** stabilizes |
| [TASK-051](tasks/archive/2026-04/TASK-051-call-record-context-quality.md) | **Complete** — dense call-record schema v2 + `lint` gate; extractor/UCN lookback split (**runtime checklist:** [TASK-053 § T053-G](tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md)) |
| [TASK-052](tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) | **Complete** (archived) — local-first prep, GDoc rebaseline, **`prep-v1` / `prep-v2`**, push-before-pull; deferred full-run bullets → **053** / **044** |
| [TASK-053](tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) | **Active TOC** — UCN/GDoc fill gaps (e.g. v2 DAL), **push before pull** after local edits, **T053-A–G** + **§T053-G** |

**Aspirational / historical backlog** items in older §6 bullets (e.g. post-flight shims, aggressive fixture guards) are **not** renumbered here. Prefer the **“TODO (historical TASK-052 backlog)”** list above in this same section, or open the relevant task file, until INDEX absorbs them.

### Withdrawn

- **TASK-052 §I — Drive PATCH-in-place reset.** User manually trashes the `_TEST_CUSTOMER/` Drive folder from the web UI before each E2E run. ROI of the script was negative given the manual workaround is cheap.
- **TASK-052 §J.5 (fixture-specific post-flight gate variant).** Replaced by generic validator-first + manual artifact review workflow.
- **TASK-052 §J.6 (minimum `_TEST_CUSTOMER` challenge-set guard).** Withdrawn; do not encode fixture-specific challenge expectations in runtime behavior.

---

## 7. Hard rules for future sessions

These are the invariants. Violating any of them breaks the guarantees the 046–052 arc was built to provide.

1. **Every write path must be validated at the MCP tool layer.** Do not move validation to a playbook note — playbooks are skippable, MCP validators are not.
2. **`FORBIDDEN_EVIDENCE_TERMS` in `prestonotes_mcp/journey.py` is the single source of truth.** Do not inline the list in rules, playbooks, or other Python modules. Import from there.
3. **`challenge-lifecycle.json` is authoritative.** The GDoc Challenge Tracker is a projection. Any time the two disagree the fix is in `challenge_lifecycle_parity.py`, not by hand-editing the doc.
4. **Call-records are read-only inputs.** If Account Summary needs a field that doesn't exist in v2, bump the schema (TASK-051 pattern); do not read raw transcripts to paper over a missing field.
5. **Older transcripts must pass validation.** `transitioned_at` can be any past date. Never gate on "transcript age < N days".
6. **Append-only artifacts stay append-only.** Ledger rows, lifecycle history, `agent_run_log` — no in-place edits, ever.
7. **No harness vocabulary in customer-facing artifacts.** `TASK-NNN`, `batch A`, `round 1`, `E2E`, `harness`, `fixture` — all forbidden. Enforced by write-path validation where applicable.
8. **Support both dense updates and true no-op updates.** Do not force synthetic updates when no material change exists; do not miss meaningful deltas when they do exist.
9. **Do not re-introduce retired MCP tools.** `update_transcript_index`, `append_ledger_v2`, `write_journey_timeline`, `read_transcript_index` — all gone. **`scripts/ci/check-repo-integrity.sh`** runs an `rg` guard so those names cannot creep back into active docs/rules (TASK-052 §F).
10. **The E2E approval-bypass is scoped to `_TEST_CUSTOMER`.** Real customers still require approval. Narrow the bypass further (TASK-052 §J.4) to exclude `write_call_record`; do not widen it.
11. **Do not use ad-hoc `tmp/*.json` mutation files to “fix” the Customer Notes GDoc** in place of playbook + rules + code changes. That path is single-run, `_TEST_CUSTOMER`-only, and not reproducible for other customers. Follow [§0.3](#03-repeatable-quality-test-loop-start-every-e2e-quality-session-here).
12. **Do not add “mutation builder” scripts that replace UCN Step 8 for customer-facing sections** (Contacts, Goals, etc.). Production UCN must stay **playbook + LLM + shared rules** so the same process applies to every account; scripts may assist **CI fixtures** only when explicitly labeled as such. See [§0.6](#06-core-product-principles--repeatability-and-multi-customer-ucn).

---

## 8. File reference — where to find each thing

| Concept | File |
|---|---|
| Call-record schema + validators + lint CLI | `prestonotes_mcp/call_records.py` |
| Challenge state machine + `FORBIDDEN_EVIDENCE_TERMS` SSoT | `prestonotes_mcp/journey.py` |
| Ledger schema v3 + validators | `prestonotes_mcp/ledger.py` |
| GDoc update + reconciler | `prestonotes_gdoc/update-gdoc-customer-notes.py` |
| Challenge Tracker ↔ lifecycle parity | `prestonotes_gdoc/challenge_lifecycle_parity.py` |
| Customer bootstrap | `prestonotes_gdoc/000-bootstrap-gdoc-customer-notes.py` |
| UCN mutation **meaning** (Contacts, Goals vs Use Cases, rubrics) | `docs/ai/gdoc-customer-notes/README.md` → `mutations-account-summary-tab.md` |
| E2E harness | `scripts/e2e-test-customer.sh` |
| v1/v2 materialize | `scripts/e2e-test-customer-materialize.py` |
| Drive push / pull | `scripts/e2e-test-push-gdrive-notes.sh`, `scripts/rsync-gdrive-notes.sh` |
| Drive restart helper | `scripts/restart-google-drive.sh` |
| E2E playbook | `docs/ai/playbooks/e2e-test-customer.md` |
| Extract Call Records playbook | `docs/ai/playbooks/extract-call-records.md` |
| Update Customer Notes playbook | `docs/ai/playbooks/update-customer-notes.md` |
| Run Account Summary playbook | `docs/ai/playbooks/run-account-summary.md` |
| Bootstrap Customer playbook | `docs/ai/playbooks/bootstrap-customer.md` |
| E2E trigger rule (approval-bypass scope) | `.cursor/rules/11-e2e-test-customer-trigger.mdc` |
| Orchestrator / extractor rules | `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc` |
| Subagent workflow | `.cursor/rules/workflow.mdc` |
| Task index / status | `docs/tasks/INDEX.md` |
| E2E harness + Drive + UCN gap tasks | `docs/tasks/active/TASK-044-e2e-test-customer-rebuild.md`, `docs/tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md`, `docs/tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md` |
| Project spec (schemas + architecture) | `docs/project_spec.md` (§7 schemas, §2 architectural rules) |

---

## 10. UCN, Challenge Tracker, and lifecycle: how data flows and where it can drop

This section ties together the **eight-step E2E** ([§2](#2-the-canonical-eight-step-e2e-flow-task-052)), **Update Customer Notes** ([`docs/ai/playbooks/update-customer-notes.md`](ai/playbooks/update-customer-notes.md)), and the **on-disk + GDoc** artifacts. Use it when the **Challenge Tracker** table in the Account Summary tab is **missing rows**, **wrong `status`**, or **out of sync** with what you believe the transcripts support.

### 10.1 Non-negotiable product rule (read first)

**Never** add runtime rules, CI checks, or playbook “detect this exact missing challenge id” logic keyed off `_TEST_CUSTOMER` fixture content, call-type patterns, or “expected” challenge lists. The fixture is **example data**; real accounts differ. Improvements must be **generic** (validators, schema, writer behavior, playbook *process*), not “if customer is X then require challenge Y.”

### 10.2 There is no `challenge-tracker.json`

| Location | What it is |
|----------|------------|
| **Google Doc → Account Summary → Challenge Tracker** | A **table in the doc** (Block B). Updated only when **`write_doc`** applies mutations that target that section. |
| **`MyNotes/Customers/<Name>/AI_Insights/challenge-lifecycle.json`** | The **authoritative** persisted challenge state machine. Updated only via MCP **`update_challenge_state`**. |
| **`MyNotes/Customers/<Name>/call-records/<call_id>.json`** | **Per-call** extraction output. Field **`challenges_mentioned[]`** describes themes surfaced **on that call**; it is **not** a second lifecycle file and is **not** auto-synced into the tracker table. |

### 10.3 Lifecycle id: how we track it

- **Canonical anchor in the GDoc row** (notes / challenge text): **`[lifecycle_id:<challenge_id>]`** — see [`mutations-account-summary-tab.md`](ai/gdoc-customer-notes/mutations-account-summary-tab.md) (Challenge lifecycle ↔ Challenge Tracker) and UCN playbook [Challenge Tracker row discipline](ai/playbooks/update-customer-notes.md). A **legacy** bare **`lifecycle:<id>`** form is tolerated for matching in some paths, but the playbook still asks for the bracketed form.
- **Authoritative state** for `<challenge_id>`: **`challenge-lifecycle.json`**, keys = ids, `current_state` + `history[]` maintained by **`update_challenge_state`** (`prestonotes_mcp/journey.py` validators: dates, no forbidden vocab, no history regression).
- **On `write_doc`**, `prestonotes_gdoc/update-gdoc-customer-notes.py` runs a **Challenge Tracker ↔ lifecycle** pass (see **§3.6** in this doc — `<Name> Notes.gdoc` — and the UCN playbook “Challenge Tracker ↔ lifecycle reconciliation” bullet): for rows that carry a matching lifecycle anchor, the writer can **reconcile row `status`** to the lifecycle mapping (`identified → Open`, etc.). If anchors are missing or lifecycle file is absent, reconciliation may **no-op** for those rows — that is a common “looks wrong in GDoc” source.

### 10.4 End-to-end chain (E2E steps 1 → 4, then 5 → 7)

**Round 1**

1. **`prep-v1`** — template Notes doc on Drive (file id may change), pull, clear `AI_Insights/`, seed **v1 transcripts**, clear **`call-records/*.json`**, bump, push ([`docs/ai/playbooks/e2e-test-customer.md`](ai/playbooks/e2e-test-customer.md)).
2. **Load Customer Context** — read transcripts + current doc snapshot; **no writes**.
3. **Extract Call Records** — for each meeting, agent proposes JSON → user approval (or E2E bypass) → **`write_call_record`** writes **`call-records/<call_id>.json`** (`prestonotes_mcp/server.py`). **Gate:** `uv run python -m prestonotes_mcp.call_records lint <customer>`.
4. **Update Customer Notes (UCN)** — agent plans ordered writes:
   - **`update_challenge_state`** appends transitions to **`challenge-lifecycle.json`**.
   - **`write_doc`** submits **mutation JSON** consumed by **`prestonotes_gdoc/update-gdoc-customer-notes.py`** (Challenge Tracker rows are part of that payload).
   - **`append_ledger_row`**, optional **`sync_notes`**, etc., per playbook.

**Round 2 (after `prep-v2`)** — same as steps 3–4 on the expanded transcript set; **`call-records`** from round 1 must remain on disk (and on Drive before pull) — harness enforces push-before-pull for local files.

### 10.5 Where mutations “live” and how to see if one was created

| Stage | Where to look | What “success” means |
|-------|----------------|----------------------|
| Extract | New/changed files under **`call-records/*.json`** | `write_call_record` returned `{"ok": true, "path": ...}`; `call_records lint` passes. |
| Lifecycle | **`AI_Insights/challenge-lifecycle.json`** | `update_challenge_state` returned `{"ok": true, ...}`; each `history[].at` is a defensible **call date** (TASK-048). |
| GDoc | **`write_doc`** response + post-`sync_notes` / `read_doc`** | Mutations applied; Challenge Tracker shows new/updated rows; reconciler may log `reconcile_with_lifecycle` style applied changes in writer output / agent run log patterns per TASK-050. |

**Dry run:** use **`write_doc`** with **`dry_run=true`** (and the same mutations file) to preview what the writer *would* apply without mutating the doc — fastest loop when tuning UCN mutation JSON.

### 10.6 Phased troubleshooting (Challenge Tracker / lifecycle / extract)

Work **one layer at a time**; do not re-run the full eight steps unless state is corrupted.

**Phase A — Transcript truth**

- Load **all** relevant **`Transcripts/*.txt`** for the customer (or the single call under investigation). If the theme is not spoken, no downstream file should invent it.

**Phase B — Call record (Extract)**

- Open the matching **`call-records/<call_id>.json`**. Check **`challenges_mentioned`**, **`deltas_from_prior_call`**, **`verbatim_quotes`**, signal arrays.
- Run **`uv run python -m prestonotes_mcp.call_records lint <customer>`**. If Extract skipped a call or MCP rejected a write, the gap is **here** before UCN.

**Phase C — Lifecycle journal**

- Read **`AI_Insights/challenge-lifecycle.json`**. If an id never appears, **`update_challenge_state` was never called** for it (or calls failed — inspect MCP JSON error payloads for regression / future-date / forbidden vocab).

**Phase D — GDoc Challenge Tracker**

- **`discover_doc`** / **`read_doc`** (or open the doc in the browser). Compare table rows to lifecycle keys:
  - Row **missing** → **`write_doc`** never included a `challenge_tracker` mutation for that theme (planner/agent gap), or the run was skipped.
  - Row **present but `status` wrong** → often **anchor missing** or lifecycle out of date relative to the row; check notes cell for **`[lifecycle_id:<id>]`** and re-read §10.3.

**Phase E — Drift narrative (LLM vs written state)**

- With **full transcripts + `read_doc` JSON/text** in context, list **drift items**: each is one concrete mismatch (e.g. “transcript T date D mentions theme X; no `challenges_mentioned` id; no lifecycle id; tracker row absent”). **Do not** collapse multiple themes into one task.

### 10.7 “Missing in UCN” vs “missing in JSON” — quick reference

| Symptom | Likely first layer to debug |
|--------|------------------------------|
| Missing **`challenges_mentioned`** entry | **Phase B** (Extract / `write_call_record` / lint) |
| Present in **call-records** but no **lifecycle** id | **Phase C** (UCN never called `update_challenge_state`, or MCP rejected) |
| **Lifecycle** ok but tracker row wrong/missing | **Phase D** (`write_doc` mutations / anchors / reconciliation) |

**Confidence:** seeing a challenge only in **`call-records`** does **not** guarantee it appears in the GDoc; **`update_challenge_state` + `write_doc`** still have to run successfully with coherent anchors.

---

## 11. Drift item task template (for the next agent or nested prompt)

Use **one task per drift item**. Paste the block below into a new chat, `docs/tasks/active/TASK-XXX-….md`, or a session sub-prompt.

```text
## Drift item (one theme / one id / one call date)

### Observed
- Transcript evidence: <file> + short quoted line(s)>
- Expected behavior (neutral): <what a correct pipeline would persist>

### Current state (paste or paths)
- call-records: <path or “absent field”>
- challenge-lifecycle.json: <key path or “id missing”>
- GDoc Challenge Tracker: <row summary or “missing”> / anchors present?

### Hypothesis (pick one to test first)
- H1 Extract did not emit …
- H2 write_call_record rejected …
- H3 UCN did not call update_challenge_state because …
- H4 update_challenge_state failed with …
- H5 write_doc mutation omitted … or dry_run shows skip …
- H6 Anchor / reconciler: …

### Experiment (smallest step)
- Command / MCP calls for this layer only (e.g. re-run lint; re-run write_doc dry_run; re-read single call-record).

### Result
- Confirmed / ruled out: <what changed in files or tool responses>

### Iterate
- Repeat up to **5** cycles (hypothesis → experiment → result) **or** until the root cause for this drift item is fixed or filed as a code/playbook change.
- If the “fix” would add fixture-specific rules (“always create ch-foo for _TEST_CUSTOMER”), **stop** — that violates the product rule in §10.1; instead propose a **generic** schema, validator, or writer improvement.
```

---

## 12. If you change any of the below, update this doc in the same commit

- `CALL_RECORD_SCHEMA` (v2 → v3)
- `LEDGER_V3_COLUMNS` (columns added / renamed / removed)
- `FORBIDDEN_EVIDENCE_TERMS` (terms added / removed — and the same SSoT location)
- Any MCP tool signature on the write path (`write_call_record`, `update_challenge_state`, `append_ledger_row`, `write_doc`, `bootstrap_customer`, `sync_notes`, `sync_transcripts`)
- The eight-step E2E playbook order or the trigger rule's approval-bypass scope
- The active component-task execution order in `docs/tasks/INDEX.md`

Keeping this doc accurate is the contract that lets the next session skip rediscovering the whole problem surface.
