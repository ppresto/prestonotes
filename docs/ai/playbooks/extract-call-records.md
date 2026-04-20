# Playbook: Extract Call Records

Trigger: **`Extract Call Records for [CustomerName]`**

Purpose: Read **per-call** transcript text under **`MyNotes/Customers/[CustomerName]/Transcripts/`**, produce **`project_spec.md` §7.1** JSON for each meeting, and persist via MCP **`write_call_record`**, then rebuild **`transcript-index.json`** with **`update_transcript_index`**.

Supporting rule: **`.cursor/rules/21-extractor.mdc`**  
Taxonomy: **`docs/ai/references/call-type-taxonomy.md`**

---

## Communication rule

Tell the user what you are doing in plain English. Prefix each major step: **`Step X of Y — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`** for tone.

---

## Preconditions

1. **`[CustomerName]`** matches an existing folder **`MyNotes/Customers/[CustomerName]/`** (sync with **`sync_notes`** MCP or **`scripts/rsync-gdrive-notes.sh`** if needed).
2. Prefer **per-call** **`Transcripts/*.txt`** from Granola (`YYYY-MM-DD-*.txt`). If **only** **`_MASTER_TRANSCRIPT_*.txt`** files exist, **stop** after Step 2 and tell the user: run **`scripts/granola-sync.py`** (or their export path) to emit per-call files — **do not** ingest an entire master into the model context. **Exception:** if the user explicitly authorizes **one** transcript file and a **max character budget** (e.g. 24k chars), you may process that single bounded slice for extraction.

---

## Step 1 of 9 — Optional sync

Run **`sync_notes`** with **`[CustomerName]`** (or full repo rsync) so local **`MyNotes/`** matches Drive.

**Tell user:** `Step 1 of 9 — Sync complete (or skipped).`

---

## Step 2 of 9 — Discover transcript files

1. List **`MyNotes/Customers/[CustomerName]/Transcripts/`**.
2. Separate **`YYYY-MM-DD-*.txt`** (per-call) vs **`_MASTER_*.txt`** (legacy bundles).
3. If no per-call `.txt`, apply **Preconditions** / master policy and **stop** if unresolved.

**Tell user:** `Step 2 of 9 — Found N per-call transcript file(s).`

---

## Step 3 of 9 — Load index and prior records

1. MCP **`read_transcript_index`** for **`[CustomerName]`**. If missing or error, note “no index yet.”
2. MCP **`read_call_records`** with **`since_date`** unset (or set to a lower bound) to learn **`call_number_in_sequence`** and content for **deltas**.

**`call_number_in_sequence` algorithm**

- Sort existing records by **`date`**, then **`call_id`**.
- Let **`M`** = max **`call_number_in_sequence`** in that list, or **0** if none.
- For each **new** meeting you add in this run, assign **`call_number_in_sequence = M + 1`**, **`M + 2`**, … in chronological order of the **new** meetings being extracted.

**Tell user:** `Step 3 of 9 — Prior index/records loaded; next sequence starts at [M+1].`

---

## Step 4 of 9 — Select files to process

- **Default:** All per-call **`.txt`** that do **not** yet have a **`call-records/*.json`** whose **`raw_transcript_ref`** equals that basename (compare basenames to index + **`read_call_records`**).
- **User override:** If the user names specific files or a date range, restrict to that set.

**Tell user:** `Step 4 of 9 — Will process [list or count] transcript(s).`

---

## Step 5 of 9 — Read transcript content (bounded)

For each selected file:

1. Read file contents up to a **reasonable** limit (keep under context limits; if huge, read head + tail and set **`extraction_confidence`** to **`medium`** or **`low`** and say so).
2. Parse **meeting metadata** when present (e.g. Granola-style `MEETING:` / `DATE:` / `ID:` headers).

**Tell user:** `Step 5 of 9 — Read [N] transcript(s).`

---

## Step 6 of 9 — Build §7.1 JSON (draft)

For each meeting, build one JSON object with **all required keys** (see **`prestonotes_mcp/call_records.py`** / spec §7.1):

| Key | Notes |
|-----|--------|
| **`call_id`** | New unique id, e.g. **`2026-04-15-campaign-2`** — must be filesystem-safe and match the file you will write |
| **`date`** | **`YYYY-MM-DD`** from transcript metadata or filename |
| **`call_type`** | Per **`call-type-taxonomy.md`** |
| **`call_number_in_sequence`** | From Step 3 algorithm |
| **`duration_minutes`** | Integer if known; else **`0`** |
| **`participants`** | Array of objects (see test fixture shape) |
| **`summary_one_liner`** | One sentence |
| **`key_topics`** | Array of short strings |
| **`challenges_mentioned`** | Array with **`id`**, **`description`**, **`status`** |
| **`products_discussed`** | e.g. `["Wiz Cloud", "Wiz Sensor"]` |
| **`action_items`** | Array of **`owner`**, **`action`**, **`due`** (use empty string if unknown) |
| **`sentiment`** | **`positive`** \| **`neutral`** \| **`cautious`** \| **`negative`** |
| **`deltas_from_prior_call`** | Array (empty if first call) |
| **`verbatim_quotes`** | Max 3; **`speaker`**, **`quote`** substring of transcript |
| **`raw_transcript_ref`** | **Basename** of the `.txt` source |
| **`extraction_date`** | Today **`YYYY-MM-DD`** (session date) |
| **`extraction_confidence`** | **`high`** \| **`medium`** \| **`low`** |

**Tell user:** `Step 6 of 9 — Drafted [N] call record(s). Here are one-liners: [bullets].`

---

## Step 7 of 9 — Approval gate (mandatory)

Present a **compact table**: `call_id`, `date`, `call_type`, `raw_transcript_ref`, `extraction_confidence`.

**Say:** “I will call **`write_call_record`** once per row, then **`update_transcript_index`**. Approve **all**, **none**, or specify which **`call_id`**s to write.”

**STOP** until the user approves. Do not call **`write_call_record`** before approval.

---

## Step 8 of 9 — Write records and rebuild index

For each approved record:

1. MCP **`write_call_record(customer_name, call_id, record_json)`** where **`record_json`** is **stringified JSON** and **`call_id`** matches **`record.call_id`**.

Then:

2. MCP **`update_transcript_index([CustomerName])`** **once**.

3. MCP **`read_transcript_index`** (and optionally **`read_call_records`**) to confirm counts.

**Tell user:** `Step 8 of 9 — Wrote [N] record(s); index shows [total_calls] calls.`

---

## Step 9 of 9 — Handoff

- If any file was skipped, list why (schema risk, user rejection, master-only policy).
- Remind: **`Test Call Record Extraction for [CustomerName]`** (**TASK-009** playbook) is the coverage QA pass.

**Tell user:** `Step 9 of 9 — Extract Call Records complete for [CustomerName].`

---

## MCP tools used

| Tool | Role |
|------|------|
| **`sync_notes`** | Optional pull from Drive |
| **`read_transcript_index`** | Prior index |
| **`read_call_records`** | Prior records + deltas + basename coverage |
| **`write_call_record`** | Persist each §7.1 JSON (after approval) |
| **`update_transcript_index`** | Rebuild **`transcript-index.json`** |

Terminal-only alternative: none required for extraction itself; paths are under **`MyNotes/`** in the repo.

---

## References

- **`docs/project_spec.md`** §7.1–§7.4  
- **`prestonotes_mcp/call_records.py`** — schema and index rebuild  
- **`prestonotes_mcp/tests/test_call_record_tools.py`** — minimal valid record shape  
