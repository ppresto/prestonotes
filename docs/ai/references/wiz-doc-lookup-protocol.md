# Wiz Doc Lookup Protocol

Shared reference for any task that needs to validate or discover Wiz product, capability, integration, or feature information.

This protocol has two modes. Each task specifies which mode to use.

## Layers and constraints (do not confuse)

| Layer | What it is | Freshness |
|------|------------|-----------|
| **1. wiz-local + disk cache** | MCP **`wiz_search_wiz_docs`** / WIN APIs writing under **`docs/ai/cache/wiz_mcp_server/`** + **`manifest.json`** | **`manifest.json`** (`next_refresh_due`, `last_cached`) — see **`docs/ai/playbooks/refresh-wiz-doc-cache.md`**. For optional **wiz-remote** `wiz_docs_knowledge_base` → on-disk markdown snapshots (no Chroma, design: **`docs/tasks/active/TASK-074-ucn-accomplishments-vendor-wins-and-upsell-path-sku-gaps.md`** §G3 / §G8), see the same. |
| **Constraint** | **`docs.wiz.io`** is usually **not** fetchable from the workstation (firewall). Do **not** rely on HTTP mirroring of the public docs site. | Use tenant GraphQL (**`scripts/wiz_docs_client.py`** / **`materialize_wiz_mcp_docs.py`**) per **`docs/ai/references/wiz-mcp-tools-inventory.md`**. External blogs: **`spider_wiz_external_pages.py`**. |
| **2. Product Intelligence file** | **`MyNotes/Internal/AI_Insights/Product-Intelligence.md`** | `last_updated` in file (playbook default max age **7** days) — **`check_product_intelligence`** |
| **3. Chroma vector index** | Embeddings over ingest roots from **`prestonotes-mcp.yaml`** `rag:` (e.g. **`wiz_docs_cache`**, **`wiz_mcp_materializations`**, optional **`wiz_ext_pages`**) | Chunk metadata may carry manifest dates; **`wiz_knowledge_search`** with **`include_staleness=true`** — Chroma does **not** auto-expire by TTL |

Rebuild vectors after cache changes: **`uv run python -m prestonotes_mcp.ingestion.build_vector_db`** or MCP **`refresh_wiz_vector_index`** (after approval). CLI snapshot: **`uv run python scripts/wiz_doc_cache_manager.py vector-index-status --repo-root .`**

## Mode 1: Baseline Build (used by Load Product Intelligence)

Goal: build a comprehensive product knowledge base from scratch.

1. **Read full local cache corpus** — all files under `./docs/ai/cache/wiz_mcp_server/docs/`, **`./docs/ai/cache/wiz_mcp_server/mcp_materializations/`** (tenant GraphQL snapshots), plus manifest, doc index, link ledger, and search patterns.
2. **Run broad MCP category sweeps** — query every category bucket to discover new/updated docs.
3. **Upsert cache metadata** after every query via `uv run python scripts/wiz_doc_cache_manager.py` (repo root).
4. **Output** the full Product Intelligence reference file.

## Mode 2: Targeted Recommendation Lookup (used by Tech Acct Plan and other downstream tasks)

Goal: get the freshest, most relevant Wiz information for specific recommendation topics while also leveraging broad product knowledge for adjacent solution discovery.

### Step 1: Load Product Intelligence as broad context
- Read `./MyNotes/Internal/AI_Insights/Product-Intelligence.md` into session context.
- Purpose: enables the AI to surface adjacent solutions the user wouldn't search for directly (for example, user asks about one workflow challenge and AI identifies relevant cross-product capabilities).
- This is not just a cache check — it's loaded for breadth so the AI can make cross-domain connections.

### Step 2: MCP search first for each recommendation topic (freshness-first)
- Run `wiz_search_wiz_docs` with a targeted query for each specific recommendation topic before checking cache.
- This catches newly added docs, updated integrations, and recent feature changes that may not be in the local cache yet.
- Use cache-guided retrieval seeds when helpful:
  - `win_apis_doc_index.json` discovered `doc_name` entries
  - `wiz-doc-link-ledger.md` seed URLs

