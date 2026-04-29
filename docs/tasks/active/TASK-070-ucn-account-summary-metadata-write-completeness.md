# TASK-070 — UCN: Account Summary + Account Metadata write completeness (`_TEST_CUSTOMER` v1)

**Status:** [x] complete (functional `_TEST_CUSTOMER` v1 write-proof executed 2026-04-24)  
**Opened:** 2026-04-24  
**Updated:** 2026-04-24 — v1_full proof: prep-v1 → extract (6 call records, lint clean) → UCN write (`write_doc` 21 applied) → `read_doc` → ledger row; doc id `15CD2Sq5avXiz6D_Jq19DG-7DfVhoXyNMsPmAJ7E6Qok`.

**Depends on:** **TASK-069** (tester/diff rules — can proceed in parallel); overlaps **TASK-053** (GDoc gaps TOC); **TASK-057** (contacts tuning); **TASK-059** (Account Metadata tuning); **TASK-062** (cross-artifact consistency)

## Process (read first)

- **This task file** is the place to review goals, scope, and **where** design rules should live.  
- **Do not** change **`.cursor/rules/*`**, **`docs/ai/gdoc-customer-notes/*`**, or playbooks for this work **without explicit user approval** after the task is reviewed. (Earlier draft edits to `core` / hub README / `11` / `mutations-global` / index references were **reverted**; they are **not** in the tree from that thread.)

## Architecture: where mutation *requirements* should live (design)

**Problem:** Tuning one category (e.g. Cloud Environment) in **four** places (playbook + two rules + tab doc) **guarantees drift**.

**Rule of thumb:** **section semantics = one file per tab** under `docs/ai/gdoc-customer-notes/` in the existing **`mutations-*-tab.md`** files. Playbooks and Cursor rules should **orchestrate** and **link**, not **restate** full section rubrics.

| If you are changing… | **Authoritative file (intended edit target)** | Other files |
| --- | --- | --- |
| What Account Summary sections mean, Cloud `tools_list` routing, Contacts evidence, etc. | `mutations-account-summary-tab.md` | Playbook: **step + link**. Rules: **invariants + link**. Code: **shape validation** + optional comment link. |
| Account Metadata field strictness / numerics | `mutations-account-metadata-tab.md` | Same |
| Global actions, JSON shape, cross-tab mechanics | `mutations-global.md` | Not a second home for *per-section* rubrics (mechanics only). |
| UCN / extract *process* (when, artifacts, approval) | `update-customer-notes.md` | **No** second full rubric table; cite tab doc §. |
| Agent posture | `21-extractor.mdc`, `20-orchestrator.mdc` | **Pointers**, not a parallel section spec. |

**Hub:** `docs/ai/gdoc-customer-notes/README.md` already has a **Layer** table (Shape / Meaning / Process). **Optional (pending approval):** add a short **“SSoT: section semantics”** subsection in that README with a roles table, so **all** implementers and agents have a single **docs** link for “where to edit” — **not** a new top-level file unless you decide otherwise.

### Recommendation: `core.mdc` vs inlining UCN design rules

| Approach | When to use |
| --- | --- |
| **Add a 1–2 sentence pointer in `core.mdc`** to `docs/ai/gdoc-customer-notes/README.md` (and, once it exists, the SSoT subsection anchor) | **Default.** Keeps **always-on** rules **lite**; UCN “what to write” stays in **docs**, versioned and reviewable like the rest of the mutation pack. |
| **Paste UCN / mutation design into `core.mdc`** | **Avoid.** Duplicates the tab docs, goes stale, and bloats every session. |
| **Only README + tab docs, no `core` change** | Viable if you accept that agents who never open the hub only see it when they `read` docs or the task tells them to. |

**Conclusion to approve:** **Link in `core`**, not full rules. Full rules stay in **`mutations-*-tab.md`** and (if added) **README § SSoT**.

### UCN design: files / dirs, roles, and how sessions see it (agreed model)

**Store UCN *design* by concern — do not paste the same section spec in four places.**

