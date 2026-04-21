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

- **`granola-sync.py`** — Granola cache → per-call `Transcripts/*.txt` under **`GDRIVE_BASE_PATH`** (TASK-005). Optional **`--log-dir ./logs`** appends **`granola-sync.log`** and writes **`granola-sync-last.json`**. Use **`--stdout-format notify`** for a one-line summary on stdout (macOS Shortcuts).
- **`run-granola-sync.zsh`** — Loads **`.cursor/mcp.env`**, runs sync with **`--log-dir`** and **`--stdout-format notify`**, prints the summary on stdout for Shortcuts and per-file details on stderr.
- **E2E `_TEST_CUSTOMER` harness:** under reconstruction per **`docs/tasks/active/TASK-044-e2e-test-customer-rebuild.md`**. The old overlapping scripts (`e2e-test-customer.sh`, `e2e-test-customer-prep.sh`, `e2e-reset-test-customer-drive.sh`, `e2e-full-validation.*`, `e2e-test-customer-report.py`, `e2e-test-customer-verify.py`, `refresh_test_customer.py`, `seed-test-customer-challenge-lifecycle.py`) and their unit tests have been removed. The Phase-2 build will provide a single entry `scripts/e2e-test-customer.sh <reset|v1|v2>`.
- **`e2e-test-customer-materialize.py`** (kept as library) — **`to-fixtures`**: copy **`MyNotes/Customers/_TEST_CUSTOMER/{Transcripts,call-records}`** → **`tests/fixtures/e2e/_TEST_CUSTOMER/v1/`** (versioned baseline). **`apply`**: copy **`v1/`** into **`MyNotes/...`**, optional **`--v2`** to merge **`tests/fixtures/e2e/_TEST_CUSTOMER/v2/Transcripts/`** only (call-records come from round-2 extract). See **`tests/fixtures/e2e/_TEST_CUSTOMER/README.md`**.
- **`e2e-test-customer-bump-dates.py`** (kept as library) — rewrites **`Transcripts/YYYY-MM-DD-*.txt`** basenames + matching **`call-records/*.json`** so rolling "last 30 days" windows stay populated.
- **`e2e-test-push-gdrive-notes.sh`** (kept as library) — push repo **`MyNotes/Customers/<name>/`** → Google Drive for Desktop mount.
- **`wiz_doc_cache_manager.py`** — Wiz cache **`manifest.json`** upserts / **`status`** / **`refresh-loop`** / **`vector-index-status`** (see **`docs/ai/references/wiz-doc-lookup-protocol.md`**).
- **`wiz_vector_coverage_report.py`** — Compare **`manifest.json`** `doc:*` rows to files under **`docs/ai/cache/wiz_mcp_server/docs/`** and optional Chroma **`wiz_docs`** collection (`--repo-root .`).
- **`wiz_docs_search_cli.py`** — **`search_wiz_docs`**-equivalent: OAuth + **`aiAssistantQuery`** using **`WIZ_*`** from **`.cursor/mcp.env`** (for shells/agents without Cursor MCP stdio). Example: `uv run python scripts/wiz_docs_search_cli.py --query "What is Wiz Defend?"`.
- **`wiz_docs_client.py`** — Shared OAuth + GraphQL + response parsing for the above and for materialization.
- **`materialize_wiz_mcp_docs.py`** — Writes **`docs/ai/cache/wiz_mcp_server/mcp_materializations/<doc_name>.md`** from DOCS search (no **`docs.wiz.io`** HTTP). Options: `--dry-run`, `--min-age-days`, `--force`, `--doc-name`, `--delay-seconds`.
- **`spider_wiz_external_pages.py`** — Fetches **`www.wiz.io`** (and allowlisted) URLs from **`ext/indexes/tier_manifest.json`** into **`ext/pages/`**; manifest TTL **365** days for those URLs. Also: **`wiz_doc_cache_manager.py spider-ext`** / **`mcp-materialize`**.

