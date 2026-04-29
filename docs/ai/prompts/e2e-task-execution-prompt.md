# LLM prompt: E2E / `_TEST_CUSTOMER` work

**Use when:** you want a Cursor session to run or debug the **`_TEST_CUSTOMER`** harness without re-negotiating the stack. **MCP:** before deep E2E, follow **Session init** in [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) (MCP smokes + fail-fast).

---

## Read first (single source of truth)

1. [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) — workflows, post-write diff (including **§6** tab coverage and **§6.1** DAL vs transcript parity), Challenge Tracker notes when debugging lifecycle.
2. [`docs/ai/playbooks/tester-e2e-ucn.md`](../playbooks/tester-e2e-ucn.md) — step order, push/pull discipline, prep-v1 / prep-v2.
3. [`scripts/lib/e2e-catalog.txt`](../../../scripts/lib/e2e-catalog.txt) — harness step list (default E2E sequence).
4. [`docs/project_spec.md`](../../project_spec.md) **§2** (rules) and **§7** (schemas) if something is ambiguous.

**Work tracking:** use a **Cursor plan** under **`.cursor/plans/`** if you need a checklist for a long session. This repo does not use `docs/tasks/`.

---

## Copy / paste: operator block

```text
You are working in the prestonotes repository on E2E / _TEST_CUSTOMER.

1) Read: .cursor/agents/tester.md (§4–§6, §8 as needed), then docs/ai/playbooks/tester-e2e-ucn.md, then scripts/lib/e2e-catalog.txt.

2) Rules: one customer; _TEST_CUSTOMER is test data only; no fixture-only behavior in production paths; user approval before any write_doc / Drive-affecting tool; push-before-pull when the playbook says so.

3) Run the verification commands you need (pytest, harness script steps). Fix failures or state blockers exactly.

4) End with: what changed, what to run next, and whether MCP / gcloud needs human auth.
```

---

## One-liner

Follow [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) and [`tester-e2e-ucn.md`](../playbooks/tester-e2e-ucn.md); drive the shell steps via [`scripts/e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh) and the catalog in [`scripts/lib/e2e-catalog.txt`](../../../scripts/lib/e2e-catalog.txt).
