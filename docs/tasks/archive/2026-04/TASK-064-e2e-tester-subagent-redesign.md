# TASK-064 — Lean E2E tester: one mental model, minimal files

**Status:** [x] **DONE** — **consolidation shipped 2026-04-24** (E2E doctrine in **`.cursor/agents/tester.md`**, `docs/e2e/` **retired**; **`docs/E2E_TEST_CUSTOMER_GUIDE.md` retired 2026-04-23** — same role as **`/tester`** + `tester-e2e-ucn.md`; do not reintroduce)  
**Opened:** 2026-04-24  
**Depends on:** **TASK-044**, **TASK-053**; coordinate **`.cursor/rules/core.mdc`** (default inline habits) and archived subagent packet templates in **`docs/archive/cursor-rules-retired/workflow.mdc`**, **`.cursor/rules/11-e2e-test-customer-trigger.mdc`**.

**Shipped (naming, 2026-04-24):** Subagent **`/tester`** = **`_TEST_CUSTOMER`** E2E harness (`.cursor/agents/tester.md`). Subagent **`/code-tester`** = unit/CI after **`/coder`** (`.cursor/agents/code-tester.md`). At the time, an optional isolated implementation pipeline was documented as **`/coder` → `/code-tester` → `/doc`** (packet templates now archived in **`docs/archive/cursor-rules-retired/workflow.mdc`**). **Current repo default:** inline engineering in the main chat per **`.cursor/rules/core.mdc`**. See **`.cursor/agents/tester.md`** for playbooks vs rules (E2E procedure layers stay in repo playbooks; rules stay invariant).

**Shipped (playbook rename, 2026-04-24):** **`tester-` E2E playbooks** — `e2e-test-customer.md` → **`tester-e2e-ucn.md`** (eight-step harness; H1 *Tester E2E — `_TEST_CUSTOMER` harness*); `e2e-troubleshoot-ucn-gdoc.md` → **`tester-e2e-ucn-debug.md`** (staged UCN↔GDoc diff). *`ucn` in the first filename is legacy shorthand; content is the full eight-step harness, not UCN-only.*

### Inventory — `/tester` and related (simplify in later PRs)

| Kind | Path | Name fit? | Simplification idea |
| --- | --- | --- | --- |
| **Playbook (procedural, `/tester`)** | `docs/ai/playbooks/tester-e2e-ucn.md` | OK; consider **`tester-e2e-harness.md`** if `ucn` confuses. | Optional rename only. |
| **Playbook (debug, `/tester`)** | `docs/ai/playbooks/tester-e2e-ucn-debug.md` | **Yes** — UCN vs GDoc staged runs. | Keep. |
| **E2E narrative SSoT** | ~~`docs/e2e/tester-playbook.md`~~ | *(retired 2026-04)* | **Merged into `.cursor/agents/tester.md`**; file **deleted**. |
| **Hub** | ~~`docs/e2e/README.md`~~ | *(retired)* | **Deleted**; `INDEX` + agent + playbooks point here. |
| **Rule (always on)** | `.cursor/rules/11-e2e-test-customer-trigger.mdc` | Triggers + eight-step *contract*; filename says `e2e` not `tester`. | Optional rename to `11-tester-e2e-trigger.mdc` — **low value**; many cross-links. |
| **Override glue** | `.cursor/rules/20-orchestrator.mdc`, `21-extractor.mdc`, `core.mdc` (E2E override bullets) | Accurate. | No rename; they cite `tester-e2e-ucn.md`. |
| **Prompts** | `e2e-task-execution-prompt.md`, `kick-off-next-task-session.md` | Filename unchanged. | **Updated** to **`.cursor/agents/tester.md`** + `tester-e2e-ucn.md` + `INDEX` (no duplicate doctrine). |
| **Stub** | ~~`docs/E2E_TEST_CUSTOMER_GUIDE.md`~~ | *(retired 2026-04-23)* | **Deleted** — use **`.cursor/agents/tester.md`** + `tester-e2e-ucn.md` only. |
| **Unit** | `.cursor/agents/code-tester.md` + **`.cursor/skills/test.sh`**, **`lint.sh`** | **`code-tester`** = Python/CI, **not** E2E. | No change. |
| **Product playbooks** | `update-customer-notes.md`, `extract-call-records.md`, `run-account-summary.md`, `load-customer-context.md` | **Shared** with production agent; not `tester-*` prefixed. | Correct — do **not** rename; `/tester` *invokes* them as steps, not re-owns them. |
| **Shell (not a playbook)** | `scripts/e2e-test-customer.sh` | Name tied to **script** and TASK history. | **Do not** rename to `tester-*.sh` without a dedicated task (breaks muscle memory + many refs). |

