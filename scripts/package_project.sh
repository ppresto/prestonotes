#!/bin/bash
set -euo pipefail

# Build a focused, shareable archive while honoring .gitignore patterns.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME="$(basename "${ROOT_DIR}")"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${ROOT_DIR}/dist"
ARCHIVE_PATH="${OUT_DIR}/${PROJECT_NAME}-share-${STAMP}.tar.gz"

mkdir -p "${OUT_DIR}"

# Core paths to include for sharing.
INCLUDE_PATHS=(
  ".cursor"
  "docs"
  "README.md"
  "scripts"
)

# Optional paths: include automatically when present.
OPTIONAL_PATHS=(
  "mcpservers"
  "prestonotes_mcp"
)

for p in "${OPTIONAL_PATHS[@]}"; do
  if [ -e "${ROOT_DIR}/${p}" ]; then
    INCLUDE_PATHS+=("${p}")
  fi
done

echo "Creating archive:"
echo "  ${ARCHIVE_PATH}"
echo "Including paths:"
printf "  - %s\n" "${INCLUDE_PATHS[@]}"

# tar is executed from project root so include paths remain relative.
(
  cd "${ROOT_DIR}"
  tar -czf "${ARCHIVE_PATH}" \
    --exclude-vcs \
    --exclude-from=".gitignore" \
    --exclude="dist" \
    "${INCLUDE_PATHS[@]}"
)

echo "Archive created successfully."
echo "Output: ${ARCHIVE_PATH}"
