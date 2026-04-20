#!/usr/bin/env bash
# Validate that required repo paths from required-paths.manifest exist.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="${ROOT}/scripts/ci/required-paths.manifest"
missing=0
while IFS= read -r line || [[ -n "${line:-}" ]]; do
  [[ -z "${line// }" || "${line}" =~ ^[[:space:]]*# ]] && continue
  rel="${line//$'\r'/}"
  path="${ROOT}/${rel}"
  if [[ ! -e "${path}" ]]; then
    echo "Missing required path: ${rel}" >&2
    missing=1
  fi
done < "${MANIFEST}"
if [[ "${missing}" -ne 0 ]]; then
  exit 1
fi
echo "Repo integrity OK."
