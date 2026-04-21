# TASK-049 — History Ledger schema v3 (rationalized, single-source, no duplicates)

**Status:** [ ] NOT STARTED
**Opened:** 2026-04-21
**Related:** Surfaced by the TASK-044 E2E review (Q5). Pairs with `TASK-048` (challenge lifecycle write discipline — provides the clean lifecycle state this schema derives 4 columns from) and `TASK-047` (harness vocabulary list — this task reuses `FORBIDDEN_EVIDENCE_TERMS` and extends enforcement to ledger cells).
**Related files:**
- `prestonotes_mcp/ledger_v2.py` (rewrite columns, drop migration code)
- `prestonotes_mcp/tools/migrate_ledger.py` (delete)
- `prestonotes_mcp/server.py` (`append_ledger_v2` + `read_ledger` signature/shape updates)
- `prestonotes_mcp/tests/test_ledger_v2.py` (rewrite against new schema)
- `prestonotes_gdoc/update-gdoc-customer-notes.py` (ledger-render helpers, if any consume `LEDGER_REQUIRED_COLUMNS`)
- `docs/ai/playbooks/update-customer-notes.md` Step 11 (new column guidance)
- `.cursor/rules/21-extractor.mdc` (ledger cell extraction rules)
- `docs/ai/playbooks/run-account-summary.md` (ledger read consumes new columns)
- `docs/ai/references/customer-notes-mutation-rules.md` (ledger section)
- `docs/project_spec.md` (§ ledger schema)
- `docs/MIGRATION_GUIDE.md` (one-line entry marking v2 → v3; no auto-migration)
- `scripts/ci/required-paths.manifest` (remove `migrate_ledger.py`)

---

## Problem

The TASK-044 E2E History Ledger output has two structural defects and two content defects. The structural defects are schema-level, which TASK-048's write discipline cannot fix.

**Schema defects (duplicate concepts at different column positions with conflicting values):**

1. **Column 13 `Value Realized` (free text)** vs **column 24 `value_realized` (free text)** — same concept, different capitalization, different cell positions, independently written.
   - Row 1 col 13: `"Cloud SKU closed; Sensor POV funded window"` — col 24: `"Cloud PO signed; Sensor POV kickoff"`.
   - Row 2 col 13: `"DSPM/CIEM acquisition win; Prisma retired"` — col 24: `"92% Wiz Score narrative solidified"`.
   - Account Summary reads one or the other inconsistently. Two customer-value narratives per row.
2. **Column 6 `Open Challenges` (count)** vs **column 22 `challenges_in_progress` (id list)** — the count is derivable from the id list but is written independently, allowing divergence. Current run has `Open Challenges = 2` while challenge-lifecycle.json has only 2 ids **for the wrong reason** (under-extraction), masking that this pair can silently disagree.
3. **Column 8 `Resolved Issues` (free text)** vs **column 23 `challenges_resolved` (id list)** — same concept split across two representations. Row 2 has `Resolved Issues` empty while the transcripts explicitly resolve sensor rollout; `challenges_resolved` is also empty; `Value Realized` mentions `"Prisma retired"` — the resolution info ends up in the wrong column three different ways.
4. **Column 7 `Aging Blockers` (free text)** + **column 9 `New Blockers` (free text)** have no structured counterpart today. Stalled and newly-identified challenges are lifecycle states; free-text duplication of them is drift-prone.
5. **Column 15 `Key Drivers` (free text)** is a catch-all that received harness vocabulary (`"Commercial expansion transcripts (v2)"`, `"v1 fixture transcript set (pre-v2 merge)"`) in this run. Semantically it overlaps with the per-category deltas (goals/tools/stakeholders changed) already tracked by columns 10–12.
6. **Column 12 `Stakeholder Shifts` (free text)** + **column 24 `key_stakeholders` (id list)** — `Shifts` = who moved, `key_stakeholders` = who was present. Keep both **concepts** but under non-ambiguous names.

**Content defects — downstream of TASK-048 / TASK-047, not this task:**

- Under-extracted challenges → TASK-048.
- Harness vocabulary in cells → TASK-047's forbidden-term list; this task extends enforcement to ledger cells at MCP write time.

**Legacy-code overhang:** `prestonotes_mcp/tools/migrate_ledger.py`, `migrate_standard_table_to_v2`, and half of `detect_standard_table_column_count` exist **only** to port 19-column legacy ledgers to 24-column v2. This project has zero production customers on the old schema. The migration code is dead weight.

---

## Goals

