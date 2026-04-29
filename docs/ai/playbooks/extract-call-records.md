# Playbook: Extract Call Records

Trigger: **`Extract Call Records for [CustomerName]`**

Purpose: Read **per-call** transcript text under **`MyNotes/Customers/[CustomerName]/Transcripts/`**, produce **`project_spec.md` §7.1** JSON for each meeting, and persist via MCP **`write_call_record`**.

**Status (operator expectation):** **Update Customer Notes** and **Run Account Summary** are **transcript-first** today — they do **not** require `call-records/*.json` or MCP **`read_call_records`**. Use this playbook only when you **choose** to maintain §7.1 JSON on disk (experiments, linting, or downstream tools).

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

Supporting rule: **`.cursor/rules/21-extractor.mdc`**  
Taxonomy: **`docs/ai/references/call-type-taxonomy.md`**

---

## Communication rule

Tell the user what you are doing in plain English. Prefix each major step: **`Step X of Y — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`** for tone.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`**.
- After multi-step work, include **`### Activity recap`** with records written and files skipped.
- State approval/write outcome explicitly.

---

## Preconditions

1. **`[CustomerName]`** matches an existing folder **`MyNotes/Customers/[CustomerName]/`** (sync with **`sync_notes`** MCP or **`scripts/rsync-gdrive-notes.sh`** if needed).
2. Prefer **per-call** **`Transcripts/*.txt`** from Granola (`YYYY-MM-DD-*.txt`). If **only** **`_MASTER_TRANSCRIPT_*.txt`** files exist, **stop** after Step 2 and tell the user: run **`scripts/granola-sync.py`** (or their export path) to emit per-call files — **do not** ingest an entire master into the model context. **Exception:** if the user explicitly authorizes **one** transcript file and a **max character budget** (e.g. 24k chars), you may process that single bounded slice for extraction.

---

## Step 1 of 9 — Optional sync (canonical Drive and repo ordering)

**This step applies to every Extract run** (single customer, full E2E, or ad hoc). The goal is a **safe** order so you do not lose work on disk.

1. **Pull first (default)** when you want the repo mirror to match what is already on **Google Drive** (e.g. another machine updated Notes, or you edited on Drive): run **`sync_notes`** with **`[CustomerName]`** *or* **`./scripts/rsync-gdrive-notes.sh [CustomerName]`** so local **`MyNotes/Customers/[CustomerName]/`** is up to date before you read transcripts and write new **`call-records/*.json`**.

2. **After** you have **new or updated** local files under that customer folder—especially new **`call-records/*.json`** that do not exist on Drive yet—**push to Drive before the next pull**:  
   **`./scripts/e2e-test-push-gdrive-notes.sh [CustomerName]`**  
   (Despite the name, this is the **scoped** repo → Drive push for **any** customer, not only E2E; see `scripts/README.md`.)  
   **Why:** `rsync-gdrive-notes.sh` **pulls** with **`--delete`** on the receiver; files present only in the repo copy can be **deleted** on pull if the Drive sender does not have them yet. **Push-first** matches **TASK-052** / `e2e-test-customer` **`prep-v2`** ordering when you need round-trip integrity.

3. If you need both (edit locally *and* pick up remote changes), order is typically: **pull → extract → write call records → push**—never **pull** in between local-only JSON work without an intervening **push** if you need to keep that JSON.

E2E troubleshooting and other playbooks should **link here** instead of duplicating this block.

**Tell user:** `Step 1 of 9 — Sync complete (or skipped).`

---

## Step 2 of 9 — Discover transcript files

1. List **`MyNotes/Customers/[CustomerName]/Transcripts/`**.
2. Separate **`YYYY-MM-DD-*.txt`** (per-call) vs **`_MASTER_*.txt`** (legacy bundles).
3. If no per-call `.txt`, apply **Preconditions** / master policy and **stop** if unresolved.

**Tell user:** `Step 2 of 9 — Found N per-call transcript file(s).`

---

## Step 3 of 9 — Load prior records

