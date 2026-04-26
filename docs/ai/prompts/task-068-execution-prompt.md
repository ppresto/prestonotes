# LLM prompt: execute **TASK-068** (UCN/E2E honesty)

**Use when:** you (or an operator) want a single session to **implement or continue** [`docs/tasks/active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md`](../../tasks/active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md) with enough context that the model does not have to re-derive scope from scratch.

**Related (generic habits, not task-specific):** [`kick-off-next-task-session.md`](kick-off-next-task-session.md) · [`e2e-task-execution-prompt.md`](e2e-task-execution-prompt.md) · [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md)

---

## Canonical spec

- **Task file (read first, end-to-end):** `docs/tasks/active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md`  
- **Backlog position:** [`docs/tasks/INDEX.md`](../../tasks/INDEX.md) — “Current active task”

**Dependencies (from task file):** **TASK-044** (harness), **TASK-064** (tester doctrine), **TASK-053** (UCN/GDoc quality TOC). **TASK-067** (MCP prereq smokes) is optional but **recommended** before any full harness work — align with **Session init** in `tester.md`.

---

## Context not spelled out in the task file (keep this in working memory)

### Two layers: harness vs UCN

| Layer | What it is | Count |
| --- | --- | --- |
| **Harness (shell + chat)** | `scripts/e2e-test-customer.sh` + Cursor playbooks | **8 steps** (`list-steps` / `tester-e2e-ucn.md`) |
| **UCN (playbook)** | `docs/ai/playbooks/update-customer-notes.md` | **11 sub-steps** (planner, gates, write, ledger, …) |

A run can “succeed” on **`write_doc`** at the harness layer while still **omitting** UCN **Step 6** (coverage), **Step 11** (History Ledger), or a honest **`v1_partial`** declaration. **TASK-068** closes that honesty gap in **docs first**, then optional **debug artifacts**, then optional **code/CI gates**.

### UCN steps the task names explicitly

- **Step 7** — Clarification / questions. **E2E `_TEST_CUSTOMER`:** no user waits; log something like `clarification_gate: none`. **Production:** behavior unchanged.  
- **Step 9** — Write approval. **E2E:** bypass per **`.cursor/rules/11-e2e-test-customer-trigger.mdc`**; log e.g. `approval: bypassed per 11-e2e`. **Do not** fork MCP — rules + playbooks only.  
- **Step 11** — **History Ledger** after a successful write. Treat **write + ledger** as the expected chain for “honest” completion unless the task/docs define a narrow exception.

### Workflow vocabulary (`e2e_workflow`)

Delegation and **`tester.md` §4** use: `v1_full` | `v1_partial` | `v2_full` | `v2_partial` | `full`.  
- **`v1_full`:** first UCN pass is **full** (all applicable UCN sub-steps) unless a doc explicitly narrows scope.  
- **`v1_partial`:** **DAL-only** or other reduced scope is OK only with an **explicit skip list** in the tester report (avoid false green when e.g. Account Summary is empty by omission).

**Operator catalog (triggers, eight steps, modes):** from repo root, `./scripts/e2e-test-customer.sh list-catalog` (alias `list-all`). SSoT file: `scripts/lib/e2e-catalog.txt`. **Goal 6** of the task extends the **header** of that file + a short **playbook** checklist + **one** `tester.md` pointer — not a second long SSoT.

### Documentation hierarchy (avoid duplicate doctrine)

- **`.cursor/agents/tester.md`:** workflows, post-write **§6** diff, quality bar, output contract, task filing — **one** SSoT for tester behavior.  
- **`docs/ai/playbooks/update-customer-notes.md`:** UCN steps 1–11; **extend** for checklist / Step 11 / planner shape.  
- **`docs/ai/playbooks/tester-e2e-ucn.md`:** eight-step harness; E2E notes; **add** “Maintaining the E2E harness” per task Goal 6.  
- **Do not** add a second parallel “E2E policy” document; **do not** mandate `ucn-approved-mutations.json` on every run.

### Sequencing (from task; default order)

1. **Docs** — all `docs/` and `.cursor/` rows in the task’s “Files to touch” (including `e2e-catalog.txt` header and playbook maintainer section).  
2. **Debug bundle** — when implementing Goal 5: flag (`Delegation` and/or `PRESTONOTES_E2E_DEBUG=1`), path under `.../AI_Insights/e2e-debug/<ISO-datetime>/`, default **off**; optional Output Contract fields `e2e_debug`, `debug_artifact_path` in `tester.md`.  
3. **Code / CI** — optional `strict_planner_coverage` / `require_ledger` / small verifier; label **phase 1 vs phase 2** in the task file when merging.

