# TASK-048 — Challenge lifecycle write-side discipline

**Status:** [x] COMPLETE — write-side discipline, MCP validations, 6 new tests, rule + playbook updates landed and docs aligned. Bullet 8 (E2E fixture refresh, §F) is runtime-dependent and re-checks on the next `Run E2E Test Customer` pass.
**Opened:** 2026-04-21
**Related:** Surfaced by the TASK-044 E2E review (Q4). Pairs with `TASK-047` (Account Summary elevates `challenge-lifecycle.json` to a +2 weighted input) and `TASK-051` (call-record quality). Independent of `TASK-046`.
**Related files:**
- Rules: `.cursor/rules/21-extractor.mdc`, `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/11-e2e-test-customer-trigger.mdc`
- Playbooks: `docs/ai/playbooks/update-customer-notes.md`, `docs/ai/playbooks/tester-e2e-ucn.md`
- MCP: `prestonotes_mcp/server.py` (`update_challenge_state`), `prestonotes_mcp/journey.py` (`append_challenge_transition`), `prestonotes_mcp/tests/test_journey_tools.py`
- Reference: `docs/ai/references/challenge-lifecycle-model.md`
- Fact-check ground truth: `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/*.txt`, `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json` (post-TASK-044 run)

---

## Problem

The TASK-044 E2E run produced `challenge-lifecycle.json` with seven concrete defects, fact-checked against the 8 transcripts in the corpus:

1. **Every transition `at` is the run date (2026-04-21)**, not the call date of the evidence-citing transcript. `ch-soc-budget` has three transitions all stamped 2026-04-21. Consequence: the stall-detection rule TASK-047 promotes to Account Summary (≥60 days since last transition per `challenge-lifecycle-model.md`) cannot fire correctly, and any diff of this file will look like same-day churn.
2. **State choice contradicts the customer.** 3/28 Cloud close transcript line 7 says verbatim: *"Splunk is still blocked by budget, but we did get approval to run the Q2 evaluation path, so track that as in progress instead of stalled."* The lifecycle file ends at `stalled` and cites that exact call as the evidence. The extractor read the call and then reversed the customer's explicit instruction.
3. **Factually wrong evidence date.** `"2026-03-29 exec readout"` — no such transcript exists; the exec sponsor readout is 2026-04-04. Evidence strings appear to be paraphrased rather than sourced.
4. **Meta-process evidence.** `"E2E UCN round-1: challenge rows added to Notes doc Challenge Tracker."` appears twice. This is not customer evidence; it is a description of what UCN did to the GDoc. It should never reach the lifecycle file.
5. **Harness vocabulary** inside evidence strings (`E2E UCN round-1`) — TASK-047 scope handles vocabulary hygiene globally; this task enforces it on the lifecycle-write path specifically.
6. **Under-extraction.** Only 2 of ~6–7 real challenges made it in. Missing: **sensor deployment stall → resolved** (QBR 4/18: *"The agent rollout is no longer stalled … 900/1000 workloads scanned"*), **Splunk integration** as a separate id from SOC budget (customer explicitly requested the split on 3/28), **kubelet-noise → resolved** (3/28: *"resolved after the patch cycle"*), **Jira auto-routing** (now working per QBR).
7. **Redundant no-op transitions.** `ch-soc-budget` writes `identified → in_progress → stalled` all with `at = 2026-04-21`. The middle `in_progress` entry's evidence is meta-process. Non-moving transitions with identical `at` values should never be written.

The failure mode is the **write-side logic**, not the schema. Schema §7.4 is fine.

Also note on operator concern (captured in the Q4 discussion): **past dates of any age are the common case, not an edge case.** Transcripts pulled a week, a month, or longer after the call are normal. The rules below reject only future dates and history regressions; past dates of any age write cleanly with no warning.

---

## Goals

