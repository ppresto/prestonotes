# Customer data ingestion — weights and lookback

Applies to any task that **loads or synthesizes** customer context: `Run Account Summary`, `Update Customer Notes`, `Load Customer Context`, `Run Full Account Rebuild` child reads, and similar.

## Lookback window (dated content)

- **Default:** **1 month** back from the **authoritative “today”** in the session (user info / system date). Count from that date: include transcript meetings and Daily Activity Log **dated subsections** whose dates fall **on or after** the lookback start.
- **Override:** If the user specifies **3, 6, or 12 months** (or an explicit `Lookback: N months`), use that window instead for **dated** sources below.
- **Undated / aggregate sources:** Not clipped by lookback unless the playbook says otherwise (see `AI_Insights`).

## Weight scale (higher = trust more for current-state truth)

Use weights when **prioritizing attention**, **resolving conflicts**, and **ordering synthesis**. When two sources disagree on a fact, prefer the **higher weight** unless the lower-weight source is **newer** and **in-window** (then reconcile explicitly).

| Weight | Source | What to load |
| :---: | :--- | :--- |
| **+4** | **Transcripts** | **v2 default:** per-call `Transcripts/*.txt` (dated headers). If only legacy bundles exist, use `_MASTER_TRANSCRIPT_*.txt` and other `.txt`. For **current-state** and **“what happened lately”**, prioritize **meetings inside the lookback**; older meetings support **history and continuity** only. |
| **+3** | **Daily Activity Logs** | Team collaboration section in the customer Google Doc or exported markdown. **Only** ingest content under **date-stamped headings** (e.g. `### Apr 2, 2026`) that fall **within the lookback** (or extended lookback if set). **Writes:** only the explicit `prepend_daily_activity_ai_summary` contract for meeting AI recaps (`docs/ai/references/daily-activity-ai-prepend.md`); otherwise treat as read-only (see core rules). **`Update Customer Notes`** must also **add** a prepend for **each** transcript meeting in lookback that is **not** already covered in Daily Activity (see `docs/ai/playbooks/update-customer-notes.md` Step 8). |
| **+2** | **Account Summary tab (full)** | The **entire** customer notes surface under the Google Doc **Account Summary** tab — not only the three **Exec Account Summary** bullets (**Goals**, **Risk**, **Upsell Path**). Load from the live doc read (`read` JSON), local `[CustomerName] Notes.md`, or export. **In scope for +2 ingestion:** **Challenge Tracker**; **Company Overview**; **Contacts**; **Org Structure**; **Cloud Environment** (including **CSP/Regions**, **Platforms (vm/containers/serverless)**, **IDP used for SSO**, **DevOps/VCS Tools**, **Security Tools**, **ASPM Tools**, **Ticketing Tools**, **Languages**, **Sizing**); **Use Cases / Requirements**; **Workflows / Processes**; **Exec Account Summary** (Goals / Risk / Upsell); plus any other **Account Summary**–tab sections in `doc-schema.yaml` for that customer (e.g. **Accomplishments**). **Out of scope at +2:** **Daily Activity Logs** (use **+3** with date filter) and the **Account Metadata** tab (Deal Stage Tracker, etc. — follow playbook; not on this four-tier scale). |
| **+1** | **`AI_Insights/`** | All files in `./MyNotes/Customers/[CustomerName]/AI_Insights/` — e.g. `*-History-Ledger.md`, `*-AI-AcctSummary.md`, seeds, other artifacts. **Load regardless of file `last_updated` or internal dates**; use as **aggregated memory and continuity** (weight lower than live transcript and recent logs). |

### Not in the table (still load when playbooks require)

- **`Product-Intelligence.md`**, Wiz doc cache — follow existing playbooks; they are not part of this four-tier customer weighting. (Legacy **`Customer-Full-Context.md`** is not used in v2.)
- **`pnotes_agent_log.md`** — operational / audit memory; read per playbook; not scored on this scale.

## How to apply in practice

1. **State the lookback** in the run (e.g. “Lookback: 1 month (default)”).
2. **Load in tier order** for mental model: transcripts (scan dates) → Daily Activity Logs (filter by date heading) → **full Account Summary tab** content (all sections above) → `AI_Insights/` folder.
3. **Synthesis:** Spend the most narrative depth on **+4** and **+3** in-window; use **+2** for **structured account truth** in the Account Summary tab (challenges, cloud env, use cases, workflows, contacts, exec bullets); use **+1** for ledger/history and prior AI artifacts without letting them override a fresher **+4** finding.

## Conflict resolution

1. **Same fact, different values:** Prefer **higher weight**. If the conflict is **transcript (+4)** vs **older Account Summary tab content (+2)** (including Challenge Tracker, Cloud Environment, Use Cases, or Exec bullets), trust **transcript** and flag stale **+2** fields.
2. **Transcript vs transcript:** Prefer **newer meeting date** within the lookback when they conflict.
3. **Daily Activity Logs vs transcripts:** **Transcripts (+4)** win for customer-stated technical/deal truth; **Daily Activity Logs (+3)** win for **internal team operational cadence** (what the team logged day-to-day). If both exist, cite both roles explicitly.
