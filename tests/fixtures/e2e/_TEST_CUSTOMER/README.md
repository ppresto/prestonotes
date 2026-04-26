# E2E corpus (canonical copy)

This directory is the **durable source** for `_TEST_CUSTOMER` transcript + call-record fixtures used by the E2E flow described in **`docs/ai/playbooks/tester-e2e-ucn.md`** (eight steps; see also archived intent doc **`docs/tasks/archive/2026-04/TASK-044-e2e-test-customer-rebuild.md`**).

## Layout

```text
v1/Transcripts/YYYY-MM-DD-<call-id>.txt
v2/Transcripts/...          # commercial expansion (+2 calls: Cloud PO + Sensor POV)
expected-call-records/      # optional: golden minimum JSON for `call_records lint` / tests (not materialized by apply)
```

## Intent

- **v1** seeds **transcripts only** in `MyNotes/.../Transcripts/`. **Call-record JSON** is not copied from this tree; the **Extract Call Records** playbook produces `call-records/*.json` at runtime.
- **v2** layers a commercial expansion on top of v1 (`2026-04-28-wiz-cloud-sku-purchase`, `2026-05-05-wiz-sensor-pov-kickoff`). **v2** materialize merges **transcripts only**; round-1 call records on disk are preserved.
- **expected-call-records/** (if present) is for regression / lint baselines, not for `e2e-test-customer-materialize.py apply`.

## Refreshing fixtures

To resnapshot the current on-disk corpus into `v1/` (use after intentionally improving fixtures):

```bash
uv run python scripts/e2e-test-customer-materialize.py to-fixtures
```

All other entry points for the E2E harness go through the single `scripts/e2e-test-customer.sh <reset|v1|v2>` command described in the playbook.
