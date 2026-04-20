#!/bin/bash
set -euo pipefail
echo "Running tests..."
run_py() {
  if [[ -f pyproject.toml ]] && command -v uv >/dev/null 2>&1; then
    uv run "$@"
  else
    "$@"
  fi
}
if [[ -d "tests" ]] || ls test_*.py 1> /dev/null 2>&1; then
  run_py pytest
fi
if [[ -f "vitest.config.ts" ]] || [[ -f "vitest.config.js" ]]; then vitest run; fi
echo "Tests complete."