### Step 2.5: Tool-aware integration capability matrix (required for workflow/routing recommendations)
- When customer tools are known (security, engineering, IT operations, data, AI, and business workflow tools), run targeted MCP queries per tool:
  - "`Wiz + <ToolName> integration supported objects`"
  - "`Wiz + <ToolName> push vs pull behavior`"
  - "`Wiz + <ToolName> limitations / prerequisites`"
- Build a per-tool matrix with:
  - tool name
  - Wiz object class (`Detection`, `Threat`, `Issue`, `Finding`, `Audit Log`)
  - direction (push/pull)
  - mechanism (native integration/webhook/API/automation rule)
  - support status (`explicitly documented` vs `not explicitly documented`)
- Recommendation constraint:
  - only recommend hard routing claims when support status is `explicitly documented`
  - if not explicit, label as provisional and avoid definitive architecture language.

### Step 3: Upsert results to cache
- After every MCP query, upsert cache metadata:
  - `uv run python scripts/wiz_doc_cache_manager.py upsert-doc ...` for `doc_name`
  - `uv run python scripts/wiz_doc_cache_manager.py upsert-url ...` for docs URLs
- This keeps the cache growing with each task run, benefiting future lookups.

### Step 4: Read cache for supplementary context
- After MCP search, read relevant cached docs from `./docs/ai/cache/wiz_mcp_server/docs/` for additional depth on related topics.
- Cache serves as the broad knowledge supplement, not the primary source for targeted recommendations.

### Step 4.5: External evidence enrichment for workflow quality (required when tools are known)
- Search external Wiz page cache for each customer tool:
  - `./docs/ai/cache/wiz_mcp_server/ext/pages/`
- If tool-specific pages are missing:
  - run external web discovery for Wiz + tool workflows (blog, case study, docs pages),
  - fetch high-quality pages,
  - cache them under `./docs/ai/cache/wiz_mcp_server/ext/pages/`,
  - update `./docs/ai/cache/wiz_mcp_server/ext/latest.md`.
- External pages are used for workflow patterns, challenge framing, sequencing quality, and new challenge archetypes; official docs remain the source of truth for support claims.

## Scope

This protocol applies to any Wiz-related claim, including but not limited to:
- Products (Cloud, Defend, Code, Compliance)
- Integrations (SIEM, SOAR, ITSM, CI/CD, API, Terraform)
- Capabilities (Security Graph, sensors, runtime detection, posture, DSPM)
- Deployment patterns and architecture
- Licensing and feature-entitlement boundaries

## Usage by Task Type

| Task | Mode | Why |
| :--- | :--- | :--- |
| Load Product Intelligence | Mode 1 (Baseline Build) | Full sweep to build the reference file |
| Tech Acct Plan | Mode 2 (Targeted Lookup) | Fresh targeted data for recommendations + broad PI for adjacent solutions |
| Account Summary | Mode 2 (Targeted Lookup) | Validate product/commercial claims |
| Other downstream tasks | Mode 2 (Targeted Lookup) | Default for any task that references Wiz capabilities |

## Guardrails

- Always ground Wiz-related recommendations in verified product capability, not assumed behavior.
- If MCP docs are unavailable (rate-limited, timeout), fall back to cache, mark the claim as provisional, and note the gap.
- Do not duplicate the full Product Intelligence sweep in downstream tasks — use Mode 2 targeted lookups against the existing baseline.
- The cache grows over time as each task run upserts new results. No task needs to build the cache from scratch except Product Intelligence.
- Do not infer support by analogy (for example: if Tool A supports object X, Tool B likely does too). Verify per tool/object pair.
- For routing outputs, include object-level specificity and direction (`what object`, `where it goes`, `how it gets there`, `supported status`).
- This protocol applies domain-agnostically: do not restrict discovery or integration validation logic to SOC/security-only assumptions.
