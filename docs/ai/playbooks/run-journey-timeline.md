# Playbook: Run Journey Timeline

Trigger: **`Run Journey Timeline for [CustomerName]`**

Purpose: Read **§7.1 call record JSON** for the customer, synthesize the **account story** (spec §9 TASK-012), assign **health** per **`docs/ai/references/health-score-model.md`**, and persist **`AI_Insights/<Customer>-Journey-Timeline.md`** with MCP **`write_journey_timeline`**. This playbook **also** contains the **Challenge governance** procedure formerly in **`Run Challenge Review`** (TASK-014): **Steps 5–8** — lifecycle JSON, union + dates, stall/drift, **one review table**, then approval-gated **`update_challenge_state`**.

**When to run (expectations):** Default **UCN** (orchestrator) already runs **Phase 0** — the same **challenge review table + Block A/B gates** — and may call **`write_journey_timeline`** after approval. Treat **this playbook** as the place to **refresh the Journey markdown artifact** and **challenge-lifecycle.json** when you want that work **without** a full UCN, or when UCN did not persist a timeline you still need.

When **Challenge governance is executed inside Update Customer Notes (UCN)** per **`.cursor/rules/20-orchestrator.mdc`**, **Steps 5–8** here are **folded into UCN’s Phase 0 + combined STOP** (do **not** duplicate a second STOP). For a **standalone** `Run Journey Timeline for [CustomerName]`, run **Steps 5–8** in full, then **Step 13** gates.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

Supporting rule: **`.cursor/rules/22-journey-synthesizer.mdc`**  
Challenge model: **`docs/ai/references/challenge-lifecycle-model.md`**  
Health rubric: **`docs/ai/references/health-score-model.md`**

---

## Communication rule

Tell the user what you are doing in plain English. Prefix each major step: **`Step X of 13 — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`** for tone.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`**.
- After multi-step work, always include **`### Activity recap`** with timeline outputs, challenge review coverage, skipped/deferred transitions, and pending approvals.
- Explicitly call out whether `write_journey_timeline` and any `update_challenge_state` writes were executed.

---

## Preconditions

1. **`[CustomerName]`** exists under **`MyNotes/Customers/[CustomerName]/`** (use **`sync_notes`** if the mirror may be stale).
2. **Call records** should exist for meaningful synthesis. If **`read_call_records`** returns **`count` < 2**, still run the flow but set health **⚪ Unknown** per **`health-score-model.md`** and say so explicitly.
3. Keep **`read_call_records`** payloads within context limits; if the corpus is huge, process **chronologically** in windows and merge summaries **without losing challenge ids**.
4. **`challenge-lifecycle.json` (§7.4):** This file exists only **after** approved **`update_challenge_state`** writes. Under the `_TEST_CUSTOMER` E2E flow (TASK-044) the file is absent after reset/bootstrap and gets created by the round-1 UCN playbook; there is no pre-seeding step.
5. **Stall signal (challenge governance):** Treat **no lifecycle or call-record movement** on a challenge for **≥ 60 days** as a **stall risk**, per **`challenge-lifecycle-model.md`**. Use **calendar days** between **today** (session date) and the **latest relevant date** for that challenge. If **`current_state`** is already **`stalled`**, surface **days since last transition** in **recommended action** instead of double-counting.

---

## Step 1 of 13 — Load all call records

1. MCP **`read_call_records([CustomerName])`** with filters **unset** unless the user supplied a **date range** or **`call_type`** scope. Records are returned sorted by `(date, call_id)`.
2. Optionally MCP **`read_ledger([CustomerName])`** for ledger-stated themes (commercial rows, challenge columns in v2 ledgers).

**Maps to spec TASK-012 step 1:** load validated §7.1 call record bodies directly — **`call-records/*.json`** is the sole source of truth now that the transcript index has been retired.

**Tell user:** `Step 1 of 13 — Loaded N call record(s) [+ ledger optional].`

