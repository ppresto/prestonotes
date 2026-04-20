# Migration Guide — `prestoNotes.orig` → v2

The **authoritative port/omit table** is [`project_spec.md` §8](project_spec.md#8-legacy-reference-guide). This file adds **process** and **v2 path naming**.

## v2 name for the Google Docs Python stack

| v1 (legacy, read-only) | v2 (this repo) |
|------------------------|----------------|
| `../prestoNotes.orig/custom-notes-agent/` | **`prestonotes_gdoc/`** |

**Why rename:** `custom-notes-agent` implied a single “agent”; v2 splits **reasoning** (`.cursor/rules/`, playbooks) from **Docs API execution** (`prestonotes_gdoc/`). See [`project_spec.md` §4 — Directory structure](project_spec.md#4-directory-structure) (subsection **`prestonotes_gdoc/` vs Cursor sub-agents**).

## Old project location

| Item | Value |
|------|--------|
| Path | `../prestoNotes.orig` (relative to this repo root) |
| Mode | **READ-ONLY** — never modify, never `import` from it at runtime |

When porting: **copy** into `prestonotes_gdoc/` or `prestonotes_mcp/`, then strip machine-specific paths and move embedded LLM prompts into `.mdc` / playbooks per [`project_spec.md` §2](project_spec.md).

## MCP / Cursor environment (v2)

The committed **[`.cursor/mcp.json`](../.cursor/mcp.json)** defines the **stdio** PrestoNotes server and uses **`envFile`** → **`.cursor/mcp.env`** (gitignored) for **`GDRIVE_BASE_PATH`**, **`MYNOTES_ROOT_FOLDER_ID`**, **`GCLOUD_ACCOUNT`**, **`GCLOUD_AUTH_LOGIN_COMMAND`**, … Copy **[`.cursor/mcp.env.example`](../.cursor/mcp.env.example)** to **`mcp.env`** and edit. Cursor merges **`mcp.json`** `env` (e.g. **`PRESTONOTES_REPO_ROOT`**) with variables from **`mcp.env`** when it spawns **`uv run python -m prestonotes_mcp`**. The Python server **does not** read **`prestonotes_mcp/.env`**; see **`prestonotes_mcp/.env.example`** for optional **shell-only** exports.

If this repo was ever shared with real values in **`mcp.json`**, rotate or restrict any exposed Drive folder IDs and use **`mcp.env`** going forward.

## Porting checklist (every file)

Before merging a port:

1. No hardcoded personal paths — use **`.cursor/mcp.env`**, **`prestonotes_mcp/config.py`**, and **`prestonotes-mcp.yaml`** patterns (not committed Python literals).
2. No secrets in code — no API keys, no pinned `gcloud` account strings in committed files.
3. No long LLM prompt strings in Python — those belong in `.cursor/rules/` or `docs/ai/playbooks/`.
4. New or changed Python has a test under `prestonotes_mcp/tests/` or `scripts/tests/` as appropriate.
5. All `run_uv_script(...)` and `paths.doc_schema` defaults point at **`prestonotes_gdoc/...`**, not `custom-notes-agent/...`.

## `prestonotes_gdoc/` file list (fill in as the port lands)

The first successful CI green build should **list every path** under **`prestonotes_gdoc/`** that the MCP server invokes (discover/read/write/ledger-append/bootstrap).

**Source tree to copy from:** `../prestoNotes.orig/custom-notes-agent/` (per §8).

**v2 lean tree (after TASK-002 cleanup):** The repo keeps the **Docs API client** (`update-gdoc-customer-notes.py`), **bootstrap** script, and **`config/**` YAML + prompts needed for read/write and MCP resources. It **does not** retain v1’s `run-main-task.py`, Python `sections/*_section.py`, seed scripts, or committed `tmp/` artifacts — those remain in **`../prestoNotes.orig`** for historical reference. Section/template **procedures** live under **`docs/ai/references/`** (e.g. `gdoc-section-changes-v2.md`).

**Files confirmed in-tree:**

- **`prestonotes_gdoc/update-gdoc-customer-notes.py`** + **`config/`** (+ bootstrap) — MCP discover/read; write/sync in **TASK-003**.

## Granola → per-call `Transcripts/*.txt` (TASK-005)

v2 expects **one raw `.txt` per meeting** under `MyNotes/Customers/<Customer>/Transcripts/` (see [`project_spec.md` §4](project_spec.md#4-directory-structure)).

**What `scripts/granola-sync.py` does**

- Reads the Granola desktop cache on macOS (default: `~/Library/Application Support/Granola/cache-v4.json`, then `cache-v3.json`), or **`GRANOLA_CACHE_PATH`**.
- Unwraps the nested JSON shape (`cache` string → inner `state` with `documents` and `transcripts`) consistent with common community parsers.
- For each meeting document that has transcript segments (or notes if **`--emit-notes-without-transcript`**), writes **one file** under  
  `{GDRIVE_BASE_PATH}/Customers/<folder-name>/Transcripts/`.
- **Folder → customer:** uses the **first** entry in each document’s `folders[]` Granola field; the folder **`name`** must match the customer directory name (sanitized). Folder names matching **`GRANOLA_INTERNAL_FOLDER_NAMES`** (default: `internal`) map to the customer directory **`Internal`** (override with **`GRANOLA_INTERNAL_CUSTOMER_NAME`**).
- **Idempotency:** re-running overwrites the same path when the file’s `granola_meeting_id` header matches; otherwise a disambiguating suffix is added if two meetings share the same date + title slug.
- **`_MASTER_TRANSCRIPT_[Customer].txt`:** not produced by this script. Legacy rolling masters remain a separate migration concern; prefer per-call files for MCP **`read_transcripts`** once present.

**If Granola changes cache format:** adjust parsing in `scripts/granola-sync.py` and extend **`scripts/tests/test_granola_sync.py`** with a fixture matching the new shape.

## Drive ↔ repo `MyNotes/` mirror (TASK-006)

| Mechanism | Role |
|-----------|------|
| **`scripts/rsync-gdrive-notes.sh`** | **Pull** from the **Google Drive for Desktop** path **`GDRIVE_BASE_PATH`** (your mounted **MyNotes** root) into **`$PRESTONOTES_REPO_ROOT/MyNotes/`**. MCP tools such as **`list_customers`** read the **repo** copy. Optional PDF → `*_OCR.md` via MarkItDown when installed. |
| **`sync_notes` MCP tool** | Runs that shell script from the repo root (optional customer argument → only **`Customers/<name>/`**). |
| **`scripts/restart-google-drive.sh`** | macOS helper to restart the Drive app so the mount catches up after API-side changes. |
| **`scripts/syncNotesToMarkdown.js`** | **Google Apps Script** (not Node): exports eligible Google Docs to **`.md`** on Drive under MyNotes; pair with rsync if you want those files in the repo. Configure **`MYNOTES_ROOT_FOLDER_ID`** as a Script property — same ID as **`.cursor/mcp.env`**. |

**Not covered by rsync:** Google Docs API read/write (**`discover_doc`**, **`read_doc`**, **`write_doc`**) and **`granola-sync.py`** — those use **`gcloud`** / Granola cache respectively, not the rsync mirror.

## Stage 1 MVP playbooks (TASK-007)

Procedures and trigger phrases live under **`docs/ai/playbooks/`** with supporting references in **`docs/ai/references/`**:

| Playbook | Role |
|----------|------|
| **`load-customer-context.md`** | Read-only session prep (ingestion weights, paths) |
| **`update-customer-notes.md`** | Daily Activity prepends + structured Customer Notes (**`read_doc`** → approved mutations → **`write_doc`**) + ledger / audit |
| **`run-license-evidence-check.md`** | License/SKU evidence matrix; may update **`[Customer]-AI-AcctSummary.md`** and ledger license columns; optional **`scripts/wiz_doc_cache_manager.py`** + wiz MCP |

Guardrails merged into **`.cursor/rules/core.mdc`** (Customer notes section); **`15-user-preferences.mdc`** and **`ai_learnings.mdc`** carry preferences and path/MCP reminders.

## Extract call records (TASK-008)

Per-call **`Transcripts/*.txt`** → **`call-records/*.json`** + **`transcript-index.json`** via playbook **`docs/ai/playbooks/extract-call-records.md`** and rule **`.cursor/rules/21-extractor.mdc`**, using MCP **`write_call_record`** / **`update_transcript_index`**. Taxonomy: **`docs/ai/references/call-type-taxonomy.md`**.

**Stage 1 gate (TASK-009):** Before starting Stage 2 work, run **`docs/ai/playbooks/test-call-record-extraction.md`** (`Test Call Record Extraction for [Customer]`) on a real customer with per-call transcripts and confirm the coverage report in that playbook.

## Journey timeline + challenge lifecycle (TASK-010)

These MCP tools write under the repo **`MyNotes/`** mirror (same customer root as call records and transcripts). They do **not** use the Google Docs API.

| Tool | On-disk target |
|------|----------------|
| **`write_journey_timeline(customer_name, content)`** | **`MyNotes/Customers/<Customer>/AI_Insights/<Customer>-Journey-Timeline.md`** — full markdown body (UTF-8). Creates **`AI_Insights/`** when missing. **`content`** is bounded by **`max_journey_timeline_bytes`** in **`prestonotes-mcp.yaml`** (default **2 MiB** in **`prestonotes-mcp.yaml.example`**). |
| **`update_challenge_state(customer_name, challenge_id, new_state, evidence)`** | **`MyNotes/Customers/<Customer>/AI_Insights/challenge-lifecycle.json`** — merges append-only history per **`challenge_id`** (safe id: letters, digits, **`._-`**, no path segments). **`new_state`** must be one of **`identified`**, **`acknowledged`**, **`in_progress`**, **`resolved`**, **`reopened`**, **`stalled`** (see **`docs/project_spec.md`** §7.4). Each recorded transition includes a **`YYYY-MM-DD`** date (UTC calendar date from the server) and a non-empty **`evidence`** string. Illegal state jumps raise **`ValueError`** with allowed next states; repeating the current state is rejected. |

**Approval:** Server instructions and tool docstrings require **show plan → user approves in chat** before calling **`write_journey_timeline`** or **`update_challenge_state`** (same pattern as **`write_doc`** / **`write_call_record`**).

## Journey synthesizer (TASK-012)

**Cursor** workflow for the **`Run Journey Timeline for [CustomerName]`** trigger (see **`docs/project_spec.md`** §11):

| Artifact | Role |
|----------|------|
| **`docs/ai/playbooks/run-journey-timeline.md`** | End-to-end procedure (TASK-012 steps 1–9 in §9); VP narrative + markdown sections for the timeline file |
| **`.cursor/rules/22-journey-synthesizer.mdc`** | Rule (playbook + **`MyNotes/**`** globs); wires MCP reads (**`read_transcript_index`**, **`read_call_records`**, optional **`read_ledger`**) and approved writes (**`write_journey_timeline`**, **`update_challenge_state`**) |
| **`docs/ai/references/challenge-lifecycle-model.md`** | Challenge lifecycle states (§7.4) and how call records inform transitions |
| **`docs/ai/references/health-score-model.md`** | Account health 🟢🟡🔴⚪ rules (same wording as §9 TASK-012) |

Complete the **Stage 1** extraction validation playbook (**`docs/ai/playbooks/test-call-record-extraction.md`**, TASK-009) on a customer before treating journey synthesis as production-ready for that account.

## Exec summary + run account summary (TASK-013)

**Trigger:** **`Run Account Summary for [CustomerName]`** (see **`docs/project_spec.md`** §11).

| Artifact | Role |
|----------|------|
| **`docs/ai/playbooks/run-account-summary.md`** | Eight-step procedure: setup → doc identity → **`read_doc`** / index → ledger + call records → weighted context (**`customer-data-ingestion-weights.md`**) → Wiz language normalization → output from template → quality gate |
| **`docs/ai/references/exec-summary-template.md`** | Section order and rules (30-second brief, challenges map, stakeholders, value realized, strategic position, Wiz commercials, open challenges) plus fact-attribution tags per the project spec |

**Writes:** This playbook does **not** require mutating customer notes. Optional **`log_run`** only when the user wants a run recorded. **`scripts/ci/required-paths.manifest`** lists both paths so repo integrity checks fail if either file is missing.

## Challenge review playbook (TASK-014)

**Trigger:** **`Run Challenge Review for [CustomerName]`** (see **`docs/project_spec.md`** §11).

| Artifact | Role |
|----------|------|
| **`docs/ai/playbooks/run-challenge-review.md`** | Eight-step procedure: optional **`sync_notes`** → read **`MyNotes/Customers/<Customer>/AI_Insights/challenge-lifecycle.json`** → union challenge ids with **§7.1** call records → dates / stall rules → recommended actions → optional ledger context → present table → **`update_challenge_state`** only after **explicit approval** per change |

**Reads:** **`challenge-lifecycle.json`**, **`read_call_records`**, optional **`read_ledger`**. **Writes:** None required; lifecycle updates use the same approval pattern as **`write_journey_timeline`** / **`update_challenge_state`** elsewhere. **`scripts/ci/required-paths.manifest`** includes **`docs/ai/playbooks/run-challenge-review.md`** so **`bash scripts/ci/check-repo-integrity.sh`** fails if the playbook is missing.

## History Ledger v2 — 19 → 24 columns (TASK-011)

The on-disk ledger is **`MyNotes/Customers/<Customer>/AI_Insights/<Customer>-History-Ledger.md`**. The markdown table under **`## Standard ledger row`** must have **24** columns before MCP **`append_ledger_v2`** can append a row.

**Five new columns** (after the existing 19): **`call_type`**, **`challenges_in_progress`**, **`challenges_resolved`**, **`value_realized`**, **`key_stakeholders`**. The MCP tool accepts **`row_json`**: a JSON object whose keys are **exactly** those 24 names (19 use the same display strings as the table header, e.g. **`Date`**, **`Account Health`**, …; the five new keys are snake_case as listed). Every value must be a **string**.

**Migrate an existing 19-column ledger** (in-place rewrite of the standard table; existing cell text preserved, new columns padded with empty strings):

```bash
uv run python -m prestonotes_mcp.tools.migrate_ledger --customer "YourCustomerFolderName"
```

Or migrate a specific file:

```bash
uv run python -m prestonotes_mcp.tools.migrate_ledger --fixture ./path/to/Acme-History-Ledger.md
```

**`--dry-run`** prints the full migrated markdown to **stdout** and does not write the file. For **`--customer`**, the CLI resolves **`PRESTONOTES_REPO_ROOT`** (from the environment, e.g. **`setEnv.sh`** / Cursor **`mcp.env`**) or falls back to the **current working directory** as the repo root.

**`append_ledger`** (v1 / GDoc subprocess path) remains for backward compatibility until each customer’s ledger is migrated; prefer **`append_ledger_v2`** for new rows once the table is v2. Optional: when **`GDRIVE_BASE_PATH`** is set and the mirrored **`Customers/<Customer>/AI_Insights/`** parent exists, **`append_ledger_v2`** also copies the updated ledger there (same pattern as **`append_ledger`**).

## Ruff and `prestonotes_gdoc/`

The root **`pyproject.toml`** excludes **`prestonotes_gdoc/`** from Ruff so the large v1-port **`update-gdoc-customer-notes.py`** does not block every commit. **Tradeoff:** style and unused-import hygiene for that tree are manual or follow-up (narrow allowlist, e.g. format **`000-bootstrap-gdoc-customer-notes.py`** only). **`prestonotes_mcp/`** and **`scripts/`** remain fully linted.

## Discrepancies found (spec vs old code)

_Add dated notes when behavior differs from [`project_spec.md`](project_spec.md)._

| Date | Topic | Spec says | Old code does | Resolution |
|------|--------|-----------|---------------|------------|
| 2026-04-17 | Granola filenames | `YYYY-MM-DD-[title].txt` examples | Stable idempotency uses an 8-char meeting-id suffix when two meetings collide on date+title | Documented above; header includes `granola_meeting_id` for overwrite detection |
