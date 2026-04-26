# TASK-051 — Call-record context quality (dense, LLM-grounded, challenge-ready)

_Previously numbered TASK-045; renumbered 2026-04-21 to resolve an ID collision with the archived `TASK-045-mcp-audit-log-under-logs-dir.md` (completed 2026-04-21, MCP audit log relocation)._

**Status:** [x] **COMPLETE** (2026-04-23). Schema v2, MCP guardrails, playbooks, goldens, and `call_records lint` shipped. **Qualitative runtime checks** (live Extract + full E2E corpus variance, UCN bounded `read_call_records`, Account Summary stakeholder surfacing) moved to **[TASK-053](../../active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) — § T053-G** and **`.cursor/agents/tester.md`** (E2E doctrine; former `docs/E2E_TEST_CUSTOMER_GUIDE.md` **retired** 2026-04-23).
**Opened:** 2026-04-21
**Depends on:** `TASK-044` (E2E harness). Not blocked by it — this task uses the harness as its regression canary.
**Related files:**
- **Canonical E2E context (read first):** [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md); procedure [`tester-e2e-ucn.md`](../../../ai/playbooks/tester-e2e-ucn.md). Call-record schema and lint: [`extract-call-records.md`](../../../ai/playbooks/extract-call-records.md), [`project_spec.md`](../../../project_spec.md) §7, **`.cursor/rules/11-e2e-test-customer-trigger.mdc`**. *(Retired file `docs/E2E_TEST_CUSTOMER_GUIDE.md` — do not restore.)*
- Playbook: `docs/ai/playbooks/extract-call-records.md`
- Rule: `.cursor/rules/21-extractor.mdc`
- Schema / IO: `prestonotes_mcp/call_records.py` (CALL_RECORD_SCHEMA), `docs/project_spec.md` §7.1–7.2
- Taxonomy: `docs/ai/references/call-type-taxonomy.md`
- Downstream consumers: `docs/ai/playbooks/update-customer-notes.md`, `docs/ai/playbooks/run-account-summary.md` (Journey Timeline was retired in TASK-047; Account Summary absorbed its narrative and is now the sole full-history call-record consumer)

---

## LLM context — *Why are we doing this?* / pros / cons / test this task alone

| Question | Answer |
| --- | --- |
| **Link to vision** | Call-records are the **compressed memory** for UCN (outside 1-month lookback) and the **core input** to Run Account Summary across the full history ([`project_spec.md` §7.1–7.2](../../../project_spec.md), [`extract-call-records.md`](../../../ai/playbooks/extract-call-records.md)). Quality stubs collapse Account Summary, Challenge feed quality, and stakeholder inference for **all** customers, not only `_TEST_CUSTOMER`. |
| **Why this task (specifically)** | It encodes the **v2 schema** (four signal arrays, quote validation, shortcut fingerprint bans) and the **lookback split**: recent transcripts in UCN, **dense** JSON for older context — see **Goals** below and `extract-call-records` / `21-extractor` rules. |
| **Pros of completing it** | Account Summary and UCN can trust **one** structure; `python -m prestonotes_mcp.call_records lint` **fails closed** on stubs; less raw-transcript re-reading. |
| **Cons / risks** | Stricter validation can **block** `write_call_record` until the extractor is fixed — expect temporary friction. Average byte caps may require iterative tuning. **TASK-052 §J.4** (narrow E2E approval-bypass) interacts with E2E velocity — see **`.cursor/rules/11-e2e-test-customer-trigger.mdc`** (artifact hygiene, eight-step contract). |
| **How to test *only* this task** | (1) `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` — must exit 0. (2) Re-run **Extract** for a **single** transcript, then re-lint. (3) Optional: `validate_call_record_against_transcript` in tests — see `prestonotes_mcp/tests/test_call_record_*.py`. (4) Full E2E steps **3+4** and **6+7** of [tester-e2e-ucn.md](../../../ai/playbooks/tester-e2e-ucn.md) with **harness** already healthy ([TASK-052](TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) can be out of scope if call-records + transcripts are already in `MyNotes`). |

---

## Problem (observed in the TASK-044 E2E run on 2026-04-21)

Fact-check of all 8 `MyNotes/Customers/_TEST_CUSTOMER/call-records/*.json` against their source transcripts revealed that **the extractor is producing stub/template output for every meaty field**, not a true per-call extraction. Evidence (identical across all 8 records, regardless of call type or content):

