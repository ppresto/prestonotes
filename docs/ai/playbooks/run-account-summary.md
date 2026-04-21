# Playbook: Run Account Summary

Trigger:

- `Run Account Summary for [CustomerName]`

Purpose: produce a **structured exec + account narrative** in chat using `docs/ai/references/exec-summary-template.md`. This playbook is **read-heavy** — it does not require writes to customer notes. Optionally append a short **`log_run`** entry only if the user asks you to record the run in the audit trail.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

> **Source hygiene:** Prefer **per-call** `Transcripts/*.txt` when present; **`read_transcripts`** MCP is the primary way to pull transcript text. **`_MASTER_TRANSCRIPT_*.txt`** is a legacy fallback. Call **`sync_notes`** MCP (optional customer scope) **or** `./scripts/rsync-gdrive-notes.sh` from repo root before deep reads.

---

## Persisting the AI Account Summary artifact (TASK-037 approach B)

- Canonical file path: `MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-AI-AcctSummary.md`.
- Current MVP behavior: this playbook generates the summary in chat; there is no dedicated MCP write tool for this artifact yet.
- When the user wants the file saved, instruct a manual save flow: copy final markdown output, create/update the file at the canonical path, then run `sync_notes` or `scripts/rsync-gdrive-notes.sh "[CustomerName]"` so the mirror and Drive stay aligned.
- Keep section headings aligned with `docs/ai/references/exec-summary-template.md`; use `docs/examples/Dayforce-AI-AcctSummary.md` as a shape example when available.

---

## Communication Rule

At every step, tell the user what you are doing in plain English. Start each step with: `"Step X of 8 — [what I'm doing]"`. Follow the format rules in `.cursor/rules/15-user-preferences.mdc`.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`**.
- After multi-step work, finish with **`### Activity recap`** listing completed reads, unresolved gaps, and optional follow-ups.
- Explicitly state whether the summary stayed in chat only or was manually saved to file.

---

## Step 1 of 8 — Setup checks

1. Run **`sync_notes`** MCP with `[CustomerName]` when you need fresh markdown exports **or** run `./scripts/rsync-gdrive-notes.sh` from repo root.
2. Call **`check_product_intelligence`** if the account summary will cite Wiz product or licensing details; refresh or note staleness if needed.
3. For Wiz product, licensing, or integration facts: query **Wiz MCP** (`wiz_search_wiz_docs` or your configured Wiz docs tool) before asserting capabilities. If docs are unavailable, mark those bullets **provisional**.

**Tell user:** "Step 1 of 8 — Setup checks passed."

---

## Step 2 of 8 — Resolve document identity

1. **`discover_doc`** MCP with `customer_name=[CustomerName]` to obtain the current **`doc_id`** (and confirm the customer folder exists).
2. If discovery fails, stop, tell the user what is missing (sync path, customer name spelling, or bootstrap), and do not continue.

**Tell user:** "Step 2 of 8 — Document identity resolved for [CustomerName]."

---

## Step 3 of 8 — Read structured notes

1. **`read_doc`** MCP with the `doc_id` from Step 2 (`include_internal` per user preference; default true for internal prep).
2. Optionally **`read_audit_log`** if recent human or automation runs matter for "what changed since last summary."

**Tell user:** "Step 3 of 8 — Read doc export for [CustomerName]."

---

## Step 3.5 of 8 — Read persisted challenge lifecycle

1. **`read_challenge_lifecycle`** MCP with `customer_name=[CustomerName]`.
2. If the tool returns `{"error": "file not found", ...}` (first run, or the customer has no approved lifecycle writes yet), note **"no persisted lifecycle yet"** in your working state and move on — Step 7 will flag the challenge review as unavailable instead of inferring state silently.
3. If the tool returns data, treat the JSON as the **source of truth** for `current_state`, `history[]`, and `last_updated` per challenge id. **Do not** infer lifecycle state from call records when persisted JSON is present — the JSON wins.

**Tell user:** "Step 3.5 of 8 — Read persisted lifecycle ([N] challenge ids loaded / no lifecycle file yet)."

---

## Step 4 of 8 — Load ledger and call records

1. **`read_ledger`** MCP with `customer_name=[CustomerName]` and an appropriate `max_rows` (start with **20** unless the user wants deeper history).
2. **`read_call_records`** MCP for recent calls (filter by date or limit as supported) to ground challenges, value realized, stakeholder first-seen / last-seen, and the chronological call spine in **structured call metadata** — pair with transcript pulls for nuance. Records are returned sorted by `(date, call_id)`.

**Tell user:** "Step 4 of 8 — Ledger and call records loaded."

---

## Step 5 of 8 — Load weighted narrative context

Use **`docs/ai/references/customer-data-ingestion-weights.md`**. Default **lookback: 1 month** unless the user specifies **3 / 6 / 12** months.

**Load and weight (same spirit as Load Customer Context):**

