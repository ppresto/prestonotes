# TASK-024 — Wiz doc cache + vector index: end-to-end pipeline (v1 parity plan)

**Status:** `[x] DONE` (archived 2026-04-20) — Phases A–D closed: docs, **`vector-index-status`**, **`refresh_wiz_vector_index`**, advisor hybrid guidance, optional OAuth smoke test.  
**Depends on:** Shipped **`wiz_knowledge_search`** + **`build_vector_db`** (Gemini embeddings + Chroma under `.vector_db/wiz_chroma`). **Operator doc sweeps** assume **[TASK-025](./TASK-025-migrate-wiz-mcp.md)** is done so **wiz-local** is wired in **`.cursor/mcp.json`**.  
**Legacy reference (sibling `../prestoNotes.orig/`):**

- `docs/ai/playbooks/refresh-wiz-doc-cache.md` — cache layout, TTL policy (7 / 14 / 3 days), manifest contract, crawl waves.
- `docs/ai/playbooks/build-product-intelligence.md` (Load Product Intelligence) — cache-first delta vs full rebuild, `docs/` + `ext/indexes/` + `ext/pages/`.
- `docs/ai/references/wiz-doc-lookup-protocol.md` — Mode 1 baseline vs Mode 2 MCP-first + cache upsert + read cache.
- `scripts/wiz_doc_cache_manager.py` — `manifest.json`, `upsert-doc` / `upsert-url`, `refresh-loop` (HTTP HEAD-ish checks for URLs; WIN doc rows tie to local `docs/{doc_name}.md` presence).

---

## 1. What v1 did (two ingestion lanes)

| Lane | Mechanism | On-disk artifacts | Freshness |
|------|-----------|-------------------|-----------|
| **WIN / MCP docs** | **`wiz-local`** MCP (`wiz_search_wiz_docs`, `win_apis`, …) — agent or script pulls content | `docs/ai/cache/wiz_mcp_server/docs/<doc_name>.md` (snapshots) | **`manifest.json`** per entry: `last_cached`, `ttl_days`, `next_refresh_due`, `status` |
| **External URLs** (blogs, case studies) | Discovery + fetch (playbook + `wiz_doc_cache_manager` URL entries, HTTP in `refresh-loop`) | `docs/ai/cache/wiz_mcp_server/ext/pages/`, indexes like `ext/indexes/tier_a_urls.md` | Same **manifest** model for `docs_url` rows |

**Important:** v1 **RAG did not exist**; retrieval was **read markdown files + live MCP search**. The cache was the **durable local corpus** and **manifest** was the **freshness index**.

---

## 2. What v2 does today (gap)

| Component | Behavior today | Gap vs v1 intent |
|-----------|----------------|------------------|
| **`build_vector_db`** | Indexes **only** `docs/ai/cache/wiz_mcp_server/docs/**/*.md` | Does **not** index `ext/pages/`, tier digests, or other cache roots unless we extend paths. |
| **Chroma** | Derived vectors + chunk text | **No embedded TTL** — Chroma does not know “7 days”; it only knows what you last ingested. |
| **`wiz_knowledge_search`** | Semantic return | Cannot know staleness unless **metadata** or a **sidecar check** supplies dates. |
| **`wiz_doc_cache_manager.py`** (v2) | Same script as v1 port | **Not wired** to auto-trigger Chroma rebuild; manifest and vector index can **diverge**. |

---

## 3. Design answers (for approval)

### Does v2 need local files to feed the vector DB?

**Yes, for the architecture we shipped:** the embedding job reads **files from disk** (or we explicitly add a second source: DB/API → chunk → embed without persisting md — higher scope).

**Recommended default:** treat **local markdown cache as the canonical ingest input** (same as v1’s “cache-second” depth). MCP still **refreshes** those files via playbooks / tools; **vector rebuild** is a **downstream materialization** of that cache.

**Extension (TASK-024 scope):** configurable **ingest roots** in `prestonotes-mcp.yaml` `rag:`:

- `wiz_docs_cache` (existing)
- `wiz_ext_pages` → `docs/ai/cache/wiz_mcp_server/ext/pages/**/*.md` (optional)
- optional max bytes / exclude globs

### How will it know content is older than 7 days and must refresh?

**Chroma alone will not.** Use one or a combination of:

