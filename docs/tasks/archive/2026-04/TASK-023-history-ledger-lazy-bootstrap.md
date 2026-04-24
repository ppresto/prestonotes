# TASK-023 — History Ledger: lazy create (align with legacy bootstrap)

**Status:** `[x] DONE` (archived 2026-04-20)  
**Type:** behavior + docs (customer lifecycle)  
**Legacy reference (sibling repo `../prestoNotes.orig/` on your machine):**

- `docs/ai/playbooks/bootstrap-customer.md` §**2d) History Ledger scaffold (headers only)** — ledger path `AI_Insights/[Customer]-History-Ledger.md`; if the file already exists, skip; first **Update Customer Notes** appends the first row.
- `custom-notes-agent/update-gdoc-customer-notes.py` — **`cmd_ledger_append` / `ledger-append`**: if `ledger_local` does not exist, **create** file (YAML + header + first data row).

## Problem

1. **Legacy contract:** On bootstrap, the History Ledger was optional until created: either a **headers-only** scaffold (“first `Update Customer Notes` will append the first row”) or **no file** until the first successful **`ledger-append`**, which **created** the file if missing.
2. **Current v2 MCP:** [`prestonotes_mcp/ledger_v2.py`](../../../../prestonotes_mcp/ledger_v2.py) **`append_ledger_v2_row`** requires the ledger file to **already exist** (`FileNotFoundError` if missing), which contradicts lazy creation.
3. **`refresh_test_customer.py`:** Always **copies the full template ledger** (including template data rows, after string replace `_TEMPLATE` → customer). That is useful for **E2E reset**, but it is **not** the same as “ledger appears only after first UCN / insight write.” It also encourages drift if Drive still has a **root-level** `Customer-History-Ledger.md` (pre–`AI_Insights/` layout); refresh already deletes that legacy path locally—see script docstring—but rsync from Drive can reintroduce it until Drive is cleaned up.

## Goal

Restore the **intent** of the old model (without breaking v2 column rules):

- **Greenfield customers:** `AI_Insights/<Customer>-History-Ledger.md` may be **absent** until the first append that should persist history.
- **First append:** MCP (or shared helper used by `ledger-append` / `append_ledger_v2`) **creates** a valid **v2** ledger document (YAML + **24-column** header + optional zero body rows—whatever `detect_standard_table_column_count` / `append_ledger_v2` require).
- **`read_ledger`:** Returns a structured “empty / no ledger yet” when the folder exists but the file does not—instead of only `"no ledger file"` as today, if product wants friendlier UX (optional sub-item).

## Non-goals

- Changing **Google Doc** creation flow (separate bootstrap port if `bootstrap-customer.md` is reintroduced).
- Rewriting **v1** `ledger-append` behavior beyond keeping parity with v2 where both exist.

## Implementation sketch

1. Add **`ensure_v2_ledger_stub(customer_name)`** (or equivalent) in [`prestonotes_mcp/ledger_v2.py`](../../../../prestonotes_mcp/ledger_v2.py) that writes the **canonical empty v2** markdown (same structure as post-**[`migrate_ledger`](../../../../prestonotes_mcp/tools/migrate_ledger.py)** file, **no data rows** under the standard table).
2. **`append_ledger_v2_row`:** If ledger missing → call stub creator, then append row (single transaction from caller’s perspective).
3. **Tests:** [`prestonotes_mcp/tests/test_ledger_v2.py`](../../../../prestonotes_mcp/tests/test_ledger_v2.py) — new case: no file → append succeeds → file exists with one row.
4. **`refresh_test_customer.py`:** Add a mode (flag or default policy—**product decision**) such as:
   - **`--ledger greenfield`:** remove `*-History-Ledger.md` under `AI_Insights/` and **do not** copy from `_TEMPLATE` (E2E “no ledger until first write”), **or**
   - **`--ledger copy-template`:** current behavior (explicitly documented as “simulates customer who already completed bootstrap with template baseline row”).
5. **Docs:** [`docs/MIGRATION_GUIDE.md`](../../../../docs/MIGRATION_GUIDE.md) + [`docs/ai/playbooks/update-customer-notes.md`](../../../../docs/ai/playbooks/update-customer-notes.md) one paragraph: ledger lifecycle vs bootstrap; link this task.

## Acceptance criteria

- [x] First successful **`append_ledger_v2`** for a customer with **no** ledger file creates **`AI_Insights/<Customer>-History-Ledger.md`** with a valid v2 table and the new row.
- [x] No regression for customers with an existing v2 ledger (append still works; migration tool unchanged or called only when columns wrong).
- [x] `refresh_test_customer` behavior documented; E2E doc/playbook updated if default changes. *(Default unchanged: **`--ledger copy-template`**; greenfield documented in script help + **`docs/MIGRATION_GUIDE.md`**.)*
- [x] Optional: stub **`bootstrap-customer.md`** in v2 repo referencing this lifecycle — **`docs/ai/playbooks/bootstrap-customer.md`**.

## Evidence (implementation)

- Commands: `uv run pytest prestonotes_mcp/tests/test_ledger_v2.py`; `uv run ruff check prestonotes_mcp/ledger_v2.py prestonotes_mcp/server.py scripts/refresh_test_customer.py`
- Outcome: **6 passed**; Ruff **All checks passed!**

## Related paths

- Current reset: [`scripts/refresh_test_customer.py`](../../../../scripts/refresh_test_customer.py) (copies template ledger; removes legacy **root** `Customer-History-Ledger.md`).
- v1 create path (still in tree): [`prestonotes_gdoc/update-gdoc-customer-notes.py`](../../../../prestonotes_gdoc/update-gdoc-customer-notes.py) `cmd_ledger_append` (~5026).
