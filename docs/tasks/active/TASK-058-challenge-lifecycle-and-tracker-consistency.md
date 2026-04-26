# TASK-058 — Challenge lifecycle and Challenge Tracker consistency

**Status:** [ ] QUEUED  
**Opened:** 2026-04-22  
**Depends on:** TASK-056

## Goal

Keep lifecycle JSON and GDoc Challenge Tracker consistent over time as challenges are identified, advanced, stalled, resolved, or unchanged.

## Scope

1. Tune challenge extraction and update behavior for stable IDs and transitions.
2. Reduce lifecycle/tracker drift conditions.
3. Preserve valid no-change outcomes when no challenge state moved.

## Acceptance

- [ ] Lifecycle updates reflect real transcript evidence.
- [ ] Challenge Tracker remains aligned with lifecycle states after UCN.
- [ ] No regression on chronology and append-only history guarantees.

## Verification

Manual: compare lifecycle JSON and tracker rows across at least two consecutive UCN runs.

