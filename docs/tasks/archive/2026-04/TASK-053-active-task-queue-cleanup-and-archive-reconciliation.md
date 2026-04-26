# TASK-053 — Active task queue cleanup and archive reconciliation

**Status:** [x] COMPLETE (2026-04-22)  
**Opened:** 2026-04-22  
**Depends on:** `docs/tasks/INDEX.md`, `docs/tasks/active/*`, `docs/tasks/archive/2026-04/*`

## Goal

Restore a clean task system with one true active task and an explicit ordered queue.

## Why this is first

Execution quality is blocked when completed work remains in `docs/tasks/active/` and INDEX has multiple active pointers.

## Scope

1. Audit all files in `docs/tasks/active/`.
2. Move completed tasks to `docs/tasks/archive/2026-04/` where appropriate.
3. Keep only real open tasks in `active/`.
4. Update `docs/tasks/INDEX.md` so:
   - one current active task is shown,
   - queued tasks are listed in order.
5. Preserve links and historical references.

## Non-goals

- No runtime code changes.
- No playbook/rule behavior changes.

## Acceptance

- [x] `docs/tasks/active/` contains only open or queued tasks.
- [x] Completed tasks are archived with working links from INDEX.
- [x] INDEX shows exactly one current active task.
- [x] INDEX contains the ordered queue for the UCN tuning wave.

## Verification

```bash
bash scripts/ci/check-repo-integrity.sh
```

