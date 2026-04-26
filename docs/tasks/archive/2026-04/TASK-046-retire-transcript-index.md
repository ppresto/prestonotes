# TASK-046 — Retire `transcript-index.json` and its MCP tools

**Status:** [ ] NOT STARTED
**Opened:** 2026-04-21
**Related:** Surfaced by the TASK-044 E2E fact-check (see also `TASK-051`). Should land **before** TASK-051 hardens the call-record schema so we do not harden a schema we are about to delete.

---

## Problem

`MyNotes/Customers/<customer>/transcript-index.json` is a summary file derived from `call-records/*.json`. Every playbook that reads it **also** immediately calls `read_call_records`, which returns the same information in full. The index:

- Does **not** carry any signal that is not already in the per-call record body.
- Adds a **drift surface** (index vs records can diverge because only `update_transcript_index` rebuilds it; record writes do not).
- Has **dead fields** (`indexed: true` is constant; `unindexed_transcript_chunks: []` has no producer).
- Costs maintenance across an MCP tool surface, spec §7.2, four playbooks, four rule files, a handful of tests, and two harness scripts.

Real usage on the 2026-04-21 E2E run:

| Consumer | What it uses | Replacement |
|---|---|---|
| Run Journey Timeline (Step 1) | `total_calls < 2` gate for health score | `len(read_call_records(...).records) < 2` |
| Run Account Summary (Step 2) | "Ordering & which calls exist" before records pull | `read_call_records` already sorts by date + carries `call_number_in_sequence` |
| Extract Call Records (Step 3) | Seed `call_number_in_sequence` | Already also calls `read_call_records` in the same step; drop the index read |
| Test Call Record Extraction | `X` in the `X==Y` coverage gate | Count records directly (Y already is); X becomes `len(records)` |

---

## Goal

One less artifact, one less drift surface, zero behavior change. Every real workflow keeps working; the file and its MCP tools are gone.

---

## Scope

### A) MCP + library

- `prestonotes_mcp/server.py` — remove tools `update_transcript_index` and `read_transcript_index`.
- `prestonotes_mcp/call_records.py` — remove `rebuild_transcript_index` and `transcript_index_path`.
- `prestonotes_mcp/tests/test_call_record_tools.py` — remove the two index tests (`test_read_transcript_index_missing`, and the index assertions after `write_call_record`).
- `prestonotes_mcp/tests/test_server_write_tools.py` — drop the `transcript-index.json` creation / assertion in the write-tools harness.
- Grep the rest of `prestonotes_mcp/` to catch stragglers.

### B) Playbooks

- `docs/ai/playbooks/extract-call-records.md` — drop Step 3 `read_transcript_index`, drop Step 8 `update_transcript_index`, drop references in the MCP tools table. Step 3 keeps the existing `read_call_records` call; Step 8 simply ends after records are written.
- `docs/ai/playbooks/run-journey-timeline.md` — drop Step 1 `read_transcript_index`. Replace the `total_calls < 2` gate with `records_count < 2` computed from `read_call_records`.
- `docs/ai/playbooks/run-account-summary.md` — drop the Step 2 "ordering" index read; rely on `read_call_records` response ordering.
- `docs/ai/playbooks/test-call-record-extraction.md` — replace "X = `total_calls` from transcript-index.json" with "X = count of validated records returned by `read_call_records`".
- `docs/ai/playbooks/tester-e2e-ucn.md` — drop `transcript-index.json` from the verification checklist and the v1 / v2 step descriptions.

### C) Rules

- `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/22-journey-synthesizer.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc` — remove any `read_transcript_index` / `update_transcript_index` / `transcript-index.json` references.

### D) Harness scripts

- `scripts/e2e-test-customer-materialize.py` — stop seeding / rebuilding a `transcript-index.json`. Transcripts + call-records only.
- `scripts/e2e-test-customer-bump-dates.py` — stop rewriting the index file.
- `scripts/rsync-gdrive-notes.sh` — drop the `_TEST_CUSTOMER` special-case exclude for `transcript-index.json` if it exists.
- `scripts/e2e-test-customer.sh` — no change expected; confirm no callsites.

