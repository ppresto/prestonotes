# TASK-045 — MCP tool-call audit log under `./logs` (not `tmp/`)

**Status:** [x] DONE  
**Opened:** 2026-04-21  
**Closed:** 2026-04-21  
**Related code:** `prestonotes_mcp/security.py` (`_audit_path`, `_write_audit`), `prestonotes_mcp/prestonotes-mcp.yaml.example`, `prestonotes_mcp/server.py` (`read_audit_log` / `audit_log_exists` resolve via same config).

---

## Problem

`paths.audit_log_rel` defaults to **`tmp/mcp-audit.log`** in code and in the example YAML. Every MCP tool invocation appends a JSON line (`security.tool_scope` → `_write_audit`). That is a **durable audit trail**, not ephemeral mutation scratch like `write_doc` uses under `tmp/`. Co-locating the audit file under `tmp/` is misleading and clutters the temp directory.

---

## Required end-state

1. **Default audit path** is under the repo log directory: e.g. **`logs/mcp-audit.log`** (relative to repo root, same resolution style as today via `ctx.path(*rel.split("/"))`).
2. **`prestonotes-mcp.yaml.example`** sets `paths.audit_log_rel` to that same default so new configs match code.
3. **`.gitignore`** already includes **`logs/`** — confirm it remains present and clearly covers local audit output (no committed log files). If anything still documents `tmp/mcp-audit.log` as the canonical location, update those references.
4. **Optional migration note** (README or MCP docs only if already documenting the path): operators with existing `prestonotes-mcp.yaml` may still have `audit_log_rel: tmp/mcp-audit.log`; they can delete the old file after switching config, or one-time copy old tail into the new file if they care about continuity.

---

## Scope (implementation checklist)

- [x] Change `_audit_path()` default in `prestonotes_mcp/security.py` from `tmp/mcp-audit.log` to `logs/mcp-audit.log`.
- [x] Update `audit_log_rel` in `prestonotes_mcp/prestonotes-mcp.yaml.example`.
- [x] Grep the repo for `mcp-audit`, `audit_log_rel`, or `tmp/mcp-audit` and align docs/comments.
- [x] Run targeted tests (`pytest prestonotes_mcp/tests/...`) if any assert paths or fixtures reference the old default.

## Verification (evidence)

- `uv run pytest prestonotes_mcp/tests/test_security_audit_path.py prestonotes_mcp/tests/test_server_write_tools.py -v` — pass
- `uv run pytest prestonotes_mcp/tests/ -q` — 49 passed, 1 skipped
- `uv run ruff check prestonotes_mcp/security.py prestonotes_mcp/tests/test_security_audit_path.py` — pass

---

## Out of scope

- Changing **`tmp/`** gitignore rules or **`write_doc`** mutation file layout (still belongs under `tmp/`).
- Centralizing every script in the repo that might write ad-hoc logs — only ensure **MCP audit** defaults and documented config live under **`logs/`** unless this task discovers another first-party **persistent** log file incorrectly defaulting to `tmp/`.

---

## Acceptance

- Fresh server with no `paths.audit_log_rel` override writes audit lines to **`logs/mcp-audit.log`** (directory created as today).
- **`logs/`** is git-ignored; no new tracked log artifacts.
