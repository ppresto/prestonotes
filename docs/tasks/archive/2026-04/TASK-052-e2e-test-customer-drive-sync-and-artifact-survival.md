# TASK-052: E2E `_TEST_CUSTOMER`: drive sync, artifact survival, and harness (local-first + GDoc rebaseline)

**Status:** [x] **COMPLETE** (archived 2026-04-23). **Harness scope closed:** Section 0 (`prep-v1` / `prep-v2`, `e2e_rebaseline_customer_gdoc.py`, push-before-pull, `materialize --v2`, playbook + CI parity, §0.6 doc-id checks). Unchecked bullets **below** (§0.9 full UCN survival proof, optional §A, legacy “one uninterrupted 8-step” matrix, Section J.3+) are **deferred** — not blocking this archive — track under **TASK-053** (manual GDoc/sync quality), **TASK-044** (harness consolidation), or future tasks; this file remains the **historical spec + backlog reference**.
**Opened:** 2026-04-21
**Last updated:** 2026-04-23 (archived). **Section 0 (new default E2E approach).** Prior Section A and Section I assumptions were revised; see **Section 0.5** and **Section I (superseded)**.
**Depends on:** TASK-044 (harness contract), TASK-046 through TASK-051 (all landed and committed, as before).
**Related files:**
- **Canonical E2E context (read first):** [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) *(E2E doctrine; `docs/e2e/tester-playbook.md` **retired** 2026-04; `docs/E2E_TEST_CUSTOMER_GUIDE.md` **retired** 2026-04-23 — same role as **`/tester`** + playbooks)*. Update **`.cursor/agents/tester.md`** and `docs/ai/playbooks/tester-e2e-ucn.md` in the **same commit** when you change harness behavior, sync order, or playbook step count.
- Shell: `scripts/e2e-test-customer.sh`, `scripts/restart-google-drive.sh`, `scripts/rsync-gdrive-notes.sh`, `scripts/e2e-test-push-gdrive-notes.sh`, `scripts/e2e-test-customer-materialize.py`, `scripts/e2e-test-customer-bump-dates.py`
- **New (Section 0.2):** E2E-only GDoc “rebaseline” script under `prestonotes_gdoc/` (name TBD, e.g. `e2e_rebaseline_test_customer_gdoc.py`) - **not** used for real customers.
- **Optional / non-default:** `prestonotes_gdoc/drive-trash-customer.py` - only if **nuclear** folder delete is explicitly requested.
- MCP: `prestonotes_mcp/server.py` (`bootstrap_customer` then `prestonotes_gdoc/000-bootstrap-gdoc-customer-notes.py`), `sync_notes` then `rsync-gdrive-notes.sh`
- Playbook / rule: `docs/ai/playbooks/tester-e2e-ucn.md`, `docs/ai/playbooks/bootstrap-customer.md`, and files listed in **Section 0.7**
- Config: `MYNOTES_ROOT_FOLDER_ID` / `prestonotes_mcp/prestonotes-mcp.yaml` - **only** stable Drive root id; see **Section 0.6** (no hardcoded per-customer doc ids in code or task docs).
- Source transcript of the 2026-04-21 failures: session "Run E2E Test Customer" #2, uuid `de1a7525-6fcc-42f0-9afd-81f3ce692b93` (background: the **Problem** section and Section 0 below).

---

## LLM context — *Why are we doing this?* / pros / cons / test this task alone

Load this block when scoping work or answering “what is the benefit to the product vision?”

| Question | Answer |
| --- | --- |
| **Link to vision** | PrestoNotes v2 must produce **customer Notes (GDoc) + AI Account Summary** that are **evidence-grounded** and **regression-safe** on real accounts ([`project_spec.md` §1–§2](../../../project_spec.md), [`.cursor/agents/tester.md` §1](../../../.cursor/agents/tester.md)). The E2E loop is the **same pipeline** as production; this task makes that loop **fast, repeatable, and safe** (**`discover_doc` after prep**, local prep, correct **push-before-pull**), so quality work (UCN, extract) is not wasted on mount bugs or stale Drive overwrites. |
| **Why this task (specifically)** | Without **ordered** Drive sync (**push before pull** when the repo is canonical), **pull** can **overwrite** newer `call-records` / `challenge-lifecycle.json` with stale Drive copies — see [TASK-053](../../active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md). Notes **file id may rotate** on E2E rebaseline (§0.7); agents must **re-discover** instead of caching a dead `doc_id`. TASK-052 is the **harness + survival** layer so artifacts stay mutually coherent. |
| **Pros of completing it** | Shorter E2E cycles; no nuclear **reset** as default; **GDoc body** resets to the template shape (same-id in-place reset **deferred** — current path may rotate id); fewer “phantom” failures from mount lag; clear script surface (`prep-v1` / `prep-v2`) for agent + human. |
| **Cons / risks** | E2E-only GDoc rebaseline code must stay **gated** (never used for real customers). More moving parts in `e2e-test-customer.sh`. Wrong push/pull order still user-error-prone — documented in [`tester-e2e-ucn.md`](../../../ai/playbooks/tester-e2e-ucn.md) and TASK-053, not only here. |
| **How to test *only* this task (without full 8-step E2E)** | (1) With Drive mounted: `./scripts/e2e-test-customer.sh list-steps` and run **`prep-v1 --skip-rebaseline`** (or with rebaseline if testing §0.2) **once**; verify **`discover_doc`** returns a Notes document before+after (if rebaseline ran, the file **id may differ** — that is OK). (2) **prep-v2:** after artificial local edit in `MyNotes/Customers/_TEST_CUSTOMER/`, run **`e2e-test-push-gdrive-notes.sh "_TEST_CUSTOMER"`** then `prep-v2` or `rsync-gdrive-notes.sh` pull; confirm local files are not reverted. (3) Grep: no **committed** 32-char Notes `doc_id` in `docs/` per §0.6. (4) Run task verification bullets in **Section 0.9** / **H** when implemented. |
| **Pairing** | Complement [TASK-053](../../active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) (UCN content + sync *order* post-write). Depends on [TASK-044](../TASK-044-e2e-test-customer-rebuild.md) playbook contract (archived). |

---

## Section 0: Primary plan (2026-04-22): local-first reset, Notes via **`discover_doc`** (file id may rotate), push after each prep block

**Intent:** Make `Run E2E Test Customer` **fast to re-run** by **not** trashing and recreating the whole `Customers/_TEST_CUSTOMER` tree for every run. **Notes** is always resolved with **`discover_doc`**; after **E2E rebaseline** the Google **file id may change** (§0.7) — refresh discovery instead of caching an old id. **All** customer files that participate in mount/rsync churn are prepared in the **repo** (`MyNotes/Customers/_TEST_CUSTOMER/…`) and **pushed** to the Google Drive for Desktop mount **once at the end of each prep block** (round-1 and round-2 seeds) when the repo is canonical.

### 0.1 Principles