---

## Step 2 of 13 — Chronological timeline of all calls

Sort by **`date`**, then **`call_id`** / sequence. Build an internal ordered list of every call with: **`call_id`**, **`date`**, **`call_type`**, **`summary_one_liner`**, **`sentiment`**, top **`key_topics`**.

**Tell user:** `Step 2 of 13 — Chronological spine has N call(s) from [first date] to [last date].`

---

## Step 3 of 13 — Milestone events

From the spine, label milestones where evidence supports them, for example:

- First substantive customer call (usually first **`discovery`** or earliest dated call).
- First clear “win” or positive inflection (pilot agreed, security outcomes, executive sponsorship).
- POC / technical deep dive start, POC readout, renewal or commercial thread (use **`call_type`** + content).

Each milestone bullet must cite **`call_id`** (and optional one-liner). Do not invent dates.

**Tell user:** `Step 3 of 13 — Identified M milestone(s) with citations.`

---

## Step 4 of 13 — Trace each challenge (narrative spine)

For each distinct **`challenges_mentioned[].id`** (canonicalize aliases per **`challenge-lifecycle-model.md`**):

- Track **`description`** drift across calls (latest wording wins in the narrative; earlier variants footnoted if useful).
- Track **`status`** over time; compare against **`AI_Insights/challenge-lifecycle.json`** when present (read from the workspace — **MCP does not expose a read tool** for this file in **`server.py`**). For **`_TEST_CUSTOMER`**, full E2E prep seeds a starter file so you can diff §7.4 history vs **`challenges_mentioned`** in call records; otherwise infer from **call records** alone unless the user pastes JSON.
- Apply **§7.4** vocabulary only.

Prepare a **Challenge trace table** (markdown): columns **`id`**, **`current_best_state`**, **`last_evidence_call_id`**, **`notes`**. The **formal TASK-014 review table** (stall, recommended_action, etc.) is built in **Step 8** after Steps 5–7.

**Tell user:** `Step 4 of 13 — Traced C challenge(s); formal review table follows in Step 8.`

---

## Step 5 of 13 — Challenge governance: optional sync

Run **`sync_notes`** with **`[CustomerName]`** (or full repo rsync) so local **`MyNotes/`** matches Drive when the user expects fresh data. Skip if Step 1 already synced and the user confirms freshness.

**Tell user:** `Step 5 of 13 — Sync complete (or skipped).`

---

## Step 6 of 13 — Challenge governance: read `challenge-lifecycle.json`

Read **`MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json`** from the workspace.

- If the file is **missing** or **empty object**, note “no persisted lifecycle yet” and rely on **call records** for ids (**Step 7**).
- For each challenge id in the JSON: capture **`current_state`** and the append-only **`history[]`** (`state`, `at` (YYYY-MM-DD), `evidence`).

**Tell user:** `Step 6 of 13 — Loaded lifecycle for N challenge id(s) [or none].`

---

## Step 7 of 13 — Challenge governance: merge universe and dates

Build the **union** of:

- All ids from **`challenge-lifecycle.json`**, and  
- All **`challenges_mentioned[].id`** values from call records (including **call-only** ids not yet in JSON).

For each **canonical** challenge id, compute:

| Field | Rule |
|-------|------|
| **Last updated (date)** | Latest of: (a) last **`history[].at`** for that id in **`challenge-lifecycle.json`**, (b) latest **`date`** among call records where that **`id`** appears in **`challenges_mentioned`**. If neither exists, leave blank and flag in **notes**. |
| **Evidence** | Short string: prefer **last `history[-1].evidence`**, else **`call_id` (YYYY-MM-DD): …** from the latest call mentioning the id; max **one** quote only if it fits. |
| **Current state** | From JSON **`current_state`** if present; else **infer read-only** from latest **`challenges_mentioned[].status`** and narrative (**§7.4** vocabulary only) and mark **“inferred (not persisted)”**. |

