# Playbook: Update Customer Notes

Triggers: `Update Customer Notes for [CustomerName]` · `UCN for [CustomerName]` · informal **`UCN`** when the customer is already set in the thread.

**Default (orchestrator):** Built-in **challenge governance** first (review table + optional persisted challenge status updates you approve), then the multi-advisor pipeline and **one** combined approval — **`.cursor/rules/20-orchestrator.mdc`**. On execute, UCN writes persisted state only: **`update_challenge_state`** (approved rows), **`write_doc`**, **`append_ledger_row`**, optional **`log_run`** / **`sync_notes`**. The human-readable account narrative (Health line, call spine, milestones, challenge review, stakeholder evolution) now lives in **`Run Account Summary for [CustomerName]`** (**`docs/ai/playbooks/run-account-summary.md`**).

Aliases (same as default): `Update Customer Notes with Challenge Review first for [CustomerName]` · `Lifecycle-first Update Customer Notes for [CustomerName]`

**Opt-out (faster, doc-only approval):** `Update Customer Notes (no challenge review) for [CustomerName]` · `UCN without challenge review for [CustomerName]` · `Light UCN for [CustomerName]`

Purpose: the **single source of truth** workflow for maintaining a customer's account story. Reads all transcripts, notes, the live Google Doc (both tabs), the History Ledger, and the audit log. Proposes targeted updates. After user approval, writes to the Google Doc, appends a History Ledger row, and logs to the audit file.

**This playbook is also the SSoT for UCN write validation:** required **`ucn-planner-preflight.py`** before any real write (Step 10), and how **`write_doc` / `update-gdoc-customer-notes.py write`** fit together. **Writer** `dry_run` / `--dry-run` (Doc API preview) is **E2E-only** for `_TEST_CUSTOMER`: **required** before each real write in the default harness — see [`tester-e2e-ucn.md`](tester-e2e-ucn.md). It is **not** a substitute for preflight and is **not** used on the default production path after Step 9 approval.

**Routing (Stage 3):** Prefer **`.cursor/rules/20-orchestrator.mdc`** (via **`.cursor/rules/10-task-router.mdc`**) for the **multi-advisor** flow (Phase 0 challenge review + Block A proposals → sync → load → extractor delta → SOC → APP → VULN → ASM → AI → compile → **one** combined STOP → ordered writes). This playbook remains the **monolithic, step-by-step fallback** until **TASK-019** validates the orchestrator path end-to-end.

> **v2 (TASK-007):** In Cursor, prefer **prestonotes** MCP tools where they map 1:1 — `check_google_auth`, `sync_notes`, `discover_doc`, `read_doc`, `write_doc` (after user approval in Step 9; **production:** real write after successful **planner preflight** in Step 10 — do **not** treat MCP `dry_run=true` as the gate that replaces preflight), `append_ledger`, `log_run`. The bash / `uv run prestonotes_gdoc/...` blocks below are the **terminal equivalent** when not using MCP. **E2E `_TEST_CUSTOMER`:** required writer `dry_run` after preflight, before each real write — [`tester-e2e-ucn.md`](tester-e2e-ucn.md).

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

- Use **`append_with_history`** (or other allowed actions from [`mutations-global.md`](../gdoc-customer-notes/mutations-global.md)) so each new goal, risk, or upsell line is added as a **bullet (list item)** under the **correct H3** — never under the wrong heading.
- **Goals:** strategic customer outcomes (one bullet per distinct theme; follow duplicate/theme rules in the mutation reference).
- **Risk:** deal and commercial risk only (budget, exec alignment, champion, timeline, procurement, competition). Put technical backlog in **Challenge Tracker**, not here.
- **Upsell Path:** each bullet must start with an allowed lead-in (`Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz Code`, `ASM`, **`Wiz DSPM`**, **`Wiz CIEM`**) plus a one-line value story, per [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md). When transcripts name **separate** expansion themes (sensitive data / PII / classification vs identity / entitlements / IAM), plan **separate** `upsell_path` appends — not one merged “Wiz Cloud” paragraph.

**Do not put in Goals / Risk / Upsell:** automation or QA about the notes doc (e.g. “internal check”, “parser”, “template”, “label-matching”, “H3 headings parse correctly”), or **ingestion status** framed as risk (e.g. “no new transcripts since …”). That content goes in **`pnotes_agent_log.md`** or planner metadata — see [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) (Exec Account Summary — forbidden meta).

Do **not** remove or rename the three H3 headings. If a customer doc predates this layout, note it in the change plan and align content to these headings on the next approved write.

---

## Communication Rule

At every step, tell the user what you are doing in plain English. Start each step with: `"Step X of 11 — [what I'm doing]"`. Do not skip steps. Do not reorder steps. Follow the format rules in `15-user-preferences.mdc`.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`** for the final response.
- After multi-step work, include **`### Activity recap`** with: what changed, what was skipped, and why.
- Always state approval/write status clearly (no writes run, preflight failed, E2E harness writer `dry_run` only vs real write completed, or approved production writes executed).

---

## Before You Start (Setup Checks)