1. MCP **`read_call_records`** with **`since_date`** unset (or set to a lower bound) to learn **`call_number_in_sequence`** and content for **deltas**. `read_call_records` returns records sorted by `(date, call_id)`.

**`call_number_in_sequence` algorithm**

- Use the sorted output of **`read_call_records`**.
- Let **`M`** = max **`call_number_in_sequence`** in that list, or **0** if none.
- For each **new** meeting you add in this run, assign **`call_number_in_sequence = M + 1`**, **`M + 2`**, … in chronological order of the **new** meetings being extracted.

**Tell user:** `Step 3 of 9 — Prior records loaded; next sequence starts at [M+1].`

---

## Step 4 of 9 — Select files to process

- **Default:** All per-call **`.txt`** that do **not** yet have a **`call-records/*.json`** whose **`raw_transcript_ref`** equals that basename (compare basenames to the set returned by **`read_call_records`**).
- **User override:** If the user names specific files or a date range, restrict to that set.

**Tell user:** `Step 4 of 9 — Will process [list or count] transcript(s).`

---

## Step 5 of 9 — Read transcript content (bounded)

For each selected file:

1. Read file contents up to a **reasonable** limit (keep under context limits; if huge, read head + tail and set **`extraction_confidence`** to **`medium`** or **`low`** and say so).
2. Parse **meeting metadata** when present (e.g. Granola-style `MEETING:` / `DATE:` / `ID:` headers).

**Tell user:** `Step 5 of 9 — Read [N] transcript(s).`

---

## Step 6 of 9 — Build §7.1 JSON (draft — schema v2 field-by-field checklist)

For each meeting, build one JSON object that **varies per call** and is grounded in transcript evidence. The canonical schema lives in **`prestonotes_mcp/call_records.py`** (`CALL_RECORD_SCHEMA`); the spec example is in **`docs/project_spec.md` §7.1**. MCP **`write_call_record`** will reject every violation listed below — extract real values or downgrade **`extraction_confidence`**.

### Banned defaults (hard reject)

- **No `ch-stub`**, **no `Fixture narrative`**, **no `E2E fixture`** — these are the stub fingerprints from the TASK-051 regression and will bounce at write time (`prestonotes_mcp/call_records.py` → `BANNED_CALL_RECORD_DEFAULTS`).
- **No hardcoded `products_discussed`.** The DSPM/PII call gets **`Wiz DSPM`** / **`Wiz CIEM`**; the shift-left call gets **`Wiz Code`** and/or **`Wiz CLI`**; the runtime hardening call gets **`Wiz Sensor`**. Do not stamp `["Wiz Cloud", "Wiz Sensor"]` on every record.
- **No identical `sentiment` across materially different calls.** Exec readout or QBR where budget freeze / champion exit dominate must be at least **`cautious`** — not **`positive`**.

### Sales discovery anchor (MEDDPICC)

Before you commit field-by-field, run a light **MEDDPICC / MEDDIC** pass across the transcript (**M**etrics, **E**conomic buyer, **D**ecision criteria, **D**ecision process, **I**dentify pain, **C**hampion, **C**ompetition, **P**aper process). Each hit gets its own schema v2 field:

- **Metrics** → `metrics_cited[]` entries (`metric`, `value`, optional `context`). Examples: Wiz Score 92%, 900/1000 workloads scanned, 10k CVSS → 12 toxic combos.
- **Economic buyer / Champion / Decision makers** → `stakeholder_signals[]` entries (`name`, optional `role`, `signal`: `sponsor_engaged` / `champion_exit` / `new_contact` / `decision_maker` / `detractor`).
- **Goals** → `goals_mentioned[]` entries (`description`, optional `category`: `adoption` / `commercial` / `operational` / `security_posture` / `stakeholder`).
- **Pain / risk / blockers** → `risks_mentioned[]` entries (`description`, `severity`: `low` / `med` / `high`, optional `evidence_quote`).

