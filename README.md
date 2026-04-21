# PrestoNotes v2

**PrestoNotes** is a **Cursor-first** workspace for Solutions Engineers: **meeting transcripts**, a **local `MyNotes/` mirror** of Google Drive, **playbooks** (step-by-step markdown), and a **local MCP server** that talks to **Google Docs**, **customer files**, and **sync scripts** — so you can load context, update customer notes, extract structured call records, and (as migration progresses) build journey and account views **without** pasting secrets into chat.

**Migration status:** **Stages 1–3** implementation **artifacts** through **[`docs/tasks/INDEX.md`](docs/tasks/INDEX.md)** are **in this repo** — domain advisor **`.mdc`** files, **[`.cursor/rules/10-task-router.mdc`](.cursor/rules/10-task-router.mdc)** / **[`20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc)**, and playbooks under **`docs/ai/playbooks/`**. **Stage 4** adds optional **Wiz doc RAG** (MCP **`wiz_knowledge_search`**, local Chroma) — see **Wiz RAG (Stage 4)** below. See **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** §11 and the roadmap. Legacy **v1** lived under `../prestoNotes.orig/` (read-only reference).

### Activity recap

**Who this is for:** Solutions Engineers using Cursor with **MyNotes**, Google Drive–backed notes, and optional Wiz search.

- You can jump to each **MVP playbook** from one list and match it to what you type in chat.
- You can scan **Full**, **Partial**, or **Gap** for those five flows plus vector RAG, using the same labels as **[`docs/tasks/active/TASK-034-mvp-five-flows-readiness.md`](docs/tasks/active/TASK-034-mvp-five-flows-readiness.md)**.
- You get a **short checklist** of what to configure before you ask the model to run customer or Wiz-heavy work so tools do not fail without a clear reason.

---

## If you are new here (10-minute path)

1. **Read** **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** — what shipped in each stage and what “MVP” means for this repo.  
2. **Install** Python **3.12+**, **[uv](https://docs.astral.sh/uv/)**, **Google Drive for Desktop**, **`gcloud`**, **[Cursor](https://cursor.com)**.  
3. **Bootstrap:** from the repo root run **`./setEnv.sh --bootstrap`** (creates **`.venv`**, runs **`uv sync`**).  
4. **Secrets:** copy **[`.cursor/mcp.env.example`](.cursor/mcp.env.example)** → **`.cursor/mcp.env`** (gitignored). Fill Drive path, **`MYNOTES_ROOT_FOLDER_ID`**, and `gcloud` account.  
5. **Cursor MCP:** enable **prestonotes** in Cursor; reload the window.  
6. **First playbook:** open **[`docs/ai/playbooks/load-customer-context.md`](docs/ai/playbooks/load-customer-context.md)** and run **`Load Customer Context for [Customer]`** (replace with a folder under **`MyNotes/Customers/`**).  
7. **When editing customer docs:** use **`Update Customer Notes for [Customer]`** — it always stops for **approval** before **`write_doc`**.

---

## Documentation map

| You want to… | Start here |
|--------------|------------|
| Understand architecture, schemas, backlog | **[`docs/project_spec.md`](docs/project_spec.md)** |
| Task order and gates | **[`docs/V2_MVP_BUILD_PLAN.md`](docs/V2_MVP_BUILD_PLAN.md)** |
| What is done / next | **[`docs/tasks/INDEX.md`](docs/tasks/INDEX.md)** |
| GDrive + Granola + ledger v2 | **[`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md)** |
| Wiz cache, MCP vs firewall, scripts | **[`docs/ai/references/wiz-mcp-tools-inventory.md`](docs/ai/references/wiz-mcp-tools-inventory.md)** · **[`docs/ai/cache/wiz_mcp_server/README.md`](docs/ai/cache/wiz_mcp_server/README.md)** |
| Run cache -> vector -> search tutorial | **[`docs/tutorials/wiz-rag-from-cache-to-search.md`](docs/tutorials/wiz-rag-from-cache-to-search.md)** |
| Shell scripts (rsync, Wiz, e2e) | **[`scripts/README.md`](scripts/README.md)** |

### MVP actions (5)

Each item is the playbook file under **`docs/ai/playbooks/`** (use the trigger phrase inside the file in Cursor).

