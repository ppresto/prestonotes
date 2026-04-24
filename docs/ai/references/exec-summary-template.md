# Exec summary template (account summary output)

Use this structure when producing the **exec-facing** portion of an account summary (for example from **`Run Account Summary for [CustomerName]`**). Each fact should carry an attribution tag per `docs/project_spec.md` (for example `[Verified: DATE | Name | Role]`, `[Inferred: DATE]`, `[Achieved: DATE]`).

Sections marked **(optional)** may be omitted for an "exec-only" cut. They are included by default in the full account summary — they absorb the content that previously lived in the retired Journey Timeline artifact.

---

## 0. Metadata (optional)

Single labeled line at the top of the document:

> `Generated: YYYY-MM-DD`

Use today's session date. This is the **only** place the run date appears. Every other date in the summary must be a **call date** or a **milestone date** sourced from evidence, not the run date.

---

## 1. Health (optional)

Single line using the verbatim band rules from `docs/ai/references/health-score-model.md`:

> `Health: 🟢 Green — Active engagement, no stalled challenges, positive sentiment, clear next steps`
> `Health: 🟡 Yellow — …`
> `Health: 🔴 Red — …`
> `Health: ⚪ Unknown — Fewer than 2 calls or no recent data`

Pick **one** band. When bands conflict, apply the most severe band that is fully supported by evidence.

---

## 2. The 30-Second Brief

**Audience:** VP / executive skimming on mobile.

**Rules:**

- **≤ 3 sentences**, one short paragraph at most.
- Plain language only — **no product jargon**, no internal codenames, no acronyms the customer did not use on the call.
- Cover in order: **who they are**, **what problem they are solving**, **where they are in the journey**, **what the next move is**.

**Template:**

> *[Customer]* is *[one-line who they are]*. They are focused on *[plain-English problem / outcome]* and are currently *[journey state in customer words or neutral phrasing]*. The **next move** is *[single concrete action or decision]*.

---

## 3. Challenges → Solutions Map

Table columns:

| Challenge | Wiz Capability | Status | Value Delivered |
|-----------|------------------|--------|-----------------|
| … | … | … | … |

**Guidance:**

- **Challenge:** Short label tied to customer language; one row per major thread.
- **Wiz Capability:** The product or pattern that maps to the challenge (keep exec-readable).
- **Status:** Align with challenge lifecycle where applicable (`docs/ai/references/challenge-lifecycle-model.md`).
- **Value Delivered:** Outcomes already achieved, with dates and evidence tags where possible.

---

## 4. Chronological call spine (optional)

Compact table, sorted by **call date** ascending. Dates here are **always the call date from the record**, never the run date. Bounded to in-lookback calls by default; expand to full history only when the user asks.

| Date | call_id | call_type | summary_one_liner | sentiment |
|------|---------|-----------|-------------------|-----------|
| YYYY-MM-DD | … | discovery / technical_deep_dive / campaign / exec_qbr / poc_readout / renewal / internal | … | positive / neutral / cautious / negative |

Source: `read_call_records` (records are returned sorted by `(date, call_id)`).

---

## 5. Milestones (optional)

Bullets for concrete inflection points in the account story. Each bullet cites a **`call_id`** + **call date** — never the run date. Derive from `call_type` transitions and lifecycle `history[]` entries (for example: first `discovery`, first POC, first POC readout, commercial close, champion transition, renewal gate).

- `YYYY-MM-DD` — [milestone label] — `call_id: …`
- `YYYY-MM-DD` — [milestone label] — `call_id: …`

Do not invent milestones that are not in the record. If no milestones can be cited, say so in one line and move on.

---

## 6. Challenge review (optional)

Table sourced from **`challenge-lifecycle.json`** (via MCP `read_challenge_lifecycle`) plus the latest call record that mentions each id. `current_state` and `last_updated` come from the lifecycle JSON — do **not** infer them from call records when the JSON is present.

| challenge_id | description | current_state | last_updated | evidence | stall / risk | recommended_action |
|--------------|-------------|---------------|--------------|----------|--------------|--------------------|
| … | short label | identified / acknowledged / in_progress / resolved / reopened / stalled | YYYY-MM-DD | latest `call_id` or short quote | `—` or `no movement 65d` or `at risk (drift)` | one imperative line |

**Stall rule:** flag `stall` when `current_state` is `identified`, `acknowledged`, or `in_progress` and `(today − last_updated) ≥ 60 days` per `docs/ai/references/challenge-lifecycle-model.md`. Phrase as `"no movement 65d"` using the actual day count. If `current_state` is already `stalled`, surface days since last transition in `recommended_action` instead of double-counting.

**When no lifecycle JSON exists yet:** render the section as a single line — `No persisted lifecycle JSON yet; run Update Customer Notes to populate challenge-lifecycle.json.` — and do **not** substitute an inferred-from-call-records table.

---

## 7. Stakeholders

| Name | Role | Champion? | Sentiment | First seen | Last seen | Last Contact |
|------|------|-------------|------------|------------|-----------|--------------|
| … | … | Yes / No / Unknown | Positive / Neutral / Cautious / Negative / Unknown | YYYY-MM-DD | YYYY-MM-DD | DATE or call id |

**Guidance:**

- **Sentiment** must reflect **signals** from recent transcripts or notes — not guesswork.
- **First seen / Last seen** come from `participants[]` across call records — first and latest call dates where the person appears.
- **Last Contact:** Prefer a call date or meeting reference tied to evidence.

---

## 8. Value Realized

Bulleted or short paragraphs:

- **Outcome** — what changed for the customer.
- **When** — date or period.
- **Evidence** — transcript, call record id, or doc section; include attribution tag.

---

## 9. Strategic Position

Subsections (brief):

- **Journey state** — where they are vs. POC / expansion / renewal / stalled (as supported by evidence).
- **Risk factors** — deal, technical, organizational (each tagged).
- **Next logical move** — one primary recommendation path for leadership (aligned with licensed vs. future lanes per `docs/ai/references/customer-data-ingestion-weights.md`).

---

## 10. Wiz Commercials

License-evidence style table (fields as known from notes, ledger, or license-evidence runs):

| Product / SKU | Status (Licensed / Eval / Unknown) | Dates / Notes | Confidence |
|---------------|--------------------------------------|-----------------|------------|
| … | … | … | High / Medium / Low |

Mark **Unknown** explicitly rather than inferring entitlements.

---

## 11. Open Challenges

List or table of challenges still in **`identified`** or **`stalled`** (per lifecycle model), with:

- **ID or short name**
- **State**
- **Last evidence** (date / call)
- **Suggested next action** (one line, non-prescriptive if license is unknown)

---

## Artifact hygiene

This template produces **customer-facing artifact content**. Keep it indistinguishable from a real-customer run:

- Do **not** mention any `TASK-NNN` identifier, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, or `fixture`.
- Every date in the body is a **call date** or a **milestone date** from evidence. The **only** place the run date may appear is the optional **Metadata** line at the top (`Generated: YYYY-MM-DD`).
- See `.cursor/rules/11-e2e-test-customer-trigger.mdc` — Artifact hygiene.

---

## Related references

- `docs/ai/references/customer-data-ingestion-weights.md` — source priority and lookback.
- `docs/ai/references/challenge-lifecycle-model.md` — challenge states.
- `docs/ai/references/health-score-model.md` — 🟢🟡🔴⚪ definitions.
- `docs/ai/playbooks/run-license-evidence-check.md` — when commercials are uncertain.
