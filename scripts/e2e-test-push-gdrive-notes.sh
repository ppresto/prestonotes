#!/usr/bin/env bash
# e2e-test-push-gdrive-notes.sh — Push repo MyNotes/ → Google Drive for Desktop "MyNotes" (reverse of rsync-gdrive-notes.sh).
#
# Usage:
#   ./scripts/e2e-test-push-gdrive-notes.sh "CustomerName"
#   ./scripts/e2e-test-push-gdrive-notes.sh --dry-run "CustomerName"
#
# Env:
#   PRESTONOTES_REPO_ROOT — repo root (default: parent of scripts/)
#   GDRIVE_BASE_PATH      — local path to the Drive-mounted MyNotes folder (see rsync-gdrive-notes.sh)

set -euo pipefail

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
    echo "Too many arguments (expected optional --dry-run and customer name)." >&2
    exit 1
  fi
  CUSTOMER_NAME="$arg"
done

if [[ -z "$CUSTOMER_NAME" ]]; then
  echo "Customer name is required (scoped push only)." >&2
  exit 1
fi
if [[ "$CUSTOMER_NAME" == *"/"* || "$CUSTOMER_NAME" == *".."* ]]; then
  echo "Invalid customer name (path separators or .. not allowed): $CUSTOMER_NAME" >&2
  exit 1
fi

if [[ ! -d "$GDRIVE_PATH" ]]; then
  echo "GDRIVE path not found: $GDRIVE_PATH" >&2
  echo "Set GDRIVE_BASE_PATH to your Drive-mounted MyNotes folder (see README). Start Google Drive for Desktop if needed." >&2
  prestonotes_gdrive_auth_hint
  exit 1
fi

if [[ ! -d "$LOCAL_PATH/Customers/$CUSTOMER_NAME" ]]; then
  echo "Local customer folder not found: $LOCAL_PATH/Customers/$CUSTOMER_NAME" >&2
  exit 1
fi

mkdir -p "$GDRIVE_PATH/Customers/$CUSTOMER_NAME"

RSYNC_EXCLUDES=(
  --exclude='[Bb]ackup*/'
  --exclude='*_OCR.md'
  --exclude='_seed_from_*/'
)

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

RSYNC_FLAGS=(-av --delete)
if [[ "$DRY_RUN" -eq 1 ]]; then
  RSYNC_FLAGS+=(-n)
fi

SRC="$LOCAL_PATH/Customers/$CUSTOMER_NAME/"
DST="$GDRIVE_PATH/Customers/$CUSTOMER_NAME/"

echo "Pushing Customers/$CUSTOMER_NAME/ from repo MyNotes -> Google Drive ..."
if ! rsync "${RSYNC_FLAGS[@]}" \
  "${RSYNC_EXCLUDES[@]}" \
  "${RSYNC_INCLUDES[@]}" \
  "$SRC" "$DST"; then
  exit $?
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run complete (no file changes)."
fi

echo "Push complete."
