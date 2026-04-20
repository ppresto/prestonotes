# TASK-007 — Port Cursor rules + MVP playbooks

## Status

| Field | Value |
|--------|--------|
| **Phase** | **Complete** (2026-04-19) |
| **Spec reference** | [`project_spec.md` §9 — TASK-007](../../project_spec.md#task-007--port-the-cursor-rules-and-ai_learnings) |
| **Build plan gate** | [`V2_MVP_BUILD_PLAN.md`](../../V2_MVP_BUILD_PLAN.md) — row **007** |

## Goal

Bring v1 **guardrail rules** and **Stage 1 MVP playbooks (three)** into v2: **`load-customer-context`**, **`update-customer-notes`**, **`run-license-evidence-check`**, aligned with per-call transcripts, **`prestonotes_gdoc/`**, MCP, and TASK-006 rsync.

## Scope — Cursor rules

- [x] **`15-user-preferences.mdc`**, **`ai_learnings.mdc`**, **core merge** — Customer notes / MyNotes / ledger / Daily Activity / tools.json / ingestion weights merged into **`.cursor/rules/core.mdc`** (§ Customer notes & MyNotes).
- [x] **Rewrite references** in playbooks and refs: **`prestonotes_gdoc/`**, rsync, per-call + MCP; license playbook + **`scripts/wiz_doc_cache_manager.py`**.

## Scope — MVP playbooks

- [x] `docs/ai/playbooks/load-customer-context.md`
- [x] `docs/ai/playbooks/update-customer-notes.md`
- [x] `docs/ai/playbooks/run-license-evidence-check.md`

## Scope — supporting reference docs

- [x] `docs/ai/references/customer-data-ingestion-weights.md`
- [x] `docs/ai/references/customer-notes-mutation-rules.md`
- [x] `docs/ai/references/daily-activity-ai-prepend.md`

## Integration

- [x] **`README.md`** / **`MIGRATION_GUIDE.md`** — pointers to MVP playbooks and §11 triggers.
- [x] **`scripts/ci/required-paths.manifest`** — playbooks, refs, **`wiz_doc_cache_manager.py`**, new rule files.

## Tests / verification

| Check | Notes |
|-------|--------|
| **Automated** | `bash scripts/ci/check-repo-integrity.sh`, `bash .cursor/skills/test.sh`, `bash .cursor/skills/lint.sh` |
| **Manual** | **`TestCo`** skeleton: run the three trigger phrases per **`project_spec.md`** §9 acceptance when MCP/Drive are configured. |

## Deferred (unchanged)

**`run-bva-report.md`**, **`run-logic-audit.md`** — later reports task; see **`project_spec.md`** §12.

---

**Orchestrator:** Archived after `/coder` → `/tester` → `/doc` pipeline for TASK-007.
