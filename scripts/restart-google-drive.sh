#!/usr/bin/env bash
# Nudge the Google Drive for Desktop app to sync after API-side folder/doc creation (TASK-006).
# macOS only (uses osascript/open/killall).
#
# Usage:
#   ./scripts/restart-google-drive.sh          # wait 10s (default), then restart
#   ./scripts/restart-google-drive.sh 15       # wait 15s, then restart

set -euo pipefail

WAIT_SECONDS="${1:-10}"

if ! [[ "$WAIT_SECONDS" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 [seconds_to_wait]" >&2
  exit 1
fi

echo "Waiting ${WAIT_SECONDS}s before restarting Google Drive (helps local mount catch up)..."
sleep "$WAIT_SECONDS"

echo "Restarting Google Drive..."
killall "Google Drive" 2>/dev/null || true
sleep 3
open -a "Google Drive"

echo "Google Drive relaunched. Allow it to finish syncing, then run ./scripts/rsync-gdrive-notes.sh or ./scripts/rsync-gdrive-notes.sh \"CustomerName\" as needed."
