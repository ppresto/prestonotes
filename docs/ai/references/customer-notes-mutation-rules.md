# Customer Notes Mutation Rules

This reference file contains all mutation logic, schemas, and quality gates for the `Update Customer Notes` playbook. The playbook references this file instead of embedding these rules inline.

---

## Daily Activity Logs — allowed AI prepend

- **Section:** `daily_activity_logs` / field `free_text`.
- **Action:** `prepend_daily_activity_ai_summary` only (see `docs/ai/references/daily-activity-ai-prepend.md`).
- **Behavior:** Inserts `heading_line` (styled as Google Docs **HEADING_3**) plus formatted `body_markdown` on the **Daily Activity Logs** tab (after **Anchors** when present; date-ordered among dated blocks). No deletes, no in-place edits to existing paragraphs.
- **`Update Customer Notes` (required):** Each run must compare transcript meetings in the active lookback to existing Daily Activity content (from the latest `read` JSON). For **each meeting not already represented** (normalized heading key would not duplicate an existing block), add **`prepend_daily_activity_ai_summary`** to the **same** mutation plan as other UCN changes so one approved `write` applies everything. If there are no gaps, omit prepend mutations and say so in the plan summary. A mutations file that contains **only** prepend actions still bypasses planner key-field coverage; mixed files must still satisfy key-field `no_evidence` / change coverage.

---

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
- Cloud Environment detail hygiene: keep each tool entry to one line by default (max two lines only for materially important context); when new validated usage context is learned, prefer `update_tool_detail` on the existing tool line.
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
  - `IDP used for SSO`: identity provider and SSO for Wiz access only (e.g. "Okta for Wiz SSO"). AISPM, webhook, or GitHub content belongs in Workflows or Use cases.
  - `Sizing`: workload/sensor/VM/cluster/node counts, quotes, % coverage only. CI/CD pipelines, IR stacks, and tool chains belong in Workflows or Cloud tools.
- `Deal Stage Tracker`: maintain per-SKU lifecycle stages, first-seen date, date quality, and renewal placeholders for manual editing and lifecycle continuity.
- `Accomplishments`: completed/validated outcomes moved from prior goals.
- `Upsell Path`: SKU-first bullets using one of `Wiz Cloud|Wiz Sensor|Wiz Defend|Wiz Code|ASM`, then one-line value story.

### Ingestion Mode

- **Full-history synthesis pass**: load all historical notes/transcripts available for the customer to identify durable trends and strategic themes.
- **Daily-delta pass**: load the newest notes/transcripts to capture current changes.
- Build mutations from the combined view (durable trend + latest delta), not from latest notes alone.

### Company Overview Exception

For `company_overview` only, if transcripts/notes do not provide enough signal, you may use a brief external lookup (customer website, public sources, reviews) to fill a concise 1-3 sentence overview. Keep this overview short and factual; do not use external research for other sections. Write as plain paragraph text (not bullets), 1-4 brief sentences.

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

## Historical Synthesis Mode (for backfill runs over old notes)

When processing historical transcripts in chronological batches, use this sequence:

1. Identify current lifecycle phase from evidence:
   - `pre-sale`, `pov`, `procurement`, `onboarding`, `operationalizing`, `expansion`, `renewal`.
2. Build a **phase timeline** before generating mutations:
   - initial-deal drivers (why buy),
   - implementation blockers,
   - operationalization outcomes,
   - expansion signals.
3. Promote only durable signals into exec summary:
   - `Goals`: strategic outcomes/use-case goals,
   - `Risk`: highest **deal/commercial** risks,
   - `Upsell Path`: SKU-first story tied to customer-stated outcomes.
4. Use recency weighting:
   - Newer evidence can supersede older assumptions; do not keep stale claims active.
5. Use status transitions:
   - If evidence says an issue is fixed/no longer active, update table status to `Resolved` or `Closed` (closed rows are removed and logged).
6. Apply stakeholder weighting:
   - If the same theme is raised by `exec_buyer`, CISO/VP-level leaders, or primary champion, elevate that theme in goal/risk prioritization.
7. Preserve first-deal baseline:
   - Keep a persistent view of initial deal drivers; do not let newer implementation details erase foundational why-buy signals.
