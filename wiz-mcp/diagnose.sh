#!/usr/bin/env bash
# OAuth + short MCP smoke. Artifacts under wiz-mcp/tmp/ (no secret values printed).
# WIZ_OAUTH_VERBOSE=1 → curl -v log in tmp (may contain POST body — do not share).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"

mkdir -p "${WIZ_MCP_TMP}"
DOTENV="${WIZ_MCP_DOTENV}"
if [[ ! -f "${DOTENV}" ]] && [[ -f "${REPO_ROOT}/.cursor/wiz-mcp.env" ]]; then
  DOTENV="${REPO_ROOT}/.cursor/wiz-mcp.env"
fi
if [[ ! -f "${DOTENV}" ]] && [[ -f "${REPO_ROOT}/.cursor/mcp.env" ]]; then
  DOTENV="${REPO_ROOT}/.cursor/mcp.env"
fi
PID=$$
HDR="${WIZ_MCP_TMP}/oauth-${PID}.hdr"
BODY="${WIZ_MCP_TMP}/oauth-${PID}.body"

echo "=== dotenv ==="
echo "  ${DOTENV}"
if [[ -f "${DOTENV}" ]]; then
  echo "  ok ($(wc -c <"${DOTENV}" | tr -d ' ') bytes); keys: $(grep -E '^[A-Z_]+=' "${DOTENV}" 2>/dev/null | cut -d= -f1 | tr '\n' ' ')"
else
  echo "  MISSING — run ./write-wiz-dotenv.sh, copy wiz-mcp.env.example → wiz-mcp.env, or add WIZ_* to ../.cursor/mcp.env"
fi

echo
echo "=== uv + server ==="
[[ -x "${UV_BIN}" ]] && echo "  uv: ${UV_BIN}" || echo "  MISSING: ${UV_BIN}"
[[ -f "${WIZ_MCP_SERVER_DIR}/server.py" ]] && echo "  server.py: ${WIZ_MCP_SERVER_DIR}" || echo "  MISSING server.py — set WIZ_MCP_CHECKOUT in config.sh"

echo
echo "=== OAuth (expect HTTP 200) ==="
if [[ ! -f "${DOTENV}" ]]; then
  echo "  skip"
else
  WIZ_CLIENT_ID="$(sed -n 's/^WIZ_CLIENT_ID=//p' "${DOTENV}" | head -1 | tr -d '\r\n' | sed 's/[[:space:]]*$//')"
  WIZ_CLIENT_SECRET="$(sed -n 's/^WIZ_CLIENT_SECRET=//p' "${DOTENV}" | head -1 | tr -d '\r\n' | sed 's/[[:space:]]*$//')"
  WIZ_ENV_VAL="$(sed -n 's/^WIZ_ENV=//p' "${DOTENV}" | head -1 | tr -d '\r\n' | sed 's/[[:space:]]*$//')"
  WIZ_ENV_VAL="${WIZ_ENV_VAL:-${WIZ_ENV_DEFAULT}}"
  if [[ -z "${WIZ_CLIENT_ID}" || -z "${WIZ_CLIENT_SECRET}" ]]; then
    echo "  skip — empty id/secret in file"
  else
    echo "  lengths: client_id=${#WIZ_CLIENT_ID} client_secret=${#WIZ_CLIENT_SECRET}"
    rm -f "${HDR}" "${BODY}"
    CURL=( -sS -g -D "${HDR}" -o "${BODY}"
      -X POST "https://auth.${WIZ_ENV_VAL}.wiz.io/oauth/token"
      -H "Content-Type: application/x-www-form-urlencoded"
      -H "Accept: application/json, text/plain, */*"
      --data-urlencode "grant_type=client_credentials"
      --data-urlencode "audience=wiz-api"
      --data-urlencode "client_id=${WIZ_CLIENT_ID}"
      --data-urlencode "client_secret=${WIZ_CLIENT_SECRET}"
    )
    VFILE="${WIZ_MCP_TMP}/oauth-VERBOSE-${PID}.log"
    if [[ "${WIZ_OAUTH_VERBOSE:-0}" == "1" ]]; then
      code="$(curl -v "${CURL[@]}" -w '%{http_code}' 2>"${VFILE}")" || code="fail"
      echo "  verbose: ${VFILE}"
    else
      code="$(curl "${CURL[@]}" -w '%{http_code}')" || code="fail"
    fi
    echo "  HTTP ${code}"
    if [[ -f "${BODY}" ]]; then
      echo "  body (${WIZ_MCP_TMP}/oauth-${PID}.body):"
      head -c 800 "${BODY}" | cat -v; echo
    fi
    if [[ "${code}" == "200" ]]; then
      rm -f "${HDR}" "${BODY}"
    else
      echo "  headers: ${HDR}"
    fi
  fi
fi

echo
echo "=== MCP smoke (first log lines, auto-stop ~8s) ==="
[[ -f "${DOTENV}" && -x "${UV_BIN}" && -f "${WIZ_MCP_SERVER_DIR}/server.py" ]] || { echo "  skip"; exit 0; }
set +e
set +o pipefail
SMOKE_LOG="${WIZ_MCP_TMP}/smoke-${PID}.log"
rm -f "${SMOKE_LOG}"
( unset WIZ_CLIENT_ID WIZ_CLIENT_SECRET WIZ_ENV WIZ_DOTENV_PATH 2>/dev/null
  export WIZ_DOTENV_PATH="${DOTENV}"
  "${UV_BIN}" --directory "${WIZ_MCP_SERVER_DIR}" run --with "mcp[cli]" mcp run server.py
) >>"${SMOKE_LOG}" 2>&1 &
smoke_pid=$!
sleep 8
kill "${smoke_pid}" 2>/dev/null || true
wait "${smoke_pid}" 2>/dev/null || true
head -25 "${SMOKE_LOG}" 2>/dev/null | cat -v