| Action | Playbook |
|--------|----------|
| Bootstrap customer (local tree + Drive handoff) | **[`bootstrap-customer.md`](docs/ai/playbooks/bootstrap-customer.md)** |
| Load product intelligence (cache + optional refresh) | **[`load-product-intelligence.md`](docs/ai/playbooks/load-product-intelligence.md)** |
| Load customer context (sync, reads, Wiz when needed) | **[`load-customer-context.md`](docs/ai/playbooks/load-customer-context.md)** |
| Run account summary (narrative in chat today) | **[`run-account-summary.md`](docs/ai/playbooks/run-account-summary.md)** |
| Update customer notes (plan + approval before Doc updates) | **[`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md)** |

Readiness detail and follow-up tasks: **[`TASK-034-mvp-five-flows-readiness.md`](docs/tasks/active/TASK-034-mvp-five-flows-readiness.md)**.

### Capability at a glance

Labels match **TASK-034**: **Full** = main agent path works with normal approvals and documented setup; **Partial** = works with clear limits or extra operator steps; **Gap** = planned file or tool still missing.

| MVP flow or capability | Status |
|------------------------|--------|
| Bootstrap customer (local scaffold + Drive) | **Partial** |
| Load product intelligence (cache read vs **`mcp-materialize`**) | **Partial** |
| Load customer context (+ Wiz in session) | **Full** |
| Run account summary → **`*-AI-AcctSummary.md`** on disk | **Partial** |
| Update customer notes (Doc updates + approval) | **Partial** |
| Vector RAG (**`wiz_knowledge_search`**) | **Partial** |

**Partial** on bootstrap: local **`bootstrap_customer`** is ready; first remote Drive folder + doc is still you + Google. **Partial** on load PI: read path is **local** cache unless you run materialize / spider. **Full** on load customer context: the playbook now includes explicit Wiz pivot + stale-cache refresh guidance during the same session. **Partial** on account summary: playbook now defines canonical `AI_Insights/*-AI-AcctSummary.md` path, but saving is manual until a dedicated MCP writer exists. **Partial** on update notes: **largely ready** with source-order and quality-bar tuning landed in **TASK-038**. **Partial** on vectors: needs keys, cache roots, and **`build_vector_db`** (see **Wiz product docs + RAG** below and tutorial link).

### Before you ask the LLM

- **`.cursor/mcp.env`** filled from **[`.cursor/mcp.env.example`](.cursor/mcp.env.example)** — Drive path, **`MYNOTES_ROOT_FOLDER_ID`**, `gcloud` account, optional **`WIZ_*`**, embedding key for vectors.
- **Drive sync** so **`MyNotes/`** matches Google Drive — **`sync_notes`** (MCP) or **`scripts/rsync-gdrive-notes.sh`** (see **[`scripts/README.md`](scripts/README.md)**).
- **`WIZ_*`** (and wiz-local or CLI) when you need **live** tenant doc pull or **`mcp-materialize`**, not only static cache files.
- **`GOOGLE_API_KEY`** or **`GEMINI_API_KEY`** when you want embeddings / **`wiz_knowledge_search`** after **`build_vector_db`**.
- **`gcloud` login** the first time tools return **`run_in_terminal_to_fix`** — run the exact command from **`mcp.env`**, finish browser login, retry.

The model should **ask** for any missing item instead of failing without saying why (**TASK-034**).

---

## How it works (short)

1. **Granola** (or your source) produces **per-call** transcripts under Drive → **`scripts/granola-sync.py`** can mirror them into **`MyNotes/Customers/<Customer>/Transcripts/`**.
2. **`sync_notes`** (MCP) or **`scripts/rsync-gdrive-notes.sh`** pulls **MyNotes** from the **Google Drive for Desktop** mount into the repo’s **`MyNotes/`** folder.
3. In **Cursor**, you type a **trigger phrase** (below). The model follows a **playbook** under **`docs/ai/playbooks/`** and uses **MCP tools** where appropriate.
4. **Writes** (Google Doc mutations, ledger rows, call records, journey files, etc.) go through **MCP + your approval** — not free-form paste into live Docs.

There is **no** v1 **`run_pipeline`** / `run-main-task.py` in v2; structured work uses **mutation JSON**, **`write_doc`**, and the other tools listed in **[`docs/project_spec.md`](docs/project_spec.md)**.

---

## Setup (detailed)

| Step | Action |
|------|--------|
| 1 | **Install:** Python **3.12+**, **[uv](https://docs.astral.sh/uv/)**, **Google Drive for Desktop**, **`gcloud`**, **[Cursor](https://cursor.com)**. |
| 2 | **Bootstrap repo:** from the repo root, run **`./setEnv.sh --bootstrap`** (creates **`.venv`**, **`uv sync`**). Optional: **`uv run pre-commit install`**. |
| 3 | **Configure MCP (secrets off-repo):** copy **[`.cursor/mcp.env.example`](.cursor/mcp.env.example)** → **`.cursor/mcp.env`** (gitignored) and replace placeholders with your Drive path, folder ID, and `gcloud` account. **[`.cursor/mcp.json`](.cursor/mcp.json)** only sets **`PRESTONOTES_REPO_ROOT`** and points **`envFile`** at **`mcp.env`**. See [Cursor MCP — STDIO](https://cursor.com/docs/mcp). |
| 4 | **Optional YAML:** copy **`prestonotes_mcp/prestonotes-mcp.yaml.example`** → **`prestonotes_mcp/prestonotes-mcp.yaml`** if you want a writable local config. The MCP process **does not** read **`prestonotes_mcp/.env`** (see **`prestonotes_mcp/.env.example`** for optional shell exports only). |
| 5 | **Cursor:** enable the **prestonotes** MCP server. Cursor runs **`uv run python -m prestonotes_mcp`** with **`mcp.json`** + **`mcp.env`**. |
| 6 | **Google auth:** if tools return **`run_in_terminal_to_fix`**, run that command in Terminal (from **`mcp.env`** / your login command), then retry. |
| 7 | **Optional wiz-local:** clone **[wiz-sec/wiz-mcp](https://github.com/wiz-sec/wiz-mcp)** and set **`WIZ_MCP_CHECKOUT`** in **`wiz-mcp/config.sh`** (or **`wiz-mcp/config.local.sh`**) if not using the default **`~/Projects/wiz-mcp`**. Put **`WIZ_CLIENT_ID`**, **`WIZ_CLIENT_SECRET`**, and **`WIZ_ENV`** in **`.cursor/mcp.env`** (same file as step 3). Enable the **wiz-local** server in Cursor. Run **`./wiz-mcp/diagnose.sh`** to verify OAuth. Details: **[`wiz-mcp/README.md`](wiz-mcp/README.md)**. Do **not** run **`wiz-mcp/setup-cursor.sh`** alone — it overwrites **`mcp.json`**. |

**MCP tool-call audit:** When **`security.audit_tool_calls`** is enabled (default in **`prestonotes-mcp.yaml.example`**), each tool invocation appends one JSON line to **`logs/mcp-audit.log`** at the repo root (default **`paths.audit_log_rel`**). The **`logs/`** directory is gitignored. Inspect entries with **`read_audit_log`**. If an older **`prestonotes-mcp.yaml`** still sets **`audit_log_rel: tmp/mcp-audit.log`**, update it to **`logs/mcp-audit.log`** and delete the old file under **`tmp/`**, or copy the tail of the old log into the new file if you need continuity.

### Wiz product docs + RAG (Stage 4)

**Constraint:** **`docs.wiz.io`** is usually **not** bulk-downloadable from your laptop (firewall). Use **tenant GraphQL** (same contract as **`search_wiz_docs`**) to refresh local text:

```bash
uv run python scripts/wiz_doc_cache_manager.py mcp-materialize --min-age-days 7 --delay-seconds 2.5
```

That writes **`docs/ai/cache/wiz_mcp_server/mcp_materializations/*.md`**. Optional **public** blog pages: **`wiz_doc_cache_manager.py spider-ext`** (see **`docs/ai/cache/wiz_mcp_server/README.md`**).

Set **`GOOGLE_API_KEY`** (or **`GEMINI_API_KEY`**) and optionally **`PRESTONOTES_GEMINI_EMBEDDING_MODEL`** (default **`text-embedding-004`**) in **`.cursor/mcp.env`**. **Ingest roots** in **`prestonotes-mcp.yaml`**: **`wiz_docs_cache`** (static WIN), **`wiz_mcp_materializations`** (GraphQL snapshots), optional **`wiz_ext_pages`**. Build Chroma with **`uv run python -m prestonotes_mcp.ingestion.build_vector_db`** (**`--dry-run`** counts files, **`--reset`** rebuilds, **`--no-ingest-mcp`** to skip MCP dir). In Cursor: **`wiz_knowledge_search`**, **`refresh_wiz_vector_index`**. Status: **`uv run python scripts/wiz_doc_cache_manager.py vector-index-status --repo-root .`**

Hands-on walkthrough: **[`docs/tutorials/wiz-rag-from-cache-to-search.md`](docs/tutorials/wiz-rag-from-cache-to-search.md)**.

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
| **`Extract Call Records for [Customer]`** | Per-call **`Transcripts/*.txt`** → **`call-records/*.json`** (sole enumeration API: **`read_call_records`**). | [`extract-call-records.md`](docs/ai/playbooks/extract-call-records.md) |
| **`Test Call Record Extraction for [Customer]`** | Coverage report **`X of Y meetings indexed…`** (gate before leaning on extraction). | [`test-call-record-extraction.md`](docs/ai/playbooks/test-call-record-extraction.md) |

### Stage 2 — Account summary

| Trigger (example) | Purpose | Playbook / rule |
|-------------------|---------|-----------------|
| **`Run Account Summary for [CustomerName]`** | Exec + account narrative in one pass — 30-Second Brief, Health line, chronological call spine, milestones, challenge review (sourced from `challenge-lifecycle.json`), stakeholder evolution, value realized, strategic position, Wiz commercials, open challenges. Exec-only cut skips the optional sections. | [`run-account-summary.md`](docs/ai/playbooks/run-account-summary.md) · [`exec-summary-template.md`](docs/ai/references/exec-summary-template.md) |

### Stage 3 — Advisors, router, and validation

| Trigger (example) | Purpose | Playbook / rules |
|-------------------|---------|------------------|
| **`Update Customer Notes for [Customer]`** | Same trigger as Stage 1; **task router** may steer the session toward the **orchestrator** (multi-advisor flow) — see playbook header. | [`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) · [`.cursor/rules/10-task-router.mdc`](.cursor/rules/10-task-router.mdc) · [`.cursor/rules/20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc) |

**Full trigger table** (MVP + future): **[`docs/project_spec.md` §11](docs/project_spec.md#11-trigger-phrase-reference-mvp)**.

---

## MCP tools (cheat sheet)

- **Reads (examples):** **`check_google_auth`**, **`list_customers`**, **`discover_doc`**, **`read_doc`**, **`read_transcripts`**, **`read_call_records`**, **`read_ledger`**, **`read_challenge_lifecycle`**, **`read_audit_log`** (tail of **`logs/mcp-audit.log`** by default), **`wiz_knowledge_search`**, **`sync_notes`**, **`sync_transcripts`**, …
- **Writes (always show a plan + get approval in chat):** **`write_doc`**, **`append_ledger`** (v1 row via subprocess), **`append_ledger_v2`** (24-column JSON row — migrate ledger first: **`uv run python -m prestonotes_mcp.tools.migrate_ledger --customer "<Name>"`**), **`write_call_record`**, **`update_challenge_state`** (requires `transitioned_at` — the ISO **call date** of the cited transcript, **not** the run date; see **TASK-048**), **`bootstrap_customer`** (`dry_run=false` only after approval), **`log_run`**, …

Details and guardrails: **[`docs/project_spec.md`](docs/project_spec.md)** (especially **Rule 3** / customer-local writes). **Auth failures** often include **`run_in_terminal_to_fix`** — paste that command from **`.cursor/mcp.env`** (or **`GCLOUD_AUTH_LOGIN_COMMAND`** there).

---

## Advanced workflows

- **Wiz cache refresh:** trigger **`Refresh Wiz Doc Cache`** → **`docs/ai/playbooks/refresh-wiz-doc-cache.md`** (`mcp-materialize`, `spider-ext`, manifest).  
- **Broad product context:** **`Load Product Intelligence`** → **`docs/ai/playbooks/load-product-intelligence.md`** (reads `docs/` + `mcp_materializations/` when present).  
- **Sub-agents:** **`coder`**, **`tester`**, **`doc`** under **[`.cursor/agents/`](.cursor/agents/)**; orchestration in **[`.cursor/rules/workflow.mdc`](.cursor/rules/workflow.mdc)**.

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
| **[`.cursor/rules/10-task-router.mdc`](.cursor/rules/10-task-router.mdc)** / **[`20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc)** | Routes **`Update Customer Notes for [Name]`** toward the orchestrator; multi-advisor flow and approval gates (see **`workflow.mdc`**). |
| Domain advisors **`23`–`27`** | **[`.cursor/rules/23-domain-advisor-soc.mdc`](.cursor/rules/23-domain-advisor-soc.mdc)** … **`27-domain-advisor-ai.mdc`** — SOC / APP / VULN / ASM / AI context for structured updates. |

**Cursor:** subagents **`coder` / `tester` / `doc`** live under **[`.cursor/agents/`](.cursor/agents/)**; orchestration rules in **[`.cursor/rules/workflow.mdc`](.cursor/rules/workflow.mdc)** (default **`/coder` → `/tester` → `/doc`**, or **`same session, inline`** when you want one chat). The former **migration-mode** Cursor rule was **retired** at Phase 3 close-out; a read-only copy lives under **[`docs/archive/cursor-rules-retired/`](docs/archive/cursor-rules-retired/)**. Ongoing porting discipline: **`docs/MIGRATION_GUIDE.md`** and **`workflow.mdc`**.

---

## Developer quality (optional)

- **Tests:** `uv run pytest` · **`bash .cursor/skills/test.sh`**
- **Lint / format:** **`bash .cursor/skills/lint.sh`** · **`uv run pre-commit run --all-files`**
- **Repo file manifest:** **`bash scripts/ci/check-repo-integrity.sh`**
- **CI:** GitHub Actions **`.github/workflows/ci.yml`** runs integrity + pytest + pre-commit on pushes and PRs to **main** and **phase3**.

**Pre-commit** runs Ruff, ShellCheck (via shellcheck-py), yamllint, and **Terraform hooks only if you have `.tf` files`** — you do not need Terraform for a Python-only tree. See **`.pre-commit-config.yaml`** for versions.

---

## Use as a template for a new project

To fork the **pattern** (not this PrestoNotes product): copy the tree, then in the **copy** rename **`pyproject.toml`** `[project].name`, run **`uv lock`**, replace **`docs/project_spec.md`**, and fix **`.cursor/`** paths that still say “PrestoNotes”. **Do not** change those in **this** repo unless you intend to rebrand here.

---

## Troubleshooting

| Symptom | What to try |
|---------|----------------|
| **Google / Docs tools fail** | Ensure **`.cursor/mcp.env`** exists (copy from **`mcp.env.example`**). Run **`check_google_auth`**. If the response includes **`run_in_terminal_to_fix`**, paste that **exact** command from **`mcp.env`** in Terminal, finish browser login, retry. |
| **MCP server fails to start (missing env)** | Create **`.cursor/mcp.env`** from the example; **`mcp.json`** no longer embeds Drive / account variables. |
| **`Invalid customer_name (pattern)` for `_TEST_CUSTOMER`** | Restart the **prestonotes** MCP server (or reload Cursor) after pulling the fix. If you copied **`prestonotes_mcp/prestonotes-mcp.yaml`** from the example earlier, update **`security.customer_name_pattern`** to allow a leading underscore (see **`TASK-041`**). |
| **`append_ledger_v2` raises migrate error** | Standard ledger table is still **19** columns. Run **`uv run python -m prestonotes_mcp.tools.migrate_ledger --customer "<Customer>"`** (or **`--fixture`** / **`--dry-run`**). See **`docs/MIGRATION_GUIDE.md`** (History Ledger v2). |
| **Drive path not found** | Confirm **Google Drive for Desktop** is running; **`GDRIVE_BASE_PATH`** matches your mount; optional **`./scripts/restart-google-drive.sh`**. |
| **Ruff / pre-commit reformats Python** | Stage the changes and commit again. |
| **Terraform hooks complain** | You have **`.tf`** files; install Terraform / tflint or narrow the hook in **`.pre-commit-config.yaml`**. |
| **`pre-commit` not found** | Run **`uv sync`** and use **`uv run pre-commit …`**. |
| **Stale `node_modules/` after pulling** | Older clones may still have **`node_modules/`** from when the repo used npm. It is **gitignored** and unused — delete with **`rm -rf node_modules`**. |

---

## Dependencies

- **Python:** **`pyproject.toml`** / **`uv.lock`**
