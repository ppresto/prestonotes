# Simple E2E stability (updated)

## The one thing to do

**Change the contract, not the stack (first).**

- Today a run can **stop after extract** and still return `blocked` with a "resume in another session" handoff. That is **indistinguishable from a real quality gate** and is why the run felt "broken" without a "big problem."
- In [`/.cursor/agents/tester.md`](.cursor/agents/tester.md), [`.cursor/rules/11-e2e-test-customer-trigger.mdc`](.cursor/rules/11-e2e-test-customer-trigger.mdc), and a short line in [`docs/ai/playbooks/tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md):

  - **`status: success`** = steps **1 through 7** from [`scripts/lib/e2e-catalog.txt`](scripts/lib/e2e-catalog.txt) are **finished** (including both UCNs and the real `write_doc` / ledger / lifecycle work the playbook requires).
  - **Stopped early, no UCN, or not all steps done** = **`status: failed`**. **Do not use a separate `incomplete` status.**
  - **Reserve `blocked` for** Phase 1 only: env, Google auth, `check_google_auth`, call-records **lint** hard failure, or a **real** tool error after a genuine write attempt (infra / auth you cannot work around in-session).

  That is a **small doc/rules edit** and makes "stopped in the middle" a **visible failure** instead of a handoff that looks half-OK.

## What "run in main, foreground" means (operator habit)

- **Main chat** = the **primary** Cursor chat attached to the repo (the one you are in when you @ files and drive the work yourself), **not** a delegated subagent (e.g. not `/tester` in a **background** run). Subagents can hit turn limits or return early with a handoff; the main session usually has a longer, continuous run for a single thread.
- **Foreground** = you (or the agent) are **actively** running the harness in that same chat **until** steps 1–7 finish or you explicitly stop—not firing the E2E and **walking away** while a short background job tries to do extract + UCN in one go.

**In one line:** do the full **E2E Test Customer** flow **in the same top-level agent chat** and keep it the active task until the catalog is done, instead of offloading the whole thing to a background subagent that may stop mid-harness.

## Background tester + other agents calling `/tester` (today vs target)

- **Can it do that today?** **Not reliably** for the **full** `e2e_default` steps **1–7** in one background subagent run. A real run already **stopped before the first UCN** in background `/tester`, so an orchestrator that delegates the **whole** harness to background tester will see **`failed`** (once the contract is tightened) or false confidence (today). Treat **main / foreground** as the **supported** way to run the **full** harness **until** the design matures.
- **What you want as it matures:** other agents **invoke** the tester subagent **in the background** and still get a **trustworthy** pass/fail. That needs the harness to be **bounded and complete** inside a subagent budget (or split into **two** explicit delegations with a **machine check** between them), and/or **phase 2** automation: **scripted or fixture-driven UCN** on the real `write_doc` path, optional **checkpoint file**, so the **chat** part is short and the **heavy** work is shell + deterministic tools.
- **Summary:** **Today** → run **full** E2E in **main, foreground** (or accept that background **full** E2E is **experimental**). **Target** → doc contract + **failed** semantics first, then add **automation / split runs** so **background** `/tester` is a **first-class** caller.

## What we are not doing in this "simple" step

- **Not** in this first step: a new `e2e-test-customer.sh ucn-apply` from fixtures, checkpoint JSON files, or CI loops. Optional **phase 2** if you want push-button stability without a long agent.

## Todos (implementation, when you execute the plan)

- [x] Update `tester.md` Output Contract: `success` only if catalog 1–7 complete; use **`failed`** for any partial / early stop; narrow `blocked` to Phase 1 + real hard errors. **No `incomplete` status.**
- [x] Mirror the same pass/fail language in `11-e2e-test-customer-trigger.mdc`.
- [x] Add pass criteria + "main chat, foreground" note to `tester-e2e-ucn.md` (interim); add one sentence that **background full E2E** is not supported until phase 2 (or list requirements).
- [ ] **Phase 2 (separate task):** make background + orchestrator viable—scripted UCN and/or split delegations + checkpoints; document the pattern in `tester.md` / catalog.
