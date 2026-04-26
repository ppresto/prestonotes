# TASK-074 — UCN: Accomplishments (vendor wins) and Upsell Path (Wiz SKU, security gaps, local license cache)

**Status:** [ ] not started — design only (build deferred)  
**Opened:** 2026-04-26  
**Updated:** 2026-04-26 — snapshot persistence spec in §G8 (no repo script until build); removed experimental `save_wiz_remote_kb_snapshot.py`

**Depends on / relates to:** **TASK-070** (Account Summary completeness); **TASK-053** (GDoc quality TOC); **TASK-073** (planner coverage — align Upsell/Accomplishments with matrix when present); E2E **`v1_full`** post-write diff (Accomplishments empty + accomplishment-like text under **Workflows** — writer/parser/placement). **Domain advisors:** `.cursor/rules/23`–`27` (invoke when reasoning about org / SOC / AppSec / AI).

## Problem

1. **Accomplishments — competitive / vendor decommission**  
   Decommissioning another vendor’s product (e.g. Prisma) is a **substantive account win** for a Wiz SE: it shows adoption, trust, and displacement. That narrative must land under **Accomplishments**, not be dropped or mis-filed under **Workflows**. Current pipeline behavior (E2E) suggests **section placement / parsing** may not match the mutation intent.

2. **Upsell Path — depth and grounding**  
   The **Upsell Path** should read as **consultative**: which **Wiz SKU** (and included capabilities) addresses which **real gap** in the customer’s **current** security stack, goals, challenges, risk, or compliance/audit context. The section is not a generic product list. Good output requires:
   - **Product / commercial truth:** **Wiz Cloud** SKU scope: which **included** capabilities can **add workloads (license units)** vs **core** entitlements that do not increase workload count (e.g. user’s distinction: **DSPM** and **ASM** as Cloud-SKU capabilities that can drive workload growth; **CIEM** as part of Cloud but **not** a workload expander in the same way). **Defend**, **Code**, and **Sensor** have **separate** consumption / licensing models from Cloud as a line.
   - **Customer truth:** A **gap** to fill (new goal, open challenge, risk, compliance/audit driver, etc.) plus **how the team works** — e.g. **SOC|IR**, **Cloud|Vuln**, **Product|AppSec** — and **architecture / workflows** (AI is a major cross-cutting driver of new exposure and upsell).  
   - **Resilience:** When **wiz-remote** (or other MCP) is down, the agent should still have **local, versioned** reference material for SKU and capability boundaries so UCN is not blind.

3. **Discovery when evidence is thin**  
   If corpus + call-records do not support a confident upsell line, the run should still be valuable by surfacing **targeted discovery questions** (for a follow-on task: see **Sequencing**).

## Goals

- **G1 — Accomplishments:** Update **`mutations-account-summary-tab.md`** (and UCN **Step 6/8** pointers in **`update-customer-notes.md`**) so **vendor / competitive decommission** and similar wins are **explicitly in scope** for **Accomplishments**, with **writer / `prestonotes_gdoc`** fixes if `read_doc` `section_map` shows mis-routing. Add a **non-regression** check (unit or golden) if the fix is in code. **E2E `v1_full`** re-run should show Prisma-style content under **Accomplishments** (or documented `skip` + reason if truly no evidence — not silent wrong tab).

- **G2 — Upsell Path rubric:** Extend the **Account Summary** / **Upsell** guidance so each upsell bullet (or small cluster) ties **(a)** a **customer gap** (goal, challenge, risk, audit, **AI** exposure) → **(b)** the **Wiz offer** (SKU / module) that fits → **(c)** **why workload / commercial motion** when relevant (license units vs core), without inventing numbers. Cite **security-team lenses** and **AI** as first-class context where transcripts support it.