**Grep anchors for future cleanup:** `docs/e2e/`, `E2E_TEST_CUSTOMER_GUIDE` *(should be zero)*, `e2e-task-execution-prompt`, `11-e2e-test-customer-trigger`.

---

## Agreement gate (historical)

Consolidation **landed 2026-04-24**. The “smallest set” to run E2E is: **`tester-e2e-ucn.md`** (steps) + **`.cursor/agents/tester.md`** (quality / diff) + **`11-e2e-test-customer-trigger.mdc`** (trigger + invariants). Optional: **`tester-e2e-ucn-debug.md`** for staged UCN↔GDoc work.

---

## Problem

E2E guidance is **split across too many surfaces**, which is confusing when building a **lean** `_TEST_CUSTOMER` tester:

| File | Role today (overlapping) |
| --- | --- |
| `.cursor/rules/11-e2e-test-customer-trigger.mdc` | Triggers, eight-step contract, hard rules, lint gate, artifact hygiene |
| `docs/e2e/tester-playbook.md` | Vision, modes, diff, tasks, artifacts, rules (duplicates trigger + playbook) |
| `docs/e2e/README.md` | Hub pointing at the above |
| `docs/ai/prompts/e2e-task-execution-prompt.md` | TASK-053/044 order + copy-paste block (again cites e2e docs) |
| `docs/ai/prompts/kick-off-next-task-session.md` | Another pointer into e2e docs |
| `docs/ai/playbooks/bootstrap-customer.md` | E2E cross-links |
| `docs/ai/playbooks/tester-e2e-ucn.md` | Eight steps, prerequisites, checklist (correct layer for *procedure*) |
| ~~`docs/E2E_TEST_CUSTOMER_GUIDE.md`~~ | *(retired)* — **`.cursor/agents/tester.md`** + playbooks |

The **`/tester`** subagent (`.cursor/agents/tester.md`) already loads **rules** and **repo context**; it does **not** need three parallel “canonical” prose docs that repeat the same gates.

---

## Goal (after agreement)

One **obvious** story for contributors:

1. **How do I run the eight-step harness?** → one playbook-shaped doc.  
2. **What must the main agent never violate on reserved triggers?** → one short **always-on** rule.  
3. **What does the `/tester` subagent load for diff / modes / task filing?** → **one** subagent-local spec (acceptable if long **only** in `.cursor/agents/tester.md`, because it is not `alwaysApply`).

---

## Proposed end state (recommended — for sign-off)

### Three files (lean)

| # | File | Contents (no duplication) |
| --- | --- | --- |
| **1** | `docs/ai/playbooks/tester-e2e-ucn.md` | **Procedure only:** prerequisites, eight steps (shell vs chat), `prep-v1`/`prep-v2` parity, debugger `list-steps` / `run-step`, optional `reset`, **manual checklist after step 8**. One line at top: “Behavioral contract + diff + task filing: `.cursor/agents/tester.md` (invoke `/tester`).” |
| **2** | `.cursor/rules/11-e2e-test-customer-trigger.mdc` | **Invariants only** (keep short; `alwaysApply: true`): trigger phrases, `_TEST_CUSTOMER` scope, must run all 8 steps in order, no fake outputs, no approval stops on trigger, **lint before UCN**, artifact hygiene bullets, pointer to **(1)** for step detail. **No** full diff template here. |
| **3** | `.cursor/agents/tester.md` | **Tester doctrine:** vision (short), link `project_spec.md` §1–2 / §6–7 / §9 when filing tasks, workflow modes (`v1_full` …), post-write **delta table** template + inputs, forbidden `tmp/` shortcuts, task lifecycle + INDEX, symptom→layer for Challenge Tracker, file reference table, **Output Contract**, playbooks vs rules (see body). *Merge the body of today’s `docs/e2e/tester-playbook.md` here, then delete `docs/e2e/tester-playbook.md`.* |

### Remove / collapse *(executed 2026-04-24)*

| Path | Action |
| --- | --- |
| `docs/e2e/tester-playbook.md` | **Deleted** after merge into **(3)** |
| `docs/e2e/README.md` | **Deleted** (no separate hub) |
| ~~`docs/E2E_TEST_CUSTOMER_GUIDE.md`~~ | **Deleted** (replaced by **tester** agent + `tester-e2e-ucn.md`) |
| `docs/ai/prompts/e2e-task-execution-prompt.md` | **Replace** with a **short** note: preferred TASK order + “read active task file + `tester-e2e-ucn.md` + `INDEX`” — **no** second copy of E2E doctrine |
| `docs/ai/prompts/kick-off-next-task-session.md` | **One line** for E2E: `tester-e2e-ucn.md` + task file |
| `docs/ai/playbooks/bootstrap-customer.md` | **One line** to step 1 of `tester-e2e-ucn.md` (drop `docs/e2e/` links) |