1. **Call date wins.** Every lifecycle transition's `at` equals the ISO call date of the single transcript cited in its `evidence`. Run date is never used.
2. **One transition = one call.** Evidence cites one transcript (by date + one direct quote), not a multi-call blob.
3. **Customer intent wins over heuristics.** When a transcript contains an explicit state directive ("treat as in_progress, not stalled"), the extractor honors that directive verbatim.
4. **Zero meta-process evidence.** Evidence describes what the customer said or did, not what UCN wrote to which doc.
5. **Resolved transitions happen.** When a later call explicitly unblocks an earlier `in_progress` or `stalled` challenge, UCN writes a `resolved` transition instead of leaving the challenge in the prior state.
6. **No no-op transitions.** If a proposed transition does not change `current_state` AND its `at` equals the prior transition's `at`, it is not written.
7. **Composite challenges split when asked.** If a transcript explicitly distinguishes two challenges ("keep Splunk renewal separate from the budget blocker"), the extractor opens two `challenge_id`s.
8. **Loud, explicit MCP errors.** Any MCP-side rejection carries a human-readable payload naming the field, the offending value, and the expected shape. No silent drops.

---

## Scope

### A) Extractor discipline (`.cursor/rules/21-extractor.mdc` + `docs/ai/playbooks/update-customer-notes.md`)

Add a **"Challenge lifecycle write rules"** section that governs every `update_challenge_state` call UCN makes:

1. `transitioned_at` MUST be read from the cited transcript's header (`DATE:` line, ISO form). If the extractor cannot determine the call date from the transcript, it **does not write** and emits one log line: `skip update_challenge_state ch=<id> reason=unknown_call_date`. UCN continues the rest of its work.
2. `evidence` MUST be structured as: `<YYYY-MM-DD> <call-topic-short>: "<direct quote, ≤ 160 chars>"`. No paraphrase. No multi-call blobs. No meta-process language.
3. If a transcript contains an explicit state directive (regex-detectable family: *"treat as X, not Y"*, *"track as X instead of Y"*, *"mark it resolved"*, *"this is no longer stalled"*), the extractor uses the directive's target state verbatim and cites that same line as evidence.
4. After writing all transitions from the current run, the extractor performs a **"resolved sweep"**: for each challenge whose current state is `in_progress` or `stalled`, scan the newest-in-lookback transcript for explicit unblock language (*"no longer stalled"*, *"resolved"*, *"shipped"*, *"done"*, *"we got it"*). If found, write a `resolved` transition at that transcript's call date.
5. Collapse rule: do not call `update_challenge_state` if the proposed `(state, at)` tuple equals the last entry already in `history` for that `challenge_id`.
6. Split rule: if a single extracted challenge contains two distinct subjects and the transcript contains explicit split language, open two ids (e.g. `ch-soc-budget` and `ch-splunk-integration`) and write them separately.
7. Forbidden evidence vocabulary (rejected at MCP write-time, see C): `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`, `UCN round`, `UCN wrote`, `challenge rows added`, `TASK-`, `prestoNotes session`.

### B) Orchestrator awareness (`.cursor/rules/20-orchestrator.mdc`)

- Reference the new extractor section from the UCN post-flight checklist.
- No new orchestrator steps — the writes still happen in the existing UCN slot after the GDoc update.

### B.1) UCN Challenge Tracker row discipline (surfaced by Q6 GDoc review)

The same "call date wins over run date" rule applies to a **second write path** that bypasses `update_challenge_state`: UCN's GDoc mutation plan writes Challenge Tracker rows directly via `write_doc`, and those rows have their own `date` column and `notes_references` evidence string. The 2026-04-21 E2E produced Challenge Tracker rows containing `Evidence: … 2026-03-29 exec readout` — a **fabricated date** (the actual exec readout transcript is 2026-04-04). Same bug family as §A.

Add to `.cursor/rules/21-extractor.mdc` (and mirror in `docs/ai/playbooks/update-customer-notes.md`):

