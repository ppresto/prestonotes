# TASK-069 — E2E tester: post-write diff accuracy (Account Summary + tab parity)

**Status:** [x] complete (docs/rules — 2026-04-24)  
**Opened:** 2026-04-24  
**Related:** **TASK-068** (E2E honesty, `v1_full` vs partial, planner checklist); **TASK-053** (GDoc/UCN quality); **TASK-070** (implementation of richer UCN writes — runs after or in parallel with rules)

## Problem

On a real **`v1_full`** run, the first **post-write diff** the agent produced was **inaccurately narrow**: it scored Exec Summary + DAL + a few free-text fields as “green” while **omitting** whole Account Summary (and related) areas that a human review immediately found empty:

- **Contacts** (expected named stakeholders from transcripts)
- **Challenge Tracker** (expected rows when call-records and dialogue name challenges)
- **Cloud Environment** sub-labels (CSP, IDP, platforms, DevOps, ticketing, security tools, sizing — all clearly stated across v1 calls)

The operator had to **point out the gaps**; only then did the agent re-inventory the **full** `read_doc` `section_map`, re-read **all six** v1 transcripts, and build a **second** diff table with correct **H**-severity rows for those sections.

**Root cause (document in task; encode in rules):**

1. **Scope of the first diff:** The run optimized for the **planner coverage guard** in `prestonotes_gdoc/update-gdoc-customer-notes.py`, which only **requires** explicit coverage for  
   `exec_account_summary.top_goal`, `exec_account_summary.risk`, `use_cases.free_text`, `workflows.free_text`.  
   It does **not** require `contacts`, `challenge_tracker`, or `cloud_environment`. The UCN mutation bundle matched that minimum + DAL — so **`read_doc` was truthfully empty** in those sections, but the **tester’s diff narrative did not call that out** as a failure of completeness.

2. **Omission in tester doctrine:** [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) §6 says to inventory the doc and corpus, but the first pass did not treat **“Account Summary tab as a checklist”** (Contacts, Challenge Tracker, Cloud Environment, and — see TASK-070 — **Account Metadata** on its tab) as **mandatory rows** in the delta table when transcript/call-record signal exists.

3. **What the second pass did differently:** On user challenge, the agent:  
   - Re-fetched **`read_doc`** and walked **`section_map`** for **every** H1-relevant area on the Account Summary experience, not only fields that had been mutated.  
   - Re-read **v1 per-call transcripts** (not just “themes”) to list **expected** contacts, **challenge** themes, and **cloud/tool** facts.  
   - Compared **expected vs `read_doc` evidence** and produced **H/M** severities for **empty-where-rich-corpus** gaps.  
   That second pass is the quality bar the **first** pass should have met.

## Goal

Make **E2E tester** post-`write_doc` **diff + recommendations** **complete and honest** by default:

1. **Mandatory delta coverage:** For `v1_full` (and `full` when UCN runs), the post-write diff **must** include explicit rows for at least:  
   - **Exec Account Summary** (goals, risk, upsell if applicable)  
   - **Contacts**  
   - **Challenge Tracker**  
   - **Cloud Environment** (per sub-field or a compact “tools + CSP + IDP + sizing” row group)  
   - **Account Metadata** (tab parity — see **TASK-070**)  
   If a section is **empty in `read_doc`**, the diff must say so and score **H** or **M** when **in-scope transcripts / call-records** contain clear signal — **unless** the approved mutation plan documented **`no_evidence` / skip+reason** for that field (per UCN playbook).

2. **No false “green”:** Do not report success on “Account Summary quality” if only the **four key fields** + DAL were updated; **surface empty sections** that the corpus supports.

3. **Encode in rules/playbooks:** Update [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) §6 (and a short pointer in [`docs/ai/playbooks/tester-e2e-ucn.md`](../../ai/playbooks/tester-e2e-ucn.md) if needed) with a **repeatable checklist** mirroring the second-pass method: full `read_doc` section inventory + transcript line-of-sight for contacts/challenges/cloud/metadata.

## Non-goals

- Changing the **code** `KEY_FIELD_COVERAGE_REQUIREMENTS` set (that is product/UCN design; optional follow-up).  
- Replacing **TASK-070** — this task is **process/rules**; TASK-070 is **implementation** of better writes.

## Files to touch (suggested)

| Area | Path(s) |
| --- | --- |
| Tester SSoT | [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) — §6 Post-write diff: mandatory rows, H when empty+signal, no silent omit |
| E2E harness playbook | [`docs/ai/playbooks/tester-e2e-ucn.md`](../../ai/playbooks/tester-e2e-ucn.md) — short “diff completeness” bullet; link §6 |
| E2E trigger (optional, one paragraph) | [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](../../.cursor/rules/11-e2e-test-customer-trigger.mdc) |
| Prompts (optional) | [`docs/ai/prompts/e2e-task-execution-prompt.md`](../../ai/prompts/e2e-task-execution-prompt.md) — pointer to full diff checklist |

## Acceptance

- [x] **tester.md §6** states that a **`v1_full` / `full` post-UCN diff** includes **Contacts, Challenge Tracker, Cloud Environment, Account Metadata** (and Exec/DAL as today), with **severity** when `read_doc` is empty but corpus is rich.  
- [x] **Explicit** note that the **planner code guard ≠ complete Account Summary** — tester must not equate the two.  
- [x] **tester-e2e-ucn.md** (or equivalent) cross-links; no second long SSoT.  
- [x] **Output Contract** row `delta_table` / `recommendations_summary` expectations updated if needed so orchestrator reviews know **empty section = scored gap**, not omitted.

## Verification

- [x] Dry-run: **§6** now mandates a **Contacts** row for `v1_full` / `full` and scores **H/M** for empty-where-corpus-signal; a mock with empty `contacts` + named stakeholders in transcripts is therefore flagged per doctrine (no code path required).  
- [x] `bash scripts/ci/check-repo-integrity.sh` — **2026-04-24** (exit 0; `tester.md` was already in `required-paths.manifest`).

## Sequencing

- Land **after or with** user approval; **TASK-070** can ship UCN content fixes while this task **tightens the harness** so the next run catches regressions.
