# TASK-053 — UCN E2E gaps: GDoc v1/v2 fill, `sync_notes` / Drive order, manual test recipes

This file is the **table of contents (TOC)** for E2E **quality** work: sub-tasks **T053-A–G**, the **recommended order**, dependency notes, and **“done when.”** It does **not** auto-track progress — as you finish each mini-task, add dated notes or evidence here (or in chat logs) so the next session knows what is left.

**Status:** Active (documentation + E2E manual hygiene; no code owner yet).  
**Related:** [TASK-052 (complete — archive)](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) (harness §0 push-before-pull + `prep-v1`/`prep-v2`; historical detail), [TASK-051 (complete — archive)](../archive/2026-04/TASK-051-call-record-context-quality.md) (schema v2 + lookback split shipped; **runtime checklist** → §T053-G below).

**Canonical E2E context (read first):** [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) — vision §1, layers §3, artifacts §7, validation §8, post-write diff §6.

---

## LLM context — *Why are we doing this?* / pros / cons / test this task alone

| Question | Answer |
| --- | --- |
| **Link to vision** | Deliver a **GDoc** and **AI Account Summary** a human can ship without rewrite ([`.cursor/agents/tester.md` §1](../../../.cursor/agents/tester.md)). Full eight-step E2E must show **each transcript represented** in DAL (and related sections) with **full metadata** and consistent lifecycle — not a partial doc because the agent **skipped** DAL or `sync_notes` **reverted** local state. |
| **Why this task (specifically)** | Separates **content** gaps (missing v2 DAL, sparse metadata) from **process** bugs (**pull** overwriting newer `call-records` / lifecycle). Without documenting both, we blame UCN for what is actually **push/pull order** ([TASK-052 §0](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md)). |
| **Pros of closing the gaps** | E2E reflects **real** customer experience; UCN/Extract debugging gets clear **per-section** test recipes; fewer “it wrote nothing” scares when Drive was stale. |
| **Cons / risks** | UCN is **heuristic** — DAL can still be skipped if not **explicit** in the prompt. `read_doc` may not list `appendix.agent_run_log` in JSON — verify in the **GDoc UI**. |
| **How to test *only* this task** | **Sync discipline:** (1) Edit `challenge-lifecycle.json` or a call-record in repo; (2) `e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"`; (3) `sync_notes` / pull; (4) `diff` — file should not revert. **T053-A/B (DAL):** one transcript at a time, extract if needed, UCN with explicit “prepend DAL for 2026-04-28” (then 5/5); `read_doc` or UI check. **T053-C (metadata):** UCN with named metadata fields, before/after `read_doc`. Do **not** need full `prep-v1` for a narrow repro if Transcripts are already on disk. |
| **Provenance note** | Live GDoc `read` in this file used a **doc id** from a session discover — **do not** treat that id as canonical; **discover** at run time (see [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) and [TASK-052 §0.6](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md)). |

---

## Problem (from UCN + user run)

- After a **live** UCN `write` + `append_ledger_row`, a **`sync_notes` (pull from Drive)** can **replace local** `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json` and **`call-records/*.json`** with an **older Drive snapshot** if those files exist on Drive but are behind the repo.
- **rsync** `P` (protect) filters **do not** block “old file overwrites new file on pull” when both sides have the path — they mainly avoid **deleting** protected targets when the sender lacks them. **Order matters:** if the repo (or you) is the source of truth, **push to Drive** (`e2e-test-push-gdrive-notes.sh` with `GDRIVE_BASE_PATH` set) **before** any pull.

## What the live GDoc read showed (2026-04-22, after v2 + extract + UCN + write)

Verified via `prestonotes_gdoc/update-gdoc-customer-notes.py discover` / `read --doc-id <from discover>` (do not commit literal ids; [TASK-052 §0.6](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md)):

| Area | State |
| --- | --- |
| **Challenge Tracker** | **Updated:** both rows `date: 2026-04-20`, notes include 2026-04-20 QBR quotes; Splunk = Stalled, Champion = In Progress. |
| **Deal Stage Tracker** | **Updated:** `cloud` row `stage: win` with 2026-03-30 PO / exec close narrative. |
| **Exec Account Summary** | Goals / Risk / Upsell each have **one** `append_with_history` entry with `timestamp: 2026-04-22` (QBR + Splunk + Jane; upsell path SKU lines). |
| **Daily Activity Logs (DAL)** | **Still missing** dedicated blocks for **v2** transcripts: `2026-04-28-07-wiz-cloud-sku-purchase.txt` and `2026-05-05-08-wiz-sensor-pov-kickoff.txt`. Existing DAL is heavy v1 + older material; v2 is not represented as separate dated blocks. |
| **Account Metadata** | Still **sparse** vs corpus (e.g. Technical Owner / MTTR / reporting hours often empty; sensor line still **90%** while narrative is **~900/1000** in other sections). |
| **appendix.agent_run_log** | **`read` parser returned `entries: []` — does not match an expected “2026-04-22 UCN” line. Treat as: **verify in Google Doc UI**; if the line is missing, the write path or parser/heading match may need a follow-up (separate from this task’s manual recipes). |

