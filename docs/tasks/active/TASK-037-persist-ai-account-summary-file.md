# TASK-037 — Persist AI Account Summary to `AI_Insights/*-AI-AcctSummary.md`

**Status:** [x] COMPLETE  
**Opened:** 2026-04-21  
**Legacy Reference:** v1 depth; user example **`docs/examples/Dayforce-AI-AcctSummary.md`** (add file to repo when redacted copy is available).

## Problem

**`run-account-summary.md`** today outputs the structured narrative **in chat only**. The long-lived artifact **`MyNotes/Customers/<C>/AI_Insights/<C>-AI-AcctSummary.md`** is referenced everywhere but **not written** by a playbook step or MCP tool.

## Goal

Choose one approach (document in task before coding):

- **A)** Extend **`run-account-summary.md`**: after approval, **write local markdown** via a **new** MCP tool (e.g. `write_customer_insight_file`) restricted to `AI_Insights/*.md`, **or**
- **B)** Instruct user to “Save as…” from chat until (A) ships; still add **template alignment** section vs Dayforce example.

### Decision (implemented)

- Selected **Approach B** for MVP safety: no new MCP write tool added in this pass.
- Updated `run-account-summary.md` to define the canonical save path and manual save workflow.
- Added scaffold example `docs/examples/Dayforce-AI-AcctSummary.md` for structure alignment.

## Acceptance

- [x] Playbook states **where** the file lives and **how** it is produced (tool vs manual).
- [x] If tool: `pytest` + schema guard (path under `MyNotes/Customers/<name>/AI_Insights/` only). *(Not applicable in Approach B; no tool added.)*

## Output / Evidence

- Playbook-only implementation (Approach B) with explicit manual path:
  - `docs/ai/playbooks/run-account-summary.md`
- Example scaffold added:
  - `docs/examples/Dayforce-AI-AcctSummary.md`
