---
name: UCN lookback batching
overview: "Planned **ucn-prep** tool: both modes **splice** `notes-lite`; **batch** mode also **splits** `_MASTER_*` when found. **(1) Default** — `handoff.json` + no state. **(2) Bundle** — windows, `migration-state.json`, validate under `MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/…`. The UCN playbook does **not** read “only the last 30 days” as a hard rule: it defaults to **1 calendar month** of **meeting-dated** transcript content (per [`customer-data-ingestion-weights.md`](docs/ai/references/customer-data-ingestion-weights.md)). Batched migration (by count or by date range) is **not** first-class today; the MCP `read_transcripts` tool is **newest-by-mtime, capped**—which can disagree with true meeting-date lookback. Supporting your migration workflow needs playbook + weighting reference updates and likely tool/API changes."
todos:
  - id: ssot-window
    content: "Decide default: rolling 30d vs 1 month; document in weights + UCN Step 4"
    status: pending
  - id: read-transcripts
    content: "Design read_transcripts (or new tool): date filter, chrono order, batch offset/limit; or pair with per-call files after normalize script"
    status: pending
  - id: normalize-script
    content: "Split _MASTER_ Granola files: MEETING/DATE/ID/==== blocks; emit YYYY-MM-DD-slug.txt + build_file_body rehydration"
    status: pending
  - id: triggers
    content: Add explicit UCN trigger phrasing for lookback / date range / batch in task-router + playbook
    status: pending
  - id: dal-migration
    content: "Define DAL/ledger rules for multi-run migration (per-batch prepends, cursor) "
    status: pending
  - id: manifest-batch
    content: "Mode 2: time windows (1w/1m/3m/1y), partition sorted corpus, migration-state.json + handoff per bundle"
    status: pending
  - id: implement-ucn-prep
    content: Implement scripts/ucn-prep.py (mode1+split+bundle), notes-lite, handoff.json, --out
    status: pending
  - id: accept-default
    content: "Run default on _TEST_CUSTOMER; validate notes-lite + handoff JSON + stdout; optional pytest golden"
    status: pending
  - id: accept-batch
    content: "Split _MASTER_ fixture; bundle --window 1m and 3m; verify state file + paths under --out"
    status: pending
isProject: false
---

**Workspace copy:** This file is in the repo at **`prestoNotes/.cursor/plans/ucn-lookback-batch-ucn-prep.md`** so you can open it from the file tree. A Cursor-managed copy may also exist under `~/.cursor/plans/`; treat **this path** as the version to link from docs and PRs.

# UCN lookback, batching, and migration — plan (read-only analysis)

## How this relates to other playbooks (Product Intelligence vs Customer Context)

- **[`load-product-intelligence.md`](docs/ai/playbooks/load-product-intelligence.md)** is for **Wiz / product** caches and internal reference material under `docs/ai/cache/`, `MyNotes/Internal/`, etc. It is **not** the home for a **specific account’s** transcript + customer-notes snapshot. Preflight may **rsync** `MyNotes`, but **ingestion scope** there is product-intel paths, not “load this customer for UCN.”
- **[`load-customer-context.md`](docs/ai/playbooks/load-customer-context.md)** is the right playbook for **+4 transcripts / +2 Account Summary (Notes.md) / +1 AI_Insights** with **lookback** — see Step 2 and `customer-data-ingestion-weights.md`. If a thread needs **deep Wiz product** detail, the same playbook’s Step 1 nudges you toward **Wiz MCP** or a pivot to **Load Product Intelligence** — that is a **separate** pass, not a requirement to mix full product sweeps with every UCN.
- **UCN** already assumes **`read_doc`** (current doc truth) + lookback-limited **transcripts** + **targeted** `read_call_records` for pre-lookback pointers — it does **not** require loading the **entire** transcript history on every run.

**Implication for this project:** Put **“what customer files to load, in what order, for a bounded window”** in the **customer / UCN** lane (scripts + `Load Customer Context` + UCN), not inside **Load Product Intelligence**. Product intel stays for **capability, licensing, and Wiz doc** questions.

## Steady-state UCN: is “more transcripts” good or just token burn?

**The concern is partly founded:** context window and cost are real. More text ≠ always better: duplicate or ancient transcripts can **dilute** the model on the **current** call’s delta.

