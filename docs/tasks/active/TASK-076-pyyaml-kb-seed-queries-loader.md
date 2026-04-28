# TASK-076 — PyYAML loader for `kb_seed_queries.yaml`

**Status:** [ ] OPEN  
**Related:** **TASK-074** §G9.a (seed SSoT). Orchestrates with the **KB seed cache redesign** plan (Cursor plan file `kb_seed_cache_redesign_baca578e.plan.md` if present locally; not committed to this repo by default). This task can land **in the same PR** as that redesign or **just before** it so the fixed YAML file parses correctly.

## Context

- The repository **already declares** the `pyyaml` package in the root [`pyproject.toml`](../../pyproject.toml) (`pyyaml>=6.0.3` in `[project] dependencies`). **No new dependency line is required** unless the version range must change.
- [`scripts/wiz_doc_cache_manager.py`](../../scripts/wiz_doc_cache_manager.py) currently uses a **hand-rolled** [`_parse_seed_yaml`](../../scripts/wiz_doc_cache_manager.py) that only supports a subset of YAML and has been error-prone (e.g. mis-indented list items in `kb_seed_queries.yaml`).
- This task is the **implementation** piece: **replace** that parser with **`yaml.safe_load`** (never `yaml.unsafe_load` / legacy `load`) for **one file**: [`docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml`](../../docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml).

## Scope

1. Load the seed file with **PyYAML** `safe_load`; validate top-level shape: `version` (optional int), `seeds` (list of dicts with `initial_query` str, `results` int defaulting to 1 in code if absent).
2. **Remove** the hand `_parse_seed_yaml` implementation (or keep a one-line wrapper that calls `safe_load` for a single path) so there is one code path.
3. **Callers:** anything that today imports or duplicates seed parsing — at minimum `wiz_doc_cache_manager` and (historical) [`scripts/deprecated/lpi_kb_seed_refresh.py`](../../scripts/deprecated/lpi_kb_seed_refresh.py) (use shared helper).
4. **Tests:** unit test that the real `kb_seed_queries.yaml` parses and yields the expected number of seeds (or a minimal fixture under `scripts/tests/` if the real file is too volatile).
5. **Docs:** note in [`scripts/README.md`](../../scripts/README.md) that seeds are **full YAML** and parsed with PyYAML.

## Non-goals

- Broad YAML loading elsewhere in the repo (unless you explicitly expand scope later).
- Changing the on-disk schema beyond what the KB redesign plan already specifies (`initial_query`, `results`).

## Verification

- `uv run pytest` for new/updated tests.
- `bash .cursor/skills/lint.sh` / `bash .cursor/skills/test.sh` per project practice after related code changes.

## Output / Evidence

- [ ] PyYAML used for `kb_seed_queries.yaml`; hand parser removed or reduced to thin wrapper.
- [ ] Tests green; README note.
