# TASK-073 — UCN full pre-write section/subsection coverage gate (simplification-first)

**Status:** [ ] not started  
**Opened:** 2026-04-25  
**Depends on:** TASK-071, TASK-072  
**Related:** TASK-053 (quality TOC), TASK-068 (E2E honesty)

## Problem

Current pre-write validation is useful but narrow:

- `scripts/ucn-planner-preflight.py` enforces DAL parity and Deal Stage trigger path.
- Writer coverage guard enforces only four fields (`top_goal`, `risk`, `use_cases`, `workflows`).

This allows runs to pass pre-write while leaving other high-signal GDoc sections/subsections underfilled (Contacts, Challenge Tracker, Cloud tools subfields, Account Metadata identities, etc.).

## Goal

Create one **strict pre-write gate** that covers **all planner-governed** GDoc sections/subsections in the current schema and requires an explicit planner decision for each in-scope target:

- `mutate`, or
- `no_evidence` / skip with an allowed reason.

**Excluded from the strict pre-write / planner contract set** (not planner-required; do not require `mutate|skip` decisions or fail preflight if omitted):

- `discovery.free_text` — unstructured discovery notes; not a UCN contract surface.
- `appendix.free_text` — scratch / overflow; not a UCN contract surface.
- `appendix.agent_run_log` — **writer-managed**; verify after write, not planner-governed (history append, not a mutation-planning target in TASK-073).

Do this with existing files and minimal file sprawl.

## Concrete in-scope preflight / matrix targets (aligned to `doc-schema.yaml`)

The plan and preflight validator should treat the following as the **explicit** planner-governed set (path = `section_key[.field]` or table id). This list is the checklist users see; implement by cross-checking keys against `doc-schema.yaml` (and existing mutations docs), not by inventing new section names in code.

**Account Summary tab**

- `exec_account_summary.top_goal`
- `exec_account_summary.risk`
- `exec_account_summary.upsell_path`
- `challenge_tracker` (table)
- `company_overview.free_text`
- `contacts.free_text`
- `org_structure.free_text`
- `cloud_environment.csp_regions`
- `cloud_environment.platforms`
- `cloud_environment.idp_sso`
- `cloud_environment.devops_vcs`
- `cloud_environment.security_tools`
- `cloud_environment.aspm_tools`
- `cloud_environment.ticketing`
- `cloud_environment.languages`
- `cloud_environment.sizing`
- `cloud_environment.archive`
- `use_cases.free_text`
- `workflows.free_text`
- `accomplishments.free_text`

**Daily Activity tab**

- `daily_activity_logs.free_text` (meeting-block / DAL parity logic per TASK-072, not “non-empty free_text” only)

**Account Metadata tab**

- `account_motion_metadata.exec_buyer`
- `account_motion_metadata.champion`
- `account_motion_metadata.technical_owner`
- `account_motion_metadata.sensor_coverage_pct`
- `account_motion_metadata.critical_issues_open`
- `account_motion_metadata.mttr_days`
- `account_motion_metadata.monthly_reporting_hours`
- `deal_stage_tracker` (table; Deal Stage trigger path per TASK-072)

**Not in this list** — see Goal exclusions (`discovery`, `appendix` targets).

## `doc-schema.yaml` vs the coverage matrix (no confusion)

- **`doc-schema.yaml` stays the structural SSoT** for the Google Doc: section keys, field keys, `update_strategy`, tables. It defines **what exists in the document shape**.
- **TASK-073 does not add** `required_in_*`, `validator_fail_code`, or planner/coverage fields **into** `doc-schema.yaml`. That would mix “document shape” with “UCN run policy” in one file without a strong reason.
- The **canonical coverage matrix** (required yes/no/conditional, allowed actions, skip reasons, fail codes) lives in **existing markdown** (e.g. playbook + `mutations-*.md`) and is **enforced by** `ucn-planner-preflight.py` (and the planner contract in mutation JSON). The matrix is **derived from** the schema + product rules; it is **policy documentation and validator rows**, not a new layer inside the YAML unless we later decide to machine-generate (out of scope unless approved).

## Scope (existing files only; no new files unless approved)

- `prestonotes_gdoc/config/doc-schema.yaml` (shape source; read for key alignment; **not** extended with matrix columns in TASK-073)
- `docs/ai/playbooks/update-customer-notes.md` (process contract)
- `docs/ai/gdoc-customer-notes/README.md` (SSoT map)
- `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` (tab semantics)
- `docs/ai/gdoc-customer-notes/mutations-account-metadata-tab.md` (strict metadata semantics)
- `docs/ai/gdoc-customer-notes/mutations-daily-activity-tab.md` (DAL semantics)
- `docs/ai/gdoc-customer-notes/mutations-global.md` (global mechanics + quality gate)
- `scripts/ucn-planner-preflight.py` (machine gate)
- `scripts/tests/test_ucn_planner_preflight.py` (gate tests)
- `.cursor/agents/tester.md` (pointer alignment only; no duplicated section definitions)

## Design requirements

### 1) Canonical section/subsection coverage matrix (must be explicit)

The rows are the **Concrete in-scope** list above (plus TASK-072 mechanics for DAL and Deal Stage embedded in the relevant lines). Document in existing docs (not a separate file unless approved) with at least these columns:

- `target` — e.g. `exec_account_summary.top_goal` or `deal_stage_tracker` (same strings as the concrete list)
- `tab` — Account Summary / Daily Activity / Account Metadata
- `required_in_ucn_full` (yes/no/conditional) — when the human/UCN run is a **full** update (all in-scope rows must be decided: mutate or allowed skip)
- `required_in_ucn_partial` (yes/no/conditional) — when the run is **partial** (smaller required subset; defined per row, not a second schema)
- `allowed_actions`, `evidence_rule`, `allowed_skip_reasons`, `validator_fail_code`

**E2E is not a column.** End-to-end tests (e.g. `v1_full`, `v2_full`) are harnesses: they should invoke the same preflight/UCN **mode** as a production run (typically “full” for a full sync). They do not add a parallel “E2E-only required set” to the matrix. If a test run needs stricter or looser checks, that is expressed by **choosing `ucn_mode` and fixture scope**, not by new matrix dimensions.

No separate new matrix file unless explicitly approved.

### 1.1) Completeness refinements (must be explicit before implementation)

To remove ambiguity and keep implementation deterministic, TASK-073 must explicitly define all six items below in the same docs/scripts already in scope.

1. **Matrix location (single canonical source)**
   - Name the exact canonical location for the matrix in docs (primary source) and where secondary docs point to it.
   - Minimum: `docs/ai/playbooks/update-customer-notes.md` owns the matrix; `docs/ai/gdoc-customer-notes/mutations-global.md` points to it (no duplicated copy).

2. **Mode contract (`full` vs `partial`)**
   - Lock exact mode names used by planner and preflight: `full`, `partial`.
   - Define where mode is set (`planner_contract` and/or preflight flag) and how validator resolves mode when omitted.
   - E2E harnesses pass the same mode production would use; no E2E-only rule dimension.

3. **Per-target allowed actions**
   - For each concrete in-scope target, declare allowed actions (`mutate`, `skip/no_evidence`) and any target-specific constraints.
   - Include table target handling for `challenge_tracker` and `deal_stage_tracker`.

4. **Skip-reason taxonomy**
   - Define allowed skip reasons and disallowed vague reasons.
   - Require a skip reason whenever action is skip/no_evidence.

5. **Validator fail-code catalog**
   - Enumerate concrete fail codes and map each to a clear trigger condition.
   - Include coverage-missing, invalid-action, invalid/absent-skip-reason, and mode-required-set failures.

6. **Verification artifact contract**
   - Define exact evidence required for closure:
     - one intentionally incomplete mutation bundle and expected fail codes,
     - one corrected bundle and preflight pass,
     - `v1_full` post-write diff evidence showing no silent omissions for in-scope targets.

### 2) Planner contract extension

Extend planner contract (same mutation JSON) to include full coverage decisions for required targets, in addition to existing TASK-072 DAL/Deal-Stage blocks.

### 3) Pre-write validator extension

Extend `ucn-planner-preflight.py` to fail when:

- required target is missing from planner decisions,
- target decision is invalid for its allowed actions,
- skip reason is absent/invalid,
- strict evidence rules are not satisfied for metadata identities/numeric fields,
- the active **UCN mode** (e.g. full vs partial) required-set from the matrix is not met (preflight flag `--ucn-mode` or equivalent; E2E passes the same mode as production for that scenario).

### 4) Prompt/process alignment

Update Step 6/8 prompts so LLM extraction and routing explicitly covers every required section/subsection and emits decision + reason when no mutation is proposed.

### 5) Tester alignment

Keep tester as post-write quality verification, but align pointers to the same canonical coverage set (no second semantic source).

## Non-goals

- Adding new config/script files by default.
- Refactoring runtime architecture beyond coverage-gate scope.
- Replacing transcript-first evidence policy.
- Rewriting section semantics in multiple places (avoid duplication).
- Enforcing planner decisions for `discovery.free_text`, `appendix.free_text`, or `appendix.agent_run_log` (see Goal exclusions).
- Extending `doc-schema.yaml` with coverage / requirement / E2E columns; keep shape separate from UCN policy (see **doc-schema vs matrix** above).

## Acceptance

- [ ] Pre-write validator enforces full section/subsection coverage for required workflow mode.
- [ ] Every required target is represented as mutate or skip/no_evidence with allowed reason.
- [ ] Canonical coverage matrix is present in existing docs and used by playbook + validator + tester pointers.
- [ ] The six completeness refinements in `1.1` are explicitly documented and implemented (location, mode contract, allowed actions, skip reasons, fail-code catalog, verification artifacts).
- [ ] No new files added unless approved with explicit rationale.
- [ ] `_TEST_CUSTOMER` `v1_full` demonstrates:
  - preflight fails when required sections are omitted,
  - preflight passes after coverage-complete planner decisions,
  - post-write diff reports no silent coverage omissions.

## Verification

1. Unit tests for preflight fail/pass cases (`scripts/tests/test_ucn_planner_preflight.py`).
2. `v1_full` dry-run mutation bundles:
   - intentionally incomplete bundle -> expected fail codes,
   - corrected bundle -> preflight pass.
3. E2E `v1_full` write/read and tester §6 diff confirms coverage discipline.
4. Verification artifacts are attached/recorded with enough detail to reproduce:
   - mutation bundle path(s),
   - preflight command(s) and output (including fail codes),
   - post-write diff summary covering all in-scope targets.

## Simplification notes

- Keep one owner per concern:
  - Shape -> `doc-schema.yaml` (keys and strategies only)
  - Coverage / required when -> matrix in docs + preflight (not new keys in YAML unless a future approved codegen step)
  - Meaning -> `mutations-*.md`
  - Process -> `update-customer-notes.md`
  - Validation -> `ucn-planner-preflight.py`
- Prefer consolidating duplicate wording in existing files over introducing new docs.
