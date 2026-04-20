#!/bin/bash
set -euo pipefail
echo "Running linters..."
run_py() {
  if [[ -f pyproject.toml ]] && command -v uv >/dev/null 2>&1; then
    uv run "$@"
  else
    "$@"
  fi
}
if [[ -f pyproject.toml ]]; then
  run_py ruff check .
  run_py ruff format .
fi
if find . \( -path ./node_modules -o -path ./.venv \) -prune -o -name "*.js" -print -quit 2>/dev/null | grep -q .; then
  if command -v biome >/dev/null 2>&1; then
    biome check --write .
  elif [[ -x node_modules/.bin/biome ]]; then
    node_modules/.bin/biome check --write .
  elif command -v npx >/dev/null 2>&1; then
    npx biome check --write .
  fi
fi
if command -v shellcheck >/dev/null 2>&1; then
  while IFS= read -r -d "" f; do
    shellcheck "$f"
  done < <(find scripts .cursor/skills -name "*.sh" -type f -print0 2>/dev/null)
fi
if find . \( -path ./node_modules -o -path ./.venv \) -prune -o \( -name "*.yaml" -o -name "*.yml" \) -print -quit 2>/dev/null | grep -q .; then
  run_py yamllint .
fi
if find . -name "*.tf" -print -quit 2>/dev/null | grep -q .; then tflint; terraform validate; fi
echo "Linting complete."