**Practical default (aligned with existing rules):**
- **Always** load current **GDoc / `[Customer] Notes.md`** (structured truth: challenges, contacts, deal stage) — that is the **+2** surface; without it, UCN is blind to what is already in the account story.
- For the **“latest call”** UCN, load **that call’s** transcript in full, plus the **default lookback** rule (e.g. last month) *only if* multiple recent calls need to be reconciled; if there is **literally one** new call since last UCN, **one transcript + doc read** is often enough.
- **Prior** transcripts: use **selectively** — e.g. **last 2–3** per-call files **or** the **single** previous call if the new one **references** open threads, people, or challenges. Full history belongs in **Account Summary** / **read_doc** and **targeted** call-records for older ids, not in loading 50 files every time.
- **Script value for steady state:** the same **index** tool can output a **“UCN prep bundle”** (paths only, sorted): `Notes.md`, `newest 1|N transcripts`, optional `next_older` — so the **LLM does not browse** the tree, but the **model still reads** those files; the script is **orchestrating and trimming the list**, not replacing judgment.

**What a script run can do in one go to reduce *LLM* work (not always fewer tokens):**
- Emit a **fixed list of paths** (and `read_doc` doc id) for “today’s UCN” — no fuzzy discovery.
- Optionally **`--ucn-prep` profile:** `index --customer X --include-notes --transcripts 3 --newest-first` → one JSON/MD the operator or agent pastes.
- For **token savings**, only **deeper** levers work: **smaller N**, **shorter lookback**, or **mechanical extraction** of named entities (risky for quote fidelity — separate product). Prefer **bounded** reads over “load all.”

### Lite data, rich context (proposed operator bundle for steady UCN)

**Goal:** Few sources, high signal, bounded tokens — *not* “every transcript in lookback” unless a migration run demands it.

| Source | Role | Weight ref |
|--------|------|------------|
| **History Ledger** (`*-History-Ledger.md` or `read_ledger`) | **Continuity + prior run / commercial signals**; compact rows. Not a substitute for **live** Challenge Tracker in doc if they diverge. | +1, plus Step 3 / ledger discipline in UCN |
| **`[Customer] Notes.md`** (export ~every 15m) | **Structured account truth** — Exec / Account Summary at top, DAL in the middle, Account Metadata (tab) material often toward the end. | +2 / +3 split by section |
| **“Top + bottom” read strategy** for large `Notes.md` | **Head:** Exec / Account Summary / tables (challenges, contacts, cloud) — what you need for mutations. **Tail:** Metadata / deal fields — for tab parity. **Skip or skim** huge middle (DAL blocks) in *read budget* unless this run’s scope is DAL. Two bounded reads or line ranges. | — |
| **Previous 2 per-call transcripts** (older → newer) | **Thread + people + challenge** continuity into the current call. | +4, bounded |
| **Current call transcript** | **Primary evidence** for this UCN’s writes and quotes. | +4, full (within byte policy) |

**Concrete three-region model (GDoc two tabs in one `.md` export):** The file has **many** `#` headings; navigation is by **known anchor titles**, not “the second H1.”
1. **Region A — Account Summary tab (read):** from the **first** line matching `# Account Summary` through the **line before** the **first** `# Daily Activity Logs`. This includes *all* H1s inside that tab in the export (Exec / Challenge / Contacts / Cloud / …) — not only the literal title `Account Summary`.
2. **Region B — Daily Activity Logs (skip for lite UCN):** from `# Daily Activity Logs` through the **line before** the **first** `# Account Metadata`. Skipped because it grows, repeats headings, and confuses *glance* reads; **include** only when this run’s job is DAL.
3. **Region C — Account Metadata tab (read):** from `# Account Metadata` through **EOF** (in typical exports, **Deal Stage Tracker** and other metadata fields sit here). If the template ever appends more after this tab, adjust the end anchor.

**Script / agent contract:** precompute or document `(start_line, end_line)` for A and C after a scan for anchors (tolerate duplicate `# Account Metadata` lines by taking the **first** Metadata block that starts the tab; export quirks may need a one-line `grep -n` recipe in the playbook).

**Implementation (easiest code):** **One forward pass** over the file (line iteration or `splitlines`), record the **first** line index of `# Daily Activity Logs` and `# Account Metadata` (match normalized headers). **Region A** = lines `[0, dal_start)`; **Region C** = lines `[metadata_start, EOF)`; **no middle** is ever concatenated. This is simpler than a **bottom-up** or **tail-from-EOF** read: reverse scans are awkward in most runtimes, and “read last N lines then find Metadata” is **fragile** if the tail moves. A single pass is **O(n) once** and easy to test.