**Tell user:** `Step 7 of 13 — Unified U challenge row(s) [including K call-only id(s) if any].`

---

## Step 8 of 13 — Challenge governance: stall, drift, and review table

1. **Days since last updated** — from Step 7 vs session date.
2. **Stall flag** — if **`current_state`** is **`in_progress`**, **`acknowledged`**, or **`identified`** and days **≥ 60**, set stall flag **yes** and phrase like **“no movement 65d”** (use actual day count).
3. **Drift** — if persisted **`current_state`** disagrees materially with the latest call narrative, note **“drift: lifecycle vs calls”** (do **not** auto-write).

Present one markdown **table** (all challenges, including **resolved** unless the user asked to hide them):

| Column | Content |
|--------|---------|
| **`challenge_id`** | Canonical id (semantic ids like `soc-budget-freeze-q1` are fine when that is what call records use). |
| **`description`** | Latest short label from calls or JSON context. |
| **`current_state`** | **`identified`** \| **`acknowledged`** \| **`in_progress`** \| **`resolved`** \| **`reopened`** \| **`stalled`** (or inferred + tag). |
| **`last_updated`** | **`YYYY-MM-DD`** from Step 7. |
| **`evidence`** | Compact pointer from Step 7. |
| **`stall / risk`** | e.g. **“—”**, **“stalled 65d”**, **“at risk (drift)”**. |
| **`recommended_action`** | One imperative line. |

**Manual QA (spec §9 TASK-014):** On a customer with **≥ 3 challenges**, verify **all rows appear**, **stall flags** match dates, and **≥ one** **`recommended_action`** is clearly sensible.

Embed this table in the **Journey Timeline** document in **Step 12** (section **Challenge review (TASK-014)** or under **Challenge journey**).

**Tell user:** `Step 8 of 13 — Stall/drift pass complete; review table ready (U rows).`

---

## Step 9 of 13 — Stakeholder evolution map

Union **`participants`** across calls. For each person: first seen, last seen, **role** changes, **`is_new`** hints, champion-like behavior (executive sponsor, internal Wiz ally) **only if supported by quotes or clear statements**.

**Tell user:** `Step 9 of 13 — Stakeholder map has P people with evidence anchors.`

---

## Step 10 of 13 — Value realized

Compile concrete **outcomes** from **`summary_one_liner`**, **`key_topics`**, **`action_items`** completions, POC language, and **`verbatim_quotes`** (max depth as needed). Each value bullet: **what**, **when (`call_id` / date)**, **evidence tag** when appropriate (§7.5).

**Tell user:** `Step 10 of 13 — Value section has V evidence-backed item(s) [or explicitly none found].`

---

## Step 11 of 13 — VP story arc (opening narrative)

Write **2–3 sentences** only: who they are, what problem matters, where they are in the journey, what happens next — **plain English**, no product jargon. This is the **`TASK-012` step 7** “story arc” opener (distinct from the longer **TASK-013** exec template).

**Tell user:** `Step 11 of 13 — Drafted VP opening (2–3 sentences).`

---

## Step 12 of 13 — Assemble Journey Timeline markdown

Produce one markdown document (UTF-8) suitable for **`write_journey_timeline`**, with **at least** these sections:

1. **Title** — `# <Customer> — Journey Timeline`
2. **Metadata** — Generated date (session), sources (`read_call_records`, optional `read_ledger`).
3. **Health** — Single line **`Health: 🟢|🟡|🔴|⚪ …`** using **only** the definitions in **`health-score-model.md`** (verbatim band rules from spec).
4. **The 30-Second VP Brief** — paste the Step 11 prose here (can be labeled as VP brief).
5. **Chronological call spine** — compact table: `Date | call_id | call_type | summary_one_liner | sentiment`
6. **Milestones** — bullets from Step 3.
7. **Challenge journey** — narrative from Step 4 trace **plus** the **Step 8 review table** (TASK-014) inline or as a subsection **Challenge review (TASK-014)**.
8. **Stakeholder evolution** — bullets or small table.
9. **Value realized** — bullets from Step 10.
10. **Strategic position & next moves** — short, grounded in last calls (no fiction).
11. **Optional appendix** — ids of transcripts referenced if you used **`read_transcripts`** for quotes.

