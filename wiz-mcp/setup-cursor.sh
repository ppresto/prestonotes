#!/usr/bin/env bash
# Writes ../.cursor/mcp.json with absolute path to run-wiz-mcp-for-cursor.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"

CURSOR_DIR="${REPO_ROOT}/.cursor"
LAUNCHER="${SCRIPT_DIR}/run-wiz-mcp-for-cursor.sh"
OUT="${CURSOR_DIR}/mcp.json"

[[ -x "${LAUNCHER}" ]] || chmod +x "${LAUNCHER}" 2>/dev/null || true

mkdir -p "${CURSOR_DIR}"

cat >"${OUT}" <<EOF
{
  "mcpServers": {
    "wiz-local": {
      "disabled": false,
      "timeout": 60,
      "command": "${LAUNCHER}",
      "args": [],
      "transportType": "stdio"
    },
    "wiz-remote": {
      "disabled": false,
      "timeout": 60,
      "transportType": "http",
      "url": "${WIZ_REMOTE_MCP_URL}"
    }
  }
}
EOF

echo "Wrote ${OUT}"
echo "  wiz-local command: ${LAUNCHER}"
echo "  wiz-remote url: ${WIZ_REMOTE_MCP_URL}"
echo "Reload Cursor (Developer → Reload Window)."
