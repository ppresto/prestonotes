# TASK-063 — GDoc mutation docs: Customer Notes hub + per-tab packs

**Status:** [x] Done (2026-04-24)  
**Opened:** 2026-04-24  
**Depends on:** None (documentation / information architecture; coordinate with **TASK-053** / **TASK-057–062** when tuning a tab).

## High-level overview (what shipped)

**Customer Notes** is the product name for the **single** per-customer Google Doc updated by UCN today. Mutation **meaning** (rubrics, routing, quality gate prose) was previously one large file, `docs/ai/references/customer-notes-mutation-rules.md`, which was hard to navigate and painful to edit when tuning **one tab or section**.

**Proposal (implemented):**

1. **Canonical hub** — [`docs/ai/gdoc-customer-notes/README.md`](../../ai/gdoc-customer-notes/README.md) maps tabs → `section_key` / files → `doc-schema.yaml` / playbooks. Subfolders under `gdoc-customer-notes/` are **deferred** until volume justifies them; all mutation markdown for this GDoc lives **flat** under this path for now.

2. **Per-tab / per-scope mutation packs** — split content so editors can open **only** the file for the surface they are testing:
   - [`mutations-account-summary-tab.md`](../../ai/gdoc-customer-notes/mutations-account-summary-tab.md) — Account Summary: fact extraction, exec summary / contacts / cloud / workflows / challenge lifecycle & tracker / deal stage.
   - [`mutations-daily-activity-tab.md`](../../ai/gdoc-customer-notes/mutations-daily-activity-tab.md) — Daily Activity Logs (`prepend_daily_activity_ai_summary` + link to `daily-activity-ai-prepend.md`).
   - [`mutations-account-metadata-tab.md`](../../ai/gdoc-customer-notes/mutations-account-metadata-tab.md) — Account Metadata strictness.
   - [`mutations-global.md`](../../ai/gdoc-customer-notes/mutations-global.md) — Cross-tab: actions matrix, JSON schema, core rules, synthesis modes, planner guard, quality gate, ledger, diff preview.

3. **Legacy index (stable URL)** — [`docs/ai/references/customer-notes-mutation-rules.md`](../../ai/references/customer-notes-mutation-rules.md) is a **short redirect table** to the hub and packs so old bookmarks and external links do not 404.

4. **Rewire** — Playbooks (especially `update-customer-notes.md`), **`.cursor/agents/tester.md`** (E2E), `project_spec.md`, `.cursor/rules` (orchestrator, extractor, core), Python docstrings that cited the monolith, CI `required-paths.manifest`, and related tasks now cite **`docs/ai/gdoc-customer-notes/`** (hub or the specific `mutations-*.md` file).

**Unchanged mental model (three layers):**

| Layer | Role | Canonical location |
| --- | --- | --- |
| **Shape** | Tabs, sections, fields, parser strategies | `prestonotes_gdoc/config/doc-schema.yaml` |
| **Meaning** | Rubrics, routing, forbidden text, mutation prose | `docs/ai/gdoc-customer-notes/` (`README.md` + `mutations-*.md`) |
| **Process** | UCN steps, approvals, coverage tables | `docs/ai/playbooks/update-customer-notes.md` |

## Problem (original)

Multiple Google Doc tabs (Account Summary, DAL, Account Metadata) and a growing section set made a **single monolithic** mutation reference difficult to maintain and review.

## Non-goals

- No change to UCN **code** behavior solely because docs moved.
- No replacement of `doc-schema.yaml` with markdown.

## Acceptance

- [x] Hub **`docs/ai/gdoc-customer-notes/README.md`** exists; describes one GDoc today, three tabs, extension rule.
- [x] Per-tab / global **`mutations-*.md`** packs exist; monolith content split (legacy path is index only).
- [x] **`docs/ai/playbooks/update-customer-notes.md`** and **`.cursor/agents/tester.md`** cite the hub and/or the correct pack.
- [x] **`scripts/ci/required-paths.manifest`** includes hub + packs + legacy index.
- [x] **`docs/tasks/INDEX.md`** line reflects the hub path (not `docs/ai/gdoc/README.md`).

## Verification

- Spot-check: `rg customer-notes-mutation-rules` — remaining hits should be **index stub**, **historical archive tasks**, or intentional mentions of the stub path in `project_spec` / README.
- `./scripts/ci/check-repo-integrity.sh` (or CI) passes after manifest update.

## Related tasks

- **TASK-053** — GDoc fill / E2E quality TOC.  
- **TASK-057–062** — Component tuning; when editing mutation meaning for a tab, prefer the matching **`mutations-*-tab.md`** (and update the hub table if `section_key` or tab layout changes).

## Notes for future work (optional)

- CI drift check: `section_key` in `doc-schema.yaml` vs rows in hub `README.md`.
- Subfolders under `gdoc-customer-notes/` if file count grows (e.g. `account-summary/`).
