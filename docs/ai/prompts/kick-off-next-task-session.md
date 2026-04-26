# Kick off the next task (reusable session prompt)

**Use when:** you start a new chat or resume work and want the model to **orient**, **summarize**, and **iterate with you** before any large implementation. Replace placeholders in the block below, then paste the whole block into Cursor.

**Related:** [`docs/tasks/INDEX.md`](../../tasks/INDEX.md), [`e2e-task-execution-prompt.md`](e2e-task-execution-prompt.md) (E2E stack order), [`.cursor/agents/tester.md`](../../../.cursor/agents/tester.md) (if the task touches `_TEST_CUSTOMER` / harness / UCN).

---

## Copy / paste — fill `<…>` then send

```text
You are working in the prestonotes repo.

## Current assignment
- **Task ID + slug:** <e.g. TASK-053 — docs/tasks/active/TASK-053-ucn-gdoc-gaps-e2e-sync-hygiene.md>
- **My goal this session:** <one sentence: e.g. “Understand T053-A scope” or “Close acceptance item X”>

## How to work (required)
1. Read `docs/tasks/INDEX.md` (Current active task + any follow-up list) so you know how this task fits the backlog.
2. Read the **entire** assigned task file. Pay special attention to the **“LLM context”** table (*why, pros/cons, how to test this task alone*), **Scope / Non-goals**, **Acceptance**, and **Verification**.
3. If the task is E2E / `_TEST_CUSTOMER` / harness / UCN / call-records: skim **`.cursor/agents/tester.md`** (E2E tester doctrine §3–§6, §10 if lifecycle, plus any section the task file points at).
4. **Do not** implement code or broad doc rewrites in your **first** reply unless I explicitly say “implement now.” First reply is **read-only orientation**.

## First reply format (required — keep it short)
Reply with **only** these sections, in order:

1. **What I read** — Bullet list of files/sections you actually opened (paths).
2. **Task in one paragraph** — What “done” means for this task, in plain language.
3. **What’s already true vs still open** — Bullets: shipped / documented vs unchecked acceptance or TODO bullets in the task file.
4. **Risks or ambiguities** — Max 5 bullets; say what you would clarify with me before coding.
5. **Suggested next step** — One sentence; wait for my go-ahead.

Use **short** bullets. No long code dumps unless I ask.

## Iteration
- I will ask follow-up questions until I understand and validate the plan.
- When I say **“implement”** (or similar), you may change code/docs within the task scope; still summarize **high-level** what you changed before and after substantive edits.
- When I say **“go to the next task”**, you must **first** run the **close-out** process below for the **current** task before picking up a new one.

## Close-out before “next task” (required when I say go to the next task)
For the task we are **finishing**:
1. Confirm **acceptance / verification** items in the task file against reality (commands run, or explicitly “deferred” with reason).
2. Update the **task file** status to match repo convention (`[x] COMPLETE` or leave open with clear remaining bullets).
3. If the task is **complete**: move the file to `docs/tasks/archive/YYYY-MM/` (same month folder as other archives unless I specify otherwise), update **`docs/tasks/INDEX.md`** (remove from “current active” narrative, add archive link, fix any “read before” lines), and fix **broken links** elsewhere (grep task id).
4. Summarize **what was completed** and **what was deferred** in ≤8 bullets for my records.
5. **Then** read `INDEX.md` again and state which task you recommend as **next** (one id + one sentence why).

Begin with the first-reply format now.
```

---

## Optional second paste — “implement now”

After you agree on the plan:

```text
Approved — implement within TASK-XXX scope only. After edits: (1) commands you ran + results, (2) bullet list of files touched, (3) anything you did not do and why.
```

---

## Optional third paste — “go to the next task”

```text
Close out the current task per kick-off-next-task-session.md (verify, update task file, archive if complete, update INDEX, fix links, short summary). Do not start the next task until close-out is done. Then recommend the next task from INDEX.
```

---

## Note on TASK-063 (optional future)

**TASK-052** is **archived** (2026-04-23) under `docs/tasks/archive/2026-04/`. If you later want a dedicated **TASK-063** for “full uninterrupted `Run E2E Test Customer` proof only,” add that task file + **INDEX** row and point deferred bullets from archived **052** / **053** at it in the same change so links stay coherent.
