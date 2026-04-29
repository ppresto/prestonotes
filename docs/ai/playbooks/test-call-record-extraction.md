# Playbook: Test Call Record Extraction

Trigger:

- **`Test Call Record Extraction for [CustomerName]`**
- **`Validate Call Record Extraction for [CustomerName]`** (alias)

Purpose: **Manual QA** after (or alongside) **`Extract Call Records for [CustomerName]`**. Compares **per-call transcript files** to **`call-records/*.json`**, emits the **Stage 1 gate** coverage line, and guides human spot-checks.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

**Upstream:** [`extract-call-records.md`](extract-call-records.md) (TASK-008) · **`.cursor/rules/21-extractor.mdc`** · **`docs/ai/references/call-type-taxonomy.md`** · **`docs/project_spec.md`** §7.1

---

## Communication rule

Use plain English. Prefix each major step: **`Step X of Y — [action]`**. Follow **`.cursor/rules/15-user-preferences.mdc`**.

## End-of-run chat format

- Follow **`.cursor/rules/15-user-preferences.mdc`**.
- After multi-step work, finish with **`### Activity recap`** containing coverage outcome, confidence distribution, and any remediation needed.

---

## Preconditions

1. **`MyNotes/Customers/[CustomerName]/`** exists (sync via **`sync_notes`** MCP or **`scripts/rsync-gdrive-notes.sh`** if needed).
2. You can read **`Transcripts/`** and **`call-records/`** under that folder (repo mirror).
3. (Recommended) Run the **schema v2 lint CLI** first — it is the main automated gate for call-record quality:

   ```bash
   uv run python -m prestonotes_mcp.call_records lint [CustomerName]
   ```

   Exit 0 means the corpus passes schema v2 + size checks (avg ≤ 1536 bytes / max ≤ 2560 bytes, no banned defaults `ch-stub` / `Fixture narrative` / `E2E fixture`, no forbidden evidence vocabulary). Non-zero exit prints the offending records — fix them (re-run **`Extract Call Records for [CustomerName]`** or hand-edit) before leaning on the human spot-check in Step 8.

---

## Step 1 of 8 — Optional sync

Run **`sync_notes`** for **`[CustomerName]`** (or full-repo rsync) so local files match Drive.

**Tell user:** `Step 1 of 8 — Sync complete (or skipped).`

---

## Step 2 of 8 — Count transcript sources (**Y**)

1. List **`MyNotes/Customers/[CustomerName]/Transcripts/`**.
2. **Meeting pool (default — defines Y):** files matching **`YYYY-MM-DD-*.txt`** (Granola per-call pattern per **`scripts/granola-sync.py`**). Count = **`Y`**.
3. **Exclude from Y by default:** **`_MASTER_TRANSCRIPT_*.txt`** and other non-`DATE-`-prefixed `.txt` unless the user explicitly asks to include them (then state the revised definition in the report).
4. **Default 1-month lookback sanity (optional but recommended for `_TEST_CUSTOMER` / E2E):** from the filename prefix `YYYY-MM-DD`, count how many per-call transcripts fall within the **last 30 days** (rolling window, UTC date math is fine). If the user expects “last month of calls” coverage in **`Load Customer Context`** / **`Update Customer Notes`**, call out when **0** per-call transcripts are recent — refresh exports or add newer `YYYY-MM-DD-*.txt` fixtures.

If **`Y = 0`**, stop and tell the user to run **`scripts/granola-sync.py`** / export per-call transcripts first. Do not claim extraction success.

**Tell user:** `Step 2 of 8 — Per-call transcript files counted: Y = [N] (recent last-30-days = [R] unless user asked for a different window).`

---

## Step 3 of 8 — Load records

1. MCP **`read_call_records([CustomerName])`** (no filters) for full payloads and **`extraction_confidence`** fields. Records that fail schema validation are excluded from the response — treat that as a discrepancy to surface.

**Tell user:** `Step 3 of 8 — Call records loaded.`

---

## Step 4 of 8 — Compute **X** (validated records)

**Default definition for X:** the **`count`** field returned by **`read_call_records`** — i.e. the number of **`call-records/*.json`** files that validate as §7.1 records.

**Consistency check:** If raw `*.json` files exist under **`call-records/`** but do not appear in the **`records`** array, list them as schema-invalid (the server logs the schema error per file).

**Tell user:** `Step 4 of 8 — Validated call records X = [N].`

---

## Step 5 of 8 — Gap analysis (transcripts vs records)

For each per-call transcript basename **`b`** in the Step 2 pool:

- Expect **at least one** call record with **`raw_transcript_ref == b`** (exact basename match).
- If missing: flag **`MISSING_RECORD`** for that file.

For each call record:

- If **`raw_transcript_ref`** does not match any file in the Step 2 pool, flag **`ORPHAN_REF`** (stale path or typo).

**Tell user:** `Step 5 of 8 — Gap check: [summary table or bullet list].`

---

## Step 6 of 8 — Confidence distribution

From **`read_call_records`** results, count **`extraction_confidence`** values:

- **`high`** / **`medium`** / **`low`** (case-normalize to lowercase for counting).
- If missing or unexpected values, bucket under **`other`** and list counts.

**Tell user:** `Step 6 of 8 — Confidence counts: high=[a], medium=[b], low=[c], other=[d].`

---

## Step 7 of 8 — Required coverage report (Stage 1 gate)

Emit **one line first** (verbatim pattern from [`project_spec.md` §9 TASK-009](../../project_spec.md#task-009--bootstrap-a-real-customer-and-run-end-to-end-stage-1-test)):

```text
X of Y meetings indexed. Confidence distribution: high/medium/low.
```

**Example:** `7 of 7 meetings indexed. Confidence distribution: high=5 / medium=2 / low=0.`

Interpretation:

- **Ideal gate pass:** **`X == Y`** (under the same definitions above), **no** `MISSING_RECORD` / `ORPHAN_REF`, and **`low`** either **0** or explained by the user.
- **Gate fail:** **`X < Y`** with unexplained gaps, or many **`low`** without rationale — instruct re-run **`Extract Call Records for [CustomerName]`** or manual JSON fixes (re-run this playbook to confirm).

**Tell user:** `Step 7 of 8 — Coverage report printed above.`

---

## Step 8 of 8 — Human accuracy checklist

Ask the user (or self-check if they are in the loop) for **sample** meetings (pick 2–3 **`high`** and 1 **`medium`** if any):

| Check | Question |
|-------|-----------|
| **Call type** | Does **`call_type`** match **`call-type-taxonomy.md`** for that meeting? |
| **Date** | Does **`date`** match transcript header or filename date? |
| **Participants** | Any invented names? Missing obvious execs who spoke? |
| **Quotes** | Are **`verbatim_quotes`** substrings of the transcript, ≤ 3 items, each ≤ 280 chars, with `speaker` matching a `participants[].name`? (The `lint` CLI checks the substring rule; the human check is whether the attribution is the *right* participant.) |
| **Challenges** | Are **`challenges_mentioned`** grounded in what was said? `id` must be kebab (`^ch-[a-z0-9][a-z0-9-]{1,40}$`) — no `ch-stub`. |
| **Products** | Does **`products_discussed`** match the SKUs actually discussed (DSPM call → `Wiz DSPM` / `Wiz CIEM`, shift-left → `Wiz Code` / `Wiz CLI`, runtime → `Wiz Sensor`), or is it a flat default on every record? |
| **Schema v2 signal fields** | When the call contains real signal, are **`metrics_cited`** (KPIs like Wiz Score, coverage %, workload counts), **`stakeholder_signals`** (sponsor_engaged / champion_exit / new_contact / decision_maker / detractor), **`goals_mentioned`**, and **`risks_mentioned`** populated? Empty `[]` is legal when there is no evidence — empty across **every** record is the fingerprint of stub output. |
| **Sentiment variance** | Across the sampled corpus, does `sentiment` vary with tone (e.g. exec readout or QBR with budget freeze → `cautious`), or is every record `positive`? |

If fixes are needed: edit the relevant **`call-records/<call_id>.json`** (preserve schema), then re-run **Step 3–7** from this playbook.

**Tell user:** `Step 8 of 8 — Test Call Record Extraction complete for [CustomerName].`

---

## MCP tools used

| Tool | Role |
|------|------|
| **`sync_notes`** | Optional mirror refresh |
| **`read_call_records`** | Full validated records, **`count`**, **`extraction_confidence`**, **`raw_transcript_ref`** |

---

## Bootstrap reminder (first-time customer)

If the customer folder is missing, MCP **`bootstrap_customer`** (see **`project_spec.md`** / MCP server) creates scaffold; then add transcripts and run **`Extract Call Records`** before this test playbook.

---

## References

- **`docs/project_spec.md`** §7.1, §9 TASK-009
- **`prestonotes_mcp/call_records.py`** — schema v2 validation, transcript grounding, size cap, banned defaults, lint CLI
- **`prestonotes_mcp/tests/test_call_record_tools.py`** — minimal valid record
- **`prestonotes_mcp/tests/test_call_record_v2_validation.py`** — schema v2 guardrails (kebab challenge ids, quote substring, size cap, confidence downgrade, anti-regression)
- **`.cursor/agents/tester.md`** post-write diff **§6** — parity checks for GDoc / Account Summary when running E2E
