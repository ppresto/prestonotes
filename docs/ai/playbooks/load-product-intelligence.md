# Playbook: Load Product Intelligence (v2)

Trigger: `Load Product Intelligence`

Purpose: refresh the internal Wiz/product reference file from internal sources, Wiz MCP docs, and cached content.

**v2 paths:** Customer Google Doc reads/writes use `prestonotes_gdoc/` through the prestonotes MCP tools (`discover_doc`, `read_doc`, `write_doc`, …). This playbook covers local markdown under `MyNotes/` and product caches under `docs/ai/cache/`. Preflight still uses `./scripts/rsync-gdrive-notes.sh` to sync MyNotes with Google Drive.

**Wiz cache maintenance:** after MCP doc sweeps, keep **`manifest.json`** and snapshots aligned with **`docs/ai/playbooks/refresh-wiz-doc-cache.md`** (use **`mcp-materialize`** for tenant GraphQL bodies — **`docs.wiz.io`** is not bulk-HTTP-mirrored). Then rebuild vectors if needed (**`refresh_wiz_vector_index`** or **`build_vector_db`**). See **`docs/ai/references/wiz-doc-lookup-protocol.md`** and **`docs/ai/references/wiz-mcp-tools-inventory.md`**.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

---

## Communication Rule
At every step, tell the user what you are doing in plain English. Follow the format rules in `15-user-preferences.mdc`.

## End-of-run chat format
- Follow **`.cursor/rules/15-user-preferences.mdc`** for final messaging.
- After multi-step work, end with **`### Activity recap`** covering what refreshed, what was read-only, and what remains pending.
- Call out whether the run used only local cache reads or executed refresh commands.

---

## 0) Execution Mode Default (Required)
- Default mode is **cache-first delta mode** when the user does not explicitly request a full sweep.
- Full baseline sweep is allowed only when the prompt explicitly includes a full intent, such as:
  - `full`
  - `rebuild`
  - `full rebuild`
  - `full sweep`
- If no explicit full intent is present, run delta mode by default.

## 0.5) Load Profile Default (Required)
- Default load profile is `default` when user does not request a profile.
- Supported profile flags:
  - `include rules` or `rules`
  - `include extras` or `extras`
  - `include all` or `all`
- Profile behavior:
  - `default`:
    - always load docs cache (`./docs/ai/cache/wiz_mcp_server/docs/`) **and** MCP materializations (`./docs/ai/cache/wiz_mcp_server/mcp_materializations/`) when present (latest tenant GraphQL text per `doc_name`)
    - always load external Tier A full pages and Tier B digests:
      - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_a_urls.md`
      - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_b_digests.md`
    - do **not** load per-item CCR/control files, updates, previews, or threat entries into synthesis context
  - `extras`:
    - include updates/previews/threat entries in addition to `default`
    - still do not load per-item CCR/control files
  - `rules`:
    - include CCR/control title indexes only:
      - `./docs/ai/cache/rules/indexes/ccr_titles.md`
      - `./docs/ai/cache/rules/indexes/control_titles.md`
    - do not load full per-item CCR/control files unless explicitly requested
  - `all`:
    - load all available caches (docs, ext, updates, previews, threat, rules)

## 1) Preflight
- Run `./scripts/rsync-gdrive-notes.sh`.
- Confirm source paths exist:
  - `./MyNotes/Internal/`
  - `./MyNotes/Case_Studies/`
- If either path is missing, continue with available source(s) and record the gap in output.

## 2) Required Ingestion Scope (Do Not Skip)
- Read **all readable text sources recursively** under:
  - `./MyNotes/Internal/`
  - `./MyNotes/Case_Studies/`
- Include at minimum: `.md`, `.txt`, `.csv`, `.json`, `.yaml`, `.yml`.
- Explicitly include internal master transcripts in the Internal root:
  - `./MyNotes/Internal/_MASTER_TRANSCRIPT_INTERNAL*.txt`
- Do not assume there is an `Internal/Transcripts/` subfolder.
- Build a source inventory table before synthesis:
  - `path`
  - `file_type`
  - `included` (`yes`/`no`)
  - `reason_if_excluded`

## 2.5) Local Wiz Cache Ingestion (Required)
- Follow `docs/ai/references/wiz-doc-lookup-protocol.md` **Mode 1** (Baseline Build) for full cache ingestion and broad MCP sweeps.
- Additional cache artifacts to read for full sweeps:
  - `./docs/ai/references/wiz-doc-search-patterns.md`
  - `./docs/ai/references/wiz-doc-link-ledger.md`
