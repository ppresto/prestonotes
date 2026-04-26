# Customer Notes — Account Summary tab (mutations)

> Part of the **Customer Notes** Google Doc mutation reference pack. Hub: [README.md](./README.md).

## Fact Extraction Categories

When analyzing transcripts and notes, extract structured facts into these categories:

- `goals_mentioned`: explicit goals stated by the customer, plus synthesized strategic goals from repeated challenge/workflow themes when explicit goals are sparse
- `deal_risks_mentioned`: deal/commercial risks to success (budget, executive alignment, sponsor/champion traction, competitive/tool-fit, timeline slip, procurement confidence)
- `upsell_signals`: expansion or upsell opportunities
- `challenges_mentioned`: each with `description` and `category` (Technical|Process|Business|Other)
- `contacts_mentioned`: each with `name`, `title`, `role` (champion|blocker|user|economic_buyer|other)
- `tech_stack`: tools per category — `csp`, `platforms`, `idp`, `devops_tools`, `security_tools`, `aspm_tools`, `ticketing_tools`, `languages`
- `use_cases_requirements`: explicit customer use cases/requirements that must be met across the account lifecycle
  - Keep clear bullets of requirements, acceptance criteria, and "must-have" outcomes.
  - Do not place workflow/process narratives here.
- `workflows`: workflows and processes
  - A workflow/process is a sequence of tools/teams/steps used to achieve an outcome.
  - Capture workflows even with partial evidence; enrich over time as additional details appear.
  - For high-impact workflows with rich evidence, write a detailed narrative (not arrow shorthand). No fixed sentence cap.
  - Every workflow entry must include a stable workflow name from customer language.
  - Include trigger, tools/scripts, team handoffs, outputs/artifacts, bottlenecks, and business/security impact.
  - Include time/resource context when available: wait time between steps, queue/approval delays, manual effort, hours/days/weeks impact.
  - Include security-gap context when available: missing owner mapping, prioritization gaps, coverage blind spots, remediation friction.
  - These may be reconstructed across multiple calls when each call fills a different gap.
  - When additional evidence appears for an existing named workflow, enrich that workflow narrative; do not drop prior validated detail.
  - Use the Wiz solution lens to map current-state workflow pain to feasible improved-state outcomes.
- `company_details`: company-level facts (size, industry, etc.)
- `next_steps`: action items from the call
- `account_motion_metadata`:
  - `stakeholders`: `exec_buyer`, `champion`, `technical_owner`
  - `outcome_metrics`: `sensor_coverage_pct`, `critical_issues_open`, `mttr_days`, `monthly_reporting_hours`
- `deal_stage_tracker` (section `Deal Stage Tracker`):
  - Maintain per-SKU lifecycle rows in format:
    - `SKU | Stage | Stage First Seen | Date Quality | Renewal Date | Status | Notes & Evidence`
  - Required default rows when empty:
    - `cloud | pre-sale | <first-seen date or current date> | verified/unverified |  | active | bootstrap default`
    - `sensor | not-active |  | unverified |  | inactive | no active opportunity`
    - `defend | not-active |  | unverified |  | inactive | no active opportunity`
    - `code | not-active |  | unverified |  | inactive | no active opportunity`

### Extraction Rules

- Only include items explicitly stated in sources.
- Do not infer or guess.
- Evaluate every templated section/field/subfield on each run and classify each as: `updated`, `unchanged`, `missing_evidence`, or `blocked_by_policy`.
- For tech_stack, only include tools the customer confirmed they actively use.
- For `account_motion_metadata`, only set controlled values listed above.
- Strict metadata rule: `exec_buyer`, `champion`, and `technical_owner` must only be updated when explicitly stated in that day's source evidence (`explicit_statement=true` in mutation payload). Do not infer from role/title hints.
- Contacts hygiene: only write person contacts in `Name - role/context` format; never place goals/challenges/use-case statements in `Contacts`.

#### Contacts — evidence and mutation shape (LLM; all customers)

These rules exist so **Update Customer Notes** produces `contacts.free_text` mutations **inside the normal Step 8 JSON** — the same path for `_TEST_CUSTOMER` and for every production account (no fixture-only scripts, no throwaway `/tmp` plans as the source of truth).