1. **Challenge Tracker row `date` column** MUST be the ISO call date of the most recent transcript that touched this challenge, not the run date.
2. **Challenge Tracker row `notes_references` `Evidence:` dates** MUST cite ISO dates that exist in the customer's `MyNotes/Customers/<X>/Transcripts/` folder. The extractor performs a preflight check: for every `YYYY-MM-DD` referenced in `notes_references`, verify a transcript file with that date prefix exists. If the check fails, skip the row and emit `skip challenge_tracker_row ch=<id> reason=evidence_date_not_in_corpus`.
3. **Same forbidden-vocabulary rejection** applies to Challenge Tracker row `notes_references` (inherits the TASK-047 list).
4. The MCP `write_doc` path does not validate these (it is a generic doc writer). Enforcement is rule-side + extractor preflight, matching the §A model for lifecycle evidence strings.

### C) MCP hard validations (`prestonotes_mcp/server.py` + `prestonotes_mcp/journey.py`)

Add three hard-reject validations to `update_challenge_state` **and** `append_challenge_transition` (both write paths):

1. **Future date rejection.** If `transitioned_at > today + 1 day` (UTC), reject with:
   ```json
   {"error": "transitioned_at in future", "field": "transitioned_at", "value": "<iso>", "expected": "<= today (UTC)"}
   ```
   Intentionally permits `+1 day` for timezone slop on same-day calls.
2. **History regression rejection.** If the file already has a transition entry for this `challenge_id` with `at` strictly newer than the incoming `transitioned_at`, reject with:
   ```json
   {"error": "transitioned_at regresses history", "field": "transitioned_at", "value": "<iso>", "latest_existing": "<iso>"}
   ```
3. **Forbidden-evidence-vocabulary rejection.** If `evidence` matches any term in the forbidden list (case-insensitive), reject with:
   ```json
   {"error": "evidence contains forbidden harness vocabulary", "field": "evidence", "matched": "<term>"}
   ```
   Forbidden list is defined in one place — `prestonotes_mcp/journey.py` `FORBIDDEN_EVIDENCE_TERMS` — and reused by the TASK-047 hygiene checks.

**Explicitly NOT rejected at MCP layer:**
- Old dates, regardless of age. A 3-month-old or 3-year-old `at` is accepted. This is the common case, not an edge case.
- `at == today` on its own. Legitimate when a call literally happened today.
- `at` mismatching `evidence` text. The extractor-rule regex heuristic is too fuzzy for a hard reject; this is enforced by rule + extractor preflight, not MCP validation.

### D) Write helper signature

- `append_challenge_transition(customer_name, challenge_id, state, transitioned_at, evidence)` — confirm signature already passes `transitioned_at`. If today it defaults to `datetime.today()`, change default to **required** (no silent fallback). Callers must pass an explicit ISO date.
- Update `update_challenge_state` MCP tool to require `transitioned_at` in its parameter schema.

### E) Tests (`prestonotes_mcp/tests/test_journey_tools.py`)

