# Plan: UCN preflight (required) vs writer dry-run (E2E-only)

**Status:** Implemented in repo (docs + rules sprawl cleanup; see git history).

---

## Why the first cut felt like sprawl

UCN is **one** user-facing playbook ([`docs/ai/playbooks/update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md)), but the repo also carries **parallel entry points** that restate parts of the same flow:

- **Cursor rules** ([`10-task-router.mdc`](.cursor/rules/10-task-router.mdc), [`20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc), [`core.mdc`](.cursor/rules/core.mdc)) — routing, approval gates, mutation hygiene.
- **Package READMEs** ([`prestonotes_gdoc/README.md`](prestonotes_gdoc/README.md), [`scripts/README.md`](scripts/README.md)) — “how to run the writer from the shell.”
- **E2E** ([`tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md), [`11-e2e-test-customer-trigger.mdc`](.cursor/rules/11-e2e-test-customer-trigger.mdc), [`tester.md`](.cursor/agents/tester.md), [`e2e-catalog.txt`](scripts/lib/e2e-catalog.txt)) — harness steps and tester contract.

**Copying the same preflight / dry-run policy into many of those** duplicates the “one playbook” story and makes updates painful (forgotten file, inconsistent wording). That is **real sprawl** — not the number of *references*, but the number of *authoritative copies*.

**E2E vs UCN:** The E2E doc is a **procedure** for `_TEST_CUSTOMER` (prep shell + UCN + diff). It should **not** re‑own general UCN policy; it should **point** at the UCN playbook for “how to UCN” and add only what is **specific to the harness** (e.g. approval bypass, **required** writer dry-run before each real write in test only).

---

## Refined policy (anti-sprawl)

| Topic | Where it is documented (single place) | Everywhere else |
|--------|----------------------------------------|-----------------|
| **Planner preflight required before `write_doc` / real `write`** | **[`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md)** — one clear subsection (e.g. Step 10 or the existing TASK-072 block). That is the **SSoT** for “anything running UCN.” | **Links only** (one sentence): e.g. `20-orchestrator.mdc` “Execute” can say “Run preflight per `update-customer-notes.md` before `write_doc`.” **No** second full paragraph in `core.mdc`, `prestonotes_gdoc/README`, `scripts/README`, or `gdoc-section-changes-v2` unless a single cross-link is needed for discoverability. |
| **Writer `dry_run` as a required E2E-only step** | **[`tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md)** only — under the UCN steps (3 and 5). | **`11-e2e` / `tester.md` / `e2e-catalog`:** at most **one** pointer: “E2E required writer dry-run: see `tester-e2e-ucn.md`.” **Do not** document production write order in E2E-only files as a second SSoT; that stays in the UCN playbook. |

**Optional follow-up (later):** hard gate in code or CI — out of scope for this doc pass unless you ask for it.

---

## Files to touch when implementing (minimal set)

**Must edit (content):**

1. [`docs/ai/playbooks/update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) — add or tighten the **required preflight before write** language in the existing TASK-072 / Step 10 path (one subsection, not scattered).

2. [`docs/ai/playbooks/tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md) — **`_TEST_CUSTOMER` harness:** required `update-gdoc-customer-notes.py write --dry-run` (or MCP `write_doc` `dry_run=true`) **after** preflight and **before** each real write; link to the UCN playbook for preflight rules.

**Optional (one line each, link-only):**

3. [`docs/ai/playbooks/update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) — ensure the intro or “Before you start” has a one-line “SSoT for UCN write validation” if helpful.

4. [`.cursor/rules/20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc) — in **Execute**, one sentence: preflight per `update-customer-notes.md` before `write_doc` (no duplicate of TASK-072 details).

5. [`.cursor/agents/tester.md`](.cursor/agents/tester.md) — replace any future long block with: E2E validation details → `tester-e2e-ucn.md`.

---

## Current sprawl — files that confuse the workflow (cleanup pass)

These entries are **not** a second SSoT; they **overlap** the UCN playbook or mix in **unrelated** `dry_run` (vector index, rsync, bootstrap). The cleanup is: **remove or shorten** the UCN policy duplicate, and only add a **link** where the reader’s job actually needs it.

| File | What’s wrong today | Proposed action |
|------|---------------------|-----------------|
| [`prestonotes_gdoc/README.md`](prestonotes_gdoc/README.md) | Full TASK-072 + “dry-run then apply” for UCN | **Remove** the long UCN block. Replace with 2–4 lines: “UCN mutations, preflight, and write order: **SSoT = [`update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md)**.” Keep **technical** `uv run … write` flags for people who already have a file path. |
| [`scripts/README.md`](scripts/README.md) | Long `ucn-planner-preflight.py` bullet (TASK-072/073 restated) | **Replace** with: script one-liner + “**When to run / contract:** see [`update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md).” |
| [`.cursor/rules/core.mdc`](.cursor/rules/core.mdc) | “`dry_run` first when available” for **all** `write_doc` | **Narrow:** Customer Notes UCN → follow [`update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md) (preflight + write). Other `write_doc` contexts (rare) keep **approval** language without implying every run uses writer dry-run. |
| [`.cursor/rules/20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc) | Block B: “`write_doc` `dry_run=true` preview when available” | **Replace** with: before real write, run **`ucn-planner-preflight`** per UCN playbook; **writer** dry-run **required** before each real write **only** for `_TEST_CUSTOMER` E2E per [`tester-e2e-ucn.md`](../docs/ai/playbooks/tester-e2e-ucn.md). |
| [`docs/ai/references/gdoc-section-changes-v2.md`](docs/ai/references/gdoc-section-changes-v2.md) | “`write_doc` with `dry_run=true` before applying” reads like global UCN policy | **Reword** for **template/section edit** smoke tests only, **or** one line: UCN product flow → UCN playbook. **Do not** make this the third copy of TASK-072. |
| [`docs/project_spec.md`](docs/project_spec.md) | `write_doc` / `dry_run` “when appropriate” (vague) | **Optional** one line: for **UCN**, see [`update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md). **Not** a full preflight re-explanation. |
| [`docs/ai/playbooks/update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) | v2 blurb + Step 10 still say `dry_run=true` for every Cursor `write_doc` | **Edit in place** (SSoT): preflight required; **writer** `dry_run` **E2E-only**, **required** before each real write for `_TEST_CUSTOMER` harness. |
| [`docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md`](docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md) | TASK-072 deal-stage / preflight snippet | **Keep** tab-specific rules; add **one** line: full matrix + command → [`update-customer-notes.md`](../docs/ai/playbooks/update-customer-notes.md). |
| [`docs/ai/gdoc-customer-notes/mutations-daily-activity-tab.md`](docs/ai/gdoc-customer-notes/mutations-daily-activity-tab.md) | DAL + `ucn-planner-preflight` | **Keep** DAL focus; add/keep pointer to UCN playbook for the **whole** bundle. |
| [`.cursor/rules/21-extractor.mdc`](.cursor/rules/21-extractor.mdc) | “extractor-side preflight” (challenge rows) | **Clarify** (optional): not the same as `ucn-planner-preflight.py` — avoid one word “preflight” meaning two things without context. |
| Unrelated | `README` wiz/vector `dry-run`, `rsync --dry-run`, `bootstrap` `dry_run`, `daily-activity-ai-prepend` tool | **No** UCN/E2E playbook link — different features. |

---

## When another file should link to UCN vs E2E vs neither

| Reader need | Link to | Notes |
|-------------|---------|--------|
| Running **Update Customer Notes** (any customer) | [`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) | **Single** product SSoT for preflight, mutations, Step 10. |
| Running the **`_TEST_CUSTOMER` E2E harness** (prep + UCN + diff) | [`tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md) | E2E-only: shell steps, approval bypass, **required** **writer** dry-run before each real write. **Also** link UCN for “how to UCN” content. |
| **Routing** (task router, orchestrator) | Short pointer to **UCN** playbook; E2E pointer **only** if the rule is about the reserved E2E trigger. | Rules stay **short**; no copy-paste of TASK-072. |
| **Package / script index README** | “See UCN playbook” for *policy*; keep **command names** local. | Developers grep scripts; they should not get a second full contract here. |
| **Tab packs** (`mutations-*-tab.md`) | Pointer to UCN for **global** preflight + full matrix; tab file keeps **section-specific** rules. | Avoid deleting tab nuance; avoid duplicating the full matrix. |
| **Template / schema** (`gdoc-section-changes-v2`, `project_spec` § tool) | **Optional** UCN link only where it prevents mistaking “template dry-run” for “UCN preflight.” | Many editors never run E2E; they may only need “dry-run writer when changing template.” |
| **Wiz cache, Granola, bootstrap, vector index** | **Neither** UCN nor E2E | Different workflows; links would add noise. |

**Principle:** Link when the file’s **audience** might do UCN or E2E next. **Do not** add links in every `*.md` that happens to mention `write_doc` — that recreates sprawl with URL soup.

---

## Open questions (narrowed)

- **Resolved:** E2E writer dry-run is **required** before each real write in the default harness (`tester-e2e-ucn.md`); **not** production.

---

## Checklist (implementation)

- [x] UCN playbook: preflight required; link to `scripts/ucn-planner-preflight.py` and exit / `ok` behavior (reuse existing blocks where possible).
- [x] E2E playbook: required writer dry-run (E2E only); link to UCN for preflight.
- [x] **Sprawl cleanup (see table):** `prestonotes_gdoc/README`, `scripts/README`, `core.mdc`, `20-orchestrator` Block B, `gdoc-section-changes-v2`, `project_spec` (optional), tab packs + `21-extractor` as listed — **remove** duplicate SSoT text, **add** one-line UCN (or UCN+E2E) pointers only per “when to link” above.
- [x] At most: orchestrator + tester one-liner pointers; no 10-file blast of **repeated** policy paragraphs.