1. **Names must appear in source text.** Prefer verbatim spellings from **in-lookback transcripts**. If Extract has written **`call-records/<call_id>.json`** for that call, you may also cite **`participants[].name`** and roles from **`participants[].role`** when they match the transcript. Do **not** invent people who appear only in generic action-item placeholders (e.g. a bare `"SE"` owner with no named person).
2. **Use `stakeholder_signals[]` for nuance, not for copying enums into the doc.** Translate `signal` values into plain customer-facing language in the **bullet** (e.g. champion transition, sponsor stepping in). Keep enum tokens and internal field paths in **`reasoning` only**.
3. **Mutation payload:** `section_key`: `contacts`, `field_key`: `free_text`, `action`: `append_with_history`, `new_value`: one line `Name - role/context; short factual tail`, `theme_key`: `contact:<kebab-slug-from-display-name>`, `evidence_date`: ISO **call** date for the strongest citation (transcript header or record `date`).
4. **Multi-call accounts:** Merge facts across calls in **one bullet per person** when the doc does not already list them separately; otherwise append once per distinct role change the customer cares about, with the **latest** material `evidence_date`.
5. **Dedupe against `read_doc`:** If an active entry already covers the same person (normalize whitespace and case for comparison), skip with an explicit skip reason or enrich only when new evidence adds a **material** fact (departure date, title change), never for wording-only churn.

- Never append housekeeping/meta text in customer-facing fields (for example: "Upsell Path item", "onboarding issue", "resolved xyz").
- Keep evidence metadata in audit logs and mutation metadata only; do not render evidence markers/dates inline in customer-facing GDoc text.

### Section Intent Rules

- `Goals`: strategic customer outcomes/use-case goals, immutable once written.
- `Risk`: deal/commercial risks only (not solvable technical backlog detail).

#### Exec Account Summary — forbidden meta (Goals, Risk, Upsell Path)

These three fields are **customer- and deal-facing**. Do **not** append bullets that are really **about the notes pipeline, the agent, or validation**:

- **Forbidden:** Phrases about **internal tooling or QA** — e.g. “internal check”, “parser”, “label-matching”, “template”, “H3 headings parse correctly”, “validation run”, “UCN”, “mutation”, “schema”, “read JSON”.
- **Forbidden:** **Ingestion / source housekeeping as if it were deal risk** — e.g. “no new transcripts since …” **as the main point of a Risk line** (that belongs in **audit log** or **planner notes**, not exec Risk). If deal risk truly depends on stale intel, say it in **customer-facing** terms (e.g. “slow feedback loop from customer side”) only when **customer-observable**, not “our transcript bundle is old.”
- **Allowed in `reasoning` / audit only:** evidence dates, tool names, and “why we proposed this” — **not** copied verbatim into Goals/Risk/Upsell bullets.

If a prior run wrote meta lines into the doc, fix them with an approved **`replace_field_entries`** cleanup pass or a targeted user edit — do not treat them as durable account truth.
- `Challenge Tracker`: canonical source for operational/technical execution issues and status.
- `Challenges` section is intake-only for manual notes/bullets; any active bullet must be promoted to tracker and then removed from bullets.
- `Use Cases / Requirements`: explicit customer requirements across lifecycle stages, separate from process narratives. Each bullet should read as a deal-breaker requirement: who must get what outcome, why purchase fails without it.
- `Workflows / Processes`: process narratives and coverage gaps.
- `Cloud Environment` fields:
  - `CSP/Regions`: cloud providers, regions, org/landing-zone scope, rough % split only. No meeting notes, pipeline narratives, or session context.
  - `IDP used for SSO`: identity provider and SSO **for Wiz access** only (e.g. "Okta for Wiz SSO"). Do **not** park generic CI/CD or SIEM products here.
  - `Sizing`: workload/sensor/VM/cluster/node counts, quotes, % coverage only. CI/CD pipelines, IR stacks, and tool chains belong in Workflows or Cloud tools.

#### Cloud Environment — `tools_list` routing (rubric-first; no vendor catalog)

**Do not** maintain or depend on an exhaustive list of product names (GitHub, Splunk, etc.). **Default (Option 1):** infer the correct `cloud_environment` **`field_key`** from **what the tool does in the customer’s narrative**, using this rubric:

| `field_key` | Route here when the transcript describes… |
| --- | --- |
| `platforms` | Cloud runtimes / compute shapes the estate runs on (K8s, serverless, VM fleets) **as infrastructure**, not a vendor security console. |
| `devops_vcs` | Source control, **CI/CD**, build pipelines, artifact/registry integration, **shift-left in the pipeline** when it is “repos + builds”, not “SOC tier-1 console”. |
| `security_tools` | **SOC-facing** controls: SIEM, log analytics, EDR/CWPP consoles, CSPM **as the security operations surface**, secrets vaults **as enforced controls**, “we send detections to …”, “existing SIEM”, IR platforms. |
| `aspm_tools` | **Application security in SDLC**: SAST, SCA, IaC policy in PRs, dependency scanning **as product categories** — not the whole GitHub product in ASPM unless the talk is specifically code scanning / supply chain in dev. |
| `ticketing` | Work management / CMDB routing / alert-to-ticket (Jira, ServiceNow, Linear **when used as ITSM/work tracking**). |
| `languages` | Primary implementation languages when stated as stack facts. |

