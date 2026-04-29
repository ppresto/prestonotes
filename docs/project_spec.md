# PrestoNotes v2.0 — Master Project Specification

**Version:** 2.0.0  
**Status:** Active Development  
**Last Updated:** 2026-04-17  

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [Core Architectural Rules](#2-core-architectural-rules)
3. [Tech Stack](#3-tech-stack)
4. [Directory Structure](#4-directory-structure)
5. [How the Agents Work](#5-how-the-agents-work)
6. [Data Flow — End to End](#6-data-flow--end-to-end)
7. [Key Data Schemas](#7-key-data-schemas)
8. [Legacy Reference Guide](#8-legacy-reference-guide)
9. [Roadmap and work tracking](#9-roadmap-and-work-tracking)
10. [Definition of Done](#10-definition-of-done)
11. [Trigger Phrase Reference](#11-trigger-phrase-reference)
12. [MVP vs Post-MVP Playbooks](#12-mvp-vs-post-mvp-playbooks)

---

## 1. What This Project Does

PrestoNotes is an AI-powered "account intelligence engine" for a cybersecurity Solutions Engineer (SE). It reads raw meeting transcripts and turns them into structured, trustworthy account summaries that get written back to Google Docs.

**The core loop, in plain English:**
1. You have a customer meeting. Granola (or sync) records it; ingestion saves **one dated transcript file per meeting** under that customer’s `Transcripts/` folder.
2. You run a trigger phrase in Cursor (e.g. `Update Customer Notes for Acme`).
3. The AI loads **call records** via `read_call_records` (and only the raw `.txt` needed for quotes), uses domain tools for recommendations, and proposes updates as **mutation JSON**.
4. You review and approve the proposed changes.
5. **MCP + Python** apply approved changes to your Google Doc and append the history ledger / audit log.

**Architecture highlights (current repo — v2 runtime):**
- **Transcripts:** **One meeting per file** under each customer’s `Transcripts/` folder. **Call records** (structured JSON per meeting under `call-records/`) are the default inputs for reasoning outside tight quote checks.
- **Reasoning vs execution:** The LLM reads, reasons, and outputs **structured plans** (including **Google Doc mutation JSON**). **Approved** MCP tools run Python that performs file I/O and Google APIs — the LLM never calls the Docs API or writes customer files directly.
- **Workflows:** Specialized sub-agents handle domains (security ops, app security, vulnerability management, attack surface, AI/ML security) instead of one monolithic prompt.
- **Journey:** The system tracks the full customer journey over time: where they started, what challenges they have, what got resolved, and what value was delivered.

---

## 2. Core Architectural Rules

These rules must never be violated. The planner should refuse any task that breaks them.

**Rule 1 — Python executes, AI proposes (including GDoc mutations).**
The LLM reads, analyzes, and produces **structured output** — including **mutation JSON** that conforms to `prestonotes_gdoc/config/doc-schema.yaml` and the Customer Notes mutation packs under `docs/ai/gdoc-customer-notes/` (hub: `README.md`; schema/actions: `mutations-global.md`). **Only after explicit user approval** may an agent invoke MCP tools that mutate external or customer state. Python (via MCP: `write_doc`, `append_ledger` / `append_ledger_row`, call-record tools, etc.) performs **all** file writes, date calculations, and **Google Docs/Drive API** calls. **Never** instruct the model to paste content into the live Doc as a substitute for the mutation pipeline.

**Rule 2 — No transcript context flooding.**
Primary path: call MCP **`read_call_records`** to load the validated §7.1 JSON records directly (already sorted by `(date, call_id)`); filter by date range or call type when the task allows it. **Optional:** load **at most one** per-call raw `.txt` transcript file when a quote or boundary check requires verbatim text — each file represents **one meeting**, so there is no legacy “multi-call master in one slice” pattern. Do **not** load `_MASTER_TRANSCRIPT_*.txt` wholesale into context during normal workflows; if a master file still exists during migration, treat it as **ingestion/source only** until split into per-call files.

**Rule 3 — User approves before any write.**
Every MCP tool that mutates data (writes to GDoc, appends ledger, writes call records, writes the journey timeline or challenge lifecycle JSON under **`AI_Insights/`**) must be preceded by a human-readable summary of the proposed changes. The user must explicitly approve before the write tool is called.

**Rule 4 — One customer per session.**
Each Cursor session works on exactly one customer. The planner should ask for the customer name at the start if not given.

**Rule 5 — ai_learnings.mdc is always loaded.**
This file contains corrections discovered during past runs. It overrides playbook defaults. Every run must load it. When a new correction is found, propose adding it to this file rather than patching the playbook.

**Rule 6 — Evidence tags on every fact.**
Every fact written to the account summary or ledger must carry one of: `[Verified: DATE | Name | Role]`, `[Inferred: DATE]`, `[Committed: DATE]`, `[Achieved: DATE]`, `[Legacy: Needs Validation]`, or `[Stale: DATE]`.

**Rule 7 — Legacy code is read-only reference.**
The old project at `../prestoNotes.orig` is used strictly to copy working code. Never modify it. Never add it as a **runtime** import dependency from v2 into the old tree. When porting, strip **machine-specific paths** and keep prompts/configs that are still product ground truth unless superseded by v2 rules.

### Transcript files (v2 layout)

- **Canonical raw form:** `MyNotes/Customers/[CustomerName]/Transcripts/YYYY-MM-DD-[sanitized-title].txt` (one file per completed meeting). **Sanitized-title** means filesystem-safe, human-readable, unique per day if multiple calls occur (append a sequence suffix if needed).
- **Granola / sync:** `scripts/granola-sync.py` (see the script’s docstring and `scripts/README.md`) is responsible for **emitting or splitting** content into these per-call files. During transition, `_MASTER_TRANSCRIPT_[Customer].txt` may still exist as a **Granola append target**; the extractor or a maintenance playbook should **prefer per-call files** once present.
- **Call record link:** Each call record’s `raw_transcript_ref` field points to the **basename** of that per-call `.txt` file (see §7.1).

### Google Doc mutation path (authoritative)

1. Agents load **read-only** context (MCP `read_doc`, call records, ledger, etc.).
2. The orchestrator / advisors produce a **mutation JSON** payload (sections, fields, actions per `doc-schema.yaml` and mutation docs under `docs/ai/gdoc-customer-notes/`).
3. **User approval** in chat.
4. **`write_doc`** MCP tool runs `prestonotes_gdoc/update-gdoc-customer-notes.py` with `--mutations` (and `dry_run` first when appropriate).

**Deprecated:** MCP tool **`run_pipeline`** is **not** part of this architecture. Do not register it on the MCP server. Historical playbooks that referenced it remain **reference only** under §12.

### Ledger writes: `append_ledger` vs `append_ledger_row`

- **`append_ledger`** — legacy row shape; runs the GDoc **`ledger-append`** flow after a successful **`write_doc`**. Retained for backward compatibility and legacy automation.
- **`append_ledger_row`** (TASK-049, schema v3) — Appends one row to **`MyNotes/Customers/<Customer>/AI_Insights/<Customer>-History-Ledger.md`**. Python signature is `append_ledger_row(customer_name: str, row: dict[str, str | int | list[str]]) -> Path`; the MCP tool wraps it and forwards the `row` dict from `row_json`. Frontmatter on a lazily-created ledger carries `schema_version: 3`.

**v3 column list (20 columns, in order — canonical copy lives in `prestonotes_mcp/ledger.py` as `LEDGER_V3_COLUMNS`):**

| # | Column | Type | Notes |
|---|---|---|---|
| 1 | `run_date` | ISO date (`str`) | UCN run date (today); append-only. |
| 2 | `call_type` | enum (`str`) | `qbr \| exec_readout \| product_demo \| commercial_close \| technical_pov \| champion_1on1 \| kickoff \| other`. |
| 3 | `account_health` | enum (`str`) | `great \| good \| at_risk \| critical`. |
| 4 | `wiz_score` | `int` 0..100 (or empty) | Verbatim customer-stated number; empty if not stated. |
| 5 | `sentiment` | enum (`str`) | `positive \| neutral \| negative \| mixed`. |
| 6 | `coverage` | free text ≤ 160 | Deployment / scan coverage headline. |
| 7 | `challenges_new` | id list (`list[str]`) | **Derived from `challenge-lifecycle.json`** — ids that entered `identified` within the run window. |
| 8 | `challenges_in_progress` | id list (`list[str]`) | **Derived** — ids whose current state is `identified` or `in_progress`. |
| 9 | `challenges_stalled` | id list (`list[str]`) | **Derived** — ids whose current state is `stalled`. |
| 10 | `challenges_resolved` | id list (`list[str]`) | **Derived** — ids that transitioned to `resolved` within the run window. |
| 11 | `goals_delta` | free text ≤ 160 | Customer goal shifts this run. |
| 12 | `tools_delta` | free text ≤ 160 | Tools that came online / retired. |
| 13 | `stakeholders_delta` | free text ≤ 160 | Stakeholder movement (departures, promotions, new sponsors). |
| 14 | `stakeholders_present` | id list (`list[str]`) | Normalized names derived from call-record `participants[]` within run window. |
| 15 | `value_realized` | free text ≤ 240 | Quantified / concrete outcomes this run. |
| 16 | `next_critical_event` | free text ≤ 160 | `YYYY-MM-DD: <desc>` when a date is known; otherwise `<desc>` alone. |
| 17 | `wiz_licensed_products` | id list (`list[str]`) | Normalized SKU ids (`wiz_cloud`, `wiz_sensor`, `wiz_code`, `wiz_defend`, `wiz_advanced`, …). |
| 18 | `wiz_license_purchases` | `ISO:sku` list (`list[str]`) | Entries matching `^\d{4}-\d{2}-\d{2}:[a-z0-9_]+$`. |
| 19 | `wiz_license_renewals` | `ISO:sku` list (`list[str]`) | Same format as purchases. |
| 20 | `wiz_license_evidence_quality` | enum (`str`) | `high \| medium \| low`. |

**Write-time validation** (hard rejects; the MCP wrapper catches `LedgerValidationError` and returns `{"ok": false, **payload}` — same shape TASK-048 introduced for `update_challenge_state`): enum violations, `run_date` later than `today + 1 day` (UTC), date regression vs the newest existing row, id-list fragments with empty pieces or surrounding whitespace, `wiz_license_purchases` / `wiz_license_renewals` entries that fail the `ISO:sku` regex, `wiz_score` outside 0..100 or not an int, free-text cells that exceed their cap, and any cell (free text or id-list fragment) containing a term from **`FORBIDDEN_EVIDENCE_TERMS`** in `prestonotes_mcp/journey.py` (same SSoT pattern §7.4 uses — the list is not redefined in `ledger.py`; see the pointer there). Missing keys render as empty cells — the validator only rejects invalid *values*, not absent ones.

**`read_ledger` shape.** `read_ledger(customer_name, max_rows)` returns typed v3 rows: `list[str]` for id-list cells, `int` for `wiz_score`, `str` for free-text / enum cells, and `""` for empty cells. The existing `{"empty": true, ...}` response is still returned when the file is missing. The count of open challenges is **derived on read** as `len(row["challenges_in_progress"]) + len(row["challenges_stalled"])` — there is no stored count column.

**No auto-migration.** There were no production customers on the earlier 24-column v2 schema; the `_TEST_CUSTOMER` E2E reset and the `bootstrap-customer` playbook create fresh v3 ledgers on the first `append_ledger_row` call. Any historical ledger files older than v3 on disk are ignored; UCN's first write re-creates the ledger from scratch (append-only rule applies from that first v3 row forward).

---

## 3. Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Python runtime | `uv` package manager | Never use pip or conda. Always `uv run` or `uv add`. |
| Python version | 3.12.3+ | Set in pyproject.toml |
| MCP server | `fastmcp >= 3.2.0` | **prestonotes** MCP: customer paths, GDoc I/O, ledger, sync, call records |
| Wiz product search (Stage 3–4 bridge) | **wiz-local** (separate MCP server) | Interim: domain advisors call **`wiz_search_wiz_docs`** (or equivalent) on the Wiz docs MCP until **TASK-021** `wiz_knowledge_search` (Chroma) replaces direct search |
| Testing | `pytest` | Write tests before code (TDD) |
| Python linter | `ruff` | Run before every task is marked complete |
| JS / Apps Script | _(none in CI)_ | **`scripts/syncNotesToMarkdown.js`** is Google Apps Script source, not run with Node here; no JS linter in pre-commit until real JS/TS lands |
| AI orchestration | Cursor agents + `.mdc` rules | Primary reasoning — **no Anthropic key required** for the default Cursor-driven flows; Stage 4 embedding/RAG may require keys where noted |
| Document format | Markdown (`.md`) for local files | Google Docs for customer-facing content (via MCP + **`prestonotes_gdoc/`** Python backend) |
| Vector DB | ChromaDB | Stage 4 only — not needed until API keys available |

### MCP tools and resources (prestonotes server)

**Read tools (non-exhaustive):** `check_google_auth`, `list_customers`, `get_customer_status`, **`discover_doc`**, **`read_doc`**, `read_transcripts`, `read_ledger`, `read_challenge_lifecycle` (TASK-047), `read_audit_log` (tail of the file at `paths.audit_log_rel`, default **`logs/mcp-audit.log`**), `check_product_intelligence`, plus Stage 1+ tools as they land (`read_call_records`, …).

**Write / sync tools (TASK-003+):** `write_doc`, `append_ledger`, `append_ledger_row` (TASK-049, v3 schema), `log_run`, `sync_notes`, `sync_transcripts`, `bootstrap_customer`, `write_call_record`, `update_challenge_state` (TASK-010), and further backlog items as they land.

**MCP resources** (stable URIs for agents and tests): `prestonotes://config/doc-schema`, `prestonotes://config/section-sequence`, `prestonotes://config/task-budgets`, `prestonotes://prompts/persona`, `prestonotes://prompts/lens`. Payloads are read from files under **`prestonotes_gdoc/config/`** at runtime.

**Not ported for v2:** `run_pipeline` (see Rule 7 follow-on “Deprecated in v2”).

---

## 4. Directory Structure

```
prestonotes/                          ← new v2 repo root
├── .cursor/
│   ├── plans/                        ← Optional Cursor plans (work tracking)
│   ├── agents/                       ← Optional subagents: coder, code-tester, doc, tester (orchestrator = main Agent + core.mdc)
│   ├── rules/                        ← Runtime rules applied to every session
│   │   ├── 00-core-execution.mdc     ← Non-negotiable guardrails
│   │   ├── 10-task-router.mdc        ← Routes trigger phrases to playbooks
│   │   ├── 15-user-preferences.mdc   ← Output format preferences
│   │   ├── 20-orchestrator.mdc       ← Main workflow orchestration (built in Stage 3)
│   │   ├── 21-extractor.mdc          ← Per-call extraction logic (built in Stage 1)
│   │   ├── 23-domain-advisor-soc.mdc ← Security operations advisor (Stage 3)
│   │   ├── 24-domain-advisor-app.mdc ← Application security advisor (Stage 3)
│   │   ├── 25-domain-advisor-vuln.mdc ← Vulnerability management advisor (Stage 3)
│   │   ├── 26-domain-advisor-asm.mdc  ← Attack surface advisor, image-aware (Stage 3)
│   │   ├── 27-domain-advisor-ai.mdc   ← AI/ML security advisor (Stage 3)
│   │   └── ai_learnings.mdc          ← Dynamic correction patches (port from old project)
│   └── skills/
│       ├── lint.sh                   ← Runs ruff (Python), shellcheck, yamllint
│       └── test.sh                   ← Runs pytest on the prestonotes_mcp/ package
│
├── prestonotes_gdoc/                 ← Google Docs / Drive Python backend
│   ├── update-gdoc-customer-notes.py   ← discover / read / write / ledger-append
│   ├── 000-bootstrap-gdoc-customer-notes.py
│   ├── config/                       ← doc-schema.yaml, sections, prompts, task-budgets, tools.json, …
│
├── docs/
│   ├── project_spec.md               ← THIS FILE — master specification
│   └── ai/
│       ├── playbooks/                ← Playbook markdown files (trigger phrase → steps)
│       └── references/               ← Reference docs (taxonomy, templates, schemas)
│
├── prestonotes_mcp/                  ← Python MCP server package
│   ├── server.py                     ← FastMCP tool definitions (the main file)
│   ├── config.py                     ← Loads prestonotes-mcp.yaml + env vars
│   ├── exec_helper.py                ← Shell script helpers (port from old project)
│   ├── runtime.py                    ← Init context (port from old project)
│   ├── security.py                   ← Input validation, path safety (port from old project)
│   ├── __init__.py
│   ├── __main__.py
│   ├── prestonotes-mcp.yaml          ← Local config (git-ignored, use .yaml.example as template)
│   ├── prestonotes-mcp.yaml.example  ← Template with all config keys documented
│   └── (optional) .env               ← Gitignored; not read by MCP — use `.cursor/mcp.env` (via `mcp.json` `envFile`)
│
├── scripts/
│   ├── granola-sync.py               ← Granola → per-call Transcripts/*.txt (v2); legacy master optional
│   ├── rsync-gdrive-notes.sh         ← Bidirectional sync with Google Drive
│   ├── syncNotesToMarkdown.js        ← Google Apps Script: GDoc → Markdown export
│   ├── restart-google-drive.sh       ← Restarts Google Drive for Desktop
│   └── ci/
│       ├── check-repo-integrity.sh   ← Validates required files exist
│       └── required-paths.manifest   ← List of files that must always exist
│
├── logs/                             ← Local, gitignored; default MCP tool-call JSON audit (`paths.audit_log_rel`, e.g. `mcp-audit.log`)
│
├── MyNotes/                          ← Local customer data (git-ignored)
│   └── Customers/
│       └── [CustomerName]/
│           ├── [CustomerName] Notes.md    ← GDoc export (read-only for AI)
│           ├── Transcripts/
│           │   ├── YYYY-MM-DD-[title].txt ← v2: one file per meeting (canonical raw transcript)
│           │   └── _MASTER_TRANSCRIPT_[CustomerName].txt  ← legacy / Granola target during migration (optional)
│           ├── call-records/              ← per-call structured JSON (§7.1)
│           │   ├── 2026-01-10-discovery-1.json
│           │   └── 2026-02-05-technical_deep_dive-2.json
│           └── AI_Insights/
│               ├── [CustomerName]-History-Ledger.md
│               ├── [CustomerName]-AI-AcctSummary.md    ← optional manual save from Run Account Summary
│               └── challenge-lifecycle.json            ← §7.4 append-only lifecycle state
│
├── pyproject.toml                    ← uv package config, dependencies, tool settings
├── README.md                         ← Setup guide and quick-start
└── .gitignore                        ← Must include MyNotes/, logs/, prestonotes_mcp/.env, *.yaml (not .example)
```

**Naming note (TASK-001):** The repo may temporarily use `.cursor/rules/core.mdc` before numbered rules exist. **Target** is the `00-core-execution.mdc` … `27-domain-advisor-ai.mdc` layout above; migrate without losing content when renaming.

### `prestonotes_gdoc/` vs Cursor sub-agents

| Location | Responsibility |
|----------|----------------|
| **`prestonotes_gdoc/`** | **Execution plumbing** for Google Docs/Drive: REST calls, mutation JSON application, bootstrap, shared **`config/`** (schema, section YAML, budgets, persona/lens **files** consumed by Python). |
| **`.cursor/rules/`** (`21-extractor`, `23–27` domain advisors, `20-orchestrator`, …) | **Reasoning** and workflow: how the LLM interprets transcripts, builds call records, proposes mutations. |
| **`docs/ai/playbooks/`** | Human + model **procedure** docs (trigger phrases, step lists). |

Port **from** `../prestoNotes.orig/custom-notes-agent/` **into** `prestonotes_gdoc/`; update **`prestonotes_mcp`** defaults (e.g. `paths.doc_schema`) and all `run_uv_script(...)` paths to use `prestonotes_gdoc/...`.

---

## 5. How the Agents Work

The **main Cursor Agent** acts as the **planner / orchestrator** (see **`.cursor/rules/core.mdc`** for default habits). **Optional subagents** under `.cursor/agents/*.md` exist for cases where you explicitly want isolated context: **`/coder`**, **`/code-tester`**, **`/doc`**, plus **`/tester`** for **`_TEST_CUSTOMER`** E2E harness work only.

```
User ↔ Main Agent (planner) → (creates/updates task file, gets approval)
                → implement + verify inline (main chat)
                → (optional) update docs when user-visible behavior changed
                → User (reports task complete)
```

**Main Agent (planner)** — The orchestrator. Reads this spec before every task. For multi-step or non-trivial work, use a **Cursor plan** under **`.cursor/plans/`** (or equivalent) if you want a written checklist — there is no `docs/tasks/` system. Asks for user approval before code changes. After approval, **default** is to do implementation work **inline in the main chat**, then run the repo’s quality commands yourself (at minimum the project’s `test.sh` / `lint.sh` equivalents) before claiming done.

**`/coder` subagent (optional)** — Use when you explicitly want an isolated implementation pass. Reads the assigned task file and this spec. Writes a failing test first (TDD) when appropriate, then implements. Updates the task file status when done.

**`/code-tester` subagent (optional)** — Use when you want an isolated verification pass. Runs `test.sh` and `lint.sh` (or the task’s stated commands). Not a substitute for ever running checks when you work inline.

**`/tester` subagent (E2E only)** — Runs the **`_TEST_CUSTOMER`** harness, gates, and post-write diff per **`.cursor/agents/tester.md`**.

**`/doc` subagent (optional)** — Use when you want a dedicated pass to update documentation after code changes.

**Handoffs (subagent mode only):** The planner may pass a **Delegation packet** (full task path, `spec_refs`, Legacy Reference, prior subagent Output Contracts) into each subagent prompt; each subagent returns a structured **Output Contract** for the next step. Format reference (historical): **`docs/archive/cursor-rules-retired/workflow.mdc`**.

**Inline vs subagents:** The repo’s **default** is **inline** work in the main chat. Subagents are **opt-in** when you invoke them. (A historical always-on “subagent pipeline” Cursor rule existed as `.cursor/rules/workflow.mdc`; it is now archived at **`docs/archive/cursor-rules-retired/workflow.mdc`**.)

---

## 6. Data Flow — End to End

This is the full picture of how data moves through the system. Build the pieces in order — each stage adds a layer.

```
[Stage 1 — Foundation]
Granola app → granola-sync.py → per-call Transcripts/YYYY-MM-DD-[title].txt
                      (optional legacy: _MASTER_TRANSCRIPT_[Customer].txt during migration)
                                         ↓
                              21-extractor.mdc (Cursor)
                                         ↓
                              call-records/YYYY-MM-DD-[type]-N.json
                                         ↓
                              [MCP] write_call_record

[Stage 2 — Account Narrative]
call-records/*.json + History-Ledger.md + challenge-lifecycle.json
                                         ↓
                              run-account-summary.md (Cursor playbook)
                                         ↓
                              Account Summary (chat; optional manual save
                              to [CustomerName]-AI-AcctSummary.md)
                              [MCP] read_call_records / read_ledger /
                                    read_challenge_lifecycle (reads only)
                              [MCP] update_challenge_state (during UCN)
                              [MCP] append_ledger_row (during UCN)

[Stage 3 — Domain Advisors]
CustomerStateUpdate.json (delta output from extractor)
                                         ↓
          SOC → APP → VULN → ASM → AI  (sequential advisor passes; SOC ships first in TASK-015)
                                         ↓
                              Recommendations[] per domain
                                         ↓
                              20-orchestrator.mdc compiles all
                                         ↓
                              [User approval gate]
                                         ↓
                              [MCP] write_doc (Google Doc update)
                              [MCP] append_ledger_row
                              [MCP] log_run (audit trail)
                              [MCP] sync_notes (rsync to Drive)

[Stage 4 — RAG (when API keys available)]
Wiz product docs → build_vector_db.py → ChromaDB
                                         ↓
                              [MCP] wiz_knowledge_search
                              (domain advisors use this instead of direct MCP search)
```

---

## 7. Key Data Schemas

### 7.1 Per-Call Record
Stored at: `MyNotes/Customers/[Name]/call-records/[YYYY-MM-DD]-[type]-[N].json`

**Canonical schema:** `prestonotes_mcp/call_records.py` (`CALL_RECORD_SCHEMA`) is the source of truth. Schema **v2** adds four optional structured-signal arrays (`goals_mentioned`, `risks_mentioned`, `metrics_cited`, `stakeholder_signals`) so downstream consumers (Account Summary, targeted UCN pre-lookback reads) can aggregate across calls without re-reading raw transcripts. Write-side guardrails live in `validate_call_record_object` + `validate_call_record_against_transcript` and enforce: kebab challenge ids (`^ch-[a-z0-9][a-z0-9-]{1,40}$`), `key_topics` `minItems: 1` / item `minLength: 3`, Wiz-SKU enum on `products_discussed` (with `Other: …` escape hatch), `verbatim_quotes` max 3 items ≤ 280 chars each and speaker ∈ `participants[].name`, quote substring check against the referenced transcript, 2560-byte serialized size cap, banned-defaults reject list (`BANNED_CALL_RECORD_DEFAULTS = ("ch-stub", "Fixture narrative", "E2E fixture")`), anti-regression (a `high`-confidence record cannot be overwritten with one that has fewer populated signal fields), and automatic downgrade of `extraction_confidence` when ≥ 3 (medium) or ≥ 5 (low) optional fields are empty. Operator-facing lint CLI: `uv run python -m prestonotes_mcp.call_records lint <customer>` — exit 0 means the corpus passes schema + size checks (avg ≤ 1536 bytes / max ≤ 2560 bytes, no banned defaults, no forbidden evidence vocabulary).

```json
{
  "call_id": "2026-04-15-discovery-1",
  "date": "2026-04-15",
  "call_type": "discovery",
  "call_number_in_sequence": 1,
  "duration_minutes": 60,
  "participants": [
    { "name": "Jane Smith", "role": "CISO", "company": "Acme", "is_new": true }
  ],
  "summary_one_liner": "First discovery call — learned about hybrid cloud environment with 3 CSPs.",
  "key_topics": ["CSPM", "hybrid cloud", "compliance"],
  "challenges_mentioned": [
    { "id": "ch-unified-cloud-visibility", "description": "No unified cloud visibility across AWS and Azure", "status": "identified" }
  ],
  "products_discussed": ["Wiz Cloud"],
  "action_items": [
    { "owner": "Jane Smith", "action": "Send architecture overview", "due": "2026-04-22" }
  ],
  "sentiment": "positive",
  "deltas_from_prior_call": [],
  "verbatim_quotes": [
    { "speaker": "Jane Smith", "quote": "We have no idea what's running in our cloud environments." }
  ],
  "goals_mentioned": [
    { "description": "Single-pane cloud visibility before Q3", "category": "security_posture", "evidence_quote": "no idea what's running in our cloud environments" }
  ],
  "risks_mentioned": [
    { "description": "Parallel CSPM rollout blocked by procurement cycle", "severity": "med" }
  ],
  "metrics_cited": [
    { "metric": "workloads_scanned", "value": "900/1000", "context": "current Wiz Cloud coverage against target" }
  ],
  "stakeholder_signals": [
    { "name": "Jane Smith", "role": "CISO", "signal": "sponsor_engaged", "note": "first exec meeting; explicit budget ownership" }
  ],
  "raw_transcript_ref": "2026-04-15-discovery-call-with-acme.txt",
  "extraction_date": "2026-04-16",
  "extraction_confidence": "high"
}
```

All four v2 arrays are **optional** — `[]` is a legal value. Extractor guidance for populating them (MEDDPICC anchor, prior-3-records rule, banned defaults) lives in `docs/ai/playbooks/extract-call-records.md` Step 6 and `.cursor/rules/21-extractor.mdc`.

### 7.2 Call Record Listing (retired index)

The legacy **`transcript-index.json`** aggregate file and its companion index MCP tools were retired in **TASK-046**. The **`call-records/*.json`** directory is now the sole source of truth; callers enumerate records via MCP **`read_call_records`**, which returns `{count, records}` already sorted by `(date, call_id)`.

### 7.3 Call Type Taxonomy

| Type | When to Use | What to Focus On |
|---|---|---|
| `discovery` | First 1-2 calls | Pain points, org structure, current stack, decision process |
| `technical_deep_dive` | Architecture review, POC scoping | Technical requirements, environment details |
| `campaign` | Ongoing relationship calls (call 3+) | Deltas from last call, challenge status changes, action item follow-up |
| `exec_qbr` | Executive business review | Value realized, strategic alignment, renewal signals |
| `poc_readout` | POC results presentation | Findings summary, customer reaction, expansion signals |
| `renewal` | Commercial renewal conversation | License scope, expansion interest, competitive threats |
| `internal` | SE/AE prep call | Strategy notes — not customer-facing |

### 7.4 Challenge Lifecycle States

```
identified → acknowledged → in_progress → resolved
                                ↑               ↓
                             reopened ←────────┘
                                
in_progress → stalled (if no movement for 60+ days)
```

**Write-path discipline (TASK-048).** MCP tool `update_challenge_state(customer_name, challenge_id, new_state, transitioned_at, evidence)` takes `transitioned_at` as a **required** ISO `YYYY-MM-DD` string; there is no silent default. The caller (the UCN extractor) MUST pass the **ISO call date of the cited transcript**, not the date of the UCN run. The same rule applies to the helper `append_challenge_transition` in `prestonotes_mcp/journey.py`. Three hard rejections run inside both write paths and return a structured error payload (field, value, expected / matched): future date (`transitioned_at > today + 1 day` UTC), history regression (`transitioned_at` older than the newest existing `at` for that `challenge_id`), and forbidden evidence vocabulary (substring match, case-insensitive). Old dates of any age are fully accepted — a transcript pulled weeks or months after the call is the common case, not an edge case. The forbidden-vocabulary list is defined exactly once — **`FORBIDDEN_EVIDENCE_TERMS`** in `prestonotes_mcp/journey.py` — and is mirrored as operator-facing prose under `.cursor/rules/11-e2e-test-customer-trigger.mdc` "Artifact hygiene". Extractor-side write rules (one transition = one call, direct-quote evidence ≤ 160 chars, explicit customer directives override heuristics, resolved sweep, split / collapse rules) live in `.cursor/rules/21-extractor.mdc` and are mirrored in `docs/ai/playbooks/update-customer-notes.md`.

### 7.5 Evidence Tags

| Tag | Meaning | When to Use |
|---|---|---|
| `[Verified: DATE \| Name \| Role]` | Explicitly stated by named person | Direct quote or clear statement |
| `[Inferred: DATE]` | Reasonably derived from context | Implied but not stated |
| `[Committed: DATE]` | Customer made a commitment | Action items, approvals |
| `[Achieved: DATE]` | Value confirmed as realized | POC results, metrics confirmed |
| `[Legacy: Needs Validation]` | Old data with no date anchor | Predates transcript coverage |
| `[Stale: DATE]` | Was verified but now > 90 days old | Intended to be **auto-applied by Python** (MCP helper or ledger writer) based on dates in structured fields — exact tool name TBD in TASK-011 / journey tasks; agents must not hand-wave stale tags without a date rule |

---

## 8. Legacy Reference Guide

The old project lives at `../prestoNotes.orig` (relative to the new repo root). It is read-only reference material. The planner must consult this table before porting code.

**Execution tree:** MCP **`write_doc`**, **`read_doc`**, **`discover_doc`**, **`append_ledger`**, and **`bootstrap_customer`** run Python under **`prestonotes_gdoc/`** (see `update-gdoc-customer-notes.py` and related `config/`). The §8 table below lists legacy → v2 paths; do not treat pre-port narratives as the live architecture.

**What to port vs. what to drop vs. reference-only:**

| Legacy source (`../prestoNotes.orig/`) | v2 destination | Action | Notes |
|---|---|---|---|
| `prestonotes_mcp/server.py` | `prestonotes_mcp/server.py` | Port — strip hardcoded paths | Keep FastMCP structure, tool signatures, security patterns; **omit** `run_pipeline`; point subprocess paths at **`prestonotes_gdoc/`** |
| `prestonotes_mcp/config.py` | `prestonotes_mcp/config.py` | Port | Env + yaml resolution |
| `prestonotes_mcp/exec_helper.py` | `prestonotes_mcp/exec_helper.py` | Port | `run_uv_script`, `run_shell_script`, repo root |
| `prestonotes_mcp/runtime.py` | `prestonotes_mcp/runtime.py` | Port | `init_ctx`, `get_ctx` |
| `prestonotes_mcp/security.py` | `prestonotes_mcp/security.py` | Port | `validate_customer_name`, path scope, mutation size checks |
| `prestonotes_mcp/prestonotes-mcp.yaml.example` | `prestonotes_mcp/prestonotes-mcp.yaml.example` | Port — update paths | Default `paths.doc_schema` (and siblings) → **`prestonotes_gdoc/config/...`** |
| MCP **resources** in `server.py` | same | Port | `prestonotes://config/*`, `prestonotes://prompts/*` → read from **`prestonotes_gdoc/config/`** |
| `custom-notes-agent/update-gdoc-customer-notes.py` | `prestonotes_gdoc/update-gdoc-customer-notes.py` | **Port** | GDoc discover/read/write + ledger-append |
| `custom-notes-agent/000-bootstrap-gdoc-customer-notes.py` | `prestonotes_gdoc/000-bootstrap-gdoc-customer-notes.py` | **Port** | `bootstrap_customer` MCP |
| `custom-notes-agent/config/` | `prestonotes_gdoc/config/` | **Port** | Ground truth for mutations and MCP resources |
| `custom-notes-agent/sections/*.py` | `prestonotes_gdoc/sections/*.py` | Port **if** imported by GDoc client | Omit modules only used by **`run-main-task.py`** |
| `custom-notes-agent/run-main-task.py` | _(none on MCP)_ | **Do not expose via MCP** | Reference only under `../prestoNotes.orig` or `docs/examples/` |
| `scripts/granola-sync.py` | `scripts/granola-sync.py` | Port — **extend** for v2 | Per-call `Transcripts/YYYY-MM-DD-[title].txt` per §2; preserve idempotency and Internal-folder routing |
| `scripts/rsync-gdrive-notes.sh` | `scripts/rsync-gdrive-notes.sh` | Port | Bidirectional sync |
| `scripts/syncNotesToMarkdown.js` | `scripts/syncNotesToMarkdown.js` | Port | GDoc → Markdown export |
| `scripts/restart-google-drive.sh` | `scripts/restart-google-drive.sh` | Port | Drive for Desktop restart helper |
| `scripts/wiz_cache_manager.py` | `scripts/wiz_cache_manager.py` | Canonical CLI | Stage 4 ingestion input |
| `scripts/ci/check-repo-integrity.sh` | `scripts/ci/check-repo-integrity.sh` | Port — update manifest | Include **`prestonotes_gdoc/`** |
| `pyproject.toml` | `pyproject.toml` | Port — bump **2.0.0** | Align deps with `uv lock` |
| `.cursor/rules/ai_learnings.mdc` | `.cursor/rules/ai_learnings.mdc` | Port | Corrections layer |
| `.cursor/rules/15-user-preferences.mdc` | `.cursor/rules/15-user-preferences.mdc` | Port | Output prefs |
| `.cursor/rules/00-core-execution.mdc` | **`.cursor/rules/core.mdc`** (merged section) | **TASK-007** | Customer-notes guardrails merged into **`core.mdc`**; v2 paths + per-call transcript rules |
| `docs/ai/playbooks/run-logic-audit.md` | `docs/ai/playbooks/run-logic-audit.md` | **Deferred** (not Stage 1 MVP) | Report playbook — port under a later **reports / QA** task after core notes flow ships |
| `docs/ai/playbooks/run-license-evidence-check.md` | `docs/ai/playbooks/run-license-evidence-check.md` | **Port — TASK-007 MVP** | SKU / entitlement evidence; may **update** local `*-AI-AcctSummary.md` (**Wiz Commercials**) and **History Ledger** license columns; depends on **wiz docs MCP** + optional **`wiz_doc_cache_manager`** (port or document fallback) |
| `docs/ai/playbooks/run-bva-report.md` | `docs/ai/playbooks/run-bva-report.md` | **Deferred** (not Stage 1 MVP) | BVA is **not** MVP |
| `docs/ai/playbooks/load-customer-context.md` | `docs/ai/playbooks/load-customer-context.md` | **Port — TASK-007 MVP** | Session prep (read-only) |
| `docs/ai/gdoc-customer-notes/README.md` (+ `mutations-*.md`) | `docs/ai/gdoc-customer-notes/` | Port | **Required** for mutation JSON quality; index stub remains at `docs/ai/references/customer-notes-mutation-rules.md` |
| `docs/ai/references/account-summary-format-spec.md` | `docs/ai/references/account-summary-format-spec.md` | Port — review | Align with exec summary template (TASK-013) |
| `docs/ai/references/value-realization-taxonomy.md` | `docs/ai/references/value-realization-taxonomy.md` | Port | Value language |
| `docs/ai/playbooks/update-customer-notes.md` | `docs/ai/playbooks/update-customer-notes.md` | **Port — TASK-007 MVP** | **AI meeting recaps (Daily Activity)** + structured **Customer Notes** mutations via MCP **`write_doc`** / ledger / audit log; **TASK-017** may later replace routing with the multi-advisor orchestrator (same trigger phrase) |
| `docs/ai/playbooks/build-product-intelligence.md` | _(post-MVP)_ | Reference — post-MVP | wiz-local MCP search per §3 |

---

## 9. Roadmap and work tracking

**Work tracking:** Use **Cursor plans** under **`.cursor/plans/`** (or your own notes). This repo does **not** use a `docs/tasks/` tree or task index.

**Stages (conceptual):**

- **Stage 1 — Foundation:** Per-call transcripts, MCP read/write, call records, Granola sync, rsync to Drive, core **`.mdc`** rules and playbooks (e.g. `load-customer-context`, `update-customer-notes`, `run-license-evidence-check`), extractor + `extract-call-records`.
- **Stage 2 — Account narrative:** Challenge lifecycle tools, History Ledger (v3), exec + account summary (`run-account-summary`).
- **Stage 3 — Orchestration:** Domain advisors, orchestrator + task router, UCN; see **§11** triggers.
- **Stage 4 — RAG (optional):** Vector ingest, `wiz_knowledge_search`, when API keys and Chroma are configured.

**Legacy porting:** For code ported from `../prestoNotes.orig`, use **§8** and the playbooks.

**Note:** Code and older prose may still mention **TASK-NNN** as historical labels; there are no accompanying task spec files in this repo.


## 10. Definition of Done

A change is complete when **all** of the following are true:

1. **The feature works** — behavior matches the agreed plan and any stated acceptance checks.
2. **Tests pass** — `uv run pytest` exits with code 0 (or the change is documentation-only and you have verified links and formatting).
3. **Linters pass** — `ruff check prestonotes_mcp/ scripts/` exits with code 0 where Python changed.
4. **Docs are updated** — `README.md` (or the relevant playbook) reflects new trigger phrases, tools, or setup steps when user-visible behavior changed.

---

## 11. Trigger Phrase Reference (MVP)

These triggers are **in scope for the v2 MVP** (Stage 1–2 and Stage 3 where noted). Wording in playbooks may vary slightly; the **task router** (`10-task-router.mdc`) is the source of truth for aliases when it ships. **Report-only** triggers **`Run Logic Audit`** and **`Run BVA Report`** are **not** Stage 1 MVP — defer to a **later reports** backlog item (see **§12**). **`Run License Evidence Check`** is Stage 1 MVP.

| Trigger | What It Does | Stage |
|---|---|---|
| `Load Customer Context for [Customer]` | Read-only snapshot for session prep | 1 |
| `Update Customer Notes for [Customer]` | **MVP (TASK-007):** Monolithic playbook — sync/read, **Daily Activity AI recaps** + structured doc mutations, user-approved **`write_doc`** / ledger / log via MCP. **Later (TASK-017):** same trigger may route through multi-advisor orchestrator. | 1 → 3 |
| `Extract Call Records for [Customer]` | Build/update **call-records** from per-call transcript files | 1 |
| `Test Call Record Extraction for [Customer]` | Manual QA / coverage report for extraction | 1 |
| `Run License Evidence Check for [Customer]` | SKU / entitlement evidence matrix; may **update** local **`[Customer]-AI-AcctSummary.md`** (**Wiz Commercials**) and **History Ledger** license columns; **wiz docs MCP** + optional cache tooling | 1 |
| `Run Account Summary for [Customer]` | Structured exec + account narrative via **`docs/ai/playbooks/run-account-summary.md`** and **`docs/ai/references/exec-summary-template.md`** (TASK-013, expanded in TASK-047 to absorb the retired Stage-2 narrative sidecar). **Read-heavy:** optional **`sync_notes`** MCP or **`scripts/rsync-gdrive-notes.sh`**, then MCP reads such as **`discover_doc`**, **`read_doc`**, **`read_ledger`**, **`read_call_records`**, **`read_challenge_lifecycle`**, **`read_transcripts`**, optional **`read_audit_log`**; weighted context per **`docs/ai/references/customer-data-ingestion-weights.md`**. No mandatory writes; optional **`log_run`** only if the user asks for an audit trail entry. For a **short exec-only blurb**, skip the optional sections (Metadata, Health, Chronological call spine, Milestones, Challenge review) and output sections 2–3 + 7–11. | 2 |
| `Run Tech Acct Plan for [Customer] [Domain]` | **Single-domain** advisor pass (used to validate SOC-first, then others as their `.mdc` ship) | 3 |

**Customer-local MCP writes (MyNotes mirror, not GDoc):** Stage 1–2 tools that mutate files under **`MyNotes/Customers/<Customer>/`** include **`write_call_record`** and **`update_challenge_state`** ( **`AI_Insights/challenge-lifecycle.json`** ). Each requires the **Rule 3** approval gate in chat before the tool runs. Challenge transitions follow §7.4 states; the JSON file stores **`current_state`** and an append-only **`history`** (`state`, `at`, `evidence`) per challenge id. The companion read tool is **`read_challenge_lifecycle`** (TASK-047), which mirrors the shape of `read_ledger` / `read_call_records`.

---

## 12. MVP vs Post-MVP Playbooks

**MVP goal:** Ship the §11 triggers with **correct prompt logic** and MCP boundaries. **Do not** block MVP on porting every legacy playbook from `../prestoNotes.orig`.

**Post-MVP (reference / enhancement):** The following are **not** MVP commitments. Keep copies under `docs/ai/playbooks/archive/` or point to `../prestoNotes.orig/docs/ai/playbooks/` until selectively promoted:

| Legacy / extra trigger | Notes |
|---|---|
| `Run Logic Audit for [Customer]` | Read-only QA report — **deferred** (not TASK-007 MVP) |
| `Run BVA Report for [Customer]` | Business value assessment — **deferred** (not TASK-007 MVP); explicitly out of MVP per product direction |
| `Run Exec Briefing for [CustomerName]` | **Retired** — use **`Run Account Summary`** §1 only. |
| `Run Challenge Review for [Customer]` | **Retired** — challenge governance (review table, 60-day stall rule, per-row `update_challenge_state` approvals) lives in **UCN** Phase 0 (`.cursor/rules/20-orchestrator.mdc`). A read-only **Challenge review** table is also an optional section of **`Run Account Summary`** (sourced from `read_challenge_lifecycle`). The former `Run Journey Timeline` home was itself retired by **TASK-047**. |
| `Debug Pipeline for [CustomerName]` | **Retired** — ad-hoc **`read_doc`** / ledger checks when debugging UCN. |
| `Run Full Account Rebuild for [Customer]` | Legacy composed workflow — **superseded** by orchestrator + explicit triggers when needed |
| `Run Step 9 Post-Seed Synthesis` / `Polish Account Summary` (and related) | Heavy **replace_field_entries** passes — reference `run-seeded-notes-replay.md` in orig |
| `build-product-intelligence` / deep doc-harvest flows | Revisit with **wiz-local** + Stage 4 RAG; avoid context flooding |
| Any playbook depending on **`run_pipeline`** / `run-main-task.py` | **Unsupported** in v2 — rewrite to LLM mutation JSON + `write_doc` if a capability must return |

**Promotion rule:** A post-MVP playbook graduates into MVP only when it has an **explicit owner** (plan or team decision) and passes Definition of Done (§10).

---