8. Process-mining and workflow gap analysis (allow-based):
   - Detect multi-step operational processes from bullets, comma-separated run-ons, or transcript dialogue.
   - Trigger cues increase confidence but are not enough by themselves.
   - Before proposing a workflow change, verify process semantics in source text:
     - linked actions in sequence,
     - actor/handoff or ownership transition,
     - output/outcome or downstream dependency.
   - When a repeated process pattern is found, you may propose it in `workflows.free_text` unless a semantically equivalent entry already exists.
   - Include explicit tools/teams/custom scripts when present.
   - Compare each workflow's current-state flow to prior runs to detect drift.
   - For each major workflow, identify security coverage/ownership/context gaps and promote:
     - active execution gaps -> `challenge_tracker`,
     - recurring strategic gap themes -> `exec_account_summary.top_goal`,
     - commercial/timeline confidence impact -> `exec_account_summary.risk`,
     - clear solution-fit opportunities -> `exec_account_summary.upsell_path` with allowed SKU token.
   - Keep `no_evidence` valid when process signal is weak or ambiguous.
9. Stage timeline detection:
   - Detect stage milestones from notes/transcript titles, section headers, and discussion text (for example: POV, procurement, onboarding, expansion, renewal).
   - Record first-seen stage changes in `deal_stage_tracker.free_text` rows per SKU.
   - If no explicit date exists, infer best date from context and mark as `unverified`.
   - Never remove user-edited stage rows without explicit contradictory evidence.
   - Named-workflow allow-trigger (generic):
     - If evidence contains a recurring named process and clear sequential steps with ownership and outcome context, propose one workflow/process mutation and optionally one new `Goals` and/or `Risk` candidate (append-only, no rewrites).

---

## Mutation Actions Reference

| Strategy (from config) | Allowed Actions |
|---|---|
| `append_with_history` | `append_with_history`, `flag_for_review` |
| `update_in_place` | `update_in_place`, `set_if_empty` |
| `set_if_empty` | `set_if_empty` |
| `tools_list` | `add_tool`, `update_tool_detail`, `remove_tool_suggestion` |
| `free_text` | `append_with_history` |
| table (`challenge_tracker`) | `add_table_row`, `update_table_row` |
| special (`exec_account_summary.top_goal`) | `move_to_accomplishments` |
| special (see below) | `replace_field_entries` — **replace entire bullet list** for that field with `new_values` (array of strings). **Routine `Update Customer Notes`** should use this **only** for user-approved consolidation. **`Run Seeded Notes Replay` Step 9 (post-seed synthesis)** may use it broadly for cleanup: exec summary themes, **deduped/aggregated contacts**, consolidated **use cases** and **workflows**, **Cloud Environment** fields (CSP/Regions, IDP, Sizing), in addition to Goals/Risk/Upsell. Same `evidence_date` rules as other mutating actions. Empty `new_values` clears the field’s bullets. **Allowed targets:** `exec_account_summary` (`top_goal`, `risk`, `upsell_path`), `cloud_environment` (`csp_regions`, `idp_sso`, `sizing`), `contacts` (`free_text`), `use_cases` (`free_text`), `workflows` (`free_text`). |
| planner-only marker | `no_evidence` |

## Mutation JSON Schema

```json
{
  "mutations": [
    {
      "section_key": "string",
      "field_key": "string (omit for table actions)",
      "action": "one of the allowed actions above",
      "new_value": "string (for append/update/set actions)",
      "target_value": "string (for flag_for_review, update_table_row, move_to_accomplishments)",
      "tool_key": "string (for tool actions — lowercase_underscores)",
      "display_name": "string (for add_tool)",
      "detail": "string (optional, for add_tool or update_tool_detail, max 60 chars)",
      "reasoning": "brief explanation",
      "theme_key": "stable semantic key for duplicate control (required for llm-first section outputs)",
      "source": "transcript",
      "evidence_date": "YYYY-MM-DD (required for mutating actions)",
      "row": {
        "challenge": "string",
        "date": "YYYY-MM-DD",
        "category": "Technical|Process|Business|Other",
        "status": "Open|In Progress|Resolved|Closed|Needs Validation",
        "notes_references": "string"
      }
    }
  ]
}
```