## Missing updates vs v1 + v2 corpus (fixtures)

| Corpus | Transcripts (under `tests/fixtures/e2e/_TEST_CUSTOMER/`) | Expected in GDoc |
| --- | --- | --- |
| **v1** | `v1/Transcripts/*.txt` (six dated files + master) | Exec summary / DAL / tracker / deal / metadata largely covered by earlier seeds; 2026-04-22 procurement block may appear with **meeting date vs heading date** nuance. |
| **v2** | `v2/Transcripts/2026-04-28-07-wiz-cloud-sku-purchase.txt`, `v2/Transcripts/2026-05-05-08-wiz-sensor-pov-kickoff.txt` | **DAL** (prepend per v2 call), **Deal Stage** (cloud + sensor / PO / POV — partially landed via “cloud win”), **Account Summary** (upsell + risk as needed), **Account Metadata** (e.g. sensor % / owners if in transcript), **call-records** JSONs (create via extract) and **optional** challenge/lifecycle if new evidence. |

---

## v1 `_TEST_CUSTOMER` transcript-vs-GDoc deltas (finish before `prep-v2`)

Use **Step 6 coverage table → Step 8 mutations** in [`docs/ai/playbooks/update-customer-notes.md`](../../ai/playbooks/update-customer-notes.md) (show-your-work + trace). **Do not run `prep-v2` until this block is checked off** (including **T053-v1-UCN-05** Challenge Tracker — see last bullet). Then continue T053-A/B and the rest of the eight-step E2E.

- [x] **T053-v1-UCN-01 — Use Cases:** Exec readout cadence (“crisp monthly readout, not a ticket dump”) → `use_cases.free_text` (playbook routing + verification write).
- [x] **T053-v1-UCN-02 — Upsell Path:** Explicit **Wiz DSPM** and **Wiz CIEM** bullets where transcripts name acquisition / PII / identity context (not only “Wiz Cloud” umbrella). *(2026-04-23: `read` → two `append_with_history` on `exec_account_summary.upsell_path` + planner `no_evidence` for other key fields; verified `read` shows three upsell entries.)*
- [x] **T053-v1-UCN-03 — Cloud Environment `tools_list`:** `add_tool` for **actively used** third-party products per **`docs/ai/gdoc-customer-notes/mutations-account-summary-tab.md` rubric** (`devops_vcs` / `ticketing` / `security_tools` / … — **not** a fixed vendor checklist). *(2026-04-24: verified via transcript-grounded `add_tool` + planner `no_evidence`; rubric-first routing doc added 2026-04-24.)*
- [x] **T053-v1-UCN-04 — Goals (strategic only):** Optional extra **Goals** bullets only for rolled-up business outcomes (e.g. legacy agent retirement / cost, acquisition visibility) — **not** requirement-level process lines (those stay Use Cases / Workflows per mutation rules). *(2026-04-24: two `append_with_history` on `top_goal` — Prisma retire/license reinvest + acquisition/sensitive-data posture; planner `no_evidence` on risk/use_cases/workflows; `read` shows three goal bullets.)*
- [x] **T053-v1-UCN-05 — Challenge Tracker (rows + anchors):** Tracker was empty after partial exec-only writes; **`write_doc`** with four corpus-aligned **`add_table_row`** mutations + planner `no_evidence` populated **four** rows with **`[lifecycle_id:…]`** in Notes (2026-04-24). **Follow-up (authoritative lifecycle):** still run **`update_challenge_state`** (MCP) so `AI_Insights/challenge-lifecycle.json` matches those ids — full **`Update Customer Notes`** playbook remains the durable path; this run unblocked empty-tracker validation only.

---

## Manual workflow (correct order — avoid reverts)

1. **Mount** `GDRIVE_BASE_PATH` (Google Drive for Desktop) when you intend to **sync to/from** Drive. If not mounted, work **repo-only**; do not assume Drive is current.
2. If **local `MyNotes/Customers/_TEST_CUSTOMER/`** was edited (lifecycle, `call-records/`, `Transcripts/`) and **should win over Drive**:
   ```bash
   export GDRIVE_BASE_PATH="/path/to/My Drive/MyNotes"   # or your prestonotes path
   scripts/e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"
   ```
