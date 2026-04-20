#!/usr/bin/env bash
# Back-compat entry: full dev bootstrap now lives in repo-root ./setEnv.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT}/setEnv.sh" --bootstrap
