# Playbook: Update Customer Notes

Triggers: `Update Customer Notes for [CustomerName]` · `UCN for [CustomerName]` · informal **`UCN`** when the customer is already set in the thread.

**Default (orchestrator):** Built-in **challenge governance** first (review table + optional persisted challenge status updates you approve), then the multi-advisor pipeline and **one** combined approval — **`.cursor/rules/20-orchestrator.mdc`**. On execute, UCN writes persisted state only: **`update_challenge_state`** (approved rows), **`write_doc`**, **`append_ledger_row`**, optional **`log_run`** / **`sync_notes`**. The human-readable account narrative (Health line, call spine, milestones, challenge review, stakeholder evolution) now lives in **`Run Account Summary for [CustomerName]`** (**`docs/ai/playbooks/run-account-summary.md`**).

Aliases (same as default): `Update Customer Notes with Challenge Review first for [CustomerName]` · `Lifecycle-first Update Customer Notes for [CustomerName]`

**Opt-out (faster, doc-only approval):** `Update Customer Notes (no challenge review) for [CustomerName]` · `UCN without challenge review for [CustomerName]` · `Light UCN for [CustomerName]`

Purpose: the **single source of truth** workflow for maintaining a customer's account story. Reads all transcripts, notes, the live Google Doc (both tabs), the History Ledger, and the audit log. Proposes targeted updates. After user approval, writes to the Google Doc, appends a History Ledger row, and logs to the audit file.

**Routing (Stage 3):** Prefer **`.cursor/rules/20-orchestrator.mdc`** (via **`.cursor/rules/10-task-router.mdc`**) for the **multi-advisor** flow (Phase 0 challenge review + Block A proposals → sync → load → extractor delta → SOC → APP → VULN → ASM → AI → compile → **one** combined STOP → ordered writes). This playbook remains the **monolithic, step-by-step fallback** until **TASK-019** validates the orchestrator path end-to-end.

> **v2 (TASK-007):** In Cursor, prefer **prestonotes** MCP tools where they map 1:1 — `check_google_auth`, `sync_notes`, `discover_doc`, `read_doc`, `write_doc` (after user approval; use `dry_run=true` to preview), `append_ledger`, `log_run`. The bash / `uv run prestonotes_gdoc/...` blocks below are the **terminal equivalent** when not using MCP.

Operating persona: **Wiz cybersecurity Solutions Engineer (post-sale, value-realization focused)**. Updates must prioritize customer business/security outcomes, measurable blockers to value realization, operational adoption and expansion readiness, and executive signal quality over transcript volume.

Primary analysis lens: `prestonotes_gdoc/config/prompts/010-wiz-solution-lens.md`

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

---

## Exec Account Summary template (Google Doc)

Customer Notes templates use this **fixed structure** under the **Account Summary** tab:

1. **H1:** `Exec Account Summary`
2. **H3 (in this order):** `Goals` → `Risk` → `Upsell Path`

**How content maps to mutations**

| Template heading | `doc-schema.yaml` field key | Mutation `section_key` / `field_key` |
| :--- | :--- | :--- |
| **Goals** (H3) | `top_goal` | `exec_account_summary` / `top_goal` |
| **Risk** (H3) | `risk` | `exec_account_summary` / `risk` |
| **Upsell Path** (H3) | `upsell_path` | `exec_account_summary` / `upsell_path` |

**Post-seed cleanup / executive polish:** For boss-ready consolidation after heavy seed/replay (or any time the Account Summary needs a presentation pass), use **`Run Step 9 Post-Seed Synthesis for [CustomerName]`** or **`Polish Account Summary for [CustomerName]`** (`docs/ai/playbooks/run-seeded-notes-replay.md`, Step 9). That pass may **rewrite every managed section** in one approved batch: **`replace_field_entries`** for Goals/Risk/Upsell, **Cloud Environment** (CSP/Regions, IDP, Sizing), contacts, use cases, workflows, and **Challenge Tracker** row merges / routing. Daily UCN remains append-first unless Step 9 applies.

**How writes appear in the doc**

- Use **`append_with_history`** (or other allowed actions from `customer-notes-mutation-rules.md`) so each new goal, risk, or upsell line is added as a **bullet (list item)** under the **correct H3** — never under the wrong heading.
- **Goals:** strategic customer outcomes (one bullet per distinct theme; follow duplicate/theme rules in the mutation reference).
- **Risk:** deal and commercial risk only (budget, exec alignment, champion, timeline, procurement, competition). Put technical backlog in **Challenge Tracker**, not here.
- **Upsell Path:** each bullet must include an allowed SKU token (`Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz Code`, or `ASM`) plus a one-line value story, per mutation rules.