---

## Core Mutation Rules

1. Never delete or replace existing content. Only append or flag.
2. Skip mutations where the field already contains the same value.
3. For `append_with_history` fields: add new values; flag old values with `flag_for_review` if they were deprioritized or achieved.
4. For `tools_list` fields: only `add_tool` for confirmed active tools; keep detail strings under 60 chars; never add duplicate tools; when a tool already exists and you learn more, use `update_tool_detail` rather than re-adding.
5. For Challenge Tracker: use `add_table_row` for new challenges; `update_table_row` for status changes on existing ones.
5a. For Challenge Tracker near-duplicates: prefer `update_table_row` to merge incremental evidence into `notes_references` instead of adding another row.
6. Be conservative — fewer high-confidence changes beat many uncertain ones.
6a. Evidence is mandatory for all mutating actions:
   - include `evidence_date` (`YYYY-MM-DD`) from transcript/notes;
   - if no evidence exists, do not mutate the field.
7. Treat Challenge Tracker as canonical:
   - if a challenge exists in tracker, do not keep duplicate bullet in `challenges.free_text`;
   - if a challenge appears as a manual bullet/text only, promote it to tracker and remove the bullet.
8. Do not append low-value duplicates:
   - avoid repeating semantically equivalent goals/risks/challenges with minor wording changes.
   - do not rewrite existing `Goals` bullets; if a similar theme already exists, prefer adding/updating a `Challenge Tracker` row.
8a. Canonical-per-theme rule across active sections (`challenge_tracker`, `deal_stage_tracker`, `exec_account_summary`):
   - one active statement/row per `theme_key`;
   - if `theme_key` already exists, update/enrich existing entry instead of adding a new one;
   - rephrased lines without net-new meaning are duplicates and must be skipped.
9. Challenge status policy:
   - `Closed` only with explicit closure evidence.
   - `Resolved` when solved but still useful for historical reporting.
   - `In Progress` when partially improved or uncertain.
   - `Needs Validation` for ambiguous state that requires confirmation on next customer call.
10. Goal synthesis from challenge patterns:
    - Customer-stated goals are weighted highest.
    - If customer-stated goals are sparse and 2+ open/in-progress challenges cluster on one theme, synthesize one strategic `Goals` line when that theme is not already represented.
    - Goals can be written from direct customer/economic-buyer signal even when challenge mapping is not yet complete.
11. Goal completion handling:
    - When evidence indicates a `Goals` line is achieved, use action `move_to_accomplishments` with `section_key=exec_account_summary`, `field_key=top_goal`, and `target_value` equal to the active goal text.
    - Do not edit/reword a written goal in place.
12. Promotion quality hints (non-blocking):
    - If repeated evidence of a named workflow/process exists, prefer proposing a corresponding `workflows.free_text` change.
    - If explicit pre-sales requirements are present, prefer proposing `use_cases.free_text` bullets for those requirements.
    - If repeated challenge themes with stakeholder weight exist, prefer proposing a new `Goals`/`Risk` candidate.
    - Do not force mutations when evidence is weak; `no_evidence` remains acceptable.

---

## Executive Presentation Mode (Step 9 / approved replace)

When running **Step 9 post-seed synthesis** or any approved **`replace_field_entries`** consolidation pass, apply these additional rules on top of the core rules above.

### Recency tiers

| Tier | Window | Treatment |
|------|--------|-----------|
| A | Latest transcript date minus 90 days through today | Highest priority; list first; prefer over conflicting older facts |
| B | 91-365 days old | Keep if still relevant; middle priority |
| C | Older than 365 days | Bottom; tag `[review]` or drop if superseded by A/B evidence |

### Theme-merge rules

- Build a **theme cluster map** before writing final bullets (cluster name to list of merged source bullets).
- Include the map in the approval preview so the user sees what was folded.
- Never silently drop a theme; merge duplicate facts into a richer surviving line.

### Cloud Environment content boundaries

| Field | Allowed | Route elsewhere |
|-------|---------|-----------------|
| CSP/Regions | Cloud providers, regions, org/landing-zone scope, % split | Workflows, Use cases, Challenge Tracker |
| IDP used for SSO | Identity provider + SSO for Wiz only | Workflows or Security tools |
| Sizing | Counts: workloads, sensors, VMs, clusters, nodes, quotes | Workflows or Cloud tools |