- **G3 — Local Wiz license / SKU knowledge as a UCN init prereq:** Use the **wiz-remote** MCP `wiz_docs_knowledge_base` tool to retrieve license / SKU / capability text for the offers in scope, then persist each response as plain markdown under **`docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/<slug>.md`** (see **§G8** for file shape and how to build the `.md` from the tool’s JSON). **No Chroma / local vector DB required** — and **no helper script in-repo until build** (persistence is manual or a small script added in the same change set as the playbook/UCN wiring).

  - **When it runs:** as an **init prereq for UCN** whenever **Upsell Path** (or other commercial wording) is in scope — **before** the heavy transcript / call-record reading pass, so the agent has product truth in context first. **It is not a substitute for `read_doc`**, which still leads.
  - **Where it lives — open decision (resolve at build):**
    1. **Option A:** new short, focused playbook (e.g. **`docs/ai/playbooks/refresh-wiz-license-snapshots.md`**) explicitly chained from UCN init.
    2. **Option B:** add an **`upsell-only`** profile to **`docs/ai/playbooks/load-product-intelligence.md`** that loads only `mcp_query_snapshots/*.md` (and the §G4 references), skipping the full `wiz_mcp_server/docs` / `mcp_materializations` corpus.
    3. **Option C:** chain it directly inside **`update-customer-notes.md`** “Before You Start” checks (Check 4 today gates on `Product-Intelligence.md`; this would gate on snapshot freshness for the SKUs in play).
    Whichever option is chosen, **agents must read only the snapshot files matching the deal context** (e.g. Cloud + DSPM + AI), not every snapshot every time, and **do not** load the full `Load Product Intelligence` corpus on this path.
  - **Refresh policy:** re-run **`wiz_docs_knowledge_base`** and re-materialize the snapshot file(s) when frontmatter `saved_at` is older than **7 days** **or** an upsell line will name a SKU not yet covered locally. Outdated snapshots are flagged, not silently used.
  - **Offline / MCP unavailable:** if `wiz_docs_knowledge_base` is down, UCN proceeds with whatever `mcp_query_snapshots/*.md` are on disk and **explicitly notes** the staleness in the run output instead of fabricating.
  - **Reuse:** align with existing **`run-license-evidence-check`** / **`wiz-mcp-tools-inventory`** language; do not duplicate full SKU prose into this task — let the snapshot files be the source.

- **G3.a — Seed query list (canonical until build moves it):** the targeted set of `wiz_docs_knowledge_base` queries the prereq seeds and refreshes. Keep small; extend only when a real deal needs it.
  - `Wiz Cloud license and workload units`
  - `Wiz Defend license ingestion pricing`
  - `Wiz Code license and consumption`
  - `Wiz Sensor license deployment`
  - `Wiz CIEM and cloud security platform`
  - `Wiz DSPM data security posture management licensing`
  - `Wiz ASM attack surface management licensing`
  - `license comparison cloud Wiz` (matches **docs.wiz.io** “license comparison” tutorial titles)

- **G4 — Curated external references for gap framing:** small, vendor-neutral set used to **reason about gaps** (SOC, cloud, AppSec, GRC, AI) and shape **Upsell** narrative + discovery questions. **Not** customer-facing copy; do **not** paste passages into Google Doc text. On build, link this table from **`mutations-account-summary-tab.md`** Upsell section. Pair with PrestoNotes domain advisors **`.cursor/rules/23-domain-advisor-soc.mdc`**, **`24-domain-advisor-app.mdc`**, **`25-domain-advisor-vuln.mdc`**, **`26-domain-advisor-asm.mdc`**, **`27-domain-advisor-ai.mdc`**.

  | Area | URL | Why open it |
  | --- | --- | --- |
  | Enterprise security lifecycle (functions) | https://www.nist.gov/cyberframework | **NIST CSF 2.0** (Govern, Identify, Protect, Detect, Respond, Recover) — map customer programs and gaps to these outcomes. |
  | CSF 2.0 publication | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf | Single PDF with the full core vocabulary. |
  | AI risk (cross-sector) | https://www.nist.gov/itl/ai-risk-management-framework | **NIST AI RMF 1.0** (GOVERN / MAP / MEASURE / MANAGE). |
  | Generative AI profile (EO 14110 alignment) | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | NIST GenAI companion profile for AI-specific risk framing. |
  | AppSec / SDLC program (product + engineering) | https://owaspsamm.org/model/ | **OWASP SAMM** — software assurance practices and maturity (strategy, construction, verification, operations). |
  | LLM / GenAI app risks | https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025 | **OWASP Top 10 for LLM Applications 2025** — gap vocabulary for AI upsell and discovery questions. |

