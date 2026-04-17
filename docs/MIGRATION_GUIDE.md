# Migration Guide — `prestoNotes.orig` → v2

The **authoritative port/omit table** is [`project_spec.md` §8](project_spec.md#8-legacy-reference-guide). This file adds **process** and **v2 path naming**.

## v2 name for the Google Docs Python stack

| v1 (legacy, read-only) | v2 (this repo) |
|------------------------|----------------|
| `../prestoNotes.orig/custom-notes-agent/` | **`prestonotes_gdoc/`** |

**Why rename:** `custom-notes-agent` implied a single “agent”; v2 splits **reasoning** (`.cursor/rules/`, playbooks) from **Docs API execution** (`prestonotes_gdoc/`). See [`project_spec.md` §4 — Directory structure](project_spec.md#4-directory-structure) (subsection **`prestonotes_gdoc/` vs Cursor sub-agents**).

## Old project location

| Item | Value |
|------|--------|
| Path | `../prestoNotes.orig` (relative to this repo root) |
| Mode | **READ-ONLY** — never modify, never `import` from it at runtime |

When porting: **copy** into `prestonotes_gdoc/` or `prestonotes_mcp/`, then strip machine-specific paths and move embedded LLM prompts into `.mdc` / playbooks per [`project_spec.md` §2](project_spec.md).

## Porting checklist (every file)

Before merging a port:

1. No hardcoded personal paths — use `prestonotes_mcp/config.py` + env + `prestonotes-mcp.yaml` patterns.
2. No secrets in code — no API keys, no pinned `gcloud` account strings in committed files.
3. No long LLM prompt strings in Python — those belong in `.cursor/rules/` or `docs/ai/playbooks/`.
4. New or changed Python has a test under `prestonotes_mcp/tests/` or `scripts/tests/` as appropriate.
5. All `run_uv_script(...)` and `paths.doc_schema` defaults point at **`prestonotes_gdoc/...`**, not `custom-notes-agent/...`.

## `prestonotes_gdoc/` file list (fill in as the port lands)

The first successful CI green build should **list every path** under **`prestonotes_gdoc/`** that the MCP server invokes (discover/read/write/ledger-append/bootstrap).

**Source tree to copy from:** `../prestoNotes.orig/custom-notes-agent/` (per §8). Shrink unused `sections/` modules only if nothing imports them.

**Files confirmed in-tree:**

- _(none yet — update when TASK-003 completes)_

## Discrepancies found (spec vs old code)

_Add dated notes when behavior differs from [`project_spec.md`](project_spec.md)._

| Date | Topic | Spec says | Old code does | Resolution |
|------|--------|-----------|---------------|------------|
| | | | | |
