# TASK-061 — Ledger over-time event integrity

**Status:** [ ] QUEUED  
**Opened:** 2026-04-22  
**Depends on:** TASK-058, TASK-059

## Goal

Improve ledger row fidelity so event progression over time is coherent, specific, and consistent with lifecycle/call-record evidence.

## Scope

1. Tune ledger row content quality from UCN outputs.
2. Ensure row-to-row progression reflects real account movement.
3. Keep ledger aligned with lifecycle and call-record snapshots for the same period.

## Acceptance

- [ ] Ledger rows capture meaningful, evidence-backed deltas over time.
- [ ] No contradiction with lifecycle or call-record signals.
- [ ] Sparse periods can produce minimal/no-change rows without invented detail.

## Verification

Manual: inspect at least two consecutive ledger rows against source artifacts.