3. **Then** (if you use sync pull): `sync_notes` / `scripts/rsync-gdrive-notes.sh` **pull** — or run your E2E harness in the order defined in [TASK-052 Section 0](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md).
4. **Never** rely on pull to “save” work from the repo; pull **imports** Google Drive as sender for the rsync path.

---

## Per-gap sub-tasks (each: call-record, transcript, GDoc/ledger, manual test)

### T053-A — DAL: 2026-04-28 (Wiz Cloud SKU) block

- **Call-record:** `raw_transcript_ref: 2026-04-28-07-wiz-cloud-sku-purchase.txt` (generate via extract / `write_call_record` if missing).
- **Transcript:** `tests/fixtures/e2e/_TEST_CUSTOMER/v2/Transcripts/2026-04-28-07-wiz-cloud-sku-purchase.txt` (or materialized `MyNotes/.../Transcripts/` after `prep-v2`).
- **GDoc:** `daily_activity_logs` (prepend: meeting title, Context, 3 `What changed` + optional Description per project template), **not** replace entire DAL.
- **Challenge Tracker / History Ledger:** only if the run introduces **new** challenge evidence; otherwise **optional**; ledger is **append_ledger** after a successful UCN `write` if the playbook is run in full.
- **Manual test sequence:**  
  1. Confirm transcript file exists in `MyNotes/Customers/_TEST_CUSTOMER/Transcripts/`.  
  2. `write_call_record` (or `extract` playbook Step 4) for that file if JSON missing.  
  3. UCN with **explicit** instruction: “Prepend a new DAL block for 2026-04-28 from this transcript; do not skip for ‘already long DAL’.”  
  4. `read_doc` / open GDoc → verify a **2026-04-28** heading and Context / What changed lines.  
  5. (Optional) `append_ledger` if the run is part of a full UCN with ledger policy.

### T053-B — DAL: 2026-05-05 (Wiz sensor POV kickoff) block

- **Call-record / transcript / GDoc / ledger:** same pattern as T053-A, using `2026-05-05-08-wiz-sensor-pov-kickoff.txt`.

### T053-C — Account Metadata: align sensor % and optional owners/MTTR with transcripts

- **Transcripts:** especially v2 (sensor POV) + any v1 with deployment metrics.
- **GDoc:** `account_motion_metadata` (`sensor_coverage_pct`, `technical_owner`, `mttr_days`, `monthly_reporting_hours`, etc. — per `doc-schema.yaml`).
- **Call-record:** whichever JSON covers **2026-05-05** (sensor POV) and **2026-04-28** (cloud SKU) for **metadata fields** the planner maps.
- **Challenge Tracker / Ledger:** usually **N/A** unless a metadata line is also **challenge** evidence; ledger = optional append after write.
- **Manual test:** `read_doc` before; UCN (or a narrow `write_doc` plan) with **update_in_place** fields only; `read_doc` after to confirm `Exec Buyer` / `Champion` / `Sensor %` / technical owner are consistent (no 90% vs 900/1000 mismatch).

### T053-D — Exec Account Summary: use case / workflow tables (if still empty in dry-run)

- **Context:** UCN **dry-run** may report `no_evidence` for `goals`, `risk`, `use cases`, `workflows` key fields if the doc or planner lacks hooks.
- **Transcript / call-record:** **all** in lookback; for **v2** specifically the two v2 files above.
- **GDoc:** managed tables / fields per schema (separate from the three H3 `append_with_history` bullets in some templates — confirm `read_doc` section list).
- **Manual test:** UCN with **read_doc** full dump; ensure mutations target the correct `section_key` from `doc-schema.yaml`; one approved `write_doc` and verify in UI.

### T053-E — `agent_run_log` in Appendix

- **Expected:** one line per UCN `write` in **Account Summary** tab `Appendix` / `Agent Run Log` (TASK-050).
- **Manual test:** open GDoc, search for **Agent Run** or 2026-04-22 in Appendix; if missing after write, file a bug: writer vs. parser/heading. CLI `read` is **not** authoritative if parser returns `entries: []`.

### T053-F — `challenge-lifecycle.json` and Drive: no surprise revert after pull

- **Artifact:** `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json`
- **Manual test:** after **push** (section above), `diff` repo copy vs `MyNotes` after **pull**; re-run [TASK-052 §0.9](../archive/2026-04/TASK-052-e2e-test-customer-drive-sync-and-artifact-survival.md) verification or e2e push again if mismatch.

### T053-G — Call-record runtime quality & UCN read discipline (from TASK-051)

**When:** after **Extract** + **`call_records lint`** green and (optionally) full `Run E2E Test Customer`. **Where:** complements [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) §8 (validation), §10 (lifecycle), §11 (drift template) — **no** fixture-specific numeric gates in CI; operator judgment on a live or materialized corpus.

