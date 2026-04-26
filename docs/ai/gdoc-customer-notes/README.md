# Customer Notes (Google Doc) — mutation docs hub

**Customer Notes** is the product name of the **single** per-customer Google Doc this repo updates today (`<Customer> Notes`). It currently has **three** tabs; more tabs may be added later—extend the tables below in the same PR as `prestonotes_gdoc/config/doc-schema.yaml` and writer changes.

| Layer | Role | Canonical path |
| --- | --- | --- |
| **Shape** | Tab/section/field keys, parser strategies | `prestonotes_gdoc/config/doc-schema.yaml` |
| **Meaning** | What to write, rubrics, routing, quality gates | **This directory** (`mutations-*.md`) |
| **Process** | UCN / extract steps, approvals | `docs/ai/playbooks/update-customer-notes.md` |

## SSoT: section semantics

Use one semantic home per tab and keep process/rules as pointers:

| If you are changing... | Authoritative file | Other files should do |
| --- | --- | --- |
| Account Summary section meaning (Goals/Risk/Upsell intent, Contacts evidence, Cloud routing rubric, Challenge Tracker semantics) | `mutations-account-summary-tab.md` | Playbooks/rules link to this file instead of restating full rubric text. |
| Account Metadata strictness and numeric evidence requirements | `mutations-account-metadata-tab.md` | Keep playbooks/rules to workflow pointers and invariants. |
| Daily Activity prepend behavior | `mutations-daily-activity-tab.md` | Keep DAL formatting details in references linked from that tab doc. |
| Cross-tab mechanics (actions matrix, JSON schema, quality gate, planner guard) | `mutations-global.md` | Do not copy per-section prose here. |
| UCN execution order / approvals | `docs/ai/playbooks/update-customer-notes.md` | Link back to the tab docs for section semantics. |

## Mutation reference files (edit here when tuning writes)

| File | Scope |
| --- | --- |
| [mutations-account-summary-tab.md](./mutations-account-summary-tab.md) | **Account Summary** tab: fact-extraction categories, section intents (Goals/Risk/Upsell, Contacts, Cloud `tools_list`, Use cases, Workflows, …), Challenge lifecycle ↔ Challenge Tracker, Challenge decision model, Deal Stage promotion rules. |
| [mutations-daily-activity-tab.md](./mutations-daily-activity-tab.md) | **Daily Activity Logs** tab: `prepend_daily_activity_ai_summary` only; points to `daily-activity-ai-prepend.md`. |
| [mutations-account-metadata-tab.md](./mutations-account-metadata-tab.md) | **Account Metadata** tab: `account_motion_metadata` strictness and numeric fields. |
| [mutations-global.md](./mutations-global.md) | **Cross-tab**: mutation actions matrix, JSON schema, core rules, historical synthesis, executive presentation / `replace_field_entries`, planner coverage guard, quality gate, History Ledger integration, diff preview format. |

## Related references (unchanged paths)

- `docs/ai/references/daily-activity-ai-prepend.md` — DAL body format (referenced from Daily Activity tab doc).
- `docs/ai/references/customer-data-ingestion-weights.md` — transcript vs doc weights for UCN.
- `docs/ai/references/granola-meeting-summary-templates.md` — meeting recap shapes.
- `docs/ai/references/gdoc-section-changes-v2.md` — section naming / migration notes (if still in use).

## Legacy index path

`docs/ai/references/customer-notes-mutation-rules.md` is now a **short index** that points here. Update deep links in bookmarks to this README or to the specific `mutations-*.md` file.

## Tab → doc-schema `section_key` (quick map)

| Google Doc tab | Primary `section_key` values (non-exhaustive) |
| --- | --- |
| Account Summary | `exec_account_summary`, `challenge_tracker`, `deal_stage_tracker`, `company_overview`, `contacts`, `org_structure`, `cloud_environment`, `use_cases`, `workflows`, `accomplishments`, `discovery`, `appendix` |
| Daily Activity Logs | `daily_activity_logs` |
| Account Metadata | `account_motion_metadata` |

Parser/writer tab routing is implemented in `prestonotes_gdoc/update-gdoc-customer-notes.py` (multiple tabs → merged section map).
