# E2E corpus (canonical copy)

This directory is the **durable source** for `_TEST_CUSTOMER` transcript + call-record fixtures used by the E2E flow described in **`docs/ai/playbooks/tester-e2e-ucn.md`** (eight steps; see also archived intent doc **`docs/tasks/archive/2026-04/TASK-044-e2e-test-customer-rebuild.md`**).

## Layout

```text
v1/Transcripts/YYYY-MM-DD-NN-<slug>.txt   # NN = 01–06 (narrative order)
v2/Transcripts/YYYY-MM-DD-NN-<slug>.txt   # NN = 07–08 (commercial expansion)
```

**Order:** `NN` is a two-digit sequence. **v1** per-call files use **`01`–`06`**; **v2** adds **`07`** (Wiz Cloud enterprise close) and **`08`** (Sensor POV kickoff). Lexicographic sort by date + `NN` matches story order. **`_MASTER_TRANSCRIPT__TEST_CUSTOMER.txt`** is a bundle and is not part of the `01`–`08` series.

## Intent

- **v1** seeds **transcripts only** in `MyNotes/.../Transcripts/`. **Call-record JSON** is not copied from this tree; the **Extract Call Records** playbook produces `call-records/*.json` at runtime.
- **v2** layers a commercial expansion on top of v1 (`2026-04-28-07-wiz-cloud-sku-purchase`, `2026-05-05-08-wiz-sensor-pov-kickoff`). **v2** materialize merges **transcripts only**; round-1 call records on disk are preserved.

## Refreshing fixtures

To resnapshot the current on-disk corpus into `v1/` (use after intentionally improving fixtures):

```bash
uv run python scripts/e2e-test-customer-materialize.py to-fixtures
```

All other entry points for the E2E harness go through the single `scripts/e2e-test-customer.sh <reset|v1|v2>` command described in the playbook.
