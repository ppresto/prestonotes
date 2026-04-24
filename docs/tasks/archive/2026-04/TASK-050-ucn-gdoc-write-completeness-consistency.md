# TASK-050 — UCN GDoc write completeness + internal consistency

**Status:** [x] CODE COMPLETE (doc/archive pending)
**Opened:** 2026-04-21
**Related:** Surfaced by the TASK-044 E2E review (Q6). Pairs with `TASK-048` (lifecycle write discipline — provides the canonical challenge state this task reconciles against) and `TASK-049` (ledger schema v3 — the derivation source for ledger-side challenge columns). The Challenge Tracker row date/evidence discipline is handled by an extended TASK-048 bullet.
**Related files:**
- Writer: `prestonotes_gdoc/update-gdoc-customer-notes.py` (timestamp fix + section fill guarantees + run-log write + cross-section reconciliation + Deal Stage Tracker motion capture)
- Playbook: `docs/ai/playbooks/update-customer-notes.md` (Steps 6–10 — plan build, reconciliation, write)
- Rules: `.cursor/rules/20-orchestrator.mdc` (UCN contract), `.cursor/rules/21-extractor.mdc` (per-section extraction rules), `.cursor/rules/11-e2e-test-customer-trigger.mdc` (E2E acceptance bullets)
- References: `docs/ai/gdoc-customer-notes/README.md` (mutation packs), `docs/ai/references/daily-activity-ai-prepend.md`, `docs/ai/references/exec-summary-template.md`
- Tests: `prestonotes_gdoc/` test suite (append_with_history timestamp, run-log entry shape, cross-section reconciler)
- Fact-check ground truth: `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/*.txt`, live GDoc `1f3L3c7vbHbQk1URA3ZWH4IpKRM6uvgQp3yGpir6Mz1U`

---

## Problem

The TASK-044 E2E run produced a customer notes GDoc that is clean of harness vocabulary and factually correct **where it wrote anything** — but it is **grossly underfilled** and **internally inconsistent** with its own lifecycle data. Seven concrete defects against the `_TEST_CUSTOMER` GDoc read on 2026-04-21:

**D1. `append_with_history` writes have `timestamp: null`** on every populated field.
All six entries in `exec_account_summary.top_goal`, `exec_account_summary.risk`, and `exec_account_summary.upsell_path` have `"timestamp": null`. After N runs there is no way to sort entries by recency, detect stale content, or drive the `customer-notes-mutation-rules` review flow. This is a **writer-schema bug** — the `append_with_history` strategy's entire purpose is the history, and the writer omits the timestamp.

**D2. Cross-section inconsistency inside a single UCN run.**
For the Splunk / SOC-budget challenge:
- `exec_account_summary.risk` entry 2 says: *"Splunk connector still has **no PO** under SOC budget rules, but finance approved a **Q2 evaluation path** — keep Splunk renewal risk distinct from Cloud purchase momentum."*
- `challenge_tracker` row 1 for the same challenge: `status: Open`.

On 2026-03-28 the customer said verbatim: *"track that as in progress instead of stalled."* The Risk writer honored the directive. The Challenge Tracker row writer didn't. Two mutations in one plan, same challenge, different states.

**D3. Section fill rate ~20%.**
Of ~25 populatable fields across the GDoc, only 5 were written:
- `exec_account_summary.top_goal` / `risk` / `upsell_path`
- `cloud_environment.csp_regions`
- `cloud_environment.idp_sso`

The following all have explicit, quotable transcript signal and were left empty:

| Section | Signal present in transcripts |
|---|---|
| `company_overview.free_text` | 100% Azure / Okta standardization / AcmeCorp acquisition |
| `contacts.free_text` | John Doe (Exec Sponsor), Jane Smith (Champion, departing), SE |
| `org_structure.free_text` | Okta hub + child tenants from acquisition |
| `cloud_environment.platforms` | Kubernetes + DaemonSet rollout |
| `cloud_environment.devops_vcs` | GitHub Actions (shift-left 4/11) |
| `cloud_environment.security_tools` | Splunk, Prisma (retired), Wiz CLI |
| `cloud_environment.ticketing` | Jira |
| `use_cases.free_text` | DSPM/PII guardrails, shift-left secrets, DaemonSet sensor, acquisition onboarding |
| `workflows.free_text` | Jira auto-routing, SIEM routing workaround, monthly exec readout cadence |
| `accomplishments.free_text` | 900/1000 coverage, Wiz Score 92%, Prisma retired, 15-min acquisition visibility, kubelet resolved, sensor unblocked |
| `account_motion_metadata.exec_buyer` | John Doe — explicit: *"officially stepping in as your Executive Sponsor"* |
| `account_motion_metadata.champion` | Jane Smith (note departure) |
| `account_motion_metadata.sensor_coverage_pct` | 90% (900/1000 workloads) |
| `account_motion_metadata.critical_issues_open` | 12 (QBR: *"12 toxic combinations"*) |

**D4. Daily Activity Logs covers 3 of 8 in-scope calls.**
Got prepends for: 2026-03-24 Sensor POV kickoff, 2026-03-28 Cloud close, 2026-04-18 QBR.
Missing prepends for: 2026-04-01 procurement, 2026-04-04 exec readout, 2026-04-08 DSPM, 2026-04-11 shift-left, 2026-04-15 runtime hardening.

Per `daily-activity-ai-prepend.md` each call in the lookback window should produce one prepend. The 5 missing prepends are an execution gap, not a design choice.

**D5. Deal Stage Tracker ignores two active motions.**
- `defend: not-active` — but `exec_account_summary.upsell_path` entry 1 says *"pair with Defend routing guidance once budget unlocks."* That's a discovery-stage motion, not `not-active`.
- `code: not-active` — the 2026-04-11 shift-left call explicitly covers Wiz CLI in GitHub Actions (a Wiz Code motion). The UCN mutation plan (`tmp/ucn-test-customer-mutations.json`) even proposed a `Wiz Code — expand governed CLI/GitHub Actions coverage` upsell entry; it was written to Exec Summary but the Deal Stage Tracker row wasn't touched.

**D6. `appendix.agent_run_log` is empty.**
It is an `append_with_history` field designed to record what each UCN run did. UCN ran twice during the E2E and wrote zero run-log entries. Per `20-orchestrator.mdc` the run log should capture: run date, sections touched, counts, skipped-with-reason.

**D7. Writer does not emit a per-run summary that operators can audit.**
Operator has no machine-parsable record of "what did UCN do this run?" beyond reading the GDoc by eye. The agent run log (D6) is half the answer; a compact `{run_date, sections_touched, entries_added, entries_skipped_with_reason}` log entry closes it.

The write path is reliable (no crashes, no corruption). The failure mode is **what the writer chooses to do and track** — not whether it can do it.

---

## Goals

1. **Every `append_with_history` entry carries a timestamp.** The writer stamps `timestamp = <run_date>` (ISO) on every new entry; existing null-timestamp entries stay null (not retroactively rewritten — append-only).
2. **Cross-section reconciliation before write.** UCN's mutation plan passes through a reconciliation step: same challenge ID must have the same state across Exec Summary Risk bullet, Challenge Tracker row status, and `challenge-lifecycle.json`. Discrepancies are resolved against the lifecycle JSON (single source of truth) before the plan is finalized.
3. **Section fill rate ≥ 80%** of populatable fields where in-scope transcripts contain explicit signal. UCN's planner iterates *every* populatable field and either proposes a write or records a skip reason.
4. **DAL prepend per call.** Every call in the UCN lookback window (per current rule: < 1 month for raw transcripts) produces exactly one Daily Activity Logs prepend, structured per `daily-activity-ai-prepend.md`.
5. **Deal Stage Tracker motion capture.** Whenever Exec Summary `upsell_path` cites a SKU narrative, the corresponding Deal Stage Tracker row is updated (stage advanced: `not-active` → `discovery` → `pov` → `win`; `activity: active`; `reason` cites the call date).
6. **Every UCN run appends one `appendix.agent_run_log` entry.** Compact structured entry: run date, sections touched, entries added count, entries skipped list with reasons.
7. **Explicit skip-with-reason accounting.** For any populatable field left empty after UCN completes, the run-log entry or the plan output records why (e.g., `skipped:company_overview.free_text reason=no_in_scope_transcript_signal`).
8. **No writer regression on existing correct behavior.** Exec Summary content (factually correct in this run) stays correct; harness vocabulary stays out.