| Field | Output in every record | What the transcript actually says |
|---|---|---|
| `key_topics` | `["E2E fixture"]` | Unique per call (Sensor POV, Cloud SKU close, procurement, exec readout, DSPM/PII, shift-left, runtime hardening, QBR) |
| `challenges_mentioned` | `[{ "id": "ch-stub", "description": "Fixture narrative", "status": "identified" }]` | At least 4 distinct challenges in the corpus (Splunk CDR + SOC freeze, champion exit, kubelet noise, Splunk Q2 eval path, acquisition onboarding) |
| `products_discussed` | `["Wiz Cloud", "Wiz Sensor"]` (hardcoded in all 8) | DSPM call = Wiz DSPM / CIEM; shift-left = Wiz CLI / Wiz Code; runtime = Wiz Sensor |
| `action_items` | `[{ "owner": "SE", "action": "Follow up", "due": "" }]` | Real owners + actions in transcripts ("name interim owners", "capture top 5 misconfigurations", "write down the two exceptions") |
| `sentiment` | `"positive"` (all 8) | Exec readout + QBR describe budget freeze + champion exit → at minimum `cautious` |
| `deltas_from_prior_call` | `[]` (all 8) | Real deltas exist (Splunk: in_progress → stalled; Cloud: pursue → purchased) |
| `verbatim_quotes[0].speaker` | `"John Doe"` on every record | Quoted line is often `Speaker: Jane Smith:` or `Speaker: SE:` — attribution is wrong |
| `verbatim_quotes[0].quote` | First non-header line of transcript (often starts with `"Speaker: SE:"`) | Should be a **substring** of a high-signal line, correctly attributed |
| `extraction_confidence` | `"high"` (all 8) | Content is generic; honest value is `low` |

What **is** correct: `call_id`, `date`, `call_type`, `call_number_in_sequence`, `raw_transcript_ref`, `summary_one_liner` (per-call identifiers and one-line summary were the only reliable fields before v2 hardening).

### Why this degrades the whole product

1. **Account Summary is the primary full-history call-record consumer** (Journey Timeline was retired in TASK-047) — and it was getting **thin** extractor output. On the 2026-04-21 run, AcctSummary Stakeholders and Value Realized lacked the rich signals visible in transcripts (scores, coverage, toxic combos, procurement, PII catch, etc.).
2. **Challenge lifecycle is starved of cross-call context** when call-records carry stubs. The stub `ch-stub` entry means extractor output is not feeding **Challenge Tracker / Goals / Risk / Upsell** work in UCN. **Coverage depth** (how many distinct themes land in `challenge-lifecycle.json`) is a **runtime** quality question — see TASK-053 §T053-G; do not encode fixture-specific minimum id lists in product code.
3. **Historical reuse is impossible.** Call-records are the **compressed memory** of everything older than UCN's 1-month lookback window. Today they are stubs, so UCN has **no** cheap way to remember older commitments when a recent transcript references them (e.g. "Splunk is still blocked"). UCN's current workaround — re-reading all transcripts — is unsustainable as an account matures past ~10 calls.
4. **Token budget wasted per-record.** 1.3–1.5 KB per record of boilerplate burns context for zero signal. With high-quality records we could fit 15–20 historical records in the window Account Summary consumes.

---

## Goals

1. **Every field varies per call**, grounded in transcript evidence. No field is allowed to be identical across all 8 `_TEST_CUSTOMER` calls unless it genuinely is (e.g. the same recurring participant).
2. **Dense format** — tighter JSON so ~20 call-records fit inside a reasonable **Account Summary** context window. Target **≤ 1.5 KB per record average**, **≤ 2.5 KB hard cap**, after compression of boilerplate arrays. No free-text essays; use short bullets.
3. **Challenges are first-class.** Extractor produces distinct `challenges_mentioned[].id`s per unique issue, with a canonical id scheme (`ch-<kebab>`) that UCN / challenge-lifecycle can reconcile without guessing.
4. **Goals + risks are extractable.** Add an explicit `goals_mentioned` and `risks_mentioned` field (small arrays of short bullets) so Account Summary's Goals / Risk / Upsell Path can be built by aggregating across recent calls instead of re-reading transcripts.
5. **Quotes are correctly attributed substrings** of the transcript, max 3 per call, each tied to a specific signal (challenge / goal / metric / risk).
6. **Stub-fallback is impossible.** Extractor schema and MCP write-side reject placeholder values at write time.
7. **Clear division of labor (lookback split):**
    - **UCN — recent only.** UCN continues to treat **raw transcripts within the default 1-month lookback** as its primary evidence (rank +4, unchanged). That set is small, fits comfortably in context, and gives UCN full fidelity for delta detection.
    - **UCN — targeted historical reads.** For the **few** cases where recent evidence references pre-lookback history (a challenge id, SKU, or stakeholder named in a recent transcript), UCN performs a **bounded targeted read of `call-records/*.json` by id / name**, not a full sweep. This is where dense call-records pay off inside UCN.
    - **Run Account Summary — full history.** That playbook remains the **heavy call-record consumer** across the corpus. It is the regression canary for extractor quality — if extractor output degrades, Account Summary degrades visibly while UCN (transcript-first inside lookback) can still look fine.
    - **`challenge-lifecycle.json` — still the cheap cross-call state.** UCN reads that (small) file to keep challenge continuity; call-records are only loaded when the lifecycle file points at history UCN needs to quote or verify.

