#!/usr/bin/env bash
# e2e-test-customer.sh — single shell entry for the _TEST_CUSTOMER E2E flow (TASK-044, TASK-052).
#
# Subcommands:
#   prep-v1   E2E full reset of GDoc (template copy) + pull + clean local AI_Insights/log +
#             materialize v1 + bump + push. Default for a clean E2E iteration (TASK-052).
#   prep-v2   Push local to Drive first, then pull, materialize v2 + bump + push
#             (round-1 UCN artifacts must hit Drive before pull; TASK-052 Section B).
#   v1        Legacy: no GDoc rebaseline, no local clean — ensure mount + materialize v1 + bump + push.
#   v2        Same as prep-v2 (kept for older docs).
#   reset     Nuclear: trash Drive folder, wipe local mirror, restart Google Drive, poll.
#   list-steps   Eight harness steps (see scripts/lib/e2e-catalog.txt).
#   list-catalog, list-all  Triggers, eight steps, and e2e_workflow modes (v1_full, full, ...).
#   run-step <n> Run only shell step n (1 or 5) or print chat trigger for other n (debugger).
#
# Options (prep-v1 only):
#   --skip-rebaseline   Do not run e2e_rebaseline_customer_gdoc.py (faster re-seed of files only).
#   --skip-clean        Do not remove pnotes_agent_log or AI_Insights (debug).
#
# Usage:
#   ./scripts/e2e-test-customer.sh prep-v1
#   ./scripts/e2e-test-customer.sh prep-v1 --skip-rebaseline
#   ./scripts/e2e-test-customer.sh prep-v2
#   ./scripts/e2e-test-customer.sh run-step 1
#   ./scripts/e2e-test-customer.sh list-steps
#   ./scripts/e2e-test-customer.sh list-catalog
#
# Canonical playbooks: docs/ai/playbooks/tester-e2e-ucn.md
# Harness + triggers + workflow modes: scripts/lib/e2e-catalog.txt
# Trigger rule: .cursor/rules/11-e2e-test-customer-trigger.mdc

set -euo pipefail

CUSTOMER="_TEST_CUSTOMER"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