Output from this anchor goes to the v2 fields **only** — do **not** rewrite `summary_one_liner` (that field's format is frozen and indexed downstream).

### Field-by-field checklist

| Key | Rule (schema v2) | `_TEST_CUSTOMER` fixture example |
|-----|------------------|----------------------------------|
| **`call_id`** | Filesystem-safe; must match the write argument and `record_json.call_id` exactly. | `2026-04-08-technical_deep_dive-4` |
| **`date`** | `YYYY-MM-DD` from transcript `DATE:` header or filename. | `2026-04-08` (DSPM/PII call) |
| **`call_type`** | Enum per `call-type-taxonomy.md`: `discovery`, `technical_deep_dive`, `campaign`, `exec_qbr`, `poc_readout`, `renewal`, `internal`. | DSPM/PII → `technical_deep_dive`; exec readout → `exec_qbr` |
| **`call_number_in_sequence`** | From Step 3 algorithm (`M + 1`, `M + 2`, …). | `4` |
| **`duration_minutes`** | Integer if stated; else `0`. | `30` |
| **`participants[]`** | Only people who actually appear in the transcript (name, optional `role` / `company` / `is_new`). Every `verbatim_quotes[].speaker` MUST match a `participants[].name`. | `[{name: "John Doe", role: "Exec Sponsor"}, {name: "Jane Smith", role: "Platform Lead"}, {name: "SE"}]` |
| **`summary_one_liner`** | One sentence; **format frozen** — do NOT move MEDDPICC signals here. | `"Post-acquisition DSPM guardrails review; AcmeCorp PII bucket caught and remediated."` |
| **`key_topics[]`** | `minItems: 1`, each item `minLength: 3`; **unique per call**. Never `["E2E fixture"]`. | `["AcmeCorp acquisition onboarding", "DSPM PII bucket finding", "Okta tenant consolidation"]` |
| **`challenges_mentioned[]`** | `id` matches `^ch-[a-z0-9][a-z0-9-]{1,40}$` (kebab); `description` `minLength: 10`; `status` uses §7.4 vocabulary. Never `ch-stub` / `"Fixture narrative"`. | `[{id: "ch-splunk-budget-freeze", description: "SOC budget frozen for Q1 blocks Splunk connector purchase.", status: "stalled"}, {id: "ch-champion-exit", description: "Jane Smith leaving next week; transition plan needed.", status: "in_progress"}]` |
| **`products_discussed[]`** | Enum: `Wiz Cloud \| Wiz Sensor \| Wiz Defend \| Wiz DSPM \| Wiz CIEM \| Wiz Code \| Wiz CLI \| Wiz Sensor POV`, or `Other: <name>` for non-Wiz products. **Call-specific** — not a constant. | DSPM/PII → `["Wiz DSPM", "Wiz CIEM"]`; shift-left → `["Wiz Code", "Wiz CLI"]`; runtime hardening → `["Wiz Sensor"]`; procurement readout → `["Wiz Cloud", "Other: Splunk"]` |
| **`action_items[]`** | Each `owner` `minLength: 1`; prefer a named individual when the transcript names one. Generic `"SE"` only when the transcript actually says `SE:` and no person is attached. | `[{owner: "Jane Smith", action: "Capture top 5 misconfigurations before handoff", due: "2026-04-15"}]` |
| **`sentiment`** | Enum `positive \| neutral \| cautious \| negative`. Exec readout / QBR with budget freeze + champion exit ⇒ `cautious` at minimum. | Exec readout → `cautious`; DSPM/PII → `positive`; procurement readout → `neutral` |
| **`deltas_from_prior_call[]`** | **Read the prior 3 per-call transcripts** (newest other meetings under `Transcripts/`, excluding the current file) before drafting this one. Populate when real state changed (Splunk: `in_progress → stalled`, Cloud: `pursue → purchased`, Sensor: `evaluate → POV`). `[]` only when there is genuinely no change. | `[{field: "ch-splunk-budget-freeze.status", from: "in_progress", to: "stalled"}]` |
| **`verbatim_quotes[]`** | `maxItems: 3`; each `quote` `maxLength: 280`, **whitespace-normalized substring** of the referenced transcript; `speaker` MUST be in `participants[].name`. MCP rejects otherwise. | `[{speaker: "Jane Smith", quote: "We actually caught an unencrypted S3 bucket full of PII exposed via an overprivileged IAM role."}]` |
| **`raw_transcript_ref`** | **Basename** of the `.txt` source under `Transcripts/`. Must exist on disk or write is rejected. | `"2026-04-08-dspm-pii-guardrails.txt"` |
| **`extraction_date`** | Today `YYYY-MM-DD` (session date). | `2026-04-20` |
| **`extraction_confidence`** | Enum `high \| medium \| low`. **Auto-downgrade:** if ≥ 3 of `{goals_mentioned, risks_mentioned, metrics_cited, stakeholder_signals, deltas_from_prior_call}` are empty, the writer downgrades `high → medium`; ≥ 5 empty forces `low`. Accept the downgrade — don't fabricate richness to preserve a `high`. | `high` for a multi-signal QBR; `medium` for a single-topic hardening sync; `low` for a scrappy procurement readout |
| **`goals_mentioned[]`** *(v2)* | Optional; each entry `{description, evidence_quote?, category?}`. Aggregated by Account Summary's **Goals** / **Upsell Path**. | `[{description: "Sensor coverage ≥ 95% across prod Azure", category: "adoption"}]` |
| **`risks_mentioned[]`** *(v2)* | Optional; each entry `{description, severity: low\|med\|high, evidence_quote?}`. Feeds Account Summary **Risk**. | `[{description: "SOC budget freeze blocks Splunk connector", severity: "med"}]` |
| **`metrics_cited[]`** *(v2)* | Optional; each entry `{metric, value, context?}`. Replaces "ledger re-derivation from transcripts" downstream. | `[{metric: "Wiz Score", value: "92%"}, {metric: "workloads scanned", value: "900/1000"}]` |
| **`stakeholder_signals[]`** *(v2)* | Optional; each entry `{name, role?, signal: sponsor_engaged\|champion_exit\|new_contact\|decision_maker\|detractor, note?}`. Captures people-movement without inflating `participants`. | `[{name: "John Doe", role: "Exec Sponsor", signal: "sponsor_engaged"}, {name: "Jane Smith", signal: "champion_exit", note: "leaving next week"}]` |

### Size and anti-regression

- Each record must serialize ≤ 2.5 KB (`CALL_RECORD_MAX_BYTES = 2560`); `write_call_record` rejects anything larger. Target corpus average ≤ 1.5 KB (the lint CLI flags above that).
- `write_call_record` refuses to overwrite an existing `high`-confidence record with one that has strictly fewer populated signal fields. Re-extract properly rather than thin an earlier good record.

**Tell user:** `Step 6 of 9 — Drafted [N] call record(s). Here are one-liners: [bullets].`

---

## Step 7 of 9 — Approval gate (mandatory)

Present a **compact table**: `call_id`, `date`, `call_type`, `raw_transcript_ref`, `extraction_confidence`.

**Say:** “I will call **`write_call_record`** once per row. Approve **all**, **none**, or specify which **`call_id`**s to write.”

**STOP** until the user approves. Do not call **`write_call_record`** before approval.

---

## Step 8 of 9 — Write records

For each approved record:

1. MCP **`write_call_record(customer_name, call_id, record_json)`** where **`record_json`** is **stringified JSON** and **`call_id`** matches **`record.call_id`**.

Then:

2. MCP **`read_call_records`** to confirm the new records validated and counts match expectations.

**Tell user:** `Step 8 of 9 — Wrote [N] record(s); read_call_records shows [count] total.`

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
| **`read_call_records`** | Prior records + deltas + basename coverage |
| **`write_call_record`** | Persist each §7.1 JSON (after approval) |

Terminal-only alternative: none required for extraction itself; paths are under **`MyNotes/`** in the repo.

---

## References

- **`docs/project_spec.md`** §7.1–§7.4  
- **`prestonotes_mcp/call_records.py`** — schema and file I/O  
- **`prestonotes_mcp/tests/test_call_record_tools.py`** — minimal valid record shape  