- For generic `Load Product Intelligence` runs, read local cache according to Section 0.5 load profile.
- Default-required cache loads (always):
  - all files under `./docs/ai/cache/wiz_mcp_server/docs/`
  - all files under `./docs/ai/cache/wiz_mcp_server/mcp_materializations/` **when that directory exists** (GraphQL snapshots; prefer for freshness vs static `docs/` alone)
  - tiered external context:
    - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_a_urls.md`
    - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_b_digests.md`
- Optional cache loads (only by profile):
  - `all`:
    - full external pages under `./docs/ai/cache/wiz_mcp_server/ext/pages/`
  - `extras` / `all`:
    - `./docs/ai/cache/updates/entries/`
    - `./docs/ai/cache/preview_hub/items/`
    - `./docs/ai/cache/threat/advisories/`
    - `./docs/ai/cache/threat/details/`
  - `rules` / `all`:
    - `./docs/ai/cache/rules/indexes/ccr_titles.md`
    - `./docs/ai/cache/rules/indexes/control_titles.md`
  - full per-item rules (`./docs/ai/cache/rules/ccr/`, `./docs/ai/cache/rules/controls/`) only when explicitly requested by user prompt.
- Use cache entries with recent freshness (`next_refresh_due` in the future) as high-confidence retrieval seeds.
- If stale entries are substantial, run cache refresh task first:
  - `Refresh Wiz Doc Cache`

## 2.51) Read vs refresh decision tree (required)

- **Read-only path (default for `Load Product Intelligence`):**
  - load local cache files already on disk into LLM context (`docs/`, `mcp_materializations/`, and configured `ext/indexes` inputs)
  - do not claim this step performed a network refresh by itself
- **Refresh path (explicit operator/agent action before or during load):**
  - run `uv run python scripts/wiz_doc_cache_manager.py mcp-materialize ...` for WIN/tenant GraphQL docs
  - optionally run `uv run python scripts/wiz_doc_cache_manager.py spider-ext ...` for external pages
  - then re-read local cache artifacts for synthesis
- **TTL defaults:** WIN/MCP docs = 7 days; external pages = 365 days (unless overridden by command flags).
- If the user asks for "latest" and freshness is stale, recommend refresh path first, then proceed with read path.

## 2.52) What "full sync" means in this playbook

- "Full sync" means full coverage of the **finite** discovered WIN catalog (`win_apis_doc_index.json`) plus configured external seed sources, not an infinite crawl of all `docs.wiz.io`.
- WIN sync completeness is measured against discovered `doc_name` entries materialized into `mcp_materializations/`.
- Discovery expansion is wave-based: run discovery waves until two consecutive waves produce no unexpected net-new URLs/doc names, then stop and record stability evidence.
- Track discovery-wave process details and proof in `docs/tasks/archive/2026-04/TASK-027-wiz-discovery-catalog.md`.

## 2.53) Discovery wave run order and rollback

- Canonical files:
  - `./docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`
  - `./docs/ai/cache/wiz_mcp_server/manifest.json`
  - `./docs/ai/cache/wiz_mcp_server/mcp_materializations/`
- Minimum run order:
  1. Regenerate/extend `win_apis_doc_index.json` from wiz-local `win_apis` categories when needed.
  2. Run `uv run python scripts/wiz_doc_cache_manager.py seed-from-index`.
  3. Run `uv run python scripts/wiz_doc_cache_manager.py refresh-loop --max-waves 2 --include-all` until two same-input waves show no net-new catalog IDs.
  4. Run `uv run python scripts/wiz_doc_cache_manager.py mcp-materialize` for any targeted refresh gaps.
  5. Rebuild vectors only if this run changed docs that should be searchable.
- Rollback rule: if a wave introduces bad entries, restore `win_apis_doc_index.json` and `manifest.json` from git, then rerun seed + refresh-loop on the restored files.
- Ops ledger template line (use in run notes or ledger): `WIZ-DISCOVERY-WAVE <YYYY-MM-DD>-<N>: index_delta=+<a>/-<b>, manifest_delta=+<c>/-<d>, decision=<stop|continue>, notes=<why>`.

## 2.55) Vector index and manifest (v2)

