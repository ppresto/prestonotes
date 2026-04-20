# TASK-005 — Port `granola-sync.py` + per-call `Transcripts/*.txt`

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-17) |
| **Spec reference** | [`project_spec.md` §9 — TASK-005](../../project_spec.md#task-005--port-the-granola-sync-script) |

## What shipped

- **`scripts/granola-sync.py`** — Reads Granola macOS cache JSON (`cache-v4` / `cache-v3` or **`GRANOLA_CACHE_PATH`**); writes per-call `Transcripts/YYYY-MM-DD-<slug>.txt` under **`{GDRIVE_BASE_PATH}/Customers/<folder>/`**. Internal folder routing via **`GRANOLA_INTERNAL_FOLDER_NAMES`** / **`GRANOLA_INTERNAL_CUSTOMER_NAME`**. Idempotent overwrite when header `granola_meeting_id` matches.
- **`scripts/run-granola-sync.sh`** — Wrapper: repo root + `uv run scripts/granola-sync.py`.
- **`scripts/tests/test_granola_sync.py`** — Idempotency, Internal routing, collision, CLI.
- **`[tool.pytest.ini_options]`** in root **`pyproject.toml`** includes **`scripts/tests`**.
- **`prestonotes_mcp/server.py`** — **`sync_transcripts`** returns JSON hint if `scripts/granola-sync.py` is missing.
- **`docs/MIGRATION_GUIDE.md`** — Granola section + discrepancies row.
- **`README.md`** — Documents **`sync_transcripts`** vs TASK-006 **`sync_notes`**.

Legacy **`../prestoNotes.orig/scripts/granola-sync.py`** was not present in this workspace; implementation follows the Granola cache shape documented in the ecosystem (nested `cache` string → `state.documents` / `state.transcripts`, folder names on documents).

## Follow-up

- **TASK-006** — `rsync-gdrive-notes.sh` and related so **`sync_notes`** runs end-to-end.