1. **Notes template reset (E2E):** “Reset to template” means the **body** of `_TEST_CUSTOMER` Notes matches `_TEMPLATE/_notes-template` (including clearing appendix run debris). **Shipped path** (`e2e_rebaseline_customer_gdoc.py`): Drive **copy + trash + rename** — the Notes **file id may change**; **re-`discover_doc`** after `prep-v1`. *Optional future:* same-id in-place body reset via **Google Docs API** `batchUpdate` (Section 0.2 historical note) if bookmark stability becomes mandatory. **E2E-only** — **not** the production `write_doc` path.
2. **No hardcoded customer doc id** in repo code, CI, or task text - only **`mynotes_root_folder_id`** (and optional env). Resolve `_TEST_CUSTOMER` Notes with existing **`discover` / `read_doc` / `.gdoc` stub** after sync.
3. **Local file prep:** After GDoc API rebaseline, **sync mount then repo** (`./scripts/rsync-gdrive-notes.sh _TEST_CUSTOMER` or `sync_notes`). On disk: **remove logs** (`pnotes_agent_log.md`, `pnotes_agent_log.archive.md` if present), **clear** `AI_Insights/*` to a **greenfield** (no `challenge-lifecycle.json`, no History Ledger) unless the test explicitly pre-seeds - then **`e2e-test-customer-materialize.py apply`**, **`e2e-test-customer-bump-dates.py`**, and **`./scripts/e2e-test-push-gdrive-notes.sh _TEST_CUSTOMER`**. **Backups** and **Backup\*** tree are **out of scope** (not part of a clean E2E).
4. **Two prep blocks, two pushes (unchanged from current semantics):** **prep-v1** (seed v1) ends with a **push**; **round-1 playbooks (steps 4 to 6) read the repo**; before **prep-v2**, **push local then Drive** again if anything round-1 wrote must be on the mount, then run **v2** merge + bump + **push** so the expansion transcripts exist before round-2 Extract. **This task adopts Section B (push before pull for v2)** and **Section C (additive v2 for call-records + transcripts)** as still required; wire them into the new subcommands.
5. **Nuclear path (optional):** Keep **`./scripts/e2e-test-customer.sh reset`** + **`drive-trash-customer.py`** as an **opt-in** “first time / corrupt folder / explicit greenfield on Drive” escape hatch - **not** the default first step of every E2E.
6. **Bootstrap (MCP `bootstrap_customer`)** is **one-time** when the folder truly does not exist, **not** every E2E run. After the first create, **Section 0.1** template reset + file prep replace “delete + bootstrap + copy doc” for iteration speed.

### 0.2 New script: E2E GDoc “rebaseline” (template-shaped body; **id may change**)

- **Path:** `prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py` (E2E-only; documented in **Section 0.7** below and [`tester-e2e-ucn.md`](../../../ai/playbooks/tester-e2e-ucn.md).)
- **Auth:** same pattern as `000-bootstrap-gdoc-customer-notes.py` / `update-gdoc-customer-notes.py` (gcloud user token).
- **Inputs:** `customer_name=_TEST_CUSTOMER` (default); **target** `doc_id` from **discover** (or CLI override read from the customer’s `… Notes` after sync - **do not** commit literal ids). **Source** = template document id from `_TEMPLATE/_notes-template.gdoc` (path configurable, same as bootstrap).
- **Effect (implemented):** Drive operations that produce **template-shaped** Notes; the resulting Google **file id may differ** from the pre-rebaseline id — **re-discover** before MCP reads/writes. *(Original design note: in-place body replace via Docs API without allocating a new id remains optional / deferred — see §0.7 operator decision.)*
- **Failure modes:** if template or target is unreadable, fail loud; no partial “half reset.”
- **Invocation:** run **before** the first `rsync` in a prep block when rebaseline is required (e.g. first step of `prep-v1`).

### 0.3 `e2e-test-customer.sh`: proposed subcommand map (implementation)

| Subcommand | Role | Replaces (old) |
|------------|------|----------------|
| **`prep-v1`** (name TBD) | GDoc rebaseline (0.2) then `rsync-gdrive` pull then delete logs + clear `AI_Insights` as spec’d then `materialize apply` then `bump-dates` then **`e2e-test-push-gdrive`** | `reset` + step 2 bootstrap + `v1` (for teams with an **existing** folder + doc) |
| **`prep-v2`** | **Push** repo then mount first (Section B) then `ensure` mount if needed then `rsync` pull then `materialize apply --v2` then `bump-dates` then **push** | `v2` (with ordering fixes) |
| **`reset` (nuclear, optional)** | `drive-trash` + local `rm` + `restart-google-drive` + poll | today’s `reset` - **rare** |
| **`bootstrap` (optional)** | Doc-only: call MCP/000-bootstrap when folder missing | chat-only today |

**Doc / rule renumbering:** `docs/ai/playbooks/tester-e2e-ucn.md` and `.cursor/rules/11-e2e-test-customer-trigger.mdc` must describe the new step order (e.g. **1 = prep-v1 shell** without mandatory nuclear `reset` and without mandatory **Bootstrap** when folder exists).

### 0.4 Script inventory (keep, retire, or new) for the E2E default run

| Artifact | Disposition | Notes |
|----------|------------|--------|
| **New: E2E GDoc rebaseline** | **Add** | Section 0.2; only for `_TEST_CUSTOMER` (or gated by flag). |
| `e2e-test-customer.sh` | **Refactor** | Expose `prep-v1` / `prep-v2` / optional `reset` per Section 0.3. |
| `e2e-test-customer-materialize.py` | **Keep + optional extend** | Optionally centralize “delete logs + clear `AI_Insights`” for greenfield, or a tiny helper called from shell. **Section C** (additive `--v2`) still required. |
| `e2e-test-customer-bump-dates.py` | **Keep** | Unchanged role. |
| `rsync-gdrive-notes.sh` | **Keep** | Pull after rebaseline; watch Section B for destructive pulls. |
| `e2e-test-push-gdrive-notes.sh` | **Keep** | `rsync --delete` to mount - **end of each prep** block. |
| `restart-google-drive.sh` | **Keep, narrow** | When mount path missing (after nuclear reset or first sync), not on every E2E. |
| `prestonotes_gdoc/drive-trash-customer.py` | **Optional** | Nuclear `reset` only. |
| `000-bootstrap-gdoc-customer-notes.py` | **Keep** | **First** folder + doc create; not every E2E. |
| `MCP` `discover` / `read` / `write` | **Unchanged** | UCN/Extract as today. |
| `python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` | **Keep** | Remains recommended gate before UCN; CI as today. |

### 0.5 Superseded or revised items vs earlier Section A / Section H / Section I

- **Section A (ensure-mount everywhere):** still useful **when the mount is missing** (nuclear `reset`, machine wake, or first-time bootstrap), but the **default** E2E path **avoids** delete+bootstrap+long mount waits. Prefer **restart + poll** only in those edge paths.
- **Section H / CI:** extend when new script exists - **required-paths** + any smoke for rebaseline **dry_run**.
- **Section I (PATCH-in-place / manual web trash):** **superseded** for **default** workflow by **the first principle in Section 0.1** plus **Section 0.2** (GDoc body rebaseline and local file tree). **Manual** Drive trash or **nuclear** `reset` remain **optional** escape hatches.

### 0.6 Id and path hygiene (acceptance for doc + code)

- [x] **No** committed literal `_TEST_CUSTOMER` Notes `doc_id` in task files, `README`, or `docs/` examples - use “discover at run time / root folder id in yaml” wording. **Enforced in CI** by `scripts/ci/check-docs-no-embedded-gdoc-file-ids.sh` (heuristic: `docs.google.com/.../d/<id>`, ` --doc-id <32+ char token>`, etc.; excludes `docs/tasks/archive/**`). Verified clean 2026-04-22.
- [x] Grep the repo for **32-char doc id** patterns in `docs/` and **scrub** sample ids from historical evidence (replace with `…` or “(discover)”) — same script; re-run when adding Playbook/CLI examples: `bash scripts/ci/check-docs-no-embedded-gdoc-file-ids.sh`

### 0.7 Files to update when implementing Section 0 (checklist)

