---
name: E2E step sequence SSoT
overview: "Option A: `e2e-catalog.txt` is the only place for harness step count, numbering, and named modes. E2E tests do not include Account Summary. Post-prep hints read from the catalog. No CI fail on catalog vs shell. Same-PR updates to shell when catalog changes."
todos:
  - id: pick-ssot
    content: "LOCKED: Option A — catalog = canonical step list/numbering; document in e2e-catalog header"
    status: completed
  - id: default-modes-in-catalog-only
    content: "Name default vs optional extended harness modes only inside e2e-catalog.txt; reserved trigger maps to one default mode — no step counts in other files"
    status: completed
  - id: remove-as-from-e2e-refs
    content: "Strip Run Account Summary / Account Summary from E2E test paths (11-e2e, tester-e2e-ucn, e2e-test-customer.sh, tester.md, e2e-catalog triggers/steps) — E2E ends at catalog-defined UCN rounds, not doc-gen playbooks"
    status: completed
  - id: dedupe-11e2e
    content: "11-e2e: point at catalog + playbook; no static numbered step list (or mark non-authoritative; edit catalog only)"
    status: completed
  - id: playbook-align
    content: "tester-e2e-ucn: procedure only; no hardcoded step count in title/intro; defer numbering to catalog + list-steps"
    status: completed
  - id: tester-md-align
    content: "tester.md: reference catalog / list-steps for length — no literal N-step count in description"
    status: completed
  - id: catalog-postprep-blocks
    content: "Add AFTER_PREP_V1_NEXT_CHAT / AFTER_PREP_V2_NEXT_CHAT blocks in e2e-catalog (below HARNESS STEPS/WORKFLOW span); content matches default E2E (no AS)"
    status: completed
  - id: shell-print-after-from-catalog
    content: "e2e-test-customer.sh: print_after_v1/v2 from catalog via awk; same E2E_CATALOG as list_steps"
    status: completed
  - id: shell-run-step-parity
    content: "When catalog step labels change: same PR updates run_one_step + run-step help; max step index comes from catalog, not hardcoded in prose elsewhere"
    status: completed
isProject: false
---

# E2E UCN harness: one SSoT for step sequence (plan only; no file edits in this pass)

## Current state (what exists today)