**Images / embeds at the bottom of `Notes.md`:** Some GDoc → Markdown paths append **image references or base64** after the text (sometimes under or after **Account Metadata**), producing **very long single lines** that blow token limits. **Easy exclusions (in order of simplicity):**
1. **Max line length:** When emitting Region C (or the combined lite bundle), **drop any line** with `len(line) >` a threshold (e.g. **8000–12000** chars). Genuine prose lines are almost always shorter; embeds are often one huge line.
2. **Substrings:** Drop lines that start with or contain **`data:image/`** (data URLs), or standard Markdown **`![`** when you only want text (images are rarely needed for UCN table edits).
3. **Optional end anchor:** If a future export uses a consistent trailer (e.g. a comment `<!-- images -->`), cut Region C at that line — **unreliable** until the export is stable.

Prefer (1) + (2) for a few lines of code and no GDoc shape dependency. If **images** are ever required for ASM/architecture, opt in with a **separate** flag that reads those paths or lines.

**Script assist:** one **`--ucn-prep --lite`** emit this exact path list (Notes.md once or “head+tail” instructions if the tool can’t split), ledger path, 2 priors + current by stem/date — so the model does not discover files ad hoc.

### Two modes: default (steady UCN prep) vs bundle (time-sliced migration)

**Splice (both modes, always):** Build **`notes-lite.md`** from **`[Customer] Notes.md`** — **Region A** (Account Summary tab content through line before `# Daily Activity Logs`) + **Region C** (from `# Account Metadata` through EOF), **skip DAL**, apply image/long-line filters. This is **LLM context** for UCN; **not** the same as transcript split below.

**Split / rename (batch mode only, conditional):** If **`Transcripts/_MASTER_*.txt`** exists, **batch mode** runs **split** first: emit per-call **`YYYY-MM-DD-<slug>.txt`** (Granola **MEETING/DATE/ID/====** → `build_file_body` rehydration), then **time-bucket** the per-call list. **Default mode** does **not** run split; it uses **only** existing per-call `YYYY-MM-DD-*.txt` (and may **warn** if `_MASTER_*` is present: “use bundle mode or run `split`”).

---

**Mode 1 — Default (steady state, no migration state file)**  
**Invocation (example):** `ucn-prep` or `ucn-prep default --customer <Name>`

**Always produces:**

1. **`notes-lite.md`** — spliced **Region A** + **Region C** from `[Customer] Notes.md` (DAL skipped; image/long-line filters).  
2. **`ledger_path`** in **`handoff.json`**.  
3. **`transcript_paths[]`** — default policy: **current + N priors** (e.g. 2) from **sorted** `YYYY-MM-DD-*.txt` (no second copy of `.txt` on disk).  
4. **Stdout JSON** — same payload as **`handoff.json`**.

The script does **not** call the LLM; the **agent `Read`s** the paths. **No** opt-out of `notes-lite` in mode 1.

**“>1 unreviewed” heuristic (no state file):** compare **sorted** transcript stems to **ledger** / DAL dates — see earlier section; mode 1 does **not** write `migration-state.json`.

---

**Mode 2 — Bundle / migration (time windows, stateful, repeat UCN until done)**  
**Invocation (example):** `ucn-prep bundle --customer <Name> --window <period>`  
**`--window`** takes a **fixed menu** of calendar-style buckets, e.g. **`1w` | `1m` | `3m` | `1y`** (exact enum TBD in implementation; may also support explicit `from..to` dates later).

**Behavior:**

1. **Corpus:** sort all per-call transcripts by **meeting date** from filename (`YYYY-MM-DD-…`) (and optional **`transcript-corpus.json`** built **once** at migration start for **stable** ordering and audit).  
2. **Partition** the sorted list into **non-overlapping bundles** by **time** — each bundle = all calls whose dates fall in that **window slice** along the timeline (oldest → newest), e.g. week 1, week 2, … or month 1, month 2, … depending on `--window`.  
3. **State file (required in this mode only):** e.g. **`migration-state.json`** next to the customer (or under `AI_Insights/migration/`) holds: `window` enum, `bundles[]` (id, date range, `transcript_paths[]`), `current_bundle_id`, `completed_bundle_ids`, `corpus_hash`, `updated_at`.  
4. **Per run:** script writes **the same** artifacts as mode 1 **for the current bundle only** — **`handoff.json`** includes `bundle_id`, `transcript_paths` **= only this bundle’s** files, plus **`notes_lite_path`**, **`ledger_path`**. Optional **generated** `customer-state.md` / view for the operator.  
5. **Loop:** operator (or LLM under instruction) runs **UCN** for that handoff → **advances** state to the **next** bundle (`complete-bundle` script step or LLM-updated field + **validation** on next `ucn-prep bundle` run) → repeat until **`current_bundle_id`** is **done** / all `completed`.