- [x] `scripts/e2e-test-customer.sh` - subcommands and ordering (**`prep-v2` push-before-pull** in `cmd_prep_v2`); `list-steps` / `run-step` / legacy `v1` `v2` — **verified 2026-04-22** against Section 0.1–0.3 (re-read `cmd_prep_v1`, `cmd_prep_v2` + `usage`).
- [x] `prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py` — **E2E rebaseline via Drive copy+trash+rename** (Notes file id may change). **Operator decision (2026-04-23):** acceptable for `_TEST_CUSTOMER` because the Google Doc does not participate in the same mount-first caching issues as local `Transcripts/` / `call-records/` / `AI_Insights/` files; use `discover_doc` after each prep when needed. Optional future: same-`doc_id` in-place body reset via Docs API only if bookmark stability becomes a priority.
- [x] `docs/ai/playbooks/tester-e2e-ucn.md` - eight steps; optional nuclear `reset` + bootstrap; **“Parity with script”** blocks for `prep-v1` / `prep-v2` (2026-04-22) match `e2e-test-customer.sh`.
- [x] `.cursor/rules/11-e2e-test-customer-trigger.mdc` - same eight steps; hard rule 5 extended with `prep-v2` push-first + `prep-v1` flags (2026-04-22).
- [x] `docs/E2E_TEST_CUSTOMER_GUIDE.md` — table + parity work shipped 2026-04-22; **file retired 2026-04-23** (replaced by **`.cursor/agents/tester.md`** + [`tester-e2e-ucn.md`](../../../ai/playbooks/tester-e2e-ucn.md)).
- [x] `docs/ai/playbooks/bootstrap-customer.md` - clarify **one-time** `bootstrap_customer` vs E2E `prep-v1` vs nuclear `reset`+bootstrap; cross-links to `tester-e2e-ucn.md`, `e2e-test-customer.sh`, **tester** agent (2026-04-22, updated after guide retirement).
- [x] `scripts/e2e-test-customer-materialize.py` and/or prep helper - logs + `AI_Insights` cleanup if not in shell. **Verified:** centralized in `scripts/e2e-test-customer.sh::clean_local_harness_artifacts` and called by `prep-v1` (unless `--skip-clean`).
- [x] This task: mark Section B, Section C, Sections D through E, Section F, Section G, **Section H**, **Section J.3 and later** with **“still applies** after Section 0 harness**”** or **“blocked until harness green”** as appropriate. (See status map below.)

### 0.8 Map from historical scope (Sections A through G and Section J) to Section 0

- **Section B:** **still applies** after Section 0 harness — push-before-pull in `prep-v2` is implemented and runtime-smoked.
- **Section C:** **still applies** after Section 0 harness — additive `materialize apply --v2` is implemented and tested.
- **Section A:** **Narrowed** (see 0.5) - not the default hot path.
- **Section D, Section E:** **still applies** after Section 0 harness — content-quality and transition-date behavior; open until full UCN round is re-verified.
- **Section F:** **still applies** after Section 0 harness — retired-tool guard now wired into `check-repo-integrity.sh`; keep rule/playbook hardening active.
- **Section G:** **still applies** after Section 0 harness — account-summary save behavior remains a playbook/runtime discipline item.
- **Section H:** **still applies** after Section 0 harness — targeted tests landed for `materialize --v2` and missing-anchor auto-insert.
- **Section J.3+ (except J.1/J.2 landed):** **blocked until harness green** on full uninterrupted runtime pass (content / playbook tightening); **not** blocked on Notes `doc_id` churn given operator decision above.

### 0.9 Revised acceptance (harness), in addition to runtime bullets below

- [x] A full **`prep-v1`** produces a **template-matching** Notes Google Doc (via `e2e_rebaseline_customer_gdoc.py`) and clears local greenfield (`AI_Insights/`, logs) before materialize — **Notes `doc_id` may change** per copy-trash-rename; re-`discover_doc` after prep is the supported workflow. *(Same-id in-place body reset deferred / optional.)*
- [ ] `prep-v1` + `prep-v2` **without** nuclear `reset` completes; **round-1** UCN outputs survive until **`prep-v2` pull** only after **push** (Section B). **Shell proof done:** `AI_Insights/foo.md` survives `prep-v2` after push-before-pull; full round-1 UCN artifact proof remains runtime-deferred.
- [x] No documentation or task text **relies** on a hardcoded `_TEST_CUSTOMER` doc id (Section 0.6) — enforced with `check-docs-no-embedded-gdoc-file-ids.sh` + prior scrub; 2026-04-22.
- [x] `lint.sh` + `test.sh` + `check-repo-integrity.sh` + `check-docs-no-embedded-gdoc-file-ids.sh` green for touched paths (CI scripts re-run 2026-04-22 on this change).

---

## Problem (observed in the #2 run and the immediately prior #1 run)

Two consecutive `Run E2E Test Customer` sessions on 2026-04-21 completed the 10-step flow only after **repeated manual rescues**. No run finished cleanly. The user's verdict: _"E2E customer test was already ran in another session - read that session and identify why it failed to run completely."_

The flow is **not a single fatal `exit 1`**; it is a compound of **five recurring breakages** - every one of which the agent had to paper over in-session. None of them is caught by `test.sh` / `lint.sh` / `check-repo-integrity.sh`, so CI is green while runtime is broken.

### Breakage 1 - Drive-mount lag after API writes (the primary failure)

`bootstrap_customer` and `reset` both mutate Drive through the REST API. Google Drive for Desktop streams the result to the local mount **asynchronously**; in the #2 run the mount lagged **> 100 s** before `Customers/_TEST_CUSTOMER/` appeared, and a second `v1` had to be aborted and retried.

- After `reset`, the first `bootstrap_customer` call in #2 **failed** because `_TEMPLATE/_notes-template.gdoc` wasn't yet visible on the mount. Retry succeeded.
- After `bootstrap_customer`, the first `./scripts/e2e-test-customer.sh v1` **failed** ("not found on the Drive mount"). Only after invoking `scripts/restart-google-drive.sh` and polling did the folder appear.