1. **Manifest as source of truth** (v1): `wiz_doc_cache_manager.py status` / `refresh-loop` + playbooks keep `next_refresh_due`. **Ingestion step** reads manifest and attaches **`last_cached` / `next_refresh_due` / `source_path`** into Chroma **metadata** at chunk or file level.
2. **Query-time warning**: `wiz_knowledge_search` (or a thin wrapper) loads manifest for returned `source_path` and if `date.today() > next_refresh_due`, append `"stale": true` / `"refresh_hint"` in JSON.
3. **Scheduled / manual rebuild**: `build_vector_db --only-if-manifest-stale` or separate **`sync_wiz_vector_index`** MCP tool that: (a) runs cache refresh playbook steps *or* calls a thin Python “refresh stale docs” helper, (b) re-embeds only changed files (by mtime or manifest list).

**Product Intelligence “7 days”** in v2 playbooks refers to **`MyNotes/Internal/AI_Insights/Product-Intelligence.md`**, not the Wiz cache manifest — TASK-024 should **cross-link** both in docs so operators know **two freshness surfaces** (PI file vs wiz cache vs vector index).

### Manual override / “pull fresh then search”

| User intent | v1 pattern | v2 target pattern |
|-------------|------------|-------------------|
| Full refresh | `Refresh Wiz Doc Cache` + MCP sweeps | Same playbook (port to v2) **then** `build_vector_db --reset` or incremental job |
| Delta | Load Product Intelligence **cache-first** | Refresh only **stale manifest rows**, then **incremental Chroma upsert** (delete chunks for changed `source_path` then re-add) |
| Force re-embed without MCP | N/A | `build_vector_db --reset` on existing md (vectors only) |

Optional **MCP tool** (TASK-024 deliverable): **`refresh_wiz_vector_index`** (dry_run default) — documents that it does **not** replace wiz-local MCP; it only re-reads disk + re-embeds.

---

## 4. Proposed deliverables (split into sub-phases)

### Phase A — Documentation (no behavior change)

- [x] **`refresh-wiz-doc-cache.md`** ported to **`docs/ai/playbooks/refresh-wiz-doc-cache.md`**; **`wiz-doc-lookup-protocol.md`** extended with **Three layers** + CLI pointers.
- [x] README **Wiz RAG (Stage 4)** subsection: three layers + **`vector-index-status`**.

### Phase B — Ingestion parity

- [x] **`build_vector_db`**: multiple roots from YAML; include **`ext/pages`** when present; stable IDs include root prefix to avoid collisions.
- [x] **Metadata**: set `last_cached` / `next_refresh_due` / `status` from manifest when entry matches `doc:{name}` for paths under `wiz_docs_cache`; else omit.

### Phase C — Freshness + operator UX

- [x] **`wiz_knowledge_search`**: optional `include_staleness=true` → join manifest, flag stale chunks (`next_refresh_due` date ≤ today).
- [x] **CLI**: **`wiz_doc_cache_manager.py vector-index-status`** — manifest stale + Chroma **`wiz_docs`** stats + next-step hint.
- [x] **MCP** **`refresh_wiz_vector_index`** (`dry_run` default **true**; **`dry_run=false`** after chat approval).

**Evidence (2026-04-20):**

```bash
uv run pytest prestonotes_mcp/tests/ -q
# 36 passed

uv run ruff check prestonotes_mcp scripts/wiz_vector_coverage_report.py
uv run ruff format prestonotes_mcp scripts/wiz_vector_coverage_report.py
```

### Phase D — TASK-022 alignment

- [x] Domain advisors **`.cursor/rules/23`–`27`**: **Retrieval hybrid** — vector first, wiz-local for live/stale gaps, cache playbook + **`refresh_wiz_vector_index`** after approval.

---

## 5. Acceptance criteria (whole task)

- [x] Operator docs: **`docs/ai/references/wiz-doc-lookup-protocol.md`**, **`README.md`**, **`load-product-intelligence.md`**, **`refresh-wiz-doc-cache.md`** — local markdown required for vector ingest unless a streaming ingestor is added later.
- [x] Automated tests: **`prestonotes_mcp/tests/test_build_vector_manifest_meta.py`** (manifest dates on chunks) + **`prestonotes_mcp/tests/test_wiz_oauth_smoke.py`** (optional live OAuth when **`WIZ_*`** env set).
- [x] Protocol + README state explicitly that **Chroma does not enforce manifest TTL** without **`include_staleness`** / manifest sidecar logic.

---

## 6. Follow-ups (optional, not blocking)

1. **`build_vector_db --only-stale`** or incremental delete-by-`source_path` — not implemented; operators use full rebuild or manual subset today.  
2. Deeper **`win_apis`** automation remains playbook-driven (no new daemon).
