# Playbook: Debug Pipeline (Stage 3 integration)

Trigger (for searchability; same spirit as `docs/project_spec.md` §11):

- `Debug Pipeline for [CustomerName]`

Purpose: **manual** checklist to validate **`Update Customer Notes for [CustomerName]`** when routed through the **orchestrator** (`.cursor/rules/20-orchestrator.mdc` via `.cursor/rules/10-task-router.mdc`) versus the **monolithic** playbook **[`update-customer-notes.md`](update-customer-notes.md)**. Use this when something diverges, a write looks wrong, or you need evidence that both paths behave as expected.

> **`update-customer-notes.md`** remains the **supported fallback** monolithic procedure until you deliberately retire it; do **not** treat “archive the old playbook” as a prerequisite for Stage 3 validation (see `docs/tasks/active/PHASE3-PLAN.md` Wave D).

> **Writes:** Only where a playbook step explicitly requires MCP writes **after** the usual user approval gate (`docs/project_spec.md` §2 Rule 3). Prefer **`read_doc`** with **`dry_run=true`** on **`write_doc`** when validating mutations.

---

## Before you start

1. Pick **`[CustomerName]`** with a known-good export under **`MyNotes/Customers/[CustomerName]/`**.
2. Capture a **baseline** (optional but recommended): save **`read_doc`** output for a fixed set of headings **or** note **`doc_id`** + timestamp **before** the test run.
3. Confirm **`check_google_auth`** succeeds if you will call Docs MCP tools.

---

## Checklist — Orchestrator path

1. **Router** — Confirm **`10-task-router.mdc`** applies: user message uses **`Update Customer Notes for [CustomerName]`** and the model loads **`20-orchestrator.mdc`** (not only the monolithic playbook in isolation).
2. **Sync (step 1)** — Verify **`sync_notes`** and **`sync_transcripts`** were invoked (or explicitly skipped with user consent and documented reason).
3. **Transcript index (step 2)** — Call **`read_transcript_index`**. Confirm index JSON matches expectations (call count, `record_file` paths). If new transcripts lack records, confirm extractor / **`write_call_record`** path only ran **after** approval per **`21-extractor.mdc`** / **`core.mdc`**.
4. **Reads (steps 3–4)** — Confirm **`read_doc`**, **`read_ledger`** (last **5** rows), and **`read_audit_log`** (last **10** entries) were used to scope **full update** vs **lighter** pass.
5. **Delta (step 5)** — Confirm a **`CustomerStateUpdate.json`** (shape per **`docs/ai/references/customer-state-update-delta.md`**) was produced or validated before advisors.
6. **Advisors (step 6)** — Confirm **SOC → APP → VULN → ASM → AI** order; each consumed the same delta object; ASM had access to **`architecture_diagram_paths`** when present.
7. **Compile (step 7)** — Inspect merged **mutation JSON** against **`prestonotes_gdoc/config/doc-schema.yaml`** and **`docs/ai/references/customer-notes-mutation-rules.md`**. Confirm proposed **`append_ledger_v2`** **`row_json`** matches **24-column** v2 expectations **or** documented **`append_ledger`** fallback.
8. **Approval gate (step 8)** — Confirm **no** **`write_doc`** / **`append_ledger`** / **`append_ledger_v2`** / **`write_journey_timeline`** / **`log_run`** / mutation **`sync_notes`** until the user explicitly approved. Confirm **`write_doc`** **`dry_run=true`** was used when offered.
9. **Execute (step 9)** — After approval only: verify **`write_doc`** success, new **History Ledger** row (v2 columns if migrated), **`write_journey_timeline`** if applicable, **`log_run`**, then **`sync_notes`**.

---

## Checklist — Monolithic path (fallback)

1. Open **[`update-customer-notes.md`](update-customer-notes.md)** and run **`Update Customer Notes for [CustomerName]`** following that playbook **without** forcing the orchestrator (e.g. session explicitly focused on the monolithic steps — use for apples-to-apples comparison only when needed).
2. Repeat the **same baseline captures** as above ( **`read_doc`**, **`read_ledger`** ) so comparisons are fair.

---

## Checklist — Regression and diff

1. **`read_doc` diff** — Compare **Account Summary** (and any other agreed sections) **before vs after** the run: headings present, no unintended blanking, list items under correct H3s per mutation rules.
2. **Ledger row** — Open **`[CustomerName]-History-Ledger.md`** (or MCP **`read_ledger`**): confirm **one** new row appended, dates align with the meeting, challenge / value columns populated per **`append_ledger_v2`** contract when on v2.
3. **Audit trail** — Confirm **`read_audit_log`** shows an expected entry if **`log_run`** was part of the approved batch.
4. **Local mirror** — After **`sync_notes`**, confirm **`[CustomerName] Notes.md`** export reflects the same story as **`read_doc`** for spot-checked paragraphs.
5. **Optional deep check** — When **`Run Logic Audit for [CustomerName]`** exists as a ported playbook, run it **once** per spec §9 TASK-019; until then, note **“deferred — logic audit playbook not MVP”** in your own run notes.

---

## Checklist — Quality comparison (orchestrator vs monolithic)

1. **Accuracy** — Do proposed changes match the **latest call** facts (participants, dates, commitments)?
2. **Duplication** — Fewer duplicate bullets vs a known-good monolithic run?
3. **Domain coverage** — Orchestrator output shows distinct **SOC / APP / VULN / ASM / AI** contributions (no copy-paste repeats across domains).
4. **Exec safety** — No internal jargon leaked into customer-facing mutations.
5. **Approvals** — Stricter path (orchestrator) never skipped the **step 8 STOP**; monolithic path never called **`write_doc`** without showing mutations first.

---

## When to stop and escalate

- **Schema / mutation validation errors** — Paste the tool error; fix JSON before retrying **`write_doc`**.
- **`append_ledger_v2` migration errors** — Follow **`docs/MIGRATION_GUIDE.md`** and **`python -m prestonotes_mcp.tools.migrate_ledger`**.
- **Auth failures** — Use MCP **`run_in_terminal_to_fix`** guidance from **`.cursor/mcp.env`**.

Record: **customer**, **date**, **path** (orchestrator vs monolithic), **pass/fail** per numbered item above, and **screenshot or pasted snippet** for any failed diff.
