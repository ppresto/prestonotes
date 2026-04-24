#!/usr/bin/env bash
# e2e-test-customer.sh — single shell entry for the _TEST_CUSTOMER E2E flow (TASK-044).
#
# Subcommands (idempotent; safe to re-run):
#   reset   Trash the Drive _TEST_CUSTOMER folder via API, wipe the local mirror,
#           restart Google Drive for Desktop, and wait for the mount to clear.
#   v1      Materialize tests/fixtures/e2e/_TEST_CUSTOMER/v1/ (transcripts +
#           starter call-records + index) into MyNotes/Customers/_TEST_CUSTOMER/,
#           roll dates forward into the rolling 30-day lookback, rebuild the index,
#           then push the mirror to Drive.
#   v2      Merge tests/fixtures/e2e/_TEST_CUSTOMER/v2/ (commercial-expansion
#           transcripts only; call-records come from the round-2 Extract playbook)
#           on top of v1, re-roll dates, rebuild the index, push to Drive.
#
# The three chat-playbook steps (Bootstrap Customer, Load Customer Context,
# Extract Call Records, Update Customer Notes, Run Account Summary) are NOT
# run from this script. The canonical 10-step sequence lives in
# docs/ai/playbooks/e2e-test-customer.md. The agent executes it end-to-end
# under the trigger rule .cursor/rules/11-e2e-test-customer-trigger.mdc.
#
# Usage:
#   ./scripts/e2e-test-customer.sh reset
#   ./scripts/e2e-test-customer.sh v1
#   ./scripts/e2e-test-customer.sh v2

set -euo pipefail