- **[`docs/ai/playbooks/tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md)** currently frames a **fixed** harness length in the title/intro and duplicates step order claims.
- **[`scripts/lib/e2e-catalog.txt`](scripts/lib/e2e-catalog.txt)** is the **operator SSoT** for `list-catalog` / `list-steps` and workflow mode names. **Only this file** should state how many steps exist and their numeric labels.
- **[`.cursor/rules/11-e2e-test-customer-trigger.mdc`](.cursor/rules/11-e2e-test-customer-trigger.mdc)** re-lists a full static sequence (and may reference non-UCN tails).
- **[`scripts/e2e-test-customer.sh`](scripts/e2e-test-customer.sh)** — `list_steps` reads the catalog; `print_after_*` and `run_one_step` still duplicate text (to be fixed per this plan).
- **[`.cursor/agents/tester.md`](.cursor/agents/tester.md)** may hardcode a harness length in wording — should point at the catalog / `list-steps` instead.

## Answer: was `tester-e2e-ucn.md` already “the one”?

**Partly.** It remains the **procedure** home. **Numbering and how many steps** come **only** from [`e2e-catalog.txt`](scripts/lib/e2e-catalog.txt) (or `./scripts/e2e-test-customer.sh list-steps` output).

## Decision (locked): Option A — catalog is canonical for numbering

**[`scripts/lib/e2e-catalog.txt`](scripts/lib/e2e-catalog.txt)`** = the **only** committed file that may define **how many** harness steps, **order**, **triggers**, and **named default vs extended** modes. Everywhere else: **“see `e2e-catalog.txt` / `list-steps`.”**

**No hardcoded step counts outside the catalog** in: playbooks, rules, agent files, or shell `usage` text (except dynamic text derived from the catalog or a `list-steps` run). The shell may still have a `case` for `run-step` with numeric keys; when the **catalog** adds or removes steps, **same PR** updates that `case` and help strings — the **numbers live in the catalog as source of truth**, not in prose in other docs.

- **`tester-e2e-ucn.md`** = procedure only; no “N steps” in the title/intro. Do not claim SSoT for order against the catalog.
- **`.cursor/rules/11-e2e-test-customer-trigger.mdc`**: point at the catalog’s **default** mode; do not paste a static numbered list as authoritative (or mark non-authoritative).

**Account Summary and E2E:** The **E2E test** flow is **UCN harness + shell prep only** (through the catalog’s defined chat steps for Load / Extract / UCN / repeat). **Do not** reference **Run Account Summary**, **Account Summary** playbook, or “step *n* = Account Summary” in **E2E** playbooks, rules, `e2e-catalog` E2E trigger/steps, or `e2e-test-customer` operator paths. Account Summary (and any similar doc) remains a **separate, non–E2E** workflow if still needed for product, **not** part of “E2E test customer.”

---

## `e2e-test-customer.sh` + catalog (required design — no CI fail, no parser milestone)

**Already catalog-backed:** `list_steps()` / `list_catalog()` read [`scripts/lib/e2e-catalog.txt`](scripts/lib/e2e-catalog.txt) (awk in [`e2e-test-customer.sh`](scripts/e2e-test-customer.sh) ~423–429).

### `print_after_v1` / `print_after_v2` — read from the same `e2e-catalog.txt`

**Goal:** Post-`prep-v1` / post-`prep-v2` “next chat” hints come **only** from the catalog (no heredocs).

**Catalog change:** Add blocks such as `=== AFTER_PREP_V1_NEXT_CHAT ===` and `=== AFTER_PREP_V2_NEXT_CHAT ===` with content that matches the **default E2E** sequence from the same catalog (whatever chat steps follow each shell block — **excluding** any Account Summary / non-UCN step).

Place these **below** the existing `=== HARNESS STEPS` … `WORKFLOW MODES` span so `list_steps` awk is unchanged.

**Shell:** `awk`/`sed` from `"${E2E_CATALOG}"` for those markers. **No** CI that fails on catalog text.

**`run_one_step`:** Keep `case` + `echo` until a later choice; **same PR** as catalog when labels or the **number** of steps changes. Prose in other files must not embed counts — **catalog** does.

## Default harness modes (product intent) — **counts and names only in the catalog**

- **Default E2E (reserved trigger):** The catalog defines one **default** `e2e_workflow` / mode name and **exactly** which steps run for `_TEST_CUSTOMER` — **not** including Account Summary or any “exec summary / AS” chat trigger.
- **Optional extended run:** If product keeps a **longer** path (e.g. extra playbooks), it is a **separately named** mode in the **same catalog** only, not a second set of hardcoded numbers in rules/playbooks.
- **Single line in the catalog header:** states which mode is the default for “Run E2E Test Customer” and that **only** this file holds numeric step data.

**Rule for other files:** they may say **“default E2E mode”** or **“see `list-steps`”** — not “step 7/8” or “omit step N” outside [`e2e-catalog.txt`](scripts/lib/e2e-catalog.txt).

## Files to touch when executing (for later; not now)

1. [scripts/lib/e2e-catalog.txt](scripts/lib/e2e-catalog.txt) — default vs extended **names**; full step table; header line for default mode; **remove** Account Summary from E2E step list and workflow text if present; optional rename of `=== EIGHT STEPS ===` in a follow-up (implementation detail — still only in this file if renamed).
2. [docs/ai/playbooks/tester-e2e-ucn.md](docs/ai/playbooks/tester-e2e-ucn.md) — no numeric harness length in title/intro; no Account Summary in E2E scope; SSoT for **procedure** only, deferring numbers to the catalog.
3. [.cursor/rules/11-e2e-test-customer-trigger.mdc](.cursor/rules/11-e2e-test-customer-trigger.mdc) — trigger → catalog default mode; no pasted numbered list; **no** Account Summary as an E2E step.
4. [scripts/e2e-test-customer.sh](scripts/e2e-test-customer.sh) — `print_after_*` from catalog; `run_one_step` + `run-step` help in sync; help text references catalog / `list-steps` instead of a literal max step in comments outside catalog.
5. [.cursor/agents/tester.md](.cursor/agents/tester.md) — harness length by reference to catalog / `tester-e2e-ucn` + `list-steps`, not a hardcoded count.
6. [`.cursor/plans/`](.cursor/plans) / task docs that still tie AS to E2E — align or defer.

## Anti-patterns to avoid

- Step counts in **non-catalog** docs (`7`, `8`, “optional eighth”, etc.).
- **Account Summary** (or any non-UCN doc playbook) in **E2E** test docs, rules, or catalog E2E sections.
- A **second** full 1–N list in 11-e2e or the playbook that could drift from the catalog.

## Summary

| Role | SSoT content |
|------|----------------|
| **Step list, counts, default mode, triggers** | **Only** [`e2e-catalog.txt`](scripts/lib/e2e-catalog.txt) |
| **Procedure (what each kind of step does)** | [`tester-e2e-ucn.md`](docs/ai/playbooks/tester-e2e-ucn.md) — no numbers, no AS in E2E |
| **Agent trigger** | [`11-e2e-test-customer-trigger.mdc`](.cursor/rules/11-e2e-test-customer-trigger.mdc) — pointer + default mode name, no static duplicate table |
| **Post-UCN quality** | [`tester.md`](.cursor/agents/tester.md) §6 |

This keeps **one numeric source** (the catalog) and an **E2E scope** that **excludes** Account Summary.