**Do not put in Goals / Risk / Upsell:** automation or QA about the notes doc (e.g. “internal check”, “parser”, “template”, “label-matching”, “H3 headings parse correctly”), or **ingestion status** framed as risk (e.g. “no new transcripts since …”). That content goes in **`pnotes_agent_log.md`** or planner metadata — see `customer-notes-mutation-rules.md` (Exec Account Summary — forbidden meta).

Do **not** remove or rename the three H3 headings. If a customer doc predates this layout, note it in the change plan and align content to these headings on the next approved write.

---

## Communication Rule

At every step, tell the user what you are doing in plain English. Start each step with: `"Step X of 11 — [what I'm doing]"`. Do not skip steps. Do not reorder steps. Follow the format rules in `15-user-preferences.mdc`.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`** for the final response.
- After multi-step work, include **`### Activity recap`** with: what changed, what was skipped, and why.
- Always state approval/write status clearly (no writes run, dry-run only, or approved writes executed).

---

## Before You Start (Setup Checks)

Run these checks in order. If any check fails, **stop** and tell the user what failed and how to fix it. Do not continue until they confirm the fix.

### Check 1 — Google Drive is available

Verify the Drive-backed `MyNotes` root exists and is readable:

```bash
# Require GDRIVE_BASE_PATH (same as `.cursor/mcp.env` → Drive-mounted MyNotes root)
: "${GDRIVE_BASE_PATH:?Set GDRIVE_BASE_PATH to your MyNotes mount}"
test -d "$GDRIVE_BASE_PATH" && test -r "$GDRIVE_BASE_PATH" && echo "OK"
```

If this fails, tell the user:
> "Google Drive folder is not available. Make sure Google Drive for Desktop is running and synced. You can restart it with: `./scripts/restart-google-drive.sh`"

Wait for confirmation before continuing.

### Check 2 — Google API auth works

```bash
gcloud auth print-access-token  # optional: add --account from `GCLOUD_ACCOUNT` in `.cursor/mcp.env`
```

If this fails, tell the user:
> "Google API auth is not working. If an MCP tool returned `run_in_terminal_to_fix`, paste that **exact** command from `.cursor/mcp.env` into Terminal (see `check_google_auth`). Otherwise run `gcloud auth login` with the account you use for Docs/Drive."

Wait for confirmation before continuing.

### Check 3 — Customer scaffold exists

- `prestonotes_gdoc/config/doc-schema.yaml` exists in the repo.
- `./MyNotes/Customers/[CustomerName]/` exists (from bootstrap or prior sync).
- Exported **`[CustomerName] Notes.md`** and/or a **`.gdoc`** stub may exist under that folder after Drive sync (layout varies by export).

If the customer folder is missing, run `./scripts/rsync-gdrive-notes.sh "[CustomerName]"` after Checks 1-2 pass.

### Check 4 — Product Intelligence is fresh

Check `./MyNotes/Internal/AI_Insights/Product-Intelligence.md`. If missing or `last_updated` is older than 7 days, run `Load Product Intelligence` first.

[STOP — tell user: "Setup checks passed. Starting Update Customer Notes for [CustomerName]. I have 11 steps."]

---

## Source bundle and fallback order (TASK-038 required)

Use this exact read order for context assembly:

1. `read_doc` result (current Google Doc truth for Account Summary + Account Metadata tabs).
2. Last-month transcript set (default lookback 1 month) via `read_transcripts` or bounded reads from `MyNotes/Customers/[CustomerName]/Transcripts/*.txt`.
3. `MyNotes/Customers/[CustomerName]/[CustomerName] Notes.md` mirror for local comparison and Daily Activity date slicing.
4. `MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-AI-AcctSummary.md` (if present; optional but strongly preferred).
5. `MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-History-Ledger.md` and audit log files for continuity + prior decisions.

Fallback behavior when files are missing:

- If `read_doc` fails, stop and resolve doc identity/auth first (do not continue with partial write planning).
- If no in-window transcripts exist, continue with doc + AI_Insights + notes, but mark transcript-dependent claims as `no recent transcript evidence`.
- If `*-AI-AcctSummary.md` is missing, continue and note that strategic narrative continuity may be sparse.
- If ledger/audit files are missing, continue and explicitly state reduced historical confidence.

