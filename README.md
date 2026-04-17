# prestonotes

This project uses **[pre-commit](https://pre-commit.com/)** so lint and format checks run automatically before every Git commit. Hooks are defined in **`.pre-commit-config.yaml`**; after you clone the repo, install them once with **`uv run pre-commit install`** (see Getting started).

## Getting started

1. Install prerequisites (see below).
2. Run `./setup_env.sh` to create the Python virtualenv (`uv`), install dev tools, and install npm dev dependencies.
3. Install Git hooks (once per clone): `uv run pre-commit install`
4. Run checks manually anytime: `uv run pre-commit run --all-files`

## Prerequisites

- **Python 3.12+** and **[uv](https://docs.astral.sh/uv/)** for Python packaging and the virtual environment.
- **Node.js** and **npm** (Biome pre-commit hooks use `language: node`).
- **pre-commit** is installed into the project via `uv` (see `pyproject.toml`). After `./setup_env.sh`, run **`uv run pre-commit install`** so commits use the configured hooks.

### OS-level tools (recommended)

Terraform hooks need the Terraform CLI and **tflint** on your `PATH` when you commit `.tf` files. Shell scripts are checked with ShellCheck via **shellcheck-py** in pre-commit (no separate `shellcheck` binary required).

On macOS with Homebrew:

```bash
brew install terraform tflint shellcheck
```

**Docker:** The official ShellCheck pre-commit repository [`koalaman/shellcheck-precommit`](https://github.com/koalaman/shellcheck-precommit) runs ShellCheck inside a Docker image. This project uses [`shellcheck-py`](https://github.com/shellcheck-py/shellcheck-py) instead so hooks work without Docker. To switch to the Docker-based official hook, replace the `shellcheck-py` block in `.pre-commit-config.yaml` with `koalaman/shellcheck-precommit` and keep Docker Desktop running.

## Pre-commit: linters and tools

Pre-commit runs these hooks (see **`.pre-commit-config.yaml`** for pinned versions):

| Hook | What it does |
|------|----------------|
| `ruff-check` | Python lint (`ruff check`) |
| `ruff-format` | Python format (`ruff format`) |
| `biome-check` | JS/TS/CSS/JSON (etc.) format + lint via Biome |
| `shellcheck` | Shell scripts (`shellcheck-py`) |
| `yamllint` | YAML files |
| `terraform_fmt` | Terraform `fmt` |
| `terraform_validate` | Terraform `validate` |
| `terraform_tflint` | Terraform lint with **tflint** |

Source repos for reference:

| Tool | Source repo |
|------|-------------|
| Ruff | [`astral-sh/ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit) |
| Biome | [`biomejs/pre-commit`](https://github.com/biomejs/pre-commit) |
| ShellCheck | [`shellcheck-py/shellcheck-py`](https://github.com/shellcheck-py/shellcheck-py) (bundled binary; Docker alternative documented above) |
| yamllint | [`adrienverge/yamllint`](https://github.com/adrienverge/yamllint) |
| Terraform / tflint | [`antonbabenko/pre-commit-terraform`](https://github.com/antonbabenko/pre-commit-terraform) |

Commands:

```bash
uv run pre-commit install          # once per clone
uv run pre-commit run --all-files  # run all hooks on demand
```

(You can also `source .venv/bin/activate` and run `pre-commit` directly if you prefer.)

## How to test

```bash
source .venv/bin/activate
uv run pytest
uv run pre-commit run --all-files
```

## Troubleshooting

- **Biome hook fails or changes files:** `biome-check` may reformat files (e.g. `package.json`). Stage the changes and commit again.
- **Terraform hooks fail:** Install `terraform` and `tflint`, run `terraform init` in modules that need it, then retry.
- **Switching to Docker-based ShellCheck:** Use `koalaman/shellcheck-precommit` and ensure Docker Desktop is running.

## Dependencies

- Python dev tools: `pyproject.toml` / `uv.lock`
- JavaScript dev tools: `package.json` / `package-lock.json`
# prestonotes