---

## Scope

### A) Schema v2 — `prestonotes_mcp/call_records.py` + spec §7.1

Keep backwards compatibility for required keys from v1 (so old records still read). Add:

- `goals_mentioned: Array<{ description: string, evidence_quote?: string, category?: "adoption"|"commercial"|"operational"|"security_posture"|"stakeholder" }>` — empty array is valid.
- `risks_mentioned: Array<{ description: string, severity: "low"|"med"|"high", evidence_quote?: string }>` — empty array is valid.
- `metrics_cited: Array<{ metric: string, value: string, context?: string }>` — captures KPIs (Wiz Score, MTTR, coverage %, workload counts, etc.) in a machine-readable slot so Account Summary can trend them without re-reading transcripts.
- `stakeholder_signals: Array<{ name: string, role?: string, signal: "sponsor_engaged"|"champion_exit"|"new_contact"|"decision_maker"|"detractor", note?: string }>` — optional; catches people-movement without inflating `participants`.
- Tighten existing fields:
    - `challenges_mentioned[].id` must match `^ch-[a-z0-9][a-z0-9-]{1,40}$` (kebab) — rejects `ch-stub`.
    - `challenges_mentioned[].description` minLength 10; reject exact string `"Fixture narrative"`.
    - `key_topics` minItems 1, items minLength 3, reject exact string `"E2E fixture"`.
    - `products_discussed` enum constrained to a known Wiz SKU list (`Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz DSPM`, `Wiz CIEM`, `Wiz Code`, `Wiz CLI`, `Wiz Sensor POV`, plus `Other: <name>` escape hatch).
    - `sentiment` enum (`positive|neutral|cautious|negative`) — already defined, but add a **cross-record rule** (below) not schema-level.
    - `verbatim_quotes[].speaker` must match one of the `participants[].name` values (schema-level: `$ref` style check; implementation-level: MCP write tool verifies after validation).
    - `verbatim_quotes[].quote` must be a substring of the raw transcript (enforced at MCP `write_call_record` — not in JSON Schema). Max 3 items, each ≤ 280 chars.
    - `action_items[].owner` minLength 1; reject generic `"SE"` unless also present in participants.
    - `extraction_confidence` must downgrade to `medium` if ≥ 3 optional fields are empty, `low` if ≥ 5 are empty — enforced in MCP writer.

### B) Extractor playbook + rule — `extract-call-records.md` + `21-extractor.mdc`

- Rewrite Step 6 as a **field-by-field checklist** with transcript-grounding examples drawn from the `_TEST_CUSTOMER` fixture corpus (the same 8 calls used by TASK-044).
- Add an explicit "**banned defaults**" section: no `ch-stub`, no `Fixture narrative`, no `E2E fixture`, no hardcoded product list, no identical sentiment across calls with materially different tone. Extractor must either extract real values or downgrade `extraction_confidence`.
- Add a **sales discovery anchor** step: prompt the LLM to run a light MEDDPICC / MEDDIC pass (Metrics, Economic buyer, Decision criteria, Decision process, Pain, Champion) and populate the appropriate v2 fields (metrics_cited, stakeholder_signals, goals_mentioned, risks_mentioned). Output goes to new fields, not into `summary_one_liner`.
- Require the extractor to **read the prior 3 call-records before drafting the current one** so `deltas_from_prior_call` is populated when real state changed.

### C) MCP write-side guardrails — `prestonotes_mcp/call_records.py`

