# TASK-074 — UCN: Accomplishments (vendor wins) and Upsell Path (Wiz SKU, security gaps, local license cache)

**Status:** [x] in progress — doc guidance + writer routing/tests landed; E2E/manual proof pending  
**Opened:** 2026-04-26  
**Updated:** 2026-04-27 — G3 location decision locked to Product Intelligence playbook; TASK-075 handoff upgraded; writer routing guardrail/tests passed

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

- **G3 — Local Wiz license / SKU knowledge as a UCN init prereq:** Use the **wiz-remote** MCP `wiz_docs_knowledge_base` tool to retrieve license / SKU / capability text for the offers in scope, then persist each response as envelope JSON under **`docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/<category>/`** (see **§G8** for path shape). **No Chroma / local vector DB required**. Reuse existing playbooks first; add scripts only when automation materially reduces manual drift.

  - **When it runs:** as an **init prereq for UCN** whenever **Upsell Path** (or other commercial wording) is in scope — **before** the heavy transcript / call-record reading pass, so the agent has product truth in context first. **It is not a substitute for `read_doc`**, which still leads.
  - **Where it lives — decision locked:** implement this in **`docs/ai/playbooks/load-product-intelligence.md`** as the canonical prereq path (with `update-customer-notes.md` pointing to it). Do **not** create a separate playbook unless a later task shows the existing playbook cannot express the flow cleanly.
  - **Read-scope discipline:** agents must read only the snapshot files matching the deal context (e.g. Cloud + DSPM + AI), not every snapshot every time, and must not load the full product corpus on this path.
  - **Refresh policy:** re-run **`wiz_docs_knowledge_base`** and re-materialize the snapshot file(s) when frontmatter `saved_at` is older than **7 days** **or** an upsell line will name a SKU not yet covered locally. Outdated snapshots are flagged, not silently used.
  - **Offline / MCP unavailable:** if `wiz_docs_knowledge_base` is down, UCN proceeds with whatever `mcp_query_snapshots/**/*.json` are on disk and **explicitly notes** the staleness in the run output instead of fabricating.
  - **Reuse:** align with existing **`run-license-evidence-check`** / **`wiz-mcp-tools-inventory`** language; do not duplicate full SKU prose into this task — let the snapshot files be the source.

- **G3.a — Seed query list (SSoT moved):** canonical seed configuration lives in **`docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml`** (`initial_query`, **`results`** = top-K rows per seed, default **1**; **one shot + top-K**, not a depth drill). This task keeps policy + acceptance; do not duplicate the full seed list here.

- **G4 — Curated external references for gap framing:** small, vendor-neutral set used to **reason about gaps** (SOC, cloud, AppSec, GRC, AI) and shape **Upsell** narrative + discovery questions. **Not** customer-facing copy; do **not** paste passages into Google Doc text. On build, link this table from **`mutations-account-summary-tab.md`** Upsell section. Pair with PrestoNotes domain advisors **`.cursor/rules/23-domain-advisor-soc.mdc`**, **`24-domain-advisor-app.mdc`**, **`25-domain-advisor-vuln.mdc`**, **`26-domain-advisor-asm.mdc`**, **`27-domain-advisor-ai.mdc`**.

  | Area | URL | Why open it |
  | --- | --- | --- |
  | Enterprise security lifecycle (functions) | https://www.nist.gov/cyberframework | **NIST CSF 2.0** (Govern, Identify, Protect, Detect, Respond, Recover) — map customer programs and gaps to these outcomes. |
  | CSF 2.0 publication | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf | Single PDF with the full core vocabulary. |
  | AI risk (cross-sector) | https://www.nist.gov/itl/ai-risk-management-framework | **NIST AI RMF 1.0** (GOVERN / MAP / MEASURE / MANAGE). |
  | Generative AI profile (EO 14110 alignment) | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | NIST GenAI companion profile for AI-specific risk framing. |
  | AppSec / SDLC program (product + engineering) | https://owaspsamm.org/model/ | **OWASP SAMM** — software assurance practices and maturity (strategy, construction, verification, operations). |
  | LLM / GenAI app risks | https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025 | **OWASP Top 10 for LLM Applications 2025** — gap vocabulary for AI upsell and discovery questions. |

- **G5 — Discovery questions and post-mutation enrichment handoff (TASK-075):** When **required** evidence for a strong Upsell line is missing, the UCN **output** (or a sidecar under **AI_Insights** if standardized) may include **3–7 concrete discovery questions** for the next live call. After TASK-074 baseline wiring lands, run the detailed follow-up in **[TASK-075](TASK-075-ucn-upsell-path-discovery-questions.md)**: (1) create initial `mutation.json`, (2) mine transcripts/notes for security themes, (3) generate and prioritize ad hoc Wiz query terms, (4) run targeted `wiz_docs_knowledge_base` fetches, and (5) perform one final mutation re-review with **in-place update + pre/post audit artifact**.

- **G6 — Explicit UCN context read order (target; wire into `update-customer-notes.md` at build):** This path is **not** “full **Load Product Intelligence**.” When Upsell / commercial accuracy is in scope, target order is:
  1. **`read_doc`** (GDoc is still source of truth for the account).
  2. **Relevant** `mcp_query_snapshots/<category>/*.json` for the deal (from **G3** + `kb_seed_queries.yaml`) and **reasoning** from the **§G4** table (open links as needed; do not paste long quotes into the customer doc).
  3. **Then** the normal UCN bundle: in-window **transcripts**, **call-records**, **Notes.md** mirror, **AI_Insights** artifacts, **History Ledger** / audit — per **`update-customer-notes.md`**.
  4. Invoke **domain advisors** (`.cursor/rules/23`–`27`) when mapping customer gaps to **SOC|IR**, **Cloud|Vuln**, **AppSec|Product**, **AI** — in addition to §G4 links.

- **G7 — Out of scope for this UCN “Upsell product path” (do not load on every UCN run):** Full recursive read of `docs/ai/cache/wiz_mcp_server/docs/`, a full **Load Product Intelligence** sweep, **`MyNotes/Internal/AI_Insights/Product-Intelligence.md` synthesis** as a blocking gate, or **`wiz_knowledge_search`** (local Chroma). The **Check 4** / Product-Intelligence age rule in the playbook can stay for **broad** runs; this task’s path uses **G3 + §G4** as the **minimal** commercial + gap-framing bundle.