---

## Steps

### Step 1 of 11 — Pull latest notes from Drive

**v2:** Run a **pull sync** for this customer (no legacy Customer-Full-Context push). Use **`sync_notes`** MCP with `[CustomerName]` **or**:

```bash
./scripts/rsync-gdrive-notes.sh "[CustomerName]"
```

**Tell user:** "Step 1 of 11 — I pulled the latest notes from Google Drive for [CustomerName]."

### Step 2 of 11 — Find the Google Doc

Run discover to get the document ID. **In Cursor,** call MCP **`discover_doc`** with `[CustomerName]` (uses `MYNOTES_ROOT_FOLDER_ID` from the MCP env). **In Terminal:**

```bash
uv run prestonotes_gdoc/update-gdoc-customer-notes.py discover \
  --customer "[CustomerName]" \
  --root-folder-id "<MYNOTES_ROOT_FOLDER_ID>"
```

Capture the returned `doc_id`.

**Tell user:** "Step 2 of 11 — I found the [CustomerName] Notes Google Doc."

### Step 3 of 11 — Read current Google Doc state (both tabs)

**In Cursor,** MCP **`read_doc`** with `doc_id` (and `include_internal` as needed). **In Terminal:**

```bash
uv run prestonotes_gdoc/update-gdoc-customer-notes.py read \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml \
  --include-internal
```

This outputs a JSON section map with every section, field, and table row from both the **Account Summary tab** and the **Account Metadata tab** (including Deal Stage Tracker rows). Save this for comparison.

