# Scripts (PrestoNotes)

## `rsync-gdrive-notes.sh` (Drive → repo `MyNotes/`)

Bidirectional mirror is **not** implemented here: this script **pulls** from your **Google Drive for Desktop** mount into **`$PRESTONOTES_REPO_ROOT/MyNotes/`** so MCP read tools and local editors see the same tree as on Drive.

**Environment**

- **`GDRIVE_BASE_PATH`** — Path to the **MyNotes** folder as mounted by Drive for desktop (same value as in **`.cursor/mcp.json`** `env`).
- **`PRESTONOTES_REPO_ROOT`** — Repo root (defaults to the parent of `scripts/`).

**Examples** (from repo root)

```bash
export GDRIVE_BASE_PATH="/path/to/My Drive/MyNotes"
./scripts/rsync-gdrive-notes.sh                    # full tree
./scripts/rsync-gdrive-notes.sh "CustomerName"     # one customer under Customers/
./scripts/rsync-gdrive-notes.sh --dry-run          # rsync dry-run only (no PDF OCR)
./scripts/rsync-gdrive-notes.sh --dry-run "CustomerName"
```

Optional **PDF → `_OCR.md`** uses **MarkItDown** if available (`uv run markitdown` from the repo, or `markitdown` on `PATH`). Dry-run skips OCR.

## `restart-google-drive.sh` (macOS)

Restarts the **Google Drive** app after a short wait so the local mount picks up API-created folders. Use when bootstrap or Drive UI changes are slow to appear.

```bash
./scripts/restart-google-drive.sh      # wait 10s
./scripts/restart-google-drive.sh 20 # wait 20s
```

## `syncNotesToMarkdown.js` (Google Apps Script)

**Not a Node script.** Deploy into **Apps Script** bound to a Drive project (or standalone). Set Script property **`MYNOTES_ROOT_FOLDER_ID`** to your MyNotes root folder ID (same as **`MYNOTES_ROOT_FOLDER_ID`** in **`.cursor/mcp.json`**). Enable the **Drive API** advanced service for PDF OCR. Schedule **`syncNotesToMarkdown`** if you want periodic GDoc → `.md` exports on Drive.

Local markdown in **`MyNotes/Customers/.../[Customer] Notes.md`** is what most MCP read paths expect after export + rsync.

## Other

- **`granola-sync.py`** — Granola cache → per-call `Transcripts/*.txt` under **`GDRIVE_BASE_PATH`** (TASK-005).
- **`run-granola-sync.sh`** — Wrapper around **`uv run scripts/granola-sync.py`**.
