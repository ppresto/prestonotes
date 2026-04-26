# TASK-072 — UCN deterministic planner contract: DAL parity + Deal Stage motion

**Status:** [x] complete  
**Opened:** 2026-04-24  
**Depends on:** TASK-060 (DAL tuning), TASK-071 (tester DAL parity), TASK-050 (writer-side Deal Stage motion capture; archived complete)

## Problem

Two user-visible gaps came from the same class of failure: the mutation plan was not deterministic enough.

1. **DAL underfill:** UCN emitted one `prepend_daily_activity_ai_summary` even though six per-call transcripts were in scope.
2. **Deal Stage no-motion:** Upsell mutation used `Wiz DSPM` wording only, but writer auto-motion currently keys on `cloud|sensor|defend|code` tokens in `exec_account_summary.upsell_path`.

Result: write succeeds, but post-write quality is incomplete.

## Goal

Define and enforce a deterministic UCN planner contract so a single approved mutation bundle:

- includes one DAL prepend for every in-scope missing meeting recap, and
- always provides at least one commercial-SKU token path for expected Deal Stage motion (or explicitly records why not).

## Design Summary (single best recommendation)

Before `write_doc`, UCN must build a **deterministic mutation inventory** with two hard checks:

1. **DAL coverage check:** `missing_meetings` must map 1:1 to `prepend_daily_activity_ai_summary` mutations.
2. **Deal Stage trigger check:** any upsell intended to change commercial posture must include at least one writer-recognized SKU token (`Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz Code`) or emit an explicit `deal_stage_tracker` row mutation.

If either check fails, planner returns **incomplete plan** (no write) with machine-readable reasons.

## Scope

1. Planner/playbook contract changes (`update-customer-notes.md`, mutation docs, optional extractor rule pointers).
2. Optional planner-side preflight validator (script/module) to fail fast before `write_doc`.
3. Tester expectations alignment (refer TASK-071, no duplicated SSoT).
4. E2E proof on `_TEST_CUSTOMER` `v1_full`.

## Non-goals

- Replacing writer `advance_deal_stage_from_upsell` logic in this task (unless approved as explicit extension).
- Expanding commercial SKU vocabulary beyond current writer contract by default.
- Changing real-customer approval rules.
- Re-defining tester post-write DAL scoring rules (owned by **TASK-071**).

## Detailed Design

### A) Deterministic DAL planning contract

Inputs:
- Step 3 `read_doc` JSON (`daily_activity_logs`)
- In-lookback per-call transcripts `Transcripts/YYYY-MM-DD-*.txt`
- Existing duplicate guard semantics from DAL references

Planner algorithm:
1. Build `transcript_meetings[]` from in-scope per-call transcript files (default exclude `_MASTER_*` unless run packet says otherwise).
2. Build `doc_meeting_keys[]` from existing DAL meeting heading lines in `read_doc`.
3. Compute `missing_meetings = transcript_meetings - doc_meeting_keys` (normalized by ISO date + normalized title).
4. Emit exactly one `prepend_daily_activity_ai_summary` mutation per element in `missing_meetings`.
5. If `missing_meetings` non-empty and emitted prepend count differs, fail plan with `dal_parity_failed`.

Required planning artifact (structured, can be in run-log or sidecar):
- `transcripts_in_scope_count`
- `dal_meetings_existing_count`
- `dal_meetings_missing_count`
- `dal_prepends_emitted_count`
- `dal_skips[]` with explicit reason per skipped meeting (allowed only for no transcript / unreadable evidence)

### B) Deterministic Deal Stage trigger contract

Current writer behavior:
- Auto-motion only fires from applied `exec_account_summary.upsell_path` mutations when text includes `cloud|sensor|defend|code` tokens.

Planner contract:
1. For each upsell thread classified as commercial motion, emit an upsell line that contains a writer-recognized commercial token.
2. If upsell story uses DSPM/CIEM wording only, add either:
   - a companion commercial-SKU line (for auto-motion), or
   - explicit `deal_stage_tracker` table mutation with evidence + reason.
3. If neither is provided, fail plan with `deal_stage_trigger_missing`.

Required planning artifact:
- `upsell_lines_emitted[]` (with token extraction preview)
- `deal_stage_expected_skus[]`
- `deal_stage_trigger_mode` per SKU: `upsell_auto` | `explicit_table_mutation` | `no_change_with_reason`

### C) Preflight validator (recommended)

Add a lightweight preflight check before write (can be in playbook procedure first, code later):
- Validate DAL N vs planned prepend count parity.
- Validate any expected Deal Stage motion has a trigger path.
- Output structured failures and block write on hard errors.

