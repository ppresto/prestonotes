# Playbook: Run Challenge Review

Trigger: **`Run Challenge Review for [CustomerName]`**

Purpose: Produce a **single review table** of every challenge — **current state**, **last updated**, **evidence anchors**, **recommended action** (including stall signals, e.g. “follow up — stalled 65 days”). Inputs: **`MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json`**, **§7.1 call records**, optional **History Ledger**. Use MCP **`update_challenge_state`** **only** after explicit user approval for each proposed transition.

Lifecycle vocabulary and transition hints: **`docs/ai/references/challenge-lifecycle-model.md`**  
Canonical states / diagram: **`docs/project_spec.md` §7.4**  
MCP implementation: **`prestonotes_mcp/journey.py`**, **`update_challenge_state`** in **`prestonotes_mcp/server.py`**

---

## Communication rule

Tell the user what you are doing in plain English. Prefix each major step: **`Step X of 8 — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`** for tone.

---

## Preconditions

1. **`[CustomerName]`** matches **`MyNotes/Customers/[CustomerName]/`** (optional **`sync_notes`** MCP or **`scripts/rsync-gdrive-notes.sh`** if the mirror may be stale).
2. **`challenge-lifecycle.json`** may be missing or partial — still run the flow by **unioning** challenge ids from **call records** (`**`challenges_mentioned[].id`**`) with ids present in the JSON file.
3. **Stall signal (default):** Treat **no lifecycle or call-record movement** on a challenge for **≥ 60 days** as a **stall risk**, aligned with **`challenge-lifecycle-model.md`** (diagram: **60+ days** without movement). Use **calendar days** between **today** (session date) and the **latest relevant date** for that challenge (see Step 4). If **`current_state`** is already **`stalled`**, surface **days since last transition** in **recommended action** instead of double-counting.

---

## Step 1 of 8 — Optional sync

Run **`sync_notes`** with **`[CustomerName]`** (or full repo rsync) so local **`MyNotes/`** matches Drive when the user expects fresh data.

**Tell user:** `Step 1 of 8 — Sync complete (or skipped).`

---

## Step 2 of 8 — Read `challenge-lifecycle.json`

Read **`MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json`** from the workspace.

- If the file is **missing** or **empty object**, note “no persisted lifecycle yet” and rely on **call records** for ids and narrative (**Step 3**).
- For each challenge id in the JSON: capture **`current_state`** and the append-only **`history[]`** (`**`state`**, **`at`** (YYYY-MM-DD), **`evidence`**`).

**Tell user:** `Step 2 of 8 — Loaded lifecycle for N challenge id(s) [or none].`

---

## Step 3 of 8 — Load call records (and optional ledger)

1. MCP **`read_transcript_index([CustomerName])`** — optional coverage context (**`total_calls`**, dates).
2. MCP **`read_call_records([CustomerName])`** — use **`challenges_mentioned[]`** (`**`id`**, **`description`**, **`status`**`) and **`call_id`** / **`date`** for **last mention** and **verbatim evidence** pointers.
3. Optionally MCP **`read_ledger([CustomerName])`** — v2 **challenge** columns / themes if present.

Keep payloads within context limits; for large corpora, process **chronologically** in windows and **merge** challenge ids **without dropping** aliases (canonicalize per **`challenge-lifecycle-model.md`**).

**Tell user:** `Step 3 of 8 — Indexed calls + M call record(s) [+ ledger optional].`

---

## Step 4 of 8 — Merge challenge universe and dates

Build the **union** of:

- All ids from **`challenge-lifecycle.json`**, and  
- All **`challenges_mentioned[].id`** values from call records (including **call-only** ids not yet in JSON).

For each **canonical** challenge id, compute:

| Field | Rule |
|-------|------|
| **Last updated (date)** | Latest of: (a) last **`history[].at`** for that id in **`challenge-lifecycle.json`**, (b) latest **`date`** among call records where that **`id`** appears in **`challenges_mentioned`**. If neither exists, leave blank and flag in **notes**. |
| **Evidence** | Short string: prefer **last `history[-1].evidence`**, else **“`call_id` (YYYY-MM-DD): …”** from the latest call mentioning the id; max **one** quote only if it fits. |
| **Current state** | From JSON **`current_state`** if present; else **infer read-only** from latest **`challenges_mentioned[].status`** and narrative (**§7.4** vocabulary only) and mark cell **“inferred (not persisted)”**. |

