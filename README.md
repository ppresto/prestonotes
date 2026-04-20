# PrestoNotes v2

**PrestoNotes** is a **Cursor-first** workspace for Solutions Engineers: **meeting transcripts**, a **local `MyNotes/` mirror** of Google Drive, **playbooks** (step-by-step markdown), and a **local MCP server** that talks to **Google Docs**, **customer files**, and **sync scripts** — so you can load context, update customer notes, extract structured call records, and (as migration progresses) build journey and account views **without** pasting secrets into chat.

**Migration status:** **Stages 1–2** through **[`docs/tasks/INDEX.md`](docs/tasks/INDEX.md)** (through **TASK-014**) are implemented in this repo. **Stage 3** (domain advisors + orchestrator) and beyond are **not** shipped here yet — see **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** for the full roadmap. Legacy **v1** lived under `../prestoNotes.orig/` (read-only reference).

---

## How it works (short)

1. **Granola** (or your source) produces **per-call** transcripts under Drive → **`scripts/granola-sync.py`** can mirror them into **`MyNotes/Customers/<Customer>/Transcripts/`**.
2. **`sync_notes`** (MCP) or **`scripts/rsync-gdrive-notes.sh`** pulls **MyNotes** from the **Google Drive for Desktop** mount into the repo’s **`MyNotes/`** folder.
3. In **Cursor**, you type a **trigger phrase** (below). The model follows a **playbook** under **`docs/ai/playbooks/`** and uses **MCP tools** where appropriate.
4. **Writes** (Google Doc mutations, ledger rows, call records, journey files, etc.) go through **MCP + your approval** — not free-form paste into live Docs.

There is **no** v1 **`run_pipeline`** / `run-main-task.py` in v2; structured work uses **mutation JSON**, **`write_doc`**, and the other tools listed in **[`docs/project_spec.md`](docs/project_spec.md)**.

---

## Quick setup

