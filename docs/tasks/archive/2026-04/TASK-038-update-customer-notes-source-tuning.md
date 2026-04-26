> **Archived:** 2026-04-22 — completed tasks moved out of `active/` per **TASK-053** ([`TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md`](TASK-053-active-task-queue-cleanup-and-archive-reconciliation.md)).
>
# TASK-038 — Update Customer Notes: source bundle + quality bar

**Status:** [x] COMPLETE  
**Opened:** 2026-04-21  
**Legacy Reference:** **`docs/ai/playbooks/update-customer-notes.md`**; **`docs/ai/references/customer-data-ingestion-weights.md`**.

## Goal

Make **Update Customer Notes** explicitly match your MVP intent:

1. **Read last month** of transcripts (per-call), **GDoc/`read_doc` export**, and **`*-AI-AcctSummary.md` if present** (blocked until **TASK-037** or manual file).
2. **Tabs:** Exec account summary, Daily Activity (prepend rules only), account metadata — align mutation plan to **what exists on Drive** for sparse vs rich accounts.
3. **Quality bar:** trends, value, **next steps for SE** — add a **checklist** in the playbook and a **“no evidence”** pattern per **project_spec** evidence tags.

## Acceptance

- [x] Playbook § lists **exact** MCP read order and fallbacks when files missing.
- [x] “Sparse account” vs “rich account” subsection.

## Output / Evidence

- `docs/ai/playbooks/update-customer-notes.md` updates:
  - Added required **source bundle and fallback order** section (last-month transcripts + `read_doc` + `*-AI-AcctSummary.md` if present).
  - Added explicit fallback behavior for missing transcript/AI_Insights/ledger data.
  - Added **Sparse vs rich account strategy** subsection.
  - Added **quality bar checklist** (trends, value, SE next steps, `no_evidence` behavior).