1. **One concept, one column.** No duplicate representations of the same fact.
2. **Derive what can be derived.** Fields computable from `challenge-lifecycle.json` are read from there, not independently written.
3. **Structured where structured helps.** Challenge deltas, stakeholder lists, license facts — id-lists and ISO dates, not free text.
4. **Free text where judgment helps.** Coverage, value realized, goals/tools/stakeholder narratives — single free-text column per concept, ≤ 160 chars.
5. **No migration scaffolding.** Project has no legacy 19-column data. The v2 path code goes away with it.
6. **Enforce vocabulary hygiene at write time.** Reuse `FORBIDDEN_EVIDENCE_TERMS` from TASK-047; reject any cell containing a forbidden term.
7. **Readable enough.** ≤ 20 columns in the markdown table. Current 24 → proposed 20.

---

## Scope

### A) New column list (schema v3 — canonical, no legacy)

Replace `LEDGER_BASE_COLUMNS` + `LEDGER_V2_EXTRA_COLUMNS` in `prestonotes_mcp/ledger_v2.py` with a single `LEDGER_V3_COLUMNS` list, in this order:

| # | Column | Type | Source | Notes |
|---|---|---|---|---|
| 1 | `run_date` | ISO date | UCN run | Today's date; append-only. |
| 2 | `call_type` | enum | UCN inference from transcripts in run window | `qbr \| exec_readout \| product_demo \| commercial_close \| technical_pov \| champion_1on1 \| kickoff \| other`. |
| 3 | `account_health` | enum | UCN synthesis | `great \| good \| at_risk \| critical`. |
| 4 | `wiz_score` | int 0..100 \| empty | explicit customer mention in transcripts | Empty if not stated. |
| 5 | `sentiment` | enum | UCN synthesis | `positive \| neutral \| negative \| mixed`. |
| 6 | `coverage` | free text ≤ 160 | UCN synthesis | Deployment/scan coverage headline for the run. |
| 7 | `challenges_new` | id list (`;`) | **derived from lifecycle** | Ids that transitioned to `identified` within the run window. Empty string if none. |
| 8 | `challenges_in_progress` | id list (`;`) | **derived from lifecycle** | Ids whose current state is `identified` or `in_progress` at run time. |
| 9 | `challenges_stalled` | id list (`;`) | **derived from lifecycle** | Ids whose current state is `stalled`. |
| 10 | `challenges_resolved` | id list (`;`) | **derived from lifecycle** | Ids that transitioned to `resolved` within the run window. |
| 11 | `goals_delta` | free text ≤ 160 | UCN synthesis | Customer goal shifts this run. |
| 12 | `tools_delta` | free text ≤ 160 | UCN synthesis | Tools that came online / retired. |
| 13 | `stakeholders_delta` | free text ≤ 160 | UCN synthesis | Who moved (departures, promotions, new sponsors). |
| 14 | `stakeholders_present` | id list (`;`) | derived from call-record `participants[]` within run window | Unique normalized names. |
| 15 | `value_realized` | free text ≤ 240 | UCN synthesis | Quantified or concrete outcomes this run. |
| 16 | `next_critical_event` | `YYYY-MM-DD: <desc>` | UCN synthesis | ISO date prefix required if a date is known; otherwise `<desc>` alone. |
| 17 | `wiz_licensed_products` | id list (`;`) | UCN synthesis | Normalized ids: `wiz_cloud`, `wiz_sensor`, `wiz_code`, `wiz_defend`, `wiz_advanced`, etc. |
| 18 | `wiz_license_purchases` | `ISO:sku` pairs (`;`) | UCN synthesis | E.g. `2026-03-28:wiz_cloud`. |
| 19 | `wiz_license_renewals` | `ISO:sku` pairs (`;`) | UCN synthesis | Same format. |
| 20 | `wiz_license_evidence_quality` | enum | UCN synthesis | `high \| medium \| low`. |

**Columns dropped (existed in 24-column v2 schema):**
- `Open Challenges` (count) — derivable as `len(challenges_in_progress) + len(challenges_stalled)`. Account Summary and UCN compute on read.
- `Aging Blockers` (free text) — replaced by structured `challenges_stalled`.
- `Resolved Issues` (free text) — replaced by structured `challenges_resolved`.
- `New Blockers` (free text) — replaced by structured `challenges_new`.
- `Value Realized` (free text col 13) — merged into `value_realized` (col 15, sole representation).
- `Stakeholder Shifts` (free text) — renamed to `stakeholders_delta` for naming consistency (same concept).
- `key_stakeholders` (id list, v2 extension) — renamed to `stakeholders_present` for naming consistency.
- `Key Drivers` (free text) — dropped entirely. Its value is covered by `coverage` + the three `*_delta` columns. This is also the column that received harness vocabulary in the TASK-044 run — dropping it removes one leakage site structurally.

**Naming discipline:** all columns are `snake_case`. No mixed `Title Case` / `snake_case` within the same table.

