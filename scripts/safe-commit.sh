#!/bin/bash
# scripts/safe-commit.sh
# Usage: ./safe-commit.sh "Your commit message here"

COMMIT_MSG=$1

if [ -z "$COMMIT_MSG" ]; then
  echo "Error: Please provide a commit message."
  exit 1
fi

echo "Running Pre-commit mechanical checks..."

# 1. Run your fast linters/formatters via pre-commit
if ! uv run pre-commit run --all-files; then
  echo "Linting failed! Aborting commit to save you from yourself."
  exit 1
fi

# 2. If everything passes, stage and commit
git add .
git commit -m "$COMMIT_MSG"
echo "Commit successful! You are safe to push."