- `validate_call_record_object` runs schema then content-quality checks: banned defaults, quote substring check against the referenced transcript, speaker-in-participants, per-record size cap (≤ 2.5 KB serialized), downgrade `extraction_confidence` as described.
- `write_call_record` refuses to overwrite a `high`-confidence record with a new record that has fewer distinct fields populated (anti-regression).
- Add a small CLI: `uv run python -m prestonotes_mcp.call_records lint <customer>` that scans existing records and reports stub hits. Wire into `make check` / CI.

### D) UCN wiring — `docs/ai/playbooks/update-customer-notes.md` + `20-orchestrator.mdc`

UCN remains **transcript-first within lookback**. Do not demote raw transcripts; do not add an unconditional `read_call_records` sweep to UCN. Instead:

- Document the **lookback split** explicitly in UCN Step 4 (Sources & weights):
    - **Inside lookback (default 1 month):** raw transcripts at weight **+4** (unchanged).
    - **Outside lookback:** **do not** load raw transcripts; instead allow a **targeted** `read_call_records` call and **filter in memory** to the few records needed when Block A (Challenge Review) or the Deal Stage Tracker references history by id / SKU / name. Budget: ≤ 5 targeted records per run (no `ids=[…]` MCP parameter — caller discipline).
    - `challenge-lifecycle.json` continues to be read once per run (cheap, cross-call compressed state).
- UCN Block A (Challenge Tracker) pulls candidate challenges from (a) **transcripts within lookback** + (b) the existing entries in `challenge-lifecycle.json`. If a recent transcript names an existing `ch-*` id, UCN may load that id's call-records to cite history; otherwise it does not.
- UCN must **not** ingest call-records for calls dated within the lookback window (those are read via raw transcripts). Avoid double-counting.
- Add a short rule to `20-orchestrator.mdc`: UCN's call-record reads are **targeted and bounded**; wholesale call-record ingestion is **Run Account Summary**’s concern.
- **Run Account Summary** playbook gets a one-paragraph note pointing at the v2 fields it should prefer over transcript re-reads for anything outside the active lookback.

_Optional follow-on (out of scope):_ a thin digest file that compresses pre-lookback call-records into one bounded markdown block for cheap “memory” load — evaluate only if Account Summary context limits bite in production.

### E) Fixture regression — `tests/fixtures/e2e/_TEST_CUSTOMER/`

- Add a **golden** `expected-call-records/` directory with one JSON per v1 transcript showing a **minimum acceptable** extraction (not exact match — LLM output varies — but required non-default fields).
- TASK-044 playbook step 5 / step 8 (round-1 / round-2 Extract) gains a post-run lint: `python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` must exit 0 before UCN runs. If it fails, UCN is not attempted — the run halts and the operator fixes the extractor prompt.

---

## Explicit non-goals

- **Do not** rewrite `summary_one_liner` format — it is working and indexed downstream.
- **Do not** add automated UCN output validation — we still rely on manual GDoc review per TASK-044 (tracked under TASK-053 / **`.cursor/agents/tester.md`** §6 post-write diff).
- **Do not** touch the approval-bypass override for `_TEST_CUSTOMER` — orthogonal.
- **Do not** add a new MCP tool surface — extend existing `write_call_record` / `read_call_records` only.
- **Do not** load call-records for calls dated **inside** UCN's active lookback window — those are read via raw transcripts (no double-counting).
- **Do not** demote raw transcripts as UCN's primary evidence within lookback — they stay at weight **+4**.
- **Do not** build the `AI_Insights/call-records-digest.md` aggregation file in this task — parked as an optional follow-on to evaluate once Phases 1–4 are proven on a real long-tenured customer.

---

## Acceptance

**Implementation (this task — all met 2026-04-23):**

- [x] Schema v2 optional arrays + tightened fields + `BANNED_CALL_RECORD_DEFAULTS` + quote / size / confidence rules — see **Output / Evidence** below.
- [x] `write_call_record` transcript grounding + anti-regression — `prestonotes_mcp/server.py`.
- [x] `python -m prestonotes_mcp.call_records lint <customer>` CLI + tests — `prestonotes_mcp/tests/test_call_record_v2_validation.py` et al.
- [x] Extractor + orchestrator + UCN + Account Summary playbook wiring for lookback split and v2 field preference.
- [x] Golden `tests/fixtures/e2e/_TEST_CUSTOMER/expected-call-records/` + E2E lint gate in playbook / CI wiring (Phase 4).

**Qualitative runtime / full-E2E checks** (transcript-grounded variance, UCN read discipline, GDoc + Account Summary richness) are **not** part of this archived task — execute under **[TASK-053 § T053-G](../../active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md)** during `Run E2E Test Customer` or phased manual runs, using **`.cursor/agents/tester.md`** (§4 workflows, §6 post-write diff) and [`tester-e2e-ucn-debug.md`](../../../ai/playbooks/tester-e2e-ucn-debug.md) when debugging UCN vs GDoc.

