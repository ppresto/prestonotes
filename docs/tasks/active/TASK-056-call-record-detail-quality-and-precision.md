# TASK-056 — Call-record detail quality and precision

**Status:** [ ] QUEUED  
**Opened:** 2026-04-22  
**Depends on:** TASK-055

## Goal

Improve extraction detail quality in call-record JSON so downstream UCN/ledger updates have richer and more accurate inputs.

## Scope

1. Tune extraction behavior for goals, risks, metrics, stakeholder signals, and deltas.
2. Reduce generic/placeholder content that passes schema but weakens downstream updates.
3. Keep improvements generic for all customers and call types.

## Acceptance

- [ ] New call-records are specific, evidence-grounded, and non-generic.
- [ ] Structured arrays are populated when transcript evidence exists.
- [ ] No regression in valid sparse records when calls are truly low-signal.

## Verification

```bash
uv run python -m prestonotes_mcp.call_records lint <customer>
```

Manual: inspect extracted records across at least two different call patterns.

