# phase2-cleanup — Post Phase 1–2 review (implemented)

## Status

**Phase:** Done (2026-04-19).

**Implemented:** Secrets moved to **`.cursor/mcp.env`** (gitignored) with **`.cursor/mcp.env.example`**; **`.cursor/mcp.json`** uses **`envFile`** only + **`PRESTONOTES_REPO_ROOT`**. Added **`prestonotes_mcp/.env.example`**, **`.gitignore`** entries (`.coverage`, `htmlcov/`, **`mcp.env`**), removed **`scripts/main.py`** and duplicate **`scripts/package*.json`**, trimmed root **`package.json`** dev deps to Biome only, **GitHub Actions CI**, expanded **`required-paths.manifest`**, **`scripts/pyproject.toml`** description, **Ruff** comment + **MIGRATION_GUIDE** subsection, **`prestonotes_gdoc/README.md`** `tools.json` note, **`scripts/README.md`** Biome exclusion note, doc/rule string updates for **`mcp.env`**.

## Acceptance (post-implementation)

- [x] No secrets in committed **`mcp.json`**; local secrets in **`mcp.env`** (copy from example).
- [x] **`.coverage`** / **`htmlcov/`** gitignored; **`mcp.env`** gitignored.
- [x] Dead **`scripts/main.py`** removed; duplicate **`scripts/`** npm tree removed.
- [x] CI runs integrity + pytest + pre-commit on **main** / **phase3**.
- [x] **`required-paths.manifest`** includes critical refs, rules, **`mcp.env.example`**, CI workflow, **`prestonotes_mcp/.env.example`**.

## Next action

None — resume **[`../INDEX.md`](../INDEX.md)** with **TASK-015** (or next chosen task).