**Ambiguity:** many vendors span two buckets (e.g. observability + security). Prefer **the role in the quoted workflow** over the vendor’s marketing category. If still ambiguous after applying the rubric to transcript evidence → **Option 2 (low-confidence backup):** at most **one** bounded public lookup (vendor docs or neutral summary) to disambiguate **category only** — no customer-sensitive strings in the query; cache the conclusion in `reasoning`, not as unsourced claims in the customer-facing `detail` line. If lookup is unavailable (offline, blocked) or still ambiguous, **omit** `add_tool` or use `update_tool_detail` on an existing line after operator confirmation — do not guess a section.

**Duplicates:** use `read_doc` / Step 3 tool keys under each `field_key`; skip `add_tool` if the same product is already listed (normalize trivial variants).

- `Deal Stage Tracker`: maintain per-SKU lifecycle stages, first-seen date, date quality, and renewal placeholders for manual editing and lifecycle continuity.
- `Accomplishments`: completed/validated outcomes moved from prior goals.
- `Upsell Path`: **SKU- or product-line-first** bullets, then a one-line value story. **Allowed lead-ins** (first token before `—`): `Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz Code`, `ASM`, **`Wiz DSPM`**, **`Wiz CIEM`**. Use **separate bullets** when transcripts name distinct expansion threads (e.g. sensitive-data / PII / data-classification posture vs cloud identity / entitlements / IAM) — do not fold those into a single generic `Wiz Cloud` line when the dialogue treats them as different solution fits. Pain-to-product hints in config: `prestonotes_gdoc/config/sections/025-exec_account_summary.yaml` → `update_from_evidence.upsell_mapping` (e.g. sensitive data → DSPM, identity → CIEM). **Deal Stage Tracker auto-motion** (`advance_deal_stage_from_upsell`) still keys only on **`cloud|sensor|defend|code`** substrings inside `upsell_path` text — DSPM/CIEM bullets are exec-facing truth regardless; add or retain a `Wiz Cloud` / `Wiz Sensor` / etc. line when you also need that automation to fire.

### Ingestion Mode

- **Full-history synthesis pass**: load all historical notes/transcripts available for the customer to identify durable trends and strategic themes.
- **Daily-delta pass**: load the newest notes/transcripts to capture current changes.
- Build mutations from the combined view (durable trend + latest delta), not from latest notes alone.

### Company Overview Exception

For `company_overview` only, if transcripts/notes do not provide enough signal, you may use a brief external lookup (customer website, public sources, reviews) to fill a concise 1-3 sentence overview. Keep this overview short and factual; do not use external research for other sections. Write as plain paragraph text (not bullets), 1-4 brief sentences.

---

## Challenge lifecycle ↔ Challenge Tracker parity (mandatory for UCN)

The append-only JSON journal under **`MyNotes/Customers/<Customer>/AI_Insights/challenge-lifecycle.json`** and the Google Doc **Challenge Tracker** table are **two views of the same journey**. If you have enough evidence to change one, you must keep the other aligned in the **same approved `write_doc` batch** (or explicitly document why the table row is intentionally unchanged).

### Anchor convention (machine-checkable)

For every persisted lifecycle **`challenge_id`**, ensure the corresponding tracker row includes this exact token (challenge cell and/or **Notes & References**):

`[lifecycle_id:<challenge_id>]`

Example: `[lifecycle_id:splunk-renewal-planning-q2]` at the end of **Notes & References** after human-readable notes.

When **`write_doc`** is called with MCP argument **`customer_name`** (forwarded as **`--customer-name`** to `prestonotes_gdoc/update-gdoc-customer-notes.py`):

- If the lifecycle file has ids but **no** row contains `[lifecycle_id:` → the writer prints a **stderr warning** (migration / legacy docs).
- If **any** anchor exists → **every** lifecycle id must have a matching anchor or the write **fails** with `LIFECYCLE_PARITY_FAIL` (prevents partial sync).
- Emergency bypass: **`--skip-lifecycle-parity-check`** on the write CLI (MCP: omit `customer_name` or add a future MCP flag if needed).

**Orchestrator expectation:** Default UCN runs pass **`customer_name`** into **`write_doc`** whenever the customer is known so drift is caught before the Doc goes stale again.

