# TASK-047 — Retire Journey Timeline; fold narrative into Account Summary

**Status:** [ ] NOT STARTED
**Opened:** 2026-04-21
**Related:** Surfaced by the TASK-044 E2E review (Q3). Pairs with `TASK-046` (retire `transcript-index.json`) and unblocks `TASK-051` (call-record quality) by removing a downstream artifact that was silently driving schema pressure.
**Related files:**
- Playbooks: `docs/ai/playbooks/run-journey-timeline.md` (delete), `docs/ai/playbooks/run-account-summary.md` (extend), `docs/ai/playbooks/update-customer-notes.md` (drop sidecar)
- Rules: `.cursor/rules/22-journey-synthesizer.mdc` (delete), `.cursor/rules/20-orchestrator.mdc` (drop sidecar + scrub harness vocab), `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`
- MCP: `prestonotes_mcp/server.py` (remove `write_journey_timeline`; add `read_challenge_lifecycle`), `prestonotes_mcp/journey.py`, `prestonotes_mcp/security.py`, `prestonotes_mcp/tests/test_journey_tools.py`
- Template: `docs/ai/references/exec-summary-template.md` (extend)
- References: `docs/ai/references/health-score-model.md`, `docs/ai/references/challenge-lifecycle-model.md`

---

## Problem

`*-Journey-Timeline.md` is a **write-only artifact** nobody reads. On the 2026-04-21 TASK-044 E2E run it produced ~20% of its playbook contract (Step 12 requires 11 sections; the output delivered 2 dated bullet clusters with no Health line, no VP brief, no call spine, no milestones, no TASK-014 review table, no stakeholder evolution, no value-realized section, no strategic position). It also leaked harness vocabulary — `"E2E UCN round 1 (TASK-044)"` and `"post-v2 corpus"` — directly into the customer-facing markdown, because the `TASK-044 override` text in the approval-bypass rules sits in the agent's context window during E2E runs.

Meanwhile:

- **No `read_journey_timeline` MCP tool exists.** No playbook, script, rule, or test reads the markdown content back.
- **UCN's "mandatory sidecar" write** (20-orchestrator.mdc lines 54 and 92) is the only caller, and it is producing the degenerate output above.
- **Account Summary — which is actually read by humans and is the natural home for an account narrative — does not read `challenge-lifecycle.json` today** (the source of truth for challenge state). It infers challenge state from call-records + the GDoc Challenge Tracker. With TASK-051 still pending and call-record fields currently stubs, this inference is fragile.
- The overlap with `challenge-lifecycle.json` is real in user-perception terms even though the schemas don't duplicate: lifecycle JSON is *state*, Journey Timeline was supposed to be *narrative*. With Journey Timeline producing 20% of its narrative contract, it reads like a redundant, flimsy shadow of the JSON file.

Consequence: we maintain a playbook, a rule, an MCP write tool, a size guard, a test, a UCN sidecar contract, and a persisted markdown artifact — all for a document no downstream system reads and which ships with harness vocabulary.

---

## Goals

1. **Delete `Journey-Timeline.md` and its entire supporting surface** (MCP tool, size guard, playbook, rule, sidecar contract). Zero downstream breakage because nothing reads it today.
2. **Enrich Run Account Summary** to absorb the Journey Timeline's unique content (Health line, chronological call spine, milestones, TASK-014 challenge review table with stall/drift) **as optional sections** driven by the existing inputs plus a new read.
3. **Give Account Summary a correct view of challenge state** by adding a thin MCP read tool for `challenge-lifecycle.json`, matching the I/O story of `read_ledger` / `read_call_records` / `read_doc`.
4. **Scrub harness vocabulary from the rules the agent reads during an E2E run**, so no customer artifact ever contains `TASK-044`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, or `E2E`.
5. **Preserve all upstream writes** — UCN continues to write `challenge-lifecycle.json` (`update_challenge_state`), the GDoc Challenge Tracker (`write_doc`), and the History Ledger (`append_ledger_v2`). Only the narrative sidecar is removed.

---

## Scope

### A) Delete Journey Timeline surface

- `prestonotes_mcp/server.py` — remove the `write_journey_timeline` MCP tool and its import of `write_journey_timeline_markdown`. Remove from the MCP instructions string.
- `prestonotes_mcp/journey.py` — remove `journey_timeline_path`, `write_journey_timeline_markdown`. Keep `append_challenge_transition` (it backs `update_challenge_state`, which stays).
- `prestonotes_mcp/security.py` — remove `check_journey_timeline_size` and the `max_journey_timeline_bytes` config key.
- `prestonotes_mcp/prestonotes-mcp.yaml.example` — drop the `max_journey_timeline_bytes` example entry.
- `prestonotes_mcp/tests/test_journey_tools.py` — remove `test_write_journey_timeline_round_trip`; keep challenge-transition tests.
- `docs/ai/playbooks/run-journey-timeline.md` — delete.
- `.cursor/rules/22-journey-synthesizer.mdc` — delete.
- `scripts/ci/required-paths.manifest` — drop entries for the deleted files.
- `prestonotes_mcp/tests/test_phase3_wave_cd_playbooks_manifest.py` — drop the `run-journey-timeline.md` expectation.

