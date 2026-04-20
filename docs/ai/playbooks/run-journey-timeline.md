# Playbook: Run Journey Timeline

Trigger: **`Run Journey Timeline for [CustomerName]`**

Purpose: Read **`transcript-index.json`** and **§7.1 call record JSON** for the customer, synthesize the **account story** (spec §9 TASK-012 steps 1–9), assign **health** per **`docs/ai/references/health-score-model.md`**, and persist the markdown artifact with MCP **`write_journey_timeline`**. Optionally reconcile challenge lifecycle with MCP **`update_challenge_state`** when corrections are justified.

Supporting rule: **`.cursor/rules/22-journey-synthesizer.mdc`**  
Challenge model: **`docs/ai/references/challenge-lifecycle-model.md`**  
Health rubric: **`docs/ai/references/health-score-model.md`**

---

## Communication rule

Tell the user what you are doing in plain English. Prefix each major step: **`Step X of 9 — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`** for tone.

---

## Preconditions

1. **`[CustomerName]`** exists under **`MyNotes/Customers/[CustomerName]/`** (use **`sync_notes`** if the mirror may be stale).
2. **Call records** should exist for meaningful synthesis. If **`read_transcript_index`** shows **`total_calls` < 2**, still run the flow but set health **⚪ Unknown** per **`health-score-model.md`** and say so explicitly.
3. Keep **`read_call_records`** / index payloads within context limits; if the corpus is huge, process **chronologically** in windows and merge summaries **without losing challenge ids**.

---

## Step 1 of 9 — Load index and all call records

1. MCP **`read_transcript_index([CustomerName])`**. If missing, report it and use **`read_call_records`** alone; note coverage gaps.
2. MCP **`read_call_records([CustomerName])`** with filters **unset** unless the user supplied a **date range** or **call_type** scope.
3. Optionally MCP **`read_ledger([CustomerName])`** for ledger-stated themes (commercial rows, challenge columns in v2 ledgers).

**Maps to spec TASK-012 step 1:** *Read all call records from `transcript-index.json`* — in practice: **index + records** (index lists calls and paths; records hold §7.1 bodies).

**Tell user:** `Step 1 of 9 — Loaded index and N call record(s) [+ ledger optional].`

---

## Step 2 of 9 — Chronological timeline of all calls

Sort by **`date`**, then **`call_id`** / sequence. Build an internal ordered list of every call with: **`call_id`**, **`date`**, **`call_type`**, **`summary_one_liner`**, **`sentiment`**, top **`key_topics`**.

**Tell user:** `Step 2 of 9 — Chronological spine has N call(s) from [first date] to [last date].`

---

## Step 3 of 9 — Milestone events

From the spine, label milestones where evidence supports them, for example:

- First substantive customer call (usually first **`discovery`** or earliest dated call).
- First clear “win” or positive inflection (pilot agreed, security outcomes, executive sponsorship).
- POC / technical deep dive start, POC readout, renewal or commercial thread (use **`call_type`** + content).

Each milestone bullet must cite **`call_id`** (and optional one-liner). Do not invent dates.

**Tell user:** `Step 3 of 9 — Identified M milestone(s) with citations.`

---

## Step 4 of 9 — Trace each challenge to current state

For each distinct **`challenges_mentioned[].id`** (canonicalize aliases per **`challenge-lifecycle-model.md`**):

- Track **`description`** drift across calls (latest wording wins in the narrative; earlier variants footnoted if useful).
- Track **`status`** over time; compare against **`AI_Insights/challenge-lifecycle.json`** if you read it from disk via prior tooling — **MCP does not expose a read tool** for that file in **`server.py`**, so infer from **call records** unless the user pastes JSON or authorizes a file read from the workspace.
- Apply **§7.4** vocabulary only.

Prepare a **Challenge trace table** (markdown): columns **`id`**, **`current_best_state`**, **`last_evidence_call_id`**, **`notes`**.

**Tell user:** `Step 4 of 9 — Traced C challenge(s); K need lifecycle correction [or none].`

---

## Step 5 of 9 — Stakeholder evolution map

Union **`participants`** across calls. For each person: first seen, last seen, **role** changes, **`is_new`** hints, champion-like behavior (executive sponsor, internal Wiz ally) **only if supported by quotes or clear statements**.