| Step | Action |
|------|--------|
| 1 | **Install:** Python **3.12+**, **[uv](https://docs.astral.sh/uv/)**, **Node + npm** (for Biome in pre-commit), **Google Drive for Desktop**, **`gcloud`**, **[Cursor](https://cursor.com)**. |
| 2 | **Bootstrap repo:** from the repo root, run **`./setEnv.sh --bootstrap`** (creates **`.venv`**, **`uv sync`**, npm dev deps). Optional: **`uv run pre-commit install`**. |
| 3 | **Configure MCP:** edit **[`.cursor/mcp.json`](.cursor/mcp.json)** → **`mcpServers.prestonotes.env`**: set **`GDRIVE_BASE_PATH`**, **`MYNOTES_ROOT_FOLDER_ID`**, **`GCLOUD_ACCOUNT`**, **`GCLOUD_AUTH_LOGIN_COMMAND`**, etc. Use **`${workspaceFolder}`** for **`PRESTONOTES_REPO_ROOT`**. |
| 4 | **Optional YAML:** copy **`prestonotes_mcp/prestonotes-mcp.yaml.example`** → **`prestonotes_mcp/prestonotes-mcp.yaml`** if you want a writable local config. The MCP process **does not** read **`prestonotes_mcp/.env`**. |
| 5 | **Cursor:** enable the **prestonotes** MCP server. Cursor runs **`uv run python -m prestonotes_mcp`** with the **`env`** you set. |
| 6 | **Google auth:** if tools return **`run_in_terminal_to_fix`**, run that command in Terminal (from **`mcp.json`**), then retry. |

**First customer folder:** use MCP **`bootstrap_customer`** (default **`dry_run=true`**) or create **`MyNotes/Customers/<Customer>/`** and sync — see **[`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md)**.

---

## MVP playbooks — what to type in Cursor

Use these **exact trigger phrases** (replace `[Customer]` / `[CustomerName]` with the folder name under **`MyNotes/Customers/`**). Each playbook file has numbered steps and MCP names.

### Stage 1 — Customer notes + transcripts + validation

| Trigger (example) | Purpose | Playbook |
|-------------------|---------|----------|
| **`Load Customer Context for [Customer]`** | Read-only snapshot (ingestion weights, transcripts, exports). | [`load-customer-context.md`](docs/ai/playbooks/load-customer-context.md) |
| **`Update Customer Notes for [Customer]`** | Daily Activity + structured Google Doc updates (**approval** before **`write_doc`**), ledger, audit. | [`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) |
| **`Run License Evidence Check for [Customer]`** | License / SKU evidence matrix; may update local summary + ledger columns. | [`run-license-evidence-check.md`](docs/ai/playbooks/run-license-evidence-check.md) |
| **`Extract Call Records for [Customer]`** | Per-call **`Transcripts/*.txt`** → **`call-records/*.json`** + index. | [`extract-call-records.md`](docs/ai/playbooks/extract-call-records.md) |
| **`Test Call Record Extraction for [Customer]`** | Coverage report **`X of Y meetings indexed…`** (gate before leaning on extraction). | [`test-call-record-extraction.md`](docs/ai/playbooks/test-call-record-extraction.md) |

### Stage 2 — Journey, account summary, challenge review

| Trigger (example) | Purpose | Playbook / rule |
|-------------------|---------|-----------------|
| **`Run Journey Timeline for [CustomerName]`** | Narrative + **`write_journey_timeline`** (approval). | [`run-journey-timeline.md`](docs/ai/playbooks/run-journey-timeline.md) · [`.cursor/rules/22-journey-synthesizer.mdc`](.cursor/rules/22-journey-synthesizer.mdc) |
| **`Run Account Summary for [CustomerName]`** | Exec-oriented account summary using the template. | [`run-account-summary.md`](docs/ai/playbooks/run-account-summary.md) · [`exec-summary-template.md`](docs/ai/references/exec-summary-template.md) |
| **`Run Challenge Review for [CustomerName]`** | Challenge table, stall signals, optional **`update_challenge_state`** (approval per change). | [`run-challenge-review.md`](docs/ai/playbooks/run-challenge-review.md) |

**Full trigger table** (MVP + future): **[`docs/project_spec.md` §11](docs/project_spec.md#11-trigger-phrase-reference-mvp)**.

---

## MCP tools (cheat sheet)

- **Reads (examples):** **`check_google_auth`**, **`list_customers`**, **`discover_doc`**, **`read_doc`**, **`read_transcripts`**, **`read_call_records`**, **`read_transcript_index`**, **`read_ledger`**, **`sync_notes`**, **`sync_transcripts`**, …
- **Writes (always show a plan + get approval in chat):** **`write_doc`**, **`append_ledger`** (v1 row via subprocess), **`append_ledger_v2`** (24-column JSON row — migrate ledger first: **`uv run python -m prestonotes_mcp.tools.migrate_ledger --customer "<Name>"`**), **`write_call_record`**, **`update_transcript_index`**, **`write_journey_timeline`**, **`update_challenge_state`**, **`bootstrap_customer`** (`dry_run=false` only after approval), **`log_run`**, …

Details and guardrails: **[`docs/project_spec.md`](docs/project_spec.md)** (especially **Rule 3** / customer-local writes). **Auth failures** often include **`run_in_terminal_to_fix`** — paste that command from **`mcp.json`**.

---

## Dig deeper (when you need more than the README)

| Doc | Use it for |
|-----|------------|
| **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** | Task order, gates, what each stage builds |
| **[`docs/project_spec.md`](docs/project_spec.md)** | Architecture, schemas (e.g. §7), full backlog §9 |
| **[`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md)** | `prestonotes_gdoc/` vs v1, Granola, rsync, ledger v2, journey tools |
| **[`docs/tasks/INDEX.md`](docs/tasks/INDEX.md)** | What shipped / what’s next |
| **[`scripts/README.md`](scripts/README.md)** | **`granola-sync`**, **`rsync-gdrive-notes`**, flags, Drive helpers |
| **[`docs/ai/references/`](docs/ai/references/)** | Ingestion weights, mutation rules, taxonomies, templates |

**Cursor:** subagents **`coder` / `tester` / `doc`** live under **[`.cursor/agents/`](.cursor/agents/)**; orchestration rules in **[`.cursor/rules/workflow.mdc`](.cursor/rules/workflow.mdc)** (default **`/coder` → `/tester` → `/doc`**, or **`same session, inline`** when you want one chat). While migrating, **[`.cursor/rules/99-migration-mode.mdc`](.cursor/rules/99-migration-mode.mdc)** stays on until **TASK-019**.

---

## Developer quality (optional)

- **Tests:** `uv run pytest` · **`bash .cursor/skills/test.sh`**
- **Lint / format:** **`bash .cursor/skills/lint.sh`** · **`uv run pre-commit run --all-files`**
- **Repo file manifest:** **`bash scripts/ci/check-repo-integrity.sh`**

**Pre-commit** runs Ruff, Biome, ShellCheck (via shellcheck-py), yamllint, and **Terraform hooks only if you have `.tf` files`** — you do not need Terraform for a Python-only tree. See **`.pre-commit-config.yaml`** for versions.

---

## Use as a template for a new project

To fork the **pattern** (not this PrestoNotes product): copy the tree, then in the **copy** rename **`pyproject.toml`** `[project].name`, run **`uv lock`**, update **`package.json` `name`**, replace **`docs/project_spec.md`**, and fix **`.cursor/`** paths that still say “PrestoNotes”. **Do not** change those in **this** repo unless you intend to rebrand here.

---

## Troubleshooting

| Symptom | What to try |
|---------|----------------|
| **Google / Docs tools fail** | Run **`check_google_auth`**. If the response includes **`run_in_terminal_to_fix`**, paste that **exact** command (from **`.cursor/mcp.json`** / `GCLOUD_*`) in Terminal, finish browser login, retry. |
| **`append_ledger_v2` raises migrate error** | Standard ledger table is still **19** columns. Run **`uv run python -m prestonotes_mcp.tools.migrate_ledger --customer "<Customer>"`** (or **`--fixture`** / **`--dry-run`**). See **`docs/MIGRATION_GUIDE.md`** (History Ledger v2). |
| **Drive path not found** | Confirm **Google Drive for Desktop** is running; **`GDRIVE_BASE_PATH`** matches your mount; optional **`./scripts/restart-google-drive.sh`**. |
| **Biome / pre-commit reformats files** | Stage the changes and commit again. |
| **Terraform hooks complain** | You have **`.tf`** files; install Terraform / tflint or narrow the hook in **`.pre-commit-config.yaml`**. |
| **`pre-commit` not found** | Run **`uv sync`** and use **`uv run pre-commit …`**. |

---

## Dependencies

- **Python:** **`pyproject.toml`** / **`uv.lock`**
- **JS tooling:** **`package.json`** / **`package-lock.json`**