The `e2e-test-customer.sh ensure_bootstrapped` helper was patched mid-session (entry 82 of the #2 transcript) to call `restart-google-drive.sh` when the mount is missing before `v1`/`v2`. That partial fix was not enough:

1. It only covers `v1`/`v2`, not the bootstrap then v1 transition _inside the same agent turn_; agents without that specific code path still hit the stall.
2. It does **not** cover the reset then bootstrap transition (the template-not-found failure above).
3. It relies on the agent noticing the stall and running the shell helper; under the `_TEST_CUSTOMER` E2E override the agent is supposed to chain without stopping.

**User's required fix (explicit ask, quoted verbatim):** _"Anytime we delete and then bootstrap a new customer/folder we need to wait a second and run the restart google drive script or it will not sync for a long time. this is a requirement so we dont need to wait for it just run it and then poll for the new directory to be available."_

### Breakage 2 - `./scripts/e2e-test-customer.sh v2` destroys round-1 UCN artifacts

`v2` calls `ensure_bootstrapped` then `rsync-gdrive-notes.sh` on the way in (pull Drive then repo mirror, `rsync -a --delete`). If round-1 UCN artifacts (`AI_Insights/challenge-lifecycle.json`, updated `*-History-Ledger.md`, any `*-AI-AcctSummary.md`, Journey-Timeline file) were **only local** and had not been pushed to Drive, `--delete` erased them. The #1 run hit exactly that; in #2 the agent manually inserted `./scripts/e2e-test-push-gdrive-notes.sh _TEST_CUSTOMER` between step 6 and step 7 as a workaround.

`rsync-gdrive-notes.sh` uses **receiver `protect` filters** (and `*.json` on pull) for ledger, lifecycle, and audit logs; **no** special-case rsync excludes for `_TEST_CUSTOMER` transcripts or call-records (same mirror as any customer). E2E re-seeds those from `e2e-test-customer-materialize.py` / `prep-v1` / `prep-v2`. The v2 path still **must** push to Drive before pull so round-1 UCN artifacts exist on the mount.

### Breakage 3 - `materialize apply --v2` clears `call-records/*.json`

`scripts/e2e-test-customer-materialize.py::_clear_per_call_corpus` wipes every `call-records/*.json` on every `apply`, including the `--v2` merge. Effect: step 7 resets the customer's call-records to empty, and step 8 must re-extract **all 8** transcripts (6 carry-overs + 2 new expansions), not just the 2 new ones. That turns round-2 Extract into a full repeat with its own LLM cost and failure surface. v2 is supposed to be _additive_ (expansion transcripts only) per the playbook header comment ("call-records come from the round-2 Extract playbook").

### Breakage 4 - Challenge Tracker rows miss `[lifecycle_id:<id>]` anchors then `LIFECYCLE_PARITY` warning

Both runs logged `LIFECYCLE_PARITY` from `write_doc` because Block B Challenge Tracker rows were written without the `[lifecycle_id:<id>]` notes-column anchor that the TASK-050 reconciler uses to flip row `status` from lifecycle JSON. Without the anchor, Challenge Tracker `status` drifts from `challenge-lifecycle.json` silently. The `_TEST_CUSTOMER` E2E should never land a Block A lifecycle update whose Block B Challenge Tracker twin lacks the anchor.

### Breakage 5 - `update_challenge_state` history-regression rejection

In #2 the agent first tried to transition `ch-soc-budget` to `stalled` with `transitioned_at=2026-03-29` when `challenge-lifecycle.json` already had a `2026-04-22` entry. TASK-048 correctly rejected it (`{"ok": false, "transitioned_at regresses history"}`). The agent recovered by using `2026-04-22`, but the mistake means the extractor / UCN rules still don't teach: **when citing older evidence, pin `transitioned_at` to the newest call date that supports the new state, never to an older evidence date.**

### Compounding - agents still reach for retired tool names

In an abandoned `python -m uv` blob inside #2 the agent imported `update_transcript_index`, `append_ledger_v2`, and `write_journey_timeline` (all retired in TASK-046 / TASK-049 / TASK-047). Current active playbooks / rules no longer mention them, but agent _session context_ does because operator triggers inherit from older runs. The E2E trigger rule should **positively enumerate** the current MCP surface (`write_doc`, `append_ledger_row`, `update_challenge_state`, `write_call_record`, `sync_notes`, `sync_transcripts`, `read_call_records`, `read_ledger`, `read_challenge_lifecycle`, `bootstrap_customer`, `discover_doc`, `read_doc`, `read_transcripts`), not just list what bypasses approval, so agents don't reach for a 2026-04-18-era API when under the override.

---

## Goals

1. **Section 0 harness (2026-04-22):** E2E uses **local-first** file prep, **GDoc template rebaseline** (E2E-only script; Notes file **id may rotate** — §0.7), log and **`AI_Insights` greenfield** on prep, and **push at end of each prep block**, with **nuclear** `reset` and **bootstrap** only when the folder or document truly does not exist (or the operator opts in).
2. **`Run E2E Test Customer` completes all 10 (or renumbered) steps in one session with zero manual rescues**, green on first try, repeatably. Success is measured by **one** uninterrupted agent transcript through Account Summary with every artifact present and internally consistent.
3. **Drive mount issues are rare** in the default path (no per-run folder delete). When the mount is wrong, use **`restart-google-drive.sh` and poll** (Section A, narrowed per Section 0.5); not blind sleeps.
4. **`v2` is additive** (Section C and Section 0): no round-1 UCN artifact is lost to `rsync --delete`; no forced re-extract of all eight call records unless explicitly intended.
5. **Challenge Tracker rows land with lifecycle anchors**; `LIFECYCLE_PARITY` is never logged on a clean E2E run (Section D and Section J.2).
6. **Extractor and UCN teach the correct transition date semantics** (Section E) so TASK-048 guardrails do not spuriously reject.
7. **CI catches harness and schema regressions** (Section H and the `call_records lint` guard as today).

---

## Explicit non-goals

- Do **not** re-open contracts for TASK-046, TASK-047, TASK-049, TASK-050, or TASK-051. Those guardrails stay; this task closes harness and playbook gaps.
- Do **not** introduce a new MCP tool. All fixes are script / playbook / rule / existing MCP wrappers.
- Do **not** alter approval gates for real customers. The `_TEST_CUSTOMER` E2E override is the only place the auto-chain is allowed.
- Do **not** add a full end-to-end pytest that invokes the LLM-backed MCP tools. The E2E remains agent-driven; CI gains non-LLM regression tests only.

---

## Scope

**Read Section 0 first (2026-04-22).** The subsections **Sections A through H** below are the **2026-04-21** plan. Where they assume **every** E2E starts with `reset` then `bootstrap` then `v1`, that is **superseded** by **Section 0.3** unless the operator uses the **nuclear** path. Item **Section B** and **Section C** remain **required** behavior for `prep-v2` / `v2` under any design.

### Section A: Bootstrap then mount visibility (user's explicit requirement; **narrowed** by Section 0.5)

Make the _"after bootstrap: restart Drive, then poll for the new dir"_ behavior **unconditional and automated**, not a runtime-noticed workaround.

1. **Add a new shell entry point** `./scripts/e2e-test-customer.sh ensure-mount [--customer _TEST_CUSTOMER] [--restart] [--timeout-sec 180]`. Exits 0 when `$MOUNT_CUSTOMER_DIR` is a directory; exits 1 after the timeout with a clear error. `--restart` invokes `restart-google-drive.sh` _first_ (before polling) so the next poll finds the folder within seconds instead of minutes. Default timeout at least 180 s.
2. **Wire it into the playbook** (`docs/ai/playbooks/tester-e2e-ucn.md`) immediately after step 2 (`Bootstrap Customer`): a shell gate `./scripts/e2e-test-customer.sh ensure-mount --restart` that **must** exit 0 before step 3 runs. Same gate runs immediately after step 1 (`reset`) with `--restart` so the template path is readable before step 2 calls `bootstrap_customer`.
3. **Wire it into the trigger rule** (`.cursor/rules/11-e2e-test-customer-trigger.mdc`): between `reset` and `Bootstrap Customer`, and between `Bootstrap Customer` and `v1`, call `ensure-mount --restart` verbatim. Update the numbered "Contract - execute all 10 steps in one session" list to make these explicit sub-steps (`1a`, `2a`) so they're part of the fixed chain.
4. **Preserve the existing `ensure_bootstrapped` helper** in `e2e-test-customer.sh` for compatibility, but have it delegate to the new `ensure-mount` path. Remove the "WARN: …" log at the top of that helper (replaced by structured output from `ensure-mount`).
5. **Do not** sleep-then-restart. The user explicitly does not want a blind wait - restart immediately, then poll. `restart-google-drive.sh 0` (or equivalent) should be the invocation: kill Google Drive, reopen, then poll.

**Implementation note:** `restart-google-drive.sh` currently defaults to a 10 s `sleep` _before_ killing Drive. That pre-kill sleep is the opposite of what we want for the E2E flow. Add a second subcommand or flag (`--no-prewait`) that skips the pre-kill sleep.

### Section B: `v2` artifact survival

1. **Push-before-pull in v2.** Modify `./scripts/e2e-test-customer.sh cmd_v2` to call `./scripts/e2e-test-push-gdrive-notes.sh "$CUSTOMER"` **before** it calls `ensure_bootstrapped` / `ensure-mount`. That guarantees round-1 UCN artifacts (`AI_Insights/challenge-lifecycle.json`, ledger, any manually-saved AcctSummary) exist on Drive before any `rsync --delete` from Drive runs.
2. **Implemented:** `rsync` **protect** filters + `*.json` pull (not `_TEST_CUSTOMER`-only path excludes for transcripts/call-records; those are re-seeded by materialize in E2E). Optional: add **protect** for `*-AI-AcctSummary.md` if the same “local-only then pull” failure mode appears for that file.
3. **Document the ordering** in `e2e-test-customer.sh` header comment and the E2E playbook step 7 section - the "pull happens last" rule is non-obvious and caused breakage #2.

### Section C: `v2` materialize must be additive

1. **Scope `_clear_per_call_corpus` to v1 only.** When `materialize apply --v2` runs, keep existing `call-records/*.json` and existing v1 `Transcripts/*.txt`; only drop any `_seed_from_*` or `Backup*` stragglers. v2 adds **2 expansion transcripts** (`2026-04-28-wiz-cloud-sku-purchase.txt`, `2026-05-05-wiz-sensor-pov-kickoff.txt`) without disturbing round-1 state.
2. **Re-test the bump-dates script** after Section C.1 - it must still succeed when call-records exist from round 1 (`e2e-test-customer-bump-dates.py --customer _TEST_CUSTOMER`). If there's a name-collision concern (which was the original reason for `_clear_per_call_corpus`), handle it by making the clear **v1-only** (`apply` with no `--v2`) and making `--v2` a pure merge.
3. **Update the E2E playbook** at the step 7 and step 8 sections to state: round 2 Extract produces **only the 2 new call-records**; the 6 from round 1 are unchanged.

### Section D: Challenge Tracker lifecycle anchors are mandatory

1. **Extractor rule** (`.cursor/rules/21-extractor.mdc`): add a line to Block B / Challenge Tracker guidance - every row that corresponds to a Block A `update_challenge_state` write **must** include `[lifecycle_id:<id>]` in its `notes` / description column, using the same id the lifecycle JSON uses.
2. **UCN playbook** (`docs/ai/playbooks/update-customer-notes.md` Section B / Block B): identical requirement with a short worked example.
3. **Preflight check in UCN writer.** Before `write_doc` submits Block B mutations, scan the Challenge Tracker rows it's about to send; if any row mentions a challenge id that `challenge-lifecycle.json` knows and the row is missing a `[lifecycle_id:<id>]` anchor, log a structured warning and **auto-insert** the anchor. (This is the mirror of TASK-050's reconciler - same map, one more direction.) File: `prestonotes_gdoc/challenge_lifecycle_parity.py` already centralises the parity helpers; extend there.
4. **Unit test** in `prestonotes_gdoc/tests/test_task_050_ucn_writer.py` (or new `test_task_052_lifecycle_anchor.py`): round-tripping a Block B mutation missing an anchor auto-repairs it when the lifecycle map has the id; leaves rows alone when the id isn't in lifecycle.

