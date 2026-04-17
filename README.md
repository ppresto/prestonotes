# PrestoNotes

Local workspace for **PrestoNotes** (account-intelligence / Cursor workflows). The same layout works well as a **starting base** for other Python + Cursor projects: see [Use as a template](#use-as-a-template-for-a-new-project).

## Building PrestoNotes v2 (migration from `prestoNotes.orig`)

| Doc | Purpose |
|-----|--------|
| **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** | **Start here** — MVP task order, validation gates, planner workflow, what each stage builds |
| [`docs/project_spec.md`](docs/project_spec.md) | Full architecture and §9 task specs |
| [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) | Legacy tree path, porting checklist, discrepancy log |
| [`examples/BUILD_ADVISORY.md`](examples/BUILD_ADVISORY.md) | Advisory: vertical slices, session habits _(gitignored if `examples/` ignored — open from disk)_ |
| [`docs/tasks/INDEX.md`](docs/tasks/INDEX.md) | Active / backlog / completed tasks |

Temporary rule while migrating: [`.cursor/rules/99-migration-mode.mdc`](.cursor/rules/99-migration-mode.mdc) — archive after **TASK-019**.

## What this base setup gives you

| Piece | Purpose |
|--------|--------|
| **[uv](https://docs.astral.sh/uv/)** + `pyproject.toml` / `uv.lock` | Python version and dependencies, reproducible installs |
| **pytest** + `tests/` | Small test harness (e.g. pre-commit config smoke test) |
| **Ruff** | Lint + format for Python |
| **[pre-commit](https://pre-commit.com/)** | Runs Ruff, Biome, ShellCheck, yamllint, and optional Terraform checks **before** each commit |
| **Biome** + `package.json` | Lint/format for JS/TS/JSON when you add front-end or tooling |
| **`.cursor/agents/`** | Planner, coder, QA, doc agent definitions |
| **`.cursor/rules/`** | Always-on and language-specific Cursor rules |
| **`.cursor/skills/`** | `lint.sh` / `test.sh` helpers agents can run |
| **`docs/project_spec.md`** | Living product/architecture spec (replace with yours when you fork) |
| **`docs/tasks/`** | Lightweight task index + active/archive folders |
| **`scripts/setup_env.sh`** | One-shot dev environment bootstrap |

You do **not** need every tool on your machine on day one—see [Pre-commit (simple explanation)](#pre-commit-simple-explanation).

## Getting started

1. Install **Python 3.12+**, **[uv](https://docs.astral.sh/uv/)**, **Node.js**, and **npm** (Biome hooks need Node).
2. From the repo root, run **`bash scripts/setup_env.sh`** — creates `.venv`, runs `uv sync`, installs npm dev dependencies.
3. Install Git hooks (once per clone): **`uv run pre-commit install`**
4. Run all checks manually anytime: **`uv run pre-commit run --all-files`**

## Pre-commit (simple explanation)

**What it does:** When you `git commit`, pre-commit can run small programs that check (or fix) your files. If a check fails, the commit is blocked until you fix the issue (or fix auto-applied changes and stage them again).

**Do I need Terraform for a Python-only project?**  
**No.** Hooks are wired for **certain file types**. For example, Terraform hooks in `.pre-commit-config.yaml` only run on **Terraform files** (e.g. `*.tf`). If your repo has **no** `.tf` files, those hooks typically **skip**—there is nothing for them to look at. You are not forced to install `terraform` or `tflint` until you actually add Terraform and want those checks.

**When would I install Terraform / tflint?**  
Only if you add `.tf` files and want those hooks to run. If a hook ever complains because a tool is missing, install it (see below) or remove that hook block from `.pre-commit-config.yaml`.

### Hooks in this repo (see `.pre-commit-config.yaml` for versions)

| Hook | What it touches |
|------|------------------|
| **ruff-check** / **ruff-format** | Python |
| **biome-check** | JS/TS/CSS/JSON (etc.) |
| **shellcheck** | Shell scripts (via shellcheck-py, no separate ShellCheck binary) |
| **yamllint** | YAML files |
| **terraform_fmt** / **terraform_validate** / **terraform_tflint** | Only Terraform (`.tf`, etc.) |

### Optional: macOS (Homebrew) if you use Terraform here

```bash
brew install terraform tflint
```

**ShellCheck and Docker:** This repo uses **shellcheck-py** so ShellCheck does not require Docker. The README used to mention a Docker-based alternative; you can still swap to [`koalaman/shellcheck-precommit`](https://github.com/koalaman/shellcheck-precommit) in `.pre-commit-config.yaml` if you prefer Docker.

## How to test

```bash
uv run pytest
uv run pre-commit run --all-files
```

With an activated venv: `source .venv/bin/activate` then the same commands work.

## Project spec and examples (overwrite when you fork)

- **`docs/project_spec.md`** — Full **PrestoNotes** specification: architecture, backlog, triggers. Treat it as an **example of how** to keep a single source of truth for a serious project. When you start a **new** product from this template, **replace** this file with your own spec (or trim it to a short stub and grow it).
- **`docs/tasks/INDEX.md`** — Explains how to name and archive task files; safe to keep as-is.
- **`examples/`** — Sample artifacts / patterns; **not** required for tooling. The directory is **gitignored** so you can keep local drafts without committing them; remove the `examples/` line from `.gitignore` if you want examples tracked in a fork.

The **README** you are reading is the right place for **how to use the repo**; keep **`docs/project_spec.md`** for **what the product is** (once you rename it for your product).

## Use as a template for a new project

To **clone the idea** without breaking this PrestoNotes repo, copy the tree to a new folder or new GitHub repo, then update names in **that copy** only.

### 1. Rename the Python package (in the **new** repo only)

In **`pyproject.toml`**, change:

- **`[project].name`** — e.g. from `prestonotes` to `myproject` (use letters, numbers, hyphens; PEP 503 style).

Then refresh the lockfile and env:

```bash
uv lock
uv sync
```

If you add a real Python **package directory** later (e.g. `src/myproject/`), align its name with `pyproject.toml` and any `tool.ruff` / pytest paths you configure.

### 2. Rename the npm package (optional)

In **`package.json`**, change the **`name`** field to match your project (lowercase, no spaces). Keeps Biome/npm metadata consistent.

### 3. Replace product docs

- Rewrite **`docs/project_spec.md`** (or replace with a short stub + link to external docs).
- Clear or replace **`examples/`** as needed.

### 4. Cursor and branding

- Update **`.cursor/agents/*.mdc`** if prompts reference “PrestoNotes” or paths that no longer exist.
- Adjust **`.cursor/rules/`** so links and `docs/` paths match your layout.

### 5. Do not change the above in this repo

If this checkout stays **PrestoNotes**, leave **`pyproject.toml`** `name = "prestonotes"` and **`package.json`** as-is unless you intentionally rebrand this project. The steps above are for **new** repos created from a copy of the template.

## Troubleshooting

- **Biome hook fails or changes files:** Stage the reformatted files and commit again.
- **Terraform hooks fail:** You added `.tf` files; install `terraform` / `tflint` and run `terraform init` where needed, or remove the Terraform hook block from `.pre-commit-config.yaml` in that project.
- **pre-commit not found:** Run `uv sync` and use `uv run pre-commit …`.

## Dependencies

- Python: **`pyproject.toml`** / **`uv.lock`**
- JavaScript tooling: **`package.json`** / **`package-lock.json`**