**Tell user:** `Step 4 of 8 — Unified C challenge row(s) [including K call-only id(s) if any].`

---

## Step 5 of 8 — Stall and drift checks

For each row:

1. **Days since last updated** — from Step 4 vs session date.
2. **Stall flag** — if **`current_state`** is **`in_progress`**, **`acknowledged`**, or **`identified`** and days **≥ 60**, set stall flag **yes** and phrase like **“no movement 65d”** (use actual day count).
3. **Drift** — if persisted **`current_state`** disagrees materially with the latest call narrative, note **“drift: lifecycle vs calls”** (do **not** auto-write).

**Tell user:** `Step 5 of 8 — Stall/drift pass complete; S stall signal(s) [or none].`

---

## Step 6 of 8 — Build the review table (primary output)

Present one markdown **table** (all challenges, including **resolved** unless the user asked to hide them):

| Column | Content |
|--------|---------|
| **`challenge_id`** | Canonical id (**`ch-…`**). |
| **`description`** | Latest short label from calls or JSON context. |
| **`current_state`** | **`identified`** \| **`acknowledged`** \| **`in_progress`** \| **`resolved`** \| **`reopened`** \| **`stalled`** (or inferred + tag). |
| **`last_updated`** | **`YYYY-MM-DD`** from Step 4. |
| **`evidence`** | Compact pointer from Step 4. |
| **`stall / risk`** | e.g. **“—”**, **“stalled 65d”**, **“at risk (drift)”**. |
| **`recommended_action`** | One imperative line, e.g. **“Schedule customer checkpoint — in_progress, no touch 62d”**, **“Confirm resolution — evidence in `2026-03-01-workshop`”**, **“Pick canonical id — alias of ch-002”**. |

**Manual QA (spec §9 TASK-014):** On a customer with **≥ 3 challenges**, verify **all rows appear**, **stall flags** match dates, and **≥ one** **`recommended_action`** is clearly sensible.

**Tell user:** `Step 6 of 8 — Review table ready (C rows).`

---

## Step 7 of 8 — Approval gate for lifecycle writes (mandatory)

If (and **only** if) you propose **persisted** state changes, present a **second compact table** of MCP rows:

| `challenge_id` | `new_state` | `evidence` (must cite **`call_id`** or lifecycle rule) |

**Say:** “I will call **`update_challenge_state(customer_name, challenge_id, new_state, evidence)`** once per **approved** row. Approve **all**, **none**, or specify which **`challenge_id`**s to update.”

**STOP** until the user approves. Do **not** call **`update_challenge_state`** before approval. Illegal transitions raise errors in **`append_challenge_transition`** — only propose **valid** single-step moves per **`prestonotes_mcp/journey.py`** / **§7.4**.

**Tell user:** `Step 7 of 8 — Awaiting approval for P proposed transition(s) [or none — skip writes].`

---

## Step 8 of 8 — Apply approved updates and hand off

For each approved row, invoke MCP **`update_challenge_state`** with the four parameters (string evidence as written in the approval table).

Then summarize: which ids were updated, which were skipped, and whether **`Run Journey Timeline for [CustomerName]`** should be rerun for narrative alignment.

**Tell user:** `Step 8 of 8 — Challenge review complete for [CustomerName].`

---

## MCP tools used

| Tool | Role |
|------|------|
| **`sync_notes`** | Optional refresh of **`MyNotes/`** |
| **`read_transcript_index`** | Call coverage / date span |
| **`read_call_records`** | **`challenges_mentioned`**, dates, evidence |
| **`read_ledger`** | Optional commercial / challenge context (v2 ledger) |
| **`update_challenge_state`** | **After approval only** — append transition to **`challenge-lifecycle.json`** |

**Workspace read (no MCP read tool for this file):** **`MyNotes/Customers/[CustomerName]/AI_Insights/challenge-lifecycle.json`**

---

## References

- **`docs/project_spec.md` §7.1**, **§7.4**, **§9 TASK-014**, **§11** (trigger row)  
- **`docs/ai/references/challenge-lifecycle-model.md`**  
- **`prestonotes_mcp/journey.py`** — lifecycle path, allowed transitions  
- **`prestonotes_mcp/tests/test_journey_tools.py`** — **`update_challenge_state`** examples
