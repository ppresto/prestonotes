#!/bin/bash
set -euo pipefail

echo "Starting local development environment setup..."

# 1) Initialize Python project if needed
if [ ! -f "pyproject.toml" ]; then
  echo "No pyproject.toml found. Initializing Python project with uv..."
  uv init
  INITIALIZED_PYTHON=true
else
  echo "pyproject.toml already exists. Skipping uv init."
  INITIALIZED_PYTHON=false
fi

# 2) Ensure a virtual environment exists and activate it
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment with uv..."
  uv venv
else
  echo ".venv already exists. Reusing existing environment."
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"
echo "Virtual environment activated: ${VIRTUAL_ENV}"

# 3) Install/Sync Python dev tooling
if [ "$INITIALIZED_PYTHON" = true ]; then
  echo "Installing initial Python dev tools with uv..."
  uv add --dev pytest ruff pre-commit yamllint
else
  echo "Syncing existing Python environment from lockfile..."
  uv sync
fi

# 4) Initialize package.json if needed
if [ ! -f "package.json" ]; then
  echo "No package.json found. Initializing npm project..."
  npm init -y
  INITIALIZED_JS=true
else
  echo "package.json already exists. Skipping npm init -y."
  INITIALIZED_JS=false
fi

# 5) Install/Sync JavaScript/Markdown tooling
if [ "$INITIALIZED_JS" = true ]; then
  echo "Installing initial JS/Markdown dev tools with npm..."
  npm install -D @biomejs/biome vitest markdownlint-cli
else
  echo "Syncing existing JS environment from lockfile..."
  npm install
fi

# 6) Helpful message for OS-level tools
echo ""
echo "Setup complete."
echo "Install OS-level tools (if missing) using your package manager."
echo "For macOS (Homebrew), run:"
echo "  brew install shellcheck terraform tflint"