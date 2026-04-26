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
- For each meeting document that has **segment transcripts** in `state.transcripts[id]` (when present) or, by default, **Granola notes** (`notes_plain` / `notes_markdown`) when the transcript index has no entry (typical Granola v6), writes **one file** under  
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

Per-call **`Transcripts/*.txt`** → **`call-records/*.json`** via playbook **`docs/ai/playbooks/extract-call-records.md`** and rule **`.cursor/rules/21-extractor.mdc`**, using MCP **`write_call_record`**. Taxonomy: **`docs/ai/references/call-type-taxonomy.md`**.

**TASK-046 — transcript-index retired:** the aggregate **`transcript-index.json`** and the `update_transcript_index` / `read_transcript_index` MCP tools were removed end-to-end. **`read_call_records`** enumerates validated §7.1 records directly (sorted by `(date, call_id)`) and is the sole listing API.

**Stage 1 gate (TASK-009):** Before starting Stage 2 work, run **`docs/ai/playbooks/test-call-record-extraction.md`** (`Test Call Record Extraction for [Customer]`) on a real customer with per-call transcripts and confirm the coverage report in that playbook.

## Challenge lifecycle (TASK-010)

This MCP tool writes under the repo **`MyNotes/`** mirror (same customer root as call records and transcripts). It does **not** use the Google Docs API.

| Tool | On-disk target |
|------|----------------|
| **`update_challenge_state(customer_name, challenge_id, new_state, transitioned_at, evidence)`** | **`MyNotes/Customers/<Customer>/AI_Insights/challenge-lifecycle.json`** — merges append-only history per **`challenge_id`** (safe id: letters, digits, **`._-`**, no path segments). **`new_state`** must be one of **`identified`**, **`acknowledged`**, **`in_progress`**, **`resolved`**, **`reopened`**, **`stalled`** (see **`docs/project_spec.md`** §7.4). **`transitioned_at`** is **required** (ISO **`YYYY-MM-DD`**) — the caller passes the **call date of the cited transcript**, not the run date. Illegal state jumps raise **`ValueError`** with allowed next states; repeating the current state is rejected. |
| **`read_challenge_lifecycle(customer_name)`** | Same path. Returns `{"path": ..., "data": {...}}` when the JSON exists, or `{"error": "file not found", "path": ...}` when it does not. Mirrors the read surface of `read_ledger` / `read_call_records` / `read_doc`. |

**Approval:** Server instructions and tool docstrings require **show plan → user approves in chat** before calling **`update_challenge_state`** (same pattern as **`write_doc`** / **`write_call_record`**). `read_challenge_lifecycle` is read-only and needs no approval.

**TASK-048 write-path discipline:** `update_challenge_state` takes `transitioned_at` as a **required** parameter — no silent default, no server-side "use today" fallback. The UCN extractor reads the ISO `DATE:` header from the cited transcript and passes that. Three hard rejections (with structured error payloads naming the field, value, and expected / matched term) run inside the tool: future date (`transitioned_at > today + 1 day` UTC), history regression (incoming `transitioned_at` older than the newest existing `at` for that `challenge_id`), and forbidden evidence vocabulary (substring match, case-insensitive). Old dates of any age — a transcript pulled a week, month, or year after the call — are fully accepted. The forbidden-vocabulary list lives in **`FORBIDDEN_EVIDENCE_TERMS`** in `prestonotes_mcp/journey.py` (single source of truth), mirrored as operator-facing prose in `.cursor/rules/11-e2e-test-customer-trigger.mdc` "Artifact hygiene". Extractor-side rules (call-date wins, one transition = one call, direct-quote evidence, resolved sweep, split / collapse, Challenge Tracker row `date` + `notes_references` discipline) live in `.cursor/rules/21-extractor.mdc` and mirror in `docs/ai/playbooks/update-customer-notes.md`.

## Account narrative lives in Run Account Summary (TASK-047)

**TASK-047 retired the Journey Timeline surface.** The `write_journey_timeline` MCP tool, the `run-journey-timeline.md` playbook, the `22-journey-synthesizer.mdc` rule, the `max_journey_timeline_bytes` config key, and the UCN "mandatory sidecar" contract have all been removed. Nothing downstream was reading `*-Journey-Timeline.md`, so deletion is safe.

Existing `MyNotes/Customers/<Customer>/AI_Insights/<Customer>-Journey-Timeline.md` files are left in place on disk — no automation touches them anymore, and operators who care can delete manually.

The account narrative (Health line, chronological call spine, milestones, challenge review, stakeholder evolution with first-seen / last-seen, value realized, strategic position) now lives in **`Run Account Summary for [CustomerName]`** (**`docs/ai/playbooks/run-account-summary.md`**) as optional sections driven by `read_call_records`, `read_ledger`, and the new `read_challenge_lifecycle` MCP tool. UCN continues to persist `challenge-lifecycle.json`, the Google Doc, and the History Ledger; it no longer writes a narrative sidecar.

