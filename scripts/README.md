# Scripts (PrestoNotes)

## `rsync-gdrive-notes.sh` (Drive → repo `MyNotes/`)

This script **pulls** from your **Google Drive for Desktop** mount into **`$PRESTONOTES_REPO_ROOT/MyNotes/`** so MCP read tools and local editors see the same tree as on Drive.

**Push (repo → Drive):** use **`e2e-test-push-gdrive-notes.sh`** for a **scoped customer** mirror (see script header; E2E-prefixed name because the primary consumer is the `_TEST_CUSTOMER` prep loop). Full-tree push is intentionally not exposed here.

**Environment**

- **`GDRIVE_BASE_PATH`** — Path to the **MyNotes** folder as mounted by Drive for desktop (same value as in **`.cursor/mcp.env`**).
- **`PRESTONOTES_REPO_ROOT`** — Repo root (defaults to the parent of `scripts/`).

**Examples** (from repo root)

```bash
export GDRIVE_BASE_PATH="/path/to/My Drive/MyNotes"
./scripts/rsync-gdrive-notes.sh                    # full tree
./scripts/rsync-gdrive-notes.sh "CustomerName"     # one customer under Customers/
./scripts/rsync-gdrive-notes.sh --dry-run          # rsync dry-run only (no PDF OCR)
./scripts/rsync-gdrive-notes.sh --dry-run "CustomerName"
```

**Push** (repo → Drive, one customer):

```bash
export GDRIVE_BASE_PATH="/path/to/My Drive/MyNotes"
./scripts/e2e-test-push-gdrive-notes.sh "CustomerName"
./scripts/e2e-test-push-gdrive-notes.sh --dry-run "CustomerName"
```

Optional **PDF → `_OCR.md`** uses **MarkItDown** if available (`uv run markitdown` from the repo, or `markitdown` on `PATH`). Dry-run skips OCR.

## `restart-google-drive.sh` (macOS)

Restarts the **Google Drive** app after a short wait so the local mount picks up API-created folders. Use when bootstrap or Drive UI changes are slow to appear.

```bash
./scripts/restart-google-drive.sh      # wait 10s
./scripts/restart-google-drive.sh 20 # wait 20s
```

## `syncNotesToMarkdown.js` (Google Apps Script)

**Not a Node script.** Deploy into **Apps Script** bound to a Drive project (or standalone). Set Script property **`MYNOTES_ROOT_FOLDER_ID`** to your MyNotes root folder ID (same as **`MYNOTES_ROOT_FOLDER_ID`** in **`.cursor/mcp.env`**). Enable the **Drive API** advanced service for PDF OCR. Schedule **`syncNotesToMarkdown`** if you want periodic GDoc → `.md` exports on Drive.

**Linting:** this file is **not** linted as Node/ESM (Google **Apps Script**). The repo does not run a JS linter on it in CI; use the Apps Script editor or your own checks if you change it.

Local markdown in **`MyNotes/Customers/.../[Customer] Notes.md`** is what most MCP read paths expect after export + rsync.

## Other