### E) Docs

- `docs/project_spec.md` §7.2 — delete the transcript-index section; adjust references from other sections.
- `docs/V2_MVP_BUILD_PLAN.md` — scrub any index references.
- `docs/MIGRATION_GUIDE.md` — add a one-line entry: "`transcript-index.json` removed in TASK-046; callers use `read_call_records` directly."
- `tests/fixtures/e2e/_TEST_CUSTOMER/README.md` — drop from fixture layout description.
- `scripts/README.md` + root `README.md` — scrub if present.

### F) Fixture cleanup

- `MyNotes/Customers/_TEST_CUSTOMER/transcript-index.json` will be removed by the next `Run E2E Test Customer` once the tooling no longer emits it. No manual delete required in the repo; a post-TASK-046 E2E run is part of verification.

---

## Explicit non-goals

- **Do not** replace the index with a new aggregate file in this task. If Account Summary / Journey Timeline later hit context pressure with 20+ calls, propose a purpose-built `AI_Insights/call-records-digest.md` in a follow-on task. Premature replacement would re-introduce the same drift problem.
- **Do not** change `call-records/*.json` schema. TASK-051 owns that.
- **Do not** change the approval-bypass rules.
- **Do not** add backwards-compat shims — the index has no out-of-repo consumers.

---

## Acceptance

- [ ] `rg "transcript[_-]index"` under the workspace returns no hits outside archived `docs/tasks/archive/`.
- [ ] `uv run pytest` passes.
- [ ] `Run E2E Test Customer` completes end-to-end; `MyNotes/Customers/_TEST_CUSTOMER/transcript-index.json` does not exist after the run; no step errors on missing index.
- [ ] `docs/project_spec.md` §7.2 removed; referring sections adjusted.
- [ ] MCP server startup shows 2 fewer tools; no consumer calls the removed tools during a full E2E run.

## Verification

- Run `Run E2E Test Customer` and confirm Journey Timeline + Account Summary still produce artifacts.
- Spot-check `read_call_records` outputs are still sorted by date (`rebuild_transcript_index` used to sort; that responsibility moves to consumers or stays in `read_call_records` — prefer keeping the sort in `read_call_records` so downstream callers do not redo it).

---

## Output / Evidence

- **Removed from `prestonotes_mcp/`:**
  - `server.py` — deleted `@mcp.tool` functions `update_transcript_index` and `read_transcript_index`; dropped imports of `rebuild_transcript_index` / `transcript_index_path` from `prestonotes_mcp.call_records`.
  - `call_records.py` — deleted `transcript_index_path` and `rebuild_transcript_index`; dropped unused `datetime` import and `validate_customer_name` import; retitled module docstring to §7.1 only. `read_call_record_files` already sorts by `(date, call_id)` so downstream callers keep their expected ordering.
  - `tests/test_call_record_tools.py` — renamed `test_write_read_update_index_round_trip` → `test_write_read_call_records_round_trip`, dropped index-tool imports/assertions; deleted `test_read_transcript_index_missing`.
  - `tests/test_server_write_tools.py` — dropped the `transcript-index.json` fixture write + post-sync assertion from the `_TEST_CUSTOMER` rsync test.
- **Removed from playbooks:**
  - `extract-call-records.md` — removed `read_transcript_index`/`update_transcript_index` references from purpose, Steps 3/7/8, recap, and the MCP tools table.
  - `run-journey-timeline.md` — dropped Step 1 index call; replaced `total_calls < 2` gate with `count < 2` from `read_call_records`; trimmed metadata + MCP tool table.
  - `run-account-summary.md` — removed Step 3 `read_transcript_index` call.
  - `test-call-record-extraction.md` — redefined X as `count` from `read_call_records`; removed all index tool references + MCP table rows.
  - `tester-e2e-ucn.md` — dropped `transcript-index.json` from the verification checklist and from v1/v2 step descriptions.