### B) Rewrite `prestonotes_mcp/ledger_v2.py`

- Replace `LEDGER_BASE_COLUMNS`, `LEDGER_V2_EXTRA_COLUMNS`, `LEDGER_V2_ALL` with a single `LEDGER_V3_COLUMNS` constant (list, ordered).
- Remove `migrate_standard_table_to_v2`, `detect_standard_table_column_count`'s migration usage, `_MIGRATE_HINT`, and the 19-col detection path entirely.
- `append_ledger_v2_row` renamed to `append_ledger_row`. Signature: `(customer_name: str, row: dict[str, str | int | list[str]]) -> Path`. Values accepted:
    - `str` for free-text and enum cells
    - `int` for `wiz_score`
    - `list[str]` for id-list cells (rendered as `;`-joined)
    - Missing keys rendered as empty cell.
- New header line in generated ledgers: `schema_version: 3` in the YAML frontmatter.
- Validation at write time (hard rejects with named error payloads, consistent with TASK-048 style):
    - **Enum violation**: `call_type`, `account_health`, `sentiment`, `wiz_license_evidence_quality` must match their enum.
    - **Date violation**: `run_date` must be `<= today + 1 day` (UTC). Regression rejected if a newer row already exists.
    - **ID-list format**: semicolon-separated, no empty fragments, no leading/trailing whitespace around fragments after render.
    - **ISO-SKU format**: `wiz_license_purchases` / `wiz_license_renewals` entries must match `^\d{4}-\d{2}-\d{2}:[a-z0-9_]+$`.
    - **Forbidden vocabulary**: any cell (free text or id list fragment) containing a term from `FORBIDDEN_EVIDENCE_TERMS` (defined in TASK-047's `prestonotes_mcp/journey.py`) is rejected with `matched` field naming the term.
    - **Length**: free-text cells enforced to the character caps in the column table above.
- `read_ledger` returns the v3 row shape with typed values (id-list cells parsed back to `list[str]`, numeric `wiz_score` to `int`). Existing `{"empty": true, ...}` response for missing file stays.

### C) Delete legacy migration code

- `prestonotes_mcp/tools/migrate_ledger.py` — delete the file.
- `scripts/ci/required-paths.manifest` — remove any entry for `migrate_ledger.py`.
- `prestonotes_mcp/tests/test_ledger_v2.py` — delete migration-related tests; rewrite to cover v3 columns.
- `README.md` — drop the `uv run python -m prestonotes_mcp.tools.migrate_ledger` line.
- `docs/MIGRATION_GUIDE.md` — replace the v1→v2 migration section with a one-line v2→v3 note: "No auto-migration. The `_TEST_CUSTOMER` E2E reset and the bootstrap-customer playbook create fresh v3 ledgers on first `append_ledger_row`." Any historical ledger files older than v3 are ignored; UCN's first write re-creates the ledger from scratch on disk (append-only rule applies from that first v3 row forward).
- `docs/project_spec.md` ledger §: replace 24-col column list with the 20-col v3 list.

### D) UCN playbook + extractor rule updates

- `docs/ai/playbooks/update-customer-notes.md` Step 11 rewrites the "build one new ledger row" section against the 20-col v3 schema. Each column gets one explicit "extract as …" line. The four challenge-* columns are documented as **"Do not extract. Derive from `read_challenge_lifecycle` output for this customer."**
- `.cursor/rules/21-extractor.mdc` adds a "**Ledger cell extraction**" section:
    - Every free-text cell cites (internally, not in the cell) one transcript line.
    - Cells MUST NOT contain harness vocabulary (inherits the TASK-047 list).
    - `run_date` = today; `call_type` = most salient of the transcripts covered; enum cells use only defined values.
    - `wiz_score` = verbatim number from a transcript if the customer stated it; otherwise leave empty — never infer.
    - `value_realized` MUST contain at least one quantified element when at least one in-scope transcript contains one (regex: `\$\d|\d+%|\d+\s*(workloads|CVEs|findings|weeks|hours|alerts)`); otherwise free text is fine.

### E) Account Summary consumer updates

- `docs/ai/playbooks/run-account-summary.md` Step 1 (`read_ledger`) documents the v3 row shape. Step 5 weights keep the ledger at its current priority.
- Any computed view (e.g. challenge-review table in the new TASK-047 Account Summary) derives **count** from `len(challenges_in_progress) + len(challenges_stalled)` on read, not from a stored count column.

### F) Fixture refresh

- The next `Run E2E Test Customer` produces a v3 ledger with zero harness vocabulary and the four challenge-* columns populated from the lifecycle JSON (post-TASK-048).
- `_TEST_CUSTOMER/AI_Insights/_TEST_CUSTOMER-History-Ledger.md` ends up with `schema_version: 3` in frontmatter.

---

## Explicit non-goals

- **No auto-migration.** v2 rows on disk (there are none in production) would be ignored; on fresh bootstrap, UCN writes a v3 header.
- **No schema change to `challenge-lifecycle.json` or call-records.** Those are TASK-048 / TASK-051.
- **No new read tool.** `read_ledger` stays; only its response shape changes to match the new columns.
- **No GDoc Challenge Tracker change.** The GDoc side is a separate surface and stays as-is for this task.
- **No change to ledger append-only rule.** Rows are never edited or deleted.
- **No column further than snake_case naming discipline.** We do not wrap cells in JSON or YAML — the markdown table stays human-readable.

---

## Acceptance

- [ ] `prestonotes_mcp/ledger_v2.py` (to be renamed `prestonotes_mcp/ledger.py`) exports `LEDGER_V3_COLUMNS` with exactly the 20 columns listed in §A, in order. No `LEDGER_BASE_COLUMNS` / `LEDGER_V2_EXTRA_COLUMNS` / `LEDGER_V2_ALL` / `migrate_standard_table_to_v2` references remain.
- [ ] `prestonotes_mcp/tools/migrate_ledger.py` does not exist.
- [ ] `rg "LEDGER_BASE_COLUMNS|LEDGER_V2_EXTRA_COLUMNS|LEDGER_V2_ALL|migrate_ledger|migrate_standard_table_to_v2"` returns no hits outside `docs/tasks/archive/`.
- [ ] `append_ledger_row` rejects: non-enum values, future `run_date`, id-list format violations, ISO-SKU format violations, `FORBIDDEN_EVIDENCE_TERMS` in any cell. Each rejection carries an error payload naming field + value + expected.
- [ ] `read_ledger` returns typed v3 rows (ints for `wiz_score`, lists for id-list cells).
- [ ] Tests in `test_ledger_v2.py` (renamed `test_ledger.py`) cover: round-trip append + read, each enum rejection, each format rejection, forbidden-vocab rejection, lazy-create path, and the "empty response when no file" path.
- [ ] `Run E2E Test Customer` on fresh `_TEST_CUSTOMER` after TASK-048 lands produces a ledger with:
    - `schema_version: 3` in frontmatter.
    - 20-column header.
    - Both rows have `challenges_new` / `challenges_in_progress` / `challenges_stalled` / `challenges_resolved` populated consistent with `challenge-lifecycle.json` (post-TASK-048 quality).
    - Row 2 (v1-window run) has `challenges_resolved` containing sensor rollout + kubelet noise ids.
    - `value_realized` written **once** per row; no duplicate-concept columns.
    - No harness vocabulary in any cell.
- [ ] `docs/project_spec.md` and `docs/MIGRATION_GUIDE.md` reflect v3; `README.md` has no `migrate_ledger` mention.

## Verification

1. Unit: `uv run pytest prestonotes_mcp/tests/test_ledger.py`.
2. Integration: `Run E2E Test Customer` on a cleanly reset `_TEST_CUSTOMER`. Diff against acceptance bullets.
3. Downstream: `Run Account Summary for _TEST_CUSTOMER`. Confirm the open-challenges count displayed in the narrative equals `len(in_progress) + len(stalled)` derived on read; confirm no cell contains `round 1`, `v1 corpus`, `v2 corpus`, `E2E`, `harness`, `fixture`, `TASK-`.
4. Operator safety smoke: run UCN on a real customer whose newest transcript is ≥ 30 days old. Confirm ledger append succeeds (no age-based rejection; TASK-048's rules don't prevent this here either).

## Sequencing

Land **after TASK-048** (TASK-049's four challenge-* columns derive from the cleaned-up lifecycle JSON). TASK-049's vocabulary enforcement reuses TASK-047's `FORBIDDEN_EVIDENCE_TERMS`, so land **after TASK-047** as well.

Full recommended order:

```
TASK-046  retire transcript-index.json
TASK-047  retire Journey Timeline; scrub harness vocab globally; enrich Account Summary
TASK-048  challenge lifecycle write discipline
TASK-049  History Ledger schema v3 (this task)
TASK-050  UCN GDoc write completeness + consistency
TASK-051  call-record quality
```

---

## Output / Evidence

_(Filled in as the task is executed.)_

- Code diffs (`ledger.py`, server tools, test suite): —
- Playbook + rule diffs (UCN Step 11, extractor ledger section): —
- Deleted files (`migrate_ledger.py`): —
- Post-task E2E `_TEST_CUSTOMER-History-Ledger.md` vs acceptance bullets: —
- Operator-safety run (≥ 30-day-old transcript) result: —
