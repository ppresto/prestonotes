# Playbook: Bootstrap customer (v2 stub)

Trigger: **`Bootstrap Customer`** (MCP **`bootstrap_customer`**) or manual folder creation.

This v2 stub documents **customer folder + History Ledger lifecycle** aligned with **TASK-023**. Full Google Doc bootstrap flows remain under **`docs/MIGRATION_GUIDE.md`** and MCP **`bootstrap_customer`**.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

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
- **E2E reset:** The `_TEST_CUSTOMER` E2E flow (TASK-044) hard-deletes the customer folder (local + Drive) and re-runs `bootstrap_customer`, so the ledger is absent after reset and gets created lazily on the first approved `append_ledger_row`.

## 3) Google Docs (separate)

Doc discovery and mutations use **`discover_doc`**, **`read_doc`**, **`write_doc`** per **`docs/ai/playbooks/update-customer-notes.md`**. This playbook does not replace those steps.

## 4) References

- **`docs/MIGRATION_GUIDE.md`** — ledger migration, lazy create
- **`docs/tasks/archive/2026-04/TASK-023-history-ledger-lazy-bootstrap.md`** — archived task definition
