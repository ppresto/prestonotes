# TASK-059 — UCN Account Metadata component tuning

**Status:** [ ] QUEUED  
**Opened:** 2026-04-22  
**Depends on:** TASK-056

## Goal

Improve accuracy and completeness of Account Metadata updates without inventing values when evidence is absent.

## Scope

1. Tune metadata extraction/mapping from call-records and transcript evidence.
2. Handle partial-signal calls safely (update only what changed).
3. Preserve existing accurate values when no new evidence appears.

## Acceptance

- [ ] Metadata fields update accurately when evidence exists.
- [ ] Unchanged/unsupported fields remain unchanged.
- [ ] Outputs are consistent across diverse customer call patterns.

## Verification

Manual: run UCN on mixed-signal windows and inspect metadata field-by-field.

