#!/usr/bin/env bash
# rsync-gdrive-notes.sh — mirror Google Drive for Desktop "MyNotes" into the repo's MyNotes/ (TASK-006).
#
# Recommended workflow: pull (this script) → run MCP / playbooks (creates ledger, lifecycle, logs on
# first use) → push (../e2e-test-push-gdrive-notes.sh) so Drive holds the last finished state. Pull
# uses "protect" filters so local files not yet on Drive are not removed by --delete; push copies
# them to Drive. JSON is included in both directions.
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

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${_SCRIPT_DIR}/lib/gdrive-auth-hint.sh"
PROJECT_ROOT="${PRESTONOTES_REPO_ROOT:-$(cd "${_SCRIPT_DIR}/.." && pwd)}"
prestonotes_source_mcp_env "${PROJECT_ROOT}"

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
  echo "Set GDRIVE_BASE_PATH to your Drive-mounted MyNotes folder (see README). Start Google Drive for Desktop if needed." >&2
  prestonotes_gdrive_auth_hint
  exit 1
fi

mkdir -p "$LOCAL_PATH"

RSYNC_EXCLUDES=(
  --exclude='[Bb]ackup*/'
  --exclude='*_OCR.md'
  --exclude='_seed_from_*/'
)

# Receiver-side "protect" (rsync `P` rule): do not DELETE these on the local repo if Google Drive
# does not have a copy yet — but if Drive *does* have a copy, normal transfer still updates local.
# This matches the desired flow: pull latest from Drive, edit locally, push; without losing files
# mid-pipeline. Do NOT use `--exclude` here: that would block *receiving* a newer file from Drive.
# See `man rsync` (protect / risk filter rules).
RSYNC_PROTECT=(
  --filter='P Customers/*/AI_Insights/*-History-Ledger.md'
  --filter='P AI_Insights/*-History-Ledger.md'
  --filter='P Customers/*/AI_Insights/challenge-lifecycle.json'
  --filter='P AI_Insights/challenge-lifecycle.json'
  --filter='P Customers/*/pnotes_agent_log.md'
  --filter='P pnotes_agent_log.md'
  --filter='P pnotes_agent_log.archive.md'
)

# E2E (`_TEST_CUSTOMER`): do **not** special-case rsync here. Reset / re-seed transcripts and
# call-records with `scripts/e2e-test-customer-materialize.py apply` (v1 or v2) from
# `tests/fixtures/e2e/_TEST_CUSTOMER/`, invoked by `./scripts/e2e-test-customer.sh prep-v1` / `prep-v2`.
# After a normal pull, that materialize step replaces the per-call corpus from fixtures; push when
# you need Drive to match the repo (same as any customer).

# Include JSON so `AI_Insights/challenge-lifecycle.json` and other .json round-trip; push already
# included *.json — pull must match for stable state. Per-file "protect" above prevents --delete
# from wiping a local-only JSON before the next push.
RSYNC_INCLUDES=(
  --include='*/'
  --include='*.md'
  --include='*.txt'
  --include='*.json'
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
    "${RSYNC_PROTECT[@]}" \
    "${RSYNC_EXCLUDES[@]}" \
    "${RSYNC_INCLUDES[@]}" \
    "$SRC" "$DST"; then
    exit $?
  fi
  PDF_FIND_ROOT="$DST"
else
  echo "Pulling full MyNotes tree from Google Drive -> local MyNotes ..."
  if ! rsync "${RSYNC_FLAGS[@]}" \
    "${RSYNC_PROTECT[@]}" \
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