CUSTOMER="_TEST_CUSTOMER"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load GDRIVE_BASE_PATH, PRESTONOTES_REPO_ROOT, .venv, etc. from .cursor/mcp.env
# via setEnv.sh. setEnv.sh inspects $1 (--help / --bootstrap / --inject-mcp-env),
# and sourcing propagates our caller args into it. Save our args, clear them for
# the duration of the source, then restore them.
__orig_args=("$@")
set --
# shellcheck disable=SC1091
source "${REPO_ROOT}/setEnv.sh"
if (( ${#__orig_args[@]} > 0 )); then
  set -- "${__orig_args[@]}"
fi
unset __orig_args

export PRESTONOTES_REPO_ROOT="${PRESTONOTES_REPO_ROOT:-$REPO_ROOT}"

LOCAL_CUSTOMER_DIR="${PRESTONOTES_REPO_ROOT}/MyNotes/Customers/${CUSTOMER}"
GDRIVE_BASE_PATH="${GDRIVE_BASE_PATH:-$HOME/Google Drive/My Drive/MyNotes}"
MOUNT_CUSTOMER_DIR="${GDRIVE_BASE_PATH}/Customers/${CUSTOMER}"
RESTART_WAIT_SEC="${E2E_RESTART_WAIT_SEC:-5}"
MOUNT_DISAPPEAR_TIMEOUT_SEC="${E2E_MOUNT_DISAPPEAR_TIMEOUT_SEC:-180}"
MOUNT_APPEAR_TIMEOUT_SEC="${E2E_MOUNT_APPEAR_TIMEOUT_SEC:-180}"

usage() {
  cat <<USAGE >&2
Usage: $(basename "$0") <reset|v1|v2>

  reset   Trash Drive folder + wipe local mirror + restart Drive mount.
          After reset, issue the chat trigger: Bootstrap Customer for _TEST_CUSTOMER.
  v1      Apply tests/fixtures/e2e/_TEST_CUSTOMER/v1/ + bump dates + push to Drive.
  v2      Merge tests/fixtures/e2e/_TEST_CUSTOMER/v2/ (transcripts only) + re-bump + push.

Canonical 10-step flow: docs/ai/playbooks/e2e-test-customer.md
USAGE
  exit 2
}

check_gcloud_auth() {
  if ! command -v gcloud >/dev/null 2>&1; then
    echo "ERROR: gcloud CLI not found on PATH. Install Google Cloud SDK and sign in." >&2
    exit 1
  fi
  if ! gcloud auth print-access-token >/dev/null 2>&1; then
    echo "ERROR: gcloud is not authenticated for Drive access." >&2
    echo "Fix: gcloud auth login --account=patrick.presto@wiz.io --enable-gdrive-access --force" >&2
    exit 1
  fi
}

poll_until() {
  # poll_until <timeout_sec> <interval_sec> <predicate_cmd...>
  local timeout="$1"
  local interval="$2"
  shift 2
  local deadline=$(( $(date +%s) + timeout ))
  while (( $(date +%s) < deadline )); do
    if "$@"; then
      return 0
    fi
    sleep "$interval"
  done
  return 1
}

mount_is_absent() { [[ ! -d "$MOUNT_CUSTOMER_DIR" ]]; }
mount_is_present() { [[ -d "$MOUNT_CUSTOMER_DIR" ]]; }

cmd_reset() {
  check_gcloud_auth

  echo "==> [reset] Trashing Drive folder Customers/${CUSTOMER} via API ..."
  uv run python "${REPO_ROOT}/prestonotes_gdoc/drive-trash-customer.py" "${CUSTOMER}"

  echo "==> [reset] Removing local mirror: ${LOCAL_CUSTOMER_DIR}"
  if [[ -d "${LOCAL_CUSTOMER_DIR}" ]]; then
    rm -rf "${LOCAL_CUSTOMER_DIR}"
  else
    echo "    (already absent)"
  fi

  echo "==> [reset] Restarting Google Drive for Desktop (wait ${RESTART_WAIT_SEC}s) ..."
  "${REPO_ROOT}/scripts/restart-google-drive.sh" "${RESTART_WAIT_SEC}"

  echo "==> [reset] Waiting up to ${MOUNT_DISAPPEAR_TIMEOUT_SEC}s for mount path to show Customers/${CUSTOMER} absent ..."
  if ! poll_until "${MOUNT_DISAPPEAR_TIMEOUT_SEC}" 3 mount_is_absent; then
    echo "ERROR: mount path still shows ${CUSTOMER} after ${MOUNT_DISAPPEAR_TIMEOUT_SEC}s: ${MOUNT_CUSTOMER_DIR}" >&2
    echo "       The Drive API trash call succeeded but the local mount has not caught up." >&2
    echo "       Wait for Drive to finish syncing and re-run 'e2e-test-customer.sh reset', or inspect Drive trash." >&2
    exit 1
  fi

  cat <<'NEXT'

[reset] COMPLETE. Next step (chat trigger):

    Bootstrap Customer for _TEST_CUSTOMER

After bootstrap reports success, run:

    ./scripts/e2e-test-customer.sh v1

NEXT
}

ensure_bootstrapped() {
  # v1 / v2 require that Bootstrap Customer has produced the folder skeleton
  # on Drive and that Drive has synced it back down to the mount. We rely on
  # the mount (not the repo mirror) because that is what bootstrap actually
  # produced. A pull from Drive populates the repo mirror on demand.
  #
  # After API-only bootstrap, Google Drive for Desktop often needs a restart
  # before the new folder appears locally (same class of issue `reset` already
  # mitigates with `restart-google-drive.sh`).
  if [[ ! -d "${MOUNT_CUSTOMER_DIR}" ]]; then
    echo "WARN: ${MOUNT_CUSTOMER_DIR} not visible yet (typical right after API bootstrap)." >&2
    echo "==> [ensure_bootstrapped] Restarting Google Drive for Desktop (wait ${RESTART_WAIT_SEC}s) ..."
    "${REPO_ROOT}/scripts/restart-google-drive.sh" "${RESTART_WAIT_SEC}"
  fi
  if ! poll_until "${MOUNT_APPEAR_TIMEOUT_SEC}" 3 mount_is_present; then
    echo "ERROR: ${MOUNT_CUSTOMER_DIR} still not found on the Drive mount after restart + wait." >&2
    echo "       Confirm bootstrap succeeded, Drive is running, then retry v1/v2." >&2
    echo "       If bootstrap was skipped, run the chat trigger: Bootstrap Customer for _TEST_CUSTOMER" >&2
    exit 1
  fi
  # Pull the bootstrap skeleton (AI_Insights/, Transcripts/, <Customer> Notes.gdoc
  # stub, pnotes_agent_log.md, etc.) from Drive into the repo mirror so the
  # materialize + bump-dates helpers operate on local files.
  echo "==> Syncing Drive → repo mirror: Customers/${CUSTOMER}/"
  "${REPO_ROOT}/scripts/rsync-gdrive-notes.sh" "${CUSTOMER}"
  if [[ ! -d "${LOCAL_CUSTOMER_DIR}" ]]; then
    echo "ERROR: local mirror missing after rsync: ${LOCAL_CUSTOMER_DIR}" >&2
    exit 1
  fi
}

materialize_and_push() {
  local variant="$1"   # v1 or v2
  local apply_flag=""
  if [[ "${variant}" == "v2" ]]; then
    apply_flag="--v2"
  fi

  echo "==> [${variant}] Materializing fixtures into ${LOCAL_CUSTOMER_DIR}/ ..."
  # shellcheck disable=SC2086
  uv run python "${REPO_ROOT}/scripts/e2e-test-customer-materialize.py" apply ${apply_flag}

  echo "==> [${variant}] Rolling fixture dates forward into rolling 30-day window ..."
  uv run python "${REPO_ROOT}/scripts/e2e-test-customer-bump-dates.py" --customer "${CUSTOMER}"

  echo "==> [${variant}] Pushing repo mirror → Drive: Customers/${CUSTOMER}/"
  "${REPO_ROOT}/scripts/e2e-test-push-gdrive-notes.sh" "${CUSTOMER}"

  cat <<NEXT

[${variant}] COMPLETE.

Next chat triggers (run in order, without stopping):

$( if [[ "${variant}" == "v1" ]]; then
cat <<V1_NEXT
    Load Customer Context for _TEST_CUSTOMER
    Extract Call Records for _TEST_CUSTOMER
    Update Customer Notes for _TEST_CUSTOMER

Then: ./scripts/e2e-test-customer.sh v2
V1_NEXT
else
cat <<V2_NEXT
    Extract Call Records for _TEST_CUSTOMER
    Update Customer Notes for _TEST_CUSTOMER
    Run Account Summary for _TEST_CUSTOMER
V2_NEXT
fi )
NEXT
}

cmd_v1() {
  ensure_bootstrapped
  materialize_and_push v1
}

cmd_v2() {
  ensure_bootstrapped
  if [[ ! -d "${LOCAL_CUSTOMER_DIR}/call-records" ]] \
     || ! find "${LOCAL_CUSTOMER_DIR}/call-records" -maxdepth 1 -name '*.json' -print -quit | grep -q .; then
    echo "ERROR: ${LOCAL_CUSTOMER_DIR}/call-records/ has no JSON records." >&2
    echo "       v2 requires v1 to have been applied first (so round-1 Extract Call Records produced records)." >&2
    echo "       Run: ./scripts/e2e-test-customer.sh v1  and complete round-1 playbooks before v2." >&2
    exit 1
  fi
  materialize_and_push v2
}

case "${1:-}" in
  reset) shift; cmd_reset "$@" ;;
  v1)    shift; cmd_v1 "$@" ;;
  v2)    shift; cmd_v2 "$@" ;;
  -h|--help|help|"") usage ;;
  *) echo "Unknown subcommand: $1" >&2; usage ;;
esac