**LLM role in mode 2:** Read **`handoff.json`** for the **active** bundle, run UCN **in scope to that bundle’s** `transcript_paths` only, then **update** migration state (or run **`complete-bundle`**) so the **next** invocation of `ucn-prep bundle` yields the next slice. **No** migration state in mode 1.

### Output location, handoff to UCN, standalone validation

**Where output lives (planned):**  
- **Default (no `--out`):** OS temp, e.g. **`/tmp/prestonotes-ucn-prep/<CustomerName>/<run-id>/`** — `notes-lite.md`, `handoff.json`.  
- **Validation / durable runs (this plan):** use **`--out`** for customer **`_TEST_CUSTOMER`** at:  
  **`MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/<run-id>/`**  
  (customer-local “`./tmp/ucn/`” under `_TEST_CUSTOMER`). Same pattern allowed for any customer: **`MyNotes/Customers/<C>/tmp/ucn/…`**.  
- Add **`MyNotes/Customers/**/tmp/`** to **`.gitignore`** (or `**/tmp/ucn/`) if these runs should not be committed.  
- **Override env:** optional **`PRESTONOTES_UCN_PREP_OUT`** same semantics as `--out`.

**How the script hands off to UCN (it does not call the model):**  
1. **Always write** `notes-lite.md` + **`handoff.json`** under the run output dir (see **Output location** above).  
2. **Stdout:** same payload as `handoff.json` (or a compact one-line path to the JSON) for copy-paste.  
3. **No** automatic UCN — **chat** trigger with: “In-scope: read `handoff.json` then `Read` each path.”

**Standalone validation (`_TEST_CUSTOMER`):**  
- **Prereq:** `MyNotes/Customers/_TEST_CUSTOMER/` present; optional `sync_notes`.  
- **Mode 1:** `uv run python scripts/ucn-prep.py --customer "_TEST_CUSTOMER"` (or `default`) → **`notes-lite.md`** + **`handoff.json`** (ledger + priors + current transcript paths) + stdout. **No** `migration-state.json`.  
- **Mode 2:** `... ucn-prep bundle --customer "_TEST_CUSTOMER" --window 1m` → **`handoff.json`** includes **`bundle_id`** + **this bundle’s** `transcript_paths`; **`migration-state.json`** created/updated.  
- **`--dry-run`:** paths + line counts, minimal write.  
- **Tests:** golden **mode-1** `handoff.json`; **mode-2** state transitions; `notes-lite` excludes DAL, includes Summary + Metadata.

**Fixture customer:** quote **`_TEST_CUSTOMER`** in shell: `--customer "_TEST_CUSTOMER"` (leading underscore).

## Implementation and acceptance (build, then verify)

**Deliverable:** one CLI entry (e.g. `scripts/ucn-prep.py`, `uv run python …`), documented in `scripts/README.md` after ship.

**Output path for implementation acceptance runs:** always **`_TEST_CUSTOMER`**, always **`--out`** under:  
**`MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/<subfolder>/`**  
e.g. `.../tmp/ucn/default/`, `.../tmp/ucn/batch-1m/`, `.../tmp/ucn/batch-3m/`. **Golden** test snapshots (if any) may live under **`tests/fixtures/`** instead of the customer tree.

### Phase A — default mode (must pass before batch)

1. **Build** mode-1: `notes-lite.md`, `handoff.json`, stdout JSON, Notes splice + image/length filters.  
2. **Run:** e.g. `uv run python scripts/ucn-prep.py --customer "_TEST_CUSTOMER" --out "MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/default/<run-id>"` (exact flags TBD).  
3. **Assert:**  
   - `handoff.json` has **`notes_lite_path`**, **`ledger_path`**, **`transcript_paths`** (non-empty), **`customer`**, timestamp/schema version.  
   - **`notes-lite.md`:** contains `# Account Summary` and `# Account Metadata`; does **not** include the DAL block between them; no multi-KB “single line” image dumps after filters.  
   - **stdout** JSON matches file JSON or points to the same `handoff.json` path.  
4. **Automate:** a pytest (or script test) with **golden** `handoff.json` snapshot for `_TEST_CUSTOMER` fixture (optional: `--update-snapshots` for refresh).

### Phase B — batch mode + `_MASTER_*` split (must pass with two window sizes)

