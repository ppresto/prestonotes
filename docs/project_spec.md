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
9. [Master Task Backlog](#9-master-task-backlog)
10. [Definition of Done](#10-definition-of-done)
11. [Trigger Phrase Reference](#11-trigger-phrase-reference)
12. [MVP vs Post-MVP Playbooks](#12-mvp-vs-post-mvp-playbooks)

---

## 1. What This Project Does

PrestoNotes is an AI-powered "account intelligence engine" for a cybersecurity Solutions Engineer (SE). It reads raw meeting transcripts and turns them into structured, trustworthy account summaries that get written back to Google Docs.

**The core loop, in plain English:**
1. You have a customer meeting. Granola (or sync) records it; ingestion saves **one dated transcript file per meeting** under that customer’s `Transcripts/` folder.
2. You run a trigger phrase in Cursor (e.g. `Update Customer Notes for Acme`).
3. The AI loads **call records + index** (and only the raw `.txt` needed for quotes), uses domain tools for recommendations, and proposes updates as **mutation JSON**.
4. You review and approve the proposed changes.
5. **MCP + Python** apply approved changes to your Google Doc and append the history ledger / audit log.

**What makes v2.0 better than v1:**
- **Transcripts:** Raw audio/text is stored **one meeting per file** — dated, titled `.txt` under each customer’s `Transcripts/` folder — so the model is not forced to load multi-call rolling masters truncated at a byte cap. **Call records** (structured JSON per meeting) plus **`transcript-index.json`** are the default inputs for reasoning.
- **Reasoning vs execution:** The LLM reads, reasons, and outputs **structured plans** (including **Google Doc mutation JSON**). **Approved** MCP tools run Python that performs file I/O and Google APIs — the LLM never calls the Docs API or writes customer files directly.
- **Workflows:** Specialized sub-agents handle domains (security ops, app security, vulnerability management, attack surface, AI/ML security) instead of one monolithic prompt.
- **Journey:** The system tracks the full customer journey over time: where they started, what challenges they have, what got resolved, and what value was delivered.

---

## 2. Core Architectural Rules

These rules must never be violated. The planner should refuse any task that breaks them.

**Rule 1 — Python executes, AI proposes (including GDoc mutations).**
The LLM reads, analyzes, and produces **structured output** — including **mutation JSON** that conforms to `doc-schema.yaml` and `docs/ai/references/customer-notes-mutation-rules.md` (once ported). **Only after explicit user approval** may an agent invoke MCP tools that mutate external or customer state. Python (via MCP: `write_doc`, `append_ledger` / `append_ledger_v2`, call-record tools, etc.) performs **all** file writes, date calculations, and **Google Docs/Drive API** calls. **Never** instruct the model to paste content into the live Doc as a substitute for the mutation pipeline.

**Rule 2 — No transcript context flooding.**
Primary path: load **`transcript-index.json`**, then only the **call record JSON** files needed for the task. **Optional:** load **at most one** per-call raw `.txt` transcript file when a quote or boundary check requires verbatim text — each file represents **one meeting**, so there is no v1-style “many calls in one 50KB slice.” Do **not** load legacy `_MASTER_TRANSCRIPT_*.txt` wholesale into context during normal workflows; if a master file still exists during migration, treat it as **ingestion/source only** until split into per-call files.

**Rule 3 — User approves before any write.**
Every MCP tool that mutates data (writes to GDoc, appends ledger, writes call records) must be preceded by a human-readable summary of the proposed changes. The user must explicitly approve before the write tool is called.

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
- **Granola / sync:** `scripts/granola-sync.py` (or a dedicated follow-on step documented in `docs/MIGRATION_GUIDE.md`) is responsible for **emitting or splitting** content into these per-call files. During transition, `_MASTER_TRANSCRIPT_[Customer].txt` may still exist as a **Granola append target**; the extractor or a maintenance playbook should **prefer per-call files** once present.
- **Call record link:** Each call record’s `raw_transcript_ref` field points to the **basename** of that per-call `.txt` file (see §7.1).

### Google Doc mutation path (authoritative)

1. Agents load **read-only** context (MCP `read_doc`, call records, ledger, etc.).
2. The orchestrator / advisors produce a **mutation JSON** payload (same semantic contract v1 used: sections, fields, actions per schema).
3. **User approval** in chat.
4. **`write_doc`** MCP tool runs `custom-notes-agent/update-gdoc-customer-notes.py` with `--mutations` (and `dry_run` first when appropriate).

**Deprecated in v2:** MCP tool **`run_pipeline`** (`custom-notes-agent/run-main-task.py` YAML section runner) is **not** part of the v2 architecture. Do not port it as a supported tool. Historical playbooks that referenced it remain **reference only** under §12.

### Ledger writes: `append_ledger` vs `append_ledger_v2`

- **Before TASK-011:** Use **`append_ledger`** (v1 row shape) after successful `write_doc` when ledger v2 is not yet available.
- **After TASK-011:** Prefer **`append_ledger_v2`** for new rows (extended columns: call type, challenge lifecycle summaries, value, stakeholders). Keep **`append_ledger`** implemented for **backward compatibility**, fixture tests, and migration until `docs/MIGRATION_GUIDE.md` declares a customer migrated.
- **TASK-017** orchestrator step 9 should use **`append_ledger_v2`** once TASK-011 is complete.

---

## 3. Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Python runtime | `uv` package manager | Never use pip or conda. Always `uv run` or `uv add`. |
| Python version | 3.12.3+ | Set in pyproject.toml |
| MCP server | `fastmcp >= 3.2.0` | **prestonotes** MCP: customer paths, GDoc I/O, ledger, sync, call records |
| Wiz product search (Stage 3–4 bridge) | **wiz-local** (separate MCP server) | v1 pattern: domain advisors call **`wiz_search_wiz_docs`** (or equivalent) on the Wiz docs MCP until **TASK-021** `wiz_knowledge_search` (Chroma) replaces direct search |
| Testing | `pytest` | Write tests before code (TDD) |
| Python linter | `ruff` | Run before every task is marked complete |
| JS linter | `biome` | For any `.js` or `.ts` files only |
| AI orchestration | Cursor agents + `.mdc` rules | Primary reasoning — **no Anthropic key required** for the default Cursor-driven flows; Stage 4 embedding/RAG may require keys where noted |
| Document format | Markdown (`.md`) for local files | Google Docs for customer-facing content (via MCP + `custom-notes-agent`) |
| Vector DB | ChromaDB | Stage 4 only — not needed until API keys available |

### MCP tools and resources (prestonotes server)

**Read tools (non-exhaustive; mirror v1 after TASK-002):** `check_google_auth`, `list_customers`, `get_customer_status`, **`discover_doc`**, **`read_doc`**, `read_transcripts`, `read_ledger`, `read_audit_log`, `check_product_intelligence`, plus Stage 1+ tools as they land (`read_call_records`, `read_transcript_index`, …).

**Write / sync tools (TASK-003+):** `write_doc`, `append_ledger`, `append_ledger_v2` (after TASK-011), `log_run`, `sync_notes`, `sync_transcripts`, `bootstrap_customer`, call-record and journey tools per backlog.

**MCP resources to port** (same URIs as v1 so agents and tests share one source of truth): `prestonotes://config/doc-schema`, `prestonotes://config/section-sequence`, `prestonotes://config/task-budgets`, `prestonotes://prompts/persona`, `prestonotes://prompts/lens`. Payloads are read from files under `custom-notes-agent/config/` after port.

**Not ported for v2:** `run_pipeline` (see Rule 7 follow-on “Deprecated in v2”).

---

## 4. Directory Structure

```
prestonotes/                          ← new v2 repo root
├── .cursor/
│   ├── agents/                       ← AI agent personas (planner, coder, qa, doc)
│   ├── rules/                        ← Runtime rules applied to every session
│   │   ├── 00-core-execution.mdc     ← Non-negotiable guardrails
│   │   ├── 10-task-router.mdc        ← Routes trigger phrases to playbooks
│   │   ├── 15-user-preferences.mdc   ← Output format preferences
│   │   ├── 20-orchestrator.mdc       ← Main workflow orchestration (built in Stage 3)
│   │   ├── 21-extractor.mdc          ← Per-call extraction logic (built in Stage 1)
│   │   ├── 22-journey-synthesizer.mdc ← Journey timeline builder (built in Stage 2)
│   │   ├── 23-domain-advisor-soc.mdc ← Security operations advisor (Stage 3)
│   │   ├── 24-domain-advisor-app.mdc ← Application security advisor (Stage 3)
│   │   ├── 25-domain-advisor-vuln.mdc ← Vulnerability management advisor (Stage 3)
│   │   ├── 26-domain-advisor-asm.mdc  ← Attack surface advisor, image-aware (Stage 3)
│   │   ├── 27-domain-advisor-ai.mdc   ← AI/ML security advisor (Stage 3)
│   │   └── ai_learnings.mdc          ← Dynamic correction patches (port from old project)
│   └── skills/
│       ├── lint.sh                   ← Runs ruff (Python) and biome (JS) linters
│       └── test.sh                   ← Runs pytest on the prestonotes_mcp/ package
│
├── custom-notes-agent/               ← PORT from v1: GDoc client, bootstrap, YAML schema, prompts
│   ├── update-gdoc-customer-notes.py
│   ├── 000-bootstrap-gdoc-customer-notes.py
│   └── config/                       ← doc-schema.yaml, sections, prompts, task-budgets, tools.json, …
│
├── docs/
│   ├── project_spec.md               ← THIS FILE — master specification
│   ├── MIGRATION_GUIDE.md            ← Maps old files → new files (for planner reference)
│   ├── tasks/
│   │   ├── INDEX.md                  ← Master list of all tasks (backlog + archive links)
│   │   ├── active/                   ← One task file per in-progress task
│   │   └── archive/YYYY-MM/          ← Completed tasks moved here
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
│   └── .env.example                  ← Template for environment variables
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
├── MyNotes/                          ← Local customer data (git-ignored)
│   └── Customers/
│       └── [CustomerName]/
│           ├── [CustomerName] Notes.md    ← GDoc export (read-only for AI)
│           ├── Transcripts/
│           │   ├── YYYY-MM-DD-[title].txt ← v2: one file per meeting (canonical raw transcript)
│           │   └── _MASTER_TRANSCRIPT_[CustomerName].txt  ← legacy / Granola target during migration (optional)
│           ├── call-records/              ← NEW: per-call structured JSON (Stage 1)
│           │   ├── 2026-01-10-discovery-1.json
│           │   └── 2026-02-05-technical_deep_dive-2.json
│           ├── transcript-index.json      ← NEW: smart loading index (Stage 1)
│           └── AI_Insights/
│               ├── [CustomerName]-History-Ledger.md
│               ├── [CustomerName]-AI-AcctSummary.md
│               └── [CustomerName]-Journey-Timeline.md  ← NEW (Stage 2)
│
├── pyproject.toml                    ← uv package config, dependencies, tool settings
├── README.md                         ← Setup guide and quick-start
└── .gitignore                        ← Must include MyNotes/, prestonotes_mcp/.env, *.yaml (not .example)
```

**Naming note (TASK-001):** The repo may temporarily use `.cursor/rules/core.mdc` before numbered rules exist. **Target** is the `00-core-execution.mdc` … `27-domain-advisor-ai.mdc` layout above; migrate without losing content when renaming.

---

## 5. How the Agents Work

The project uses four specialized agents in a strict pipeline. The planner owns the process; the others only execute when delegated to.

```
User → @planner → (creates task file, gets approval)
                → @coder   (writes tests first, then code)
                → @qa      (runs tests + linters, fixes issues)
                → @doc     (updates README and docs after QA passes)
                → User (reports task complete)
```

**@planner** — The orchestrator. Reads this spec before every task. Creates one task file per request in `docs/tasks/active/`. Always asks for user approval before code changes. Never writes code directly.

**@coder** — Reads only the assigned task file and this spec. Writes a failing test first (TDD), then writes the implementation. Runs linters. Updates the task file status when done.

**@qa** — Runs `test.sh` and `lint.sh`. Fixes failures up to 3 times. Reports blockers to planner if it can't fix them.

**@doc** — Runs only after QA passes. Updates README.md and any affected docs to reflect what was actually built.

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
                              transcript-index.json
                                         ↓
                              [MCP] write_call_record
                              [MCP] update_transcript_index

[Stage 2 — Journey Intelligence]
call-records/*.json + History-Ledger.md + AcctSummary.md
                                         ↓
                              22-journey-synthesizer.mdc (Cursor)
                                         ↓
                              [CustomerName]-Journey-Timeline.md
                              Enhanced History Ledger (with lifecycle states)
                                         ↓
                              [MCP] write_journey_timeline
                              [MCP] update_challenge_state
                              [MCP] append_ledger_v2

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
                              [MCP] append_ledger_v2
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
    { "id": "ch-001", "description": "No unified cloud visibility across AWS and Azure", "status": "identified" }
  ],
  "products_discussed": ["Wiz Cloud"],
  "action_items": [
    { "owner": "SE", "action": "Send architecture overview", "due": "2026-04-22" }
  ],
  "sentiment": "positive",
  "deltas_from_prior_call": [],
  "verbatim_quotes": [
    { "speaker": "Jane Smith", "quote": "We have no idea what's running in our cloud environments." }
  ],
  "raw_transcript_ref": "2026-04-15-discovery-call-with-acme.txt",
  "extraction_date": "2026-04-16",
  "extraction_confidence": "high"
}
```

### 7.2 Transcript Index
Stored at: `MyNotes/Customers/[Name]/transcript-index.json`

```json
{
  "customer": "Acme Corp",
  "last_rebuilt": "2026-04-16",
  "total_calls": 3,
  "calls": [
    {
      "call_id": "2026-04-15-discovery-1",
      "date": "2026-04-15",
      "call_type": "discovery",
      "call_number": 1,
      "summary_one_liner": "First discovery call...",
      "record_file": "call-records/2026-04-15-discovery-1.json",
      "indexed": true
    }
  ],
  "unindexed_transcript_chunks": []
}
```

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

The old project lives at `../prestoNotes.orig` (relative to the new repo root). It is read-only reference material. The planner must consult this guide before building any task that involves porting code.

**Critical fact:** In v1, MCP **`write_doc`**, **`read_doc`**, **`discover_doc`**, **`append_ledger`**, and **`bootstrap_customer`** already delegate to **`custom-notes-agent/`** Python entrypoints. v2 **ports that package in-tree** (supported subset: everything those subprocesses and `uv run` paths require, including **`config/`** YAML/MD prompts, **`sections/`** Python if imported by `update-gdoc-customer-notes.py` or `run-main-task.py`, and tests under `custom-notes-agent/test/` as needed for regression). **`docs/MIGRATION_GUIDE.md`** must list the exact file list once the first green CI port exists.

**What to port vs. what to drop vs. reference-only:**

| Old File / area | Action | Notes |
|---|---|---|
| `prestonotes_mcp/server.py` | Port — strip hardcoded paths | Keep FastMCP structure, tool signatures, security patterns; **omit** `run_pipeline` registration for v2 |
| `prestonotes_mcp/config.py` | Port | Env + yaml resolution |
| `prestonotes_mcp/exec_helper.py` | Port | `run_uv_script`, `run_shell_script`, repo root |
| `prestonotes_mcp/runtime.py` | Port | `init_ctx`, `get_ctx` |
| `prestonotes_mcp/security.py` | Port | `validate_customer_name`, path scope, mutation size checks |
| `prestonotes_mcp/prestonotes-mcp.yaml.example` | Port — update paths | Document `MYNOTES_ROOT_FOLDER_ID`, `GDRIVE_BASE_PATH`, etc. |
| MCP **resources** in `server.py` | Port | `prestonotes://config/*`, `prestonotes://prompts/*` → read from ported `custom-notes-agent/config/` |
| `custom-notes-agent/update-gdoc-customer-notes.py` | **Port in-tree** | GDoc discover/read/write + ledger-append implementation |
| `custom-notes-agent/000-bootstrap-gdoc-customer-notes.py` | **Port in-tree** | `bootstrap_customer` MCP |
| `custom-notes-agent/config/` (doc-schema, sections, prompts, task-budgets, tools.json, …) | **Port in-tree** | Ground truth for mutations and MCP resources |
| `custom-notes-agent/sections/*.py` | Port **if** required by imported graph | `run-main-task.py` section builders are **not** used when `run_pipeline` is removed; keep only modules still imported by the GDoc client |
| `custom-notes-agent/run-main-task.py` | **Do not expose via MCP** | Optional: copy into `docs/examples/` or rely on `../prestoNotes.orig` for archaeology only |
| `scripts/granola-sync.py` | Port — **extend** for v2 | Must support (or delegate to a helper that produces) **per-call** `Transcripts/YYYY-MM-DD-[title].txt` layout per §2; preserve idempotency and Internal-folder routing from v1 tests |
| `scripts/rsync-gdrive-notes.sh` | Port | Bidirectional sync |
| `scripts/syncNotesToMarkdown.js` | Port | GDoc → Markdown export |
| `scripts/restart-google-drive.sh` | Port | Drive for Desktop restart helper |
| `scripts/wiz_doc_cache_manager.py` | Port / reference | Stage 4 ingestion input |
| `scripts/ci/check-repo-integrity.sh` | Port — update manifest | Include `custom-notes-agent/` and new v2 paths |
| `pyproject.toml` | Port — bump **2.0.0** | Align deps with `uv lock` |
| `.cursor/rules/ai_learnings.mdc` | Port | Corrections layer |
| `.cursor/rules/15-user-preferences.mdc` | Port | Output prefs |
| `.cursor/rules/00-core-execution.mdc` | Rebuild from v1 | v2 paths, per-call transcript rules |
| `docs/ai/playbooks/run-logic-audit.md` | Port | Read-only QA |
| `docs/ai/playbooks/run-license-evidence-check.md` | Port | Commercial |
| `docs/ai/playbooks/run-bva-report.md` | Port | BVA |
| `docs/ai/playbooks/load-customer-context.md` | Port — update paths | Session prep |
| `docs/ai/references/customer-notes-mutation-rules.md` | Port | **Required** for mutation JSON quality |
| `docs/ai/references/account-summary-format-spec.md` | Port — review | Align with exec summary template (TASK-013) |
| `docs/ai/references/value-realization-taxonomy.md` | Port | Value language |
| `docs/ai/playbooks/update-customer-notes.md` | **Reference / archive** | Superseded by **TASK-017** orchestrator; keep for diffing prompt behavior during Stage 3 |
| `docs/ai/playbooks/build-product-intelligence.md` | Reference — post-MVP | Do not block MVP on this pattern; use wiz-local MCP search per §3 |

---

## 9. Master Task Backlog

Tasks are organized into four stages. Build them in order — each stage depends on the previous one. **The planner should build exactly one task at a time.** When you finish a task, the planner moves its file to `docs/tasks/archive/YYYY-MM/` and the user picks the next task from this list.

### Stage 1 — Foundation (Build the pipeline from transcript → structured record)

**Goal of Stage 1:** Ingest **per-call transcript files**, build **call records** + **transcript index**, and prove end-to-end extraction without using multi-call master files as the primary AI context.

---

**TASK-001 — Scaffold the repo**
- **What it builds:** The directory structure, `pyproject.toml`, `.gitignore`, `README.md` skeleton, `docs/MIGRATION_GUIDE.md` (stub OK), and placeholder dirs: `prestonotes_mcp/`, `custom-notes-agent/` (empty or README-only until TASK-003), `docs/ai/playbooks/`, `docs/ai/references/`.
- **Why it matters:** Nothing else can be built until the repo skeleton is correct.
- **Reference from old project:** `../prestoNotes.orig/pyproject.toml` for dependencies. Bump version to `2.0.0`.
- **Test:** Run `python -c "import prestonotes_mcp"` — should import without error. Run `scripts/ci/check-repo-integrity.sh` — should pass.
- **Files created:** `pyproject.toml`, `README.md`, `.gitignore`, `docs/project_spec.md` (this file), `docs/MIGRATION_GUIDE.md`, `docs/tasks/INDEX.md`, `.cursor/skills/lint.sh`, `.cursor/skills/test.sh`, `scripts/ci/check-repo-integrity.sh`, `scripts/ci/required-paths.manifest` (include **`custom-notes-agent/`** once populated).

---

**TASK-002 — Port the MCP server (read-only tools only)**
- **What it builds:** A working FastMCP server with **all** safe read-only tools from v1: `check_google_auth`, `list_customers`, `get_customer_status`, **`discover_doc`**, **`read_doc`**, `read_transcripts`, `read_ledger`, `read_audit_log`, `check_product_intelligence`. **`read_doc` / `discover_doc`** require the **`custom-notes-agent`** port (TASK-003 dependency order: either merge TASK-002+003 in one PR or stub discover/read until the agent exists — planner choice). Register **MCP resources**: `prestonotes://config/doc-schema`, `prestonotes://config/section-sequence`, `prestonotes://config/task-budgets`, `prestonotes://prompts/persona`, `prestonotes://prompts/lens`.
- **Why it matters:** This is the foundation that all AI tools call. Stage 2/3 cannot load structured GDoc state without **`read_doc`**. Resources keep one canonical copy of schema/budgets/prompts.
- **`read_transcripts` behavior (v2):** Implement as “latest **N transcript files**” (newest mtime first) from `Transcripts/*.txt`, **excluding** or deprioritizing `_MASTER_*.txt` once per-call files exist; optional per-file byte cap for safety. Document default `N` and cap in `prestonotes-mcp.yaml.example`.
- **Reference from old project:** `../prestoNotes.orig/prestonotes_mcp/server.py` (read tools + resource block). Port `config.py`, `exec_helper.py`, `runtime.py`, `security.py`. Strip hardcoded personal paths. **Do not** register `run_pipeline`.
- **Test:** Run `uv run python -m prestonotes_mcp` — server should start. Run `pytest prestonotes_mcp/tests/test_server_read_tools.py` — at least `check_google_auth` returns valid JSON; **`read_doc`** with a fixture or mocked subprocess if needed.
- **Files created:** `prestonotes_mcp/server.py`, `prestonotes_mcp/config.py`, `prestonotes_mcp/exec_helper.py`, `prestonotes_mcp/runtime.py`, `prestonotes_mcp/security.py`, `prestonotes_mcp/__init__.py`, `prestonotes_mcp/__main__.py`, `prestonotes_mcp/prestonotes-mcp.yaml.example`, `prestonotes_mcp/.env.example`, `prestonotes_mcp/tests/test_server_read_tools.py`.

---

**TASK-003 — Port the write/sync tools to MCP server**
- **What it builds:** The mutation MCP tools: `write_doc`, `append_ledger`, `log_run`, `sync_notes`, `sync_transcripts`, `bootstrap_customer` — same subprocess contracts as v1, targeting **in-repo** `custom-notes-agent/` (TASK-001 / companion task must land the ported tree first). **`run_pipeline` is intentionally omitted** from v2 (see §2).
- **Why it matters:** These tools apply approved changes. **Mutation path:** Cursor agents produce **mutation JSON** → user approves → **`write_doc`** runs Python (`update-gdoc-customer-notes.py write --mutations …`). **`append_ledger`** runs the v1 `ledger-append` path after a successful write. Nothing writes customer or Google state without MCP + approval.
- **Reference from old project:** `../prestoNotes.orig/prestonotes_mcp/server.py` (write/sync section). Preserve `check_mutation_json_size` and temp mutation file behavior.
- **Test:** `pytest prestonotes_mcp/tests/test_server_write_tools.py` — test `bootstrap_customer` with `dry_run=True` (never `dry_run=False` in CI). Test `append_ledger` against a fixture file. Test `write_doc` with `dry_run=True` and minimal valid mutations JSON.
- **Files modified:** `prestonotes_mcp/server.py` (add write tools). `prestonotes_mcp/tests/test_server_write_tools.py` (new). **`custom-notes-agent/`** tree per §8.

---

**TASK-004 — Add the call record MCP tools**
- **What it builds:** Four new MCP tools that do NOT exist in the old project: `write_call_record`, `read_call_records`, `update_transcript_index`, `read_transcript_index`.
- **Why it matters:** These tools are the bridge between raw transcripts and structured AI reasoning. Without them, the extractor has nowhere to save its output.
- **What each tool does:**
  - `write_call_record(customer_name, call_id, record_json)` → validates the JSON matches the call record schema, writes to `MyNotes/Customers/[Name]/call-records/[call_id].json`
  - `read_call_records(customer_name, since_date=None, call_type=None)` → returns list of call records matching filters
  - `update_transcript_index(customer_name)` → rebuilds `transcript-index.json` by scanning `call-records/` directory
  - `read_transcript_index(customer_name)` → returns the index JSON
- **Test:** `pytest prestonotes_mcp/tests/test_call_record_tools.py` — write a call record, read it back, update the index, verify the index reflects the written record.
- **Files modified:** `prestonotes_mcp/server.py`. New: `prestonotes_mcp/tests/test_call_record_tools.py`.

---

**TASK-005 — Port the granola-sync script**
- **What it builds:** `scripts/granola-sync.py` — reads new meetings from the Granola app cache. **v2 requirement:** emit or split transcripts into **per-call** `Transcripts/YYYY-MM-DD-[title].txt` files per §2 (while preserving v1 behaviors: idempotency, Internal-folder routing). If Granola only yields combined text in one pass, document a **second step** (same script phase or `scripts/split-master-transcript.py`) in `docs/MIGRATION_GUIDE.md` so no planner task invents behavior ad hoc.
- **Why it matters:** First data ingestion; without it there are no raw inputs for the extractor.
- **Reference from old project:** `../prestoNotes.orig/scripts/granola-sync.py` — port logic, replace hardcoded paths with config/env.
- **Test:** `pytest scripts/tests/test_granola_sync.py` — idempotency; Internal routing; **when per-call mode is enabled**, assert one output file per meeting fixture (define fixtures in the test plan).
- **Files created:** `scripts/granola-sync.py`, `scripts/run-granola-sync.sh`, `scripts/tests/test_granola_sync.py`.

---

**TASK-006 — Port the rsync and GDrive sync scripts**
- **What it builds:** `scripts/rsync-gdrive-notes.sh`, `scripts/restart-google-drive.sh`, `scripts/syncNotesToMarkdown.js`.
- **Why it matters:** These scripts keep the local `MyNotes/` folder in sync with Google Drive. The AI reads from local files; Google Drive is the source of truth for the GDoc.
- **Reference from old project:** Port all three unchanged. They work as-is.
- **Test:** Run `bash scripts/rsync-gdrive-notes.sh --dry-run` — should print what it would sync without making changes.
- **Files created:** `scripts/rsync-gdrive-notes.sh`, `scripts/restart-google-drive.sh`, `scripts/syncNotesToMarkdown.js`.

---

**TASK-007 — Port the cursor rules and ai_learnings**
- **What it builds:** Runtime `.mdc` rules: `00-core-execution.mdc` (or merge into existing `core.mdc` until renamed), `15-user-preferences.mdc`, `ai_learnings.mdc`. **MVP playbooks** (prompt logic references for v2 rebuild): `load-customer-context.md`, `run-logic-audit.md`, `run-license-evidence-check.md`, `run-bva-report.md`. Additional long-form playbooks from v1 live under **§12 post-MVP** unless explicitly promoted into MVP by the user.
- **Why it matters:** Rules + a small playbook set establish guardrails and repeatable read-only checks before write paths exist.
- **Reference from old project:** `../prestoNotes.orig/.cursor/rules/` and `../prestoNotes.orig/docs/ai/playbooks/`. Update paths for v2 repo layout and per-call transcripts.
- **Test:** Create `MyNotes/Customers/TestCo/` skeleton. Run `Load Customer Context for TestCo`. Verify correct files and no accidental `_MASTER_` full-file load unless intentional.
- **Files created:** `.cursor/rules/00-core-execution.mdc` (or equivalent), `.cursor/rules/15-user-preferences.mdc`, `.cursor/rules/ai_learnings.mdc`, MVP playbooks under `docs/ai/playbooks/`.

---

**TASK-008 — Build the extractor .mdc rule and playbook**
- **What it builds:** `21-extractor.mdc` (the AI rule) and `docs/ai/playbooks/extract-call-records.md` (the trigger playbook). Also creates reference doc `docs/ai/references/call-type-taxonomy.md`.
- **Why it matters:** This is the first real intelligence step. The extractor reads **one per-call** raw `.txt` (or a bounded excerpt) and produces structured per-call JSON — the piece that replaces loading **multi-call** master transcripts into context.
- **What the extractor does:**
  1. Accept: **one** per-call transcript file (path or MCP-fetched content) + customer name + number of calls already recorded
  2. Detect meeting boundaries in the text (look for date stamps, attendee lists, meeting titles)
  3. For each meeting found: classify the call type, extract all fields from the call record schema (section 7.1), compute sentiment, extract up to 3 verbatim quotes
  4. Output: one JSON object per meeting
  5. Call `write_call_record` MCP tool for each, then `update_transcript_index`
- **Trigger phrase:** `Extract Call Records for [CustomerName]`
- **Test (manual):** Run the trigger on a customer with known meeting history. Verify the number of call records created matches the number of distinct meetings in the transcript. Verify call types are correctly classified. Verify participant names and dates are accurate.
- **Files created:** `.cursor/rules/21-extractor.mdc`, `docs/ai/playbooks/extract-call-records.md`, `docs/ai/references/call-type-taxonomy.md`.

---

**TASK-009 — Bootstrap a real customer and run end-to-end Stage 1 test**
- **What it builds:** A test runbook at `docs/ai/playbooks/test-call-record-extraction.md`. No new code — this is a validation task.
- **Why it matters:** Stage 1 is only "done" when you can extract call records from a real customer's transcripts, verify the records are accurate, and confirm the transcript index is correct.
- **What to do:**
  1. Run `bootstrap_customer` MCP tool for your real test customer (creates the folder structure)
  2. Run `Extract Call Records for [CustomerName]`
  3. Run `Test Call Record Extraction for [CustomerName]` (the new test playbook)
  4. Review output: does each call record match what you remember from the meetings?
  5. Manually fix any wrong call types or missing participants
- **Test:** The test playbook produces a coverage report: "X of Y meetings indexed. Confidence distribution: high/medium/low."
- **Files created:** `docs/ai/playbooks/test-call-record-extraction.md`.

---

### Stage 2 — Journey Intelligence (Build the customer story)

**Goal of Stage 2:** Produce the Journey Timeline artifact. Make the system tell the "story" of the customer from call 1 to today. Improve the exec summary format. Track challenges through their lifecycle.

---

**TASK-010 — Add journey timeline and challenge lifecycle MCP tools**
- **What it builds:** Two new MCP tools: `write_journey_timeline(customer_name, content)` and `update_challenge_state(customer_name, challenge_id, new_state, evidence)`.
- **Why it matters:** The journey timeline is the core new artifact in v2. The challenge lifecycle tool lets Python track state transitions with evidence, so the AI can't accidentally "lose" a challenge's history.
- **Test:** `pytest prestonotes_mcp/tests/test_journey_tools.py` — write a journey timeline, read it back. Update a challenge state from `identified` to `in_progress`, verify the transition is logged with a date and evidence reference.
- **Files modified:** `prestonotes_mcp/server.py`. New: `prestonotes_mcp/tests/test_journey_tools.py`.

---

**TASK-011 — Extend the ledger schema for challenge lifecycle**
- **What it builds:** A new MCP tool `append_ledger_v2` that extends the history ledger with new columns: `call_type`, `challenges_in_progress`, `challenges_resolved`, `value_realized`, `key_stakeholders`. Also a Python migration script for existing customers' ledgers.
- **Why it matters:** The history ledger is the persistent state of an account over time. Adding challenge lifecycle and value columns gives the journey narrative its raw data.
- **Reference from old project:** `../prestonotes_mcp/server.py` — the existing `append_ledger` tool. The new v2 version adds columns but must be backward compatible with existing ledger rows.
- **Test:** `pytest prestonotes_mcp/tests/test_ledger_v2.py` — write a v2 ledger row, read it back, verify all new columns persist correctly. Run migration script on a fixture ledger file, verify old rows are preserved unchanged.
- **Files modified:** `prestonotes_mcp/server.py`. New: `prestonotes_mcp/tools/migrate_ledger.py`, `prestonotes_mcp/tests/test_ledger_v2.py`.

---

**TASK-012 — Build the journey synthesizer rule and playbook**
- **What it builds:** `22-journey-synthesizer.mdc` and `docs/ai/playbooks/run-journey-timeline.md`. Also creates `docs/ai/references/challenge-lifecycle-model.md` and `docs/ai/references/health-score-model.md`.
- **Why it matters:** This produces the "story of the account" — the core new value in v2. It takes all call records, traces how challenges evolved, and writes a narrative humans actually want to read.
- **What the synthesizer does:**
  1. Read all call records from `transcript-index.json`
  2. Build a chronological timeline of all calls
  3. Identify milestone events (first call, first win, POC start, commercial discussion)
  4. Trace each challenge from `identified` → current state
  5. Build a stakeholder evolution map (who joined, who left)
  6. Compile "value realized" entries from all call records
  7. Write the opening 2-3 sentence narrative (the "story arc" for a VP audience)
  8. Produce the Journey Timeline markdown (schema in section 7 of the v2 design plan)
  9. Call `write_journey_timeline` MCP tool
- **Trigger phrase:** `Run Journey Timeline for [CustomerName]`
- **Health score model:**
  - 🟢 Green: Active engagement, no stalled challenges, positive sentiment, clear next steps
  - 🟡 Yellow: One of: stalled challenge, missed follow-up, cautious sentiment, unclear next step
  - 🔴 Red: Two or more yellow signals, or: champion departure, competitive threat, budget lost
  - ⚪ Unknown: Fewer than 2 calls or no recent data
- **Test (manual):** Run on a customer with 5+ calls. Verify: timeline has the right number of entries, challenge lifecycle states match what you know happened, value realized section has at least one entry if applicable, health score is correct.
- **Files created:** `.cursor/rules/22-journey-synthesizer.mdc`, `docs/ai/playbooks/run-journey-timeline.md`, `docs/ai/references/challenge-lifecycle-model.md`, `docs/ai/references/health-score-model.md`.

---

**TASK-013 — Build the exec summary template and enhanced account summary playbook**
- **What it builds:** `docs/ai/references/exec-summary-template.md` and updates `docs/ai/playbooks/run-account-summary.md` to produce an exec summary following the new template.
- **Why it matters:** The old account summary was single-pass with no clear structure. The new one has a defined template with specific sections that a VP can read in 30 seconds.
- **Exec summary template structure:**
  - **The 30-Second Brief** — 1 paragraph: who they are, what problem they have, where they are in the journey, what the next move is. Written for a VP — no jargon.
  - **Challenges → Solutions Map** — Table: Challenge | Wiz Capability | Status | Value Delivered
  - **Stakeholders** — Table: Name | Role | Champion? | Sentiment | Last Contact
  - **Value Realized** — Concrete outcomes with dates and evidence
  - **Strategic Position** — Current journey state, risk factors, next logical move
  - **Wiz Commercials** — License evidence table
  - **Open Challenges** — Challenges still `identified` or `stalled`
- **Test (manual):** Run `Run Account Summary for [CustomerName]`. Compare the output to the old account summary. Verify: 30-second brief is ≤ 3 sentences and has no jargon, challenges table is populated, stakeholders table has sentiment signals.
- **Files created:** `docs/ai/references/exec-summary-template.md`. Modified: `docs/ai/playbooks/run-account-summary.md`.

---

**TASK-014 — Build the challenge review playbook**
- **What it builds:** `docs/ai/playbooks/run-challenge-review.md`.
- **Why it matters:** As accounts grow (10+ calls), challenges pile up. This playbook gives a quick way to review all challenges, flag ones that are stalled, and propose state transitions.
- **Trigger phrase:** `Run Challenge Review for [CustomerName]`
- **What it produces:** A table of all challenges with their current state, last-updated date, evidence, and a recommended action (e.g., "follow up — stalled 65 days").
- **Test (manual):** Run on a customer with at least 3 challenges. Verify: all challenges are listed, stalled challenges are correctly flagged, at least one recommended action is sensible.
- **Files created:** `docs/ai/playbooks/run-challenge-review.md`.

---

### Stage 3 — Domain Advisors (Split the monolithic update into specialized passes)

**Goal of Stage 3:** Replace the old `Update Customer Notes` playbook with the new orchestrated flow: extractor → domain advisors (sequential) → writer. Each domain advisor knows one area deeply.

---

**TASK-015 — Build the SOC domain advisor (implement first)**
- **What it builds:** `23-domain-advisor-soc.mdc` — the **first** domain advisor shipped to prove the pattern. **TASK-016** must still deliver APP, VULN, ASM, and AI advisors; SOC-first is **sequencing**, not a scope cut.
- **Why it matters:** Security Operations is the most common domain for Wiz conversations; fastest feedback loop for orchestrator integration.
- **What the SOC advisor does:**
  1. Receive: `CustomerStateUpdate.json` (the delta output from the extractor — contains challenges, gaps, current stack)
  2. Look up relevant Wiz docs using the **Wiz docs MCP (wiz-local)** product search tool (same role as v1 `wiz_search_wiz_docs` / server-specific name — configure in Cursor MCP settings)
  3. For each gap or challenge that relates to threat detection, incident response, or runtime security: produce a 2-3 sentence recommendation linking the gap to a specific Wiz capability
  4. Output: structured JSON with `domain: "soc"`, `gaps_analyzed`, `recommendations[]`, `no_match_gaps[]`
- **Test (manual):** Give the advisor a `CustomerStateUpdate.json` with at least one SOC-related gap (e.g., "no runtime threat detection"). Verify: recommendation references a specific Wiz capability, includes a docs link, has a confidence score.
- **Files created:** `.cursor/rules/23-domain-advisor-soc.mdc`.

---

**TASK-016 — Build the remaining domain advisors (required scope)**
- **What it builds:** `24-domain-advisor-app.mdc`, `25-domain-advisor-vuln.mdc`, `26-domain-advisor-asm.mdc` (image-aware), `27-domain-advisor-ai.mdc`. All follow the same contract as TASK-015 (input `CustomerStateUpdate.json`, product lookup via **wiz-local MCP** until TASK-021, structured JSON out).
- **Why it matters:** Full-domain coverage is a **v2 architecture commitment**; SOC alone is insufficient for production account updates across mixed engagements.
- **Special note for ASM advisor (26):** This one also accepts `architecture_diagram_paths` from `CustomerStateUpdate.json`. If diagram image files exist in the customer folder, the advisor reads them (as base64) and uses them to identify coverage gaps visible in the architecture topology.
- **Test (manual):** Run all five advisors on the same `CustomerStateUpdate.json`. Verify: no two advisors produce the same recommendations, ASM advisor references the diagram if one exists.
- **Files created:** `.cursor/rules/24-domain-advisor-app.mdc`, `.cursor/rules/25-domain-advisor-vuln.mdc`, `.cursor/rules/26-domain-advisor-asm.mdc`, `.cursor/rules/27-domain-advisor-ai.mdc`.

---

**TASK-017 — Build the main orchestrator rule and update the task router**
- **What it builds:** `20-orchestrator.mdc` (the main workflow rule) and updates `10-task-router.mdc` to route `Update Customer Notes for [Name]` to the orchestrator.
- **Why it matters:** This is the piece that ties everything together. The orchestrator runs the full pipeline: sync → load context → run extractor → run advisors (one by one) → compile proposed changes → get user approval → execute writes.
- **Orchestrator steps (in order):**
  1. Sync: call `sync_notes` and `sync_transcripts` MCP tools
  2. Load: read `transcript-index.json`, check for unindexed chunks, run extractor if needed
  3. Load: read account summary, last 5 ledger rows, last 10 audit log entries
  4. Determine scope: if new call records since last ledger row → full update; else → logic audit only
  5. Run extractor: pass only new call records + current state → receive `CustomerStateUpdate.json`
  6. Run advisors: SOC → APP → VULN → ASM → AI (sequential, each receives `CustomerStateUpdate.json`)
  7. Compile: merge extractor output + advisor recommendations into proposed GDoc mutations
  8. **STOP — present to user:** plain English summary of what will change, specific mutations, new ledger row
  9. Execute (only after approval): `write_doc`, `append_ledger_v2`, `write_journey_timeline`, `log_run`, `sync_notes`
- **Trigger phrase:** `Update Customer Notes for [CustomerName]`
- **Test (manual):** Run full orchestrator on a customer with one new call record. Verify: the proposed changes are accurate to the call, the user approval gate appears before any write, the GDoc and ledger are updated correctly after approval.
- **Files created:** `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/10-task-router.mdc`. Modified: archived old `update-customer-notes.md` playbook.

---

**TASK-018 — Build the exec briefing playbook**
- **What it builds:** `docs/ai/playbooks/run-exec-briefing.md`.
- **Why it matters:** Sometimes you need a quick 1-pager for a manager or executive — not the full account summary. This playbook produces exactly the exec summary section and nothing else.
- **Trigger phrase:** `Run Exec Briefing for [CustomerName]`
- **Test (manual):** Run on any customer. Output should fit on one page. No technical jargon. No internal notes.
- **Files created:** `docs/ai/playbooks/run-exec-briefing.md`.

---

**TASK-019 — Full end-to-end Stage 3 integration test**
- **What it builds:** A debug/test playbook at `docs/ai/playbooks/debug-pipeline.md`.
- **Why it matters:** Stage 3 is only "done" when the full orchestrated pipeline runs without errors and produces better output than the old monolithic playbook.
- **Test (manual):**
  1. Archive the old `update-customer-notes.md`
  2. Run `Update Customer Notes for [CustomerName]` with the new orchestrator
  3. Run `Run Logic Audit for [CustomerName]` to verify no data regressions
  4. Compare output quality to the last known good run from the old playbook
- **Files created:** `docs/ai/playbooks/debug-pipeline.md`.

---

### Stage 4 — RAG and Automation (Requires API Keys — Build When Ready)

**Goal of Stage 4:** Eliminate context flooding permanently. Automate data ingestion. Enable precise vector search over Wiz product docs.

**Note:** This stage requires **embedding-capable** credentials (e.g. Anthropic or another provider supported by the ingestion code) plus operational keys for any hosted vector dependency. Do not start Stage 4 until those are available. Until then, domain advisors use **wiz-local MCP** search (§3); **TASK-022** switches advisors to `wiz_knowledge_search` when Chroma is live.

---

**TASK-020 — Build the vector DB ingestion script**
- **What it builds:** `prestonotes_mcp/ingestion/build_vector_db.py` — a script that reads Wiz product docs from local markdown cache and ingests them into ChromaDB.
- **Why it matters:** Direct MCP search is good but imprecise — it returns whatever the search index finds. Vector search returns semantically similar content, which produces much more targeted recommendations.
- **Reference from old project:** `../prestoNotes.orig/scripts/wiz_doc_cache_manager.py` — shows how Wiz docs are cached locally.
- **Test:** `pytest prestonotes_mcp/tests/test_vector_db.py` — ingest 3 test documents, query with a semantic question, verify at least one returned result is topically relevant.
- **Files created:** `prestonotes_mcp/ingestion/build_vector_db.py`, `prestonotes_mcp/tests/test_vector_db.py`.

---

**TASK-021 — Add wiz_knowledge_search MCP tool**
- **What it builds:** A new MCP tool `wiz_knowledge_search(query, domain=None, max_results=5)` that queries ChromaDB and returns semantically relevant Wiz product doc snippets.
- **Why it matters:** After TASK-022, this replaces **wiz-local** direct search calls in domain advisors. Advisors get higher-quality context with less token usage.
- **Test:** `pytest prestonotes_mcp/tests/test_wiz_knowledge_search.py` — query "cloud posture management visibility gaps", verify results contain CSPM-relevant content.
- **Files modified:** `prestonotes_mcp/server.py`. New: `prestonotes_mcp/tests/test_wiz_knowledge_search.py`.

---

**TASK-022 — Update domain advisors to use vector search**
- **What it builds:** Updates each of the five domain advisor `.mdc` rules to call `wiz_knowledge_search` instead of direct MCP product search.
- **Why it matters:** Completes the migration to RAG-based product intelligence.
- **Test (manual):** Run `Run Tech Acct Plan for [CustomerName] SOC` with the updated SOC advisor. Compare recommendation quality and token usage to the pre-RAG version.
- **Files modified:** `.cursor/rules/23-domain-advisor-soc.mdc` through `27-domain-advisor-ai.mdc`.

---

## 10. Definition of Done

A task is only complete when ALL of the following are true:

1. **The feature works** — the "Test" section in the task backlog above is satisfied
2. **Tests pass** — `uv run pytest` exits with code 0
3. **Linters pass** — `ruff check prestonotes_mcp/ scripts/` exits with code 0
4. **Task file is complete** — the task file in `docs/tasks/active/` is marked `[x] COMPLETE` with evidence (test commands run, output summary)
5. **Docs are updated** — `README.md` reflects any new trigger phrases, tools, or setup steps introduced by the task
6. **Task is archived** — the task file is moved to `docs/tasks/archive/YYYY-MM/` and `docs/tasks/INDEX.md` is updated

---

## 11. Trigger Phrase Reference (MVP)

These triggers are **in scope for the v2 MVP** and map directly to tasks in §9. Wording in playbooks may vary slightly; the **task router** (`10-task-router.mdc`) is the source of truth for aliases.

| Trigger | What It Does | Stage |
|---|---|---|
| `Load Customer Context for [Customer]` | Read-only snapshot for session prep | 1 |
| `Extract Call Records for [Customer]` | Build/update **call-records** + **transcript-index** from per-call transcript files | 1 |
| `Test Call Record Extraction for [Customer]` | Manual QA / coverage report for extraction | 1 |
| `Run Logic Audit for [Customer]` | Read-only quality check — no writes | 1 |
| `Run License Evidence Check for [Customer]` | Commercial entitlement check | 1 |
| `Run BVA Report for [Customer]` | Business value assessment | 1 |
| `Run Journey Timeline for [Customer]` | Build or refresh **Journey-Timeline** artifact | 2 |
| `Run Account Summary for [Customer]` | Exec + detailed account summary (template-driven) | 2 |
| `Run Exec Briefing for [Customer]` | One-page exec summary | 2 |
| `Run Challenge Review for [Customer]` | Challenge table + stall signals | 2 |
| `Update Customer Notes for [Customer]` | Full orchestrated update: sync → extract → advisors → approval → **write_doc** / ledger / log | 3 |
| `Run Tech Acct Plan for [Customer] [Domain]` | **Single-domain** advisor pass (used to validate SOC-first, then others as their `.mdc` ship) | 3 |
| `Debug Pipeline for [Customer]` | Verbose troubleshooting playbook for Stage 3 integration | 3 |

---

## 12. MVP vs Post-MVP Playbooks

**MVP goal:** Ship the §11 triggers with **correct prompt logic** and MCP boundaries. **Do not** block MVP on porting every legacy playbook from `../prestoNotes.orig`.

**Post-MVP (reference / enhancement):** The following come from **v1** or earlier drafts and are **not** MVP commitments. Keep copies under `docs/ai/playbooks/archive/` or point to `../prestoNotes.orig/docs/ai/playbooks/` until selectively promoted:

| Legacy / extra trigger | Notes |
|---|---|
| `Run Full Account Rebuild for [Customer]` | Composed multi-step v1 workflow — **superseded** by orchestrator + explicit triggers when needed |
| `Run Step 9 Post-Seed Synthesis` / `Polish Account Summary` (and related) | Heavy **replace_field_entries** passes — reference `run-seeded-notes-replay.md` in orig |
| `build-product-intelligence` / deep doc-harvest flows | Revisit with **wiz-local** + Stage 4 RAG; avoid context flooding |
| Any playbook depending on **`run_pipeline`** / `run-main-task.py` | **Unsupported** in v2 — rewrite to LLM mutation JSON + `write_doc` if a capability must return |

**Promotion rule:** A post-MVP playbook graduates into MVP only when it has an **owner task** in §9 and passes Definition of Done (§10).