- **`granola-sync.py`** — Granola cache → per-call `Transcripts/*.txt` under **`GDRIVE_BASE_PATH`** (TASK-005). **`--log-dir ./logs`** appends **`granola-sync.log`**: hash **`# ===`** banner + **`RUN_START:`**, then a short **`# Status meanings`** block, then lines **`YYYY-MM-DDTHH:MMZ STATUS: details`** (UTC minute) (`RUN:`, **`SYNC_NEW:`** / **`SYNC_UPD:`** with `title=…, file=…, path=…`, **`SKIP:`**, **`END:`** with `new=` / `updated=`). **`--write-last-json`** opt-in restores **`granola-sync-last.json`**. **`--log-max-lines`** caps how many SYNC/SKIP lines are logged. Re-runs that only overwrite existing files get a **short** notify line and a **one-line** stderr summary; use **`--no-human-summary`** to silence stderr paths. Notes fallback, title-prefix routing, and envs **`GRANOLA_NOTES_FALLBACK`** / **`GRANOLA_TITLE_PREFIX_CUSTOMER`** unchanged from prior docs. **`--stdout-format notify`** for Shortcuts.
- **`run-granola-sync.zsh`** — Loads **`.cursor/mcp.env`**, runs sync with **`--log-dir`** and **`--stdout-format notify`**; stdout = summary, stderr = human details (quiet when only in-place updates).
- **E2E `_TEST_CUSTOMER` harness:** canonical procedure **`docs/ai/playbooks/tester-e2e-ucn.md`**; entry script **`./scripts/e2e-test-customer.sh`** (`prep-v1` / `prep-v2` / `reset` / `list-steps`). The old overlapping scripts (`e2e-test-customer-prep.sh`, `e2e-reset-test-customer-drive.sh`, `e2e-full-validation.*`, `e2e-test-customer-report.py`, `e2e-test-customer-verify.py`, `refresh_test_customer.py`, `seed-test-customer-challenge-lifecycle.py`, …) have been removed.
- **`e2e-test-customer-materialize.py`** (kept as library) — **`to-fixtures`**: copy **`MyNotes/Customers/_TEST_CUSTOMER/Transcripts`** → **`tests/fixtures/e2e/_TEST_CUSTOMER/v1/Transcripts`** only. **`apply`**: copy v1 (and optional v2) **transcripts** into **`MyNotes/...`**; clears **`call-records/*.json` on v1** apply; never copies call-record JSON from git fixtures. Optional **`--v2`** merges **`v2/Transcripts/`** while preserving round-1 extracts. See **`tests/fixtures/e2e/_TEST_CUSTOMER/README.md`**.
- **`e2e-test-customer-bump-dates.py`** (kept as library) — rewrites **`Transcripts/YYYY-MM-DD-*.txt`** basenames + matching **`call-records/*.json`** so rolling "last 30 days" windows stay populated. **Narrative order is preserved:** after a bump, **oldest** story → **earliest** new calendar date in the window, **newest** story → **latest** (so filename sort matches call order).
- **`e2e-test-push-gdrive-notes.sh`** (kept as library) — push repo **`MyNotes/Customers/<name>/`** → Google Drive for Desktop mount.
- **`ucn-prep.py`** — UCN prep handoff: writes **`notes-lite.md`** (Account Summary + Account Metadata regions, Daily Activity omitted, long line / image URL filters) and **`handoff.json`** (`notes_lite_path`, `ledger_path`, `transcript_paths`, optional `bundle_id`). **Default:** newest per-call transcript plus `--priors` older files; warns if `_MASTER_*.txt` exists. **`bundle --window 1w|1m|3m|1y`:** splits `_MASTER_*.txt` into `YYYY-MM-DD-*.txt` (same body shape as `granola-sync.py`), partitions by timeline buckets, writes **`migration-state.json`**; **`--advance`** completes the current bundle and moves to the next. Use **`--out`** for durable runs (e.g. under `MyNotes/Customers/<C>/tmp/ucn/…`). Optional env: **`PRESTONOTES_REPO_ROOT`**, **`PRESTONOTES_UCN_PREP_OUT`**.
- **`ucn-planner-preflight.py`** — validates planner contract on a mutation JSON before `write_doc`:
  - TASK-072 gates: DAL parity + Deal Stage trigger path.
  - TASK-073 gates: canonical section/subsection coverage decisions (`planner_contract.coverage.decisions`) for the **full** matrix (`required_in_ucn_full` in `TARGET_MATRIX`); `planner_contract.ucn_mode` other than `full` is **ignored** (stderr warning). Allowed skip reasons, per-target action checks, and strict metadata evidence checks.
  - Exit `0` = `planner_contract_ok`, exit `2` = `planner_contract_failed:*`.
- **`wiz_cache_manager.py`** — Canonical Wiz cache CLI (manifest upserts, `status`, `refresh-loop`, `vector-index-status`, `kb-snapshot ...`). Legacy shim: `wiz_doc_cache_manager.py`.
- **`materialize_licensing_kb_snapshots.py`** — Optional offline rebuild of TASK-074 **licensing** KB envelopes from `kb_licensing_seed_sources/` (`meta.json` + `bodies/*.md`). Use `--ingest-incoming` to build those from `_incoming/*.mcp.json` first. When you have MCP, prefer `kb-snapshot save` directly (§2.595).
- **`lpi_kb_seed_refresh.py`** — **Shim only (exit 2).** Archived implementation: `scripts/deprecated/lpi_kb_seed_refresh.py`. Use **Cursor `wiz-remote` MCP** + `wiz_cache_manager.py kb-snapshot save` (optional `--slice-top-k`) per `load-product-intelligence.md` §2.59.
- **`wiz_vector_coverage_report.py`** — Compare **`manifest.json`** `doc:*` rows to files under **`docs/ai/cache/wiz_mcp_server/docs/`** and optional Chroma **`wiz_docs`** collection (`--repo-root .`).
- **`wiz_docs_search_cli.py`** — **`search_wiz_docs`**-equivalent: OAuth + **`aiAssistantQuery`** using **`WIZ_*`** from **`.cursor/mcp.env`** (for shells/agents without Cursor MCP stdio). Example: `uv run python scripts/wiz_docs_search_cli.py --query "What is Wiz Defend?"`.
- **`wiz_docs_client.py`** — Shared OAuth + GraphQL + response parsing for the above and for materialization.
- **`materialize_wiz_mcp_docs.py`** — Writes **`docs/ai/cache/wiz_mcp_server/mcp_materializations/<doc_name>.md`** from DOCS search (no **`docs.wiz.io`** HTTP). Options: `--dry-run`, `--min-age-days`, `--force`, `--doc-name`, `--delay-seconds`.
- **`spider_wiz_external_pages.py`** — Fetches **`www.wiz.io`** (and allowlisted) URLs from **`ext/indexes/tier_manifest.json`** into **`ext/pages/`**; manifest TTL **365** days for those URLs. Also: **`wiz_cache_manager.py spider-ext`** / **`mcp-materialize`**.
