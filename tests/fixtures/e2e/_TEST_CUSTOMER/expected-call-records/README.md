# Golden minimum call-records (TASK-051 §E)

One JSON per v1 transcript under `tests/fixtures/e2e/_TEST_CUSTOMER/v1/Transcripts/`.

These are **minimum acceptable** extractions — not strict equality targets.
LLM variance is allowed at runtime, but the extractor's live output for the
`_TEST_CUSTOMER` corpus must meet these minimums before UCN runs:

- Per-call `key_topics` that reflect the transcript subject.
- At least one non-stub `challenges_mentioned` entry per transcript (where a
  challenge is actually discussed).
- `products_discussed` specific to the call (DSPM call → `Wiz DSPM`; shift-left
  → `Wiz Code` / `Wiz CLI`; runtime hardening → `Wiz Sensor`).
- Exec readout / QBR carries `sentiment: cautious` when budget freeze /
  champion exit dominates.
- ≥ 1 `metrics_cited` and ≥ 1 `stakeholder_signals`.
- Every record validates against the v2 schema
  (`prestonotes_mcp.call_records.validate_call_record_object`).

Live extractor output that falls short of these minimums is what the
`python -m prestonotes_mcp.call_records lint _TEST_CUSTOMER` gate is
designed to catch before UCN runs downstream.
