# TASK-001 — Scaffold the repo

## Status

| Field | Value |
|--------|--------|
| **Phase** | Ready — **complete** (2026-04-17) |
| **Spec reference** | [`project_spec.md` §9 — TASK-001](../../project_spec.md#task-001--scaffold-the-repo) |

---

## Legacy Reference

| | |
|--|--|
| **Primary reference (deps / versions)** | `../prestoNotes.orig/pyproject.toml` — aligned dev groups / Python bound in `pyproject.toml` |
| **What to strip** | N/A for scaffold |

---

## Goal

Establish the **v2 repo skeleton** so later tasks can add `prestonotes_mcp`, port `prestonotes_gdoc/`, and scripts.

---

## Completion evidence

| Check | Result |
|--------|--------|
| `uv run python -c "import prestonotes_mcp"` | exit 0 |
| `bash scripts/ci/check-repo-integrity.sh` | exit 0 |
| `uv run pytest` | pass |
| `bash .cursor/skills/lint.sh` | pass |
| `uv run pre-commit run --all-files` | pass |

**Notable files:** `prestonotes_mcp/__init__.py`, `prestonotes_gdoc/README.md`, `docs/ai/playbooks/`, `docs/ai/references/`, `scripts/ci/check-repo-integrity.sh`, `scripts/ci/required-paths.manifest`, `pyproject.toml` (v2.0.0 + setuptools), `.yamllint` (ignore vendor trees), `.cursor/skills/lint.sh` (`uv run` + `run_py` helper).

---

## Acceptance / tests (Definition of Done)

- [x] `python -c "import prestonotes_mcp"` exits **0** (after `uv sync`).
- [x] `bash scripts/ci/check-repo-integrity.sh` exits **0**.
- [x] `uv run pytest` exits **0**.
- [x] Ruff on `prestonotes_mcp/` and CI scripts passes (via `ruff check .` and pre-commit).
