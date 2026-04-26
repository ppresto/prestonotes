# TASK-066 — GDrive session: `setEnv`, folder id, and copy-paste gcloud re-auth

**Status:** [x] DONE (2026-04-24)  
**Opened:** 2026-04-24  
**Depends on:** None (complements **TASK-044** / E2E harness; optional cross-link with **TASK-065** if touching `workflow.mdc` only).

## Problem

- **`MYNOTES_ROOT_FOLDER_ID`** and **`discover_doc`** require env aligned with what Cursor’s MCP and terminal E2E scripts use; operators set this via **`.cursor/mcp.env`**, loaded by **`source ./setEnv.sh`**, but the contract is not consistently **actionable** when gcloud / Drive access fails.
- On **GDrive or gcloud authentication failure**, agents and scripts should **stop** (as today) but also emit a **single copy-paste recovery command** the operator can run—same string every time, not invented per session.
- **`.cursor/mcp.env.example`** already documents **`GCLOUD_AUTH_LOGIN_COMMAND`**, but **`setEnv.sh`**, E2E shell paths, and **`.cursor/agents/tester.md`** do not yet form one closed loop: *source setEnv → vars available → on auth failure, print the exact `GCLOUD_AUTH_LOGIN_COMMAND` (or point to it without exposing secrets in logs).*

## Goal

Establish a **small, reviewable SSoT** for:

1. Terminal / agent **session init**: from repo root, `source ./setEnv.sh` loads **`PRESTONOTES_REPO_ROOT`**, **`.cursor/mcp.env`**, **`.venv`**, **`MYNOTES_ROOT_FOLDER_ID`**, and **`GCLOUD_AUTH_LOGIN_COMMAND`** (and related vars).
2. **Auth failure path**: any script or **tester** run that bails for gcloud / Drive / mount / discover_doc prerequisites prints **one** recovery line: prefer **`$GCLOUD_AUTH_LOGIN_COMMAND`** if set, else a documented placeholder telling the user to set it in **`mcp.env`** (never commit real account emails in-repo).
3. **Tester** explicitly: before E2E shell steps, note **prereq check** and **Output Contract** addition when blocked: *status `blocked` + `handoff_for_next` includes the copy-paste string or explicit reference*.

## Scope

1. **`setEnv.sh`**
   - After loading **`mcp.env`**, ensure **`GCLOUD_AUTH_LOGIN_COMMAND`** is **exported** when present (or document that it is inherited from `set -a` source—verify behavior in bash and zsh).
   - Optional: **quiet** one-line hint on source when gcloud is not logged in (e.g. `gcloud auth print-access-token` fails) that prints the recovery command—*avoid spamming* on every healthy source; prefer **on-demand** `setEnv.sh --print-gdrive-auth` or print only on failure in scripts.
2. **Shell scripts** that can fail for Drive/gcloud (at minimum audit and update as needed):
   - `scripts/e2e-test-customer.sh` (and any helper it calls for `ensure_bootstrapped` / mount)
   - `scripts/rsync-gdrive-notes.sh`
   - `scripts/e2e-test-push-gdrive-notes.sh`
   - Other scripts that hard-fail on missing mount or gcloud, if they exist and are in the E2E path.
3. **Docs / agent contract**
   - `docs/ai/playbooks/tester-e2e-ucn.md` — Prerequisites: tie **`source ./setEnv.sh`** to **`MYNOTES_ROOT_FOLDER_ID`** + re-auth one-liner from **`mcp.env`**.
   - `.cursor/agents/tester.md` — "How to run" + **Read order** or a short **Session init**: `source setEnv`, confirm `MYNOTES_ROOT_FOLDER_ID` for discover; on gdrive/gcloud block, **Output Contract** must include recovery command.
4. **Rules (minimal)**
   - `.cursor/rules/workflow.mdc` or a **small** optional rule: one paragraph—*Drive-touching work: if auth fails, exit and emit `GCLOUD_AUTH_LOGIN_COMMAND`.* (Avoid duplicating **TASK-065** scope: keep to one file unless INDEX explicitly batches.)

## Non-goals

- No change to MCP **tool** semantics beyond possibly clearer error messages in subprocess wrappers (no new public API).
- No committing real **folder IDs** or **email addresses**—only **`.cursor/mcp.env.example`** placeholders and `setEnv` **comments** with `YOUR_…` style examples.
- No new external dependency beyond existing **`gcloud`** and **`gcloud auth login`**.

## Acceptance

- [x] Sourcing **`./setEnv.sh`** in zsh and bash from repo root exports **`MYNOTES_ROOT_FOLDER_ID`** when set in **`.cursor/mcp.env`**, and **`GCLOUD_AUTH_LOGIN_COMMAND`** is available in the same shell for **`echo "$GCLOUD_AUTH_LOGIN_COMMAND"`** when defined in **`mcp.env`**.
- [x] At least the **E2E-related** shell scripts in Scope print the **same** recovery string on auth / mount / Drive failures (or a single shared helper in **`scripts/lib/`** or inline **DRY** snippet—pick the smallest change).
- [x] **`tester-e2e-ucn.md`** and **`tester.md`** document the init + blocked-output contract.
- [x] Spot-check: simulate missing auth (e.g. subshell with empty `GCLOUD_*` and forced failure) and confirm the printed line matches the **`mcp.env.example`** field name and operator instructions.

## Verification

- [x] Manual: `source ./setEnv.sh` → `test -n "$MYNOTES_ROOT_FOLDER_ID" && test -n "$GCLOUD_AUTH_LOGIN_COMMAND"` when both set in `mcp.env` (local only; do not log secrets).
- [x] `bash scripts/ci/check-repo-integrity.sh` passes.
- [x] Grep: no new hard-coded work email in committed files; only `mcp.env.example` / comments with placeholders.

## Shipped

- **`scripts/lib/gdrive-auth-hint.sh`** — `prestonotes_gdrive_auth_hint`, `prestonotes_source_mcp_env`
- **`setEnv.sh`** — `export` for **`GCLOUD_*`**, **`./setEnv.sh --print-gdrive-auth`**
- **`scripts/e2e-test-customer.sh`**, **`rsync-gdrive-notes.sh`**, **`e2e-test-push-gdrive-notes.sh`** — call hint on gcloud / mount / rebaseline failure; removed hard-coded account from **`check_gcloud_auth`**
- **`.cursor/agents/tester.md`**, **`docs/ai/playbooks/tester-e2e-ucn.md`**, **`.cursor/rules/workflow.mdc`**, **`.cursor/mcp.env.example`**
- **`scripts/ci/required-paths.manifest`** — `scripts/lib/gdrive-auth-hint.sh`

## Suggested sequencing

1. **setEnv** + **shared print helper** (if any).
2. **Scripts** (failures emit recovery).
3. **tester.md** + **tester-e2e-ucn.md** + **workflow** one-liner.
4. **Manual spot-check** + **CI integrity**.

**Approval:** Operator approved in chat 2026-04-24; implementation complete same day.
