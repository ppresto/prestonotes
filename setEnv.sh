#!/usr/bin/env bash
# PrestoNotes — export repo root for local shells; optional dev bootstrap.
#
# MCP + Google env vars live in .cursor/mcp.json (Cursor injects them when it starts the server).
# For terminal-only commands (e.g. uv run scripts/granola-sync.py), export the same names yourself
# or paste values once into your shell profile.
#
# Typical use:
#   source ./setEnv.sh     # exports PRESTONOTES_REPO_ROOT only
#
# First-time / refresh dev dependencies:
#   ./setEnv.sh --bootstrap

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
export PRESTONOTES_REPO_ROOT="$REPO_ROOT"

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
  if [[ -f package.json ]]; then
    echo "setEnv: bootstrapping JS (npm)…"
    npm install
  fi
  echo "setEnv: --bootstrap complete."
  exit 0
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage:"
  echo "  source ./setEnv.sh       Export PRESTONOTES_REPO_ROOT (matches .cursor/mcp.json pattern)"
  echo "  ./setEnv.sh --bootstrap  Create/use .venv, uv sync, npm install"
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
