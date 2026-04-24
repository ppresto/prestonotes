#!/usr/bin/env bash
# Writes wiz-mcp.env from 1Password (requires: op signed in, --reveal for concealed secrets).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"

OP_ITEM="${WIZ_OP_ITEM}"
WIZ_ENV_VALUE="${WIZ_ENV:-${WIZ_ENV_DEFAULT}}"
OUT="${WIZ_MCP_DOTENV}"

mkdir -p "$(dirname "${OUT}")"
mkdir -p "${WIZ_MCP_TMP}"

if ! command -v op >/dev/null 2>&1; then
  echo "error: 1Password CLI (op) not in PATH" >&2
  exit 1
fi

_clean() { tr -d '\r\n' | sed 's/[[:space:]]*$//'; }

_secret() {
  local item="$1" v=""
  if [[ -n "${WIZ_OP_FIELD_SECRET:-}" ]]; then
    op item get "${item}" --fields "${WIZ_OP_FIELD_SECRET}" --reveal 2>/dev/null | _clean
    return
  fi
  for f in credential password; do
    v="$(op item get "${item}" --fields "$f" --reveal 2>/dev/null | _clean)"
    [[ -n "${v}" && ${#v} -ge 16 && "${v}" != *"use 'op item get"* ]] && { echo "${v}"; return 0; }
  done
  echo ""
}

CID="$(op item get "${OP_ITEM}" --fields "${WIZ_OP_FIELD_ID}" 2>/dev/null | _clean)"
CSEC="$(_secret "${OP_ITEM}")"

[[ -n "${CID}" ]] || { echo "error: empty client id (op item \"${OP_ITEM}\" field \"${WIZ_OP_FIELD_ID}\")" >&2; exit 1; }
[[ -n "${CSEC}" && "${CSEC}" != *"use 'op"* ]] || {
  echo "error: empty/masked secret — use: op item get \"${OP_ITEM}\" --fields credential --reveal" >&2
  exit 1
}

umask 077
printf 'WIZ_CLIENT_ID=%s\nWIZ_CLIENT_SECRET=%s\nWIZ_ENV=%s\n' "${CID}" "${CSEC}" "${WIZ_ENV_VALUE}" >"${OUT}.tmp"
mv "${OUT}.tmp" "${OUT}"
chmod 600 "${OUT}" 2>/dev/null || true

echo "Wrote ${OUT} (item=${OP_ITEM}, WIZ_ENV=${WIZ_ENV_VALUE}). Reload Cursor."