## Verification

Manual inspection of the TASK-044 E2E artifacts (GDoc + `AI_Insights/` + `call-records/`) is the acceptance gate — no separate automated verifier. The schema + content-quality lint is the one automated check.

---

## Output / Evidence

_(Filled in as the task is executed.)_

### Phase 1 — Schema + MCP write-side guardrails

- `prestonotes_mcp/call_records.py`:
  - Extended `CALL_RECORD_SCHEMA` with schema v2 optional arrays: `goals_mentioned`, `risks_mentioned`, `metrics_cited`, `stakeholder_signals`.
  - Tightened existing fields per §A: `challenges_mentioned[].id` kebab pattern (`^ch-[a-z0-9][a-z0-9-]{1,40}$`), `challenges_mentioned[].description` `minLength: 10`, `key_topics` `minItems: 1` + item `minLength: 3`, `products_discussed` enum (Wiz SKU list) with `Other: …` escape hatch via `oneOf`, `sentiment` enum, `verbatim_quotes` `maxItems: 3` / `maxLength: 280`, `action_items[].owner` `minLength: 1`.
  - Added module-level `BANNED_CALL_RECORD_DEFAULTS = ("ch-stub", "Fixture narrative", "E2E fixture")` — separate from `FORBIDDEN_EVIDENCE_TERMS` in `prestonotes_mcp/journey.py` (that list remains ledger/lifecycle vocabulary; no duplication).
  - `validate_call_record_object(data)` now runs schema → `_check_banned_defaults` → `_check_speaker_in_participants` → `_check_size_cap` (2560-byte serialized cap) → `_downgrade_extraction_confidence` (in-place mutation documented in docstring).
  - Added `validate_call_record_against_transcript(data, customer_name)` — locates transcript under `MyNotes/Customers/<name>/Transcripts/<basename>`, rejects missing/unreadable transcripts as hard error (no invented quotes), verifies each `verbatim_quotes[].quote` is a whitespace-collapsed substring.
  - Added `main()` / `__main__` block for `python -m prestonotes_mcp.call_records lint <customer>` — scans corpus, reports per-record size, flags >1536 avg as non-zero exit, substring-scans for banned defaults + `FORBIDDEN_EVIDENCE_TERMS` safety net.
- `prestonotes_mcp/server.py` — `write_call_record` now calls `validate_call_record_against_transcript` after `validate_call_record_object`, and enforces anti-regression (refuses to overwrite a `high`-confidence record with one that has fewer populated signal fields). `_TEST_CUSTOMER` override is orthogonal to data quality — no bypass here.
- Tests added in `prestonotes_mcp/tests/test_call_record_v2_validation.py` (16 cases covering: accept-v2-arrays, reject ch-stub id / fixture narrative description / E2E fixture topic, non-enum product, orphan speaker, over-long quote, >3 quotes, size cap, confidence downgrades, quote substring check, missing transcript, anti-regression, CLI zero/non-zero corpus).
- Existing tests in `prestonotes_mcp/tests/test_call_record_tools.py` were updated with `_seed_transcript` fixture helper since write_call_record now requires transcript grounding.
- `docs/project_spec.md` §7.1 — canonical schema doc expanded to show the four v2 optional arrays (`goals_mentioned`, `risks_mentioned`, `metrics_cited`, `stakeholder_signals`) inline in the example JSON, with a lead paragraph naming `CALL_RECORD_SCHEMA` + `validate_call_record_against_transcript` as source-of-truth, documenting the kebab challenge-id pattern, Wiz-SKU enum, 2560-byte cap, `BANNED_CALL_RECORD_DEFAULTS`, anti-regression, confidence-downgrade rule, and the `python -m prestonotes_mcp.call_records lint <customer>` operator CLI.

### Phase 2 — Extractor playbook + rule rewrite