__orig_args=("$@")
set --
# shellcheck disable=SC1091
source "${REPO_ROOT}/setEnv.sh"
if (( ${#__orig_args[@]} > 0 )); then
  set -- "${__orig_args[@]}"
fi
unset __orig_args

# shellcheck disable=SC1091
source "${REPO_ROOT}/scripts/lib/gdrive-auth-hint.sh"

export PRESTONOTES_REPO_ROOT="${PRESTONOTES_REPO_ROOT:-$REPO_ROOT}"

E2E_CATALOG="${REPO_ROOT}/scripts/lib/e2e-catalog.txt"

LOCAL_CUSTOMER_DIR="${PRESTONOTES_REPO_ROOT}/MyNotes/Customers/${CUSTOMER}"
GDRIVE_BASE_PATH="${GDRIVE_BASE_PATH:-$HOME/Google Drive/My Drive/MyNotes}"
MOUNT_CUSTOMER_DIR="${GDRIVE_BASE_PATH}/Customers/${CUSTOMER}"
RESTART_WAIT_SEC="${E2E_RESTART_WAIT_SEC:-5}"
MOUNT_DISAPPEAR_TIMEOUT_SEC="${E2E_MOUNT_DISAPPEAR_TIMEOUT_SEC:-180}"
MOUNT_APPEAR_TIMEOUT_SEC="${E2E_MOUNT_APPEAR_TIMEOUT_SEC:-180}"
E2E_DEBUG_FLAG="${PRESTONOTES_E2E_DEBUG:-0}"
E2E_DEBUG_ROOT="${LOCAL_CUSTOMER_DIR}/AI_Insights/e2e-debug"
E2E_DEBUG_ACTIVE_FILE="${E2E_DEBUG_ROOT}/active-run.txt"
E2E_DEBUG_RUN_DIR=""
E2E_DEBUG_ENABLED=0
case "$(printf '%s' "$E2E_DEBUG_FLAG" | tr '[:upper:]' '[:lower:]')" in
  1|true|yes|on) E2E_DEBUG_ENABLED=1 ;;
esac

usage() {
  cat <<USAGE >&2
Usage: $(basename "$0") <command> [args]

  prep-v1 [--skip-rebaseline] [--skip-clean]
            Rebaseline Notes GDoc from template (Drive copy), pull, clean logs + AI_Insights,
            materialize v1, bump dates, push.
  prep-v2   Push local to Drive, pull, materialize v2, bump, push.
  v1        Legacy seed: mount + materialize v1 + bump + push (no GDoc rebaseline, no clean).
  v2        Same as prep-v2.
  reset     Trash Drive folder + wipe local + restart Drive + wait for mount absent.
  list-steps     Eight harness steps + debugger; same content as part of list-catalog.
  list-catalog, list-all
                 Triggers, eight steps, e2e_workflow modes (v1_full, full, …), /tester note.
  debug-path  Print active e2e-debug path (PRESTONOTES_E2E_DEBUG=1 only).
  run-step <1-8>  Run shell step 1 or 5 only; for other numbers print the chat trigger.

SSoT: ${REPO_ROOT}/scripts/lib/e2e-catalog.txt
Full docs: docs/ai/playbooks/tester-e2e-ucn.md
USAGE
  exit 2
}

debug_log_event() {
  local event="${1:-event}"
  local details="${2:-}"
  [[ "${E2E_DEBUG_ENABLED}" -eq 1 ]] || return 0
  [[ -n "${E2E_DEBUG_RUN_DIR}" ]] || return 0
  printf '%s\t%s\t%s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "${event}" "${details}" \
    >> "${E2E_DEBUG_RUN_DIR}/events.log"
}

debug_init_templates_if_missing() {
  [[ "${E2E_DEBUG_ENABLED}" -eq 1 ]] || return 0
  [[ -n "${E2E_DEBUG_RUN_DIR}" ]] || return 0

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/manifest.json" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/manifest.json" <<EOF
{
  "customer": "${CUSTOMER}",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "debug_enabled_via": "PRESTONOTES_E2E_DEBUG=1"
}
EOF
  fi

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/harness-steps-1-8.checklist.md" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/harness-steps-1-8.checklist.md" <<'EOF'
# Harness 1-8 checklist

- [ ] 1 Shell: prep-v1
- [ ] 2 Chat: Load Customer Context for _TEST_CUSTOMER
- [ ] 3 Chat: Extract Call Records for _TEST_CUSTOMER
- [ ] 4 Chat: Update Customer Notes for _TEST_CUSTOMER
- [ ] 5 Shell: prep-v2
- [ ] 6 Chat: Extract Call Records for _TEST_CUSTOMER
- [ ] 7 Chat: Update Customer Notes for _TEST_CUSTOMER
- [ ] 8 Chat: Run Account Summary for _TEST_CUSTOMER
EOF
  fi

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/ucn-steps-1-11.checklist.md" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/ucn-steps-1-11.checklist.md" <<'EOF'
# UCN 1-11 checklist

- [ ] 1 Pull latest notes from Drive
- [ ] 2 Discover Google Doc
- [ ] 3 Read current Google Doc
- [ ] 4 Load transcripts and local context
- [ ] 5 Check rejection watermarks
- [ ] 6 Extract facts and build coverage table
- [ ] 7 Clarification gate (E2E: clarification_gate=none)
- [ ] 8 Build mutation plan with explicit mutate/skip outcomes
- [ ] 9 Approval gate (E2E: approval=bypassed per 11-e2e)
- [ ] 10 Apply approved write_doc changes
- [ ] 11 Append ledger row and report result
EOF
  fi

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/read-doc-pointers.json" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/read-doc-pointers.json" <<'EOF'
{
  "pre_read_doc_path": "",
  "post_read_doc_path": "",
  "notes": "Store durable pointers/paths to read_doc snapshots used for diff."
}
EOF
  fi

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/ledger-attempt.json" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/ledger-attempt.json" <<'EOF'
{
  "status": "pending",
  "attempted_at": "",
  "result_summary": "",
  "error": ""
}
EOF
  fi

  if [[ ! -f "${E2E_DEBUG_RUN_DIR}/mutations.json" ]]; then
    cat > "${E2E_DEBUG_RUN_DIR}/mutations.json" <<'EOF'
{
  "status": "pending",
  "mutations_path": "",
  "notes": "Record the approved mutation JSON path or copy the payload here."
}
EOF
  fi
}

debug_prepare_run_dir() {
  local mode="${1:-continue}"  # start|continue
  [[ "${E2E_DEBUG_ENABLED}" -eq 1 ]] || return 0

  mkdir -p "${E2E_DEBUG_ROOT}"
  local run_id=""

  if [[ "${mode}" == "start" ]]; then
    run_id="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
  elif [[ -f "${E2E_DEBUG_ACTIVE_FILE}" ]]; then
    run_id="$(awk 'NR==1{print; exit}' "${E2E_DEBUG_ACTIVE_FILE}")"
  fi

  if [[ -z "${run_id}" ]]; then
    run_id="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
  fi

  E2E_DEBUG_RUN_DIR="${E2E_DEBUG_ROOT}/${run_id}"
  mkdir -p "${E2E_DEBUG_RUN_DIR}"
  printf '%s\n' "${run_id}" > "${E2E_DEBUG_ACTIVE_FILE}"

  debug_init_templates_if_missing
  debug_log_event "debug_bundle_ready" "mode=${mode} path=${E2E_DEBUG_RUN_DIR}"
}

debug_mark_shell_step() {
  local step="${1:?step required}"
  local result="${2:?result required}"
  [[ "${E2E_DEBUG_ENABLED}" -eq 1 ]] || return 0
  debug_log_event "harness_step_${step}" "result=${result}"
}

debug_print_path() {
  if [[ "${E2E_DEBUG_ENABLED}" -ne 1 ]]; then
    echo "Debug bundle is disabled. Set PRESTONOTES_E2E_DEBUG=1 to enable." >&2
    return 1
  fi
  debug_prepare_run_dir continue
  echo "${E2E_DEBUG_RUN_DIR}"
}

check_gcloud_auth() {
  if ! command -v gcloud >/dev/null 2>&1; then
    echo "ERROR: gcloud CLI not found on PATH. Install Google Cloud SDK, then sign in (see GCLOUD_AUTH_LOGIN_COMMAND in .cursor/mcp.env.example)." >&2
    prestonotes_gdrive_auth_hint
    exit 1
  fi
  if ! gcloud auth print-access-token >/dev/null 2>&1; then
    echo "ERROR: gcloud is not authenticated for Drive API access." >&2
    prestonotes_gdrive_auth_hint
    exit 1
  fi
}

poll_until() {
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
    prestonotes_gdrive_auth_hint
    exit 1
  fi

  cat <<'NEXT'

[reset] COMPLETE. Next: chat trigger "Bootstrap Customer for _TEST_CUSTOMER", then:

    ./scripts/e2e-test-customer.sh prep-v1 --skip-rebaseline

(or prep-v1 without skip after you want GDoc from template again)

NEXT
}

ensure_bootstrapped() {
  if [[ ! -d "${MOUNT_CUSTOMER_DIR}" ]]; then
    echo "WARN: ${MOUNT_CUSTOMER_DIR} not visible yet (typical right after API bootstrap)." >&2
    echo "==> [ensure_bootstrapped] Restarting Google Drive for Desktop (wait ${RESTART_WAIT_SEC}s) ..."
    "${REPO_ROOT}/scripts/restart-google-drive.sh" "${RESTART_WAIT_SEC}"
  fi
  if ! poll_until "${MOUNT_APPEAR_TIMEOUT_SEC}" 3 mount_is_present; then
    echo "ERROR: ${MOUNT_CUSTOMER_DIR} still not found on the Drive mount after restart + wait." >&2
    echo "       Run: Bootstrap Customer for _TEST_CUSTOMER  or check Google Drive for Desktop and GDRIVE_BASE_PATH." >&2
    prestonotes_gdrive_auth_hint
    exit 1
  fi
  echo "==> Syncing Drive → repo mirror: Customers/${CUSTOMER}/"
  "${REPO_ROOT}/scripts/rsync-gdrive-notes.sh" "${CUSTOMER}"
  if [[ ! -d "${LOCAL_CUSTOMER_DIR}" ]]; then
    echo "ERROR: local mirror missing after rsync: ${LOCAL_CUSTOMER_DIR}" >&2
    exit 1
  fi
}

clean_local_harness_artifacts() {
  echo "==> [clean] Removing audit logs and AI_Insights under ${LOCAL_CUSTOMER_DIR} (e2e greenfield) ..."
  rm -f "${LOCAL_CUSTOMER_DIR}/pnotes_agent_log.md" \
        "${LOCAL_CUSTOMER_DIR}/pnotes_agent_log.archive.md" 2>/dev/null || true
  if [[ -d "${LOCAL_CUSTOMER_DIR}/AI_Insights" ]]; then
    find "${LOCAL_CUSTOMER_DIR}/AI_Insights" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
  fi
  mkdir -p "${LOCAL_CUSTOMER_DIR}/AI_Insights"
}

materialize_bump_push() {
  local variant="$1"   # v1 or v2
  local apply_flag=""
  if [[ "${variant}" == "v2" ]]; then
    apply_flag="--v2"
  fi
  echo "==> [${variant}] Materializing fixtures into ${LOCAL_CUSTOMER_DIR}/ ..."
  # shellcheck disable=SC2086
  uv run python "${REPO_ROOT}/scripts/e2e-test-customer-materialize.py" apply ${apply_flag}

  echo "==> [${variant}] Rolling fixture dates (rolling 30-day window) ..."
  uv run python "${REPO_ROOT}/scripts/e2e-test-customer-bump-dates.py" --customer "${CUSTOMER}"

  echo "==> [${variant}] Pushing repo mirror → Drive: Customers/${CUSTOMER}/"
  "${REPO_ROOT}/scripts/e2e-test-push-gdrive-notes.sh" "${CUSTOMER}"
}

print_after_v1() {
  cat <<'V1_NEXT'

[prep-v1 / v1] COMPLETE. Next chat steps (in order):
    Load Customer Context for _TEST_CUSTOMER
    Extract Call Records for _TEST_CUSTOMER
    Update Customer Notes for _TEST_CUSTOMER
Then: ./scripts/e2e-test-customer.sh prep-v2

V1_NEXT
}

print_after_v2() {
  cat <<'V2_NEXT'

[prep-v2] COMPLETE. Next chat steps (in order):
    Extract Call Records for _TEST_CUSTOMER
    Update Customer Notes for _TEST_CUSTOMER
    Run Account Summary for _TEST_CUSTOMER

V2_NEXT
}

cmd_legacy_v1() {
  debug_prepare_run_dir start
  debug_mark_shell_step 1 started
  ensure_bootstrapped
  materialize_bump_push v1
  debug_mark_shell_step 1 completed
  print_after_v1
}

cmd_prep_v1() {
  local skip_reb=0 skip_clean=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skip-rebaseline) skip_reb=1 ;;
      --skip-clean) skip_clean=1 ;;
      -h|--help) usage ;;
      *) echo "Unknown option for prep-v1: $1" >&2; usage ;;
    esac
    shift
  done

  debug_prepare_run_dir start
  debug_mark_shell_step 1 started
  if [[ "${skip_reb}" -eq 0 ]]; then
    check_gcloud_auth
  fi

  if [[ "${skip_reb}" -eq 0 ]]; then
    echo "==> [prep-v1] Rebaselining Notes GDoc from template (E2E script) ..."
    uv run python "${REPO_ROOT}/prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py" "${CUSTOMER}" || {
      echo "ERROR: e2e_rebaseline_customer_gdoc failed. If the customer folder is missing, run" >&2
      echo "  Bootstrap for _TEST_CUSTOMER  (or: reset + bootstrap) then retry." >&2
      prestonotes_gdrive_auth_hint
      exit 1
    }
  else
    echo "==> [prep-v1] --skip-rebaseline: leaving existing Notes GDoc in Drive."
  fi

  ensure_bootstrapped
  if [[ "${skip_clean}" -eq 0 ]]; then
    clean_local_harness_artifacts
  else
    echo "==> [prep-v1] --skip-clean: keeping pnotes_agent_log and AI_Insights."
  fi
  materialize_bump_push v1
  debug_mark_shell_step 1 completed
  print_after_v1
}

