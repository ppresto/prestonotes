#!/usr/bin/env bash
# PrestoNotes — export repo root + same Google/Drive vars as MCP; optional dev bootstrap.
#
# Canonical secrets/paths: **`.cursor/mcp.env`** (gitignored; copy from `.cursor/mcp.env.example`
# or generate from **`.cursor/mcp.env.tpl`** with 1Password CLI).
# Cursor still loads that file for the MCP server via `.cursor/mcp.json` → `envFile`.
# When you **source** this script, the same file is applied to **your shell** so
# `uv run …`, rsync scripts, and agent terminal commands see `GDRIVE_BASE_PATH`, etc.
#
# Typical use:
#   source ./setEnv.sh     # PRESTONOTES_REPO_ROOT + .cursor/mcp.env (if present) + .venv activate
#
# Regenerate MCP env from 1Password (writes gitignored `.cursor/mcp.env` for Cursor + shell):
#   ./setEnv.sh --inject-mcp-env
#
# First-time / refresh dev dependencies:
#   ./setEnv.sh --bootstrap

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
export PRESTONOTES_REPO_ROOT="$REPO_ROOT"
# 1Password CLI `op inject --account` (edit here if you use a different sign-in domain).
export PRESTONOTES_OP_ACCOUNT="wizio.1password.com"

if [[ "${1:-}" == "--inject-mcp-env" ]]; then
  cd "${REPO_ROOT}" || exit 1
  MCP_TPL="${REPO_ROOT}/.cursor/mcp.env.tpl"
  MCP_OUT="${REPO_ROOT}/.cursor/mcp.env"
  if [[ ! -f "${MCP_TPL}" ]]; then
    echo "setEnv: missing ${MCP_TPL} (use op:// references; see .cursor/mcp.env.example)." >&2
    exit 1
  fi
  if ! command -v op >/dev/null 2>&1; then
    echo "setEnv: 1Password CLI (op) not found. https://developer.1password.com/docs/cli" >&2
    exit 1
  fi
  echo "setEnv: writing ${MCP_OUT} via op inject…"
  op inject -i "${MCP_TPL}" -o "${MCP_OUT}" --account "${PRESTONOTES_OP_ACCOUNT}" || exit 1
  echo "setEnv: --inject-mcp-env complete. Restart the prestonotes MCP server in Cursor if it is running."
  exit 0
fi

# Only when sourced (zsh or bash): subprocesses like `./setEnv.sh --bootstrap` must not
# mutate a disposable shell; Cursor/agents should use `source ./setEnv.sh` before Drive/GDoc commands.
_load_repo_env=false
if [[ -n "${ZSH_VERSION:-}" ]]; then
  case ${ZSH_EVAL_CONTEXT:-} in *:file*) _load_repo_env=true ;; esac
elif [[ -n "${BASH_VERSION:-}" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
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

if [[ "${1:-}" == "--bootstrap" ]]; then
  cd "${REPO_ROOT}" || exit 1
  if [[ ! -f pyproject.toml ]]; then
    echo "setEnv: no pyproject.toml; run from repo root." >&2
    exit 1
  fi
  echo "setEnv: bootstrapping Python (uv)…"
  if [[ ! -d .venv ]]; then
    uv venv
  fi
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  uv sync
  echo "setEnv: --bootstrap complete."
  exit 0
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage:"
  echo "  source ./setEnv.sh            PRESTONOTES_REPO_ROOT + source .cursor/mcp.env if present + activate .venv"
  echo "  ./setEnv.sh --bootstrap       Create/use .venv, uv sync"
  echo "  ./setEnv.sh --inject-mcp-env  op inject .cursor/mcp.env.tpl → .cursor/mcp.env (for Cursor MCP envFile)"
  exit 0
fi

# Basename only: when sourced, $0 is the shell (e.g. bash), not this file.
case "${0##*/}" in
  setEnv.sh)
    if [[ -z "${1:-}" ]]; then
      echo "setEnv: ran as a subprocess — exports do not persist. Use:" >&2
      echo "  source ./setEnv.sh" >&2
      exit 0
    fi
    ;;
esac