### Section E: Transition date guardrail teaching (avoid TASK-048 rejections)

1. **Extractor playbook** (`docs/ai/playbooks/extract-call-records.md` Step 6 - deltas + challenges): add a brief "Transition date rule" callout. When you propose a `deltas_from_prior_call[].status_change`, the `at` date the downstream UCN run will use is the **newer call's date**, never the older evidence date.
2. **UCN playbook** (`docs/ai/playbooks/update-customer-notes.md` Section B.1 rule 1 - already says "call date, not run date"): append a rule 1a - _"if the call date is older than the most recent `at` in `challenge-lifecycle.json` for that id, use the newest supporting call date instead. Never backdate below history."_
3. **21-extractor.mdc** - match the rule in both places.
4. **`.cursor/rules/11-e2e-test-customer-trigger.mdc`** - include the transition-date rule explicitly in the "Hard rules" list so the override doesn't accidentally silence it.

### Section F: Positive tool enumeration in the trigger rule

Amend `.cursor/rules/11-e2e-test-customer-trigger.mdc` "Contract" block to enumerate the **current** MCP tool surface the flow is allowed to use (the list in this task's Problem / Compounding section). Explicitly call out retired tools that agents sometimes reach for: `update_transcript_index`, `append_ledger_v2`, `write_journey_timeline` - do not invoke; this is a bug if present in agent output.

Also land an `rg` guard in `check-repo-integrity.sh` (`scripts/ci/`) asserting that none of those three tokens appear in **active** playbooks / rules (archive tasks are excluded).

### Section G: Account Summary save is part of the E2E flow

Step 10 should always leave `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/_TEST_CUSTOMER-AI-AcctSummary.md` on disk with a real artifact (not an agent chat transcript copy-paste). Options, smallest first:

1. **Document-only change:** `docs/ai/playbooks/run-account-summary.md` and `tester-e2e-ucn.md` step 10 instruct: after generating the summary in chat, write it to the canonical path and push to Drive. (Current state is ambiguous; the #2 run's save was ad-hoc.)
2. **Optional helper:** `./scripts/e2e-test-customer.sh finalize` (name TBD) - takes the last chat-generated summary via stdin or an argv path, writes it to `AI_Insights/`, pushes to Drive. Keeps the flow shell-gated end-to-end.

Prefer option 1 unless option 2 falls out naturally.

### Section H: CI regression coverage

Non-LLM, non-Drive tests to catch regressions of Sections A through F without needing a live Drive mount:

1. `scripts/e2e-test-customer-materialize.py` - add pytest in `prestonotes_mcp/tests/` (or next to the script) verifying `_clear_per_call_corpus` is **not** invoked on the `--v2` code path and that a pre-populated `call-records/*.json` survives `apply --v2`. Use a `tmp_path` fixture.
2. `prestonotes_gdoc/challenge_lifecycle_parity.py` - extend `test_challenge_lifecycle_parity.py` with a case proving the auto-anchor-insertion from Section D.3.
3. `scripts/e2e-test-customer.sh` - shellcheck pass (via `lint.sh`) + a `--help`/`ensure-mount` unit style smoke test in `scripts/ci/check-repo-integrity.sh` (invoke `ensure-mount --help` and assert the subcommand is wired).
4. `scripts/ci/check-repo-integrity.sh` - add the `rg` guard from Section F.
5. `scripts/ci/required-paths.manifest` - add any new scripts / playbook paths this task introduces.

---

## Proposed sequencing (revised 2026-04-22)

1. **Section 0, land the harness** (E2E GDoc rebaseline script, `e2e-test-customer.sh` `prep-v1` and `prep-v2`, push-before-pull in v2, local log and `AI_Insights` cleanup, docs and rule renumbering). **No LLM.**
2. **Sections B and C:** verify push ordering and additive `--v2` are correct inside the new subcommands; add or keep unit tests per Section H.
3. **Section A:** only as needed: `ensure-mount` or equivalent for **nuclear** or first-boot paths; do not block shipping Section 0 on full Section A if the default path no longer trashes the folder.
4. **Sections D, E, and F:** quality work (can parallelize with step 1 in a second agent if needed).
5. **Section H:** CI and `rg` guards; add coverage for the new script and subcommands.
6. **Run `Run E2E Test Customer`** on the **default** (non-nuclear) path; then spot-check **nuclear** `reset` and **bootstrap** once.
7. **Section G and Section J.3 onward:** account-summary save clarity, post-flight hygiene, and UCN and Extract quality follow-ups (may be **separate** tasks if harness work is already large).

Use the **coder, then tester, then doc** workflow per `.cursor/rules/workflow.mdc`. Do not land Section D without the unit test; do not land Section A without a shellcheck pass.

---

## Acceptance

### Code-level (verifiable in CI / `test.sh` / `lint.sh` / `check-repo-integrity.sh`)

- [x] **Section 0:** `./scripts/e2e-test-customer.sh prep-v1` runs **E2E GDoc rebaseline** (template clone), then pull then file prep then push. **`--help` / `list-steps` documents** subcommands. Notes file id may change on rebaseline — acceptable per operator; `discover_doc` when automation needs the current id.
- [ ] (Optional, Section A) `ensure-mount --help` and restart+poll behavior when **nuclear** / empty mount.
- [x] **Section 0 and Section B:** `prep-v2` (or `v2` in refactored harness) **pushes local then Drive** before any pull. Running `v2` after a clean `v1` and a manual `AI_Insights/foo.md` touch leaves `AI_Insights/foo.md` intact on disk.
- [x] `scripts/e2e-test-customer-materialize.py apply --v2` with a pre-populated `MyNotes/Customers/_TEST_CUSTOMER/call-records/` directory preserves every pre-existing JSON record and only merges the v2 expansion transcripts.
- [x] Unit test `test_challenge_lifecycle_parity.py::test_missing_anchor_auto_inserted` green.
- [x] `rg "update_transcript_index|append_ledger_v2|write_journey_timeline" docs/ai docs/project_spec.md .cursor/rules` returns **zero** hits (archive is excluded). Guard-shell script `check-repo-integrity.sh` fails loudly if any hit appears.
- [x] `lint.sh` clean on the modified shell + python.

### Runtime (verifiable only by `Run E2E Test Customer`)

- [ ] One uninterrupted `Run E2E Test Customer` session completes the canonical **8-step** flow with **no** repair loops, **no** `LIFECYCLE_PARITY` warnings, **no** `transitioned_at regresses history` error, **no** mount-missing retry, and **no** manual artifact re-creation.
- [ ] Post-run on-disk artifacts: `call-records/*.json` count is **8** (6 carry-overs from round 1 + 2 new from round 2). `challenge-lifecycle.json` has at least 2 ids in terminal state (e.g. `ch-soc-budget` stalled, `ch-champion-exit` in_progress or resolved). `*-History-Ledger.md` has exactly **2** new rows (one per UCN round). `*-AI-AcctSummary.md` exists under `AI_Insights/`. Drive mirrors the repo mirror.
- [ ] Account Summary chat output contains no harness vocabulary (`TASK-NNN`, `round 1`, `phase`, `E2E`, `harness`, `fixture`). Existing `FORBIDDEN_EVIDENCE_TERMS` guard covers that; reaffirming here as part of acceptance.

---

## Verification commands (for the `tester` subagent)

```bash
bash .cursor/skills/test.sh
bash .cursor/skills/lint.sh
bash scripts/ci/check-repo-integrity.sh
uv run python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER # when call-records present
# After Section 0 ships (replace with actual subcommand names from e2e-test-customer.sh --help):
# ./scripts/e2e-test-customer.sh prep-v1 --help
# ./scripts/e2e-test-customer.sh ensure-mount --help # if Section A subcommand still exists
```

The runtime `Run E2E Test Customer` session is performed by the **user** after the coder / tester / doc phases land, not by a subagent.

---

## Output / Evidence (filled by the `doc` subagent on completion)

- Phase 1 (coder): _paste Output Contract from coder_
- Phase 2 (tester): _paste Output Contract from tester, including which runtime acceptance bullets remain `[ ] runtime-deferred`_
- Phase 3 (doc): _paste Output Contract from doc_
- Post-runtime (user): one line "E2E green on YYYY-MM-DD, transcript uuid ..." - flip acceptance checkboxes in-place.

---

## Handoff / follow-ups (if any slip)

- If Section G option 2 (explicit `finalize` helper) proves necessary, open a follow-up. Do not let it block Sections A through F.
- If the Drive-restart cadence still races under Section A - e.g. restart itself takes > 60 s on first boot - add a second poll phase (wait for `_TEMPLATE/_notes-template.gdoc` visible **before** `bootstrap_customer` runs) and document in `docs/ai/playbooks/bootstrap-customer.md`.
- If round-2 Extract still re-extracts all 8 records despite Section C being correct, inspect `docs/ai/playbooks/extract-call-records.md` Step 3 gap-detection logic - it may be comparing the transcript set as a whole instead of per-id deltas.

---

## Source evidence (read-only pointers)

- Agent transcript of the #2 E2E run: `de1a7525-6fcc-42f0-9afd-81f3ce692b93` (entries 92, 148, 150 contain the two run recaps and the final root-cause summary).
- Mid-session fix landed in `scripts/e2e-test-customer.sh::ensure_bootstrapped` (#2 transcript entry 82) - still on `main` as of this task opening. Section A.4 preserves it but moves the canonical helper to `ensure-mount`.
- 2026-04-21 22:10, third E2E run artifacts (the fact-checked inputs for Section 0 and Section J below):
  - Gdoc: Drive document id **(redacted; discover at run time; do not commit literal ids per Section 0.6)**, tabs `Account Summary`, `Daily Activity Logs`, `Account Metadata`.
  - `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/challenge-lifecycle.json`: 2 ids (`ch-soc-budget` stalled, `ch-champion-exit` in_progress); both history entries use run-date `at` stamps instead of call dates; `ch-soc-budget.history[0].at=2026-03-25` and `ch-champion-exit.history[0].at=2026-03-30` are hallucinated (no corresponding transcripts).
  - `…/AI_Insights/_TEST_CUSTOMER-History-Ledger.md`: schema v3 (landed via TASK-049), but coverage and value_realized columns are vague and under-capture QBR evidence (missing 900 of 1000 workloads, 10k to 12 toxic combos, Prisma decommissioning, PII bucket catch).
  - `…/AI_Insights/_TEST_CUSTOMER-Journey-Timeline.md`: still present despite TASK-047 retiring the artifact. No code path writes it anymore (`rg` clean); the E2E agent hand-wrote it with forbidden harness vocabulary ("batch A", "batch B").
  - `…/AI_Insights/_TEST_CUSTOMER-AI-AcctSummary.md`: Goals, Risk, and Upsell populated; Challenges to Solutions map names 3 challenges but only 2 live in lifecycle JSON; "Acquisition and data risk" is narrated as open without a lifecycle entry.
  - `…/call-records/*.json`: 8 files, every one with `extraction_confidence: "low"` and the "wave-2 shortcut" fingerprint (hardcoded `["Wiz platform","Security posture"]`, `"Capture next steps from call"` action, `summary_one_liner` = first speaker utterance verbatim, `challenges_mentioned[].id` = 24 to 27 character kebab slug of description). TASK-051 validator passed these because its banned-defaults list was scoped to the v1-era fingerprints only.

---

## Appendix: Q1 through Q9 fact-check of the 2026-04-21 22:10 run (the third run)

The user ran `Run E2E Test Customer` a third time and reported "it behaves the same as before all of our changes." The per-question fact-check against the 8 transcripts is below; each finding ends with the remediation already folded into Sections A through J.

### Q1 (call-records), CRITICAL; partial fix landed in Section J.1

All 8 records exhibit the **wave-2 shortcut-extractor fingerprint** (see the Source evidence block). TASK-051's `BANNED_CALL_RECORD_DEFAULTS` only covered `ch-stub`, `Fixture narrative`, or `E2E fixture` (v1 fingerprints) so the v2 write path accepted every shortcut record. Section J.1 extends the banned list and adds two new structural guards; the remaining gap is agent behavior and lives in Section J.3 (playbook tightening) and Section J.4 (approval-bypass scope reduction).

### Q3 (journey timeline), present but retired

`_TEST_CUSTOMER-Journey-Timeline.md` persists under `AI_Insights/`. No source code path writes it (`rg` across `prestonotes_mcp`, `prestonotes_gdoc`, `scripts`, `docs/ai/playbooks`, `.cursor/rules` returns zero matches). The file is hand-written by the E2E agent from session memory - confirmed by the forbidden harness vocabulary "batch A" / "batch B" and the header `# _TEST_CUSTOMER - Journey Timeline`. Addressed by new Section J.5 (post-flight guard) which fails the E2E if the file exists or if any artifact contains `FORBIDDEN_EVIDENCE_TERMS`.

### Q4 (challenge-lifecycle.json) - missing challenges + hallucinated dates

Two entries present (`ch-soc-budget`, `ch-champion-exit`); ground truth from transcripts supports at least **five more** that the extractor missed:

1. `ch-kubelet-noise` - resolved 2026-03-29 per the "kubelet-noise issue from earlier is resolved after the patch cycle and should stay marked resolved" line; recurs 2026-04-16 as a manageable annoyance. Should be `identified then resolved then reopened_low` or similar.
2. `ch-acquisition-data-risk` - identified 2026-04-09 (AcmeCorp onboarding / PII bucket finding) then resolved 2026-04-09 (DSPM + CIEM + 100 % visibility in 15 min).
3. `ch-sensor-rollout-stall` - identified pre-QBR (Jane Smith references "the agent rollout is no longer stalled") then resolved 2026-04-19 via DaemonSet + 900/1000 coverage.
4. `ch-cli-policy-exceptions` - identified 2026-04-12 (two exceptions: service accounts + break-glass); in_progress pending named owners.
5. `ch-jira-routing-ownership` - identified 2026-04-05 / 2026-04-16 (named owners before Jane's last day); bundleable under `ch-champion-exit` but user explicitly asked to keep themes distinct.

Hallucinated dates: `ch-soc-budget.history[0].at=2026-03-25` (no Splunk/budget content on 2026-03-25; first mention is 2026-04-05 - `ch-champion-exit.history[0].at=2026-03-30` (no 2026-03-30 transcript at all). Root cause: TASK-048 MCP-side validator rejects future / history-regressing dates but does **not** verify the `at` date matches the cited evidence's transcript date. Section J.6 adds an extractor-side minimum-challenge-set check that fails the #_TEST_CUSTOMER_ run if lifecycle JSON has fewer than 4 ids, covering the "missed themes" class; the date-cross-check is left in the extractor playbook as per TASK-048's compromise.

### Q5 (history ledger) - schema-correct but content-thin

Both rows are schema-v3-valid (TASK-049 landed). Content issues:

- `coverage` column blurb is vague ("Graph triage and sensor threads active"); should concretely cite 900/1000 workloads scanned, Wiz Score 92 %, 10k CVSS criticals then 12 toxic combos, Prisma agents decommissioned.
- `value_realized` row 1 ("DSPM and acquisition visibility wins noted in calls") misses the concrete quote "caught an unencrypted S3 bucket full of PII exposed via an overprivileged IAM role."
- `wiz_licensed_products = wiz_cloud;wiz_sensor` misses `wiz_dspm`, `wiz_ciem`, `wiz_cli`, `wiz_code` - all explicitly discussed.
- Both rows dated `2026-04-22` (UTC run date) - acceptable by v3 spec but makes it hard to tell which round each came from when the E2E runs two UCN passes back-to-back. Section J.7 adds a `round` discriminator to the ledger row (`round=v1|v2|standalone`).

### Q6 (Account Summary tab) - Goals/Risk/Upsell OK; everything else empty

- **Goals / Risk / Upsell Path:** present, directionally correct, but mildly repetitive (Sensor POV appears in Goals and Upsell; Splunk in Risk twice). Acceptable for this round.
- **Challenge Tracker:** only 2 rows. The 5 additional themes in Q4 are missing. Rows use `lifecycle:ch-soc-budget` (bare) instead of canonical `[lifecycle_id:ch-soc-budget]` - Section J.2 makes the reconciler accept both, but the writer should still emit the canonical form (Section D.3 is the remaining work).
- **Company Overview, Contacts, Org Structure, Use Cases / Requirements, Workflows / Processes, Accomplishments:** every one is **empty**. Ground truth for each is in the transcripts (explicit Wiz Score, 900/1000 workloads, Okta hub, GitHub Actions, Jira, SOC2 automation, PII bucket catch, top 12 toxic combos, etc.). TASK-050 Section B requires at least 80 % section fill; this run hit ~20 %. Root cause: the UCN playbook doesn't enforce per-section fill; the agent under E2E override writes only the sections it feels like. Section J.8 adds a UCN post-flight that refuses to finalize the write if a per-transcript-fact threshold is not met.
- **Contacts:** no names, roles, or personal facts despite explicit signals (John Doe = Exec Sponsor self-identified 2026-04-05 + 2026-04-19; Jane Smith = transitioning out, leaving "next week"). Section J.8 carries this as an acceptance bullet.
- **Cloud Environment:** two fields filled (CSP, IDP) out of nine. Missing: DevOps tools (GitHub Actions), Security Tools (Splunk, Prisma being decommissioned), ASPM (Wiz CLI), Ticketing (Jira), Sizing (1k workloads / 900 scanned), Platforms (containers / DaemonSet). Section J.8.

### Q7 (challenge identify then track then sync flow) - broken at the anchor boundary

Designed flow: extractor then `update_challenge_state` then lifecycle JSON then UCN Block B mutation then Challenge Tracker row with `[lifecycle_id:<id>]` anchor then TASK-050 reconciler flips row status from lifecycle. Observed: anchor format was `lifecycle:<id>` (bare), reconciler matched nothing, row status says `Open` while lifecycle says `stalled`. Section J.2 (landed) fixes lookup; Section D.3 (TODO) adds auto-repair at write time.

### Q8 (Daily Activity Logs) - coverage gap + uniform template

Only 3 date-headed entries (2026-03-25, 2026-03-29, 2026-04-19) for 8 transcripts - 5 missing (2026-04-02, 2026-04-05, 2026-04-09, 2026-04-12, 2026-04-16). A stray `- Description` row at the end is template debris. Content uses a generic label pattern (`Coverage & scanning` / `Integrations` / `Risks`) regardless of call type; no MEDDPICC vocabulary; no per-call-type prompt switching. The UCN playbook currently has one DAL recipe for all calls. Section J.9 adds a call-type then DAL template map (QBR, POV kickoff, shift-left working session, commercial close, procurement readout, exec monthly) so the recap shape fits the call.

### Q9 (Account Metadata tab) - mostly empty; Deal Stage Tracker partially right

All 7 top-of-tab metadata fields are empty (Exec Buyer, Champion, Technical Owner, Sensor Coverage %, Critical Issues Open, MTTR Days, Monthly Reporting Hours) despite explicit transcript signals (Exec Buyer = John Doe; Coverage = 900/1000 = 90 %; Critical Issues = 12 toxic combos; Champion = John Doe post-handoff). Deal Stage Tracker has 4 rows: `cloud=win` ok , `sensor=pov` ok , `defend=discovery` ok , `code=not-active` not ok (should be at least `discovery` - Wiz CLI is integrated in GitHub Actions per 2026-04-12). Section J.8 acceptance covers the metadata fill; Section J.10 adds a per-SKU Deal Stage inference rule that uses `products_discussed` from call-records.

---

## Section I: Drive PATCH-in-place reset (**withdrawn 2026-04-21**; **superseded 2026-04-22** by Section 0.2 and Section 0.5)

**2026-04-21 (historical):** Manual web-UI trash of the folder was considered as a workaround; building a full PATCH client was deprioritized.

**2026-04-22 (historical intent):** Approve **E2E-only** “reset Notes to template” **without** nuclear folder delete: **clear the document body** and **reapply the template body** (ideal: Docs API / `batchUpdate` **in place**). **2026-04-23 (as shipped):** `e2e_rebaseline_customer_gdoc.py` uses Drive **copy+trash+rename** — Notes **`doc_id` may change**; **re-`discover_doc`** after prep. Same-id in-place reset remains **optional** if bookmark stability becomes a priority. Then **local file** prep and **rsync push** (Section 0).

**Nuclear** folder delete (API or web) + **`bootstrap_customer`** remain **optional** (first-time, corrupt state, explicit greenfield) - not the per-iteration default.

**Implication for Section A (`ensure-mount --restart`):** still applies **on paths that** trash/recreate a folder or when the **mount** is empty after a **long** off-line period; the **default** E2E path in Section 0 **avoids** that trifecta so `ensure-mount` is **rare** rather than at every step.

---

## Section J: Content-quality runtime guardrails (Q1 through Q9 remediation, partly landed and partly TODO)

### Section J.1: Call-record validator hardening (LANDED 2026-04-21)

Extended `BANNED_CALL_RECORD_DEFAULTS` in `prestonotes_mcp/call_records.py` with the three wave-2 fingerprints observed on the 22:10 run: `"Capture next steps from call"`, `"Wiz platform"`, `"Security posture"`. Added `_check_no_shortcut_fingerprints` (two checks: `challenges_mentioned[].id at least 25 chars AND kebab-prefix-of-description` then reject; `summary_one_liner` verbatim copy of any `verbatim_quotes[].quote` then reject). Wired into `validate_call_record_object`. Tests added: `test_schema_v2_rejects_wave2_hardcoded_key_topics`, `test_schema_v2_rejects_wave2_generic_action_item`, `test_schema_v2_rejects_shortcut_challenge_id_fingerprint`, `test_schema_v2_rejects_summary_equals_quote`, `test_schema_v2_accepts_legit_short_themed_challenge_id`. Full suite green: 115 passed.

### Section J.2: Lifecycle anchor regex tolerance (LANDED 2026-04-21)

`MARKER_RE` in `prestonotes_gdoc/challenge_lifecycle_parity.py` and `_LIFECYCLE_ID_RE` in `prestonotes_gdoc/update-gdoc-customer-notes.py` now accept both the canonical `[lifecycle_id:<id>]` anchor and the bare `lifecycle:<id>` form (with negative lookbehind to avoid `nonlifecycle:` false positives). Reconciler can now heal older rows written with the shorter syntax. Test added: `test_parity_accepts_legacy_bare_lifecycle_anchor`. Canonical emission at write time is still required (see Section D.3).

### Section J.3: Extract-Call-Records playbook sharpening (TODO)

The playbook already lists banned defaults, MEDDPICC anchors, and field-by-field rules, but the E2E agent still skipped them. Proposed:

- Move the "Banned defaults (hard reject)" callout to the top of Step 6 instead of mid-step, so it's the first thing the agent encounters.
- Add a per-record **self-check** block the agent must write into its chat output before calling `write_call_record` - 4 bullets confirming: (1) `key_topics` are call-specific and not `["Wiz platform", "Security posture"]`; (2) `products_discussed` match the transcript; (3) `summary_one_liner` is a paraphrase not a quote echo; (4) `challenges_mentioned[].id` is a short thematic kebab.
- Add a negative example table in the playbook ("don't do this: `ch-we-want-a-timeboxed-sens`; do this: `ch-sensor-pov`").

### Section J.4: E2E override approval-bypass scope reduction (TODO)

Current `.cursor/rules/11-e2e-test-customer-trigger.mdc` bypasses approval for **all** write operations during the `_TEST_CUSTOMER` E2E. This collapses the Step 7 "Approval gate (mandatory)" of `Extract Call Records` and is where content quality goes to die (the agent ships whatever it generates). Proposed: narrow the bypass to **MCP writes that update customer state** (`write_doc`, `append_ledger_row`, `update_challenge_state`, `sync_notes`); **do not** bypass the `write_call_record` approval gate. The E2E playbook already knows to stop at the gate; just add "proceed" logic that inspects the preview table and, if all records are `high`/`medium` confidence and pass the validator, auto-approves. Any `low`-confidence record should fail the run visibly.

### Section J.5: Retired-artifact + forbidden-vocabulary post-flight (TODO)

Add `scripts/ci/check-e2e-artifact-hygiene.sh` invoked by the E2E playbook after step 10:

- Fail if `MyNotes/Customers/_TEST_CUSTOMER/AI_Insights/_TEST_CUSTOMER-Journey-Timeline.md` exists (TASK-047 retired it).
- Fail if any of `call-records/*.json`, `AI_Insights/*.{md,json}`, or the gdoc body contains any `FORBIDDEN_EVIDENCE_TERMS` term (`TASK-NNN`, `batch A`, `batch B`, `round 1`, `round 2`, `v1 corpus`, `v2 corpus`, `phase`, `E2E`, `harness`, `fixture`).
- Fail if any `call-records/*.json` has `extraction_confidence == "low"` (wave-2 auto-downgrade symptom).

### Section J.6: Minimum-lifecycle-challenge-set guard for `_TEST_CUSTOMER` (TODO)

Add to `scripts/ci/check-e2e-artifact-hygiene.sh`: after E2E completion, assert `challenge-lifecycle.json` has **at least 4 distinct ids** for `_TEST_CUSTOMER` and that the set includes at minimum `ch-soc-budget`, `ch-champion-exit`, `ch-kubelet-noise`, and `ch-acquisition-data-risk`. Drives the extractor toward thematic coverage. Documented in TASK-044 fixture notes.

### Section J.7: Ledger row `round` discriminator (TODO: schema v3 minor bump to 3.1)

Add optional `round` column (`v1` / `v2` / `standalone`) to `LEDGER_V3_COLUMNS` in `prestonotes_mcp/ledger.py`. Backfill on write using `last_ai_update` + round counter in the E2E harness. Non-breaking for real customers (field is optional).

### Section J.8: UCN per-section fill floor + call-type-aware DAL + contact/metadata inference (TODO)

Single umbrella change in `prestonotes_gdoc/update-gdoc-customer-notes.py`:

1. **Fill-rate gate:** after rendering all proposed Block A+B mutations but before `applyChanges`, compute `filled_sections / total_sections` over the 9 Account-Summary-tab sections (Goals, Risk, Upsell, Challenge Tracker, Company Overview, Contacts, Org Structure, Cloud Environment, Use Cases, Workflows, Accomplishments - 11 trackable). Refuse to finalize if fill rate < 60 % **and** the transcript corpus has at least 8 files (i.e. there is ample signal). For `_TEST_CUSTOMER` E2E this tightens to at least 80 %.
2. **Contacts inference:** auto-populate from `stakeholder_signals` in call-records - `signal=sponsor_engaged` then Exec Sponsor; `signal=champion_exit` then Outgoing Champion; `role` + `name` fields flow directly.
3. **Account Metadata inference:** Exec Buyer = latest `sponsor_engaged`; Champion = latest `champion_active` or `new_contact` marked champion; Technical Owner = latest engineer-role participant; Sensor Coverage % = latest `metrics_cited[].metric=="workloads scanned"` then compute `value` as percentage; Critical Issues Open = latest `metrics_cited[].metric in {"toxic combinations","critical issues"}`.
4. **DAL per-call-type template map:** QBR then 4 sections (Coverage & Metrics / Commercial / Risk / Stakeholder Signals); POV kickoff then (Scope / Success Metrics / Budget / Ownership); shift-left working session then (Policy / Exceptions / Owners); commercial close then (Commercial Outcome / Deal Stage Movement / Finance Actions); procurement readout then (Commercial Gates / Evaluation Path / Budget Signals); exec monthly then (Platform Posture / Commercial Reality / Stakeholder Changes). Each template picks from MEDDPICC fields in the underlying call-record.

### Section J.9: DAL prompt configurability (TODO)

Template map in Section J.8.4 lives in `prestonotes_gdoc/dal_templates.yaml` so operators can tune shapes without touching Python. UCN loads it at runtime; fallback to generic 4-section if yaml is missing.

### Section J.10: Deal Stage inference from `products_discussed` (TODO)

In Section J.8, replace the "agent decides Deal Stage Tracker row by hand" logic with an inference: if `products_discussed` across the session's new call-records contains `Wiz CLI` or `Wiz Code`, bump `code` from `not-active` to `discovery` minimum; same pattern for `Wiz Defend`, `Wiz DSPM`, `Wiz CIEM`. The existing bump-up-only rule (never downgrade) stays.

---

## Sequencing refresh (2026-04-21 end-of-day) - **superseded for ordering by "Proposed sequencing (revised 2026-04-22)" above**

**Already landed (this session):** Section J.1, Section J.2.

**Prior 2026-04-21 plan:** Section A (ensure-mount) + Section J.5 + Section F first; assumed manual web trash of folder (old Section I). **2026-04-22 (Section 0):** land the **GDoc rebaseline + prep-v1 / prep-v2** harness first; use **nuclear** reset + manual trash only as escape hatch; Section J.5/Section F still valuable after default path is stable.

**Follow-on sitting (≈ 2 h):** Section B + Section C + Section D.3 + Section E + Section J.3 + Section J.4 + Section J.6. These target **correctness** once the E2E is green mechanically.

**Final polish (≈ 1 h):** Section J.7 + Section J.8 + Section J.9 + Section J.10 + Section H (CI regression tests) + Section G (Account Summary save). These are the content-quality ceiling bumps.

The 22:10 run's failures are distributed across all three sittings; no single fix resolves the "behaves the same as before" symptom. Section J.1 + Section J.2 (landed today) block the most glaring regressions (stub records, silent reconciler no-ops), but a full E2E retest is expected to still expose the Section A / Section J.5 / Section J.6 gaps until those land.