cmd_prep_v2() {
  debug_prepare_run_dir continue
  debug_mark_shell_step 5 started
  if [[ ! -d "${LOCAL_CUSTOMER_DIR}/call-records" ]] \
     || ! find "${LOCAL_CUSTOMER_DIR}/call-records" -maxdepth 1 -name '*.json' -print -quit | grep -q .; then
    echo "ERROR: ${LOCAL_CUSTOMER_DIR}/call-records/ has no JSON records." >&2
    echo "       prep-v2 needs round-1 call records. Run prep-v1 and round-1 Extract (and UCN) first." >&2
    exit 1
  fi

  echo "==> [prep-v2] Pushing local repo → Drive (round-1 UCN and call-records must be on Drive before pull) ..."
  "${REPO_ROOT}/scripts/e2e-test-push-gdrive-notes.sh" "${CUSTOMER}"

  ensure_bootstrapped
  materialize_bump_push v2
  debug_mark_shell_step 5 completed
  print_after_v2
}

list_steps() {
  if [[ ! -f "${E2E_CATALOG}" ]]; then
    echo "ERROR: missing ${E2E_CATALOG}" >&2
    exit 1
  fi
  # Eight-step block only: from === EIGHT STEPS ... up to (not including) === WORKFLOW MODES ===
  awk '/^=== EIGHT STEPS /{f=1; next} /^=== WORKFLOW MODES /{exit} f' "${E2E_CATALOG}"
}