Run these checks in order. If any check fails, **stop** and tell the user what failed and how to fix it. Do not continue until they confirm the fix. If the run is explicitly non-commercial and will not touch Upsell/commercial language, Check 4 can be marked `not_applicable`.

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

### Check 4 — Upsell SKU snapshots are fresh (when Upsell/commercial text is in scope)

For runs that may write `exec_account_summary.upsell_path` (or other SKU/commercial wording), check targeted local snapshots in:

- `./docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/`
- seed configuration: `./docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml`

Seed query SSoT is `kb_seed_queries.yaml` (`initial_query`, **`results`** = number of top-scoring KB rows to keep per seed, default **1**; **one shot + top-K**, not a depth drill).

For each seed relevant to the current deal:

- Snapshot files live under **`mcp_query_snapshots/<category>/`** (category = first segment of `initial_query`, e.g. `licensing`).
- Snapshot files are JSON envelopes with `query`, `saved_at`, `source_tool`, `result_count`, `results`, and usually `top_k`.
- For TASK-074 hosted KB snapshots: use **`docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml`** for path → query mapping; **missing** snapshot → re-run that row’s `initial_query` via `wiz_docs_knowledge_base` and overwrite the envelope (`wiz_cache_manager.py kb-snapshot save`).
- Refresh when per-file `saved_at` is older than 7 days or needed SKU coverage is missing.
- Preferred source is wiz-remote MCP `wiz_docs_knowledge_base`; respect max 10 concurrent calls and retry/backoff policy from `load-product-intelligence.md`.

If wiz-remote is unavailable, proceed with on-disk snapshots and explicitly call out staleness risk in the run output. Do not fabricate SKU/licensing claims.

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
- **Commercial grounding prereq (when Upsell/commercial is in scope):**
  1. Start with `read_doc` output from Step 3.
  2. Read only relevant JSON snapshots in `./docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/<category>/` for SKUs in play (e.g. `licensing/wiz-code-billable-units.json`), not every file in the tree.
  3. Use TASK-074 §G4 references (NIST CSF, NIST AI RMF, OWASP SAMM, OWASP LLM Top 10) as gap-framing context when shaping upsell logic and discovery prompts.
  4. Then continue with transcript/call-record/history reads below.
- This path is intentionally lighter than `Load Product Intelligence`; do not block UCN on a full product-intel sweep for this use case.
- **+4 — Transcripts (inside lookback only):** `./MyNotes/Customers/[CustomerName]/Transcripts/` (all `.txt` files **dated inside lookback**). Raw transcripts remain UCN's primary evidence at full fidelity for delta detection and quoting.
- **+3 — Daily Activity Logs:** In local notes or synced export, ingest **only** content under **Daily Activity Logs** with **date headings inside lookback**. Do **not** propose generic edits to this section; the **only** allowed write is the documented `prepend_daily_activity_ai_summary` flow (see `docs/ai/references/daily-activity-ai-prepend.md`), not part of the default UCN mutation plan.
- **+2 — Account Summary tab (full):** Same notes export / doc as Step 3 — **entire** Account Summary tab: **Challenge Tracker**, **Company Overview**, **Contacts**, **Org Structure**, **Cloud Environment** (CSP/Regions, Platforms, IDP, DevOps/VCS, Security, ASPM, Ticketing, Languages, Sizing), **Use Cases / Requirements**, **Workflows / Processes**, and **Exec Account Summary** (Goals / Risk / Upsell — `top_goal`, `risk`, `upsell_path` in JSON).
- **+1 — AI_Insights:** `./MyNotes/Customers/[CustomerName]/AI_Insights/` — **History Ledger** (`[CustomerName]-History-Ledger.md`), optional `SEED-Deal-Stage-Tracker.md`, prior `*-AI-AcctSummary.md`, etc. **Read regardless of file date.**
- Local notes path: `./MyNotes/Customers/[CustomerName]/[CustomerName] Notes.md`
- Optional: `Customer-Full-Context.md` if it exists
- **Audit log:** `./MyNotes/Customers/[CustomerName]/pnotes_agent_log.md` (and `.archive.md` if present) — check for active rejection watermarks and prior run outcomes (not on the +1–+4 scale; operational requirement).

#### Lookback split — transcripts vs call-records (TASK-051 §D)

UCN stays **transcript-first inside lookback** and reaches for **targeted** call-records only when recent evidence names pre-lookback history by id, SKU, or stakeholder:

- **Inside lookback (default 1 month):** raw transcripts at weight **+4** (unchanged). Do **not** also load `call-records/*.json` for calls dated inside lookback — those are already covered by the raw transcripts and double-counting them inflates the signal.
- **Outside lookback:** do **not** load raw transcripts. Instead, when Block A (Challenge Tracker) or the Deal Stage Tracker references history by **challenge id**, **SKU**, or **stakeholder name**, perform a **targeted** `read_call_records` and filter the result to **≤ 5 specific records** (by `call_id` and/or `raw_transcript_ref`). `read_call_records` does not currently accept an `ids=[…]` parameter — caller discipline: narrow the result set in memory to just the ids you actually need to cite. A wholesale `read_call_records()` sweep is an **Account Summary** concern, not a UCN concern.
- **`challenge-lifecycle.json`** remains the cheap cross-call compressed state (one `read_challenge_lifecycle` per run).
- **Signal preference:** When a targeted call-record exposes a schema v2 field (`metrics_cited`, `stakeholder_signals`, `goals_mentioned`, `risks_mentioned`), prefer that structured value over re-quoting the transcript — it is already the compressed memory of that call.

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