Add:
- `test_update_challenge_state_rejects_future_at` — `at = today + 2 days` → error payload shape matches.
- `test_update_challenge_state_rejects_regression` — seed file with `at = 2026-04-10`, call with `at = 2026-04-05` → rejected.
- `test_update_challenge_state_accepts_month_old_at` — `at = today - 45 days` → accepted (guards against the user's operational concern).
- `test_update_challenge_state_accepts_year_old_at` — `at = today - 400 days` → accepted.
- `test_update_challenge_state_rejects_forbidden_evidence` — evidence containing `"UCN round-1"` → rejected with `matched == "UCN round"`.
- `test_update_challenge_state_requires_transitioned_at` — omitting the field → validation error, not a silent default.

### F) E2E fixture refresh

- After TASK-048 lands, the TASK-044 E2E run should produce a `challenge-lifecycle.json` that:
    - Has ≥ 4 distinct `challenge_id`s (SOC budget, champion exit, sensor rollout, Splunk integration at minimum — kubelet noise and Jira bonus).
    - Uses **call dates** for `at` (distributed across 2026-03-24 … 2026-04-18, never 2026-04-21 unless a call literally happened that day).
    - Marks sensor rollout and kubelet noise as `resolved`.
    - Has no harness vocabulary anywhere in evidence.
    - Has no no-op transitions.
- No fixture schema change required; this is a content correctness requirement verified by the E2E validation checklist in `docs/ai/playbooks/tester-e2e-ucn.md`.

---

## Explicit non-goals

- **Do not change §7.4 schema.** Keys, shapes, ISO formats all stay.
- **Do not add age-based rejection.** Old transcripts of any age are fully supported.
- **Do not move the write path.** UCN still calls `update_challenge_state` after the GDoc update.
- **Do not add the regex "does `at` match evidence-cited date?" check to MCP.** Enforced by extractor rule, not hard validation, to avoid false rejects on edge formatting.
- **Do not modify Account Summary or Journey Timeline in this task.** TASK-047 owns those. TASK-048 only improves the data that TASK-047 will read.
- **Do not modify call-record extraction.** TASK-051 owns that. Lifecycle extraction reads transcripts directly (UCN's own extractor step), not call-records.

---

## Acceptance

- [x] `update_challenge_state` and `append_challenge_transition` both require explicit `transitioned_at`; omitting the field returns a loud validation error, no silent default.
- [x] `at > today + 1 day` rejected with named error payload.
- [x] `at` older than the latest existing `at` for the same challenge rejected with named error payload.
- [x] `at = today - 45 days` and `at = today - 400 days` both accepted without warning.
- [x] Evidence containing any forbidden term rejected with `matched` field identifying the term.
- [x] Six new tests in `test_journey_tools.py` pass.
- [x] `.cursor/rules/21-extractor.mdc` documents the seven extractor-side rules in §A.
- [ ] Post-TASK-048 GDoc Challenge Tracker rows for `_TEST_CUSTOMER`: every `notes_references` `Evidence: YYYY-MM-DD` value points to a real transcript file in `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/`. Zero hallucinated dates (the `2026-03-29 exec readout` class of bug cannot recur). _(Verified at next `Run E2E Test Customer` execution — §F.)_ (runtime-deferred; re-check after next Run E2E Test Customer)
- [ ] Post-TASK-048 TASK-044 E2E run produces `_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json` with: (runtime-deferred; re-check after next Run E2E Test Customer)
    - ≥ 4 distinct `challenge_id`s.
    - All `at` values on call dates in 2026-03-24 … 2026-04-18 range, none on 2026-04-21 (the run date).
    - Sensor rollout marked `resolved`.
    - `ch-splunk-integration` split from `ch-soc-budget`.
    - Zero evidence strings containing `round 1`, `UCN`, `E2E`, `TASK-`, `corpus`, `phase`, `harness`, `fixture`.
    - No two consecutive entries with identical `(state, at)` for the same `challenge_id`.

## Verification

1. Unit: `uv run pytest prestonotes_mcp/tests/test_journey_tools.py`.
2. Integration: `Run E2E Test Customer` on a cleanly reset `_TEST_CUSTOMER`. Diff `AI_Insights/challenge-lifecycle.json` against the acceptance bullets above.
3. Operator safety smoke: run UCN on a real customer whose newest transcript is ≥ 30 days old. Confirm lifecycle writes succeed (`at` is the old call date, no rejection). This directly covers the concern raised in Q4 that older transcripts must not be silently dropped.

## Sequencing

Land **after TASK-046 → TASK-047**, **before TASK-051**. Rationale:
- TASK-046 shrinks the I/O surface Account Summary depends on.
- TASK-047 defines where the challenge-lifecycle data is read from and scrubs global harness vocabulary, giving TASK-048 a clean target for its write rules.
- TASK-051 then inherits a high-quality lifecycle as a reference point when hardening call-record content.

---

## Output / Evidence

- Rule + playbook diffs:
    - `.cursor/rules/21-extractor.mdc` — added top-level sections **"Challenge lifecycle write rules (TASK-048)"** (§A rules 1–7) and **"Challenge Tracker row discipline (TASK-048 §B.1)"** (4 rules). Rule 7 cites `FORBIDDEN_EVIDENCE_TERMS` in `prestonotes_mcp/journey.py` as the single source of truth; the list mirror in `.cursor/rules/11-e2e-test-customer-trigger.mdc` is operator-facing only.
    - `.cursor/rules/20-orchestrator.mdc` — added pointer lines to the new extractor sections from the UCN post-approval **Execute** block (lifecycle path and Challenge Tracker path). No new orchestrator steps.
    - `docs/ai/playbooks/update-customer-notes.md` — mirrored both §A and §B.1 as operator-facing UCN prose at the end of the playbook (before References).
- MCP + journey.py + test diffs:
    - `prestonotes_mcp/journey.py` — added `FORBIDDEN_EVIDENCE_TERMS` constant (declaration-ordered tuple, case-insensitive substring match via `_match_forbidden_evidence`), added `ChallengeValidationError(ValueError)` carrying a JSON-serializable `payload` dict, replaced the `at: str | None = None` kwarg on `append_challenge_transition` with a required `transitioned_at: str | None = None` that rejects empty/missing with a plain `ValueError`, and added three hard-reject `ChallengeValidationError` checks (future date `> today + 1 day`, forbidden evidence vocabulary, history regression). Existing illegal-transition and redundant-same-state `ValueError`s preserved verbatim so `test_update_challenge_state_rejects_illegal_jump` still raises.
    - `prestonotes_mcp/server.py` — `update_challenge_state` MCP tool gained required positional `transitioned_at: str` parameter, docstring documents the three structured rejections, and the tool catches `ChallengeValidationError` and returns `json.dumps({"ok": False, **payload})` on stdout while letting plain `ValueError` (illegal transitions) propagate. **Parameter schema change** — flagged to `/code-tester` for the required-paths integrity sweep (`scripts/ci/check-repo-integrity.sh`).
    - `prestonotes_mcp/tests/test_journey_tools.py` — updated the 4 existing tests to pass explicit `transitioned_at` (no silent default exists any more), added the 6 new tests from §E verbatim. `uv run pytest prestonotes_mcp/tests/test_journey_tools.py` → 10 passed. `uv run pytest` → 79 passed, 1 skipped.
- Post-task E2E `challenge-lifecycle.json` vs acceptance bullets: Runtime-deferred; bullet 8 requires a fresh `Run E2E Test Customer` pass. Write-side discipline is enforced in code + rules + playbook; the §F acceptance content assertions only produce signal after a full E2E rerun.
- Operator-safety run (≥30-day-old transcript) result: Runtime-deferred; §Verification step 3 is an operational smoke test. Unit coverage (`test_update_challenge_state_accepts_month_old_at` at today − 45 days, `test_update_challenge_state_accepts_year_old_at` at today − 400 days) already guards the "old call dates write cleanly" invariant.

## Handoff / follow-ups

- **MCP parameter schema change** (`update_challenge_state` gained required `transitioned_at`) — no entries in `scripts/ci/required-paths.manifest` track tool signatures (only file paths), so `scripts/ci/check-repo-integrity.sh` should pass unchanged. Noted for `/code-tester` all the same.
- **§F E2E fixture refresh** is runtime-only (the §F acceptance bullets are content assertions on `_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json` produced by a full E2E pass). This TASK-048 hardens the write path that produces it; closing §F requires a fresh `Run E2E Test Customer` run and a diff vs the acceptance bullets, which is out of scope for the coder subagent.
- **TASK-049 reuse**: `FORBIDDEN_EVIDENCE_TERMS` now lives in `prestonotes_mcp/journey.py`; TASK-049's ledger-cell vocabulary check should import from there rather than redefining.
- **TASK-050 reuse**: same import source when TASK-050 extends forbidden-vocab enforcement to GDoc cells.
