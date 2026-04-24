# Customer Notes — Global mutation mechanics

> Cross-tab rules: schema, actions, quality gate, synthesis modes, ledger, diff preview. Hub: [README.md](./README.md). Account Summary narrative rules: [mutations-account-summary-tab.md](./mutations-account-summary-tab.md).

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
     - clear solution-fit opportunities -> `exec_account_summary.upsell_path` with an **allowed upsell lead-in** (see § `Upsell Path` under Section Intent Rules).
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
- **Upsell semantics**: every upsell line must start with an **allowed lead-in** (`Wiz Cloud`, `Wiz Sensor`, `Wiz Defend`, `Wiz Code`, `ASM`, `Wiz DSPM`, or `Wiz CIEM`) before the value story; prefer **distinct bullets** for DSPM vs CIEM vs core commercial SKUs when transcripts support distinct threads.
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

After a successful Google Doc write, `Update Customer Notes` appends **one schema v3 row** to `*-History-Ledger.md` via MCP **`append_ledger_row`** using the same evidence discipline as the doc mutations. The full column list, types, and caps live in **`docs/project_spec.md`** § _Ledger writes: `append_ledger` vs `append_ledger_row`_ and are enforced by `prestonotes_mcp/ledger.py` `LEDGER_V3_COLUMNS`. UCN playbook **Step 11** walks through the column-by-column extraction rules.

- **20 snake_case columns** at `schema_version: 3`: `run_date, call_type, account_health, wiz_score, sentiment, coverage, challenges_new, challenges_in_progress, challenges_stalled, challenges_resolved, goals_delta, tools_delta, stakeholders_delta, stakeholders_present, value_realized, next_critical_event, wiz_licensed_products, wiz_license_purchases, wiz_license_renewals, wiz_license_evidence_quality`.
- **Derived, not extracted.** The four `challenges_*` columns are **derived from `read_challenge_lifecycle`** for the customer (see UCN Step 11 table); never extract them from transcripts. The open-challenges count is derived on read as `len(challenges_in_progress) + len(challenges_stalled)` — it is **not** a stored column.
- **Typed values.** `wiz_score` is `int`; id-list cells are `list[str]`; everything else is `str`. Missing keys render as empty cells — do not pass placeholder tokens (`"n/a"`, `"None"`).
- **Write-time rejections** (tool returns `{"ok": false, ...}` with `field` + `value`/`expected`/`matched`): non-enum values for `call_type` / `account_health` / `sentiment` / `wiz_license_evidence_quality`, future `run_date`, regressed `run_date`, id-list fragments with whitespace or empty pieces, `wiz_license_purchases` / `wiz_license_renewals` entries that fail `^\d{4}-\d{2}-\d{2}:[a-z0-9_]+$`, free-text cap violations (`coverage` / `goals_delta` / `tools_delta` / `stakeholders_delta` / `next_critical_event` ≤ 160; `value_realized` ≤ 240), and any cell containing a term from **`FORBIDDEN_EVIDENCE_TERMS`** in `prestonotes_mcp/journey.py` (same SSoT TASK-048 uses for `update_challenge_state`).
- Empty cells for any column without available data — **no fabrication**; leave the key out and the writer will render `""`.
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