Analyze the loaded transcripts and notes. Extract structured facts using the categories and rules defined in [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) (see hub [`README.md`](../gdoc-customer-notes/README.md)).

**Transcript scan — route “requirement” signal to Use Cases (not Goals):** While reading each in-lookback call, flag lines that are **requirements / operating asks** (reporting cadence or format, deliverable shape, must-have capability, compliance or evidence pack, integration behavior the product must support). For each **new** distinct requirement not already reflected under **Use Cases / Requirements** in Step 3’s `read_doc` JSON, plan **`use_cases` / `free_text`** with **`append_with_history`** in Step 8 (with `evidence_date`, `reasoning`, `theme_key`). **Do not** put those in **`exec_account_summary` / `top_goal`** unless the transcript states a **rolled-up strategic business outcome** (few big goals); see [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) — **Goals** vs **Use Cases / Requirements**.

**Transcript scan — route expansion / cross-sell to Upsell Path (DSPM, CIEM, core SKUs):** After Step 3 `read_doc`, compare **active** `exec_account_summary.upsell_path` bullets to in-lookback transcripts (and optional bounded `read_call_records` fields such as `products_discussed`, `upsell_signals`). Plan **`append_with_history`** on **`upsell_path`** when **all** are true: (1) the transcript states a **clear solution-fit or expansion** narrative, (2) it is **not** already represented by an existing upsell bullet (same lead-in + same core claim — skip duplicates), (3) it belongs in exec cross-sell, not in Use Cases (requirements) or Workflows (process). **Routing cues (non-exhaustive):** sensitive data / PII / classification / “what sensitive data we have” / acquisition data posture → **`Wiz DSPM`**; cloud identity / entitlements / excessive permissions / IAM / non-human identities → **`Wiz CIEM`**. **Do not** absorb a distinct DSPM or CIEM thread into a single **`Wiz Cloud`** bullet just to save space — one bullet per **distinct** exec expansion line. Use `evidence_date` from the supporting call; `theme_key` stable per thread (e.g. `upsell-dspm-acquisition-data`). This is how E2E / UCN produces the mutation JSON **without** hand-maintaining `tmp/*.json`.

**Transcript scan — route competitive/vendor displacement to Accomplishments:** If transcripts or call-records show a non-Wiz product being displaced, decommissioned, or retired as part of adoption progress, plan an `accomplishments.free_text` `append_with_history` row with evidence date and concise business/security impact. Keep process implementation detail in `workflows` when helpful, but do not leave a clear adoption win only in Workflows.

**Transcript scan — route named products to Cloud Environment `tools_list`:** For each **third-party product or service** the customer **actively uses** (stated in transcript), compare Step 3 `read_doc` `cloud_environment` tool maps. Plan **`add_tool`** with the correct **`field_key`** using the **rubric-first** table in [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) → **Cloud Environment — `tools_list` routing** (intent by role: CI/CD vs SIEM vs ticketing, etc.). **Do not** require a curated vendor list — route by **function in context**. If the rubric leaves **two** plausible `field_key`s, use **at most one** optional public lookup to disambiguate (same doc: Option 2 backup); if still unclear, skip or ask the operator. One coverage-table row per **distinct** missing tool.

Compare extracted facts against **three** sources of current/historical truth:
1. **Google Doc state** from Step 3 (current doc content, challenge tracker, deal stage tracker)
2. **History Ledger** from Step 4 (how the account looked at prior snapshots)
3. **Audit log** from Step 4 (what was previously tried or rejected)

Use these cross-references to:
- **Avoid proposing challenges that are already resolved** — if the challenge tracker says "Resolved" and no transcript contradicts it, skip it.
- **Avoid recommending products already purchased** — if Deal Stage Tracker says a SKU is at "win" stage, do not propose buying it again. Do not propose challenges that were pre-sale issues likely solved after purchase.
- **Detect regressions** — if the ledger shows a challenge was resolved but transcripts suggest it resurfaced, flag it for clarification.
- **Detect stale state** — if the ledger's last row is old and transcripts show material changes, note the gap.

