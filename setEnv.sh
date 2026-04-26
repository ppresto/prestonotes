#!/usr/bin/env bash
# PrestoNotes — export repo root + same Google/Drive vars as MCP; optional dev bootstrap.
#
# Works when **sourced** from **zsh** or **bash** (or run as `bash setEnv.sh` for flags).
# When `source ./setEnv.sh` from zsh, bash's BASH_SOURCE is unset — we find the repo by
# walking up from $PWD until we see `pyproject.toml` + `prestonotes_mcp/`.
#
# Typical use (from any directory *inside* the prestonotes repo, or the repo root):
#   source ./setEnv.sh
#
# zsh: no need to `exec bash` — this file is read by your current zsh. Use `emulate -R` only if
# you hit option conflicts (rare).
#
# If the shell still exits, check `.cursor/mcp.env` for a stray `exit` or `exec`.
#
# What depends on this (repo):
#   - `scripts/e2e-test-customer.sh` — sources this before Drive/repo E2E steps
#   - `scripts/setup_env.sh` — re-execs `./setEnv.sh --bootstrap`
#   - `README.md` / playbooks — bootstrap: `./setEnv.sh --bootstrap`, then `source ./setEnv.sh`
#   - `scripts/rsync-gdrive-notes.sh`, `e2e-test-push-gdrive-notes.sh`, `run-granola-sync.zsh` — read
#     `PRESTONOTES_REPO_ROOT` + `GDRIVE_BASE_PATH` from the environment (not setEnv-intrinsic, but
#     sourcing setEnv is how you align the shell with `.cursor/mcp.env`)
#   - **Cursor MCP** — `.cursor/mcp.json` sets `PRESTONOTES_REPO_ROOT` and loads `.cursor/mcp.env`
#     for the server process; **terminal** workflows use this script for the same vars
#
#   ./setEnv.sh --bootstrap       (run as command, not: source --bootstrap)
#   ./setEnv.sh --inject-mcp-env
#   ./setEnv.sh --print-gdrive-auth  (loads mcp.env, prints GCLOUD_AUTH_LOGIN_COMMAND; run as bash, not source)

# Sourcing runs in the *current* shell: use return, not exit, when appropriate.
SETENV_SOURCED=0
if [[ -n "${ZSH_VERSION:-}" ]]; then
  SETENV_SOURCED=1
elif [[ -n "${BASH_VERSION:-}" && -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "$0" ]]; then
  SETENV_SOURCED=1
fi

# Resolve real repo: bash can use BASH_SOURCE; zsh and others walk up from $PWD.
setenv_find_repo() {
  if [[ -n "${BASH_VERSION:-}" && -n "${BASH_SOURCE[0]:-}" ]]; then
    REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  else
    local _d
    _d=$(pwd 2>/dev/null) || _d=/
    REPO_ROOT=""
    while [[ -n "$_d" && "$_d" != / ]]; do
      if [[ -f "$_d/pyproject.toml" && -d "$_d/prestonotes_mcp" ]]; then
        REPO_ROOT="$_d"
        break
      fi
      _d=$(dirname "$_d")
    done
  fi
}

REPO_ROOT=""
setenv_find_repo
unset -f setenv_find_repo 2>/dev/null || true

if [[ -z "$REPO_ROOT" ]]; then
  echo "setEnv: could not find repo (need pyproject.toml and prestonotes_mcp/ up from \$PWD), or re-run from inside the prestonotes tree." >&2
  if [[ -n "${ZSH_VERSION:-}" && ${ZSH_EVAL_CONTEXT:-} == *:file* ]] || { [[ -n "${BASH_VERSION:-}" && -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "$0" ]]; }; then
    return 1
  fi
  exit 1
fi
export PRESTONOTES_REPO_ROOT="$REPO_ROOT"