1. **Fixtures (customer `_TEST_CUSTOMER` only for acceptance):** copy a multi-call **`_MASTER_TRANSCRIPT_*.txt`** (e.g. from [`Discord/Transcripts/`](MyNotes/Customers/Discord/Transcripts/)) into **`MyNotes/Customers/_TEST_CUSTOMER/Transcripts/`** (or a parallel **test fixture** path).  
2. **Splice** runs in both phases (see above). **Bundle mode** additionally **splits** `_MASTER_*` **when found** (per-call files next to or under the same `Transcripts/` tree), then partitions by **`--window`**.  
3. **Run bundle with `--window 1m`:** **`--out`** e.g. `MyNotes/Customers/_TEST_CUSTOMER/tmp/ucn/batch-1m/<run-id>/` — build bundles + **`migration-state.json`**; assert **slice counts**, **`bundle_id`s`, **`transcript_paths`**.  
4. **Run again with `--window 3m`:** **`--out`** e.g. `.../tmp/ucn/batch-3m/<run-id>/` — assert **different** (coarser) bundle partitions; state file **shape** still valid.  
5. **Assert state file** fields: `window`, `bundles[]`, `current_bundle_id`, `completed_bundle_ids` (or equivalent), `corpus_hash`/`updated_at` as designed.  
6. **Handoff** for current bundle: same `notes_lite` + `ledger` + **only** in-bundle **`transcript_paths`**.

**Manual spot-check:** open **`notes-lite`** and **`handoff.json`** in the **validate** output path for one **1m** and one **3m** run and confirm **readable** and **no DAL** in `notes-lite`.

**Done when:** Phase A + B tests pass in CI (or `uv run pytest` locally); README lists **example commands** and the **`--out`** contract.

## What the playbook does today (not “30 days” verbatim)

- **Default window:** **1 month** back from session “today,” using **meeting dates** in transcript files and Daily Activity headings — see [`docs/ai/references/customer-data-ingestion-weights.md`](docs/ai/references/customer-data-ingestion-weights.md) and Step 4 in [`docs/ai/playbooks/update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) (lines 197–206).
- **Overrides in the reference (today):** only **3 / 6 / 12 months** (or phrasing like `Lookback: N months`) — not “30 days,” not “first 5 calls,” not “Jan–Mar then Apr–Jun.”
- The playbook **Purpose** line still says “Reads **all** transcripts” while Step 4 scopes **+4 transcripts to inside lookback only** — those two ideas conflict; the **operational** contract is lookback-scoped for current-state work.

**Important implementation gap — MCP does *not* use a date-parsing script today:** [`read_transcripts`](prestonotes_mcp/server.py) (lines 352–383) does **not** read `DATE:` or split multi-call files. It:

- sorts by **`st_mtime`**, **newest first** (unreliable for true call order, as you noted);
- applies a **`limit`** (default from config, **max 20**), which can **drop entire transcript files** from the returned set — not “cap output size per meeting.”
- for each file selected, it may **truncate body bytes** (`transcript_max_bytes`); that can cut off **the tail of a file** mid-content (still one file in the list), not a clean per-meeting cap.

**Separate path (Granola → Drive):** [`scripts/granola-sync.py`](scripts/granola-sync.py) already writes **one file per meeting** to `Transcripts/`, using the meeting’s date from Granola JSON (`meeting_date_from_doc`) and `YYYY-MM-DD-<slug>.txt` naming — that side does **not** depend on `st_mtime` for meaning. It does not solve **imported** or **legacy bundles** with **several calls in one `.txt`**.

**Optional migration-friendly approach (your idea — not implemented yet):** a **one-off or repeatable script** that:

- parses in-file headers / `DATE:` / delimiters to detect **one vs many calls** per file;
- splits into **per-call** files (filename including **date, time, title** slug), aligned with the repo’s per-call convention;
- then range / count / “next 5” can use **chronological sort of filenames or parsed start times** without trusting OS timestamps, and `read_transcripts` (or a thin wrapper) can list and slice **whole files** only.

**Tradeoffs for splitting script:** heuristics for boundaries (vendors differ); need **idempotency** (re-run should not duplicate); may need a **sidecar** manifest if titles collide on the same day.

### Granola legacy `_MASTER_*` block grammar (example: Discord)

Example files under `MyNotes/Customers/Discord/Transcripts/`: [`_MASTER_TRANSCRIPT_DISCORD.txt`](MyNotes/Customers/Discord/Transcripts/_MASTER_TRANSCRIPT_DISCORD.txt) (at least one block at file start), and especially [`_MASTER_TRANSCRIPT_DISCORD_3.txt`](MyNotes/Customers/Discord/Transcripts/_MASTER_TRANSCRIPT_DISCORD_3.txt) (several calls in one file).

**Record separator (repeat for each call):** a **4-line header** followed by a **line of equal signs**, then **body** until the next line matching `^MEETING:` (or EOF):