**Daily Activity Logs — prepend-per-call (required; feed Step 8):**
- From Step 3 `read` JSON, treat `daily_activity_logs.free_text` entries as paragraphs: derive a **normalized meeting title key** for each block’s **first line** (strip leading `#`, trim — same idea as the duplicate guard in `docs/ai/references/daily-activity-ai-prepend.md`).
- From Step 4 transcripts **within lookback**, list meetings you can recap (date, title, source path). **UCN emits one DAL prepend per call in the lookback window**, not per chosen narrative. For a customer with N in-lookback transcripts, `daily_activity_logs.free_text` receives exactly N new date-headed groups (after the duplicate guard filters out meetings that already have a recap).
- **Only recap meetings with usable transcript content.** If a meeting block contains `[No Transcript Data]` (or otherwise lacks substantive transcript body), mark it as `no transcript available`, record `skipped:dal_prepend call=<date> reason=empty_transcript` in the run log (§F), and do **not** include it in Daily Activity recap mutations.
- **Missing recaps:** meetings whose proposed `heading_line` would **not** duplicate any existing normalized first line. If the same calendar meeting already has a recap, skip unless the user asked to refresh it.
- Carry the **missing** list (count + identifiers) into Step 8.

**Populatable-field walk (required; feed Step 8):** Enumerate every populatable GDoc field the planner must visit in Step 8 — 15 fields, listed in Step 8 below. For each, decide whether the in-lookback transcripts contain explicit signal; if yes, draft a candidate mutation; if no, pre-classify the skip reason (`no_in_scope_transcript_signal`, `same_as_current_entry`, `evidence_below_confidence_threshold`, `section_off_by_opt_out`). The per-field extraction rules are the canonical list in `.cursor/rules/21-extractor.mdc` § **Per-section GDoc extraction**.

**Call records vs UCN (today):** Inside lookback, **raw transcripts stay primary** (+4); do **not** treat `call-records/*.json` as a second full evidence stream for the same dates (see **`.cursor/rules/20-orchestrator.mdc`** — *Call-record reads inside UCN*). **Optional gap check:** after the transcript scan, run **one** bounded **`read_call_records`** for the customer, then for each in-lookback `call_id` compare schema **v2** fields (`goals_mentioned`, `risks_mentioned`, `metrics_cited`, `stakeholder_signals`, `products_discussed`, etc.) to your Step 6 notes. If structured extract names a **theme** you did not route to a section yet, add it to the right row in the **coverage table** below or record why you skip—**transcript wording still wins** for quotes and strict metadata.

**Show your work (required before Step 8):** Emit a **markdown table** in chat (no JSON yet) so the operator can see full coverage before mutations:

| # | Source (transcript date + file or `call_id`) | Signal (one line) | Planned `section_key` / `field_key` (or “none”) | Planned action (`append_with_history` / `no_evidence` / other) | Skip reason if not mutating |
|---|----------------------------------------------|-------------------|--------------------------------------------------|----------------------------------------------------------------|-----------------------------|

- One row per **distinct** requirement (use **Use Cases** routing from the paragraph above), per **strategic** goal/risk candidate, per **distinct Upsell Path** lead-in (e.g. separate rows for **Wiz DSPM** vs **Wiz CIEM** vs **Wiz Cloud** when transcripts support separate threads), and per **meaningful** populatable-field hit from the 15-field walk; merge duplicates.
- If the table is empty of real signals, say so explicitly and still complete the row walk with `no_evidence` or skip reasons in Step 8.

**Where sections are “configured” (for the model):** **Shape** (which sections/fields exist, keys, strategies) → `prestonotes_gdoc/config/doc-schema.yaml`. **Meaning** (Goals vs Risk vs Use Cases vs Cloud, forbidden text, tool rules) → [`docs/ai/gdoc-customer-notes/README.md`](../gdoc-customer-notes/README.md) and the `mutations-*.md` packs it indexes. **Process** (this step order, lookback, DAL, tables) → this playbook and **`.cursor/rules/20-orchestrator.mdc`**.

**Tell user:** "Step 6 of 11 — I read through all the notes, built the coverage table ([N] rows), optional call-record gap check [done / skipped], [N] conflicts, Daily Activity: [N] of [N] in-lookback calls still need a recap, and [N] of the 15 populatable fields carry in-scope transcript signal."

### Step 7 of 11 — Clarification gate (ask before acting on ambiguity)

Before building the change plan, present **numbered questions** to the user for any situation where the evidence is unclear. Common triggers:

- **Resolved-but-maybe-not:** The doc says a challenge is Resolved, but a recent transcript mentions the same problem. Ask: "Challenge X was marked Resolved on [date]. Transcript from [date] mentions it again. Should I reopen it in the challenge tracker, or is it a different issue?"
- **Product already bought:** Deal Stage Tracker shows SKU at "win" but notes suggest expansion issues. Ask: "Wiz [SKU] shows as purchased. Should I add an expansion risk, or is this resolved?"
- **Prior rejection with ambiguous new evidence:** Audit log shows a rejection, and new evidence partially overlaps. Ask: "I proposed [X] last time and you rejected it. New transcript from [date] has related info. Should I try again?"
- **Unresolved problem with no update:** A challenge has been open for 60+ days with no new evidence. Ask: "Challenge [X] has been open since [date] with no updates. Is it still active, resolved, or should I mark it Needs Validation?"
- **Account Metadata discrepancy:** Notes suggest a new champion or exec buyer but no explicit statement. Ask: "[Name] appears to be acting as champion based on [evidence]. Should I update Account Metadata?"

