# TASK-051 — Call-record context quality (dense, LLM-grounded, challenge-ready)

_Previously numbered TASK-045; renumbered 2026-04-21 to resolve an ID collision with the archived `TASK-045-mcp-audit-log-under-logs-dir.md` (completed 2026-04-21, MCP audit log relocation)._

**Status:** [ ] NOT STARTED
**Opened:** 2026-04-21
**Depends on:** `TASK-044` (E2E harness). Not blocked by it — this task uses the harness as its regression canary.
**Related files:**
- Playbook: `docs/ai/playbooks/extract-call-records.md`
- Rule: `.cursor/rules/21-extractor.mdc`
- Schema / IO: `prestonotes_mcp/call_records.py` (CALL_RECORD_SCHEMA), `docs/project_spec.md` §7.1–7.2
- Taxonomy: `docs/ai/references/call-type-taxonomy.md`
- Downstream consumers: `docs/ai/playbooks/update-customer-notes.md`, `run-account-summary.md`, `run-journey-timeline.md`

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

What **is** correct: `call_id`, `date`, `call_type`, `call_number_in_sequence`, `raw_transcript_ref`, `summary_one_liner` (also present in `transcript-index.json` — the only field with real per-call signal).

### Why this degrades the whole product

1. **Account Summary + Journey Timeline are the primary call-record consumers — and they are getting thin output.** On the 2026-04-21 run, AcctSummary Stakeholders had 3 rows and Value Realized had 3 bullets — none of the rich signals above (Wiz Score 92%, 900/1000 scanned, 10k CVSS → 12 toxic combos, Prisma decommissioned, SOC2 evidence automation, Jira auto-routing, AcmeCorp PII bucket catch) surfaced.
2. **Challenge lifecycle is starved of cross-call context.** The stub `ch-stub` entry means extractor output is not feeding the **Challenge Tracker / Goals / Risk / Upsell Path** lifecycle. `challenge-lifecycle.json` only has 2 ids on the current run; a real deployment needs ≥ 4 based on the transcript corpus (Splunk budget freeze, champion exit, kubelet noise, Splunk Q2 eval path).
3. **Historical reuse is impossible.** Call-records are the **compressed memory** of everything older than UCN's 1-month lookback window. Today they are stubs, so UCN has **no** cheap way to remember older commitments when a recent transcript references them (e.g. "Splunk is still blocked"). UCN's current workaround — re-reading all transcripts — is unsustainable as an account matures past ~10 calls.
4. **Token budget wasted per-record.** 1.3–1.5 KB per record of boilerplate burns context for zero signal. With high-quality records we could fit 15–20 historical records in the window Account Summary consumes.

---

## Goals

1. **Every field varies per call**, grounded in transcript evidence. No field is allowed to be identical across all 8 `_TEST_CUSTOMER` calls unless it genuinely is (e.g. the same recurring participant).
2. **Dense format** — tighter JSON so ~20 call-records fit inside a reasonable Account-Summary / Journey-Timeline context window. Target **≤ 1.5 KB per record average**, **≤ 2.5 KB hard cap**, after compression of boilerplate arrays. No free-text essays; use short bullets.
3. **Challenges are first-class.** Extractor produces distinct `challenges_mentioned[].id`s per unique issue, with a canonical id scheme (`ch-<kebab>`) that UCN / challenge-lifecycle can reconcile without guessing.
4. **Goals + risks are extractable.** Add an explicit `goals_mentioned` and `risks_mentioned` field (small arrays of short bullets) so Account Summary's Goals / Risk / Upsell Path can be built by aggregating across recent calls instead of re-reading transcripts.
5. **Quotes are correctly attributed substrings** of the transcript, max 3 per call, each tied to a specific signal (challenge / goal / metric / risk).
6. **Stub-fallback is impossible.** Extractor schema and MCP write-side reject placeholder values at write time.
7. **Clear division of labor (lookback split):**
    - **UCN — recent only.** UCN continues to treat **raw transcripts within the default 1-month lookback** as its primary evidence (rank +4, unchanged). That set is small, fits comfortably in context, and gives UCN full fidelity for delta detection.
    - **UCN — targeted historical reads.** For the **few** cases where recent evidence references pre-lookback history (a challenge id, SKU, or stakeholder named in a recent transcript), UCN performs a **bounded targeted read of `call-records/*.json` by id / name**, not a full sweep. This is where dense call-records pay off inside UCN.
    - **Account Summary + Journey Timeline — full history.** These two playbooks remain the **heavy call-record consumers** and read the full cross-call corpus. They are the regression canary for extractor quality — if extractor output degrades, their output degrades visibly and UCN stays unaffected.
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
    - **Outside lookback:** **do not** load raw transcripts; instead allow a **targeted** `read_call_records(ids=[…])` call when Block A (Challenge Review) or the Deal Stage Tracker references history by id / SKU / name. Budget: ≤ 5 targeted records per run.
    - `challenge-lifecycle.json` continues to be read once per run (cheap, cross-call compressed state).
