# Tasks: Pre-commit configuration

1. **Done** — Added `.pre-commit-config.yaml` at the repository root with hooks for **ruff**, **Biome**, **ShellCheck** (via `shellcheck-py`), **yamllint**, and **Terraform / tflint** (`antonbabenko/pre-commit-terraform`). Adjusted `.cursor/skills/lint.sh` for ShellCheck SC2035 and `node_modules/` in `.gitignore`.

2. **Done** — Updated **`README.md`** with prerequisites, `pre-commit install` / `pre-commit run --all-files`, Homebrew installs, and ShellCheck Docker vs `shellcheck-py` notes.

3. **Done** — Ran `pre-commit run --all-files` successfully (with tracked files). Added **`tests/test_pre_commit_config.py`** to assert expected hook repositories are listed.
