# TASK-009 — Stage 1 validation runbook (`test-call-record-extraction`)

## Status

| Field | Value |
|--------|--------|
| **Phase** | **Complete** (2026-04-19) |
| **Spec reference** | [`project_spec.md` §9 — TASK-009](../../project_spec.md#task-009--bootstrap-a-real-customer-and-run-end-to-end-stage-1-test) |
| **Build plan gate** | [`V2_MVP_BUILD_PLAN.md`](../../V2_MVP_BUILD_PLAN.md) — row **009** |

## Goal

Ship **`docs/ai/playbooks/test-call-record-extraction.md`** for trigger **`Test Call Record Extraction for [CustomerName]`** — Stage 1 **manual** validation and coverage report before Stage 2.

## What shipped

- [x] **`docs/ai/playbooks/test-call-record-extraction.md`** — 8-step playbook; **Y** = per-call `YYYY-MM-DD-*.txt` count; **X** = `total_calls` from index; gap + confidence distribution; required gate line.
- [x] **`scripts/ci/required-paths.manifest`** — playbook path.
- [x] **`README.md`** — Stage 1 playbooks row includes TASK-009 trigger.
- [x] **`docs/MIGRATION_GUIDE.md`** — Stage 1 gate sentence.

## Tests / verification

| Check | Result |
|-------|--------|
| **`bash scripts/ci/check-repo-integrity.sh`** | OK |
| **`bash .cursor/skills/test.sh`** | **28 passed** |
| **`bash .cursor/skills/lint.sh`** | OK |
| **Manual gate** | Run on a customer with per-call **`Transcripts/*.txt`** after **`Extract Call Records`**; confirm coverage line. |

## Follow-up

- **TASK-010** — Journey + challenge MCP tools (only after TASK-009 manual gate satisfied on a chosen customer).

---

**Planner:** Archived after user approval and implementation.