- `docs/ai/playbooks/extract-call-records.md` Step 6 rewritten as field-by-field checklist with `_TEST_CUSTOMER`-corpus examples, banned-defaults callout (`ch-stub`, `Fixture narrative`, `E2E fixture`, hardcoded products, flat-sentiment), MEDDPICC anchor mapping to v2 arrays (`metrics_cited`, `stakeholder_signals`, `goals_mentioned`, `risks_mentioned`) — summary format untouched — and an explicit instruction to read the prior 3 call-records before drafting so `deltas_from_prior_call` reflects real state change. Step count preserved at 9.
- `.cursor/rules/21-extractor.mdc` field discipline block now aligns with schema v2: kebab challenge ids, quote/participant rules, enum-constrained `products_discussed`, optional-field emptiness → downgrade contract, banned-defaults pointer to `BANNED_CALL_RECORD_DEFAULTS`, MEDDPICC table. Challenge-lifecycle, ledger, GDoc sections preserved.
- `docs/ai/playbooks/test-call-record-extraction.md` (QA playbook) — added `lint` CLI as a recommended Step 0 precondition, expanded Step 8 human-check table to cover schema v2 fields (`metrics_cited`, `stakeholder_signals`, `goals_mentioned`, `risks_mentioned`), quote constraints (≤ 3 / ≤ 280 chars / speaker ∈ participants), kebab challenge ids, per-call SKU variance, and sentiment variance (flat-`positive` is the stub fingerprint). References section now points at `call_records.py`, `test_call_record_v2_validation.py`, and this task file.

### Phase 3 — UCN wiring

- `docs/ai/playbooks/update-customer-notes.md` Step 4 — added a "Lookback split — transcripts vs call-records" subsection. Inside lookback: raw transcripts at +4 (unchanged); do **not** load call-records for those calls (no double-counting). Outside lookback: no raw transcripts; targeted `read_call_records` result filtered in-memory to ≤ 5 specific records by `call_id` / `raw_transcript_ref` when Block A / Deal Stage Tracker references history by id/SKU/name. Documented caller discipline (no `ids=[…]` parameter added — explicit non-goal).
- `.cursor/rules/20-orchestrator.mdc` — added "Call-record reads inside UCN (TASK-051 §D)" section codifying the same rules at rule-file level; calls out that wholesale call-record ingestion is **Run Account Summary**’s job (Journey Timeline retired in TASK-047).
- `docs/ai/playbooks/run-account-summary.md` — added a paragraph preferring v2 fields (`metrics_cited`, `stakeholder_signals`, `goals_mentioned`, `risks_mentioned`) over transcript re-reads for anything outside the active lookback.
- Task file Related files line 13 fixed — replaced `run-journey-timeline.md` with `docs/ai/playbooks/run-account-summary.md` + rationale.

### Phase 4 — E2E regression run (TASK-044)

- `tests/fixtures/e2e/_TEST_CUSTOMER/expected-call-records/` created with 6 golden JSON records (one per v1 transcript) — each passes schema v2 validation, populates ≥ 1 `metrics_cited` + ≥ 1 `stakeholder_signals`, has `sentiment: "cautious"` on exec_qbr-1, uses per-call `products_discussed` (DSPM call → Wiz DSPM / CIEM; shift-left → Wiz Code / Wiz CLI; runtime → Wiz Sensor). Corpus: 6 records, 9162 bytes total, avg 1527 bytes (under the 1536 lint threshold), max 1605 bytes (under 2560 hard cap). Includes `README.md` documenting these are "minimum acceptable" targets, not strict-equality matches.
- `docs/ai/playbooks/tester-e2e-ucn.md` Steps 5 and 8 now include a REQUIRED shell gate: `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` must exit 0 before UCN runs in Steps 6 and 9 respectively. `.cursor/rules/11-e2e-test-customer-trigger.mdc` reflects the same gate.
- `scripts/ci/required-paths.manifest` — added the six golden JSON paths + README + `prestonotes_mcp/call_records.py`.
- `.github/workflows/ci.yml` — added a guarded "Call-record lint" step that runs `python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` only when `MyNotes/Customers/_TEST_CUSTOMER/call-records` is materialized; otherwise prints a skip message. No-op on a fresh clone.
- **Runtime / manual E2E acceptance** is tracked in **TASK-053 § T053-G** (not here). The automated gate (`lint _TEST_CUSTOMER` exit 0) is proven against the golden corpus.

### Commands run

- `uv run pytest -q` — 108 passed, 1 skipped.
- `uv run pytest prestonotes_mcp/tests/` — 84 passed, 1 skipped (MCP surface).
- `bash .cursor/skills/test.sh` — 108 passed.
- `bash .cursor/skills/lint.sh` — all checks passed.
- `bash scripts/ci/check-repo-integrity.sh` — Repo integrity OK.
- `PRESTONOTES_REPO_ROOT=/tmp/pnotes-lint-test python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` — exit 0 (corpus avg 1527 bytes).