**Tell user:** `Step 5 of 9 — Stakeholder map has P people with evidence anchors.`

---

## Step 6 of 9 — Value realized

Compile concrete **outcomes** from **`summary_one_liner`**, **`key_topics`**, **`action_items`** completions, POC language, and **`verbatim_quotes`** (max depth as needed). Each value bullet: **what**, **when (`call_id` / date)**, **evidence tag** when appropriate (§7.5).

**Tell user:** `Step 6 of 9 — Value section has V evidence-backed item(s) [or explicitly none found].`

---

## Step 7 of 9 — VP story arc (opening narrative)

Write **2–3 sentences** only: who they are, what problem matters, where they are in the journey, what happens next — **plain English**, no product jargon. This is the **`TASK-012` step 7** “story arc” opener (distinct from the longer **TASK-013** exec template).

**Tell user:** `Step 7 of 9 — Drafted VP opening (2–3 sentences).`

---

## Step 8 of 9 — Assemble Journey Timeline markdown

Produce one markdown document (UTF-8) suitable for **`write_journey_timeline`**, with **at least** these sections:

1. **Title** — `# <Customer> — Journey Timeline`
2. **Metadata** — Generated date (session), sources (`read_transcript_index`, `read_call_records`, optional `read_ledger`).
3. **Health** — Single line **`Health: 🟢|🟡|🔴|⚪ …`** using **only** the definitions in **`health-score-model.md`** (verbatim band rules from spec).
4. **The 30-Second VP Brief** — paste the Step 7 prose here (can be labeled as VP brief).
5. **Chronological call spine** — compact table: `Date | call_id | call_type | summary_one_liner | sentiment`
6. **Milestones** — bullets from Step 3.
7. **Challenge journey** — narrative + Step 4 table.
8. **Stakeholder evolution** — bullets or small table.
9. **Value realized** — bullets from Step 6.
10. **Strategic position & next moves** — short, grounded in last calls (no fiction).
11. **Optional appendix** — ids of transcripts referenced if you used **`read_transcripts`** for quotes.

Keep under configured max bytes; trim appendix first if needed.

**Tell user:** `Step 8 of 9 — Journey Timeline markdown assembled (~X chars).`

---

## Step 9 of 9 — Approval gates and MCP writes

### Gate A — Challenge lifecycle corrections (optional)

If Step 4 found corrections, present a **compact table**: `challenge_id`, `new_state`, `evidence` (must include **`call_id`** or short quote / date).

**Say:** “I will call **`update_challenge_state`** once per approved row. Approve **all**, **none**, or specify which **`challenge_id`**s to update.”

**STOP** until the user approves. Do not call **`update_challenge_state`** before approval.

### Gate B — Journey timeline (mandatory if persisting)

Show the **Health** line and a **two-section preview** (VP brief + call spine header + first 2 rows). Then the full body in a collapsible or truncated view is acceptable if huge — but the approving user must see **enough** to validate claims.

**Say:** “I will call **`write_journey_timeline(customer_name, content)`** with the assembled markdown. **Approve / reject / request edits.**”

**STOP** until the user approves. Do not call **`write_journey_timeline`** before approval.

### Execute

1. For each approved challenge transition: MCP **`update_challenge_state(customer_name, challenge_id, new_state, evidence)`**.
2. On timeline approval: MCP **`write_journey_timeline([CustomerName], content)`** with the final markdown string.

**Tell user:** `Step 9 of 9 — Run Journey Timeline complete for [CustomerName].`

---

## MCP tools used

| Tool | Role |
|------|------|
| **`read_transcript_index`** | Call list, coverage, pointers to record files |
| **`read_call_records`** | §7.1 JSON corpus for synthesis |
| **`read_ledger`** | Optional account history / v2 challenge columns |
| **`write_journey_timeline`** | Persist **`AI_Insights/<Customer>-Journey-Timeline.md`** (after approval) |
| **`update_challenge_state`** | Append lifecycle transitions (after approval) |
| **`sync_notes`** | Optional refresh of **`MyNotes/`** |

---

## References

- **`docs/project_spec.md`** §6 Stage 2 diagram, §7.1, §7.4, §9 TASK-012  
- **`prestonotes_mcp/tests/test_journey_tools.py`** — expected filesystem targets for journey outputs