if [[ "${1:-}" == "--print-gdrive-auth" ]]; then
  cd "${REPO_ROOT}" || exit 1
  MCP_ENV="${REPO_ROOT}/.cursor/mcp.env"
  if [[ -r "${MCP_ENV}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${MCP_ENV}"
    set +a
  fi
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/scripts/lib/gdrive-auth-hint.sh"
  prestonotes_gdrive_auth_hint
  exit 0
fi

_setenv_done() {
  local c="${1:-0}"
  if [[ "$SETENV_SOURCED" -eq 1 ]]; then
    return "$c"
  fi
  exit "$c"
}
export PRESTONOTES_OP_ACCOUNT="wizio.1password.com"

if [[ "${1:-}" == "--inject-mcp-env" ]]; then
  cd "${REPO_ROOT}" || { echo "setEnv: could not cd to ${REPO_ROOT}" >&2; _setenv_done 1; }
  MCP_TPL="${REPO_ROOT}/.cursor/mcp.env.tpl"
  MCP_OUT="${REPO_ROOT}/.cursor/mcp.env"
  if [[ ! -f "${MCP_TPL}" ]]; then
    echo "setEnv: missing ${MCP_TPL} (use op:// references; see .cursor/mcp.env.example)." >&2
    _setenv_done 1
  fi
  if ! command -v op >/dev/null 2>&1; then
    echo "setEnv: 1Password CLI (op) not found. https://developer.1password.com/docs/cli" >&2
    _setenv_done 1
  fi
  echo "setEnv: writing ${MCP_OUT} via op inject…"
  if ! op inject -i "${MCP_TPL}" -o "${MCP_OUT}" --account "${PRESTONOTES_OP_ACCOUNT}"; then
    _setenv_done 1
  fi
  echo "setEnv: --inject-mcp-env complete. Restart the prestonotes MCP server in Cursor if it is running."
  _setenv_done 0
fi

# Load the same .cursor/mcp.env Cursor uses when *sourced* in zsh, or in bash (not a bare `bash setEnv.sh` with no source).
_load_repo_env=false
if [[ -n "${ZSH_VERSION:-}" ]]; then
  _load_repo_env=true
elif [[ -n "${BASH_VERSION:-}" && -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "$0" ]]; then
  _load_repo_env=true
fi
if [[ "${_load_repo_env}" == true ]]; then
  MCP_ENV="${REPO_ROOT}/.cursor/mcp.env"
  if [[ -r "${MCP_ENV}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${MCP_ENV}"
    set +a
  fi
  if [[ -z "${VIRTUAL_ENV:-}" && -f "${REPO_ROOT}/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "${REPO_ROOT}/.venv/bin/activate"
  fi
fi
unset _load_repo_env

# E2E / local testing convenience (same paths as `scripts/e2e-test-customer.sh`):
#   R = repo MyNotes customer folder, M = Drive-mounted customer folder.
#   `GDRIVE_BASE_PATH` / `MYNOTES_ROOT_FOLDER_ID` usually come from `.cursor/mcp.env` (loaded above);
#   if mcp.env is missing, the Drive path defaults below; set MYNOTES yourself for
#   `gcloud`/`discover` flows — do not commit real folder IDs in-repo.
#   Example one-liner: export MYNOTES_ROOT_FOLDER_ID="YOUR_MYNOTES_ROOT_FOLDER_ID"
export GDRIVE_BASE_PATH="${GDRIVE_BASE_PATH:-$HOME/Google Drive/My Drive/MyNotes}"
export CUST="${CUST:-_TEST_CUSTOMER}"
export CUSTOMER="${CUSTOMER:-$CUST}"
export R="${PRESTONOTES_REPO_ROOT}/MyNotes/Customers/${CUST}"
export M="${GDRIVE_BASE_PATH}/Customers/${CUST}"
export MYNOTES_ROOT_FOLDER_ID="${MYNOTES_ROOT_FOLDER_ID:-}"
export GCLOUD_ACCOUNT="${GCLOUD_ACCOUNT:-}"
export GCLOUD_AUTH_LOGIN_COMMAND="${GCLOUD_AUTH_LOGIN_COMMAND:-}"

if [[ "${1:-}" == "--bootstrap" ]]; then
  cd "${REPO_ROOT}" || { echo "setEnv: could not cd to ${REPO_ROOT}" >&2; _setenv_done 1; }
  if [[ ! -f pyproject.toml ]]; then
    echo "setEnv: no pyproject.toml; run from repo root." >&2
    _setenv_done 1
  fi
  echo "setEnv: bootstrapping Python (uv)…"
  if [[ ! -d .venv ]]; then
    uv venv
  fi
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  uv sync
  echo "setEnv: --bootstrap complete. Then: source ./setEnv.sh"
  _setenv_done 0
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage:"
  echo "  source ./setEnv.sh     PRESTONOTES_REPO_ROOT + .cursor/mcp.env (if present) + .venv"
  echo "                         + GDRIVE_BASE_PATH, CUST/CUSTOMER, R, M, MYNOTES (see script header)"
  echo "  Source from repo root (or any subdir) in bash or zsh; repo is found via BASH_SOURCE or cwd walk."
  echo "  ./setEnv.sh --bootstrap"
  echo "  ./setEnv.sh --inject-mcp-env"
  echo "  ./setEnv.sh --print-gdrive-auth   # print GCLOUD_AUTH_LOGIN_COMMAND from .cursor/mcp.env (run with bash)"
  _setenv_done 0
fi

# Only when *executed* by bash (not `source`): BASH_SOURCE[0] and $0 are the script path.
# In zsh, $0 is often the sourced file name — do not use $0=setEnv.sh for this check or zsh
# `source` wrongly hits exit and drops your session.
if [[ -n "${BASH_VERSION:-}" && -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" == "$0" && "${0##*/}" == "setEnv.sh" && -z "${1:-}" ]]; then
  echo "setEnv: ran as a subprocess — exports do not persist. Use:" >&2
  echo "  source ./setEnv.sh" >&2
  exit 0
fi
