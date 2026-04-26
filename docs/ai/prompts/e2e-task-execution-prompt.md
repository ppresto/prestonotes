# LLM prompt: execute the next E2E-related task

**Use when:** you want a Cursor/Chat agent to pick up **TASK-053** (or other E2E work) in a defined order, without re-negotiating scope. **MCP:** before deep E2E, follow **Session init** in [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) (MCP smokes + fail-fast).

---

## Preferred order (E2E stack we defined)

`docs/tasks/INDEX.md` may show **multiple active** tasks; for **E2E work**, still pick **one** primary E2E task to advance per session. Default execution habits: [`.cursor/rules/core.mdc`](../../../.cursor/rules/core.mdc). (Historical subagent packet templates, if needed: [`docs/archive/cursor-rules-retired/workflow.mdc`](../../../docs/archive/cursor-rules-retired/workflow.mdc).) Tackle in this order:

| Order | Id | What it delivers | Why this sequence |
| ---: | --- | --- | --- |
| **0** | *(prerequisite)* | Read [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) + [`docs/tasks/INDEX.md`](../../tasks/INDEX.md) | Vision, layers, eight-step relationship, **post-write diff §6** (mandatory rows: Contacts, Challenge Tracker, Cloud Environment, Account Metadata for `v1_full`/`full` — **TASK-069**), plus **§6.1 DAL parity** (`N` transcripts vs `M` DAL meeting blocks — **TASK-071**), task lifecycle §2. |
| **1** | [**TASK-053**](../../tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md) | UCN/GDoc fill, **sync order** recipes, per-gap manual tests **T053-A–G** | Primary **TOC** for E2E quality. |
| **2** | [**TASK-044**](../../tasks/archive/2026-04/TASK-044-e2e-test-customer-rebuild.md) | *(archived 2026-04-24; harness work landed outside this file)* | Historical spec; current eight-step SSoT is **`tester-e2e-ucn.md`**. |

**Next task to execute (default):** **TASK-053** (unless `INDEX` marks a different “current” focus).

---

## Copy / paste: prompt for the LLM (fill `<TASK_ID>`)

```text
You are working in the prestonotes repository.

1) Read in order (skim is OK for parts you already know, but do not skip the “LLM context” table in the task file):
   - .cursor/agents/tester.md (§4 workflows, §5 quality loop, §6 post-write diff, §10 Challenge Tracker if debugging lifecycle)
   - docs/tasks/active/TASK-<TASK_ID>-*.md (entire file; pay special attention to “LLM context — Why are we doing this? / pros / cons / test this task alone”)
   - docs/ai/playbooks/tester-e2e-ucn.md if the task touches harness steps or push/pull order
   - docs/project_spec.md §2 and §9 if schema or product boundaries are unclear

2) Operating rules:
   - Stay inside TASK-<TASK_ID> scope; do not refactor unrelated code or add docs the task does not require.
   - _TEST_CUSTOMER is test data only; do not add fixture-only behavior to production paths.
   - Any write to Google Docs / Drive: prefer dry_run first, then user-approved live writes.
   - If the task needs Drive: require GDRIVE_BASE_PATH mounted; for prep-v2, follow push-before-pull (see tester-e2e-ucn.md step 5 parity) before any pull/sync_notes.

3) Work plan:
   - State the single outcome this session will complete (one acceptance bullet or one subsection of the task).
   - List commands you will run (from the task’s verification / “test this task alone” section). Run them; fix failures; repeat until green or until you hit a blocked dependency (then state the blocker exactly).

4) End with:
   - What changed (files, behavior).
   - What is left for TASK-<TASK_ID>.
   - Whether the next run should be the same task (remaining scope) or the next id in the preferred order: **053** → **044** (when off hold).
```

**Example:** set `<TASK_ID>` to **`053`** and open `TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md`.

---

## One-liner variant (minimal)

```text
Execute `docs/tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md`: read its “LLM context” block and the next **T053-*** sub-task; validate using **`.cursor/agents/tester.md`** §8 and §6. Harness step order: `docs/ai/playbooks/tester-e2e-ucn.md`.
```

Swap the filename to **053** or **044** when you are ready to move on.