If no conflicts or ambiguities exist, skip this step and say so.

[STOP — wait for user answers before continuing. Use their responses as evidence for the change plan. For `_TEST_CUSTOMER` E2E runs triggered by `.cursor/rules/11-e2e-test-customer-trigger.mdc`, do not pause; record `clarification_gate: none` and continue.]

**Tell user:** "Step 7 of 11 — I have [N] questions before I build the plan. [questions]. Please answer and I'll use your responses as evidence."

### Step 8 of 11 — Build the change plan

Every mutating row in the JSON must **trace to a row** in the Step 6 **Show your work** table (same `theme_key` / same source) **or** be an allowed mechanical row (e.g. `prepend_daily_activity_ai_summary`, lifecycle/challenge rows) documented in the Step 8 summary. Do not invent net-new bullets that never appeared in Step 6.

Produce a typed change plan (mutation JSON) following the schema, core rules, and quality gate in [`mutations-global.md`](../gdoc-customer-notes/mutations-global.md). Each proposed change must include:
- `reasoning`: why this change is being proposed
- `evidence_date`: the date from the transcript/notes that supports it
- `theme_key`: stable key for duplicate control

Incorporate user answers from Step 7 as evidence (cite "user confirmation [date]" as evidence source).

### TASK-073 canonical coverage matrix (single source)

This section is the canonical policy table for planner-required coverage and preflight checks. `docs/ai/gdoc-customer-notes/mutations-global.md` points here and must not maintain a second copy.

**Mode contract (`ucn_mode`):**

- **Preflight always enforces the full coverage matrix** (`required_in_ucn_full` in `scripts/ucn-planner-preflight.py` `TARGET_MATRIX`). Every target needs a `mutate` or `skip` (with an allowed `skip_reason`).
- `planner_contract.ucn_mode` is optional; set it to `full` for clarity. Any other value (e.g. legacy `partial`) is **ignored** and a **stderr warning** is printed when running `ucn-planner-preflight.py` — the validator still uses the full matrix.
- E2E workflow names (`v1_full`, `v2_full`, etc.) are harness labels, not a second preflight mode.

**Decision contract (required in `planner_contract.coverage.decisions`):**

- **Intent:** The gate is *accounting*, not *filling the doc*. Every matrix target must have a row so each section was **considered**; **`skip` with a reason is a passing outcome** when there is no defensible change (avoids bad or invented data). Only use **`mutate`** when evidence supports the write.
- `action`: `mutate` or `skip` (`no_evidence` is accepted as a `skip` *action* synonym in the preflight code path for backward compatibility — you still need a real `skip_reason` from the list below).
- For `skip`, `skip_reason` is required and must be one of:
  - `no_in_scope_transcript_signal` — typical when the in-scope corpus has nothing usable for that section
  - `same_as_current_entry` — already represented; no edit needed
  - `evidence_below_confidence_threshold` — signal too weak to change customer-facing text
  - `section_off_by_opt_out` — out of scope for this run (rare; document in run notes)
  - `empty_transcript` — e.g. DAL guard when a meeting has no substance

