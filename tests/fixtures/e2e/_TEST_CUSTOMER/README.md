# E2E corpus (canonical copy)

This directory is the **durable source** for `_TEST_CUSTOMER` transcript + call-record fixtures used by the E2E flow described in **`docs/tasks/active/TASK-044-e2e-test-customer-rebuild.md`** / **`docs/ai/playbooks/e2e-test-customer.md`**.

## Layout

```text
v1/Transcripts/YYYY-MM-DD-<call-id>.txt
v1/call-records/<call-id>.json

v2/Transcripts/...          # commercial expansion (+2 calls: Cloud PO + Sensor POV)
```

## Intent

- **v1** seeds the baseline corpus: 6+ per-call transcripts and matching call-record JSON objects so **Load Customer Context**, **Extract Call Records**, and **Update Customer Notes** have meaningful input the first time through the flow.
- **v2** layers a commercial expansion on top of v1 (`2026-04-28-wiz-cloud-sku-purchase`, `2026-05-05-wiz-sensor-pov-kickoff`) so round-2 **Extract Call Records** generates new JSON and round-2 **Update Customer Notes** has signal to move **Deal Stage Tracker** / **Account Metadata** and advance challenges (e.g., Splunk renewal lifecycle).
- **v2 intentionally ships transcripts only.** The round-2 **Extract Call Records** step must generate JSON from those transcripts during the test.

## Refreshing fixtures

To resnapshot the current on-disk corpus into `v1/` (use after intentionally improving fixtures):

```bash
uv run python scripts/e2e-test-customer-materialize.py to-fixtures
```

All other entry points for the E2E harness go through the single `scripts/e2e-test-customer.sh <reset|v1|v2>` command described in the playbook.