For **CSP/Regions** and **Sizing**, each string in `replace_field_entries` / `update_in_place` `new_value` maps to **one Google Doc list item** (bulleted), not a single paragraph block—use one short line per fact.

### Use-case deal-breaker rubric

Each **Use cases / Requirements** bullet must read as a **deal-breaker requirement**: who must get what outcome, and why the purchase fails without it. Cap at ~5-8 bullets unless the user expands. POV packaging lists, SKU bundles, and wish-list items do not belong here; route to Upsell, Workflows, or Discovery.

### Visual hygiene

- No `[SUPERSEDED]` tags in customer-facing Doc text. The writer no longer renders them.
- Dates appear **at the end** of a line as `[YYYY-MM-DD]` only when needed (prefer on `[review]` lines only).
- No leading `[YYYY-MM-DD]` on active lines.

### Detail preservation

When `replace_field_entries` removes old bullets, the mutations JSON (`step9-apply-mutations-*.json`) serves as the audit trail via `reasoning` and `evidence_date` per mutation. Optionally include a "Lines retired from Doc" appendix in the `POST-SEED-SYNTHESIS-*.md` artifact so nothing is lost.

---

## Planner Coverage Guard

Every run must explicitly cover these fields with either a mutating action or `no_evidence`:
- `exec_account_summary.top_goal`
- `exec_account_summary.risk`
- `use_cases.free_text`
- `workflows.free_text`

`no_evidence` entries are planner markers for audit traceability and are not written to the GDoc.

---

## Mutation Quality Gate (must pass before showing to user)

- **Evidence**: each proposed change must cite transcript date(s) and reason.
- **Template completeness**: every schema field must be assessed each run; leave empty only with explicit `missing_evidence` outcome.
- **Section integrity**: no cross-section leakage (risk text cannot contain upsell/path notes, etc.).
- **Use-cases/workflows integrity**:
  - requirement text belongs in `use_cases.free_text`;
  - process narrative belongs in `workflows.free_text`;
  - do not use `->` shorthand in `workflows.free_text`.
- **Risk semantics**: `exec_account_summary.risk` must be deal/commercial risk language; technical backlog belongs in `challenge_tracker`.
- **Exec meta hygiene**: reject any proposed `top_goal` / `risk` / `upsell_path` line that matches **forbidden meta** patterns in § Section Intent → Exec Account Summary — forbidden meta (pipeline, parser, transcript-ingestion housekeeping).
- **Upsell semantics**: every upsell line must include one allowed SKU token (`Wiz Cloud|Wiz Sensor|Wiz Defend|Wiz Code|ASM`).
- **State accuracy**: include lifecycle/status transition when evidence supports it.
- **Value clarity**: every exec-summary change must map to one of:
  - risk reduction,
  - operational efficiency/time saved,
  - compliance/audit improvement,
  - expansion readiness.
- **Duplication control**: same issue should not appear in two canonical places.
- **Theme key discipline**: each AI-authored proposal must include stable `theme_key` so duplicate control is deterministic across runs.

---

## History Ledger Integration

After a successful Google Doc write, `Update Customer Notes` appends one row to `*-History-Ledger.md` using the same evidence discipline as the doc mutations:
- Row columns match the required set in `.cursor/rules/core.mdc` (History Ledger — TASK-007).
- Data is derived from the post-write doc state + applied mutations from this run.
- Empty cells for any column without available data — no fabrication.
- The ledger row is **not** written on rejection or zero-write runs.

---

## Diff Preview Format (for showing changes to user)

Use `+` for adds, `~` for modifications, `-` for removals.

First line: target field. Second line (indented): exact change payload. Optional third line: short reasoning.

```text
+ exec_account_summary.risk
    Runtime telemetry blind spots in EKS reduce confidence in triage.
    reason: Explicitly stated in latest transcript.

~ cloud_environment.security_tools.crowdstrike
    detail: "in use while runtime coverage is expanded"

- challenge_tracker.row["Legacy finding workflow noise"]
    remove row (status -> Closed); moved to audit log
```