---

## Scope

### A) Timestamp fix (D1) — `prestonotes_gdoc/update-gdoc-customer-notes.py`

- Locate the `append_with_history` write path; `timestamp` is currently emitted as `null` or omitted.
- Set `timestamp = <run_date ISO>` on every new entry created in this run. `run_date` is the UCN run date (today's date per UCN Step 11 convention — same value that flows into the ledger `run_date` column in TASK-049).
- Existing entries with `timestamp: null` are **left alone** (append-only contract — no backfill).
- Add a unit test: invoking the writer on a fixture with one new `append_with_history` entry produces an entry whose `timestamp` parses as today's ISO date.

### B) Cross-section reconciliation (D2) — UCN mutation planner

- Before the mutation plan is approved/written, run a **reconciliation pass**:
    1. Build the authoritative challenge-state view from `challenge-lifecycle.json` (post-TASK-048).
    2. For every proposed mutation that references a challenge (by id in `notes_references`, or by theme key, or by substring match on canonical challenge descriptors), verify its asserted state matches the lifecycle view.
    3. If mismatch: **rewrite the mutation** to match the lifecycle view, and record the reconciliation in the run-log entry (D6).
- Challenge Tracker row `status` mapping from lifecycle state is authoritative:
    - lifecycle `identified` → Challenge Tracker `Open`
    - lifecycle `in_progress` → Challenge Tracker `In Progress`
    - lifecycle `stalled` → Challenge Tracker `Stalled`
    - lifecycle `resolved` → Challenge Tracker `Resolved` (and row soft-hidden per `customer-notes-mutation-rules.md` if that rule exists; otherwise stays visible with state)
- Exec Summary Risk entries that describe the same challenge must not contradict the above status.

### C) Section fill rate (D3) — UCN mutation planner

Rewrite Step 7 of `docs/ai/playbooks/update-customer-notes.md` ("Propose targeted updates") to require:

- **Enumerate every populatable field** in the doc section map. "Populatable" = field present in `section-sequence` / section map. Today UCN visits only a subset; make the visit exhaustive.
- For each field, planner either:
    - **Proposes a mutation** (with transcript-grounded `new_value` + `evidence_date` = call date of the citing transcript, per the extractor rule extended by TASK-048), OR
    - **Records a skip** with one of these reasons: `no_in_scope_transcript_signal`, `same_as_current_entry`, `evidence_below_confidence_threshold`, `section_off_by_opt_out`.
- Extraction rules per field (add to `.cursor/rules/21-extractor.mdc` new §"Per-section GDoc extraction"):
    - `company_overview.free_text` — industry + size + platform stance. Quote one transcript line.
    - `contacts.free_text` — every speaker named in transcripts. Include role if stated. Flag departures explicitly (e.g., `Jane Smith — Champion (departing 2026-04-25 per 2026-04-04 exec readout)`).
    - `org_structure.free_text` — identity hub, tenant structure, acquisition relationships.
    - `cloud_environment.platforms` — `tools_list` entries for container orchestrator (Kubernetes), compute (VMs), serverless.
    - `cloud_environment.devops_vcs` — CI/CD systems named in transcripts.
    - `cloud_environment.security_tools` — SIEMs, agents, CDRs named in transcripts, including retired ones with `(retired)` suffix.
    - `cloud_environment.ticketing` — ticketing tools named.
    - `use_cases.free_text` — one entry per distinct use case covered by a call.
    - `workflows.free_text` — one entry per distinct workflow/process covered.
    - `accomplishments.free_text` — one entry per quantified customer win (workload counts, retired tools, score deltas, acquisition visibility, challenge resolutions).
    - `account_motion_metadata.exec_buyer` — named exec sponsor.
    - `account_motion_metadata.champion` — named champion.
    - `account_motion_metadata.technical_owner` — named technical owner/SE counterpart.
    - `account_motion_metadata.sensor_coverage_pct` — numeric only, verbatim from transcript.
    - `account_motion_metadata.critical_issues_open` — numeric only, verbatim from transcript.
    - `account_motion_metadata.mttr_days` / `monthly_reporting_hours` — populate only when explicitly stated; otherwise skip with `no_in_scope_transcript_signal`.

### D) DAL prepend completeness (D4) — UCN + `daily-activity-ai-prepend.md`

- UCN emits one DAL prepend **per call in the lookback window**, not per chosen narrative.
- Prepend body follows the existing `2026-MM-DD — <call-topic>` / `<Section>: <content>` structure.
- Acceptance: for a customer with N transcripts in the lookback window, `daily_activity_logs.free_text` receives exactly N new date-headed groups.
- Skip reason if a call window transcript has no extractable content: log `skipped:dal_prepend call=<date> reason=empty_transcript` to the run log (D6) — but this should be rare.

### E) Deal Stage Tracker motion capture (D5)

- UCN planner reads both `exec_account_summary.upsell_path` proposed mutations and the Deal Stage Tracker current rows, then:
    - For every SKU referenced in an `upsell_path` entry: if its Deal Stage row is `not-active`, advance it to `discovery` (unless transcripts support a higher stage, in which case use that).
    - For every SKU with explicit purchase evidence (`PO signed`, `enterprise SKU purchased`): set stage to `win`.
    - For every SKU with explicit POV evidence (`Timeboxed … POV`, `POV kicked off`): set stage to `pov`.
- Update `reason` with the most recent supporting call date.
- Mapping table lives in `docs/ai/references/customer-notes-mutation-rules.md` (add section `### Deal Stage Tracker — SKU signal mapping`).

### F) Agent run log (D6 + D7) — new writer contract

- Every successful UCN run MUST append one entry to `appendix.agent_run_log` with `append_with_history` strategy. Entry shape (serialized as a short markdown bullet group):
    ```
    run_date: 2026-04-21
    sections_touched: exec_account_summary.top_goal, exec_account_summary.risk, challenge_tracker, daily_activity_logs.free_text, deal_stage_tracker, cloud_environment.csp_regions
    entries_added: 12
    entries_skipped: 7
    skipped_reasons:
      - company_overview.free_text: no_in_scope_transcript_signal
      - account_motion_metadata.mttr_days: no_in_scope_transcript_signal
      …
    reconciled: splunk_soc_budget (Risk vs Challenge Tracker status → lifecycle:stalled wins)
    lookback_window: 2026-03-21 → 2026-04-21 (30d)
    transcripts_in_scope: 8
    dal_prepends_emitted: 8
    ```
- On rejection (plan not approved): do NOT write a run-log entry (matches the existing "no ledger row on rejection" rule).
- Writer test: invoking UCN writer with a seeded plan produces exactly one new `agent_run_log` entry with all required keys present.

### G) E2E fixture + acceptance updates

- `.cursor/rules/11-e2e-test-customer-trigger.mdc` "Artifact hygiene" block (added in TASK-047) gets one more bullet: "After UCN, `appendix.agent_run_log` MUST have one new entry; `exec_account_summary.*` entries MUST have `timestamp` set."
- `docs/ai/playbooks/e2e-test-customer.md` manual verification checklist gets three bullets:
    - [ ] Every populated `append_with_history` entry has a non-null `timestamp`.
    - [ ] Challenge Tracker row `status` matches `challenge-lifecycle.json` `current_state` for every row referencing a lifecycle id.
    - [ ] `appendix.agent_run_log` has exactly 2 new entries (one per UCN round) after the E2E completes.
- Expected post-TASK-050 `_TEST_CUSTOMER` fill rate ≥ 80% of populatable fields; DAL prepends = transcripts-in-scope count; agent_run_log entries = UCN-run count.

---

## Explicit non-goals

- **No backfill of historical null timestamps.** Append-only rule applies — we stamp going forward only.
- **No GDoc schema change.** Section map / section sequence stays as-is. We're fixing writer behavior, not adding sections.
- **No new MCP tools.** All work happens in `update-gdoc-customer-notes.py` + UCN playbook/rules.
- **No change to challenge-lifecycle.json format or to the ledger.** Those are TASK-048 / TASK-049.
- **No change to call-record extraction.** That is TASK-051. TASK-050 only consumes what the transcripts directly say (UCN's extractor reads transcripts directly for GDoc mutations, independent of call-records).
- **No rewriting of factually correct existing entries.** The Exec Summary content from the TASK-044 run is accurate; it stays.
- **No auto-archival of resolved challenges.** Challenge Tracker rows whose state flips to `Resolved` stay visible; soft-hiding is out of scope.

---

## Acceptance

- [ ] `rg '"timestamp": null' MyNotes/Customers/_TEST_CUSTOMER/` — after a post-TASK-050 E2E run — returns hits only for pre-existing entries (if any); **no new** null timestamps introduced. _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] Every populated `exec_account_summary.top_goal` / `risk` / `upsell_path` entry created by UCN has `timestamp` equal to that run's run_date. _(runtime-deferred; re-check after next Run E2E Test Customer — unit tests prove the writer emits `value [YYYY-MM-DD]`, but the acceptance bar is "after a post-TASK-050 E2E run")_
- [ ] Challenge Tracker row `status` equals the lifecycle `current_state` mapping for every row whose `notes_references` cites a `lifecycle:<id>` tag. _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] Fresh `_TEST_CUSTOMER` E2E post-TASK-050 produces a GDoc with ≥ 80% of populatable fields non-empty (concrete count: ≥ 20 of 25 populatable fields by the enumeration in §C). _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] `daily_activity_logs.free_text` contains exactly one date-headed group per transcript in the lookback window (8 for `_TEST_CUSTOMER`). _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] Deal Stage Tracker `defend` and `code` rows are NOT `not-active` in the post-run GDoc — they reflect at least `discovery` with a call-date-cited reason, OR the run-log entry records why Deal Stage updates were skipped. _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] `appendix.agent_run_log` has one new entry per UCN run, each containing all keys enumerated in §F. _(runtime-deferred; re-check after next Run E2E Test Customer)_
- [ ] No GDoc cell contains harness vocabulary from the TASK-047 `FORBIDDEN_EVIDENCE_TERMS` list. _(writer change introduces no new cell-rendering path that could inject harness vocab; runtime-verified by existing E2E post-run scan.)_
- [x] Unit tests in `prestonotes_gdoc/` cover: timestamp emission, run-log entry shape, cross-section reconciliation flipping a Challenge Tracker status to match lifecycle.
- [ ] No regression in existing UCN fields that were correctly populated in TASK-044 (Exec Summary, csp_regions, idp_sso content stays factually equivalent). _(runtime-deferred; re-check after next Run E2E Test Customer)_