list_catalog() {
  if [[ ! -f "${E2E_CATALOG}" ]]; then
    echo "ERROR: missing ${E2E_CATALOG}" >&2
    exit 1
  fi
  cat "${E2E_CATALOG}"
}

run_one_step() {
  case "${1:-}" in
    1) shift; cmd_prep_v1 "$@" ;;
    2) echo "Chat: Load Customer Context for _TEST_CUSTOMER" ;;
    3) echo "Chat: Extract Call Records for _TEST_CUSTOMER" ;;
    4) echo "Chat: Update Customer Notes for _TEST_CUSTOMER" ;;
    5) cmd_prep_v2 ;;
    6) echo "Chat: Extract Call Records for _TEST_CUSTOMER" ;;
    7) echo "Chat: Update Customer Notes for _TEST_CUSTOMER" ;;
    8) echo "Chat: Run Account Summary for _TEST_CUSTOMER" ;;
    *) echo "Step must be 1-8 (see list-steps)" >&2; return 2 ;;
  esac
}

SUB="${1:-}"
case "${SUB}" in
  reset) shift; cmd_reset "$@" ;;
  prep-v1) shift; cmd_prep_v1 "$@" ;;
  prep-v2) shift; cmd_prep_v2 "$@" ;;
  v1) shift; cmd_legacy_v1 "$@" ;;
  v2) shift; cmd_prep_v2 "$@" ;;
  list-steps) list_steps ;;
  list-catalog|list-all) list_catalog ;;
  debug-path) debug_print_path ;;
  run-step)
    shift
    if [[ -z "${1:-}" ]]; then
      echo "run-step needs a number 1-8" >&2
      exit 2
    fi
    s="$1"
    shift
    run_one_step "$s" "$@"
    ;;
  -h|--help|help) usage ;;
  "")
    usage
    ;;
  *) echo "Unknown command: $SUB" >&2; usage ;;
esac
