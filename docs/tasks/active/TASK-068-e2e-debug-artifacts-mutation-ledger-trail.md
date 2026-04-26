# TASK-068 — UCN/E2E honesty: checklist, ledger, E2E vs prod, debug trail

**Status:** [ ] open  
**Opened:** 2026-04-24  
**Depends on:** **TASK-044** (harness), **TASK-064** (tester doctrine), **TASK-053** (GDoc/UCN quality TOC, cross-links); **TASK-067** (MCP prereq checks) optional

## Problem

- **Harness** steps **1–8** (`e2e-test-customer.sh`) and **UCN** sub-steps **1–11** (`update-customer-notes.md`) are different layers. Agents can “win” on **`write_doc`** while **skipping** the UCN **Step 6** coverage work, **Step 11** ledger, or a clear **DAL-only** scope.
- **Quality** for “every field visited or explicitly skipped” is a **playbook** bar today, not a hard **lint**—so work is **skipped in practice** without a toolchain error.
- **E2E `_TEST_CUSTOMER`**: approval pauses (UCN **Step 9**) and question stops (**Step 7**) must stay **off**; **production** must keep them. This must stay **one sentence** in docs, not a second policy file.
- **Ledger**: after a successful GDoc change, a **History Ledger** row is expected; skipping it is a **harness** gap, not a preference.
- **`ucn-approved-mutations.json`**: still **optional** for routine runs; teams need a **debug** trail without duplicating a second doctrine doc.

## Goal (agreed 2026-04-24)

1. **Planner / checklist (UCN 6/8, high level)**  
   - Require a **short machine-friendly outcome** (same skip reasons the playbook already names): every important section is either **updated** or **skipped with a reason**—**no silent skip.**  
   - **Prefer extending existing playbooks and one validation path** over new parallel “guides.”

2. **E2E vs production (UCN 7 & 9)**  
   - **E2E `_TEST_CUSTOMER`:** no waiting on the user for questions or write approval; log a one-liner (e.g. `clarification_gate: none`, `approval: bypassed per 11-e2e`).  
   - **Real customers:** keep UCN **Step 7** and **9** as today. **Do not** fork MCP; **`.cursor/rules`** + playbook notes only.

3. **`v1_full` vs `v1_partial`**  
   - **`v1_full`** = first UCN is **full** (all UCN sub-steps that apply) unless the doc says otherwise. **DAL-only** = **`v1_partial`** with an **explicit** skip list in the tester report (so empty Account Summary is not a false “green”).

4. **Ledger after write (UCN 11)**  
   - Treat a successful UCN write and a **new ledger row** as one **expected** chain for honest E2E and prod. Implementation may be: stronger playbook wording, a **`write` flag**, or a small **post-check** script for CI/E2E.

5. **Optional debug mode** (no routine file spam)  
   - Flag (Delegation packet and/or `PRESTONOTES_E2E_DEBUG=1`): under **`MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/e2e-debug/<ISO-datetime>/`** (or same pattern for any customer in debug), write **`mutations.json`**, **pre/post `read_doc` pointers**, **harness 1–8** + **UCN 1–11** checklists, **ledger** attempt/result. Default **off**.

6. **E2E operator catalog — maintainer contract (future flow changes)**  
   - **SSoT:** [`scripts/lib/e2e-catalog.txt`](../../../scripts/lib/e2e-catalog.txt) — trigger phrases, eight-step harness, `e2e_workflow` modes; printed by **`./scripts/e2e-test-customer.sh list-catalog`** (alias **`list-all`**) and sliced by **`list-steps`**.  
   - **Design doc (layered, minimal duplication):**  
     - **Contract** in the **header comments** of `e2e-catalog.txt`: what `list-catalog` / `list-steps` are for; that any new user-visible **step**, **trigger**, or **workflow mode** must be updated here; **sync list** (e.g. `11-e2e-test-customer-trigger.mdc`, `tester.md` §4, shell `usage` if new subcommands).  
     - **Procedure** in [`docs/ai/playbooks/tester-e2e-ucn.md`](../../ai/playbooks/tester-e2e-ucn.md): short **“Maintaining the E2E harness”** (or equivalent) checklist — when adding/renaming flows, update catalog → rule/tester as needed → verify with `list-catalog`.  
     - **One cross-link** in [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) (operator section): structural E2E changes are driven from **`e2e-catalog.txt` + that playbook section**; do not maintain a second long spec in `tester.md`.  
   - **Non-goal:** a separate long `docs/…` “catalog architecture” file unless the checklist outgrows the playbook.

## Non-goals

- A second SSoT next to **`.cursor/agents/tester.md`**.  
- Mandating `ucn-approved-mutations.json` on every run.  
- **Breaking** the default `write_doc` contract without a versioned follow-up; optional flags are OK.

## Files to touch (reuse; avoid new parallel docs)

