# Playbook: Bootstrap customer (v2 stub)

Trigger: **`Bootstrap Customer`** (MCP **`bootstrap_customer`**) or manual folder creation.

This v2 stub documents **customer folder + History Ledger lifecycle** aligned with **TASK-023**. Full Google Doc bootstrap flows remain under **`docs/MIGRATION_GUIDE.md`** and MCP **`bootstrap_customer`**.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

## One-time bootstrap vs E2E `prep-v1` vs nuclear `reset` ([TASK-052](../../tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md))

Do **not** conflate these three. Pick **one** path for the situation:

| What you need | When to use it | Notes Google Doc | See also |
| --- | --- | --- | --- |
| **A. `bootstrap_customer` (one-time)** | **No** `Customers/<Name>/` on Drive (or no `_Name Notes` yet). First real scaffold: folder, stub files, and a **new** Notes doc by **copying** the template (Drive API). | A **new** file is created; `doc_id` comes from **`discover_doc`** after **`sync_notes`**. | This playbook + `prestonotes_gdoc/000-bootstrap-gdoc-customer-notes.py` (invoked by MCP). |
| **B. E2E `prep-v1` (repeatable, same customer)** | **`_TEST_CUSTOMER`** (or any customer) **already** has a folder and Notes doc; you are **re-seeding** the E2E fixture or **resetting the doc body to the template** without a new file id. | **Same** `doc_id` kept; body replaced by E2E-only `e2e_rebaseline_customer_gdoc.py` (unless `prep-v1 --skip-rebaseline`). | [`tester-e2e-ucn.md`](tester-e2e-ucn.md) — step 1; shell: [`e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh) `prep-v1` (workflow modes: [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) §4). |
| **C. Nuclear `reset` + bootstrap** | You **deleted** the whole customer tree (Drive + local) — corrupt state, or intentional full greenfield. | After trash/wipe, run **A** again; you get a **new** Notes `doc_id`. Then run E2E [`prep-v1`](tester-e2e-ucn.md) (or `prep-v1 --skip-rebaseline` if the doc from bootstrap is already template-shaped). | [`tester-e2e-ucn.md`](tester-e2e-ucn.md) “Optional: nuclear reset”; shell: [`e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh) `reset` then `Bootstrap Customer for _TEST_CUSTOMER` then `prep-v1` / `prep-v1 --skip-rebaseline`. |

**Rule of thumb:** use **`bootstrap_customer`** when the **folder or doc does not exist**. Use **`./scripts/e2e-test-customer.sh prep-v1`** for **E2E re-runs** when the doc **already exists** and you only need a template-aligned body + local seed + push. Use **`reset` + bootstrap** only for **delete-the-world** recovery.

---

## Communication rule

Follow **`.cursor/rules/15-user-preferences.mdc`**. Show plans before writes; use MCP **`dry_run=true`** until the user approves.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`** for the final response shape.
- After any multi-step run, include a **`### Activity recap`** section with completed work, skipped/deferred items, and next action.
- Explicitly state whether any write-capable step was executed or intentionally not executed.

---

## 1) On-disk customer root

- Canonical mirror: **`MyNotes/Customers/<Customer>/`**
- MCP **`bootstrap_customer`** can scaffold folders; **`sync_notes`** pulls from Drive when configured.

## 2) History Ledger v3 (lazy create)

- **Path:** **`MyNotes/Customers/<Customer>/AI_Insights/<Customer>-History-Ledger.md`**
- **Greenfield:** the ledger file may be **absent** until the first successful **`append_ledger_row`** — the MCP path creates an empty **20-column** `schema_version: 3` table, then appends the row.
- **`read_ledger`:** returns an **`empty`** JSON shape when **`AI_Insights/`** exists but the ledger file does not (see **`docs/MIGRATION_GUIDE.md`** §History Ledger v3).
- **E2E nuclear path:** A full [E2E `reset`](tester-e2e-ucn.md) (see [`e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh) `reset`) trashes the customer folder (local + Drive) **only when** the operator opts in. After that, `bootstrap_customer` (or a fresh bootstrap) recreates the tree; the ledger is absent until the first approved **`append_ledger_row`**. The **default** E2E loop ([TASK-052](../../tasks/archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) §0) is **`prep-v1` / `prep-v2`** on an **existing** customer — no delete each run.

## 3) Google Docs (separate)

Doc discovery and mutations use **`discover_doc`**, **`read_doc`**, **`write_doc`** per **`docs/ai/playbooks/update-customer-notes.md`**. This playbook does not replace those steps.

## 4) References

- [`tester-e2e-ucn.md`](tester-e2e-ucn.md) — eight-step E2E for `_TEST_CUSTOMER` (shell: [`../../../scripts/e2e-test-customer.sh`](../../../scripts/e2e-test-customer.sh))
- [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) — E2E tester doctrine; when `prep-v1` runs vs `bootstrap`
- **`docs/MIGRATION_GUIDE.md`** — ledger migration, lazy create
- **`docs/tasks/archive/2026-04/TASK-023-history-ledger-lazy-bootstrap.md`** — archived task definition