Pay special attention to:
- **Exec Account Summary** — read **`top_goal`**, **`risk`**, and **`upsell_path`** entries from the JSON. In the live doc these are the bullet lists under the **H3** headings **Goals**, **Risk**, and **Upsell Path** (see [Exec Account Summary template](#exec-account-summary-template-google-doc) above). When proposing updates, add **one bullet per append** under the matching heading.
- **Deal Stage Tracker rows** — which SKUs are purchased, at what stage, and what verification activity exists. This tells you what the customer already owns.
- **Account Metadata fields** — exec buyer, champion, technical owner, operational metrics.
- **Challenge Tracker rows** — what's already tracked, with status and dates.
- **Accomplishments section** — what has already been resolved and recognized.

**Tell user:** "Step 3 of 11 — I read the current state of the Google Doc (both tabs). Deal Stage Tracker shows [N] SKUs tracked."

### Step 4 of 11 — Load transcripts, notes, history, and audit

Follow **`docs/ai/references/customer-data-ingestion-weights.md`**. Set **lookback** to **1 month** by default; use **3 / 6 / 12** months if the user specified a longer window for this run.

Read all available customer source material using **weights**:
- **+4 — Transcripts:** `./MyNotes/Customers/[CustomerName]/Transcripts/` (all `.txt` files). Prioritize **meetings dated within lookback** for new facts; use older meetings for continuity.
- **+3 — Daily Activity Logs:** In local notes or synced export, ingest **only** content under **Daily Activity Logs** with **date headings inside lookback**. Do **not** propose generic edits to this section; the **only** allowed write is the documented `prepend_daily_activity_ai_summary` flow (see `docs/ai/references/daily-activity-ai-prepend.md`), not part of the default UCN mutation plan.
- **+2 — Account Summary tab (full):** Same notes export / doc as Step 3 — **entire** Account Summary tab: **Challenge Tracker**, **Company Overview**, **Contacts**, **Org Structure**, **Cloud Environment** (CSP/Regions, Platforms, IDP, DevOps/VCS, Security, ASPM, Ticketing, Languages, Sizing), **Use Cases / Requirements**, **Workflows / Processes**, and **Exec Account Summary** (Goals / Risk / Upsell — `top_goal`, `risk`, `upsell_path` in JSON).
- **+1 — AI_Insights:** `./MyNotes/Customers/[CustomerName]/AI_Insights/` — **History Ledger** (`[CustomerName]-History-Ledger.md`), optional `SEED-Deal-Stage-Tracker.md`, prior `*-AI-AcctSummary.md`, etc. **Read regardless of file date.**
- Local notes path: `./MyNotes/Customers/[CustomerName]/[CustomerName] Notes.md`
- Optional: `Customer-Full-Context.md` if it exists
- **Audit log:** `./MyNotes/Customers/[CustomerName]/pnotes_agent_log.md` (and `.archive.md` if present) — check for active rejection watermarks and prior run outcomes (not on the +1–+4 scale; operational requirement).

Also read the Wiz solution lens:
- `prestonotes_gdoc/config/prompts/010-wiz-solution-lens.md`

**Tell user:** "Step 4 of 11 — I loaded sources with lookback [N] month(s) and weights applied: transcripts +4, Daily Activity Logs +3 (in-window), full Account Summary tab +2, AI_Insights +1. [N] transcript files, [has/no] history ledger, [N] audit log entries. Meeting date range: [oldest] to [newest]."

### Step 5 of 11 — Check rejection watermarks

Read `pnotes_agent_log.md` for this customer. If there are active rejection holds (from a prior run where the user said no), check:
- Are there **new** transcripts or notes **after** the watermark date?
- Did the user explicitly ask to override the hold?

If no new evidence and no override, do not re-propose the same changes. Tell the user what's held and why.

**Tell user:** "Step 5 of 11 — [No active holds found / Found hold from [date] — checking for new evidence...]"

### Step 6 of 11 — Extract facts, compare, and identify conflicts

Analyze the loaded transcripts and notes. Extract structured facts using the categories and rules defined in `docs/ai/references/customer-notes-mutation-rules.md`.

Compare extracted facts against **three** sources of current/historical truth:
1. **Google Doc state** from Step 3 (current doc content, challenge tracker, deal stage tracker)
2. **History Ledger** from Step 4 (how the account looked at prior snapshots)
3. **Audit log** from Step 4 (what was previously tried or rejected)

Use these cross-references to:
- **Avoid proposing challenges that are already resolved** — if the challenge tracker says "Resolved" and no transcript contradicts it, skip it.
- **Avoid recommending products already purchased** — if Deal Stage Tracker says a SKU is at "win" stage, do not propose buying it again. Do not propose challenges that were pre-sale issues likely solved after purchase.
- **Detect regressions** — if the ledger shows a challenge was resolved but transcripts suggest it resurfaced, flag it for clarification.
- **Detect stale state** — if the ledger's last row is old and transcripts show material changes, note the gap.

**Daily Activity Logs — meeting recap gap (required; feed Step 8):**
- From Step 3 `read` JSON, treat `daily_activity_logs.free_text` entries as paragraphs: derive a **normalized meeting title key** for each block’s **first line** (strip leading `#`, trim — same idea as the duplicate guard in `docs/ai/references/daily-activity-ai-prepend.md`).
- From Step 4 transcripts **within lookback**, list meetings you can recap (date, title, source path).
- **Only recap meetings with usable transcript content.** If a meeting block contains `[No Transcript Data]` (or otherwise lacks substantive transcript body), mark it as `no transcript available` and **do not** include it in Daily Activity recap mutations.
- **Missing recaps:** meetings whose proposed `heading_line` would **not** duplicate any existing normalized first line. If the same calendar meeting already has a recap, skip unless the user asked to refresh it.
- Carry the **missing** list (count + identifiers) into Step 8.

**Tell user:** "Step 6 of 11 — I read through all the notes and found [N] possible updates across [N] sections, [N] conflicts that need your input, and Daily Activity: [N] meetings in lookback still need a recap / all covered."

### Step 7 of 11 — Clarification gate (ask before acting on ambiguity)

Before building the change plan, present **numbered questions** to the user for any situation where the evidence is unclear. Common triggers:

- **Resolved-but-maybe-not:** The doc says a challenge is Resolved, but a recent transcript mentions the same problem. Ask: "Challenge X was marked Resolved on [date]. Transcript from [date] mentions it again. Should I reopen it in the challenge tracker, or is it a different issue?"
- **Product already bought:** Deal Stage Tracker shows SKU at "win" but notes suggest expansion issues. Ask: "Wiz [SKU] shows as purchased. Should I add an expansion risk, or is this resolved?"
- **Prior rejection with ambiguous new evidence:** Audit log shows a rejection, and new evidence partially overlaps. Ask: "I proposed [X] last time and you rejected it. New transcript from [date] has related info. Should I try again?"
- **Unresolved problem with no update:** A challenge has been open for 60+ days with no new evidence. Ask: "Challenge [X] has been open since [date] with no updates. Is it still active, resolved, or should I mark it Needs Validation?"
- **Account Metadata discrepancy:** Notes suggest a new champion or exec buyer but no explicit statement. Ask: "[Name] appears to be acting as champion based on [evidence]. Should I update Account Metadata?"

If no conflicts or ambiguities exist, skip this step and say so.

[STOP — wait for user answers before continuing. Use their responses as evidence for the change plan.]

**Tell user:** "Step 7 of 11 — I have [N] questions before I build the plan. [questions]. Please answer and I'll use your responses as evidence."

### Step 8 of 11 — Build the change plan

Produce a typed change plan (mutation JSON) following the schema, core rules, and quality gate in `docs/ai/references/customer-notes-mutation-rules.md`. Each proposed change must include:
- `reasoning`: why this change is being proposed
- `evidence_date`: the date from the transcript/notes that supports it
- `theme_key`: stable key for duplicate control

Incorporate user answers from Step 7 as evidence (cite "user confirmation [date]" as evidence source).

Run the planner coverage guard: every run must explicitly cover `exec_account_summary.top_goal`, `exec_account_summary.risk`, `use_cases.free_text`, and `workflows.free_text` with either a change or `no_evidence`.

When you **do** append to the exec summary, target the correct field so new text becomes a **bullet under the matching H3** (**Goals** / **Risk** / **Upsell Path**). Do not place deal-risk language in `top_goal` or SKU upsell lines in `risk`.

**Account Metadata and Deal Stage Tracker rules:**
- Only update Deal Stage Tracker if there is **explicit proof** a SKU stage changed (transcript quote, contract reference, user confirmation). Otherwise, ask in Step 7 and use the response as proof.
- Only update `exec_buyer`, `champion`, `technical_owner` when explicitly stated in source evidence.

**Daily Activity Logs — meeting recaps (required each run):**
- Do **not** append or replace arbitrary text in Daily Activity. The **only** allowed write is **`prepend_daily_activity_ai_summary`** (see `docs/ai/references/daily-activity-ai-prepend.md`).
- For **each** meeting in the Step 6 **missing** list, add one **`prepend_daily_activity_ai_summary`** object to the **same** mutation JSON as the rest of UCN (`section_key`: `daily_activity_logs`, `field_key`: `free_text`). Include `heading_line`, `body_markdown`, `evidence_date`, `reasoning`, and `source`.
- Do **not** generate `prepend_daily_activity_ai_summary` for meetings marked `no transcript available` in Step 6. Never write placeholder summaries.
- Draft recaps using `docs/ai/references/granola-meeting-summary-templates.md` (T1–T5 by call type). In `body_markdown`, use top-level `- **Context:**` style section labels (bold label on its own line, nested bullets under sections, `**bold**` for emphasis in prose — formatting rules in `daily-activity-ai-prepend.md`).
- If the missing list is **empty**, add **no** prepend mutations and state in the summary: "Daily Activity: all meetings in lookback already have recaps."

**Accomplishments flow:**
- When evidence shows a challenge is resolved, propose `update_table_row` to set status to Resolved, AND propose an addition to the Accomplishments section describing what was achieved.
- When evidence suggests a previously-resolved issue has returned, ask the user first (Step 7), then either reopen in challenge tracker or leave as-is.

Run the quality gate before showing to user.

### Sparse vs rich account strategy (required)

- **Sparse account (limited recent evidence):**
  - prioritize correctness over volume; only propose high-confidence updates backed by current doc/transcript evidence
  - explicitly use `no_evidence` outcomes where required by schema instead of filling with generic statements
  - keep Daily Activity additions limited to meetings with usable transcript content
- **Rich account (broad recent evidence):**
  - include trend lines across recent calls (what improved, what regressed, what is unchanged)
  - include value articulation tied to delivered outcomes and supporting evidence tags
  - include concrete next steps for SE execution (owner + near-term action)

### Quality bar checklist (required before Step 9)

- Trends are stated when evidence spans multiple recent calls.
- Value realized is explicit, dated, and evidence-tagged when available.
- Next steps for SE are concrete (owner/action/timebox) and not generic.
- Any unsupported area uses explicit `no_evidence` language instead of invented detail.

**Tell user:** "Step 8 of 11 — I built the change plan. [N] proposed changes, [N] sections marked no new evidence, [N] Daily Activity meeting recap(s) to prepend."

### Step 9 of 11 — Show proposed changes and wait for approval

Display the proposed changes grouped by section using the diff preview format from `docs/ai/references/customer-notes-mutation-rules.md`. Include **`prepend_daily_activity_ai_summary`** items explicitly (show `heading_line` and a short excerpt of `body_markdown` for each).

**Tell user:** "Step 9 of 11 — Here are the changes I want to make. Please review and say yes, no, or tell me which ones to keep."

[STOP — wait for user approval before continuing. Do not write anything until the user says yes.]

**If user rejects (all or some):** Follow the rejection logging process below (section "When User Rejects Changes").

### Step 10 of 11 — Apply approved changes

Save the approved change plan to a temp JSON file and run:

**In Cursor,** MCP **`write_doc`** with `doc_id`, `mutations_json`, and `dry_run=true` until the user approves, then `dry_run=false`. **In Terminal:**

```bash
uv run prestonotes_gdoc/update-gdoc-customer-notes.py write \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml \
  --mutations /tmp/customer_notes_mutations.json
```

For first-time testing, add `--dry-run`.

After write, re-run the `read` subcommand to confirm changes are reflected. Save the post-write doc state for the ledger row.

**Tell user:** "Step 10 of 11 — Changes written to Google Doc. Here's what changed: [summary]. Here's what I skipped and why: [summary]."

### Step 11 of 11 — Append History Ledger row and sync

After a successful Google Doc write, assemble one **schema v3** row and append it via **MCP `append_ledger_row`**. The canonical column order and typing lives in **`prestonotes_mcp/ledger.py`** (`LEDGER_V3_COLUMNS`) and the full spec is **`docs/project_spec.md`** § _Ledger writes: `append_ledger` vs `append_ledger_row`_. Do **not** handcraft markdown tables in this playbook flow.

1. **Read or create the ledger file:**
   - Path: `./MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-History-Ledger.md`.
   - If the file is missing, `append_ledger_row` creates a fresh `schema_version: 3` stub on first append; treat a missing file as first-run / no-history and continue.

2. **Build one new ledger row as a Python dict** keyed by the **20 v3 columns** (the MCP wrapper forwards it as `row_json`). Each column below has exactly one "extract as …" rule. The four `challenges_*` columns are **derived**, not extracted:

   | # | Column | How to fill |
   |---|---|---|
   | 1 | `run_date` | Extract as **today's ISO date** (`YYYY-MM-DD`). The only place the run date ever appears in a row. |
   | 2 | `call_type` | Extract as the **most salient `call_type`** across the transcripts covered by this run. Enum: `qbr \| exec_readout \| product_demo \| commercial_close \| technical_pov \| champion_1on1 \| kickoff \| other`. |
   | 3 | `account_health` | Extract as a synthesis of challenge severity + sentiment + coverage. Enum: `great \| good \| at_risk \| critical`. Leave empty string only if every input is unknown. |
   | 4 | `wiz_score` | Extract as the **verbatim integer** the customer stated in an in-scope transcript (0..100). **Do not infer.** Empty string if no transcript states one. |
   | 5 | `sentiment` | Extract as the synthesized tone for the run. Enum: `positive \| neutral \| negative \| mixed`. |
   | 6 | `coverage` | Extract as one free-text headline (≤ 160 chars) summarizing deployment / scan coverage for the run (e.g. `"Sensor coverage 82% prod AWS; Code GitHub org onboarded"`). |
   | 7 | `challenges_new` | **Do not extract. Derive from `read_challenge_lifecycle` output for this customer** — ids that transitioned to `identified` within the run window. Pass as `list[str]` of challenge ids. |
   | 8 | `challenges_in_progress` | **Do not extract. Derive from `read_challenge_lifecycle` output for this customer** — ids whose current state is `identified` or `in_progress`. |
   | 9 | `challenges_stalled` | **Do not extract. Derive from `read_challenge_lifecycle` output for this customer** — ids whose current state is `stalled`. |
   | 10 | `challenges_resolved` | **Do not extract. Derive from `read_challenge_lifecycle` output for this customer** — ids that transitioned to `resolved` within the run window. |
   | 11 | `goals_delta` | Extract as a free-text line (≤ 160 chars) describing goal shifts customers stated this run. Empty string if none. |
   | 12 | `tools_delta` | Extract as a free-text line (≤ 160 chars) describing tools that came online or were retired this run. |
   | 13 | `stakeholders_delta` | Extract as a free-text line (≤ 160 chars) describing who moved: departures, promotions, new sponsors. |
   | 14 | `stakeholders_present` | Extract as a `list[str]` of normalized stakeholder names derived from call-record `participants[]` across the in-window calls (unique, deduped). |
   | 15 | `value_realized` | Extract as ≤ 240 chars of quantified / concrete outcomes this run. **MUST include at least one quantified element when any in-window transcript contains one** (regex — see `.cursor/rules/21-extractor.mdc` "Ledger cell extraction"). Otherwise free text is fine. |
   | 16 | `next_critical_event` | Extract as `YYYY-MM-DD: <desc>` when a date is known; otherwise `<desc>` alone (≤ 160 chars). |
   | 17 | `wiz_licensed_products` | Extract as a `list[str]` of normalized SKU ids actively licensed (e.g. `["wiz_cloud", "wiz_sensor"]`). Source: Deal Stage Tracker rows at "win" / "tech win" + prior ledger. |
   | 18 | `wiz_license_purchases` | Extract as a `list[str]` of `ISO:sku` pairs newly purchased (e.g. `["2026-03-28:wiz_cloud"]`). Must match `^\d{4}-\d{2}-\d{2}:[a-z0-9_]+$`. Empty list if none. |
   | 19 | `wiz_license_renewals` | Extract as a `list[str]` of `ISO:sku` pairs renewing. Same format as purchases. |
   | 20 | `wiz_license_evidence_quality` | Extract as an enum. Enum: `high \| medium \| low`. |

   - **Omit** a key to write an empty cell — the writer accepts absent keys as empty. Do **not** write `"None"`, `"n/a"`, or placeholder tokens.
   - Free-text cells must obey `.cursor/rules/21-extractor.mdc` "Ledger cell extraction": one internal transcript citation per cell, no harness vocabulary (MCP rejects any match against `FORBIDDEN_EVIDENCE_TERMS` in `prestonotes_mcp/journey.py`), cap enforcement.

3. **Append the row** with MCP **`append_ledger_row(customer_name, row_json=<dict>)`** (append-only — never edit prior rows). On a rejection the tool returns `{"ok": false, "error": "...", "field": "...", "value": "..." | "matched": "..."}`; fix the row locally and retry. Rejections do not write a partial file.

4. **Mirror** the updated ledger to Google Drive:
   - `$GDRIVE_BASE_PATH/Customers/[CustomerName]/AI_Insights/[CustomerName]-History-Ledger.md`

5. **Cross-reference in audit log:** The audit log entry from the write step should note `"Ledger row appended: <run_date>"` so the two files link to each other.

**Tell user:** "Step 11 of 11 — Done. Ledger row appended for [date]. Files synced to Google Drive."

---

## When User Rejects Changes

When the user rejects some or all proposed changes before Step 10, or the run ends with zero writes by user decision:

1. **Log to the customer audit file** (local + Google Drive mirror):
   - Path: `./MyNotes/Customers/[CustomerName]/pnotes_agent_log.md`
   - Prepend a new `##` run block with:
     - **Rejected / not applied:** list of what was proposed (section + action), or "all proposals rejected"
     - **Reason** (if user gave one)
     - **Source watermark:** latest evidence dates used for that plan (newest transcript date and newest Notes.md activity date)
     - **Resume rule:** Do not re-propose the same changes unless new transcripts/notes exist after the watermark, or user explicitly asks to revisit

2. **Do NOT append a ledger row** on rejection — the ledger only tracks successful state changes.

3. **Next run:** Read `pnotes_agent_log.md` before building a new change plan and honor any active rejection watermark.

4. **Optional:** If the user wants the hold visible across sessions, add a one-line dated entry to `.cursor/rules/ai_learnings.mdc` pointing at this customer's `pnotes_agent_log.md`.

This applies to every customer, not just one account.

---

## Output Contract

- This task modifies a Google Doc in-place via the `write` subcommand.
- After successful writes, this task also appends to `[CustomerName]-History-Ledger.md` under `AI_Insights/`.
- The change plan JSON is temporary (written to `/tmp/`).
- Local MyNotes files modified: `pnotes_agent_log.md` (audit logging on every run) and `*-History-Ledger.md` (on successful writes only).
- All modified local files are mirrored to Google Drive.
- Audit logging includes successful writes, rejected/zero-write runs, and ledger-append cross-references.
- Run-log format: Markdown headings/sections/tables, with `+` for adds, `~` for modifications, `-` for removals.
- **Daily Activity Logs** are updated only via **`prepend_daily_activity_ai_summary`**, which is **part of this task** whenever Step 6 finds meetings in lookback that are not yet captured there; those mutations ship in the **same** approved JSON as other UCN changes (one `write`).

## Challenge lifecycle write rules (TASK-048)

When UCN calls **`update_challenge_state`** in Step 10 (Block A execute), every call must follow these rules. Three are hard-enforced by MCP (future date, history regression, forbidden evidence vocabulary — see `prestonotes_mcp/journey.py`); the rest are operator / extractor discipline only.

1. **Call date, not run date.** The `transitioned_at` argument is the ISO call date from the cited transcript's `DATE:` header, not today. If you cannot determine a call date from the transcript, **do not write the transition** — log `skip update_challenge_state ch=<id> reason=unknown_call_date` and move on.
2. **Evidence format:** `<YYYY-MM-DD> <call-topic-short>: "<direct quote, ≤ 160 chars>"`. No paraphrase. No multi-call blobs. No meta-process language ("challenge rows added to Notes doc", "UCN round-1", etc.).
3. **Customer directives win.** When a transcript contains an explicit directive ("treat as in progress, not stalled", "mark it resolved", "this is no longer stalled"), use that target state verbatim and cite the same line as evidence.
4. **Resolved sweep.** After processing new transcripts, for every challenge still at `in_progress` or `stalled`, scan the newest in-lookback transcript for unblock language ("no longer stalled", "resolved", "shipped", "done", "we got it"). If found, write a `resolved` transition at that transcript's call date.
5. **No no-op transitions.** Skip the call if the proposed `(state, transitioned_at)` tuple equals the last history entry for that challenge.
6. **Split composite challenges.** If a transcript explicitly splits two subjects ("keep Splunk renewal separate from the budget blocker"), open two `challenge_id`s and write them separately.
7. **Forbidden evidence vocabulary.** `evidence` must not contain any term from `FORBIDDEN_EVIDENCE_TERMS` in `prestonotes_mcp/journey.py` (case-insensitive substring match): `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`, `UCN round`, `UCN wrote`, `challenge rows added`, `TASK-`, `prestoNotes session`. The MCP layer will reject violations with a structured JSON error — scrub before calling.

## Challenge Tracker row discipline (TASK-048 §B.1)

The same "call date wins over run date" rule applies to a **second write path** — the Challenge Tracker rows UCN writes through **`write_doc`**. That path is a generic doc writer and does **not** validate these; the operator / extractor is the sole check.

1. **`date` column** in every Challenge Tracker row must be the ISO call date of the most recent transcript that touched the challenge, not today.
2. **`notes_references` `Evidence: YYYY-MM-DD`** values must cite ISO dates that exist as transcript files in `MyNotes/Customers/[CustomerName]/Transcripts/`. Preflight: confirm each `YYYY-MM-DD` has a matching transcript file prefix. If the check fails, **skip the row** and log `skip challenge_tracker_row ch=<id> reason=evidence_date_not_in_corpus` — do not persist a row citing a date that is not in the corpus.
3. **No forbidden vocabulary** in `notes_references` — same list as §Challenge lifecycle write rules #7. Scrub before building the mutation plan.
4. **Parity with lifecycle writes.** Every Block A `update_challenge_state` row should have a matching Challenge Tracker row in Block B whose `date` and `notes_references` dates come from the same transcript(s). If §B.1 #1–#3 cannot be satisfied for a row, drop the Block A lifecycle row too rather than persist an inconsistent pair.

## References

- `docs/ai/playbooks/run-seeded-notes-replay.md` — **daily bundle seed + replay** (fork or migrated folder); use when you need `SEED-YYYY-MM-DD.txt` files and **block-by-block** date replay before or instead of a single monolithic pass. After all replays, that playbook’s **Step 9** is the **post-seed synthesis** pass (separate from UCN policy).
- `docs/ai/references/customer-notes-mutation-rules.md` — all mutation logic, schemas, quality gates
- `prestonotes_gdoc/config/prompts/010-wiz-solution-lens.md` — analysis lens
- `prestonotes_gdoc/config/prompts/015-customer-notes-se-persona-prompt.md` — operating persona
- `prestonotes_gdoc/config/doc-schema.yaml` — Google Doc section schema
- `.cursor/rules/core.mdc` — canonical field ownership, ledger schema, Daily Activity Logs guardrail (TASK-007)