---

## Challenge Decision Model

Use this model whenever proposing `challenge_tracker` changes:

1. **Readability gate first** (hard filter):
   - Exclude unreadable/non-human artifacts before analysis (for example image/base64 payloads, markdown table debris, formatting-only fragments).
   - If content cannot be meaningfully read, do not treat it as challenge evidence.
2. **AI decides challenge inclusion:**
   - From readable content plus historical context, decide whether each candidate is a true challenge.
   - Do not require rigid keyword-only or intent-only gates.
3. **AI generates challenge title:**
   - Generate a short, meaningful title (not a clipped prefix).
   - Avoid bullets, numeric prefixes, and markdown/table syntax in title text.
4. **Dedupe against current doc before add:**
   - Compare against existing `challenge_tracker` rows already in the Google Doc.
   - If semantically similar challenge already exists, prefer `update_table_row` and append new evidence/details to notes.
   - Only use `add_table_row` when net-new.
   - This semantic dedupe/routing happens in planner/section logic before write.
5. **No hard volume caps:**
   - Do not enforce per-day row count caps.
   - Sensitivity can be tuned via profile (`major|medium|minor`) in section policy; this affects strictness, not hard limits.
6. **Writer boundary:**
   - `update-gdoc-customer-notes.py` is a write engine only (schema validation + deterministic apply/report).
   - Do not place semantic classification/dedupe policy in the writer.

---

### Deal Stage Tracker — SKU signal mapping

TASK-050 §E: on every approved UCN write, the writer scans each applied `exec_account_summary.upsell_path` mutation for SKU references and promotes the corresponding Deal Stage Tracker row. This happens after the mutation plan is applied and is emitted as an additional `advance_deal_stage_from_upsell` change — the planner does not need to pre-compute the row update; it just needs to keep the upsell line factual.

**Canonical vocabulary** (shipped in `prestonotes_gdoc/update-gdoc-customer-notes.py`):

- `COMMERCIAL_SKUS = {"cloud", "sensor", "defend", "code"}` — only these four SKU keys participate in auto-promotion. ASM stays manual.
- `DEAL_STAGE_POV_PHRASES = ("pov", "proof-of-value", "proof of value", "timeboxed", "pilot", "poc kicked off", "pov kicked off")`
- `DEAL_STAGE_WIN_PHRASES = ("po signed", "po issued", "purchase order", "enterprise sku purchased", "purchased", "contract signed", "closed-won", "closed won")`
- `ALLOWED_DEAL_STAGE_VALUES = {"not-active", "discovery", "pov", "tech win", "procurement", "win"}` — `discovery` is the default floor for any SKU cited in `upsell_path`.

**Promotion rules (the writer applies these in order of stage, keeping the highest stage whose evidence fires):**

| Evidence in the applied `upsell_path` line | Target stage |
|---|---|
| Any SKU reference + no POV / no win phrase hit | `discovery` (advance from `not-active`) |
| Any SKU reference + POV phrase hit | `pov` |
| Any SKU reference + win phrase hit | `win` |

**Row-level side effects the writer also performs:**

- `activity` column flips to `active`.
- `reason` (the Notes & References cell) is rewritten to `<target-stage> evidence in upsell_path (<call-date>)`, using the latest ISO date found in the upsell_path line (fallback: today). Existing bootstrap phrases (`bootstrap default`, `no active opportunity`) are replaced; other existing narrative is appended with `; <reason>`.
- **Rank guard:** a row already at a higher stage is never demoted. If the row is already at `pov`, an `upsell_path` line that only matches `discovery` is a no-op.

**Skipped / manual cases:**

- Rows whose `challenge` key is not one of `COMMERCIAL_SKUS` are untouched (e.g. a manually seeded ASM row).
- If no `upsell_path` mutations applied this run, Deal Stage Tracker is not touched — use `update_table_row` manually per § Mutation Actions Reference when you need a one-off stage change.

**TASK-072 deterministic planner contract (required in UCN plan):**

- Add `planner_contract.deal_stage.expected_skus` (`cloud|sensor|defend|code`) for SKUs expected to move this run.
- For each expected SKU, provide one trigger path:
  - `upsell_auto` via an `exec_account_summary.upsell_path` line containing a recognized token, or
  - explicit `deal_stage_tracker` table mutation (`update_table_row` / `add_table_row`), or
  - `no_change_with_reason` with evidence-backed reason.
- Validate with `scripts/ucn-planner-preflight.py`; if `deal_stage_trigger_missing:*` appears, do not write.

---
