# Customer Notes — Daily Activity Logs tab (mutations)

> Part of the **Customer Notes** Google Doc mutation reference pack. Hub: [README.md](./README.md).

## Daily Activity Logs — allowed AI prepend

- **Section:** `daily_activity_logs` / field `free_text`.
- **Action:** `prepend_daily_activity_ai_summary` only (see `docs/ai/references/daily-activity-ai-prepend.md`).
- **Behavior:** Inserts `heading_line` (styled as Google Docs **HEADING_3**) plus formatted `body_markdown` on the **Daily Activity Logs** tab (after **Anchors** when present; date-ordered among dated blocks). No deletes, no in-place edits to existing paragraphs.
- **`Update Customer Notes` (required):** Each run must compare transcript meetings in the active lookback to existing Daily Activity content (from the latest `read` JSON). For **each meeting not already represented** (normalized heading key would not duplicate an existing block), add **`prepend_daily_activity_ai_summary`** to the **same** mutation plan as other UCN changes so one approved `write` applies everything. If there are no gaps, omit prepend mutations and say so in the plan summary. A mutations file that contains **only** prepend actions still bypasses planner key-field coverage; mixed files must still satisfy key-field `no_evidence` / change coverage.
- **TASK-072 deterministic contract:** include `planner_contract.dal` in the same JSON:
  - `expected_missing_count` (int),
  - `expected_missing_keys` (`YYYY-MM-DD:<slug>` list),
  - optional `skips` with `{meeting_key, reason}`.
  Run `scripts/ucn-planner-preflight.py` before write; if DAL parity fails (`dal_parity_failed`), do not call `write_doc`.
- **Full UCN bundle** (all targets, Step 10, optional E2E writer preview): **[`docs/ai/playbooks/update-customer-notes.md`](../playbooks/update-customer-notes.md)** (and E2E-only preview in [`tester-e2e-ucn.md`](../playbooks/tester-e2e-ucn.md)).

---