- **G9 — Load Product Intelligence must materialize TASK-074 caches (not UCN-only):** When an operator runs **`Load Product Intelligence`** in a mode that performs **remote refresh / delta hydration** (see **`docs/ai/playbooks/load-product-intelligence.md`** §2.51 refresh path and §2.59), the run **must**:
  1. **External / architecture-aligned gap framing:** For each URL in **§G4**, ensure it is represented in the external cache model (indexes under `./docs/ai/cache/wiz_mcp_server/ext/indexes/` and, when content is **missing** or classified **stale/missing** per §2.7–§2.8, hydrate into `./docs/ai/cache/wiz_mcp_server/ext/pages/` using the same **delta** rules as other Tier A external refs — **do not** assume §G4 links are “browser-only”; they are first-class inputs for gap vocabulary during LPI synthesis and downstream UCN reasoning.
  2. **Hosted docs KB (`wiz_docs_knowledge_base`):** Execute **wiz-remote** `wiz_docs_knowledge_base` using seeds from `kb_seed_queries.yaml`; refresh only per-file stale/missing snapshots (`saved_at` > 7d or missing), then write/overwrite under **`mcp_query_snapshots/<category>/`** per **§G8**.
  - **Read-only LPI** (context load without refresh) still **reads** existing snapshot and ext page files if present; it does not substitute for refresh when the operator expects cache repair.
- **G9.a — Single source of truth for seed query strings:** `docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml` is canonical (`initial_query`, **`results`**). `update-customer-notes.md` Check 4 and LPI refresh path should reference it directly.

- **G8 — Wiz-remote snapshot -> on-disk JSON (persistence spec):** After `wiz_docs_knowledge_base` returns JSON (`results` with `Content`, `Title`, `Href`, `Score`), write **one** envelope JSON per seed (one MCP call; keep top **`results`** rows by `Score`).
  - **Path root:** `docs/ai/cache/wiz_mcp_server/mcp_query_snapshots/<category>/` — **category** = slug of the first ` - `-delimited segment of `initial_query` (e.g. `licensing`).
  - **File naming:** `slugify(remainder of query after first segment).json` (e.g. `wiz-cloud-billable-units.json`).
  - **Envelope fields:** `query`, `saved_at`, `source_tool`, `result_count`, `results`, `top_k` (same as seed `results` when written by `wiz_cache_manager.py kb-snapshot save` / `materialize_licensing_kb_snapshots.py`).
  - **Expected seeds:** `docs/ai/cache/wiz_mcp_server/kb_seed_queries.yaml` lists each `initial_query`; each maps to one envelope path under `mcp_query_snapshots/<category>/` (see `wiz_cache_manager.py` naming rules). **`kb-snapshot status --initial-slug <category>`** compares on-disk envelopes to yaml (optional `--seed-file`).
  - **Missing-file behavior:** re-run that seed’s `initial_query` via `wiz_docs_knowledge_base` and overwrite the derived `<stem>.json`.

## Non-goals

- Replacing **wiz-remote** for interactive search when available; local cache is a **fallback + speed** layer, not a second product database.
- **Guaranteed** commercial accuracy on every price/SKU edge case — **flag uncertainty** and use discovery questions instead of fabricating.
- **Runtime** `if _TEST_CUSTOMER` hacks; fixture may **illustrate** acceptance only.

## Scope (files — expect to touch; exact list after design)

- `docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` (Accomplishments + **Upsell Path**)
- `docs/ai/playbooks/update-customer-notes.md` (step pointers; no duplicate full rubric)
- `docs/ai/playbooks/load-product-intelligence.md` (**§G9** / **§2.59** — TASK-074 snapshot + §G4 ext hydration on LPI refresh)
- `prestonotes_gdoc/` only if **G1** requires parser / section mapping fixes
- External + SKU reasoning: **§G4 in this task** (and tab-doc link) — not a new standalone reference file until build.
- **`mcp_query_snapshots/`** — **gitignored or committed** (operator choice); output-only, no `README` in the cache root required.
- **Build:** optional helper script + tests as described in **§G8**; prefer extending **`load-product-intelligence.md`** and **`update-customer-notes.md`** over adding new markdown files.
- **`.cursor/rules/21-extractor.mdc`**: short pointer if extraction posture for Upsell/Accomplishments changes

## Acceptance

- [x] **A1a** — Tab doc and playbook state clearly that **decommissioning or displacing a non-Wiz security product** is a **first-class Accomplishment** when evidenced. *(doc guidance landed)*
- [x] **A1b** — Writer/parser placement behavior is correct: UCN output maps accomplishment-like vendor displacement evidence to **Accomplishments** (not **Workflows**) in `read_doc` `section_map`, or uses an explicit allowed skip with reason. *(covered by writer routing tests in `prestonotes_gdoc/tests/test_task_050_ucn_writer.py`)*
- [ ] **A1c** — Proof artifact exists: **E2E `v1_full`** or approved **manual** UCN on `_TEST_CUSTOMER` shows the correct section placement for the Prisma-style case.
- [x] **A2** — **Upsell Path** guidance includes: **Wiz Cloud** vs **Defend / Code / Sensor** licensing **concepts**; **workload-driving** vs **core** capabilities (with **user-vetted** examples like DSPM/ASM vs CIEM); and **gap → SKU → business language** mapping tied to **goals, challenges, risk, compliance, AI**.
- [x] **A3** — **Local license / product snapshot** path and refresh policy documented in **this task (§G3)**; refresh procedure + what to do when **MCP unavailable**; no silent stub content in customer artifacts.
- [x] **A4** — **External references (§G4 table)** is linked from **`mutations-account-summary-tab.md`** Upsell section at build; **no separate** `ucn-upsell-context-refs` file required — **§G4** in **TASK-074** is the SSoT until optional split at build.
- [x] **A5** — At least one of: **(i)** discovery-question pattern in this task’s deliverables, or **(ii)** explicit handoff to **TASK-075** with clear scope (see **[TASK-075](TASK-075-ucn-upsell-path-discovery-questions.md)**).
- [ ] **A6** — **Verification** below passes. *(repo lint/test/integrity passed; E2E/manual `_TEST_CUSTOMER` proof still pending per A1c)*
- [x] **A7** — **`load-product-intelligence.md`** states that a **refresh/delta-hydration** LPI run hydrates **§G4** URLs into the **ext** cache (indexes + `ext/pages/` when missing/stale) per that playbook’s external model; **Activity recap** (or run notes) can cite which §G4 URLs were skipped-as-fresh vs hydrated. *(**§2.59** item 2; **§5** required-structure bullet for §2.59 touch summary.)*
- [x] **A8** — **`load-product-intelligence.md`** states that a **refresh** LPI run invokes **`wiz_docs_knowledge_base`** for seeds in `kb_seed_queries.yaml` and materializes **`mcp_query_snapshots/<category>/*.json`** per **§G8** when snapshots are missing or stale; recap lists refreshed vs skipped-as-fresh.

## Verification

- `bash .cursor/skills/lint.sh` and `bash .cursor/skills/test.sh` after code/doc changes.
- `bash scripts/ci/check-repo-integrity.sh` if paths / manifests / rules lists change.
- Re-run **E2E `v1_full`** (or **manual** UCN on `_TEST_CUSTOMER` with same corpus) and confirm **tester.md §6** row for **Accomplishments** is no longer a false **H** for the Prisma-style case; **Upsell** rows show defensible **H/M/L** with documented gaps only where corpus is thin.
- `uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` remains **0** when extract is in the loop.

## Sequencing

- Land **G1** early if it is a **writer bug** blocking honest E2E scoring.
- **G3** can parallel **G2/G4** once the local path shape is agreed.
- **Follow-on — TASK-075 (detailed and ready):** Execute **[`TASK-075-ucn-upsell-path-discovery-questions.md`](TASK-075-ucn-upsell-path-discovery-questions.md)** immediately after TASK-074 baseline completion as the always-on post-`mutation.json` enrichment pass. Keep write policy as **in-place mutation update with mandatory review artifact** and include the no-new-evidence/no-change branch.

## Notes (product direction — from task author)

- **Wiz Cloud SKU** maps to multiple capabilities; some **increase** licensed **workloads**; **CIEM** may be **in** Cloud but framed as **core** value, not volume, depending on deal — document **nuance** from official Wiz material ingested into the local cache, not only from this task text.
- **AI** is a primary **macro** driver of new security gaps; Upsell should **connect** to it when transcripts or strategy discussions do.
- The most valuable agent behavior when data is missing: **well-formed discovery questions** for the next customer conversation.

## Appendix G10 — Portal nav query paths (`tmp/portal.html.out`)

Ordered **breadcrumb** strings (hyphen-separated path segments) derived from the Wiz docs knowledge portal nav. Use each line as a **candidate** `wiz_docs_knowledge_base` query text; materialized snapshots follow **§G8** (`<category>/` + remainder slug). Seed SSoT is `kb_seed_queries.yaml`.

**Source:** `tmp/portal.html.out` (full file; 1192 lines). Operator: prune, dedupe, and merge sections before scheduling bulk MCP runs.

```text
Licensing and Billing
Licensing and Billing-Billable Units
Licensing and Billing-Billable Units-Wiz Audit History
Licensing and Billing-Billable Units-Wiz Cloud Cost
Licensing and Billing-Billable Units-Wiz Code
Licensing and Billing-Billable Units-Wiz Cloud
Licensing and Billing-Billable Units-Wiz Defend Ingestion
Licensing and Billing-Billable Units-Wiz for On-prem
Licensing and Billing-Billable Units-Wiz Log Retention
Licensing and Billing-Billable Units-Wiz Runtime Sensor
Licensing and Billing-Consumption-based Pricing
Licensing and Billing-License Comparison
Licensing and Billing-License Comparison-Wiz Cloud
Licensing and Billing-License Comparison-Wiz Code
Licensing and Billing-License Comparison-Wiz Defend Ingestion
Licensing and Billing-License Comparison-Wiz Runtime Sensor
Licensing and Billing-License Comparison-Wiz Cloud Cost
Licensing and Billing-License Comparison-Wiz Tenant Manager
Licensing and Billing-License Comparison-Support Licenses
Products-Overview
Products-Wiz Code
Products-Wiz Code-Cloud-Aware Scanning
Products-Wiz Code-Code-to-Cloud Pipeline
Products-Wiz Code-Code-to-Cloud Pipeline-Containers (Manual)
Products-Wiz Code-Code-to-Cloud Pipeline-Containers (Seamless)
Products-Wiz Code-Code-to-Cloud Pipeline-IaC
Products-Wiz Code-Exception Management
Products-Wiz Code-How Wiz Code Works
Products-Wiz Code-How Wiz Code Works-IDE Extension
Products-Wiz Code-How Wiz Code Works-VCS Connectors
Products-Wiz Code-How Wiz Code Works-Wiz CLI
Products-Wiz Code-Implement Wiz Code
Products-Wiz Code-Implement Wiz Code-Implement Developer Workflows
Products-Wiz Code-Implement Wiz Code-Implement for VCS
Products-Wiz Code-Implement Wiz Code-Implement for CI/CD
Products-Wiz Code-Implement Wiz Code-IDE Quick Start
Products-Wiz Code-Remediate with Wiz Code
Products-Wiz Code-Supply Chain Security
Products-Wiz Code-Supply Chain Security-IDE
Products-Wiz Code-Supply Chain Security-VCS
Products-Wiz Code-Supply Chain Security-CI
Products-Wiz Code-Supported Languages
Products-Wiz Code-Tutorials
Products-Wiz Code-Use Wiz CLI
Products-Wiz Code-Use Wiz CLI-Diff-Based Mode
Products-Wiz Code-Use Wiz CLI-Scan & Tag Container Images
Products-Wiz Code-Use Wiz CLI-Scan Directories
Products-Wiz Code-Use Wiz CLI-Scan VM Images
Products-Wiz Code-Use Wiz CLI-Scan VMs
Products-Wiz Code-Wiz AI in Code
Products-Wiz Cloud
Products-Wiz Cloud-Agentless Scanning
Products-Wiz Cloud-Agentless Scanning-Container Scanning
Products-Wiz Cloud-Agentless Scanning-Attack Surface Scanner
Products-Wiz Cloud-Agentless Scanning-End-of-Life Detection
Products-Wiz Cloud-Agentless Scanning-Registry Scanning
Products-Wiz Cloud-Agentless Scanning-Serverless Scanning
Products-Wiz Cloud-Agentless Scanning-Supported Third-party Detections
Products-Wiz Cloud-Agentless Scanning-Workload Scanning
Products-Wiz Cloud-Cloud Risk Assessment
Products-Wiz Cloud-Cloud Risk Assessment-Wiz Green Agent
Products-Wiz Cloud-Cloud Risk Assessment-Attack Surface Rules
Products-Wiz Cloud-Cloud Risk Assessment-Cloud Detection & Response
Products-Wiz Cloud-Cloud Risk Assessment-Custom File Detection
Products-Wiz Cloud-Cloud Risk Assessment-File Integrity Monitoring
Products-Wiz Cloud-Cloud Risk Assessment-Malicious IP & Domain Detection
Products-Wiz Cloud-Cloud Risk Assessment-Malware Detection
Products-Wiz Cloud-Cloud Risk Assessment-Network Exposure
Products-Wiz Cloud-Cloud Risk Assessment-Threat Detection
Products-Wiz Cloud-Cloud Risk Assessment-IaC Drift Detection
Products-Wiz Cloud-Cloud Risk Assessment-HCP Terraform Connector
Products-Wiz Cloud-Cloud Risk Assessment-Supported Platforms
Products-Wiz Cloud-Tutorials
Products-Wiz Cloud-Tutorials-Environment Segregation
Products-Wiz Cloud-Tutorials-Cloud Detection & Response
Products-Wiz Cloud-Tutorials-End-of-Life Detection
Products-Wiz Cloud-Tutorials-External Exposure
Products-Wiz Cloud-Tutorials-Malware Detection
Products-Wiz Cloud-Tutorials-Serverless Functions
Products-Wiz Cloud-FAQ
Products-Wiz Defend
Products-Wiz Defend-Start your Journey
Products-Wiz Defend-Connect
Products-Wiz Defend-Connect-Supported Log Types
Products-Wiz Defend-Connect-Workload Logs
Products-Wiz Defend-Prepare
Products-Wiz Defend-Prepare-Incident Readiness Assessment
Products-Wiz Defend-Prepare-Incident Readiness Framework
Products-Wiz Defend-Prepare-Improve Your Readiness
Products-Wiz Defend-Detect
Products-Wiz Defend-Detect-Threat Detection Coverage
Products-Wiz Defend-Detect-Legacy Threat Detection Rules
Products-Wiz Defend-Investigate
Products-Wiz Defend-Investigate-Automatic Investigation
Products-Wiz Defend-Investigate-Blue Agent
Products-Wiz Defend-Respond
Products-Wiz Defend-SecOps Integration
Products-Wiz Defend-Attack Simulations
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations-AWS
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations-Azure
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations-Azure and Sensor
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations-GCP
Products-Wiz Defend-Attack Simulations-Automated Multi-Stage Simulations-Okta
Products-Wiz Defend-Attack Simulations-Red Team Simulations
Products-Wiz Defend-Attack Simulations-Red Team Simulations-AWS
Products-Wiz Defend-Attack Simulations-Red Team Simulations-Azure
Products-Wiz Defend-Attack Simulations-Red Team Simulations-GCP
Products-Wiz Defend-Attack Simulations-Red Team Simulations-GitHub
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Kubernetes (Recommended)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Kubernetes (Lite)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Kubernetes (TeamTNT)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Kubernetes (Windows)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Linux
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Linux (Lite)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Fargate (ECS)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Fargate (EKS)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Azure Container Apps (ACA)
Products-Wiz Defend-Attack Simulations-Runtime Sensor Simulations-Windows (Lite)
Products-Wiz Defend-Attack Simulations-Custom Simulation Best Practices
Products-Wiz Runtime Sensor
Products-Wiz Runtime Sensor-How the Sensor Works
Products-Wiz Runtime Sensor-How the Sensor Works-Linux (eBPF)
Products-Wiz Runtime Sensor-How the Sensor Works-Windows (Driver)
Products-Wiz Runtime Sensor-How the Sensor Works-Serverless Containers (ptrace)
Products-Wiz Runtime Sensor-How the Sensor Works-Communication
Products-Wiz Runtime Sensor-How the Sensor Works-Runtime Operations
Products-Wiz Runtime Sensor-How the Sensor Works-Resource Consumption
Products-Wiz Runtime Sensor-Threat Detection & Response
Products-Wiz Runtime Sensor-Threat Detection & Response-Real-time Threat Detection
Products-Wiz Runtime Sensor-Threat Detection & Response-Runtime Events
Products-Wiz Runtime Sensor-Threat Detection & Response-Sensor-based Forensics
Products-Wiz Runtime Sensor-Risk Assessment
Products-Wiz Runtime Sensor-Risk Assessment-Network Mapping
Products-Wiz Runtime Sensor-Risk Assessment-Vulnerability Runtime Validation
Products-Wiz Runtime Sensor-Risk Assessment-Runtime Network Exposure
Products-Wiz Runtime Sensor-Risk Assessment-Workload Scanner
Products-Wiz Runtime Sensor-Tutorials
Products-Wiz Runtime Sensor-FAQ
Products-Wiz Cloud Cost
Products-Wiz Cloud Cost-Get Started
Products-Wiz Cloud Cost-Setup
Products-Wiz Cloud Cost-Setup-AWS Setup
Products-Wiz Cloud Cost-Setup-Azure Setup
Products-Wiz Cloud Cost-Setup-GCP Setup
Products-Wiz Cloud Cost-Discovery
Products-Wiz Cloud Cost-Discovery-Kubernetes Costs
Products-Wiz Cloud Cost-Optimization
Products-Wiz Cloud Cost-Optimization-Optimization Engine
Products-Wiz Cloud Cost-Optimization-Rightsizing
Products-Wiz Cloud Cost-Monitoring
Products-Wiz Cloud Cost-Governance

Solutions-Overview
Solutions-AI Security
Solutions-AI Security-About Wiz AI Security
Solutions-AI Security-How AI Security Works
Solutions-AI Security-Coverage
Solutions-AI Security-Use Cases
Solutions-AI Security-AI Visibility
Solutions-AI Security-AI Visibility-AI Resource Discovery
Solutions-AI Security-AI Visibility-Using the AI Inventory
Solutions-AI Security-AI Visibility-MCP Server Detection
Solutions-AI Security-AI Visibility-Log-Based AI Discovery
Solutions-AI Security-AI Posture & Risk
Solutions-AI Security-AI Posture & Risk-AI Risk Detection
Solutions-AI Security-AI Posture & Risk-Reduce AI Posture Risk
Solutions-AI Security-Runtime AI Protection
Solutions-AI Security-Runtime AI Protection-AI Threat Detection
Solutions-AI Security-Runtime AI Protection-Shadow AI Detection
Solutions-AI Security-Tutorials
Solutions-API Security
Solutions-API Security-About API Security
Solutions-API Security-API Discovery (Cloud)
Solutions-API Security-API Discovery (Sensor)
Solutions-API Security-API Discovery (Sensor)-Sensor Setup
Solutions-API Security-API Discovery (Sensor)-API Identification
Solutions-API Security-API Discovery (Attack Surface)
Solutions-API Security-API Security Risk Assessment
Solutions-API Security-API Security Tutorials
Solutions-Attack Surface Management (ASM)
Solutions-Attack Surface Management (ASM)-About ASM
Solutions-Attack Surface Management (ASM)-How ASM Works
Solutions-Attack Surface Management (ASM)-Activation Best Practices and Load Management
Solutions-Attack Surface Management (ASM)-Wiz Red Agent
Solutions-Compliance
Solutions-Compliance-How Compliance Assessment Works
Solutions-Compliance-Supported Cloud Assessment Frameworks
Solutions-Compliance-Supported Host Assessment Frameworks
Solutions-Compliance-Compliance Framework AI Assistant
Solutions-Compliance-Compliance FAQ
Solutions-Container & K8s Security
Solutions-Container & K8s Security-Container & Kubernetes Security Tutorials
Solutions-Container & K8s Security-How Container & Kubernetes Security Work
Solutions-Container & K8s Security-Container & Kubernetes Security FAQ
Solutions-Data Security (DSPM)
Solutions-Data Security (DSPM)-Wiz Data Security
Solutions-Data Security (DSPM)-AI-Powered Classification
Solutions-Data Security (DSPM)-Shadow Data Detection
Solutions-Data Security (DSPM)-Shadow Data Detection-How Detection Works
Solutions-Data Security (DSPM)-Shadow Data Detection-Configure Detection
Solutions-Data Security (DSPM)-Configuration
Solutions-Data Security (DSPM)-Quickstart
Solutions-Data Security (DSPM)-Coverage
Solutions-Data Security (DSPM)-Data Scanning
Solutions-Data Security (DSPM)-Data Classification Rules
Solutions-Data Security (DSPM)-Data Inventory & Findings
Solutions-Data Security (DSPM)-Enforce Data Labeling
Solutions-Data Security (DSPM)-Tutorials
Solutions-Data Security (DSPM)-FAQ
Solutions-Identity Security (CIEM)
Solutions-Identity Security (CIEM)-How Identity Security Works
Solutions-Identity Security (CIEM)-Access Management
Solutions-Identity Security (CIEM)-Identity Security Tutorials
Solutions-Identity Security (CIEM)-Access Privilege Mapping
Solutions-Identity Security (CIEM)-Access Privilege Mapping-AWS
Solutions-Identity Security (CIEM)-Access Privilege Mapping-Azure
Solutions-Identity Security (CIEM)-Access Privilege Mapping-GCP
Solutions-Identity Security (CIEM)-Access Privilege Mapping-OCI
Solutions-Identity Security (CIEM)-Access Privilege Mapping-AAD
Solutions-Identity Security (CIEM)-Access Privilege Mapping-Azure DevOps
Solutions-Identity Security (CIEM)-Access Privilege Mapping-GitHub
Solutions-Identity Security (CIEM)-Access Privilege Mapping-Snowflake
Solutions-Identity Security (CIEM)-Access Privilege Mapping-GitLab
Solutions-Identity Security (CIEM)-Access Privilege Mapping-Microsoft Graph
Solutions-Identity Security (CIEM)-AWS Condition Keys
Solutions-Identity Security (CIEM)-Identity Security FAQ
Solutions-Post-Quantum Cryptography (PQC)
Solutions-Software Composition Analysis (SCA)
Solutions-Software Composition Analysis (SCA)-Vulnerability Assessment
Solutions-Software Composition Analysis (SCA)-Tutorials
Solutions-Static Application Security Testing (SAST)
Solutions-Secure Cloud Configuration (CSPM)
Solutions-Secure Cloud Configuration (CSPM)-How CSPM Works
Solutions-Secure Cloud Configuration (CSPM)-Near Real-time Scanning
Solutions-Secure Cloud Configuration (CSPM)-Supported Resources
Solutions-Secure Cloud Configuration (CSPM)-How CCRs are Developed
Solutions-Secure Cloud Configuration (CSPM)-Custom Rules
Solutions-Secure Cloud Configuration (CSPM)-Custom Rules-Writing Custom Rules
Solutions-Secure Cloud Configuration (CSPM)-Custom Rules-Rego Basics
Solutions-Secure Cloud Configuration (CSPM)-Custom Rules-Writing Exercises
Solutions-Secure Cloud Configuration (CSPM)-Function Catalogs
Solutions-Secure Cloud Configuration (CSPM)-Function Catalogs-Cloud
Solutions-Secure Cloud Configuration (CSPM)-Function Catalogs-IaC
Solutions-Secure Cloud Configuration (CSPM)-IaC File Parsing
Solutions-Secure Cloud Configuration (CSPM)-IaC File Parsing-CloudFormation
Solutions-Secure Cloud Configuration (CSPM)-IaC File Parsing-Terraform
Solutions-Secure Cloud Configuration (CSPM)-Tutorials
Solutions-Secure Host Configuration
Solutions-Secure Host Configuration-How Secure Host Configuration Works
Solutions-Secure Host Configuration-Secure Host Configuration Tutorials
Solutions-Secure Host Configuration-Writing Custom HCRs
Solutions-Secure Host Configuration-Secure Host Configuration FAQ
Solutions-Secure Host Configuration-Wiz Direct OVAL schema
Solutions-Secure Use of Secrets
Solutions-Secure Use of Secrets-Secret Detection
Solutions-Secure Use of Secrets-AI-Powered Detection
Solutions-Secure Use of Secrets-Secret Validation
Solutions-Secure Use of Secrets-Secret Findings & Graphs
Solutions-Secure Use of Secrets-Secret Scanning Coverage
Solutions-Secure Use of Secrets-Secrets Tutorials
Solutions-Snowflake
Solutions-Snowflake-Snowflake Scanning
Solutions-Snowflake-Snowflake Tutorials
Solutions-Snowflake-Snowflake FAQ
Solutions-Unified Vulnerability Management (UVM)
Solutions-Unified Vulnerability Management (UVM)-Quick Start
Solutions-Unified Vulnerability Management (UVM)-How Asset Correlation Works
Solutions-Unified Vulnerability Management (UVM)-How Asset Classification Works
Solutions-Unified Vulnerability Management (UVM)-Manage Duplicates
Solutions-Unified Vulnerability Management (UVM)-Infrastructure Vulnerability Scanners
Solutions-Unified Vulnerability Management (UVM)-AppSec Code Scanners (SAST & SCA)
Solutions-Unified Vulnerability Management (UVM)-Data Security Scanners (DSPM)
Solutions-Unified Vulnerability Management (UVM)-API Security Scanners (DAST)
Solutions-Unified Vulnerability Management (UVM)-UVM and Attack Surface Management
Solutions-Vulnerability Management
Solutions-Vulnerability Management-How Vulnerability Detection Works
Solutions-Vulnerability Management-How Vulnerability Management Works
Solutions-Vulnerability Management-Export Vulnerability Findings
Solutions-Vulnerability Management-Tutorials
Solutions-Vulnerability Management-Bridging the NVD Gap
Solutions-Vulnerability Management-Adapting to the new NIST model
Solutions-Vulnerability Management-Dependency Libraries & Packages
Solutions-Vulnerability Management-Recommended Scanner Settings
Solutions-Vulnerability Management-FAQ
Solutions-Vulnerabilities Changelog
Solutions-VMware vSphere
Solutions-Wiz for On-prem-Quick Start
Solutions-Wiz for On-prem-Resource Management
Solutions-Wiz for Gov
Solutions-Wiz for Gov-Secure Configuration
Solutions-Wiz for Gov-Supported FedRAMP Controls
Solutions-Wiz for Gov-Supported Providers
Solutions-Wiz Tenant Manager
Solutions-Wiz Tenant Manager-Get Started
Solutions-Wiz Tenant Manager-Architecture
Solutions-Wiz Threat Services
Solutions-Wiz Threat Services-Incident Response
Solutions-Wiz Threat Services-Threat Exposure
Solutions-Wiz Threat Services-Threat Hunting
Solutions-Wiz Threat Services-Tabletop Wargame
Solutions-WizOS
Solutions-WizOS-Quickstart
Solutions-WizOS-Required URLs
Solutions-WizOS-Tutorials
Solutions-WizOS-Alpine-to-WizOS Compatibility
Solutions-WizOS-How WizOS Works
Solutions-WizOS-Deploy WizOS
Solutions-WizOS-Deploy WizOS-Pilot WizOS
Solutions-WizOS-Deploy WizOS-Operationalize at Scale
Solutions-WizOS-FAQ
Platform Capabilities-Overview
Platform Capabilities-Actions & Automations
Platform Capabilities-Actions & Automations-Automation Rules & Triggers
Platform Capabilities-Actions & Automations-How Actions and Automation Rules Work
Platform Capabilities-Actions & Automations-Automated Platform Actions
Platform Capabilities-Actions & Automations-Test Actions and Automations
Platform Capabilities-Audit History
Platform Capabilities-Cloud Inventory
Platform Capabilities-Compliance Frameworks
Platform Capabilities-Compliance Frameworks-Cloud Frameworks
Platform Capabilities-Compliance Frameworks-Wiz Frameworks
Platform Capabilities-Connectors
Platform Capabilities-Ignore Rules
Platform Capabilities-Ignore Rules-Using Ignore Rules
Platform Capabilities-Forensics
Platform Capabilities-Forensics-Agentless Forensics
Platform Capabilities-Ownership Management
Platform Capabilities-Quotas & Limits
Platform Capabilities-Remediation & Response
Platform Capabilities-SBOM
Platform Capabilities-Security Graph
Platform Capabilities-Security Graph-Cloud Resource Graph Object
Platform Capabilities-Security Graph-Data Resource Graph Object
Platform Capabilities-Security Graph-Representative Resources
Platform Capabilities-Security Graph-Security Graph Object Normalization
Platform Capabilities-Security Graph-Security Graph Schema
Platform Capabilities-Security Graph-Tutorials
Platform Capabilities-Security Graph-Tutorials-Building Custom Queries
Platform Capabilities-Security Graph-Tutorials-Optimizing Queries
Platform Capabilities-Security Graph-Tutorials-Advanced Custom Queries
Platform Capabilities-Service Catalog
Platform Capabilities-Service Catalog-About Services
Platform Capabilities-Service Catalog-How Service Catalog Works
Platform Capabilities-Service Catalog-About Discovery Rules
Platform Capabilities-Service Catalog-Projects & Services
Platform Capabilities-Service Catalog-Workflow
Platform Capabilities-Service Catalog-Automate Ownership via API
Platform Capabilities-System Health Issues
Platform Capabilities-Wiz AI
Platform Capabilities-Wiz AI-AI Tools
Platform Capabilities-Wiz Integrations (WIN)
Platform Capabilities-Wiz Integrations (WIN)-How Integrations Work
Platform Capabilities-Wiz Integrations (WIN)-Integration Tutorials
Platform Capabilities-Wiz Integrations (WIN)-Integrate with BI tools
Platform Capabilities-Wiz Integrations (WIN)-All ServiceNow Integrations
Platform Capabilities-Wiz Integrations (WIN)-Troubleshoot Integrations
Platform Capabilities-Wiz Threat Intelligence
Platform Capabilities-Wiz Workflows
Platform Capabilities-Wiz Workflows-Create a Workflow
Platform Capabilities-Wiz Workflows-Best Practices
Platform Capabilities-Wiz Workflows-CEL Reference
Connect, Deploy & Configure-Overview-API Calls Used by Wiz
Connect, Deploy & Configure-Overview-CSP Permissions
Connect, Deploy & Configure-Overview-Container Image Validation
Connect, Deploy & Configure-Overview-Deployment Versioning
Connect, Deploy & Configure-Overview-Migrate to a New Tenant
Connect, Deploy & Configure-Overview-Public Checksums
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Advanced Outpost
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Kubernetes Connectors
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Remediation & Response
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Runtime Sensor
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-VCS Connectors
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Wiz Admission Controller
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Wiz Broker
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Wiz CLI
Connect, Deploy & Configure-Overview-Required URLs, IPs and Account IDs-Wiz IDE Extension
Connect, Deploy & Configure-Overview-Static IP Egress for Wiz Deployments
Connect, Deploy & Configure-Overview-Deployments - Terraform Registry Modules
Connect, Deploy & Configure-Access & Projects
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-How SAML SSO Works
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-How OIDC SSO Works
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-How SCIM User Provisioning Works
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-AD FS
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-AWS IAM Identity Center
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Entra ID (AAD)
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Google Workspace
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-JumpCloud
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Okta (manual)
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-OneLogin
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Ping Federate
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Ping Identity
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using SAML-Generic SAML IdP
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using OIDC
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using OIDC-Entra ID
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using OIDC-Google Workspace
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using OIDC-Okta
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SSO using OIDC-Generic OIDC IdP
Connect, Deploy & Configure-Access & Projects-Single Sign-On (SSO)-Configure SCIM Provisioning
Connect, Deploy & Configure-Access & Projects-How Projects Work
Connect, Deploy & Configure-Access & Projects-How Role Mapping Works
Connect, Deploy & Configure-Access & Projects-Login & MFA
Connect, Deploy & Configure-Access & Projects-Login & MFA-Built-in User Roles
Connect, Deploy & Configure-Access & Projects-Login & MFA-Multi-tenant (Advanced) Login
Connect, Deploy & Configure-Access & Projects-Login & MFA-Role-Based Access Control
Connect, Deploy & Configure-CI/CD Connectors
Connect, Deploy & Configure-CI/CD Connectors-Connect to HCP Terraform
Connect, Deploy & Configure-CI/CD Connectors-Required Permissions and APIs
Connect, Deploy & Configure-Cloud Connectors
Connect, Deploy & Configure-Cloud Connectors-Alibaba Cloud Connectors
Connect, Deploy & Configure-Cloud Connectors-Alibaba Cloud Connectors-Connect to Alibaba Cloud
Connect, Deploy & Configure-Cloud Connectors-Alibaba Cloud Connectors-Required Permissions for Connectors in Alibaba
Connect, Deploy & Configure-Cloud Connectors-Alibaba Cloud Connectors-Update Connector Permissions
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-How the Wiz Azure App Works
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Connect to Azure
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Connect to Azure (manual)
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Connect Azure Cloud Events and Logs
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Connect Azure Cloud Events and Logs-Azure Cloud Events
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Connect Azure Cloud Events and Logs-VNet Flow Logs
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Required Permissions for Connectors in Azure
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Update Connector Permissions
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Deploy Azure Policy for Key Vaults
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Scan ADE Encrypted VMs
Connect, Deploy & Configure-Cloud Connectors-Azure Connectors-Troubleshoot Connector
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect using Delegated Administrator
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS (manual)
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-AWS CloudTrail
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-AWS EKS Audit Logs
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-AWS VPC Flow Logs
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-AWS DNS Logs
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-Multiple S3 Buckets
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Connect to AWS Cloud Events and Logs-Bedrock Invocation Logs
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Troubleshoot Connectors to AWS
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Update Connector Permissions
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Required Permissions for Connectors in AWS
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Deploy AWS BYOK
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Deploy Custom Re-encryption Keys
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-AWS Sovereign Account (cloud scan only)
Connect, Deploy & Configure-Cloud Connectors-AWS Connectors-Convert to Organization Deployment
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP (manual)
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP Cloud Events and Logs
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP Cloud Events and Logs-Connect to GCP Audit Logs
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP Cloud Events and Logs-Connect to GCP VPC Flow Logs
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Connect to GCP Cloud Events and Logs-Connect to Google Workspace
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Uninstall Connector Resources
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Required Permissions for Connectors in GCP
Connect, Deploy & Configure-Cloud Connectors-GCP Connectors-Update Connector Permissions
Connect, Deploy & Configure-Cloud Connectors-OCI Connectors
Connect, Deploy & Configure-Cloud Connectors-OCI Connectors-Connect to OCI
Connect, Deploy & Configure-Cloud Connectors-OCI Connectors-Connect Cloud Events
Connect, Deploy & Configure-Cloud Connectors-OCI Connectors-Required Permissions
Connect, Deploy & Configure-Cloud Connectors-OCI Connectors-Update Connector Permissions
Connect, Deploy & Configure-Cloud Connectors-Connect to Linode
Connect, Deploy & Configure-Cloud Connectors-Connect to Linode-Required Permissions
Connect, Deploy & Configure-Cloud Connectors-Connect to VMware vSphere
Connect, Deploy & Configure-Cloud Connectors-Connect to VMware vSphere-Required Permissions
Connect, Deploy & Configure-IDE Extension
Connect, Deploy & Configure-IDE Extension-Scan Code in AI IDEs
Connect, Deploy & Configure-IDE Extension-Scan Code in JetBrains IDEs
Connect, Deploy & Configure-IDE Extension-Scan Code in Visual Studio
Connect, Deploy & Configure-IDE Extension-Scan Code in VS Code
Connect, Deploy & Configure-IDE Extension-Compatibility of the IDE Extension with Wiz CLI
Connect, Deploy & Configure-Kubernetes Deployments
Connect, Deploy & Configure-Kubernetes Deployments-Install all K8s Deployments (Helm)
Connect, Deploy & Configure-Kubernetes Connectors
Connect, Deploy & Configure-Kubernetes Connectors-Connect to Kubernetes (Helm)
Connect, Deploy & Configure-Kubernetes Connectors-Connect to Kubernetes (Terraform)
Connect, Deploy & Configure-Kubernetes Connectors-Connect to Kubernetes (Bash Script)
Connect, Deploy & Configure-Kubernetes Connectors-Connect to Kubernetes (kubectl)
Connect, Deploy & Configure-Kubernetes Connectors-Required Permissions and APIs for Kubernetes Connectors
Connect, Deploy & Configure-Kubernetes Connectors-Versioning for Kubernetes Connectors
Connect, Deploy & Configure-Kubernetes Connectors-Configure K8s Audit Log Collector
Connect, Deploy & Configure-Kubernetes Connectors-Platform-specific Installation
Connect, Deploy & Configure-Kubernetes Connectors-Kubernetes Secret Rotation
Connect, Deploy & Configure-Kubernetes Connectors-Provide Secrets to Helm Charts
Connect, Deploy & Configure-Kubernetes Connectors-Auto-connect EKS clusters
Connect, Deploy & Configure-Kubernetes Connectors-Wiz Deployment Network Troubleshooting Tool
Connect, Deploy & Configure-Kubernetes Connectors-Use a Proxy Server with K8s
Connect, Deploy & Configure-Registry Connectors
Connect, Deploy & Configure-Registry Connectors-Connect to Amazon ECR
Connect, Deploy & Configure-Registry Connectors-Connect to Azure Container Registry
Connect, Deploy & Configure-Registry Connectors-Connect to GHCR
Connect, Deploy & Configure-Registry Connectors-Connect to Docker Hub Container Registry
Connect, Deploy & Configure-Registry Connectors-Connect to JFrog Artifactory Container Registry
Connect, Deploy & Configure-Registry Connectors-Connect to a Container Registry (generic)
Connect, Deploy & Configure-Registry Connectors-SLSA Provenance in Registry Scanning
Connect, Deploy & Configure-Remediation & Response
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS-Deploy R&R to AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS-Update R&R in AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS-Create Custom Response Functions for AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS-Response Functions in AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in AWS-Troubleshoot R&R in AWS
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Deploy R&R to Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Update R&R in Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Create Custom Response Functions for Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Response Functions in Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Manually Deploy R&R to Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in Azure-Troubleshoot R&R in Azure
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Deploy R&R to GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Update Remediation & Response in GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Create Custom Response Functions for GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Response Functions in GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Manually Deploy R&R to GCP
Connect, Deploy & Configure-Remediation & Response-Remediation & Response in GCP-Troubleshoot R&R in GCP
Connect, Deploy & Configure-Remediation & Response-R&R Deployment Patterns
Connect, Deploy & Configure-Remediation & Response-Create Automation Rules for Remediation & Response
Connect, Deploy & Configure-Remediation & Response-Versioning for R&R
Connect, Deploy & Configure-Remediation & Response-Remove R&R deployment
Connect, Deploy & Configure-Remediation & Response-R&R Python Libraries Reference
Connect, Deploy & Configure-Remediation & Response-Response Functions Permissions Reference
Connect, Deploy & Configure-Remediation & Response-R&R Event Payloads Reference
Connect, Deploy & Configure-Remediation & Response-R&R System Health Issues
Connect, Deploy & Configure-Runtime Sensor
Connect, Deploy & Configure-Runtime Sensor-Workload Scanner
Connect, Deploy & Configure-Runtime Sensor-Workload Scanner-Troubleshoot
Connect, Deploy & Configure-Runtime Sensor-Installation Guidelines
Connect, Deploy & Configure-Runtime Sensor-Installation Guidelines-Supported Platforms
Connect, Deploy & Configure-Runtime Sensor-Installation Guidelines-Required Permissions
Connect, Deploy & Configure-Runtime Sensor-Installation Guidelines-Environment Variables
Connect, Deploy & Configure-Runtime Sensor-Installation Guidelines-Configure TLS Proxy
Connect, Deploy & Configure-Runtime Sensor-Kubernetes
Connect, Deploy & Configure-Runtime Sensor-Kubernetes-Install
Connect, Deploy & Configure-Runtime Sensor-Kubernetes-Upgrade
Connect, Deploy & Configure-Runtime Sensor-Kubernetes-Uninstall
Connect, Deploy & Configure-Runtime Sensor-Kubernetes-Troubleshoot
Connect, Deploy & Configure-Runtime Sensor-Linux
Connect, Deploy & Configure-Runtime Sensor-Linux-Install (Native/Container)
Connect, Deploy & Configure-Runtime Sensor-Linux-Install for ECS on EC2
Connect, Deploy & Configure-Runtime Sensor-Linux-Install for NixOS
Connect, Deploy & Configure-Runtime Sensor-Linux-Upgrade
Connect, Deploy & Configure-Runtime Sensor-Linux-Uninstall
Connect, Deploy & Configure-Runtime Sensor-Linux-Troubleshoot
Connect, Deploy & Configure-Runtime Sensor-Serverless Container
Connect, Deploy & Configure-Runtime Sensor-Serverless Container-Install for ECS
Connect, Deploy & Configure-Runtime Sensor-Serverless Container-Install for EKS
Connect, Deploy & Configure-Runtime Sensor-Serverless Container-Install for ACA
Connect, Deploy & Configure-Runtime Sensor-Serverless Container-Install (Embedded)
Connect, Deploy & Configure-Runtime Sensor-Serverless Container-Troubleshoot
Connect, Deploy & Configure-Runtime Sensor-Windows
Connect, Deploy & Configure-Runtime Sensor-Windows-Install on Windows VMs
Connect, Deploy & Configure-Runtime Sensor-Windows-Install on Multiple Azure VMs
Connect, Deploy & Configure-Runtime Sensor-Windows-Install on Kubernetes nodes
Connect, Deploy & Configure-Runtime Sensor-Windows-Troubleshoot
Connect, Deploy & Configure-Runtime Sensor-Windows-Uninstall
Connect, Deploy & Configure-Runtime Sensor-Advanced Installation Methods
Connect, Deploy & Configure-Runtime Sensor-Advanced Installation Methods-1-click EC2 Install
Connect, Deploy & Configure-Runtime Sensor-Advanced Installation Methods-Azure Policy Install
Connect, Deploy & Configure-Runtime Sensor-Advanced Installation Methods-PrivateLink Connect
Connect, Deploy & Configure-Runtime Sensor-Versioning
Connect, Deploy & Configure-Runtime Sensor-Versioning-Freeze Sensor Definitions
Connect, Deploy & Configure-Runtime Sensor-Metrics Exporter
Connect, Deploy & Configure-SaaS Connectors
Connect, Deploy & Configure-SaaS Connectors-Connect to Cloudflare
Connect, Deploy & Configure-SaaS Connectors-Connect to CrowdStrike
Connect, Deploy & Configure-SaaS Connectors-Connect to Databricks
Connect, Deploy & Configure-SaaS Connectors-Connect to Microsoft 365
Connect, Deploy & Configure-SaaS Connectors-Connect to Okta
Connect, Deploy & Configure-SaaS Connectors-Connect to Okta-Okta Tutorials
Connect, Deploy & Configure-SaaS Connectors-Connect to OpenAI
Connect, Deploy & Configure-SaaS Connectors-Connect to Snowflake
Connect, Deploy & Configure-SaaS Connectors-Connect to Vercel
Connect, Deploy & Configure-SaaS Connectors-Required Permissions and APIs
Connect, Deploy & Configure-VCS Connectors
Connect, Deploy & Configure-VCS Connectors-Connect to Azure DevOps
Connect, Deploy & Configure-VCS Connectors-Connect to Bitbucket Cloud
Connect, Deploy & Configure-VCS Connectors-Connect to Bitbucket Data Center
Connect, Deploy & Configure-VCS Connectors-Connect to GitHub
Connect, Deploy & Configure-VCS Connectors-Connect to GitLab
Connect, Deploy & Configure-VCS Connectors-Required Permissions and APIs for Version Control Connectors
Connect, Deploy & Configure-Wiz Admission Controller
Connect, Deploy & Configure-Wiz Admission Controller-Best Practices
Connect, Deploy & Configure-Wiz Admission Controller-Best Practices-1. Onboard and Validate
Connect, Deploy & Configure-Wiz Admission Controller-Best Practices-2. Use & Manage
Connect, Deploy & Configure-Wiz Admission Controller-(Optional) Terraform Setup
Connect, Deploy & Configure-Wiz Admission Controller-Install Wiz Admission Controller
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller-Configure Policy Enforcement
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller-Prevent Misconfigurations
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller-Freeze Clusters
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller-Enforce Image Trust
Connect, Deploy & Configure-Wiz Admission Controller-Use Wiz Admission Controller-Enforce Image Trust with Third-party Signed Images
Connect, Deploy & Configure-Wiz Admission Controller-Prometheus Metrics
Connect, Deploy & Configure-Wiz Admission Controller-High Availability Strategies
Connect, Deploy & Configure-Wiz Admission Controller-Troubleshoot Wiz Admission Controller
Connect, Deploy & Configure-Wiz Admission Controller-Versioning for Wiz Admission Controller
Connect, Deploy & Configure-Wiz Admission Controller-Required Permissions for Wiz Admission Controller
Connect, Deploy & Configure-Wiz Terraform Provider
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_cloud_accounts
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_cloud_configuration_rules
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_cloud_organizations
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_container_registries
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_controls
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_graphql_query
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_host_configuration_rules
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_host_configuration_target_platforms
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_ignore_rules
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_image_integrity_validators
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_integrations
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_kubernetes_clusters
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_kubernetes_namespaces
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_projects
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_repositories
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_resource_groups
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_response_actions_catalog
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_saml_idps
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_security_frameworks
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_threat_detection_rules
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_tunnel_server
Connect, Deploy & Configure-Wiz Terraform Provider-Data Sources-wiz_users
Connect, Deploy & Configure-Wiz Terraform Provider-Resources
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_action_template
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_automation_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_aws_connector
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_cicd_scan_policy
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_cloud_configuration_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_control
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_custom_control
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_custom_rego_package
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_data_classification_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_file_upload
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_gcp_connector
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_github_connector
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_gitlab_connector
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_host_configuration_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_ignore_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_image_integrity_validator
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_integration
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_kubernetes_connector
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_project
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_remediation_and_response_deployment_v2
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_report
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_resource_tagging_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_response_action_catalog_item
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_runtime_response_policy
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_saml_group_mapping
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_saml_idp
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_saml_lens_mapping
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_saved_graph_query
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_scanner_custom_detection_custom_ip_ranges
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_scanner_exclusions
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_scanner_nonos_disk_scan
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_security_framework
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_service_account
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_threat_detection_rule
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_user
Connect, Deploy & Configure-Wiz Terraform Provider-Resources-wiz_user_role
Connect, Deploy & Configure-Wiz Terraform Provider-Modules
Connect, Deploy & Configure-Wiz Terraform Provider-Modules-Manage Custom CCRs
Connect, Deploy & Configure-Wiz Terraform Provider-Modules-Manage Custom Controls
Connect, Deploy & Configure-Wiz Terraform Provider-Modules-Manage Custom HCRs
Connect, Deploy & Configure-Wiz Terraform Provider-Modules-Import Projects
Connect, Deploy & Configure-Wiz Terraform Provider-Modules-Project Import Tutorial
Connect, Deploy & Configure-Wiz Terraform Provider-Versioning for Wiz Terraform Provider
Connect, Deploy & Configure-Wiz Terraform Provider V2
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_action_templates
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_automation_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cicd_scan_policies
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_accounts
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_configuration_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_event_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_organizations
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_resources
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_cloud_resources_v2
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_connectors
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_container_registries
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_controls
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_data_classifiers
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_graphql_query
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_host_configuration_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_host_configuration_target_platforms
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_ignore_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_image_integrity_validators
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_integrations
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_kubernetes_clusters
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_manager_tenant_license_allocation_summary
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_member_tenant_groups
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_member_tenant_license_allocations
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_member_tenant_management_settings
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_member_tenants
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_policy_packages
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_projects
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_reports
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_repositories
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_resource_tagging_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_response_action_catalog_items
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_runtime_response_policies
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_saml_identity_providers
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_saved_graph_queries
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_secret_detection_rules
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_security_frameworks
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_service_accounts
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_sso_identity_providers
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_user_roles
Connect, Deploy & Configure-Wiz Terraform Provider V2-Data Sources-wizv2_users
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_action_template
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_automation_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_cicd_scan_policy
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_cli_deployment
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_cloud_configuration_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_cloud_event_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_control
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_data_classifier
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_file_upload
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_generic_connector
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_host_configuration_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_ignore_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_image_integrity_validator
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_integration
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_managed_tenant_connection
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_manager_tenant_invitation
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_member_tenant_group
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_member_tenant_group_members
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_member_tenant_license_allocation
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_oidc_identity_provider
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_policy_package
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_project
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_report
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_resource_tagging_rule
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_runtime_response_policy
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_saml_identity_provider
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_saved_graph_query
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_scanner_custom_detection_custom_ip_ranges
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_scanner_exclusions
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_scanner_nonos_disk
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_security_framework
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_service_account
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_sso_group_mapping
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_sso_lens_mapping
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_sso_oidc_user
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_sso_saml_user
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_user
Connect, Deploy & Configure-Wiz Terraform Provider V2-Resources-wizv2_user_role
Connect, Deploy & Configure-Wiz Terraform Provider V2-Ephemeral Resources
Connect, Deploy & Configure-Wiz Terraform Provider V2-Ephemeral Resources-wizv2_login_as_member_tenant
Connect, Deploy & Configure-Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Install Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Update Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Connect over AWS PrivateLink
Connect, Deploy & Configure-Wiz Broker-Uninstall Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Troubleshoot Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Versioning for Wiz Broker
Connect, Deploy & Configure-Wiz Broker-High Availability for Wiz Broker
Connect, Deploy & Configure-Wiz Broker-Threat Model for Wiz Broker
Connect, Deploy & Configure-Wiz Browser Extension
Connect, Deploy & Configure-Wiz Browser Extension-Add WizExtend
Connect, Deploy & Configure-Wiz Browser Extension-Use WizExtend
Connect, Deploy & Configure-Wiz CLI
Connect, Deploy & Configure-Wiz CLI-Set Up Wiz CLI V1.X
Connect, Deploy & Configure-Wiz CLI-Integrate Wiz CLI with Git Hooks
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with AWS CodeBuild
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Atlantis
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Azure DevOps
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with BitBucket
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Brainboard
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Buildkite
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with CircleCI
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with GCP Cloud Build
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with GitHub
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with GitLab
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Harness
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Jenkins
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with OpenShift Pipelines
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with Spacelift
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with TeamCity
Connect, Deploy & Configure-Wiz CLI-CI/CD Pipeline Integrations-Integrate Wiz CLI with CI/CD Tools (generic)
Connect, Deploy & Configure-Wiz CLI-Versioning for Wiz CLI
Connect, Deploy & Configure-Wiz MCP
Connect, Deploy & Configure-Wiz MCP-Remote Wiz MCP
Connect, Deploy & Configure-Wiz Outpost
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Required Permissions for Outpost in Alibaba
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Troubleshoot Outpost in Alibaba
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Rotate Outpost Keys in Alibaba
Connect, Deploy & Configure-Wiz Outpost-Alibaba Outpost-Update Outpost Permissions in Alibaba
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Troubleshoot Outpost in AWS
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Required Permissions for Outpost in AWS
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Harden Outpost in AWS
Connect, Deploy & Configure-Wiz Outpost-AWS Outpost-Enable Private EKS
Connect, Deploy & Configure-Wiz Outpost-Sovereign AWS Outpost
Connect, Deploy & Configure-Wiz Outpost-Sovereign AWS Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Sovereign AWS Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Sovereign AWS Outpost-Rotate Outpost Keys in AWS Sovereign
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Phase 3
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Responsibilities & Network Management
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Required Permissions for BYON Outpost in AWS
Connect, Deploy & Configure-Wiz Outpost-AWS Self-managed Network Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Azure Outpost Architecture
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Wiz Automated Outpost Threat Model in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Troubleshoot Outpost in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Required Permissions for Outpost in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Required Permissions for Outpost in Azure (legacy)
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Update Outpost Permissions in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Rotate Outpost Keys in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Verify Bash Script Parameters for Azure Outpost
Connect, Deploy & Configure-Wiz Outpost-Azure Outpost-Harden Outpost in Azure
Connect, Deploy & Configure-Wiz Outpost-Sovereign Azure Outpost
Connect, Deploy & Configure-Wiz Outpost-Sovereign Azure Outpost-Considerations
Connect, Deploy & Configure-Wiz Outpost-Sovereign Azure Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Sovereign Azure Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Sovereign Azure Outpost-Rotate Outpost Secrets in Azure Sovereign
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Phase 3
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Responsibilities & Network Management
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Required Permissions for BYON Outpost in Azure
Connect, Deploy & Configure-Wiz Outpost-Azure Self-managed Network Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Troubleshoot Outpost in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Create a Wiz Outpost in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Connect a GCP Environment
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Required Permissions for Outpost in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Update Outpost Permissions in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Rotate Outpost Keys in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Outpost-Harden Outpost in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Phase 3
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Required Permissions for BYON Outpost in GCP
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Add GCP Network Tags
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Responsibilities & Network Management
Connect, Deploy & Configure-Wiz Outpost-GCP Self-managed Network Outpost-Deployed Resources
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Troubleshoot Outpost in OCI
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Enable Private OKE
Connect, Deploy & Configure-Wiz Outpost-OCI Outpost-Rotate Outpost Keys in OCI
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Phase 1
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Phase 2
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Phase 3
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-OCI Self-managed Network Outpost-Responsibilities & Network Management
Connect, Deploy & Configure-Wiz Outpost-Outpost Lite
Connect, Deploy & Configure-Wiz Outpost-Outpost Lite-How Outpost Lite Works
Connect, Deploy & Configure-Wiz Outpost-Outpost Lite-Registry Scanning
Connect, Deploy & Configure-Wiz Outpost-Outpost Lite-VCS Scanning
Connect, Deploy & Configure-Wiz Outpost-Outpost Lite-Lock Outpost Version
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-AWS Deployment
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-AWS Deployment-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-AWS Deployment-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-AWS Deployment-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-AWS Deployment-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Azure Deployment
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Azure Deployment-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Azure Deployment-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Azure Deployment-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Azure Deployment-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-GCP Deployment
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-GCP Deployment-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-GCP Deployment-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-GCP Deployment-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-GCP Deployment-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-OCI Deployment
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-OCI Deployment-Phase 1
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-OCI Deployment-Phase 2
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-OCI Deployment-Required Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-OCI Deployment-Update Permissions
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Upgrade
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Cluster Deployment Script
Connect, Deploy & Configure-Wiz Outpost-Self-managed Outpost-Versioning
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-AWS Isolated Partition
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-AWS Isolated Partition-Phase 1: AWS
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-AWS Isolated Partition-Phase 2: AWS
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-Azure Sovereign (Non-Gov)
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-Azure Sovereign (Non-Gov)-Phase 1: Azure
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-Self-managed Network Outpost Sovereign (Non-Gov)
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-Self-managed Network Outpost Sovereign (Non-Gov)-AWS Deployment
Connect, Deploy & Configure-Wiz Outpost-Sovereign (Non-Gov) Outpost-Self-managed Network Outpost Sovereign (Non-Gov)-Azure Deployment
Connect, Deploy & Configure-Wiz Outpost-FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Cloud & Registry Connectors FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Kubernetes Deployments FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Wiz Admission Controller FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Wiz Broker FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Wiz CLI FAQ
Connect, Deploy & Configure-Wiz Outpost-FAQ-Wiz Outpost FAQ

Troubleshooting-Access & Authentication-Code Mismatch Error Message when Setting Up MFA
Troubleshooting-Access & Authentication-Email Address Field is Empty or Incorrect
Troubleshooting-Access & Authentication-How to Generate HAR Files
Troubleshooting-Access & Authentication-How to Capture and Decode a SAML Response
Troubleshooting-Access & Authentication-Local User Forgotten Password
Troubleshooting-Access & Authentication-Local User Lost or Wants to Reconfigure MFA
Troubleshooting-Access & Authentication-MFA Invalid or Expired Code Error Message when Setting Up MFA
Troubleshooting-Access & Authentication-Missing Permissions for a Page or Action in the Wiz Portal
Troubleshooting-Access & Authentication-SSO User Lost or Wants to Reconfigure MFA
Troubleshooting-Access & Authentication-SSO Users Cannot Log in to the Wiz Portal: Email not in the Tenant Allowed Domains
Troubleshooting-Access & Authentication-SSO Users not Listed on the User Management Page
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Bad SAML Request
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Audience Restriction Error
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: custom:saml_groups Error
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: empty update path Error
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Error Decrypting EncryptedAssertion
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Invalid relayState or samlResponse
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Invalid SAML Metadata
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: SAML Response Signature is Invalid
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Invalid Thumbprint
Troubleshooting-Access & Authentication-Unable to Log in to the Wiz Portal: Responses Must Contain Exactly One Assertion
Troubleshooting-Access & Authentication-Unable to See Data or Use the Wiz Portal
Troubleshooting-Access & Authentication-Unable to See Data or Use the Wiz Portal: RBAC Error
Troubleshooting-Access & Authentication-Usernames in Portal Do not Show First and Last Name
Troubleshooting-Access & Authentication-Wiz for Gov User Prompted to Authenticate to app.wiz.io
Troubleshooting-AWS Connector
Troubleshooting-AWS Connector-Connector is Missing Permissions for a Specific AWS Service or Operation
Troubleshooting-AWS Connector-Connector is Missing Permissions for Workload Scan Cleanup
Troubleshooting-AWS Connector-Connector is Unable to Assume AWS IAM Role
Troubleshooting-AWS Connector-Update of resource types is not permitted Error When Trying to Update CloudFormation Stack Set
Troubleshooting-AWS Connector-CloudFormation Stack Update Fails with EntityAlreadyExists Error
Troubleshooting-Azure Connector
Troubleshooting-Azure Connector-Verify the Wiz Azure App
Troubleshooting-Azure Connector-Verify Azure Connector Scope and Role Assignments
Troubleshooting-Azure Connector-Unable to run installation script in Azure Cloud Shell
Troubleshooting-Azure Connector-Not All Entra ID Users Appear in Wiz
Troubleshooting-GCP Connector
Troubleshooting-GCP Connector-Connector is Missing Permissions for a Specific GCP Service or Operation
Troubleshooting-GCP Connector-Installation Script Permission Failure in GCP Cloud Shell
Troubleshooting-GCP Connector-Invalid Project Number Error While Running GCP Installation Script
Troubleshooting-Deployment Scripts
Troubleshooting-Deployment Scripts-Troubleshoot Terraform Deployment Issues
Troubleshooting-Deployment Scripts-Update an Existing Terraform Deployment
Troubleshooting-Deployment Scripts-Find Your Existing Terraform Configuration
Troubleshooting-Deployment Scripts-Recover a Lost Terraform State File
Troubleshooting-Deployment Scripts-inherit_errexit: invalid shell option name Error Message when Running a Deployment Script
Troubleshooting-Deployment Scripts-Troubleshoot Terraform Deployment Issues
Troubleshooting-Docs & Training
Troubleshooting-Docs & Training-Failed to Verify Browser When Accessing Wiz Docs
Troubleshooting-Docs & Training-SSO Users Cannot Access the Academy Training
Troubleshooting-HCP Terraform Connector
Troubleshooting-HCP Terraform Connector-Failed HCP Terraform Connector Scan
Troubleshooting-HCP Terraform Connector-Stuck or Timed Out HCP Terraform Wiz Task
Troubleshooting-HCP Terraform Connector-Wiz Run Task Verification Failure in Terraform Enterprise
Troubleshooting-IDE Extension
Troubleshooting-IDE Extension-IDE Extension is Missing Required Windows Privileges
Troubleshooting-Integrations, Actions, & Automations
Troubleshooting-Integrations, Actions, & Automations-Integration is Stuck in 'Initializing' or 'Inactive' Status
Troubleshooting-Integrations, Actions, & Automations-Proxy Errors in Wiz Add-on for Splunk
Troubleshooting-Integrations, Actions, & Automations-Wiz Data Not Appearing in 3rd-Party Integrations
Troubleshooting-Kubernetes Deployments
Troubleshooting-Kubernetes Deployments-Context deadline exceeded
Troubleshooting-Kubernetes Deployments-HTTPS proxy (tcp: remote error, tls: handshake failure)
Troubleshooting-Kubernetes Deployments-i/o timeout error
Troubleshooting-Kubernetes Deployments-TLS: server selected unadvertised ALPN protocol
Troubleshooting-Kubernetes Deployments-TLS: unknown certificate authority
Troubleshooting-Kubernetes Deployments-Duplicate clusters shown with matching External IDs
Troubleshooting-Kubernetes Deployments-Verifying creds for Complete Kubernetes Service Account via API returns 'Bad Request'
Troubleshooting-Pricing & Licensing
Troubleshooting-Pricing & Licensing-Data Still Shown in Portal Although Subscription has Been Terminated or Expired
Troubleshooting-Pricing & Licensing-Project Folder Has Fewer Billable Units Than Its Individual Projects
Troubleshooting-Pricing & Licensing-Total Billable Units Mismatch: Licenses Page vs. Resource Discovery Script
Troubleshooting-Pricing & Licensing-Total Billing Objects Mismatch: Licenses Page vs. Security Graph and Inventory
Troubleshooting-Registry Connectors
Troubleshooting-Registry Connectors-ACR Connector: Registry Access Restricted by Firewall
Troubleshooting-User Preferences
Troubleshooting-User Preferences-User Preferences Not Synchronized Across Wiz Tenants
Troubleshooting-VCS Connectors
Troubleshooting-VCS Connectors-Connector Fails to Scan Pull Requests
Troubleshooting-VCS Connectors-Failed GitHub App Installation Parameters
Troubleshooting-VCS Connectors-Mismatched GitHub App Permissions
Troubleshooting-VCS Connectors-Missing Scan Findings
Troubleshooting-VCS Connectors-Missing GitHub App Permissions
Troubleshooting-VCS Connectors-Scans are missing from the Wiz portal
Troubleshooting-VCS Connectors-Stuck Pull Request Scan Status
Troubleshooting-Vulnerability Management
Troubleshooting-Vulnerability Management-Duplicate Findings for a Single Resource
Troubleshooting-Vulnerability Management-Findings Generated but File Path or Library not Mentioned in OS Advisory
Troubleshooting-Vulnerability Management-Findings Generated for Serverless Functions After Disabling Manifest File Scanning for the Deploy Phase
Troubleshooting-Vulnerability Management-Findings Generated for Software not Installed on a Windows Machine
Troubleshooting-Vulnerability Management-Incorrect Suggested Fixed Version
Troubleshooting-Vulnerability Management-Incorrect Version Detection of Vulnerable Component
Troubleshooting-Vulnerability Management-Incorrect/Missing Vulnerability Metadata (e.g. CVSS properties)
Troubleshooting-Vulnerability Management-Persistent Finding for a File Path after File Update/Removal and VM Rescan
Troubleshooting-Vulnerability Management-Unable to Install Wiz-Recommended Fix Version or Latest Version Package
Troubleshooting-Vulnerability Management-Unable to Locate Flagged Vulnerable Components on a Resource
Troubleshooting-Vulnerability Management-Unable to Locate a User-Specific Path on a Windows Machine
Troubleshooting-Wiz CLI
Troubleshooting-Wiz CLI-Forbidden IP address Error Message When Authenticating to Wiz CLI
Troubleshooting-Wiz CLI-Wiz CLI Fails to Authenticate
Troubleshooting-Wiz CLI-Wiz CLI is Missing Required Windows Privileges
Troubleshooting-Wiz CLI-Wiz CLI SAST Scan Fails When Git is Not Available
Troubleshooting-Wiz Issues
Troubleshooting-Wiz Issues-Persistent Wiz Issue After Remediation and Rescan
Troubleshooting-Wiz Issues-Wiz Issue Generated for a Wiz Service Account
Troubleshooting-Wiz Outpost
Troubleshooting-Wiz Outpost-Registry or Service Access Blocked on Wiz Outpost Clusters
Troubleshooting-Wiz Outpost-Self-managed Network Outpost AKS Clusters Show Outdated Node Image Versions
Troubleshooting-Wiz Projects
Troubleshooting-Wiz Projects-Validation failed Error When Saving or Editing a Project
Troubleshooting-WizOS
Troubleshooting-WizOS-Network Connectivity Problem when Trying to Install a WizOS Package

Integrations-Integrations Overview
API & Graph Queries-Overview
API & Graph Queries-Getting Started with Wiz API
API & Graph Queries-Getting Started with Wiz API-Introduction to Wiz API
API & Graph Queries-Getting Started with Wiz API-Using the Wiz API
API & Graph Queries-Getting Started with Wiz API-Generate an API Token with Device Code Flow
API & Graph Queries-Getting Started with Wiz API-APIs and Required Permission Scopes
API & Graph Queries-Getting Started with Wiz API-Permission Scopes and Allowed APIs
API & Graph Queries-Developer Tools & Resources
API & Graph Queries-Developer Tools & Resources-Wiz SDK for Python
API & Graph Queries-Developer Tools & Resources-Python SDK Module Reference
API & Graph Queries-Developer Tools & Resources-Integration APIs
API & Graph Queries-Developer Tools & Resources-Postman Collection
API & Graph Queries-Developer Tools & Resources-Handling API Errors
API & Graph Queries-Developer Tools & Resources-Deprecated GraphQL APIs
API & Graph Queries-API Use Cases
API & Graph Queries-API Use Cases-Bulk Invite New Users
API & Graph Queries-API Use Cases-Manage Projects
API & Graph Queries-API Use Cases-Create SAML Group Mappings
API & Graph Queries-API Use Cases-Get Cloud Configuration Findings
API & Graph Queries-API Use Cases-Get Issues
API & Graph Queries-API Use Cases-Get System Health Issues
API & Graph Queries-API Use Cases-Get VM Hostnames
API & Graph Queries-API Use Cases-Get Vulnerabilities
API & Graph Queries-API Use Cases-Identify Controls Near Issue Limits
API & Graph Queries-API Use Cases-Pre-provision SAML users from CSV
API & Graph Queries-API Use Cases-Delete SAML Group
Security & Trust
Security & Trust-Overview
Security & Trust-Architecture, Controls and Principles
Security & Trust-Architecture, Controls and Principles-AI Principles
Security & Trust-Architecture, Controls and Principles-Cloud Security Principles
Security & Trust-Architecture, Controls and Principles-Data Protection Principles
Security & Trust-Architecture, Controls and Principles-Runtime Sensor Security Principles
Security & Trust-Architecture, Controls and Principles-System Architecture
Security & Trust-Architecture, Controls and Principles-Business Continuity and Disaster Recovery
Security & Trust-Architecture, Controls and Principles-Data Retention
Security & Trust-Architecture, Controls and Principles-Shared Responsibility Model
Security & Trust-Securing Your Wiz Tenant
Security & Trust-Third Parties
Security & Trust-Third Parties-AI Providers
Security & Trust-FAQ
Private Previews
Private Previews-Add Custom TI Source
Private Previews-Security Insights for Bug Bounty Platforms
Private Previews-Granular Issue Status Permissions (Ignore Action)
Private Previews-Connect to Akamai
Private Previews-Connect to AWS Security Lake
Private Previews-Connect to Microsoft Power Platform (Copilot Studio)
Private Previews-Connect to IBM Cloud
Private Previews-Connect to IBM Cloud-Update Connector Permissions in IBM Cloud
Private Previews-Connect to IBM Cloud-Required Permissions for IBM Cloud Connectors
Private Previews-Connect to Nexus
Private Previews-Connect to OpenStack
Private Previews-Connect to OpenStack-Update Permissions
Private Previews-Connect to OpenStack-Required Permissions for OpenStack Connectors
Private Previews-Connect to Private Azure OpenAI
Private Previews-Connect to Salesforce and Agentforce
Private Previews-Data Scanning for Azure File Share
Private Previews-Data Scanning for CosmosDB
Private Previews-Exclude Workloads from Scanning
Private Previews-Windows Sensor-based Workload Scanner
Private Previews-Outpost Lite: DB Scanning
Private Previews-Pentest Findings
Private Previews-Remediation & Response via Outpost Lite
Private Previews-Remediation & Response via Outpost Lite-Deploy R&R to AWS with Outpost Lite
Private Previews-Remediation & Response via Outpost Lite-Custom Response Actions
Private Previews-Remediation & Response via Outpost Lite-Revertible Custom Response Actions
Private Previews-Remediation & Response via Outpost Lite-Migrate to R&R via Outpost Lite
Private Previews-Remediation & Response via Outpost Lite-Troubleshoot R&R via Outpost Lite
Private Previews-1-click Sensor Install for Outpost Lite
Private Previews-Scan Public Personal Code Repositories
Private Previews-Sensor for Google Cloud Run
Private Previews-Sensor for AWS Lambda Functions
Private Previews-Sensor Install using Wiz AC
Private Previews-Sensor for Windows Workloads (Atomic Red Team)
Private Previews-Wiz Threat Services
Private Previews-Wiz Threat Services-Managed Detection and Response (MDR)
Private Previews-AI Workload Analysis
Private Previews-Ingest GitHub Secrets Findings
Private Previews-On-demand Container Image Scanning
Private Previews-Workflow Variable Governance
```
