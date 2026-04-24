# Customer Notes — Daily Activity Logs tab (mutations)

> Part of the **Customer Notes** Google Doc mutation reference pack. Hub: [README.md](./README.md).

## Daily Activity Logs — allowed AI prepend

- **Section:** `daily_activity_logs` / field `free_text`.
- **Action:** `prepend_daily_activity_ai_summary` only (see `docs/ai/references/daily-activity-ai-prepend.md`).
- **Behavior:** Inserts `heading_line` (styled as Google Docs **HEADING_3**) plus formatted `body_markdown` on the **Daily Activity Logs** tab (after **Anchors** when present; date-ordered among dated blocks). No deletes, no in-place edits to existing paragraphs.
- **`Update Customer Notes` (required):** Each run must compare transcript meetings in the active lookback to existing Daily Activity content (from the latest `read` JSON). For **each meeting not already represented** (normalized heading key would not duplicate an existing block), add **`prepend_daily_activity_ai_summary`** to the **same** mutation plan as other UCN changes so one approved `write` applies everything. If there are no gaps, omit prepend mutations and say so in the plan summary. A mutations file that contains **only** prepend actions still bypasses planner key-field coverage; mixed files must still satisfy key-field `no_evidence` / change coverage.

---
