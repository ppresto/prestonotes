# Design: Pre-commit linters (root `.pre-commit-config.yaml`)

## Goal

Add a root-level [pre-commit](https://pre-commit.com/) configuration so that **ruff**, **Biome**, **shellcheck**, **yamllint**, and **tflint** run automatically before every `git commit`, aligning with the core rule to **lint and validate before considering work complete**.

## Scope

- **In scope**: New `.pre-commit-config.yaml` in the repository root; hooks for the five named tools; local developer workflow (`pre-commit install`).
- **Out of scope (for this change)**: CI integration (e.g. GitHub Actions), custom linter rule content beyond defaults, Terraform module layout.

## Approach

1. **Framework**: Use the standard pre-commit hook manager. The project already installs `pre-commit` via `uv` / `setup_env.sh`; hooks will run in the developer environment after `pre-commit install`.
2. **Hook sources**: Prefer **official or widely used pre-commit mirror repos** with pinned `rev` values (updated via `pre-commit autoupdate` when desired). Where no single shared repo fits (e.g. Biome via `npx`/`node_modules`), use a **`repo: local`** hook that invokes the project’s installed CLI (consistent with `package.json` devDependencies).
3. **File targeting**: Restrict each hook to relevant paths (`types`, `files`, or `exclude`) so commits stay fast and unrelated files are not scanned.
4. **System binaries**: **shellcheck** and **tflint** (and Terraform for `terraform validate` if paired with tflint) are typically **OS-level** installs (e.g. Homebrew). The config should assume they are on `PATH` when those hooks run; document prerequisites in setup/README rather than silently failing without guidance.

## Tool mapping (expected)

| Tool       | Role                         | Typical integration notes |
|-----------|------------------------------|---------------------------|
| Ruff      | Python lint/format           | Official `ruff-pre-commit` repo; format + check stages as appropriate. |
| Biome     | JS/TS (and related) lint/format | Local hook running `biome check` (or check --write) via `npx` or `node_modules/.bin`. |
| shellcheck| Shell scripts                | Hook that runs `shellcheck` on `*.sh` (and similar). |
| yamllint  | YAML                         | Hook running `yamllint` on `*.yaml` / `*.yml`. |
| tflint    | Terraform                    | Hook running `tflint` on `*.tf` (and optionally HCL); requires `tflint` installed. |

Exact `rev` pins and `files`/`exclude` patterns are left to implementation and should match this repository’s layout.

## Testing strategy

- After configuration: run `pre-commit install` once per clone, then `pre-commit run --all-files` to verify all hooks execute without configuration errors.
- **Regression**: A commit that only touches unrelated file types should not unnecessarily fail; adjust globs if hooks are too broad.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Missing OS binaries (shellcheck, tflint, terraform) | Document prerequisite installs; optional hook `pass_filenames` / `always_run` only where justified. |
| Slow commits on large repos | Tight `files` filters; developers can use `SKIP` env for rare emergencies (document sparingly). |
| Biome not found | Ensure `npm install` has been run so `npx biome` or local binary resolves. |

## References

- Core rules: `.cursor/rules/core.mdc` (design-first, small steps, TDD, linting).
