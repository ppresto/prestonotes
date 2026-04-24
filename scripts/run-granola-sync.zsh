#!/bin/zsh
# shellcheck shell=bash disable=SC1071
# Granola → MyNotes per-call transcripts (scripts/granola-sync.py, TASK-005 / v2 layout).
# Intended for Terminal and macOS Shortcuts: stdout is a Shortcuts-friendly summary; stderr has details.
set -euo pipefail

SCRIPT_DIR=${0:A:h}
# Same layout as scripts/rsync-gdrive-notes.sh: optional override, else repo root (parent of scripts/).
PROJECT_ROOT="${PRESTONOTES_REPO_ROOT:-${SCRIPT_DIR:h}}"
export PRESTONOTES_REPO_ROOT="$PROJECT_ROOT"
cd "$PROJECT_ROOT"

MCP_ENV="${PROJECT_ROOT}/.cursor/mcp.env"
if [[ -r $MCP_ENV ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$MCP_ENV"
  set +a
fi
# If still unset after mcp.env, match rsync-gdrive-notes.sh (Google Drive for Desktop default).
if [[ -z ${GDRIVE_BASE_PATH:-} ]]; then
  export GDRIVE_BASE_PATH="${HOME}/Google Drive/My Drive/MyNotes"
fi

if [[ -n ${UV_BIN-} && -x $UV_BIN ]]; then
  :
elif [[ -x /opt/homebrew/bin/uv ]]; then
  UV_BIN=/opt/homebrew/bin/uv
else
  UV_BIN=uv
fi

mkdir -p "$PROJECT_ROOT/logs"
tmp_base="$(mktemp "${TMPDIR:-/tmp}/granola-sync.XXXXXX")"
stdout_file="${tmp_base}.out"
stderr_file="${tmp_base}.err"
cleanup() { rm -f "$stdout_file" "$stderr_file" "$tmp_base"; }
trap cleanup EXIT

set +e
"$UV_BIN" run scripts/granola-sync.py \
  --log-dir "$PROJECT_ROOT/logs" \
  --stdout-format notify \
  "$@" >"$stdout_file" 2>"$stderr_file"
granola_exit=$?
set -e

if [[ -s $stderr_file ]]; then
  cat "$stderr_file" >&2
fi

# Shortcuts read stdout — emit notify line even on failure (Python writes it for early errors too).
if [[ -s $stdout_file ]]; then
  cat "$stdout_file"
fi

if [[ $granola_exit -ne 0 ]]; then
  echo 'Granola sync failed; skipping local pull sync.' >&2
  exit "$granola_exit"
fi
