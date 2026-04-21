# TASK-040 — Doc subagent: README readability + MVP clarity

**Status:** [x] COMPLETE (2026-04-21)  
**Opened:** 2026-04-21  
**Assignee:** **`/doc`** subagent (after user approval per **workflow.mdc**)  
**Legacy Reference:** **`README.md`**; **`docs/tasks/INDEX.md`**; user request for “what is 100% / partial / unknown”.

## Goal

Improve **`README.md`** so a new reader sees, **above the fold**:

1. **What the repo does today** (bullet: fully automated vs needs credentials vs manual once).
2. **MVP actions** (the five flows in **TASK-034**) with **one line each** + link to playbook.
3. **Prerequisites table** (Drive, gcloud, Wiz MCP, Gemini key for vectors) — what blocks the LLM if missing.

Follow **`.cursor/rules/15-user-preferences.mdc`**: lead with **3 bullets**, then **`### Activity recap`** style section listing doc files touched.

## Acceptance

- [x] README has **MVP actions (5)**, **Capability at a glance**, **Before you ask the LLM**, **Activity recap** opener; links **`TASK-034`**.

## Output / Evidence

- **`README.md`** — doc subagent pass (2026-04-21).