Keep under configured max bytes; trim appendix first if needed.

**Tell user:** `Step 12 of 13 — Journey Timeline markdown assembled (~X chars).`

---

## Step 13 of 13 — Approval gates and MCP writes

### Gate A — Challenge lifecycle corrections

If Step 8 (or Step 4) implies **persisted** state changes, present a **compact table**: `challenge_id`, `new_state`, `evidence` (must include **`call_id`** or short quote / date).

**Say:** “I will call **`update_challenge_state`** once per approved row. Approve **all**, **none**, or specify which **`challenge_id`**s to update.”

**STOP** until the user approves. Do not call **`update_challenge_state`** before approval. Illegal transitions raise errors in **`append_challenge_transition`** — only propose **valid** single-step moves per **`prestonotes_mcp/journey.py`** / **§7.4**.

If **no** lifecycle writes are proposed, say **“Gate A — none proposed”** and skip **`update_challenge_state`**.

### Gate B — Journey timeline (mandatory if persisting)

Show the **Health** line and a **two-section preview** (VP brief + call spine header + first 2 rows). Then the full body in a collapsible or truncated view is acceptable if huge — but the approving user must see **enough** to validate claims.

**Say:** “I will call **`write_journey_timeline(customer_name, content)`** with the assembled markdown. **Approve / reject / request edits.**”

**STOP** until the user approves. Do not call **`write_journey_timeline`** before approval.

### Execute

1. For each approved challenge transition: MCP **`update_challenge_state(customer_name, challenge_id, new_state, evidence)`**.
2. On timeline approval: MCP **`write_journey_timeline([CustomerName], content)`** with the final markdown string.

**Tell user:** `Step 13 of 13 — Run Journey Timeline complete for [CustomerName].`

---

## MCP tools used

| Tool | Role |
|------|------|
| **`sync_notes`** | Optional refresh of **`MyNotes/`** |
| **`read_call_records`** | §7.1 JSON corpus for synthesis and **`challenges_mentioned`** (sorted by date) |
| **`read_ledger`** | Optional account history / v2 challenge columns |
| **`write_journey_timeline`** | Persist **`AI_Insights/<Customer>-Journey-Timeline.md`** (after approval) |
| **`update_challenge_state`** | Append lifecycle transitions (after approval) |

**Workspace read (no MCP read tool for this file):** **`MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json`**

---

## Relation to UCN (required behavior)

**Do not** paste the full **13-step** journey playbook into **`update-customer-notes.md`** — keep orchestration in **`.cursor/rules/20-orchestrator.mdc`**.

**UCN must keep sidecar sync:** After **`update_challenge_state`** (Block A, ≥1 row executed) **and/or** after **`write_doc`** (Block B), **`.cursor/rules/20-orchestrator.mdc`** requires a **`write_journey_timeline`** call so **`Journey-Timeline.md`** matches **`challenge-lifecycle.json`** and the latest account context (minimum: **Health**, **Challenge review / challenge journey**, **Strategic position**; fuller spine when steps **1–7** already loaded the corpus). **Not optional** for those paths.

**`Run Journey Timeline` standalone:** Use when you want the **full** playbook pass (all **13** steps, both gates) without running UCN.

---

## References

- **`docs/project_spec.md`** §6 Stage 2 diagram, §7.1, §7.4, §9 TASK-012, TASK-014 (merged here)  
- **`prestonotes_mcp/tests/test_journey_tools.py`** — expected filesystem targets for journey outputs