- UCN Block A (Challenge Tracker) pulls candidate challenges from (a) **transcripts within lookback** + (b) the existing entries in `challenge-lifecycle.json`. If a recent transcript names an existing `ch-*` id, UCN may load that id's call-records to cite history; otherwise it does not.
- UCN must **not** ingest call-records for calls dated within the lookback window (those are read via raw transcripts). Avoid double-counting.
- Add a short rule to `20-orchestrator.mdc`: UCN's call-record reads are **targeted and bounded**; wholesale call-record ingestion is an Account Summary / Journey Timeline concern.
- Account Summary and Journey Timeline playbooks get a one-paragraph note pointing at the v2 fields they should prefer over transcript re-reads for anything outside the active lookback.

_Optional follow-on (out of scope — flagged for a future task):_ a thin `AI_Insights/call-records-digest.md` regenerated by Journey Timeline that compresses all pre-lookback call-records into one bounded markdown block UCN could load as a single cheap "memory" file. Evaluate after Phases 1–4 ship.

### E) Fixture regression — `tests/fixtures/e2e/_TEST_CUSTOMER/`

- Add a **golden** `expected-call-records/` directory with one JSON per v1 transcript showing a **minimum acceptable** extraction (not exact match — LLM output varies — but required non-default fields).
- TASK-044 playbook step 5 / step 8 (round-1 / round-2 Extract) gains a post-run lint: `python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` must exit 0 before UCN runs. If it fails, UCN is not attempted — the run halts and the operator fixes the extractor prompt.

---

## Explicit non-goals

- **Do not** rewrite `summary_one_liner` format — it is working and indexed downstream.
- **Do not** change `transcript-index.json` shape (it already captures what it should).
- **Do not** add automated UCN output validation — we still rely on manual GDoc review per TASK-044.
- **Do not** touch the approval-bypass override for `_TEST_CUSTOMER` — orthogonal.
- **Do not** add a new MCP tool surface — extend existing `write_call_record` / `read_call_records` only.
- **Do not** load call-records for calls dated **inside** UCN's active lookback window — those are read via raw transcripts (no double-counting).
- **Do not** demote raw transcripts as UCN's primary evidence within lookback — they stay at weight **+4**.
- **Do not** build the `AI_Insights/call-records-digest.md` aggregation file in this task — parked as an optional follow-on to evaluate once Phases 1–4 are proven on a real long-tenured customer.

---

## Acceptance

Re-running the TASK-044 harness end-to-end (`Run E2E Test Customer`) must show:

- [ ] All 8 round-1 records + 2 round-2 records have distinct `key_topics`, distinct `challenges_mentioned[].id`s where warranted (≥ 3 distinct ids across the 10 records), and per-call `products_discussed` that reflect the actual SKUs discussed.
- [ ] No record contains `"ch-stub"`, `"Fixture narrative"`, `"E2E fixture"`. MCP `write_call_record` rejects any attempt to persist those.
- [ ] `verbatim_quotes[].speaker` matches a participant name for every quote; quote string is a substring of the referenced transcript (lint pass).
- [ ] `sentiment` varies across the corpus — at least one `cautious` record (exec readout or QBR where budget freeze / champion exit dominate).
- [ ] `action_items[].owner` is a named individual (not "SE") in at least 60% of records where the transcript names an owner.
- [ ] `deltas_from_prior_call` is populated on ≥ 4 of the 10 records (the corpus contains at least 4 genuine state changes: Splunk identified→in_progress→stalled, champion identified→in_progress, Cloud pursue→purchased, Sensor evaluate→POV).
- [ ] Each record serialized ≤ 2.5 KB; corpus average ≤ 1.5 KB. (Current corpus is 1.35–1.48 KB per record but 100% boilerplate — density, not raw size, is the target.)
- [ ] UCN Block A Challenge Tracker is materially richer (≥ 4 distinct challenge rows on the `_TEST_CUSTOMER` GDoc, not 2 as in the 2026-04-21 run) — driven primarily by transcripts-within-lookback + `challenge-lifecycle.json`, with at most a targeted call-record read per referenced id.
- [ ] UCN does **not** perform a wholesale `read_call_records()` sweep. Any call-record read during UCN is id-scoped and ≤ 5 records per run. (Verified by inspecting the agent transcript of the TASK-044 re-run.)
- [ ] Account Summary Stakeholders table surfaces `stakeholder_signals` from call-records (champion exit, sponsor engagement) **without** re-reading transcripts for any call older than the lookback window.
- [ ] Journey Timeline cites at least one pre-lookback call-record by `call_id` in its narrative when the corpus has pre-lookback history (establishes the "historical memory" pattern working).
- [ ] `python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` exits 0.

## Verification

Manual inspection of the TASK-044 E2E artifacts (GDoc + `AI_Insights/` + `call-records/`) is the acceptance gate — no separate automated verifier. The schema + content-quality lint is the one automated check.

---

## Output / Evidence

_(Filled in as the task is executed.)_

### Phase 1 — Schema + MCP write-side guardrails

-

### Phase 2 — Extractor playbook + rule rewrite

-

### Phase 3 — UCN wiring

-

### Phase 4 — E2E regression run (TASK-044)

-