## Verification

1. Unit: `uv run pytest prestonotes_gdoc/` (new tests for timestamp, run-log, reconciler).
2. Integration: `Run E2E Test Customer` on a cleanly reset `_TEST_CUSTOMER`. Pull the GDoc via `read_doc` and validate against the acceptance bullets.
3. Cross-artifact consistency check: diff the Challenge Tracker rows vs `challenge-lifecycle.json` — every lifecycle-tagged row's status should map 1:1 to the lifecycle current_state.
4. Operator smoke: run UCN on a real customer with a ≥ 30-day-old newest transcript to confirm the extractor extension doesn't reject old-date evidence (date discipline matches TASK-048 — call date, any age, accepted).

## Sequencing

Land **after TASK-048** (lifecycle JSON must be clean before reconciliation can trust it) and **after TASK-049** (ledger schema v3 stabilizes the adjacent write contract so the UCN writer changes don't collide with ledger writer changes).

Full recommended order:

```
TASK-046  retire transcript-index.json
TASK-047  retire Journey Timeline; scrub harness vocab; enrich Account Summary
TASK-048  challenge lifecycle write discipline (+ Challenge Tracker row date bullet — see that task)
TASK-049  History Ledger schema v3
TASK-050  UCN GDoc write completeness + consistency   ← this task
TASK-051  call-record quality
```

---

## Output / Evidence

- Writer diffs (`prestonotes_gdoc/update-gdoc-customer-notes.py`):
    - §A (D1): added `APPEND_WITH_HISTORY_FIELDS` and `_ENTRY_TRAILING_DATE_RE`; `_format_entry_line_for_section()` now suffixes `value [YYYY-MM-DD]` only for the four `append_with_history` fields (`exec_account_summary.top_goal` / `risk` / `upsell_path`, `appendix.agent_run_log`) and only when `entry.timestamp` is truthy — roundtrip-safe, no backfill of pre-existing null timestamps.
    - §B (D2): added `_load_challenge_lifecycle`, `_lifecycle_ids_for_row`, `_reconcile_with_lifecycle`, and `LIFECYCLE_STATE_TO_TRACKER_STATUS` (`identified → Open`, `in_progress → In Progress`, `stalled → Stalled`, `resolved → Resolved`, plus `acknowledged → Open`, `reopened → In Progress`). `cmd_write` now calls the reconciler after `_reconcile_challenges_with_tracker` when `--customer-name` is supplied; each flipped row is recorded as an `applied` entry with `action=reconcile_with_lifecycle`. Added `"Stalled"` to `ALLOWED_CHALLENGE_STATUSES` so the `stalled → Stalled` mapping round-trips through the existing row validation.
    - §E (D5): added `COMMERCIAL_SKUS = {"cloud", "sensor", "defend", "code"}`, `DEAL_STAGE_POV_PHRASES`, `DEAL_STAGE_WIN_PHRASES`, plus `_sku_tokens_in_text`, `_infer_deal_stage_from_text`, `_rank_deal_stage`, `_extract_latest_call_date`, `_advance_deal_stage_from_applied`; `"discovery"` added to `ALLOWED_DEAL_STAGE_VALUES`. `cmd_write` now advances Deal Stage rows for every SKU cited in an applied `exec_account_summary.upsell_path` mutation (`not-active → discovery` by default; POV phrases promote to `pov`; purchase phrases promote to `win`; `activity` flips to `active`; `reason` is rewritten with the most-recent call date parsed from the upsell line).
    - §F (D6+D7): added `_build_agent_run_log_value` and `_inject_agent_run_log_entry`; `cmd_write` appends one `appendix.agent_run_log` Entry per successful run (skips injection when `applied` is empty — mirrors the "no ledger row on rejection" rule). Entry carries `run_date`, `sections_touched`, `entries_added`, `entries_skipped`, `skipped_reasons`, `reconciled`, and — when the planner supplies them — `lookback_window`, `transcripts_in_scope`, `dal_prepends_emitted`; renders with a trailing `[YYYY-MM-DD]` via the §A formatter.
- Tests (new): `prestonotes_gdoc/tests/conftest.py` (session-scoped `pn_gdoc_writer` fixture that loads the hyphenated module via importlib + sys.modules pre-registration so dataclass string annotations resolve); `prestonotes_gdoc/tests/test_task_050_ucn_writer.py` (15 cases: 4 for §A timestamp emission, 4 for §B lifecycle reconciliation, 3 for §E Deal Stage motion capture, 4 for §F run-log entry shape + roundtrip).
- Playbook + rule diffs:
    - `docs/ai/playbooks/update-customer-notes.md` — Steps 6–10 rewritten: Step 6 calls out prepend-per-call (§D) + the populatable-field walk (§C); Step 8 adds the 15-field enumeration + four skip reasons (§C); Step 10 documents the writer-side §A timestamp emission, §B reconciliation pass, §E Deal Stage motion capture, and §F agent_run_log append.
    - `.cursor/rules/21-extractor.mdc` — new § **Per-section GDoc extraction (TASK-050 §C)** enumerates the 15 populatable fields verbatim with extraction rules + the mttr_days / monthly_reporting_hours skip guidance.
    - `docs/ai/references/customer-notes-mutation-rules.md` — new `### Deal Stage Tracker — SKU signal mapping` subsection under § Mutation Actions Reference documents `COMMERCIAL_SKUS` / `DEAL_STAGE_POV_PHRASES` / `DEAL_STAGE_WIN_PHRASES` and the `upsell → discovery / pov / win` promotion rules + row-level side effects + rank guard.
    - `.cursor/rules/20-orchestrator.mdc` — UCN contract Execute Step 2 now cites the §B lifecycle reconciler (writer rewrites Challenge Tracker row `status` to match lifecycle JSON) and the §F agent_run_log append (one entry per successful run; none on rejection).
    - `.cursor/rules/11-e2e-test-customer-trigger.mdc` — Artifact hygiene block adds the TASK-050 §G bullet: "After UCN, `appendix.agent_run_log` MUST have one new entry; `exec_account_summary.*` entries MUST have `timestamp` set."
    - `docs/ai/playbooks/e2e-test-customer.md` — manual verification checklist adds the three §G bullets (timestamp on every populated append_with_history entry; Challenge Tracker status vs lifecycle parity; exactly 2 new agent_run_log entries after the E2E).
    - `docs/ai/references/daily-activity-ai-prepend.md` — opening paragraph rewritten for prepend-per-call (one prepend per in-lookback call, not per narrative); empty-transcript skip routes to the `agent_run_log` `skipped:dal_prepend call=<date> reason=empty_transcript` line.
    - `docs/ai/references/exec-summary-template.md` — **no change** — the `<value> [YYYY-MM-DD]` shape is a GDoc Exec Account Summary rendering detail, not user-facing in the Account Summary template (this file describes the `Run Account Summary` artifact, not the GDoc).
- Post-task `_TEST_CUSTOMER` GDoc fill-rate count vs acceptance: **runtime-deferred — re-check after next Run E2E Test Customer.**
- Post-task `appendix.agent_run_log` contents: **runtime-deferred — re-check after next Run E2E Test Customer.**
- Cross-artifact consistency check (Challenge Tracker vs lifecycle): **runtime-deferred — verification step 3 is runtime-only.**
- Operator-safety run (≥ 30-day-old transcript) result: **runtime-deferred — verification step 4 is runtime-only.**
- Verification evidence (unit tests, from /tester):
    ```
    uv run pytest prestonotes_gdoc/tests/  →  15 passed
    uv run pytest                          →  92 passed, 1 skipped
    uv run ruff check .                    →  All checks passed!
    bash scripts/ci/check-repo-integrity.sh →  OK
    ```

## Handoff / follow-ups

- Runtime-only acceptance bullets (1–7, 9) stay `[ ]` with the `runtime-deferred; re-check after next Run E2E Test Customer` annotation. The orchestrator / operator re-runs the E2E when they are ready; this task does not start a new run (user constraint 4).
- No scope creep into TASK-051 (call-record quality) or TASK-046–049 archive files; any behavior discovered mid-doc-pass that belongs elsewhere is to be filed as a new task by the orchestrator rather than inlined here.