| target | tab | required_in_ucn_full | required_in_ucn_partial | allowed_actions_when_mutate | evidence_rule | validator_fail_code |
|---|---|---|---|---|---|---|
| `exec_account_summary.top_goal` | account_summary | yes | yes | `append_with_history`,`set_if_empty`,`replace_field_entries` | standard | `coverage_mutation_missing` |
| `exec_account_summary.risk` | account_summary | yes | yes | `append_with_history`,`set_if_empty`,`replace_field_entries` | standard | `coverage_mutation_missing` |
| `exec_account_summary.upsell_path` | account_summary | yes | yes | `append_with_history`,`set_if_empty`,`update_in_place`,`replace_field_entries` | deal_stage_trigger_path | `coverage_mutation_missing` |
| `challenge_tracker` | account_summary | yes | no | `add_table_row`,`update_table_row` | challenge_row_evidence | `coverage_mutation_missing` |
| `company_overview.free_text` | account_summary | yes | no | `append_with_history` | standard | `coverage_mutation_missing` |
| `contacts.free_text` | account_summary | yes | no | `append_with_history`,`replace_field_entries` | named_contact_evidence | `coverage_mutation_missing` |
| `org_structure.free_text` | account_summary | yes | no | `append_with_history` | standard | `coverage_mutation_missing` |
| `cloud_environment.csp_regions` | account_summary | yes | no | `set_if_empty`,`update_in_place`,`replace_field_entries` | standard | `coverage_mutation_missing` |
| `cloud_environment.platforms` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.idp_sso` | account_summary | yes | no | `set_if_empty`,`update_in_place`,`replace_field_entries` | standard | `coverage_mutation_missing` |
| `cloud_environment.devops_vcs` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.security_tools` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.aspm_tools` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.ticketing` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.languages` | account_summary | yes | no | `add_tool`,`update_tool_detail`,`remove_tool_suggestion` | tool_evidence | `coverage_mutation_missing` |
| `cloud_environment.sizing` | account_summary | yes | no | `set_if_empty`,`update_in_place`,`replace_field_entries` | numeric_or_capacity_signal | `coverage_mutation_missing` |
| `cloud_environment.archive` | account_summary | yes | no | `append_with_history` | standard | `coverage_mutation_missing` |
| `use_cases.free_text` | account_summary | yes | yes | `append_with_history`,`replace_field_entries` | requirements_signal | `coverage_mutation_missing` |
| `workflows.free_text` | account_summary | yes | yes | `append_with_history`,`replace_field_entries` | workflow_signal | `coverage_mutation_missing` |
| `accomplishments.free_text` | account_summary | yes | no | `append_with_history` | resolved_outcome_signal | `coverage_mutation_missing` |
| `daily_activity_logs.free_text` | daily_activity | yes | yes | `prepend_daily_activity_ai_summary` | dal_parity | `coverage_mutation_missing` |
| `account_motion_metadata.exec_buyer` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | explicit_statement_required | `coverage_explicit_statement_required` |
| `account_motion_metadata.champion` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | explicit_statement_required | `coverage_explicit_statement_required` |
| `account_motion_metadata.technical_owner` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | standard | `coverage_mutation_missing` |
| `account_motion_metadata.sensor_coverage_pct` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | numeric_value_required | `coverage_numeric_value_invalid` |
| `account_motion_metadata.critical_issues_open` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | numeric_value_required | `coverage_numeric_value_invalid` |
| `account_motion_metadata.mttr_days` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | numeric_value_required | `coverage_numeric_value_invalid` |
| `account_motion_metadata.monthly_reporting_hours` | account_metadata | yes | no | `set_if_empty`,`update_in_place` | numeric_value_required | `coverage_numeric_value_invalid` |
| `deal_stage_tracker` | account_metadata | yes | no | `add_table_row`,`update_table_row` | deal_stage_trigger_path | `coverage_mutation_missing` |

Excluded from planner-required coverage in TASK-073: `discovery.free_text`, `appendix.free_text`, `appendix.agent_run_log`.

**Coverage artifact (required):** before approval, store explicit planner decisions in the same mutation bundle under `planner_contract.coverage.decisions`; no silent skips.

**Deterministic planner contract (TASK-072, required):** include a top-level `planner_contract` object in the same JSON file as `mutations` and run preflight before Step 9/10.

- **DAL contract (`planner_contract.dal`):**
  - `expected_missing_count` (int): count of meetings from Step 6 missing list.
  - `expected_missing_keys` (`list[str]`): normalized keys (`YYYY-MM-DD:<slug>`) for missing meetings.
  - `skips` (`list[{meeting_key, reason}]`): only for allowed skip cases (e.g. empty transcript).
- **Deal Stage contract (`planner_contract.deal_stage`):**
  - `expected_skus` (`list[str]` from `cloud|sensor|defend|code`) that should move or be explicitly accounted for this run.
  - `no_change_with_reason` (`list[{sku, reason}]`) when expected SKU is intentionally unchanged.
- **Hard gate command (must pass):**

```bash
uv run python scripts/ucn-planner-preflight.py \
  --mutations "./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json" \
  --json-output