### Session init (if the session will run **MCP, Drive, or `prep-v1`/`prep-v2`**)

Follow **Session init** in `tester.md` (hard fail before harness): `source ./setEnv.sh`, **`check_google_auth`** (prestonotes), **`wiz_docs_knowledge_base`** (wiz-remote) when relevant, Google/Drive gate. Rationale: **TASK-067** / misleading “green” without MCP.

### Verification commands (as applicable to your edits)

- Repo touch / manifests: `bash scripts/ci/check-repo-integrity.sh`  
- **After Python/MCP changes:** `bash .cursor/skills/test.sh` and `bash .cursor/skills/lint.sh` (per project norms / **code-tester**).  
- E2E harness smoke (operator): `./scripts/e2e-test-customer.sh list-catalog` (expect coherent triggers + steps + modes).  
- **Manual (task file):** debug on → `e2e-debug` tree populated; debug off → no spam (or documented empty manifest only).

---

## Acceptance (copy from task — check off as you land work)

- [ ] **Docs:** 8 harness steps vs 11 UCN sub-steps; `v1_full` vs `v1_partial` (DAL-only = partial + explicit skips); E2E = no Step 7/9 **user** pauses; prod = keep pauses.  
- [ ] **Checklist / planner:** every key section is **mutate** or **skip+reason** (no silent skip); align with `update-customer-notes.md` and existing skip language.  
- [ ] **Ledger:** playbook + tester: UCN not “done” without **Step 11** when a write applied; E2E expects ledger like prod.  
- [ ] **Debug mode:** one flag, layout as in task, default off; optional Output Contract `e2e_debug`, `debug_artifact_path`.  
- [ ] **E2E catalog maintainer contract:** `e2e-catalog.txt` header; **Maintaining the E2E harness** in `tester-e2e-ucn.md`; one **tester.md** pointer.  
- [ ] **Code (if in scope):** optional gates/script; state phase 1 vs 2 in task file when closing.  
- [ ] **Verification section** of task file (manual + `check-repo-integrity`).

**Prompts:** update [`e2e-task-execution-prompt.md`](e2e-task-execution-prompt.md) only if paths/terms are wrong — **one** pointer to `tester.md` + `e2e_debug` / `v1_partial` as needed.

---

## Copy / paste: full session instructions for the model

```text
You are working in the prestonotes repository on TASK-068.
Read the full spec: docs/tasks/active/TASK-068-e2e-debug-artifacts-mutation-ledger-trail.md
Also read: docs/ai/prompts/task-068-execution-prompt.md (this file’s repo copy) for layer context, sequencing, and verification.

Required orientation (open and use):
1) .cursor/agents/tester.md — §3 layers, §4 e2e_workflow, §6 post-write diff, “How to run and validate (operator)”, Output Contract
2) docs/ai/playbooks/tester-e2e-ucn.md — eight-step harness; will gain “Maintaining the E2E harness” per task
3) docs/ai/playbooks/update-customer-notes.md — Steps 1–11 (emphasis 6, 7, 8, 9, 10, 11)
4) .cursor/rules/11-e2e-test-customer-trigger.mdc — _TEST_CUSTOMER only; at most tighten by one short paragraph
5) scripts/lib/e2e-catalog.txt — SSoT for list-catalog; extend header per Goal 6

Rules:
- Stay inside TASK-068 goals and non-goals; do not create a second tester SSoT or a long parallel E2E architecture doc
- Default order: docs → optional debug implementation → optional code/CI; document phase 1 vs 2 in the task file
- E2E vs prod: one-sentence each where the task points; no MCP fork
- If implementing debug or running harness: respect Session init in tester.md; fail fast on MCP/Drive
- When done with substantive edits: run bash scripts/ci/check-repo-integrity.sh; if you changed Python, run .cursor/skills/test.sh and lint.sh

Deliver: (1) which acceptance bullets you satisfied, (2) files changed, (3) commands run + results, (4) what remains for TASK-068, (5) if phase-2 code is deferred, say so in the task file
```

---

## One-liner variant (after you have read the task once)

```text
Execute TASK-068 using docs/ai/prompts/task-068-execution-prompt.md + the task file: docs first (UCN checklist, ledger, E2E 7/9, v1_full/v1_partial, e2e-catalog maintainer block), then debug bundle if in scope, then optional code gates; verify with check-repo-integrity and tester.md Session init before any real harness run.
```