| Role | Path | What goes here |
| --- | --- | --- |
| **Per-tab meaning** (rubric, evidence, what to write, Cloud `tools_list` routing, metadata strictness) | `docs/ai/gdoc-customer-notes/mutations-*-tab.md` (Account Summary, Account Metadata, Daily Activity, …) | **The** file to change for “section semantics” for that Google Doc tab. |
| **Cross-tab mechanics** (actions matrix, JSON shape, quality gate, ledger) | `docs/ai/gdoc-customer-notes/mutations-global.md` | Mechanics only — not a second home for per-section rubrics. |
| **Hub / index** | `docs/ai/gdoc-customer-notes/README.md` | Shape vs meaning vs process; optional **§ SSoT: section semantics** (file-roles table) when approved. |
| **UCN *process*** (step order, artifacts, approval) | `docs/ai/playbooks/update-customer-notes.md` | *When* the run happens; may enumerate fields as **flow** — **link** to tab docs for prose, no duplicate full rubric. |
| **Agent posture** | `.cursor/rules/20-orchestrator.mdc`, `.cursor/rules/21-extractor.mdc` | Invariants + **pointers** to tab docs. |
| **Product / schema contract** | `docs/project_spec.md` | Product rules and schemas; not a substitute for `mutations-*-tab` wording. |
| **Shape in code** | `prestonotes_gdoc/config/doc-schema.yaml`, `prestonotes_gdoc/`, MCP | Keys and validation; optional **comment** links to tab SSoT. |

**Invariants:** (1) One **semantic** home per tab: **`mutations-*-tab.md`**. (2) Playbooks and rules **orchestrate** and **link**; they do not restate the same section prompt in full.

**How *all* sessions are nudged without bloating `core`:**

- **`core.mdc`** is **`alwaysApply: true`** — keep it **lite**: at most a **1–2 sentence** pointer to **`docs/ai/gdoc-customer-notes/README.md`** (and the **§ SSoT** anchor if present). That is the cheap always-on signpost.
- **Cursor does not** auto-embed the full hub, `project_spec`, or tab packs in every chat. The **authoritative** text is loaded when an agent or human **reads** those files, or when a **scoped** rule applies (e.g. UCN playbooks in context, task / `@` / glob-attached rules).
- **No** pasting the full UCN / mutation design into **`core`**.

### E2E trigger rule alignment — `.cursor/rules/11-e2e-test-customer-trigger.mdc` vs harness

**Problem:** A **`git checkout HEAD`** on **`11`** (during an unrelated revert) can leave **`.cursor/rules/11-e2e-test-customer-trigger.mdc`** pointing at **stale** wiring: e.g. **`e2e-test-customer.md`** / **10 steps** / **`reset` + Bootstrap** while the branch has moved to **`tester-e2e-ucn.md`**, **harness per `scripts/lib/e2e-catalog.txt`** (see **`list-steps`**), **`prep-v1` / `prep-v2`**, and the **TASK-069** quality pointer to **`.cursor/agents/tester.md` §6** (post-write diff, mandatory rows).

**Do this in TASK-070 (or a tight sub-PR) when touching E2E:**

| Fix | Detail |
| --- | --- |
| **Playbook path** | **`11`** “Follow … exactly” must reference **`docs/ai/playbooks/tester-e2e-ucn.md`** (and match the **current** filename on disk — not a retired path). |
| **Step count + shell/chat order** | Match **`tester-e2e-ucn.md`** and **`scripts/lib/e2e-catalog.txt`** (or `./scripts/e2e-test-customer.sh list-steps`); remove **10-step** / **`reset` + Bootstrap** language if the harness no longer uses it. |
| **TASK-069 pointer** | Restore a **short** canonical line in **`11`** (if desired for always-on E2E sessions): **tester.md §6** post-write diff; mandatory delta rows for Contacts, Challenge Tracker, Cloud Environment, Account Metadata on **`v1_full`** / **`full`**; planner **`KEY_FIELD_COVERAGE`** is not a substitute — **without** duplicating the full §6 template (pointer only). |

**Dependency:** Confirm **`scripts/e2e-test-customer.sh`** subcommands and step labels match **`tester-e2e-ucn.md`** before editing **`11`** numbering.

## Design principle (content)

**Do not** encode write completeness or E2E acceptance as “search for product names” (Okta, Jira, Azure, etc.). **Rubric + transcript evidence** — see **`mutations-account-summary-tab.md`** (Cloud / `tools_list` routing, no vendor catalog).

**TASK-070** (implementation work) should prove the write path on **`_TEST_CUSTOMER` v1** with **structural** checks — not vendor keyword lists.

## Problem

(unchanged) A **`v1_full`** UCN that only satisfies the **four-field planner coverage guard** + DAL can leave **Contacts**, **Challenge Tracker**, **Cloud Environment**, and **Account Metadata** thin or empty even when the corpus is rich. Root cause: **write-path** mutations, not the Google API. See the task one-liner in **INDEX** for the full account-summary intent.

## Goal