1. `MEETING: <title>` — free text; becomes the **title** for slug + `build_file_body`.
2. `DATE: <ISO8601>` — e.g. `2026-04-06T18:59:10.154Z`; use **date part only** `YYYY-MM-DD` for the filename (UTC date of the instant; same as [`meeting_date_from_doc`](scripts/granola-sync.py) style).
3. `ID: <uuid>` — maps to **`granola_meeting_id`** in the output; use for **idempotent** overwrites / `unique_filename` disambiguation (reuse logic from [`unique_filename`](scripts/granola-sync.py) / [`_existing_meeting_id`](scripts/granola-sync.py)).
4. A full line of `=` characters (e.g. `========================================`) — **not** part of the body; body starts on the next line.

**Body** may include `Speaker:` lines, `----------------------------------------`, `MANUAL NOTES (from Granola)`, and other notes — all stay inside that call’s segment until the next `MEETING:`.

**Output naming (match current export):** `YYYY-MM-DD-<slug>.txt` where **slug** = [`slugify_title(title, meeting_id)`](scripts/granola-sync.py) applied to the `MEETING:` title string (after the `MEETING: ` prefix). If the target name exists and the `ID:` differs, append `-<first8 of uuid>` like `granola-sync` does.

**Output *body* format:** Per-call files produced today by [`granola-sync.py`](scripts/granola-sync.py) use [`build_file_body`](scripts/granola-sync.py) — YAML front matter (`granola_meeting_id`, `title`, `granola_synced_at`) + **raw transcript/notes text**, **not** the old `MEETING:`/`DATE:`/`ID:` block. The splitter should **rehydrate** to that shape so new files match the repo standard and tools that read `granola_meeting_id` / [`_existing_meeting_id`](scripts/granola-sync.py) keep working. Optional: `--keep-legacy-block` to emit the old header for a one-time diff; default on should be “same as `granola-sync` output”.

**Validation:** dry-run mode that lists `date`, `slug`, `meeting_id`, and planned path without writing; warn on **duplicate** `ID:` or **missing** `DATE:`/`ID:` in a block.

## Will UCN support batch migration “as-is”?

**Partially, by convention, not by contract:**

- You can **state in chat** a custom long lookback (3/6/12 months) and the **playbook + weights** already allow that.
- You **cannot** rely on a single, crisp contract for:
  - **chronological batches** (oldest 5, then next 5);
  - **arbitrary date ranges** (e.g. Q1 2024 only);
  - **guaranteed complete coverage** of all meetings in a window in one run (because of `read_transcripts` mtime+limit + no date filter).

**Downstream rules that complicate long or batched runs without design work:**

