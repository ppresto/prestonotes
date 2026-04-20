# Exec summary template (account summary output)

Use this structure when producing the **exec-facing** portion of an account summary (for example from **`Run Account Summary for [CustomerName]`**). Each fact should carry an attribution tag per `docs/project_spec.md` (for example `[Verified: DATE | Name | Role]`, `[Inferred: DATE]`, `[Achieved: DATE]`).

---

## 1. The 30-Second Brief

**Audience:** VP / executive skimming on mobile.

**Rules:**

- **≤ 3 sentences**, one short paragraph at most.
- Plain language only — **no product jargon**, no internal codenames, no acronyms the customer did not use on the call.
- Cover in order: **who they are**, **what problem they are solving**, **where they are in the journey**, **what the next move is**.

**Template:**

> *[Customer]* is *[one-line who they are]*. They are focused on *[plain-English problem / outcome]* and are currently *[journey state in customer words or neutral phrasing]*. The **next move** is *[single concrete action or decision]*.

---

## 2. Challenges → Solutions Map

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

## 3. Stakeholders

| Name | Role | Champion? | Sentiment | Last Contact |
|------|------|-------------|------------|--------------|
| … | … | Yes / No / Unknown | Positive / Neutral / Cautious / Negative / Unknown | DATE or call id |

**Guidance:**

- **Sentiment** must reflect **signals** from recent transcripts or notes — not guesswork.
- **Last Contact:** Prefer a call date or meeting reference tied to evidence.

---

## 4. Value Realized

Bulleted or short paragraphs:

- **Outcome** — what changed for the customer.
- **When** — date or period.
- **Evidence** — transcript, call record id, or doc section; include attribution tag.

---

## 5. Strategic Position

Subsections (brief):

- **Journey state** — where they are vs. POC / expansion / renewal / stalled (as supported by evidence).
- **Risk factors** — deal, technical, organizational (each tagged).
- **Next logical move** — one primary recommendation path for leadership (aligned with licensed vs. future lanes per `docs/ai/references/customer-data-ingestion-weights.md`).

---

## 6. Wiz Commercials

License-evidence style table (fields as known from notes, ledger, or license-evidence runs):

| Product / SKU | Status (Licensed / Eval / Unknown) | Dates / Notes | Confidence |
|---------------|--------------------------------------|-----------------|------------|
| … | … | … | High / Medium / Low |

Mark **Unknown** explicitly rather than inferring entitlements.

---

## 7. Open Challenges

List or table of challenges still in **`identified`** or **`stalled`** (per lifecycle model), with:

- **ID or short name**
- **State**
- **Last evidence** (date / call)
- **Suggested next action** (one line, non-prescriptive if license is unknown)

---

## Related references

- `docs/ai/references/customer-data-ingestion-weights.md` — source priority and lookback.
- `docs/ai/references/challenge-lifecycle-model.md` — challenge states.
- `docs/ai/playbooks/run-license-evidence-check.md` — when commercials are uncertain.