1. **+4 — Transcripts:** Prefer per-call files; use **`read_transcripts`** for bounded text. Prioritize meetings within lookback for "what is true now."
2. **+3 — Daily Activity Logs:** From the doc export or `[CustomerName] Notes.md`, only dated subsections under **Daily Activity Logs** within lookback. Do not edit from this playbook.
3. **+2 — Account Summary sections:** Challenge Tracker, Company Overview, Contacts, Org Structure, Cloud Environment, Use Cases / Requirements, Workflows / Processes, Exec Goals / Risk / Upsell — from **`read_doc`** output or markdown mirror.
4. **+2 — `challenge-lifecycle.json`:** From **Step 3.5** (via MCP `read_challenge_lifecycle`). This is the **source-of-truth JSON** for challenge state and history — weighted equal to the Google Doc's Account Summary sections so Step 7's Challenge review table does not drift from persisted state.
5. **+1 — AI_Insights:** `[CustomerName]-AI-AcctSummary.md`, `[CustomerName]-History-Ledger.md`, and related files when present.

**Tell user:** "Step 5 of 8 — Weighted context loaded with lookback [1|3|6|12] month(s)."

---

## Step 6 of 8 — Normalize Wiz object language

Before stating integrations or detections posture:

1. Map customer discussions to **Defend** (`Detections -> Threats`) vs **Cloud** (`Findings -> Issues`) lanes.
2. Separate **docs-supported** claims from **recommended operating model** for this account.

**Tell user:** "Step 6 of 8 — Wiz terminology normalized for exec-safe wording."

---

## Step 7 of 8 — Compose the account summary

Emit markdown following **`docs/ai/references/exec-summary-template.md`** in order. Sections marked **(optional)** may be skipped when the user asks for an "exec-only" cut; they are **included by default** for a full account summary.

1. **Metadata (optional)** — single labeled line `Generated: YYYY-MM-DD` using today's session date. This is the **only** place the run date may appear. Every other date in the summary must be a **call date** or a **milestone date** sourced from evidence.
2. **Health (optional)** — single line `Health: 🟢|🟡|🔴|⚪ …` per **`docs/ai/references/health-score-model.md`**. Use the spec's verbatim band rules. If the corpus is thin (fewer than 2 calls or no recent data), use **⚪ Unknown** and say so.
3. **The 30-Second Brief** (≤ 3 sentences, no jargon).
4. **Challenges → Solutions Map** (table populated where evidence exists; otherwise say what is unknown).
5. **Chronological call spine (optional)** — compact table sourced from Step 4's `read_call_records` output, filtered to the lookback window by default:

   | Date | call_id | call_type | summary_one_liner | sentiment |
   |---|---|---|---|---|

   **Dates are the call dates from each record, never the run date.** Expand to the full history only on explicit user ask.
6. **Milestones (optional)** — bullets drawn from `call_type` transitions and lifecycle `history[]` entries (first discovery, first POC, first POC readout, commercial close, champion transition, renewal gate, etc.). Each bullet cites `call_id` + call date. Do not invent milestones that are not in the record.
7. **Challenge review (optional)** — table sourced from `challenge-lifecycle.json` (Step 3.5) with evidence drawn from the latest call that mentions each id:

   | challenge_id | description | current_state | last_updated | evidence | stall / risk | recommended_action |
   |---|---|---|---|---|---|---|

   - `current_state` and `last_updated` come from the lifecycle JSON (`current_state`, latest `history[].at`).
   - `evidence` cites the latest `call_id` (or short quote) mentioning the challenge.
   - `stall / risk` flags **stall** when `current_state` is `identified`, `acknowledged`, or `in_progress` and the days since `last_updated` is **≥ 60** (per `docs/ai/references/challenge-lifecycle-model.md`). Phrase as `"no movement 65d"` with the actual count.
   - If Step 3.5 reported "no persisted lifecycle yet," render the section as a single line — `No persisted lifecycle JSON yet; run Update Customer Notes to populate challenge-lifecycle.json.` — and do not infer challenge state from call records in its place.
8. **Stakeholders** — extend the template table with **First seen** and **Last seen** columns derived from `participants[]` across call records. Sentiment signals are required when named stakeholders appear in source material.
9. **Value Realized** (dated, attributed).
10. **Strategic Position** (journey, risks, next move).
11. **Wiz Commercials** (evidence table; unknowns explicit).
12. **Open Challenges** — `identified` or `stalled` entries from the Challenge review table, with a one-line next action each.

Apply **fact attribution tags** on material claims per `docs/project_spec.md` (for example `[Verified: DATE | Name | Role]`, `[Inferred: DATE]`, `[Achieved: DATE]`).

**Tell user:** "Step 7 of 8 — Draft account summary composed from template."

---

## Step 8 of 8 — Quality gate and handoff

Verify before sending:

- 30-second brief meets **≤ 3 sentences** and **no unexplained jargon**.
- At least one row in **Challenges → Solutions Map** when the account has documented challenges; if none, state that explicitly.
- **Stakeholders** table includes **Sentiment** only when sourced; otherwise `Unknown`.
- When the **Challenge review** section is present, every row's `current_state` matches what `read_challenge_lifecycle` returned in Step 3.5 (no silent drift).
- Section dates in the **Chronological call spine** and **Milestones** are **call dates** from records, never the run date. The only place the run date may appear is the optional **Metadata** line.
- Artifact content contains **no** test-only vocabulary (`TASK-NNN`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`) per `.cursor/rules/11-e2e-test-customer-trigger.mdc` — Artifact hygiene.
- No recommendation that **requires** unlicensed products without labeling it as future / license-dependent.

Optional: if the user wants a paper trail, call **`log_run`** with a short markdown block summarizing that this playbook ran and the lookback window.

**Tell user:** "Done. Account summary for [CustomerName] is ready — ask for edits, a shorter exec-only cut, or a `log_run` if you want this recorded."