| Area | Path(s) — edit in place, cross-link; don’t duplicate long prose |
| --- | --- |
| Tester workflow / `v1_full` vs `v1_partial` | [`.cursor/agents/tester.md`](../../.cursor/agents/tester.md) §4 (and session/init if needed) |
| Eight-step harness + E2E note on UCN 7/9 | [`docs/ai/playbooks/tester-e2e-ucn.md`](../../ai/playbooks/tester-e2e-ucn.md) (short), link [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](../../.cursor/rules/11-e2e-test-customer-trigger.mdc) + [`core.mdc`](../../.cursor/rules/core.mdc) |
| UCN: checklist, Step 11 ledger, optional planner shape | [`docs/ai/playbooks/update-customer-notes.md`](../../ai/playbooks/update-customer-notes.md) Steps 6, 8, 10, 11; optional pointer from [`docs/ai/gdoc-customer-notes/README.md`](../../ai/gdoc-customer-notes/README.md) or [`mutations-global.md`](../../ai/gdoc-customer-notes/mutations-global.md) if the playbook would bloat |
| Tighter E2E bullets (if needed) | [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](../../.cursor/rules/11-e2e-test-customer-trigger.mdc) — one paragraph max |
| **Code (later / same task phase 2)** | [`prestonotes_mcp/server.py`](../../../prestonotes_mcp/server.py) `write_doc` / optional validation; [`prestonotes_gdoc/update-gdoc-customer-notes.py`](../../../prestonotes_gdoc/update-gdoc-customer-notes.py) `write`; [`prestonotes_mcp/server.py`](../../../prestonotes_mcp/server.py) `append_ledger_row` orchestration; optional new script under [`scripts/`](../../../scripts/) or [`scripts/ci/`](../../../scripts/ci/) for “write without ledger” detection |
| E2E catalog SSoT + maintainer contract | [`scripts/lib/e2e-catalog.txt`](../../../scripts/lib/e2e-catalog.txt) (header comments); [`scripts/e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh) `list-catalog` / `list-steps` (no duplicate prose — script reads the file) |
| Playbook: maintaining harness | [`docs/ai/playbooks/tester-e2e-ucn.md`](../../ai/playbooks/tester-e2e-ucn.md) — **Maintaining the E2E harness** (checklist) |
| INDEX | [`docs/tasks/INDEX.md`](../INDEX.md) — only if the task title/summary line needs refresh |

**Prompts:** full-session context for implementers: [`docs/ai/prompts/task-068-execution-prompt.md`](../../ai/prompts/task-068-execution-prompt.md). Update [`docs/ai/prompts/e2e-task-execution-prompt.md`](../../ai/prompts/e2e-task-execution-prompt.md) **only** if it still points at old paths—**one** pointer to `tester.md` + this task’s terms (`e2e_debug`, `v1_partial`).

## Acceptance

- [x] **Docs:** 8 harness steps vs 11 UCN sub-steps; **`v1_full` vs `v1_partial`** (DAL-only = partial + explicit skips); E2E = no Step 7/9 **user** pauses, prod = keep pauses.  
- [x] **Checklist / planner:** documented requirement that every key section is **mutate** or **skip+reason** (shape TBD; align with `update-customer-notes.md` and existing skip enums).  
- [x] **Ledger:** playbook + tester say UCN is not “done” without **Step 11** when a write applied; E2E expects ledger row the same as prod.  
- [x] **Debug mode:** one flag, artifact layout, default off; optional **Output Contract** fields `e2e_debug`, `debug_artifact_path` in **`.cursor/agents/tester.md`**.  
- [x] **E2E catalog maintainer contract:** `e2e-catalog.txt` header documents design + sync targets; `tester-e2e-ucn.md` has a short **maintaining the harness** checklist; `tester.md` has **one** pointer to those (no second SSoT).  
- [x] **Code (if in scope of this task):** shipped phase-2 recovery path in MCP (`write_doc` latest recovery cache + state machine, `read_ucn_recovery_state`, `recover_ledger_from_latest`) and orchestrator/playbook recovery mandate; strict fail-fast verifier script remains optional follow-up.

## Verification

- [ ] **Manual:** `v1_full` run with debug on → `e2e-debug` folder populated; with debug off → no new tree (or documented empty manifest only).  
- [ ] **Manual / CI:** run a controlled ledger-failure drill: after a successful `write_doc`, force `append_ledger_row` failure and confirm `read_ucn_recovery_state` + `recover_ledger_from_latest` returns state to `complete` (or clearly `blocked` with recovery payload).  
- [x] `bash scripts/ci/check-repo-integrity.sh` (or project equivalent) still passes if touched manifests.

## Sequencing (suggested)

1. **Docs only** (all files in “Files to touch” that are `docs/` or `.cursor/`).  
2. **Debug directory behavior** (agent or thin script that writes the bundle when flag on).  
3. **Code gates** (validator +/or ledger coupling +/or CI script) as a **follow-up** sub-PR in the same task or explicit “phase 2” in INDEX.

## References

- `scripts/lib/e2e-catalog.txt` — SSoT for triggers, eight steps, workflow modes; `list-catalog` / `list-steps`  
- `scripts/e2e-test-customer.sh` `list-catalog` · `list-steps`  
- `docs/ai/playbooks/tester-e2e-ucn.md`  
- `docs/ai/playbooks/update-customer-notes.md` (Steps 1–11)  
- `.cursor/agents/tester.md` §4  
- `docs/ai/gdoc-customer-notes/` (mutation meaning; no duplicate “second playbook”)
- `docs/ai/prompts/task-068-execution-prompt.md` — LLM session prompt (layers, UCN 7/9/11, sequencing, verification)  
