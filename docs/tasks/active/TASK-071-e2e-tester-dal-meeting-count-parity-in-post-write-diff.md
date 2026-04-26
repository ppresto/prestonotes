# TASK-071 — E2E tester: DAL **meeting-block count** vs transcript lookback in post-write diff

**Status:** [x] complete  
**Opened:** 2026-04-24  
**Related:** **TASK-069** (mandatory section rows; **missed** DAL *richness* dimension); **TASK-060** (UCN DAL product tuning); **TASK-072** (deterministic planner contract); `docs/ai/playbooks/update-customer-notes.md` Step 6 / 8; `docs/ai/references/daily-activity-ai-prepend.md`

## Problem

On **`v1_full`**, a post-`read_doc` diff can report **Daily Activity** as “filled” because `section_map.daily_activity_logs.fields.free_text.entries` contains **multiple paragraphs** (Anchors, **one** `YYYY-MM-DD — title` line, **Outcomes / Risks / Next** labels, **Description** stubs, etc.). That is **one meeting recap** expanded into many `entries` — not **6–7 distinct meeting recaps** matching **6** per-call transcripts in lookback (optionally **7** if `_MASTER_` is in scope).

The UCN contract is: **one `prepend_daily_activity_ai_summary` per in-lookback transcript meeting** that is not already represented in the doc (`update-customer-notes.md` Step 6–8; `mutations-daily-activity-tab.md`).

A tester who only checks “DAL row exists / has text” will **false-green** when the **approved mutations** included a **single** `prepend_daily_activity_ai_summary` (e.g. latest QBR only) while five other calls had **no** prepend.

## Goal

Make **E2E post-write diff** catch **DAL count gaps** the same way it now catches empty Contacts / Cloud / Metadata:

1. **Transcript inventory:** Count **per-call** files under `MyNotes/Customers/<customer>/Transcripts/YYYY-MM-DD-*.txt` in the **active lookback** (E2E: use orchestrator/operator **stated** lookback; default **exclude** `_MASTER_*` unless the run packet says otherwise). Expected meeting count = that count (or explicit skip list, `v1_partial` style).
2. **Doc inventory — meeting blocks, not raw entry count:** From `read_doc` DAL, count **distinct meeting recaps** using the same normalization idea as the UCN **duplicate guard** (first line of each **dated heading block** / `heading_line` pattern: `^\\d{4}-\\d{2}-\\d{2}` or equivalent per `daily-activity-ai-prepend.md`). **Do not** use `len(entries)` as a proxy for “number of meetings.”
3. **Delta row (mandatory for `v1_full` / `full` when DAL is in scope):**  
   - **Transcripts in lookback (N)** vs **DAL meeting blocks in doc (M)**.  
   - If **M < N** and the mutation plan did **not** document **skip+reason** for the missing dates → severity **H** (customer-visible gap) unless the run was explicitly `v1_partial` with a written skip list.

## Boundary (avoid duplication with TASK-072)

- This task is **tester post-write scoring only** (how to detect/report DAL underfill).
- Planner generation rules and fail-fast preflight for DAL/Deal Stage belong to **TASK-072**.

## Non-goals

- Changing the Google Doc writer or planner in this task (tuning lives in **TASK-060** / UCN workstreams).
- Requiring **verbatim** heading text between transcript filename and DAL (normalize on **date** first).

## Files to touch (suggested)

| Area | Path(s) |
| --- | --- |
| Tester SSoT | [`.cursor/agents/tester.md`](../.cursor/agents/tester.md) — §6: DAL **meeting-block** vs **transcript count**; warn on `entries.length` as misleading |
| E2E harness | [`docs/ai/playbooks/tester-e2e-ucn.md`](../ai/playbooks/tester-e2e-ucn.md) — one checklist bullet |
| Optional | [`docs/ai/prompts/e2e-task-execution-prompt.md`](../ai/prompts/e2e-task-execution-prompt.md) — pointer |

## Acceptance

- [x] **tester.md §6** includes an explicit **DAL parity** sub-step (**§6.1**): compare **N** transcript files (in lookback, `_MASTER_` rule stated) to **M** **meeting** blocks in DAL, not `entries` count. *(Landed 2026-04-24.)*
- [x] **v1_full** / **full** delta table includes a **Daily Activity (coverage)** row when UCN was in scope, showing **N vs M** and **H/M/L** when `M < N` without documented skips. *(§6.1 + mandatory rows bullet in §6 step 3.)*
- [x] Short **non-goal** note: multi-line DAL = one meeting; do not treat many `free_text` entries as many meetings. *(In §6.1.)*
- [x] `docs/tasks/INDEX.md` lists this task. *(Landed 2026-04-24.)*
- [x] **`tester-e2e-ucn.md`** one bullet under Post-UCN diff. *(Landed 2026-04-24.)*
- [x] **`e2e-task-execution-prompt.md`** — optional pointer to §6.1 (if not redundant with existing TASK-069 text). *(Landed 2026-04-24.)*

## Verification

- **Doc-only dry-run:** A mock report with 6 lookback transcripts and one dated heading in DAL is scored **H** on the DAL row per §6 (no code required for merge).
- [x] `bash scripts/ci/check-repo-integrity.sh` (if manifest requires touched paths). *(Exit 0 on 2026-04-24.)*

## Sequencing

- Land after **TASK-069** (already complete); complements **TASK-060** (product) with **harness** enforcement.

## Incident note (2026-04-24 `_TEST_CUSTOMER` v1_full)

- **N:** Six per-call `v1/Transcripts/YYYY-MM-DD-*.txt` files in fixture; seven files if including `_MASTER_TRANSCRIPT__TEST_CUSTOMER.txt` (usually **out of scope** for per-call DAL; confirm in run packet).  
- **M:** **One** `prepend_daily_activity_ai_summary` in `.cursor/task070_ucn_mutations.json` (only `2026-04-21 — QBR and monthly sync`).  
- **Why not caught:** §6 required a **Daily Activity** *section* row but did not require **N↔M** count parity; the agent conflated **rich `entries` array** with **multiple meetings**.  
- **Per-meeting “miss” (same root cause, not six independent bugs):** The UCN run did not apply Step 6 **missing list** + Step 8 **one prepend per missing meeting**; only the latest QBR was prepended. No per-call writer failure — **mutation plan incompleteness**.
