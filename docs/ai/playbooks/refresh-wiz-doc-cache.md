# Playbook: Refresh Wiz Doc Cache (v2)

Trigger: **`Refresh Wiz Doc Cache`**

Build and maintain the **local markdown cache** of Wiz documentation: **WIN inventory**, **tenant GraphQL (DOCS) materializations**, optional **external** pages, and **`manifest.json`**. This playbook drives **disk + manifest**; it does **not** rebuild Chroma by itself — after substantive cache updates, run **`uv run python -m prestonotes_mcp.ingestion.build_vector_db`** or MCP **`refresh_wiz_vector_index`** (with approval). See **`docs/ai/references/wiz-doc-lookup-protocol.md`** and **`docs/ai/references/wiz-mcp-tools-inventory.md`**.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

---

## Communication rule

At each step, tell the user what you are doing in plain English. Follow **`.cursor/rules/15-user-preferences.mdc`**.

---

## 1) Purpose

- Keep **`./docs/ai/cache/wiz_mcp_server/`** current: static **`docs/`** (legacy WIN exports if present), **`mcp_materializations/`** (latest text from **tenant GraphQL**, same contract as **`search_wiz_docs`**), **`ext/pages/`**, **`manifest.json`**, **`win_apis_doc_index.json`**.
- **Do not** assume **`https://docs.wiz.io`** is reachable from the workstation; use **wiz-local** / **`wiz_docs_search_cli.py`** / **`materialize_wiz_mcp_docs.py`** instead.

## 2) Cache layout (v2)

| Path | Role |
|------|------|
| **`docs/ai/cache/wiz_mcp_server/manifest.json`** | Authoritative freshness: `last_cached`, `ttl_days`, `next_refresh_due`, `status` |
| **`docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`** | Discovered WIN `doc_name` values by category |
| **`docs/ai/cache/wiz_mcp_server/docs/<doc_name>.md`** | Static WIN snapshots (optional legacy / import) |
| **`docs/ai/cache/wiz_mcp_server/mcp_materializations/<doc_name>.md`** | **MCP / GraphQL** snapshots (preferred for “latest” product text) |
| **`docs/ai/cache/wiz_mcp_server/ext/pages/`** | External **`www.wiz.io`** (and allowlisted) pages |

## 3) Refresh workflow

1. **Status:** `uv run python scripts/wiz_doc_cache_manager.py status`
2. **Vector vs cache (optional):** `uv run python scripts/wiz_doc_cache_manager.py vector-index-status --repo-root .`
3. **WIN index:** Enumerate categories with **wiz-local** **`win_apis`**; update **`win_apis_doc_index.json`** when new `doc_name` values appear.
4. **Materialize (tenant GraphQL):** refresh all WIN rows older than **7** days (adjust flags as needed):

   ```bash
   uv run python scripts/wiz_doc_cache_manager.py mcp-materialize --min-age-days 7 --delay-seconds 2.5
   ```

   Or: `uv run python scripts/materialize_wiz_mcp_docs.py --min-age-days 7`

5. **External pages (HTTP, long TTL):** optional refresh of **`ext/pages/`** from **`ext/indexes/tier_manifest.json`** (default **365**-day skip if file is fresh):

   ```bash
   uv run python scripts/wiz_doc_cache_manager.py spider-ext --dry-run --max-pages 5
   ```

6. **Manifest-only sweep (no new GraphQL bodies):** `refresh-loop` re-checks disk snapshots and URL HTTP status — see **`docs/ai/cache/wiz_mcp_server/README.md`** for limits.

## 4) Freshness defaults

| Class | Typical TTL | Mechanism |
|-------|-------------|------------|
| WIN / MCP materializations | **7** days | `mcp-materialize` / `materialize_wiz_mcp_docs.py` |
| High-churn product URL (if ever probed) | 7 days | `upsert-url` + `refresh-loop` |
| Reference / tutorial (static export) | 14 days | manifest |
| Changelog / release | 3 days | (if indexed as `docs_url`) |
| **External blog / marketing** | **365** days | `spider-ext` |

## 5) Contract

Any Wiz MCP doc read in-session should have a matching manifest row (create or update **`last_checked`** / **`last_cached`** / **`status`**).

## 6) Output

Print a short summary: materialize attempts, spider pages, rate-limited/errors, stale remaining. Point to **`vector-index-status`** if vectors may be out of date after **`mcp_materializations/`** changes.