1. **Layering (documentation) — *after approval*:** One semantic home per tab; **deduplicate** playbook/rule prose into links where duplicates exist.  
2. **Account Summary + Metadata (functional):** For **`_TEST_CUSTOMER` v1**, populate (when evidence exists) contacts, **≥2** challenge rows when the corpus has multiple challenges, **Cloud Environment** with **≥3** distinct `field_key` tool groups **when the corpus supports that** (rubric, not keywords), and **≥3** metadata fields with explicit evidence.  
3. **Alignment:** Valid mutations per `mutations-global.md` + tab docs; `evidence_date` on mutating actions; `FORBIDDEN_EVIDENCE_TERMS` respected.

## Non-goals

- Curated product keyword lists.  
- New “requirements” file types without your approval — default is **extend the existing hub + tab files**.  
- Unapproved edits to `KEY_FIELD_COVERAGE` in Python unless a blocker is proven.

## Scope (pending approval — do not start until user signs off this list)

| Priority | Work |
| --- | --- |
| **1. Docs (optional hub §)** | Add **README § SSoT: section semantics** (or equivalent) + optional **one** cross-line in `mutations-global.md` top matter pointing at it — *only* if approved. **Optional** **one** short pointer in **`core.mdc`** to the hub (link only, no rubric tables), per table above. |
| **2. Deduplicate** | `update-customer-notes.md` and `20`/`21` rules: replace duplicate rubric blocks with links, *if* duplicates are found. |
| **3. E2E** | `_TEST_CUSTOMER` v1: `read_doc` meets functional acceptance; lint + ledger per harness. |
| **3b. `11` vs harness** | Align **`.cursor/rules/11-e2e-test-customer-trigger.mdc`** with **`tester-e2e-ucn.md`** + **catalog** (path, script names) and optional **TASK-069** — **`.cursor/agents/tester.md` §6** pointer; see subsection **E2E trigger rule alignment** above. |
| **4. Code** | Writer/MCP *only* if a **valid** mutation is blocked. |

## Acceptance

**Docs / architecture**

- [x] Added hub **SSoT: section semantics** table in `docs/ai/gdoc-customer-notes/README.md` as the long-form file-role reference.  
- [x] `core.mdc` remains a pointer for E2E flow pathing (no duplicated rubric tables).  
- [x] `11-e2e-test-customer-trigger.mdc` now uses pointer-style TASK-069 cross-reference for post-write diff requirements.

**Functional / E2E**

- [x] **`11` / harness:** **`11-e2e-test-customer-trigger.mdc`** now references **`tester-e2e-ucn.md`**, uses the **catalog + `list-steps`** contract, matches script ordering, and includes a TASK-069 pointer to **`tester.md` §6**.
- [x] `read_doc`: `contacts` ≥2 stakeholder lines with evidence traceability (John Doe, Jane Smith under `section_map.contacts.fields.free_text.entries`).  
- [x] `read_doc`: ≥2 Challenge rows when the corpus has ≥2 challenges; lifecycle-consistent (`challenge_tracker` rows match `challenge-lifecycle.json` `in_progress` → **In Progress** for `ch-soc-budget`, `ch-champion-exit`).  
- [x] Cloud: ≥3 `field_key` groups **when** corpus supports — `csp_regions`, `idp_sso`, `sizing` (update_in_place) plus `platforms`, `devops_vcs`, `ticketing` (tools_list); rubric-based, not vendor-keyword acceptance.  
- [x] Metadata: ≥3 fields with evidence — `exec_buyer`, `champion` (`explicit_statement` mutations), `sensor_coverage_pct` (90 from 900/1000), `critical_issues_open` (12 toxic combos).  
- [x] E2E run documented: **`v1_full`** (prep-v1, load context via `sync_notes` + `read_transcripts`, extract to `call-records/*.json`, lint → UCN → `read_doc` §6-style diff below).  
- [x] **TASK-069** on this run: mandatory sections scored in table below; planner-only four-field guard is not treated as full Account Summary completeness.  

## Verification

- [x] GDoc vs `read_doc` check: `read_doc` on doc id above after write; local mirror pushed with `./scripts/e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"`.  
- [x] `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` → **0** before UCN (corpus avg ≤1.5 KB after lean records).  
- [x] Ledger: `append_ledger_row` appended v3 row to `AI_Insights/_TEST_CUSTOMER-History-Ledger.md` (`run_date=2026-04-24`).  
- [x] `bash scripts/ci/check-repo-integrity.sh` passes (post task update).

## Notes

- **TASK-057/059, TASK-053** — same as before (merge or link when this closes).

---

**One-line summary for implementers (after approval):** UCN **design** lives in **`mutations-*-tab.md` + hub**; **`core`** = **one signpost** only; align **`11`** with **`tester-e2e-ucn.md`** + **TASK-069** pointer; then **`_TEST_CUSTOMER` v1** proves Account Summary + Metadata writes + TASK-069 diff.