### Other files (touch only if needed)

- **`docs/archive/cursor-rules-retired/workflow.mdc`**: **`/tester`** (E2E) vs **`/code-tester`** (unit) — path references to agent files updated when consolidation lands. (Note: this file was later moved out of **`.cursor/rules/`** so it is not always-on.)
- **`required-paths.manifest`**: keep agent paths (`tester`, `code-tester`, `coder`, `doc`) in sync.
- **Active tasks (044, 053, 063, INDEX)**: update links to the three-file model.
- **Archived tasks**: optional follow-up (low priority) to fix dead links; not blocking.

### Rationale: does the E2E **`/tester`** agent “need more” (playbooks vs rules only)?

**No third canonical markdown tree under `docs/e2e/`** long term. The subagent already sees **rules** (`11`, `20`, `21`, …). For **code** after **`/coder`**, use **`/code-tester`**, not **`/tester`**. **Playbooks** (`tester-e2e-ucn.md`, `tester-e2e-ucn-debug.md`) are **on-demand procedure** — step order, staged UCN↔GDoc debug — *not* duplicates of the rules. Heavy harness rubric (diff, modes) may live in **`.cursor/agents/tester.md`** after merge of `tester-playbook.md`.

---

## Operator decision (resolved 2026-04-24)

- [x] **Three-surface model:** procedure **`tester-e2e-ucn.md`**, doctrine **`.cursor/agents/tester.md`**, invariants **`11-e2e-test-customer-trigger.mdc`**.
- [x] **`docs/e2e/`** files removed; **`E2E_TEST_CUSTOMER_GUIDE.md`** **removed** (2026-04-23) — SSoT is **`.cursor/agents/tester.md`** + E2E playbooks.
- [x] **`e2e-task-execution-prompt.md`** and **`kick-off-next-task-session.md`** point at agent + playbook (no long duplicate).

---

## Workflow catalog (unchanged semantics; doc refs update after merge)

Orchestrator passes exactly one **`e2e_workflow`**:

| Mode | Scope | Mandatory post-run |
| --- | --- | --- |
| **`v1_full`** | Steps 1–4: `prep-v1` (rebaseline) → Load → Extract → **lint 0** → UCN → `read_doc` → **post-write diff** | Diff **required** before “green” |
| **`v1_partial`** | Subset; orchestrator passes `partial_phase` | Mini diff + “not run” list |
| **`v2_full`** | Steps 5–7 after round 1 | Diff + round-2 delta focus |
| **`v2_partial`** | Narrow | Mini diff + disclaimers |
| **`full`** | All 8 incl. Account Summary | Diff after **each** UCN |

*(After agreement, section anchors may live in `.cursor/agents/tester.md` headings — no `docs/e2e/` §6 references if playbook is merged away.)*

---

## Acceptance — implementation (shipped 2026-04-24)

- [x] **`.cursor/agents/tester.md`** — merged E2E doctrine (former `tester-playbook.md`), Output Contract, read order.
- [x] **`tester-e2e-ucn.md`** — procedure + top link to **`.cursor/agents/tester.md`**.
- [x] **`11-e2e-test-customer-trigger.mdc`** — **SSoT pointer** to **`.cursor/agents/tester.md` §6** (post-write diff); no full duplicate template in rule *(optional follow-up: further trim if rule feels long — non-blocking)*.
- [x] **`docs/e2e/`** — both files and directory **removed**; `required-paths.manifest` updated.
- [x] **`docs/E2E_TEST_CUSTOMER_GUIDE.md`** — **retired** (replaced by **tester** subagent + `tester-e2e-ucn.md` / `tester-e2e-ucn-debug.md`).
- [x] **`e2e-task-execution-prompt.md`**, **`kick-off-next-task-session.md`**, **`bootstrap-customer`**, **workflow** — updated.
- [x] **INDEX** + related tasks **cross-consistent** with the above.

## Verification (after implementation)

- New contributor reads **only** `tester-e2e-ucn.md` + `.cursor/agents/tester.md` + `11-e2e-test-customer-trigger.mdc` and can name lint gate + step order + where diff template lives.
- `scripts/ci/check-repo-integrity.sh` passes.

## Related

- **`.cursor/agents/code-tester.md`** — unit path after `/coder` (`/code-tester`).
- **TASK-044**, **TASK-053** — consume updated links after merge.

## Notes

- If the operator prefers **playbook** to hold the long diff template instead of the agent file, say so in approval — task then swaps **(1)** vs **(3)** boundaries but still targets **one** long + **one** short + trigger rule.
