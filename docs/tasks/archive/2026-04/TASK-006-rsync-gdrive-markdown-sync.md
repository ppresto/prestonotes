# TASK-006 — Port rsync / GDrive / markdown sync scripts

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-19) |
| **Spec reference** | [`project_spec.md` §9 — TASK-006](../../project_spec.md#task-006--port-the-rsync-and-gdrive-sync-scripts) |
| **Build plan gate** | [`V2_MVP_BUILD_PLAN.md`](../../V2_MVP_BUILD_PLAN.md) — row **006**: `rsync-gdrive-notes.sh --dry-run` works |

## Goal

Ship the three legacy scripts so the **local `MyNotes/` tree** (under the repo or via `GDRIVE_BASE_PATH`) can stay in sync with **Google Drive**, and the MCP tool **`sync_notes`** runs end-to-end instead of returning a missing-script error.

## Legacy reference (read-only)

| v2 path | Legacy source |
|---------|---------------|
| `scripts/rsync-gdrive-notes.sh` | `../prestoNotes.orig/scripts/rsync-gdrive-notes.sh` |
| `scripts/restart-google-drive.sh` | `../prestoNotes.orig/scripts/restart-google-drive.sh` |
| `scripts/syncNotesToMarkdown.js` | `../prestoNotes.orig/scripts/syncNotesToMarkdown.js` |

## What shipped

- **`scripts/rsync-gdrive-notes.sh`** — Pull from **`GDRIVE_BASE_PATH`** into **`$PRESTONOTES_REPO_ROOT/MyNotes/`**; optional customer folder; **`--dry-run`** (rsync `-n`, skips PDF OCR); no `.venv` activation; portable **`stat`**; optional MarkItDown via **`uv run markitdown`** or **`markitdown`** on `PATH`; fails fast if Drive mount path missing.
- **`scripts/restart-google-drive.sh`** — macOS Drive app restart (ported).
- **`scripts/syncNotesToMarkdown.js`** — Google Apps Script: **`MYNOTES_ROOT_FOLDER_ID`** from Script Properties (no hardcoded folder ID in repo); **`biome.json`** excludes this file from Biome (not Node).
- **`scripts/README.md`** — Operator docs for all three.
- **`scripts/tests/test_rsync_gdrive_notes.py`** — Dry-run + real rsync against tmp fixtures (skip if no `rsync`).
- **`prestonotes_mcp/tests/test_server_write_tools.py`** — **`repo_ctx_gdrive`** + **`test_sync_notes_runs_rsync_for_customer`** (skip if no `rsync`).
- **`scripts/ci/required-paths.manifest`** — Lists the three script paths.
- **`README.md`**, **`docs/MIGRATION_GUIDE.md`** — Drive ↔ repo mirror section and MCP **`sync_notes`** pointer.

## Scope checklist

- [x] **`scripts/rsync-gdrive-notes.sh`**
- [x] **`scripts/restart-google-drive.sh`**
- [x] **`scripts/syncNotesToMarkdown.js`**
- [x] **`sync_notes` MCP tool** verified with fixture + rsync
- [x] **`scripts/ci/required-paths.manifest`**
- [x] **`README.md`**
- [x] **`docs/MIGRATION_GUIDE.md`**

## Verification run (post-`/tester`)

- `uv run pytest` (full suite) — **28 passed**
- `bash .cursor/skills/lint.sh` — passed (`shellcheck` on `scripts/*.sh`)
- `bash scripts/ci/check-repo-integrity.sh` — passed

## Follow-up

- **TASK-007** — Cursor rules + MVP playbooks
