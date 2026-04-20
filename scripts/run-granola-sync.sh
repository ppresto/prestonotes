#!/usr/bin/env bash
# Run Granola → MyNotes per-call transcript export from the repo root (same as MCP sync_transcripts).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec uv run scripts/granola-sync.py "$@"
