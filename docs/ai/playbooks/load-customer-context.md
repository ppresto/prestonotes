# Playbook: Load Customer Context

Trigger:
- `Load Customer Context for [CustomerName]`
- `Load Context for [CustomerName]`

Purpose: rapid, recommendation-ready customer snapshot before answering questions or running downstream analysis tasks. This does not write any files — it only loads context and outputs a summary in chat.

> **v2 (TASK-007):** Prefer **per-call** `Transcripts/*.txt` (newest first) when present; use **`read_transcripts`** MCP or bounded reads. **`_MASTER_TRANSCRIPT_*.txt`** is a legacy fallback only. Use **`sync_notes`** MCP or `./scripts/rsync-gdrive-notes.sh` before loading.

---

## Communication Rule
At every step, tell the user what you are doing in plain English. Start each step with: `"Step X of 6 — [what I'm doing]"`. Follow the format rules in `15-user-preferences.mdc`.

---

## Step 1 of 6 — Setup checks
1. Run **`sync_notes`** MCP (optional customer scope) **or** `./scripts/rsync-gdrive-notes.sh` from repo root.
2. Ensure Product Intelligence freshness; refresh first if stale.
3. For any Wiz product/licensing/integration/capability detail needed for context:
   - Query Wiz MCP docs first via `wiz_search_wiz_docs` before using secondary sources.
   - If MCP docs are unavailable, mark those details as provisional.

**Tell user:** "Step 1 of 6 — Setup checks passed."

## Step 2 of 6 — Load customer files (weighted + lookback)
Use **`docs/ai/references/customer-data-ingestion-weights.md`**. Default **lookback: 1 month** for dated content unless the user specifies **3 / 6 / 12** months.

**Load and weight:**
1. **+4 — Transcripts:** Prefer **per-call** `Transcripts/*.txt` (exclude `_MASTER_*` when other `.txt` exist); otherwise `_MASTER_TRANSCRIPT_*.txt`. Prioritize **meetings within lookback** for “what’s true now.”
2. **+3 — Daily Activity Logs:** In `[CustomerName] Notes.md` or doc export, read **only** dated subsections under **Daily Activity Logs** that fall **within lookback**. Do not edit this section from this playbook; optional AI prepends use `prepend_daily_activity_ai_summary` (see `docs/ai/references/daily-activity-ai-prepend.md`).
3. **+2 — Account Summary tab (full):** All **Account Summary**–tab sections in `[CustomerName] Notes.md` or parsed doc — Challenge Tracker, Company Overview, Contacts, Org Structure, Cloud Environment (all subfields), Use Cases / Requirements, Workflows / Processes, and Exec Goals / Risk / Upsell.
4. **+1 — AI_Insights:** `[CustomerName]-AI-AcctSummary.md`, `[CustomerName]-History-Ledger.md`, and other `AI_Insights/` files **regardless of date**; tech acct plans if relevant.

**Tell user:** "Step 2 of 6 — I loaded sources for [CustomerName] with lookback [1|3|6|12] month(s) and applied ingestion weights (+4 transcripts … +1 AI_Insights)."

## Step 3 of 6 — Wiz data model normalization
1. Classify discussed Wiz security data into the correct object model before giving architecture or integration guidance:
   - `Wiz Defend`: `Detections -> Threats` (runtime/SOC response lane)
   - `Wiz Cloud`: `Findings -> Issues` (posture/remediation lane)
2. For each integration recommendation, explicitly map:
   - object type (`Threat`, `Detection`, `Issue`, `Finding`, `Audit Log`)
   - source module (`Defend`, `Cloud`, or platform/audit)
   - target system (`XSOAR`, `SIEM`, `ServiceNow`, `Jira`, etc.)
3. Build and use a customer-specific routing matrix before advising implementation:
   - default: `Threats -> SOC response workflow`
   - default: `Issues -> remediation ticket workflow`
   - default: `Audit logs -> SIEM analytics/correlation`
4. For integration capability questions:
   - Query Wiz MCP docs first (`wiz_search_wiz_docs`).
   - Distinguish `supported by docs` vs `recommended operating model for this customer`.
   - If support is not explicit in docs, say `not explicitly documented` and avoid assumptions.

**Tell user:** "Step 3 of 6 — Wiz data model mapped for [CustomerName]."

## Step 4 of 6 — Build context snapshot
1. Extract customer-stated priorities from the latest transcript using customer wording.
2. Build a recommendation-safety profile from `Wiz Commercials`:
   - licensed products
   - evaluating/planned products
   - unknown license fields that block immediate recommendations
3. Build an operational state snapshot from ledger + latest transcript:
   - current maturity state (`Reactive`, `Proactive`, `Automated`) per active workflow domain
   - active blockers and aging blockers
   - upcoming critical event(s)
4. Build a recommendation readiness map:
   - `Now (Licensed)` recommendation lanes
   - `Future (Requires Purchase/Expansion)` recommendation lanes
   - dependencies and unknowns to validate before implementation detail
5. Build a quote and evidence pack:
   - 2-4 customer quotes or paraphrases anchored to transcript context
   - explicit evidence references for each high-priority recommendation lane

**Tell user:** "Step 4 of 6 — Context snapshot built."

## Step 5 of 6 — Output snapshot in chat
- `Customer Snapshot` (5-8 bullets)
- `Wiz Product and License Snapshot`:
  - licensed products
  - known purchase dates
  - known renewal/expiration dates
  - unknown fields requiring validation
- `Wiz Object and Routing Matrix`:
  - Defend (`Detections -> Threats`) handling lane
  - Cloud (`Findings -> Issues`) handling lane
  - where each object class should route in this customer's current stack
- `Top Active Challenges` (P1/P2 focus)
- `Immediate Recommendations (Now - Licensed)`
- `Future Recommendations (Requires Purchase/Expansion)`
- `Critical Unknowns to Confirm` (max 5)
- `Recommendation Readiness Pack`:
  - top 3 recommendation lanes with:
    - business objective
    - expected outcome metric (`MTTR`, ticket volume, alert fatigue, ownership clarity, coverage)
    - implementation owner hypothesis (SOC, Cloud, AppSec, Platform)
    - confidence (`High/Medium/Low`)
    - blockers/dependencies
- `Deep-Dive Follow-up Questions`:
  - 3-5 technical implementation questions for architect/engineer sessions

**Tell user:** "Step 5 of 6 — Here's your [CustomerName] snapshot."

## Step 6 of 6 — Recommendation rules
- Never provide immediate technical recommendations that require unlicensed products.
- If license status is unknown, explicitly mark recommendation dependency as `License status unknown - verify`.
- Do not claim customer pain points unless directly supported by latest transcript/notes context.

**Tell user:** "Done. Context loaded for [CustomerName]. Ask me anything about this account."