```

If preflight prints `planner_contract_failed` / non-zero, do **not** proceed to Step 9/10. Fix the mutation plan first.

**Contacts — LLM-built `contacts.free_text` (required; no sidecar mutation generators):**

- **You** (the agent executing UCN) compose `append_with_history` rows for `contacts` / `free_text` inside the **same** Step 8 mutation JSON as everything else. Do **not** substitute a repo Python “mutation builder” script or disposable `/tmp/*.json` as the plan — the next playbook run would not reproduce that path for 20+ real accounts.
- **Evidence (multi-customer):** For each named person, tie the Step 6 table row to **(a)** a quoted or cited line from an in-lookback **transcript**, and **(b)** when `call-records/<call_id>.json` exists for that call, cite matching **`participants[]`** / **`stakeholder_signals[]`** as structured support (roles + `signal` enum). Rules and phrasing live in [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) → **Contacts — evidence and mutation shape**.
- **Shape:** `Name - role/context` one bullet per distinct person; `theme_key` = `contact:<kebab-from-display-name>`; `evidence_date` = ISO **call** date (transcript `DATE:` / record `date`), not the run date; `reasoning` lists transcript path + optional call-record path (never paste harness or TASK ids into `new_value`).
- **Dedupe:** If Step 3 `read_doc` already has an active contact line for the same normalized name, skip with `same_as_current_entry` or enrich via playbook-allowed actions only when evidence adds material fact.
- If **no** named stakeholders exist in scope, use `no_evidence` / skip reason on the Step 6 row — do not fabricate names.

When you **do** append to the exec summary, target the correct field so new text becomes a **bullet under the matching H3** (**Goals** / **Risk** / **Upsell Path**). Do not place deal-risk language in `top_goal` or SKU upsell lines in `risk`.

**Account Metadata and Deal Stage Tracker rules:**
- Only update Deal Stage Tracker if there is **explicit proof** a SKU stage changed (transcript quote, contract reference, user confirmation). Otherwise, ask in Step 7 and use the response as proof.
- Only update `exec_buyer`, `champion`, `technical_owner` when explicitly stated in source evidence.

**Daily Activity Logs — meeting recaps (required each run):**
- Do **not** append or replace arbitrary text in Daily Activity. The **only** allowed write is **`prepend_daily_activity_ai_summary`** (see `docs/ai/references/daily-activity-ai-prepend.md`).
- For **each** meeting in the Step 6 **missing** list, add one **`prepend_daily_activity_ai_summary`** object to the **same** mutation JSON as the rest of UCN (`section_key`: `daily_activity_logs`, `field_key`: `free_text`). Include `heading_line`, `body_markdown`, `evidence_date`, `reasoning`, and `source`.
- Do **not** generate `prepend_daily_activity_ai_summary` for meetings marked `no transcript available` in Step 6. Never write placeholder summaries.
- Draft recaps using `docs/ai/references/granola-meeting-summary-templates.md` (T1–T5 by call type) and `docs/ai/references/daily-activity-ai-prepend.md` (Format B). In `body_markdown`, use top-level bold-label lines and nested bullets (e.g. `- **Context:**` style) as in that prepend doc.
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

- **Challenge lifecycle anchors:** warn in the Step 8/9 handoff if any `challenge_tracker` change would put `[lifecycle_id:` in the **Challenge** column; anchors belong in **`notes_references`** only (see `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md`).
- Trends are stated when evidence spans multiple recent calls.
- Value realized is explicit, dated, and evidence-tagged when available.
- Next steps for SE are concrete (owner/action/timebox) and not generic.
- Any unsupported area uses explicit `no_evidence` language instead of invented detail.

**Tell user:** "Step 8 of 11 — I built the change plan. [N] proposed changes, [N] sections marked no new evidence, [N] Daily Activity meeting recap(s) to prepend."

### Step 9 of 11 — Show proposed changes and wait for approval

Display the proposed changes grouped by section using the diff preview format from [`mutations-global.md`](../gdoc-customer-notes/mutations-global.md). Include **`prepend_daily_activity_ai_summary`** items explicitly (show `heading_line` and a short excerpt of `body_markdown` for each).

**Tell user:** "Step 9 of 11 — Here are the changes I want to make. Please review and say yes, no, or tell me which ones to keep."

[STOP — wait for user approval before continuing. Do not write anything until the user says yes. For `_TEST_CUSTOMER` E2E runs under `.cursor/rules/11-e2e-test-customer-trigger.mdc`, record `approval: bypassed per 11-e2e` and continue without a user pause.]

**If user rejects (all or some):** Follow the rejection logging process below (section "When User Rejects Changes").

### Step 10 of 11 — Apply approved changes

Save the approved change plan to **`./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json`** (or another path **under that customer folder** so it rsyncs to Google Drive — avoid disposable `/tmp` paths as the only copy). For production recovery, `write_doc` also caches an always-latest copy and state under `AI_Insights/ucn-recovery/` (`latest-mutations.json`, `latest-write-state.json`).

**Planner preflight (required every UCN write, all customers):** run **`scripts/ucn-planner-preflight.py`** on the same mutations JSON **before** calling **`write_doc`** / **`update-gdoc-customer-notes.py write`**. If preflight exits non-zero or returns `planner_contract_failed:*`, **do not** write — fix the mutation plan first. Preflight enforces the planner contract (coverage matrix, DAL parity, Deal Stage triggers, etc.); it is **not** the same as the writer’s Doc API **`dry_run`** preview.

**Production / normal customers (after Step 9 approval):** MCP **`write_doc`** with `doc_id`, `mutations_json`, **`dry_run=false`**, and **`customer_name`** when known. Step 9 already showed the diff; do not cycle `dry_run=true` as a default extra gate.

**`_TEST_CUSTOMER` E2E harness only:** after preflight passes, you **must** call **`write_doc`** with **`dry_run=true`** once (or `update-gdoc-customer-notes.py write --dry-run`) to preview engine output, **then** run the real write — see [`tester-e2e-ucn.md`](tester-e2e-ucn.md) (**Required writer dry-run**). Skipping the writer preview before the real write is a **failed** E2E for `e2e_default`, not production policy.

**In Terminal (same order as MCP):**

```bash
uv run python scripts/ucn-planner-preflight.py \
  --mutations "./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json" \
  --json-output

uv run prestonotes_gdoc/update-gdoc-customer-notes.py write \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml \
  --mutations "./MyNotes/Customers/[CustomerName]/AI_Insights/ucn-approved-mutations.json" \
  --customer-name "[CustomerName]"
```

Add **`--dry-run`** on `write` only for the **`_TEST_CUSTOMER` E2E harness** (required there before each real write per [`tester-e2e-ucn.md`](tester-e2e-ucn.md)) — **not** as the default production path.

**What the writer does before it emits the final applied change set:**

- **Append-with-history timestamp emission** — for the four `append_with_history` fields (`exec_account_summary.top_goal` / `risk` / `upsell_path`, `appendix.agent_run_log`) the writer renders each newly added entry as `<value> [YYYY-MM-DD]` using the current run date. Pre-existing entries without a timestamp are left alone (append-only; no backfill). This is what drives the acceptance bar in §G — every new `append_with_history` entry in the post-run doc carries `[YYYY-MM-DD]`.
- **Challenge Tracker ↔ lifecycle reconciliation pass** — when `write_doc` receives the customer name, the writer loads `MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json` and, for every Challenge Tracker row whose **Notes & References** cell carries a `[lifecycle_id:<id>]` anchor (or legacy `lifecycle:`), rewrites the row `status` to match the lifecycle mapping: `identified → Open`, `in_progress → In Progress`, `stalled → Stalled`, `resolved → Resolved` (plus `acknowledged → Open`, `reopened → In Progress`). Each row the reconciler flips shows up as an applied change with `action=reconcile_with_lifecycle`. If lifecycle JSON is absent or unreadable, the reconciler is a no-op and the rest of the write proceeds unchanged. **Anchor rules, parity gate (including new lifecycle ids), and when to add a tracker row vs JSON-only:** see [`mutations-account-summary-tab.md`](../gdoc-customer-notes/mutations-account-summary-tab.md) — section **Challenge lifecycle ↔ Challenge Tracker parity**.
- **Deal Stage Tracker motion capture** — for every SKU (`cloud`, `sensor`, `defend`, `code`) cited in an applied `exec_account_summary.upsell_path` entry, the writer advances the Deal Stage row: `not-active → discovery` by default, `→ pov` when the upsell text matches POV evidence phrases (`pov`, `timeboxed`, `pilot`, `poc kicked off`, …), `→ win` when it matches purchase evidence phrases (`po signed`, `purchased`, `contract signed`, …). `activity` flips to `active`; `reason` is rewritten to `<stage> evidence in upsell_path (<call-date>)` using the most recent ISO date found in the upsell line (fallback: today). Applied as `action=advance_deal_stage_from_upsell`.
- **Agent run log append** — on a successful run with ≥ 1 applied mutation, the writer appends exactly one `appendix.agent_run_log` entry carrying the TASK-050 §F keys (`run_date`, `sections_touched`, `entries_added`, `entries_skipped`, `skipped_reasons`, `reconciled`, and — when the planner supplies them — `lookback_window`, `transcripts_in_scope`, `dal_prepends_emitted`). On rejection / zero-write runs the writer does **not** append a run-log entry (matches the "no ledger row on rejection" rule).

After write, re-run the `read` subcommand to confirm changes are reflected. Save the post-write doc state for the ledger row.

**Tell user:** "Step 10 of 11 — Changes written to Google Doc. Here's what changed: [summary]. Here's what I skipped and why: [summary]. Reconciled [N] Challenge Tracker rows against the lifecycle. Advanced [N] Deal Stage rows. Appended one `agent_run_log` entry with mutate/skip coverage outcomes."

### Step 11 of 11 — Append History Ledger row and sync

After a successful Google Doc write, assemble one **schema v3** row and append it via **MCP `append_ledger_row`**. The canonical column order and typing lives in **`prestonotes_mcp/ledger.py`** (`LEDGER_V3_COLUMNS`) and the full spec is **`docs/project_spec.md`** § _Ledger writes: `append_ledger` vs `append_ledger_row`_. Do **not** handcraft markdown tables in this playbook flow. Treat this write→ledger chain as one completion unit: if the doc write succeeded but the ledger append did not, the run remains incomplete until the ledger outcome is resolved and reported.

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
   - If append fails **after** `write_doc` succeeded, run recovery before ending the run: call MCP **`read_ucn_recovery_state`** (inspect `status`, `last_ledger_error`, `ledger_attempt_count`) and then **`recover_ledger_from_latest(customer_name, doc_id, dry_run=false)`**. The run is not complete while state is `write_succeeded_ledger_pending` or `recovery_failed`.

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
- The change plan JSON should be saved under `./MyNotes/Customers/[CustomerName]/AI_Insights/` (for example `ucn-approved-mutations.json`, containing the **full** Step 8 plan the agent produced) so it syncs to Drive and survives reruns. **Do not** treat `/tmp/` as the only durable artifact store.
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
- [`docs/ai/gdoc-customer-notes/README.md`](../gdoc-customer-notes/README.md) — Customer Notes mutation doc hub; per-tab packs `mutations-*.md` (schema / quality gate: [`mutations-global.md`](../gdoc-customer-notes/mutations-global.md))
- `prestonotes_gdoc/config/prompts/010-wiz-solution-lens.md` — analysis lens
- `prestonotes_gdoc/config/prompts/015-customer-notes-se-persona-prompt.md` — operating persona
- `prestonotes_gdoc/config/doc-schema.yaml` — Google Doc section schema
- `.cursor/rules/core.mdc` — canonical field ownership, ledger schema, Daily Activity Logs guardrail (TASK-007)