Failure payload examples:
- `dal_parity_failed: expected 6 prepends, planned 1`
- `deal_stage_trigger_missing: upsell mentions dspm thread but no commercial sku token or explicit table row mutation`

### D) Write-time and post-write observability

At successful write, ensure run metadata includes:
- DAL: `transcripts_in_scope`, `dal_prepends_emitted`, `dal_missing_after_plan` (should be 0 unless documented skip)
- Deal Stage: `deal_stage_expected_skus`, `deal_stage_rows_advanced`, `deal_stage_rows_explicitly_mutated`

Tester continues independent `read_doc` verification (TASK-071) and does not trust planner claims blindly.

## Files to touch (implementation map)

| Area | Path(s) |
| --- | --- |
| UCN process contract | `docs/ai/playbooks/update-customer-notes.md` (Step 6/8 deterministic checks) |
| DAL semantics | `docs/ai/references/daily-activity-ai-prepend.md`, `docs/ai/gdoc-customer-notes/mutations-daily-activity-tab.md` |
| Deal Stage semantics | `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` (make trigger requirement explicit) |
| Optional planner rule pointer | `.cursor/rules/21-extractor.mdc` (short invariant pointer, not duplicate spec) |
| Optional code preflight | planner helper path to be chosen during implementation (likely under `prestonotes_gdoc/` or `scripts/`) |
| Tester parity | no new logic required beyond TASK-071; keep pointer only |

## Acceptance

- [x] UCN planning procedure explicitly requires DAL parity: `missing_meetings` count equals prepend mutations count (or documented skip list). *(Landed in `update-customer-notes.md` + DAL mutation docs on 2026-04-24.)*
- [x] UCN planning procedure explicitly requires Deal Stage trigger path for commercial motion (`upsell_auto` token or explicit table mutation). *(Landed in `update-customer-notes.md` + account-summary mutation docs on 2026-04-24.)*
- [x] Planner blocks write when either hard check fails, with machine-readable reason codes. *(`scripts/ucn-planner-preflight.py` + `scripts/tests/test_ucn_planner_preflight.py`, reason codes: `dal_parity_failed:*`, `deal_stage_trigger_missing:*`, etc.)*
- [x] `_TEST_CUSTOMER` `v1_full` proof shows:
  - DAL prepends emitted for all in-scope missing meetings.
  - Deal Stage row motion present when upsell intends commercial movement.
- [x] Tester post-write diff (TASK-071) reports no DAL count gap for proof run.

## Verification

Manual/E2E:
1. Run `prep-v1`, extract, lint.
2. Generate UCN mutation plan and inspect deterministic inventory fields.
3. Assert DAL and Deal Stage preflight checks pass.
4. Run write + `read_doc`.
5. Confirm DAL meeting block count equals expected transcript count (minus documented skips).
6. Confirm Deal Stage row update path exists for targeted SKU(s).

Implementation verification completed 2026-04-24:
- [x] `uv run pytest scripts/tests/test_ucn_planner_preflight.py` (5 passed)
- [x] `bash scripts/ci/check-repo-integrity.sh` (exit 0)

Strict close-out runtime proof completed 2026-04-25:
- [x] `./scripts/e2e-test-customer.sh prep-v1` (new doc id `1ITJwqPlVx9jLTb5eQtdGMnc2wtRqnqjSPc9XMjSDwRc`)
- [x] call-record extraction corpus regenerated + lint gate: `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` (6/6 OK, avg 1359 bytes)
- [x] Deterministic plan persisted at `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/ucn-approved-mutations.json`
- [x] Preflight gate passed: `uv run python scripts/ucn-planner-preflight.py --mutations ... --json-output` (`ok: true`; DAL required=6 emitted=6; expected_skus=[cloud], auto_skus=[cloud])
- [x] `write_doc` dry-run + apply completed (21 applied, 2 skipped strict metadata fields)
- [x] `read_doc` confirmed DAL headings for all six in-lookback meetings and `deal_stage_tracker.cloud.stage = discovery`
- [x] Ledger append + Drive mirror completed (`append_ledger_row` OK; `./scripts/e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"` OK)

## Rollout Notes

1. Land docs/procedure first (low-risk).
2. Add optional code preflight validator second.
3. Re-run `_TEST_CUSTOMER` `v1_full` and update related tasks with evidence links.

## Links

- `docs/tasks/active/TASK-060-ucn-daily-activity-log-component-tuning.md`
- `docs/tasks/active/TASK-071-e2e-tester-dal-meeting-count-parity-in-post-write-diff.md`
- `docs/ai/playbooks/update-customer-notes.md`
- `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md`
- `docs/ai/references/daily-activity-ai-prepend.md`