- **Corpus variance (LLM output):** Round-1 + round-2 `call-records/*.json` show **distinct** `key_topics` and **distinct** `challenges_mentioned[].id` where transcripts warrant it; `products_discussed` reflects actual SKUs per call (not a repeated default list).
- **Sentiment:** at least one **`cautious`** (or equivalent honest tone) where exec/QBR content warrants it — goldens illustrate shape; live runs still need eyeballing.
- **Action items:** `action_items[].owner` favors **named individuals** over generic `"SE"` when transcripts name owners.
- **Deltas:** `deltas_from_prior_call` populated where the corpus has genuine state change across calls (extractor reads prior records per playbook).
- **GDoc Challenge Tracker:** rows reflect **real** cross-call themes from the corpus (depth is qualitative — do not treat a fixed row count as a product invariant).
- **UCN `read_call_records` discipline:** no wholesale sweep; reads stay **targeted and bounded** (≤ 5 records per run per [`update-customer-notes.md`](../../ai/playbooks/update-customer-notes.md) lookback split + `.cursor/rules/20-orchestrator.mdc`).
- **Account Summary:** Stakeholders / narrative surfaces **`stakeholder_signals`** (and other v2 fields) when transcript + call-record evidence supports it.

**Overlap with component tasks (avoid duplicating backlogs):** scoped tuning and regression work for UCN sections, noop/delta detection, ledger integrity, and cross-artifact consistency live under **TASK-055**–**TASK-062** (see [`docs/tasks/INDEX.md`](../INDEX.md)). Use **T053-A–G** here as the **ordered manual E2E smoke path**; open or extend **055–062** when you need a **code + unit-test** owner for a specific subsystem.

---

## Account Summary vs DAL vs Account Metadata (dependencies)

| Section | **Typical UCN data dependency** | **Write behavior** (high level) |
| --- | --- | --- |
| **Exec Account Summary (Goals / Risk / Upsell)** | Transcripts in lookback, **optional** `challenge-lifecycle.json` for consistency with **Challenge Tracker**; call-records for older lookback. | `append_with_history` bullets under fixed H3s; duplicate/theme rules. |
| **Challenge Tracker** | `challenge-lifecycle.json` (canonical lifecycle + evidence) + current `read_doc` rows. | **Table** row update; `update_challenge_state` + `write_doc` together when governance applies. |
| **Daily Activity Logs (DAL)** | **Per-transcript** meeting narrative; long doc may cause planner to **skip** “full DAL” unless instructed. | **Prepend** new block at top; duplicate guards; **highest** chance of “missing v2” if agent decides scope is “already done.” |
| **Account Metadata** | Latest factual owner/coverage/MTTR from **recent** transcripts. | **update_in_place**; easy to be **stale** if the agent does not re-read. |
| **Deal Stage Tracker** | Commercial motion (PO, POV, win) in transcripts / call-records. | **Table** updates; can be partially satisfied by a single UCN (e.g. `cloud` → `win`). |
| **History Ledger** | Run outcome + metadata after write; **separate** file. | `append_ledger_row` (append-only); not automatic from DAL. |

**Flow difference (simple):** **one** UCN can bundle mutations for all sections, but **DAL** has different **heuristics** (noise, length, “already populated” skips) and **Account Metadata** is easy to under-fill vs narrative-heavy sections. **Account Summary** and **Challenge Tracker** share **governance** (reconciler / lifecycle). **Order inside E2E:** materialize **Transcripts** → **call-records** (extract) → **read_doc** + Phase 0 challenges → **write_doc** (batch) → **append_ledger** → only then **sync to Drive** if the repo is canonical (push) or after you accept Drive as canonical (pull with care).

---

## Recommended order to tackle

1. **T053-F / harness (TASK-052) hygiene:** adopt **push before pull** whenever MyNotes in repo is ahead; confirm **GDRIVE** mounted for rsync (canonical write-up: archived **TASK-052** §0).  
2. **T053-A** then **T053-B** (v2 DAL — highest user-visible gap for v1+v2 E2E).  
3. **T053-C** (metadata alignment) — after DAL or in same UCN with explicit field list.  
4. **T053-D** (use case / workflow if still `no_evidence` in your runs).  
5. **T053-E** (confirm `agent_run_log` in UI; escalate parser if CLI read stays empty but UI shows a line).  
6. **T053-G** (call-record runtime quality + UCN read discipline): run after v2 JSON exists for both v2 transcripts; confirms live Extract + UCN behavior, not only goldens.

**Done for this file when:** a human can run the **manual test sequences** above in order without Drive reverting `lifecycle` or `call-records`, and the GDoc shows **v2** DAL blocks and consistent metadata for `_TEST_CUSTOMER`, and **T053-G** has been exercised on at least one full or staged E2E pass.