- **Manifest (freshness source of truth):** `./docs/ai/cache/wiz_mcp_server/manifest.json` — per-entry `last_cached`, `next_refresh_due`, `status`.
- **CLI status:** `uv run python scripts/wiz_doc_cache_manager.py status` — entry counts and stale-or-due rows.
- **Chroma rebuild** after large cache pulls or when vectors must match disk: from repo root run  
  `uv run python -m prestonotes_mcp.ingestion.build_vector_db --reset`  
  (indexes `rag.wiz_docs_cache` and optional `rag.wiz_ext_pages` from `prestonotes-mcp.yaml`; see `prestonotes-mcp.yaml.example`).
- **Coverage spot-check:** `uv run python scripts/wiz_vector_coverage_report.py --repo-root .`
- **Operator tutorial:** `docs/tutorials/wiz-rag-from-cache-to-search.md`

## 2.6) Wiz-Remote Enrichment Cache (Required)
- Use the `wiz-remote` MCP server to pull product-level intelligence that is not customer/tenant-specific.
- For all tools in this section, **ignore tenant-specific operational data** such as findings, issue instances, and environment metrics.
- Focus only on reusable product intelligence:
  - capability descriptions
  - feature status/type
  - release/change details
  - threat advisory narratives
  - rule/control metadata
- Ensure these cache paths exist and persist outputs there:
  - `./docs/ai/cache/updates/` for `list_product_updates`
  - `./docs/ai/cache/preview_hub/` for `list_preview_migration_hub_items`
  - `./docs/ai/cache/threat/` for `list_threat_advisory_items`, `get_threat_center_item`
  - `./docs/ai/cache/rules/` for `list_cloud_configuration_rules`, `list_controls`
- Required cache shape (do not store only counts/summaries):
  - updates: `./docs/ai/cache/updates/entries/<update_id>.md`
  - preview hub: `./docs/ai/cache/preview_hub/items/<item_id>.md`
  - threat: `./docs/ai/cache/threat/advisories/<advisory_id>.md` and optional `./docs/ai/cache/threat/details/<advisory_id>.md`
  - rules: `./docs/ai/cache/rules/ccr/<rule_id>.md` and `./docs/ai/cache/rules/controls/<control_id>.md`
  - each area may keep `latest.md` as run summary, but per-item files are mandatory
- Required per-item fields (frontmatter + body):
  - frontmatter: `id`, `title_or_name`, `source_tool`, `fetched_at`, `last_updated`, `freshness_state`
  - body: normalized item summary, key metadata, and source links
- Freshness-first mode: keep the latest cache state current; historical snapshots are optional and not required.

## 2.7) Cache-First Delta Mode (Required for Time-Optimized Runs)
- Before running broad discovery, build a cache inventory from existing local artifacts:
  - `./docs/ai/cache/wiz_mcp_server/docs/`
  - `./docs/ai/cache/wiz_mcp_server/ext/`
  - `./docs/ai/cache/updates/`
  - `./docs/ai/cache/preview_hub/`
  - `./docs/ai/cache/threat/`
  - `./docs/ai/cache/rules/`
- Use inventory fields where available (`id`, `url`, `title`, `updatedAt`, `last_updated`, `next_refresh_due`) to classify each item:
  - `fresh` (keep; skip re-fetch)
  - `stale` (eligible for refresh)
  - `missing` (must fetch)
- Delta-mode execution policy:
  - do not re-fetch `fresh` IDs/URLs
  - fetch all `missing` IDs/URLs
  - refresh only `stale` IDs/URLs
  - if metadata is insufficient to classify freshness, treat as `stale`
- Maintain a run-time delta ledger with:
  - skipped fresh items
  - refreshed stale items
  - net-new discovered items
  - unresolved items (fetch attempted but failed)
- Delta identity keys:
  - updates/previews/threat/rules/controls: use canonical item `id`
  - external pages: use canonical `url`
- Delta hydration rule:
  - `fresh`: keep existing per-item file; skip hydration
  - `stale`/`missing`: write or overwrite per-item file with full normalized content

## 2.8) External Source Cache Model (Required)
- Treat external blog/customer content as URL-keyed, mostly immutable artifacts.
- Cache roots:
  - `./docs/ai/cache/wiz_mcp_server/ext/sources/` for source indexes and discovery manifests
  - `./docs/ai/cache/wiz_mcp_server/ext/pages/` for one content file per canonical URL
- Required source index fields (`index.json` per seed source):
  - `source_name`
  - `seed_url`
  - `last_scanned_at`
  - `discovered_urls[]` with `url`, `title`, `published_at` (if present), `first_seen_at`
