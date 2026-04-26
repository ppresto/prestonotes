# TASK-067 — E2E `/tester`: MCP server prereq checks (fail fast)

**Status:** [x] **DONE** (2026-04-24) — Session init + prerequisites updated in **`.cursor/agents/tester.md`**, **`tester-e2e-ucn.md`**, **`e2e-task-execution-prompt.md`**.  
**Opened:** 2026-04-24  
**Depends on:** **TASK-044** (harness — archived same day; work landed outside the task file), **TASK-064** (tester doctrine); complements **TASK-066** (gcloud / `setEnv` / Drive — archived) — that task covers **terminal** auth; this task covers **Cursor MCP connectivity** before any E2E work.

## Problem

- The **`/tester`** agent can run **`./scripts/e2e-test-customer.sh prep-v1`** and other shell steps when **gcloud** and the **Drive mount** are healthy, then **stall or mis-report** when **prestonotes** (or other required MCP servers) are **not enabled** in the session. That wastes time and confuses the **Output Contract** (shell “green” but no Extract / UCN / `read_doc`).
- **GDrive re-auth** is already a first-class **blocked** path in **`.cursor/agents/tester.md`** (Session init) and **TASK-066**; **MCP availability** is an equally hard prerequisite for chat steps **2–4** and **6–8** of **`tester-e2e-ucn.md`**, but it is not yet a **fail-fast** gate in the same place.

## Goal

1. **Document** which MCP servers must be **enabled in Cursor** before a full E2E or **`v1_full` / `v2_full` / `full`** workflow (see **`.cursor/agents/tester.md` §4**).
2. **Fail fast** at **session start** (before `prep-v1` or, at minimum, before any chat step that needs MCP): if a required server is down, return **`status: blocked`** in the **Output Contract** with an **operator action** line (how to enable MCP in Cursor, which server names), not after partial shell work.
3. **Smoke calls** (read-only, cheap):
   - **prestonotes:** `check_google_auth` (no args) — confirms the server is wired and Google token path works; aligns with existing gcloud story.
   - **wiz-remote** (Cursor display name from server metadata: **`prestoNotes-wiz-remote`**): one lightweight read, e.g. `wiz_docs_knowledge_base` with a short test query — confirms OAuth / tenant path for Wiz product docs used by RAG and playbooks that touch Wiz.

## Scope

| Surface | Change |
| --- | --- |
| **`.cursor/agents/tester.md`** | Expand **Session init (agent; before shell step 1 or any Drive / `discover_doc` work)** to **also** require MCP smokes: run the checks below; if any fail, **`status: blocked`**, `handoff_for_next` = enable MCP in Cursor + server display names, **do not** run `prep-v1` until prestonotes passes (or document order if product prefers smoke-after-`setEnv` only). |
| **`docs/ai/playbooks/tester-e2e-ucn.md`** | **Prerequisites:** new bullet — required MCP servers enabled; link to **`.cursor/agents/tester.md`** Session init; one-line “fail fast if MCP missing.” |
| **`docs/ai/prompts/e2e-task-execution-prompt.md`** (if it exists) | Optional one-line: MCP prereq + pointer to **tester.md** Session init — avoid duplicating the full table. |
| **Implementation note (for agents)** | In **Cursor**, `call_mcp_tool` may require the **server** identifier as shown in the MCP descriptor (e.g. `project-0-prestoNotes-prestonotes`, `project-0-prestoNotes-wiz-remote`) — not always the short label **“prestonotes”**. Document in **tester.md** or a short **Troubleshooting** sub-bulle so implementers do not false-negative “MCP missing” when the name is wrong. |

## Non-goals

- No new **bash** script that pretends to probe Cursor MCP (stdio is not available from a generic shell without duplicating the MCP config).
- No change to **MCP tool semantics** in **`prestonotes_mcp/`** beyond optional clearer error text (prefer docs + agent contract).
- No **CI** block on MCP — developer machines and Cursor session config vary; this is an **agent session** gate.

## Acceptance

- [x] **tester.md** lists **MCP smokes** in **Session init**, in a clear order with **`source ./setEnv.sh`**, **MCP** checks, and **gcloud/Drive** checks, and states **fail fast** behavior (no `prep-v1` if prestonotes smoke fails).
- [x] **tester-e2e-ucn.md** Prerequisites reference the same requirement.
- [x] A **blocked** E2E run documents **`handoff_for_next`**: Settings → **MCP** → enable **`prestonotes`** and **`wiz-remote`** (Cursor display names may differ — match **`.cursor/mcp.json`**; Agent identifiers may look like `project-0-prestoNotes-prestonotes` / `project-0-prestoNotes-wiz-remote`).
- [x] No duplicate long tables: pointer to **tester.md** SSoT.

## Verification

- [ ] Manual: with MCP **disabled**, agent reports **blocked** and does not claim shell-only success for **full** E2E.
- [ ] Manual: with MCP **enabled**, smokes pass (`check_google_auth` + one **wiz** read-only tool).
- [x] `bash scripts/ci/check-repo-integrity.sh` passes (if manifest picks up edited tracked files).

## References

- **E2E eight-step:** `docs/ai/playbooks/tester-e2e-ucn.md`
- **Tester Output Contract + Session init:** `.cursor/agents/tester.md`
- **GDrive / gcloud init (complementary):** archived **TASK-066**; `setEnv.sh`, `scripts/lib/gdrive-auth-hint.sh`