### B) Drop UCN's mandatory sidecar contract

- `.cursor/rules/20-orchestrator.mdc` — remove the "mandatory `write_journey_timeline` after lifecycle or GDoc write" language (lines ~54 and ~92 in the current file). UCN after TASK-047 writes: `update_challenge_state` (as approved), `write_doc` (as approved), `append_ledger_v2`, optional `log_run`, optional `sync_notes`. No journey sidecar.
- `.cursor/rules/core.mdc`, `.cursor/rules/21-extractor.mdc` — scrub any residual `write_journey_timeline` references.
- `.cursor/rules/11-e2e-test-customer-trigger.mdc` — drop `write_journey_timeline` from the "mutation tools bypass approval" list.
- `docs/ai/playbooks/update-customer-notes.md` — drop "mandatory journey sidecar" language if present.
- `docs/ai/playbooks/tester-e2e-ucn.md` — remove the Step 6 / Step 9 references to "close with mandatory `write_journey_timeline`".

### C) Enrich Run Account Summary (the new home for the narrative)

- `docs/ai/playbooks/run-account-summary.md` — rewrite Steps 3–7 to include:
    - **New Step 3.5** — `read_challenge_lifecycle([CustomerName])` MCP call (see D). Make this a required input when the file exists; when it does not, fall through with an explicit "no persisted lifecycle yet" note. Do **not** infer lifecycle state from call-records when the JSON is present — JSON wins.
    - **Step 7 template changes** — add five optional sections sourced from the retired Journey contract:
        - **Health** — single line `Health: 🟢|🟡|🔴|⚪ …` per `docs/ai/references/health-score-model.md`.
        - **30-Second Brief** — already present; keep.
        - **Chronological call spine** — compact table: `Date | call_id | call_type | summary_one_liner | sentiment`. Dated by **call date**, never by run date. Bounded to in-lookback calls by default; expandable to full history on explicit user ask.
        - **Milestones** — bullets (first discovery, first POC, first POC readout, commercial close, champion transition, renewal gate, etc.). Each bullet cites `call_id` + date. Derive from `call_type` + `challenges_mentioned[].id` transitions + lifecycle `history[]`.
        - **Challenge review (TASK-014)** — table: `challenge_id | description | current_state | last_updated | evidence | stall/risk | recommended_action`. `current_state` + `last_updated` come from lifecycle JSON; `evidence` cites latest `call_id`; stall flag = ≥ 60 days since last transition per `challenge-lifecycle-model.md`.
        - **Stakeholders** (already present) — extend with first-seen / last-seen columns derived from call-records `participants[]`.
    - **Step 5 weights** — add **`challenge-lifecycle.json`** at **+2** (source-of-truth JSON). `Journey-Timeline.md` no longer exists.
- `docs/ai/references/exec-summary-template.md` — mirror the new sections; mark the three new ones as optional so a user asking for an "exec-only" summary can skip them.
- `docs/examples/Dayforce-AI-AcctSummary.md` (if shape example) — refresh to include one of the new sections as a worked example.

### D) Add `read_challenge_lifecycle` MCP tool

- `prestonotes_mcp/server.py` — new read tool. Implementation mirrors `read_transcript_index`-style shape (customer-scoped path resolution via `customer_dir`, JSON-text return, `{"error": "file not found"}` payload when absent, `tool_scope` telemetry).
- `prestonotes_mcp/journey.py` — add `challenge_lifecycle_path(customer_name) -> Path` helper if one doesn't already exist.
- `prestonotes_mcp/tests/test_journey_tools.py` — add round-trip tests: (a) missing file returns error payload; (b) seeded file returns parseable JSON matching `challenge-lifecycle.json` §7.4 shape.
- Why MCP (not workspace read, despite being "cheaper"): the workspace-read path requires the agent to resolve the customer folder on its own, which has bitten us before with leading-underscore names (TASK-041). The MCP tool reuses `validate_customer_name` + `customer_dir`, giving byte-for-byte identical resolution with `read_ledger` / `read_call_records` / `read_doc`. The ~15 LOC cost buys 100% consistency with the rest of the MCP read surface.

### E) Scrub harness vocabulary from agent context