- Required page metadata fields:
  - `url`, `source_name`, `fetched_at`, `published_at` (if present), `extraction_mode`, `content_hash`
- Required external tiering artifacts:
  - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_manifest.json`
  - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_a_urls.md`
  - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_b_digests.md`
  - `./docs/ai/cache/wiz_mcp_server/ext/indexes/tier_c_urls.md`
- Delta rule for external pages:
  - URL present in cache => `fresh` (skip re-fetch)
  - URL missing in cache => hydrate and cache
  - refresh existing URL only in explicit full/rebuild mode, or if cached artifact is missing/corrupt

## 3) Wiz MCP Product Docs Ingestion (Broad Sweep)
- This task uses the Wiz Doc Lookup Protocol in **broad sweep mode** — querying all category buckets, not just targeted topics.
- Mandatory source: Wiz MCP docs search tool (`wiz_search_wiz_docs`) for product/capability claims.
- Constraint: this MCP interface is search-driven and may not expose a canonical "list all docs" endpoint.
- To maximize coverage, run a category sweep and deduplicate returned links.
- Use cache-guided retrieval order:
  1. `win_apis_doc_index.json` discovered `doc_name` entries
  2. `wiz-doc-link-ledger.md` seed URLs
  3. `wiz-doc-search-patterns.md` query patterns
- Required query buckets (at least one query each):
  - Platform architecture and core concepts
  - Wiz Cloud (CSPM/CNAPP, exposure, graph, posture)
  - Wiz Code (SAST, SCA, IaC, container, CI/CD)
  - Wiz Defend / Runtime Sensor / detections / response
  - Data security / DSPM / identities / entitlements
  - Integrations (SIEM, SOAR, ticketing, API, Terraform)
  - Compliance, governance, and frameworks
  - Release notes/changelog for recent feature changes
- For each docs query, capture:
  - query text
  - links returned
  - short evidence notes
- Any time a document/link is queried, upsert cache metadata per the lookup protocol.
- Maintain a "docs coverage ledger" in the output:
  - unique doc links reviewed
  - link count by category
  - known blind spots / low-confidence zones
- In cache-first delta mode:
  - resolve/query only links that are `missing` or `stale` per Section 2.7
  - skip links already present and `fresh` in `./docs/ai/cache/wiz_mcp_server/docs/` or `./docs/ai/cache/wiz_mcp_server/ext/`
  - keep a `skipped_as_fresh` count per docs category

## 3.5) Wiz-Remote Product Enrichment Sweep (Broad, Non-Tenant)
- Run the following `wiz-remote` tools and cache each result to the paths in Section 2.6:
  - `list_product_updates`
  - `list_preview_migration_hub_items`
  - `list_threat_advisory_items`
  - `get_threat_center_item` (for selected high-value advisories returned by list)
  - `list_cloud_configuration_rules`
  - `list_controls`
- MCP invocation requirement (do not skip):
  - call remote tools using `arguments` payload shape (for example: `CallMcpTool(..., arguments={\"first\":500,...})`)
  - do not pass tool parameters as top-level fields; if you do, defaults may be silently applied and coverage will be incomplete
- Enrichment extraction requirements:
  - keep product-level descriptions, titles, tags, docs links, rule/control metadata
  - discard customer/tenant-specific findings, issue counts, and environment-specific metrics
- For product updates and preview items:
  - prioritize docs/blog links for follow-up validation and cache growth
  - track new vs previously seen entries by ID where available
  - when links are present, resolve and cache them by target:
    - any `docs.wiz.io` links must be resolved via `wiz-local` MCP `wiz_search_wiz_docs` and then cached to `./docs/ai/cache/wiz_mcp_server/docs/`
    - do not use direct HTTP fetch for `docs.wiz.io` content
    - any external links (blogs and other non-`docs.wiz.io`) -> `./docs/ai/cache/wiz_mcp_server/ext/`
  - if a link cannot be fetched, still cache the URL and retrieval status for freshness tracking
- For external links (`non-docs.wiz.io`) in updates/previews:
  - fetch page body content when reachable and persist to:
    - `./docs/ai/cache/wiz_mcp_server/ext/pages/<normalized-url-slug>.md`
  - include in file:
    - URL, fetch timestamp, title, extracted body text/summary, and retrieval status
  - if fetch fails or page is script-heavy, persist a stub with failure reason and fallback metadata
- For threat and rule/control sweeps:
  - capture information that improves "what Wiz can detect/check" coverage explanations
  - do not include demo-tenant posture outcomes in Product Intelligence conclusions
- CCR/Control completeness policy (required):
  - `list_cloud_configuration_rules` and `list_controls` must be treated as completeness-gated, not single-call snapshots
  - build a deduplicated ID set from multiple shards and compare against API `totalCount`
  - required shard sequence for CCR:
    - base pull (`first: 500`) to capture baseline and `totalCount`
    - provider/service shards (`cloud_provider`, `service_type`)
    - severity shards (`severity`)
    - IaC-style shards (`matcher_types`, targeted `search` terms such as `T-IAC-Rule-` when needed)
    - temporal shards (`created_at_*` / `updated_at_*`) when any shard still truncates at page cap
  - required shard sequence for controls:
    - type + severity shards (`type`, `severity`)
    - enabled/disabled shards (`enabled`) to capture controls with null/edge severity groupings
    - alternate ordering shards (`order_by_field`, `order_by_direction`) if deduped coverage remains below `totalCount`
  - completion gate:
    - if deduped IDs `< totalCount` for CCR or controls, mark run as `partial_coverage`
    - record exact missing counts in `./docs/ai/cache/rules/latest.md`
    - do not claim full cache completeness in output until deduped IDs == `totalCount`
- CCR/control title aggregation requirement:
  - maintain compact title indexes for default analysis mode:
    - `./docs/ai/cache/rules/indexes/ccr_titles.md`
    - `./docs/ai/cache/rules/indexes/control_titles.md`
  - these title indexes are the default rules context payload for `rules` profile.
- In cache-first delta mode:
  - updates/previews: skip known `fresh` IDs, fetch only `missing`/`stale`
  - threat advisories: skip known `fresh` advisory IDs; call `get_threat_center_item` only for `missing`/`stale` high-value IDs
  - rules/controls: refresh only when stale or missing (do not re-ingest unchanged fresh records)
  - external blog/customer pages: hydrate only net-new URLs from Section 3.8 discovery indexes
  - always preserve full coverage by running a lightweight listing pass to detect net-new IDs, then selectively hydrate only deltas

## 3.7) JS-Heavy External Page Assessment (Required for Ext Cache Quality)
- For each external URL fetched into `./docs/ai/cache/wiz_mcp_server/ext/pages/`, assess content extractability:
  - classify page as `content-first`, `mixed`, or `script-heavy`
  - record quick metrics where possible: script tag count, text density estimate, and whether meaningful body content was extracted
- If classified `script-heavy` with poor extracted body:
  - keep cached stub with URL + classification + reason
  - mark for enhanced browser-based render capture in a follow-up pass
- Browser-render fallback (required for low-quality extracts):
  - trigger fallback when any of these are true:
    - extracted body is truncated or obviously incomplete
    - classification is `script-heavy`
    - extract is style/template dominated and lacks article context
  - use browser automation to render JS and extract content from `article` / `main` / highest-text container
  - overwrite the page cache file with rendered extraction (do not keep only raw template output)
  - add frontmatter fields:
    - `extraction_mode` (`static_fetch` or `browser_rendered`)
    - `render_wait_seconds`
    - `selector_used`
    - `content_length_chars`
    - `extract_quality_notes`

## 3.8) External Blog and Customer Delta Crawl (Required)
- Run a dedicated external discovery pass (independent of update/preview links) for:
  - `https://www.wiz.io/blog/tag/ai`
  - `https://www.wiz.io/blog/tag/security`
  - `https://www.wiz.io/blog/tag/product`
  - `https://www.wiz.io/blog/tag/datasecurity`
  - `https://www.wiz.io/blog/tag/news`
  - `https://www.wiz.io/blog/tag/public-sector`
  - `https://www.wiz.io/customers`
- Parallelization requirement:
  - scan all six blog tag pages in parallel
  - scan the customers hub in parallel with blog scans
- Discovery/indexing behavior:
  - extract canonical article/story URLs from each seed page
  - write/update one source index per seed under `./docs/ai/cache/wiz_mcp_server/ext/sources/`
  - compare discovered URLs against existing `./docs/ai/cache/wiz_mcp_server/ext/pages/` cache
- Hydration behavior in delta mode:
  - hydrate only net-new URLs
  - skip already-cached URLs as `fresh`
  - for `/customers`, prioritize text write-ups and skip video/media payloads
- Tiering/classification behavior (required after hydration):
  - classify each external page into one of:
    - Tier A: high operational/workflow value (load full content by default)
    - Tier B: medium incremental value (store/load 5-line digest by default)
    - Tier C: low incremental value vs docs (metadata only by default)
  - generate/update:
    - `tier_manifest.json` (URL -> tier + scoring metadata)
    - `tier_a_urls.md`, `tier_b_digests.md`, `tier_c_urls.md`
  - default memory-load policy for future runs:
    - load Tier A full page content
    - load Tier B digest only
    - skip Tier C content unless `include all` is requested
- Update detection for subsequent scans:
  - primary key: canonical URL
  - secondary diagnostics: title, published date, first-seen timestamp

## Rate limits (required) — wiz-local MCP

- **Hard cap:** never exceed **10 requests per second** to the wiz-local MCP server (aggregate across parallel callers).
- **Slow start (recommended):** sleep **0.2–0.5 seconds** between calls (~**2–5** requests per second) until the run is stable; do not burst above **10/s** even briefly.
- After large doc-cache pulls, use `wiz_doc_cache_manager.py status`, review `./docs/ai/cache/wiz_mcp_server/manifest.json`, then rebuild vectors if needed:  
  `uv run python -m prestonotes_mcp.ingestion.build_vector_db --reset`

## 3.6) wiz-remote pacing and backoff (required)

- Apply pacing for **`wiz-remote`** independently from wiz-local (separate credentials and limits).
- Start **`wiz-remote`** at **15 concurrent requests**.
- If any request returns a limit signal (`429`, explicit throttling, or retry-after):
  - immediately reduce **`wiz-remote`** to **10 concurrent requests**
  - add pacing delay between batches for that server only
- Pacing ladder for **`wiz-remote`** after a limit event:
  - first limit event: `1s` inter-batch delay at concurrency `10`
  - repeated limit event: increase delay to `2s`, then `4s`, then `8s`
  - cap delay at `8s` unless the run still fails, then hold and record as unstable
- Stability criteria:
  - at least 3 consecutive clean batches (no throttling/timeouts) at the current setting
  - once stable, keep the current setting for the rest of the run (do not re-increase above `10` in the same run after a limit event)
- Always log pacing telemetry in run notes/output (starting concurrency, first limit signal, fallback concurrency, final stable delay).

## 4) Synthesis Rules
- Only include claims supported by either:
  - Internal/Case_Studies sources, or
  - Wiz docs evidence from MCP links.
- Tag factual lines using:
  - `[Verified: YYYY-MM-DD]`
  - `[Inferred: YYYY-MM-DD]`
  - `[Legacy: Needs Validation]`
- Separate sections for:
  - Product capabilities by domain
  - Competitive intelligence signals
  - Sales strategy and objection handling
  - Architecture and deployment patterns
  - SE enablement and discovery plays
  - Gaps requiring follow-up research

## 5) Output
- Ensure `./MyNotes/Internal/AI_Insights/` exists.
- Overwrite:
  - `./MyNotes/Internal/AI_Insights/Product-Intelligence.md`
- Required structure:
  - YAML header:
    - `last_updated`
    - `sources_ingested_total`
    - `sources_ingested_paths`
    - `wiz_docs_links_reviewed`
    - `confidence_summary`
  - Source inventory summary (from Section 2)
  - Wiz docs coverage ledger (from Section 3)
  - Wiz-remote enrichment cache summary (from Section 3.5), including:
    - tools executed
    - cache files written
    - entries reviewed
    - net-new IDs discovered
    - per-item files written by area (updates/preview/threat/rules/ext)
  - Delta-mode efficiency summary (from Section 2.7), including:
    - items skipped as fresh
    - items refreshed as stale
    - items fetched as missing
    - estimated API calls avoided
  - External page extraction quality summary (from Section 3.7):
    - content-first vs mixed vs script-heavy counts
    - list of script-heavy URLs needing enhanced render capture
  - External source discovery summary (from Section 3.8):
    - seed sources scanned
    - net-new URLs discovered
    - URLs hydrated vs skipped-as-fresh
    - tier counts (A/B/C)
    - Tier B digests generated
  - Intelligence sections (from Section 4)

## 6) Sync
- Mirror output to:
  - `$GDRIVE_BASE_PATH/Internal/AI_Insights/`