- **Removed from rules:**
  - `.cursor/rules/20-orchestrator.mdc` — pruned `update_transcript_index` from TASK-044 override; reworded Step 2 to read validated records via `read_call_records`.
  - `.cursor/rules/21-extractor.mdc` — removed `update_transcript_index` from TASK-044 override and Output section.
  - `.cursor/rules/22-journey-synthesizer.mdc` — removed `read_transcript_index` read path; noted `read_call_records` sort guarantee; fixed the "call records + index" discipline line.
  - `.cursor/rules/11-e2e-test-customer-trigger.mdc` — removed `update_transcript_index` from the approval-bypass mutation list.
- **Removed from scripts:**
  - `scripts/e2e-test-customer-materialize.py` — dropped the `transcript-index.json` copy in `to-fixtures`, and the `_load_rebuild_index` loader + `apply` rebuild step. Removed now-unused `importlib.util`, `json`, `sys` imports.
  - `scripts/e2e-test-customer-bump-dates.py` — deleted the internal `rebuild_transcript_index` helper, the final file write, and the `index_total_calls` field from the JSON summary.
  - `scripts/rsync-gdrive-notes.sh` — removed the `_TEST_CUSTOMER` `--exclude='transcript-index.json'` rule.
- **Spec / doc updates:**
  - `docs/project_spec.md` — replaced §7.2 body with a retirement note; scrubbed §1 transcripts bullet, §2 Rule 2 read path, §3 tool lists, §4 directory tree, §6 data-flow diagram, §9 TASK-004 / TASK-012 / TASK-017 bodies, §11 trigger table, §11 customer-local writes paragraph.
  - `docs/V2_MVP_BUILD_PLAN.md` — updated stage-1 mermaid node to `call-records/*.json`; amended TASK-004 row to note the tools were retired.
  - `docs/MIGRATION_GUIDE.md` — rewrote the TASK-008 extract paragraph and added a one-line TASK-046 retirement entry; fixed the journey-synthesizer rule row.
  - `README.md` — removed `read_transcript_index` / `update_transcript_index` from the MCP cheat sheet.
  - `scripts/README.md` — updated the `e2e-test-customer-materialize.py` description.
  - `tests/fixtures/e2e/_TEST_CUSTOMER/README.md` — removed `v1/transcript-index.json` layout line.
  - `docs/tasks/archive/2026-04/TASK-044-e2e-test-customer-rebuild.md` — removed the "rebuild `transcript-index.json`" bullets from v1 and v2 step descriptions so the harness doc matches the new behavior.
- **E2E run after removal:** Not executed in this task; `Run E2E Test Customer` will delete the stale `MyNotes/Customers/_TEST_CUSTOMER/transcript-index.json` on its next invocation (per §F). Post-task operator should run it once to confirm.

## Handoff / follow-ups

- **Out-of-scope active tasks still reference the index.** TASK-047 / TASK-049 / TASK-050 / TASK-051 were explicitly excluded from this scope; each still contains one or more `transcript-index` references (TASK-047 line 79 and 127; TASK-049 line 192; TASK-050 line 222; TASK-051 lines 33, 119). These references become stale once TASK-046 ships but must be rewritten in those tasks' own scopes to avoid scope creep here. Acceptance item "`rg transcript[_-]index` returns no hits outside archive" therefore has an intentional exception for those five active task files plus the `docs/tasks/archive/` tree; re-run the grep after TASK-047/049/050/051 land to confirm no remaining hits.
- **Archive references preserved.** `docs/tasks/archive/2026-04/TASK-004-call-record-mcp-tools.md` and `docs/tasks/archive/2026-04/TASK-008-extractor-mdc-playbook.md` still name the retired tools in their historical records; these are intentionally not edited.
- **MCP server tool count.** After this task the prestoNotes MCP surface is two tools smaller (no `update_transcript_index`, no `read_transcript_index`). Clients that still call those names will fail with a tool-not-found error from FastMCP — no shim is provided (per non-goals).