- UCN Step 6/8 expect **one DAL prepend per in-lookback call** that lacks a recap ([`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md) — DAL / meeting recap rules). A **huge** lookback in one run could explode write scope.
- **Challenge / ledger** logic assumes a coherent “what’s new since last run” story; multi-batch migration needs a clear **cursor** (e.g. “processed through date X”) to avoid duplicate or skipped work.

## What would be required: default “last 30 days” + operator overrides

| Layer | Purpose |
|--------|--------|
| **Single source of truth for window** | Update [`customer-data-ingestion-weights.md`](docs/ai/references/customer-data-ingestion-weights.md) and UCN Step 4 to define: **default** = e.g. **rolling 30 days** *or* keep **1 month** and document the difference; **override types** = `days`, `months`, `date_range` (`from` / `to`), and optional `batch` (`max_calls` or `chronological_slice`). |
| **Trigger surface** | Extend task-router / playbook triggers (e.g. `Update Customer Notes for [Customer] with lookback: 90d` or `... transcript batch: 2024-01-01..2024-03-31`) so the session **binds** parameters without ad-hoc chat only. |
| **MCP / reads** | Extend [`read_transcripts`](prestonotes_mcp/server.py) (or add a sibling tool) to support **meeting-date** ordering and filtering: parse `DATE:` (or existing headers) from **per-call** files, return **all** in range (or **offset/limit** in **chronological** order for “next 5”). Cap **size** with **per-file** byte limits without silently skipping whole files in-range — or rely on a **pre-step** normalization script so every on-disk unit is one call. |
| **Transcript normalization (migration)** | New script: split multi-call `.txt` into per-call files with stable naming; document when to run (before UCN batch migration). Optional: dry-run and diff report. |
| **Orchestrator** | Mirror the same contract in [`.cursor/rules/20-orchestrator.mdc`](.cursor/rules/20-orchestrator.mdc) Step 1–2 so `sync` + `load` steps use the same window and don’t reintroduce “read everything.” |
| **DAL + writes** | For migration batches, decide: only **prepend DAL** for calls **in this batch**; or **split** “migration UCN” vs “steady-state UCN” so one playbook variant skips bulk DAL until the doc is caught up. |
| **Tests / fixtures** | Add MCP tests for date-sorted and ranged reads; optional playbook examples for “batch 2 of N.” |

## Recommendation

Treat “default last 30 days + user-set window” as a **product contract** change: **docs + rules + `read_transcripts` behavior** together. Without tool support, “first 5 by **call date**” will stay **brittle** even if the playbook text says the right thing.

Plan updates only (no product code) — roadmap evolves with this file.

---

## Beyond split: one tool can do batching, manifests, and resumable state

The same **transcript-migration** script (or a small **family** of subcommands) can do more than **normalize** `_MASTER_*` into `YYYY-MM-DD-*.txt`.

### 1) What else the script can do (recommended surfaces)

| Mode / output | Role |
|---------------|------|
| **`split` / `normalize`** | As already planned: multi-call → per-call, `build_file_body` rehydration. |
| **`index` / `manifest`** | Scan `Transcripts/*.txt` (after split), **sort by call date** (from filename + optional YAML `granola_meeting_id` / front matter), write **`transcript-corpus.json`** (or `.md` table) — **source of truth** for order and file paths. No LLM required to “remember” order. |
| **`batch-plan`** | Given `manifest` + `--by-date <from>..<to>` *or* `--by-count 5` + `--offset N`, print **the exact list of files** in this batch (and optional **single-line** `read_transcripts` is still wrong for this; the operator pastes paths or a small MCP reads explicit paths). |
| **`print-next`** | Read **machine-owned state** (see below) and print “next 5 file paths + suggested UCN trigger line” (copy-paste for chat). |
| **Dry-run / diff** | List collisions, out-of-order files, files missing parseable date in name. |

So yes: the script can **batch** and **emit the ordered list** the LLM (or the operator) should use. Prefer **JSON manifest + script slicing** over asking the model to re-derive order from a folder listing.

### 2) `state.md` vs machine-owned state (avoid “LLM forgot the next step”)

**Problem:** A free-form `state.md` that only the LLM updates will **drift** (format errors, wrong next index, lost on token trim).

**Better pattern:**

- **Canonical state:** `migration-state.json` (or `*.yaml`) under e.g. `MyNotes/Customers/<C>/AI_Insights/migration/` (or a dedicated non-synced path if you want zero Drive churn) with **strict fields**: `version`, `customer`, `corpus_fingerprint` (hash of manifest), `batch_size`, `cursor` (index into sorted manifest, or `last_completed_meeting_id`), `completed_ranges` (list of `from..to` or `file_stems[]`), `updated_at`.
- **Human/LLM-facing mirror:** generate **`state.md` from the JSON** after each **script** step (or on demand). The **LLM may append a “session log”** section, but the **only trusted “next step”** is re-derived by running `print-next` (or the script re-reads JSON, advances `cursor` only on **explicit** `complete-batch` with validated file list).
- **Append-only run log (optional):** `migration-runs.log` with one line per UCN batch: `ISO8601 batch=3/12 files=… ledger=ok` — good for forensics, not for control flow.

**If you still want the LLM to “tick” state:** have it call a **constrained** block (e.g. only update one line `next_cursor: 15`) in a file **validated** by a script on next run — more fragile; prefer **script updates JSON** after the operator (or CI) says “batch 2 done.”

### 2b) Ephemeral `customer-state.md` in `/tmp` (LLM contract — single run)

**When it fits:** One Cursor session (or a short sequence the same day). **`/tmp` is OK** if you accept: reboot / different machine = **no resume** from this file; **recovery** = re-run `index` + `print-next` from the repo (manifest on disk) to rebuild.

**Principles**

1. **One source of batch truth in the file:** a **script-written** block the model **must not** rewrite (or it invalidates the plan). The LLM only edits a **clearly delimited** section.
2. **Stable headings** (fixed `##` order) so the model can `search` / follow instructions: “Update only *LLM* section below.”
3. **Narrow write surface:** 2–4 bullets max per cycle — e.g. `Status`, `This batch done (yes/no)`, `Next step after user confirms`.
4. **No tables for control flow** unless the script also emits them; prefer a **bulleted list of file paths** for the current batch.

**Suggested structure (template)**

```markdown
# Batched UCN — <CustomerName>

## Script block (do not edit — machine-owned)
- Manifest: <path in repo, or sha>
- Batch: <k> of <n>  |  cursor: <i>  |  mode: <by-count|by-date>
- In-scope files (this batch):
  - `MyNotes/Customers/.../Transcripts/...`

## Instructions for the assistant
1. Use **only** the in-scope file list above for transcript evidence in this UCN.
2. After a successful UCN (writes done), set **LLM** → Status to `batch_done` and fill **LLM** → Summary (one line).
3. Do **not** change **Script block**. Tell the user to run: `<complete-batch or print-next command>`.

## LLM (edit below this line)
### Status
`pending` | `running` | `batch_done` | `blocked`

### One-line summary of this batch
<empty until done>

### User must run next
<paste: print-next / complete-batch, or "none — migration complete">

## Session log (append only)
- <timestamp> — …
```

**Regeneration each batch:** Prefer the **script re-write** the whole `customer-state.md` in `/tmp` on each `print-next` (fresh Script block + empty LLM section) so the model does not carry **stale** batch lists across cycles.

**If you need survive reboot:** use the same template under the repo, e.g. `MyNotes/.../AI_Insights/migration/customer-state.md` — not `/tmp`.

### 2c) What the LLM knows: **within** a batch vs **next** batch; one file for the whole migration

**Within one batch (same UCN run)**  
The default design is: **one UCN = one batch** = the **entire** “in scope” file list in the Script block. The model **does not** need a “next transcript inside the batch” pointer: it should treat **all listed paths** as **+4 evidence** for that run (in chronological order if the instructions say so). UCN’s internal steps (read → plan → write) are the playbook, not a per-file state machine.  
*If* a single batch is too large for context, **fix the batching** (smaller `N`, or a date sub-window) — not an LLM-maintained “file 2 of 5 in batch” file unless you explicitly add **sub-batches** to the state machine.

**How it knows the *next* batch**  
It **does not** hold that in long-term memory. After a batch finishes, the **user runs a script** (`complete-batch` then `print-next`, or a combined step) that **increments** a global `cursor` in **one migration state** and **regenerates** the view file. The *next* batch is whatever the script writes into the new Script block — until then, the LLM should say: “Run `print-next` to load the next batch” rather than guess.

**Single state file for the full migration?**  
**Yes — that is the right shape.** One **canonical** `migration-state.json` (or equivalent) for the customer+manifest that always holds: `corpus` id / hash, `cursor` (or `offset`), `batch_size` or batch rule, `status`, `updated_at`, optional `completed_batch_ids` / `last_ucn_run_id`. The **`customer-state.md` in /tmp** is a **view** of *this chunk* of work (current batch’s file list + LLM section), not the long-term SSoT — or it is **rebuilt from** the JSON each time. That way “what is the next batch?” = **read state JSON** (or re-run `print-next`), not **ask the model**.

**Flow in one line:** `print-next` writes “batch *k* of *n* + file list” → LLM runs UCN for **that** list only → `complete-batch` moves cursor → `print-next` again for batch *k+1* (or “done”).

### 3) Best process: batched migration UCN (high level)

1. **Normalize once:** split all legacy `_MASTER_*` → per-call; fix any manual naming gaps; **build manifest** (`index`).
2. **Decide DAL policy for migration:** either (a) **UCN (migration profile)** = lookback = **this batch’s date range only** + DAL prepends only for those calls, or (b) a documented **“defer DAL”** mode until the corpus is in the doc — product decision; align with **DAL** rules in [`update-customer-notes.md`](docs/ai/playbooks/update-customer-notes.md).
3. **For each batch:** `sync_notes` (pull) → **read only the batch’s files** (by path from manifest) + normal `read_doc` / ledger → UCN with **explicit in-chat scope**: “In-scope transcript files: [list]” (or a playbook variant) → writes → `sync_notes` (push) if you need Drive **and** local aligned.
4. **Advance state:** `complete-batch` updates `migration-state.json` and regenerates `state.md`; run **`print-next`** to confirm the next batch.
5. **Stop** when `cursor` reaches `len(manifest)`.

**Why not one giant lookback?** DAL explosion, context overflow, and ledger narrative harder to keep honest — **batches** keep each UCN bounded and auditable.

**Chunking rules:** by **chronological** order (oldest → newest) for migration is usually best so the GDoc and ledger “grow” in story order; by **date windows** (e.g. 3 months) matches your earlier ask and maps cleanly to manifest date filters.

### 4) What the script does *not* replace

- **UCN itself** and **`write_doc`** still run in **Cursor** with MCP; the script **does not** replace the playbook — it **feeds** scope and resumable bookkeeping.
- **Extractor / call records** for historical calls: optional separate passes per [`extract-call-records.md`](docs/ai/playbooks/extract-call-records.md); the manifest can mark `call_record_status` per file when you add that.

Plan updates only — no implementation in this pass.
