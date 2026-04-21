# TASK-033 — LLM response format: plain language + activity recap

**Status:** [x] COMPLETE  
**Opened:** 2026-04-21  
**Legacy Reference:** `../prestoNotes.orig/.cursor/rules/15-user-preferences.mdc` (v1 **Response format**, **Forbidden words**, **How to talk**, **numbered steps**); v2 **`.cursor/rules/15-user-preferences.mdc`**.

## Goal

Make long, accurate agent replies **easy to scan**: keep detailed prose when needed, but always add a **short activity recap** and use **simple language** rules from v1 so users can dig deeper from a clear table of contents.

## Done (2026-04-21)

- [x] Ported v1 rules into **`.cursor/rules/15-user-preferences.mdc`**: step prefix, pre-write summary, post-run “what changed / skipped”, forbidden-word table, numbered “what did you do”, **`### Activity recap`** requirement for long replies.
- [x] **`.cursor/rules/workflow.mdc`** — **doc** subagent row now requires following **`15-user-preferences`** on doc deliverables.

## Remaining

- [x] Audit customer-facing playbooks under **`docs/ai/playbooks/`** and add **“End-of-run chat format”** sections that point to **`15-user-preferences.mdc`** and require **`### Activity recap`** after multi-step work.
- [x] Added the same reminder to **`.cursor/rules/core.mdc`** for customer-note flows.

## Output / Evidence

- Diff: `.cursor/rules/15-user-preferences.mdc`, `.cursor/rules/workflow.mdc`
- Playbook updates:
  - `docs/ai/playbooks/bootstrap-customer.md`
  - `docs/ai/playbooks/load-product-intelligence.md`
  - `docs/ai/playbooks/load-customer-context.md`
  - `docs/ai/playbooks/run-account-summary.md`
  - `docs/ai/playbooks/update-customer-notes.md`
  - `docs/ai/playbooks/run-license-evidence-check.md`
  - `docs/ai/playbooks/run-journey-timeline.md`
  - `docs/ai/playbooks/extract-call-records.md`
  - `docs/ai/playbooks/test-call-record-extraction.md`
  - `docs/ai/playbooks/e2e-test-customer.md`
- Optional reminder patch:
  - `.cursor/rules/core.mdc`