- **G5 — Discovery questions (optional in this task; full library in TASK-075):** When **required** evidence for a strong Upsell line is missing, the UCN **output** (or a sidecar under **AI_Insights** if standardized) may include **3–7 concrete discovery questions** for the next live call. Deeper **templates and scenarios** live in **[TASK-075](TASK-075-ucn-upsell-path-discovery-questions.md)**.

- **G6 — Explicit UCN context read order (target; wire into `update-customer-notes.md` at build):** This path is **not** “full **Load Product Intelligence**.” When Upsell / commercial accuracy is in scope, target order is:
  1. **`read_doc`** (GDoc is still source of truth for the account).
  2. **Relevant** `mcp_query_snapshots/*.md` for the deal (from **G3** + **G3.a**) and **reasoning** from the **§G4** table (open links as needed; do not paste long quotes into the customer doc).
  3. **Then** the normal UCN bundle: in-window **transcripts**, **call-records**, **Notes.md** mirror, **AI_Insights** artifacts, **History Ledger** / audit — per **`update-customer-notes.md`**.
  4. Invoke **domain advisors** (`.cursor/rules/23`–`27`) when mapping customer gaps to **SOC|IR**, **Cloud|Vuln**, **AppSec|Product**, **AI** — in addition to §G4 links.

- **G7 — Out of scope for this UCN “Upsell product path” (do not load on every UCN run):** Full recursive read of `docs/ai/cache/wiz_mcp_server/docs/`, a full **Load Product Intelligence** sweep, **`MyNotes/Internal/AI_Insights/Product-Intelligence.md` synthesis** as a blocking gate, or **`wiz_knowledge_search`** (local Chroma). The **Check 4** / Product-Intelligence age rule in the playbook can stay for **broad** runs; this task’s path uses **G3 + §G4** as the **minimal** commercial + gap-framing bundle.

- **G8 — Wiz-remote snapshot → on-disk markdown (persistence spec; implement at build):** After `wiz_docs_knowledge_base` returns a JSON body in Cursor (typical top-level key **`results`**: list of objects with **`Content`**, **`Title`**, **`Href`**, **`Score`**) the operator or automation must write one file per **seed query** (see **G3.a**), not a dump of the entire hosted KB.
  - **Path:** `docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/<slug>.md` where **slug** = lowercased query with non-alphanumeric characters collapsed to **`-`**, max ~120 chars (human-readable, stable in git).
  - **Frontmatter (YAML) minimum:** `query` (string), `saved_at` (ISO date), `source_tool` (e.g. `wiz_docs_knowledge_base`), `result_count` (int).
  - **Body:** For each result, include **title**, **source URL** (`Href`), **score** if present, and the **raw chunk text** (`Content`) in a fenced code block (plain text) so the file stays diff-friendly.
  - **Build deliverable (optional in same PR):** a small **`uv run python scripts/...py`** (name TBD) that reads stdin or `--json-file` and writes the above, plus **`pytest`** for happy-path and empty-`results` — **deferred** until implementation; this task is design-only and does not require the script to land before the playbook changes.
  - **Until then:** an agent can create/update the `.md` by hand in-editor from the tool output so UCN can still be tested.

## Non-goals

- Replacing **wiz-remote** for interactive search when available; local cache is a **fallback + speed** layer, not a second product database.
- **Guaranteed** commercial accuracy on every price/SKU edge case — **flag uncertainty** and use discovery questions instead of fabricating.
- **Runtime** `if _TEST_CUSTOMER` hacks; fixture may **illustrate** acceptance only.

