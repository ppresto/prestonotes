# TASK-034 — MVP five flows: readiness, gaps, prerequisites

**Status:** [x] COMPLETE (matrix refreshed; child gaps 027/033/035/036/037/038 closed)  
**Opened:** 2026-04-21  
**Legacy Reference:** **`docs/project_spec.md`** §11; playbooks **`bootstrap-customer`**, **`load-product-intelligence`**, **`load-customer-context`**, **`run-account-summary`**, **`update-customer-notes`**; example account summary: add **`docs/examples/Dayforce-AI-AcctSummary.md`** when available (user reference file not yet in repo).

## Purpose

Single place to track **your five MVP actions** until each is **100%** runnable by an agent with **only** normal approvals (e.g. **`write_doc`**) and **clear** pre-reqs.

---

## 1) Bootstrap a new customer folder into Google Drive

| State | Notes |
| :--- | :--- |
| **Partial** | MCP **`bootstrap_customer`** scaffolds **local** `MyNotes/Customers/<Name>/` (see **`docs/ai/playbooks/bootstrap-customer.md`**). **Creating** the remote Drive tree + first GDoc is still **operator + Google** (folder ID, template copy) unless scripted elsewhere. |
| **LLM can** | Run **`bootstrap_customer`** (`dry_run` first), explain missing paths, run **`sync_notes`** after you have Drive. |
| **You must** (if not done): **Google Drive for Desktop**, **`GDRIVE_BASE_PATH`**, **`MYNOTES_ROOT_FOLDER_ID`**, **`gcloud` auth**, customer name pattern. |

**Tasks:** tighten **`bootstrap-customer.md`** with a **checklist** for “first GDoc exists in Drive”; optional future task for Apps Script / Drive API automation.

---

## 2) Load Product Intelligence

| State | Notes |
| :--- | :--- |
| **Partial** | **Read path:** playbook loads **local** cache (`docs/`, **`mcp_materializations/`**, tier digests) — disk → LLM context only. **Refresh path:** **`mcp-materialize`** (WIN via tenant GraphQL) + optional **`spider-ext`** (external URLs). Playbook now documents **Read vs refresh**, finite WIN/discovery-wave full-sync coverage, and discovery-wave run order/rollback. |
| **LLM can** | Run **`wiz_doc_cache_manager.py mcp-materialize`**, **`spider-ext`**, read caches into session; explain TTLs (**7d** WIN/MCP, **365d** ext). |
| **You must:** **`WIZ_*`** in **`.cursor/mcp.env`**, wiz-local or CLI; for vectors **`GOOGLE_API_KEY`** / **`GEMINI_API_KEY`**. |

**Gaps to close:** Completed in this pass — **TASK-035** + **TASK-027** now capture read-vs-refresh guidance, finite “full sync” definition, and two-wave stability evidence.

**Tutorial:** **TASK-036** — end-to-end “materialize → `build_vector_db` → `wiz_knowledge_search`”.

---

## 3) Load Customer Context + Wiz in same session

| State | Notes |
| :--- | :--- |
| **Full** | **`load-customer-context.md`** defines sync + weighted reads + Wiz MCP first for product facts, including explicit pivot behavior to refresh product intelligence when stale. |
| **LLM can** | **`sync_notes`**, **`read_*`**, then answer questions; invoke **Load Product Intelligence** when user asks Wiz-specific questions. |
| **You must:** synced **`MyNotes/`**; **`discover_doc`** works for that customer. |

**Tasks:** Completed in this pass — explicit **“If user pivots to Wiz”** mini-step added (reload PI cache or run materialize if stale).

---

## 4) Create AI Account Summary (`*-AI-AcctSummary.md`)

| State | Notes |
| :--- | :--- |
| **Partial** | **`run-account-summary.md`** now documents canonical path **`MyNotes/Customers/<C>/AI_Insights/<C>-AI-AcctSummary.md`** and manual save flow (**Approach B**). There is still no dedicated MCP write tool. |
| **LLM can today** | Produce markdown in chat with explicit instructions for manual save to canonical file path + sync. |
| **Needed for 100%** | Future toolized write path (optional post-MVP): add a constrained MCP writer and tests. |

---

## 5) Update Customer Notes (tabs: exec summary, daily activity, metadata)

| State | Notes |
| :--- | :--- |
| **Partial** | **`update-customer-notes.md`** + **`write_doc`** + mutation rules; orchestrator path is largely ready with source-order and quality-bar tuning landed in **TASK-038**. |
| **LLM can** | Full read → plan → approval → **`write_doc`**; Daily Activity via **`prepend_daily_activity_ai_summary`**. |
| **You must:** **`read_doc`** working, schema awareness, **approval** for writes. |

**Tasks:** Completed in this pass via **TASK-038** (explicit source order + sparse/rich strategy + quality gates).

---

## Mandatory utilities (before LLM can succeed)

| Prerequisite | Why |
|--------------|-----|
| **`.cursor/mcp.env`** filled | Drive path, folder ID, gcloud account, optional **`WIZ_*`**, embedding key |
| **Drive sync** | **`sync_notes`** or **`scripts/rsync-gdrive-notes.sh`** so `MyNotes/` matches GDrive |
| **wiz-local or CLI** | For live doc pulls / materialize |
| **First-time gcloud** | Browser login when MCP returns **`run_in_terminal_to_fix`** |

The LLM should **ask** for any missing item instead of failing silently.

## Child tasks

- **TASK-035** — Product intelligence: discovery proof + “full sync” definition (**done**)  
- **TASK-036** — Tutorial: Wiz cache → embeddings → `wiz_knowledge_search` (**done**)  
- **TASK-037** — Persist **AI Account Summary** to `AI_Insights/*-AI-AcctSummary.md` (**done via approach B manual save path**)  
- **TASK-038** — **Update Customer Notes**: data-dependent tuning + explicit source list (**done**)  
- **TASK-033** — End-of-run chat format / activity recap alignment across playbooks (**done**)  
- **TASK-027** — Discovery catalog two-wave proof (**done**)  