- `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc`, `.cursor/rules/core.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc` — change any `TASK-044 override` language to `_TEST_CUSTOMER` E2E override (see `docs/ai/playbooks/tester-e2e-ucn.md`)`. The rule mechanics do not depend on the task id; only the cross-reference did.
- `.cursor/rules/11-e2e-test-customer-trigger.mdc` — add a rule block titled **"Artifact hygiene"**:
  > Customer artifacts (GDoc, History Ledger, challenge-lifecycle.json, Account Summary, call-records) must be indistinguishable from a real-customer run. **Do not** mention any `TASK-NNN` identifier, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`, or any test-only vocabulary. Section dates are **call / milestone dates**, never the run date. Metadata headers (when a section explicitly called "Metadata" exists) may carry the run date labeled as "Generated: YYYY-MM-DD".
- `docs/ai/playbooks/tester-e2e-ucn.md` — neutralize the "round 1 / round 2" vocabulary in instructions to the agent, or move that vocabulary to "operator-facing only" sections clearly outside the agent's artifact-writing context.

### F) Data-on-disk cleanup

- Existing `MyNotes/Customers/*/AI_Insights/*-Journey-Timeline.md` files are left in place at migration time (the file is write-only; leaving a stale one does not break anything). The **next** `Run E2E Test Customer` / `Run Account Summary` run will not produce or touch it. Operators who care can delete manually; a one-liner in `docs/MIGRATION_GUIDE.md` covers this.

---

## Explicit non-goals

- **Do not** change `challenge-lifecycle.json` schema. §7.4 stays as-is.
- **Do not** change UCN's existing writes to lifecycle + GDoc + ledger.
- **Do not** change `read_call_records` / `read_ledger` / `write_doc` / `update_challenge_state`.
- **Do not** add a new "narrative" persisted artifact. The Account Summary output stays the on-demand deliverable (chat + optional manual save per TASK-037 approach B).
- **Do not** rewrite call-record content in this task — TASK-051 owns that. TASK-047 only consumes whatever fields the records currently expose.
- **Do not** introduce a `read_journey_timeline` read tool. We are deleting the artifact, not re-wrapping it.
- **Do not** modify the approval-bypass behavior for `_TEST_CUSTOMER` — only the cross-reference wording changes.

---

## Acceptance

- [ ] `rg "write_journey_timeline|Journey-Timeline|run-journey-timeline|22-journey-synthesizer"` under the workspace returns no hits outside archived `docs/tasks/archive/`.
- [ ] `rg "TASK-044 override"` returns no hits; `rg "_TEST_CUSTOMER. E2E override"` (or equivalent neutral phrasing) is used in all four rule files.
- [ ] `prestonotes_mcp/server.py` no longer exposes `write_journey_timeline`; it does expose `read_challenge_lifecycle`.
- [ ] `uv run pytest` passes, including the two new `test_read_challenge_lifecycle_*` tests.
- [ ] `Run Account Summary for _TEST_CUSTOMER` (after a TASK-044 full E2E) produces a single markdown artifact containing: Health line, 30-Second Brief, Challenges → Solutions Map, Chronological call spine (dated by call dates), Milestones, **Challenge review table with stall/drift sourced from `challenge-lifecycle.json`**, Stakeholders (with first-seen / last-seen), Value Realized, Strategic Position, Wiz Commercials, Open Challenges.
- [ ] That artifact contains **zero** instances of `TASK-044`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`.
- [ ] Section dates in the spine and milestones are **call dates**, not the run date. The run date only appears in a `Metadata` / `Generated:` line if present.
- [ ] A subsequent `Run E2E Test Customer` completes end-to-end without any orchestrator step calling `write_journey_timeline` (verified via agent transcript or `_TEST_CUSTOMER-AI-AcctSummary.md` contents).
- [ ] `docs/MIGRATION_GUIDE.md` has a one-line entry explaining the removal.

## Verification

- Run `Run E2E Test Customer` on a cleanly reset `_TEST_CUSTOMER`. Confirm:
    - UCN runs both rounds without writing a Journey Timeline.
    - Account Summary output (chat) has all new sections and none of the banned vocabulary.
    - `challenge-lifecycle.json` on disk is unchanged in schema; Account Summary's challenge review reflects its `current_state` / `history[]`.
- Sequencing: land **after TASK-046** (transcript-index removal) to avoid touching two simultaneous Account Summary input changes, and **before TASK-051** so the call-record schema work doesn't need to also satisfy a Journey Timeline schema.

---

## Output / Evidence

_(Filled in as the task is executed.)_

- MCP + library diffs: —
- Playbook + rule diffs: —
- Vocabulary scrub: —
- Acceptance run (fresh `_TEST_CUSTOMER` E2E + Account Summary): —