## Scope (files — expect to touch; exact list after design)

- `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` (Accomplishments + **Upsell Path**)
- `docs/ai/playbooks/update-customer-notes.md` (step pointers; no duplicate full rubric)
- `prestonotes_gdoc/` only if **G1** requires parser / section mapping fixes
- External + SKU reasoning: **§G4 in this task** (and tab-doc link) — not a new standalone reference file until build.
- **`mcp_query_snapshots/`** — **gitignored or committed** (operator choice); output-only, no `README` in the cache root required.
- **Build:** optional helper script + tests as described in **§G8**; optional thin playbook or **`load-product-intelligence.md`** `upsell-only` profile — see **G3** options.
- **`.cursor/rules/21-extractor.mdc`**: short pointer if extraction posture for Upsell/Accomplishments changes

## Acceptance

- [ ] **A1** — Tab doc and playbook state clearly that **decommissioning or displacing a non-Wiz security product** is a **first-class Accomplishment** when evidenced; **E2E** or **manual** UCN on `_TEST_CUSTOMER` shows correct **section** in `read_doc` (or an explicit, allowed skip).
- [ ] **A2** — **Upsell Path** guidance includes: **Wiz Cloud** vs **Defend / Code / Sensor** licensing **concepts**; **workload-driving** vs **core** capabilities (with **user-vetted** examples like DSPM/ASM vs CIEM); and **gap → SKU → business language** mapping tied to **goals, challenges, risk, compliance, AI**.
- [ ] **A3** — **Local license / product snapshot** path and refresh policy documented in **this task (§G3)**; refresh procedure + what to do when **MCP unavailable**; no silent stub content in customer artifacts.
- [ ] **A4** — **External references (§G4 table)** is linked from **`mutations-account-summary-tab.md`** Upsell section at build; **no separate** `ucn-upsell-context-refs` file required — **§G4** in **TASK-074** is the SSoT until optional split at build.
- [ ] **A5** — At least one of: **(i)** discovery-question pattern in this task’s deliverables, or **(ii)** explicit handoff to **TASK-075** with clear scope (see **[TASK-075](TASK-075-ucn-upsell-path-discovery-questions.md)**).
- [ ] **A6** — **Verification** below passes.

## Verification

- `bash .cursor/skills/lint.sh` and `bash .cursor/skills/test.sh` after code/doc changes.
- `bash scripts/ci/check-repo-integrity.sh` if paths / manifests / rules lists change.
- Re-run **E2E `v1_full`** (or **manual** UCN on `_TEST_CUSTOMER` with same corpus) and confirm **tester.md §6** row for **Accomplishments** is no longer a false **H** for the Prisma-style case; **Upsell** rows show defensible **H/M/L** with documented gaps only where corpus is thin.
- `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` remains **0** when extract is in the loop.

## Sequencing

- Land **G1** early if it is a **writer bug** blocking honest E2E scoring.
- **G3** can parallel **G2/G4** once the local path shape is agreed.
- **Follow-on — TASK-075:** **Discovery question library** for Upsell Path (AI, org model, gaps) — **[`TASK-075-ucn-upsell-path-discovery-questions.md`](TASK-075-ucn-upsell-path-discovery-questions.md)** (stub; expand after **G2/G3** land here).

## Notes (product direction — from task author)

- **Wiz Cloud SKU** maps to multiple capabilities; some **increase** licensed **workloads**; **CIEM** may be **in** Cloud but framed as **core** value, not volume, depending on deal — document **nuance** from official Wiz material ingested into the local cache, not only from this task text.
- **AI** is a primary **macro** driver of new security gaps; Upsell should **connect** to it when transcripts or strategy discussions do.
- The most valuable agent behavior when data is missing: **well-formed discovery questions** for the next customer conversation.
