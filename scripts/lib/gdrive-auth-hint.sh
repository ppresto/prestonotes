#!/usr/bin/env bash
# Shared stderr messages for Google Drive / gcloud recovery (TASK-066).
# shellcheck shell=bash
#
# Env (from .cursor/mcp.env via setEnv or prestonotes_source_mcp_env):
#   GCLOUD_AUTH_LOGIN_COMMAND — copy/paste gcloud login one-liner (see .cursor/mcp.env.example)

prestonotes_source_mcp_env() {
  local root="${1:-}"
  if [[ -z "$root" ]]; then
    return 1
  fi
  local mcp="${root}/.cursor/mcp.env"
  if [[ -r "$mcp" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$mcp"
    set +a
  fi
}

# Print the same recovery line(s) shell scripts and the /tester subagent use on GDrive/gcloud failure.
prestonotes_gdrive_auth_hint() {
  if [[ -n "${GCLOUD_AUTH_LOGIN_COMMAND:-}" ]]; then
    echo "GDrive / gcloud re-auth (copy/paste):" >&2
    echo "  ${GCLOUD_AUTH_LOGIN_COMMAND}" >&2
  else
    echo "GDrive / gcloud: set GCLOUD_AUTH_LOGIN_COMMAND in .cursor/mcp.env (see .cursor/mcp.env.example), then: source ./setEnv.sh" >&2
    echo "Or after mcp.env is configured: ./setEnv.sh --print-gdrive-auth" >&2
  fi
}