## Exec summary + run account summary (TASK-013)

**Trigger:** **`Run Account Summary for [CustomerName]`** (see **`docs/project_spec.md`** §11).

| Artifact | Role |
|----------|------|
| **`docs/ai/playbooks/run-account-summary.md`** | Eight-step procedure: setup → doc identity → **`read_doc`** / index → ledger + call records → weighted context (**`customer-data-ingestion-weights.md`**) → Wiz language normalization → output from template → quality gate |
| **`docs/ai/references/exec-summary-template.md`** | Section order and rules (30-second brief, challenges map, stakeholders, value realized, strategic position, Wiz commercials, open challenges) plus fact-attribution tags per the project spec |

**Writes:** This playbook does **not** require mutating customer notes. Optional **`log_run`** only when the user wants a run recorded. **`scripts/ci/required-paths.manifest`** lists both paths so repo integrity checks fail if either file is missing.

## Journey timeline + challenge governance (TASK-012 + TASK-014 → retired/redistributed by TASK-047)

**Historical note.** The original Stage 2 shape shipped a dedicated **`Run Journey Timeline for [CustomerName]`** playbook (`docs/ai/playbooks/run-journey-timeline.md`) with **TASK-014** challenge governance (review table, 60-day stall rule, per-row `update_challenge_state` approvals) living **inside** it as Steps 5–8. **TASK-047 retired that surface** (see the section above). What each half of that work became:

| Former piece (retired) | Current home (after TASK-047) |
|------------------------|-------------------------------|
| `docs/ai/playbooks/run-journey-timeline.md` + `.cursor/rules/22-journey-synthesizer.mdc` + MCP `write_journey_timeline` + `*-Journey-Timeline.md` sidecar | Deleted. Narrative content (Health line, chronological call spine, milestones, stakeholder evolution) is now **optional sections** in `docs/ai/playbooks/run-account-summary.md` sourced from `read_call_records`, `read_ledger`, and the new read-only `read_challenge_lifecycle` MCP tool. |
| **TASK-014** challenge governance (review table, stall rules, approved `update_challenge_state` rows) | Primary home is **UCN Phase 0** in `.cursor/rules/20-orchestrator.mdc` (Block A — Challenge status updates), executed during `Update Customer Notes`. A read-only **Challenge review** table also appears as an optional section of `Run Account Summary`, sourced from `challenge-lifecycle.json` (via `read_challenge_lifecycle`) with the same 60-day stall rule from `docs/ai/references/challenge-lifecycle-model.md`. |

**Reads still in use:** `challenge-lifecycle.json` (via `read_challenge_lifecycle`), `read_call_records`, optional `read_ledger`. **Writes still in use:** `update_challenge_state` (approved, per-row, from UCN Phase 0). `write_journey_timeline` was deleted — do not invoke it from any playbook or rule. `scripts/ci/required-paths.manifest` no longer lists `docs/ai/playbooks/run-journey-timeline.md`.

## History Ledger v3 — 20 snake_case columns (TASK-049)

The on-disk ledger is **`MyNotes/Customers/<Customer>/AI_Insights/<Customer>-History-Ledger.md`**. The markdown table under **`## Standard ledger row`** is **20** columns at **`schema_version: 3`**. The canonical column list lives in **`prestonotes_mcp/ledger.py`** as **`LEDGER_V3_COLUMNS`**; the column-by-column specification (types, sources, caps, enum values) lives in **`docs/project_spec.md`** § _Ledger writes: `append_ledger` vs `append_ledger_row`_.

**No auto-migration.** The **`_TEST_CUSTOMER`** E2E reset and the bootstrap-customer playbook create fresh **v3** ledgers on the first **`append_ledger_row`** call. Any historical ledger files on disk older than v3 are ignored; UCN's first write re-creates the ledger from scratch on disk (append-only rule applies from that first v3 row forward).

## Ruff and `prestonotes_gdoc/`

The root **`pyproject.toml`** excludes **`prestonotes_gdoc/`** from Ruff so the large v1-port **`update-gdoc-customer-notes.py`** does not block every commit. **Tradeoff:** style and unused-import hygiene for that tree are manual or follow-up (narrow allowlist, e.g. format **`000-bootstrap-gdoc-customer-notes.py`** only). **`prestonotes_mcp/`** and **`scripts/`** remain fully linted.

## Discrepancies found (spec vs old code)

_Add dated notes when behavior differs from [`project_spec.md`](project_spec.md)._

| Date | Topic | Spec says | Old code does | Resolution |
|------|--------|-----------|---------------|------------|
| 2026-04-17 | Granola filenames | `YYYY-MM-DD-[title].txt` examples | Stable idempotency uses an 8-char meeting-id suffix when two meetings collide on date+title | Documented above; header includes `granola_meeting_id` for overwrite detection |
