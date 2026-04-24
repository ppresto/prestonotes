# shellcheck shell=bash
# Shared settings for wiz-mcp helper scripts. Copy to a new repo as-is; edit below or use config.local.sh.
#
# Optional overrides: copy config.local.example.sh → config.local.sh (gitignored).

# This directory (the wiz-mcp pack in your project)
WIZ_HELPER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project / git root (parent of wiz-mcp/)
# shellcheck disable=SC2034  # REPO_ROOT is exported/used by sibling helper scripts.
REPO_ROOT="$(cd "${WIZ_HELPER_ROOT}/.." && pwd)"

# --- Edit for your machine / clone paths ---
UV_BIN="${UV_BIN:-/opt/homebrew/bin/uv}"
# Cloned Wiz MCP repo (contains src/wiz_mcp_server/server.py)
WIZ_MCP_CHECKOUT="${WIZ_MCP_CHECKOUT:-${HOME}/Projects/wiz-mcp}"
# 1Password item for WIZ_CLIENT_ID / WIZ_CLIENT_SECRET (username + credential fields)
WIZ_OP_ITEM="${WIZ_OP_ITEM:-csaprod - presto-admin}"
# Auth host segment: app → auth.app.wiz.io
WIZ_ENV_DEFAULT="${WIZ_ENV_DEFAULT:-app}"
# 1Password field for client id (usually "username")
WIZ_OP_FIELD_ID="${WIZ_OP_FIELD_ID:-username}"

# --- Usually leave as defaults ---
WIZ_MCP_DOTENV="${WIZ_MCP_DOTENV:-${WIZ_HELPER_ROOT}/wiz-mcp.env}"
WIZ_MCP_SERVER_DIR="${WIZ_MCP_SERVER_DIR:-${WIZ_MCP_CHECKOUT}/src/wiz_mcp_server}"
WIZ_MCP_TMP="${WIZ_MCP_TMP:-${WIZ_HELPER_ROOT}/tmp}"
WIZ_REMOTE_MCP_URL="${WIZ_REMOTE_MCP_URL:-https://mcp.demo.wiz.io}"

if [[ -f "${WIZ_HELPER_ROOT}/config.local.sh" ]]; then
  # shellcheck source=/dev/null
  source "${WIZ_HELPER_ROOT}/config.local.sh"
fi
