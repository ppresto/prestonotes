#!/usr/bin/env bash
# TASK-052 §0.6: do not commit literal Google Doc / Drive file ids in user-facing
# documentation — resolve ids at runtime via discover_doc / gcloud.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

paths=(docs README.md)
# Exclude archived task text (historical session dumps may still contain examples).
tmpf="$(mktemp)"
trap 'rm -f "${tmpf}"' EXIT

rg -n -S --glob '!**/docs/tasks/archive/**' \
  -e '/document/d/[0-9A-Za-z_-]{20,}' \
  -e 'docs\.google\.com/spreadsheets/d/[0-9A-Za-z_-]{20,}' \
  "${paths[@]}" 2>/dev/null >>"${tmpf}" || true

# Unquoted or quoted 32+ char id after --doc-id (CLI examples)
rg -n -S --glob '!**/docs/tasks/archive/**' \
  -e '--doc-id[[:space:]]+[0-9A-Za-z_-]{32,}' \
  -e '--doc-id[[:space:]]+["'"'"'`][0-9A-Za-z_-]{32,}' \
  "${paths[@]}" 2>/dev/null >>"${tmpf}" || true

if [[ -s "${tmpf}" ]]; then
  echo "check-docs-no-embedded-gdoc-file-ids: FAIL — possible Google file id in docs or README." >&2
  echo "Use discover at run time; do not commit literal ids (TASK-052 §0.6)." >&2
  echo "" >&2
  cat "${tmpf}" >&2
  exit 1
fi

echo "check-docs-no-embedded-gdoc-file-ids: OK (no disallowed id patterns in docs/ + README)."
