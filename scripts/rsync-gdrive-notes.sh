#!/usr/bin/env bash
# rsync-gdrive-notes.sh — mirror Google Drive for Desktop "MyNotes" into the repo's MyNotes/ (TASK-006).
#
# Usage:
#   ./scripts/rsync-gdrive-notes.sh                  # full MyNotes tree
#   ./scripts/rsync-gdrive-notes.sh "CustomerName"   # only Customers/<CustomerName>/
#   ./scripts/rsync-gdrive-notes.sh --dry-run        # rsync dry-run only (no PDF OCR)
#   ./scripts/rsync-gdrive-notes.sh --dry-run "CustomerName"
#
# Env:
#   PRESTONOTES_REPO_ROOT — repo root (default: parent of scripts/)
#   GDRIVE_BASE_PATH      — local path to the Drive-mounted MyNotes folder (default: ~/Google Drive/My Drive/MyNotes)

set -uo pipefail

PROJECT_ROOT="${PRESTONOTES_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LOCAL_PATH="$PROJECT_ROOT/MyNotes"

GDRIVE_PATH="${GDRIVE_BASE_PATH:-$HOME/Google Drive/My Drive/MyNotes}"

DRY_RUN=0
CUSTOMER_NAME=""
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    DRY_RUN=1
    continue
  fi
  if [[ -n "${CUSTOMER_NAME}" ]]; then
    echo "Too many arguments (expected optional --dry-run and optional customer name)." >&2
    exit 1
  fi
  CUSTOMER_NAME="$arg"
done

if [[ -n "$CUSTOMER_NAME" ]]; then
  if [[ "$CUSTOMER_NAME" == *"/"* || "$CUSTOMER_NAME" == *".."* ]]; then
    echo "Invalid customer name (path separators or .. not allowed): $CUSTOMER_NAME" >&2
    exit 1
  fi
fi

if [[ ! -d "$GDRIVE_PATH" ]]; then
  echo "GDRIVE path not found: $GDRIVE_PATH" >&2
  echo "Set GDRIVE_BASE_PATH to your Drive-mounted MyNotes folder (see README)." >&2
  exit 1
fi

mkdir -p "$LOCAL_PATH"

RSYNC_EXCLUDES=(
  --exclude='[Bb]ackup*/'
  --exclude='*_OCR.md'
  --exclude='_seed_from_*/'
)

# `_TEST_CUSTOMER` is a committed E2E fixture customer in many dev setups. Google Drive may lag
# behind the repo's local per-call transcripts / call records. Without these excludes,
# `rsync --delete` would remove locally-added fixture files that are not yet on Drive.
if [[ "${CUSTOMER_NAME:-}" == "_TEST_CUSTOMER" ]]; then
  RSYNC_EXCLUDES+=(
    --exclude='Transcripts/[0-9][0-9][0-9][0-9]-*.txt'
    --exclude='call-records/*.json'
  )
fi

RSYNC_INCLUDES=(
  --include='*/'
  --include='*.md'
  --include='*.txt'
  --include='*.pdf'
  --include='*.png'
  --include='*.gif'
  --include='*.jpg'
  --include='*.jpeg'
  --exclude='*'
)

RSYNC_FLAGS=(-av --size-only --delete)
if [[ "$DRY_RUN" -eq 1 ]]; then
  RSYNC_FLAGS+=(-n)
fi

if [[ -n "$CUSTOMER_NAME" ]]; then
  SRC="$GDRIVE_PATH/Customers/$CUSTOMER_NAME/"
  DST="$LOCAL_PATH/Customers/$CUSTOMER_NAME/"
  if [[ ! -d "$SRC" ]]; then
    echo "Drive path not found (sync Google Drive for Desktop or check name): $SRC" >&2
    exit 1
  fi
  echo "Pulling Customers/$CUSTOMER_NAME/ from Google Drive -> local MyNotes ..."
  mkdir -p "$DST"
  if ! rsync "${RSYNC_FLAGS[@]}" \
    "${RSYNC_EXCLUDES[@]}" \
    "${RSYNC_INCLUDES[@]}" \
    "$SRC" "$DST"; then
    exit $?
  fi
  PDF_FIND_ROOT="$DST"
else
  echo "Pulling full MyNotes tree from Google Drive -> local MyNotes ..."
  if ! rsync "${RSYNC_FLAGS[@]}" \
    "${RSYNC_EXCLUDES[@]}" \
    "${RSYNC_INCLUDES[@]}" \
    "$GDRIVE_PATH/" "$LOCAL_PATH/"; then
    exit $?
  fi
  PDF_FIND_ROOT="$LOCAL_PATH"
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run complete (no file changes; PDF OCR skipped)."
  exit 0
fi

# Portable mtime (seconds) and display date for headers
_stat_mtime() {
  local f="$1"
  if stat --version >/dev/null 2>&1; then
    stat -c %Y "$f"
  else
    stat -f %m "$f"
  fi
}

_stat_date() {
  local f="$1"
  if stat --version >/dev/null 2>&1; then
    stat -c %y "$f" | cut -c1-10
  else
    stat -f %Sm -t "%Y-%m-%d" "$f"
  fi
}

_append_markitdown() {
  local pdf="$1"
  local out="$2"
  if command -v uv >/dev/null 2>&1 && (cd "$PROJECT_ROOT" && uv run markitdown "$pdf" >>"$out" 2>/dev/null); then
    return 0
  fi
  if command -v markitdown >/dev/null 2>&1 && markitdown "$pdf" >>"$out" 2>/dev/null; then
    return 0
  fi
  return 1
}

echo "Processing PDFs with MarkItDown (optional; install markitdown or skip)..."

while IFS= read -r -d '' pdf_file; do
  [[ -f "$pdf_file" ]] || continue
  md_file="${pdf_file%.pdf}_OCR.md"

  do_convert=true
  if [[ -f "$md_file" ]]; then
    if ! grep -q "SOURCE: LOCAL OCR" "$md_file" 2>/dev/null; then
      do_convert=true
    else
      pdf_time=$(_stat_mtime "$pdf_file")
      md_time=$(_stat_mtime "$md_file")
      diff=$((md_time - pdf_time))
      if [[ "$diff" -gt -300 ]]; then
        echo "Skipping $(basename "$pdf_file") (MD is up to date)"
        do_convert=false
      fi
    fi
  fi

  if [[ "$do_convert" == true ]]; then
    echo "Converting $(basename "$pdf_file") via MarkItDown..."
    mod_date=$(_stat_date "$pdf_file")
    echo "--- SOURCE: LOCAL OCR | FILE: $(basename "$pdf_file") | LAST_MODIFIED: $mod_date ---" >"$md_file"
    if ! _append_markitdown "$pdf_file" "$md_file"; then
      echo "WARNING: markitdown not available; install or use: uv tool install markitdown" >&2
      rm -f "$md_file"
    fi
  fi
done < <(find "$PDF_FIND_ROOT" -name "*.pdf" -type f -print0 2>/dev/null)

echo "Sync and local PDF conversion pass complete."
