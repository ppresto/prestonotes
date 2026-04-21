#!/usr/bin/env bash
# Cursor stdio entrypoint for wiz-local. Forces WIZ_DOTENV_PATH to this pack’s wiz-mcp.env.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"

# Prefer wiz-mcp/wiz-mcp.env; else legacy .cursor/wiz-mcp.env; else PrestoNotes .cursor/mcp.env (WIZ_* there).
DOTENV_FILE="${WIZ_MCP_DOTENV}"
if [[ ! -f "${DOTENV_FILE}" ]] && [[ -f "${REPO_ROOT}/.cursor/wiz-mcp.env" ]]; then
  DOTENV_FILE="${REPO_ROOT}/.cursor/wiz-mcp.env"
fi
if [[ ! -f "${DOTENV_FILE}" ]] && [[ -f "${REPO_ROOT}/.cursor/mcp.env" ]]; then
  DOTENV_FILE="${REPO_ROOT}/.cursor/mcp.env"
fi
if [[ ! -f "${DOTENV_FILE}" ]]; then
  echo "error: no credentials file. Copy wiz-mcp/wiz-mcp.env.example to wiz-mcp/wiz-mcp.env" >&2
  echo "  or place secrets at: ${WIZ_MCP_DOTENV}" >&2
  echo "  or: ${REPO_ROOT}/.cursor/wiz-mcp.env" >&2
  echo "  or add WIZ_CLIENT_ID / WIZ_CLIENT_SECRET / WIZ_ENV to: ${REPO_ROOT}/.cursor/mcp.env" >&2
  exit 1
fi

unset WIZ_DOTENV_PATH 2>/dev/null || true
export WIZ_DOTENV_PATH="${DOTENV_FILE}"

exec "${UV_BIN}" --directory "${WIZ_MCP_SERVER_DIR}" \
  run --with "mcp[cli]" mcp run server.py
