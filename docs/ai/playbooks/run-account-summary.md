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
2. If discovery fails, stop and report what is missing (sync path, customer name spelling, or bootstrap).

**Tell user:** "Step 2 of 8 — Document identity resolved for [CustomerName]."

---

## Step 3 of 8 — Read structured notes

1. **`read_doc`** MCP with the `doc_id` from Step 2 (`include_internal` per user preference; default true for internal prep).
2. Optionally **`read_audit_log`** if recent human or automation runs matter for "what changed since last summary."

**Tell user:** "Step 3 of 8 — Read doc export for [CustomerName]."

---

## Step 4 of 8 — Load ledger and call records

1. **`read_ledger`** MCP with `customer_name=[CustomerName]` and an appropriate `max_rows` (start with **20** unless the user wants deeper history).
2. **`read_call_records`** MCP for recent calls (filter by date or limit as supported) to ground challenges, value realized, and stakeholder updates in **structured call metadata** — pair with transcript pulls for nuance.

**Tell user:** "Step 4 of 8 — Ledger and call records loaded."

---

## Step 5 of 8 — Load weighted narrative context

Use **`docs/ai/references/customer-data-ingestion-weights.md`**. Default **lookback: 1 month** unless the user specifies **3 / 6 / 12** months.

**Load and weight (same spirit as Load Customer Context):**

1. **+4 — Transcripts:** Prefer per-call files; use **`read_transcripts`** for bounded text. Prioritize meetings within lookback for "what is true now."
2. **+3 — Daily Activity Logs:** From the doc export or `[CustomerName] Notes.md`, only dated subsections under **Daily Activity Logs** within lookback. Do not edit from this playbook.
3. **+2 — Account Summary sections:** Challenge Tracker, Company Overview, Contacts, Org Structure, Cloud Environment, Use Cases / Requirements, Workflows / Processes, Exec Goals / Risk / Upsell — from **`read_doc`** output or markdown mirror.
4. **+1 — AI_Insights:** `[CustomerName]-AI-AcctSummary.md`, `[CustomerName]-History-Ledger.md`, and related files when present.

**Tell user:** "Step 5 of 8 — Weighted context loaded with lookback [1|3|6|12] month(s)."

---

## Step 6 of 8 — Normalize Wiz object language

Before stating integrations or detections posture:

1. Map customer discussions to **Defend** (`Detections -> Threats`) vs **Cloud** (`Findings -> Issues`) lanes.
2. Separate **docs-supported** claims from **recommended operating model** for this account.

**Tell user:** "Step 6 of 8 — Wiz terminology normalized for exec-safe wording."

---

## Step 7 of 8 — Compose the account summary

Emit markdown following **`docs/ai/references/exec-summary-template.md`** in order:

1. **The 30-Second Brief** (≤ 3 sentences, no jargon).
2. **Challenges → Solutions Map** (table populated where evidence exists; otherwise say what is unknown).
3. **Stakeholders** (sentiment signals required when named stakeholders appear in source material).
4. **Value Realized** (dated, attributed).
5. **Strategic Position** (journey, risks, next move).
6. **Wiz Commercials** (evidence table; unknowns explicit).
7. **Open Challenges** (`identified` / `stalled` only).

Apply **fact attribution tags** on material claims per `docs/project_spec.md`.

**Tell user:** "Step 7 of 8 — Draft account summary composed from template."

---

## Step 8 of 8 — Quality gate and handoff

Verify before sending:

- 30-second brief meets **≤ 3 sentences** and **no unexplained jargon**.
- At least one row in **Challenges → Solutions Map** when the account has documented challenges; if none, state that explicitly.
- **Stakeholders** table includes **Sentiment** only when sourced; otherwise `Unknown`.
- No recommendation that **requires** unlicensed products without labeling it as future / license-dependent.

Optional: if the user wants a paper trail, call **`log_run`** with a short markdown block summarizing that this playbook ran and the lookback window.

**Tell user:** "Done. Account summary for [CustomerName] is ready — ask for edits, a shorter exec-only cut, or a `log_run` if you want this recorded."
