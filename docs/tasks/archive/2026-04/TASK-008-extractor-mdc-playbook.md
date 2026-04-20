# TASK-008 — Extractor `.mdc` rule + playbook + call-type taxonomy

## Status

| Field | Value |
|--------|--------|
| **Phase** | **Complete** (2026-04-19) |
| **Spec reference** | [`project_spec.md` §9 — TASK-008](../../project_spec.md#task-008--build-the-extractor-mdc-rule-and-playbook) · schemas **§7.1–7.2** · taxonomy **§7.3** |
| **Build plan gate** | [`V2_MVP_BUILD_PLAN.md`](../../V2_MVP_BUILD_PLAN.md) — row **008** |

## Goal

Ship the **Stage 1 extractor** as Cursor **reasoning** artifacts: **`21-extractor.mdc`**, **`extract-call-records.md`**, **`call-type-taxonomy.md`**, aligned with MCP **`write_call_record`** / **`update_transcript_index`** and **`prestonotes_mcp/call_records.py`**.

**Trigger phrase:** `Extract Call Records for [CustomerName]`

## What shipped

- [x] **`.cursor/rules/21-extractor.mdc`** — globs, schema/taxonomy pointers, approval gate, sentiment vocabulary, master-transcript policy.
- [x] **`docs/ai/playbooks/extract-call-records.md`** — 9-step playbook, MCP names, **`call_number_in_sequence`** algorithm, approval gate, §7.1 field table.
- [x] **`docs/ai/references/call-type-taxonomy.md`** — expanded §7.3 with signals, edge cases, anti-patterns, Granola filename hint.
- [x] **`scripts/ci/required-paths.manifest`** — three new paths + **`21-extractor.mdc`**.
- [x] **`README.md`** — Stage 1 playbooks row includes extraction trigger.
- [x] **`docs/MIGRATION_GUIDE.md`** — short TASK-008 subsection.

## Tests / verification

| Check | Result |
|-------|--------|
| **`bash scripts/ci/check-repo-integrity.sh`** | OK |
| **`bash .cursor/skills/test.sh`** | **28 passed** |
| **`bash .cursor/skills/lint.sh`** | OK |
| **Manual** | Run **`Extract Call Records for [Customer]`** on a folder with per-call **`Transcripts/*.txt`** (TASK-009 deepens QA). |

## Follow-up

- **TASK-009** — **`test-call-record-extraction.md`** runbook and end-to-end Stage 1 validation.

---

**Planner:** Archived after user approval and implementation pass.
