---
name: E2E sync hygiene + agent_run_log read parity
overview: Stop local-only call-records from being deleted by pull-before-push, and fix read_doc JSON showing empty appendix.agent_run_log.entries when the Doc writer appended run-log lines.
todos:
  - id: sync-ordering-ssot
    content: Document and enforce push-after-extract before any pull (playbook + optional MCP warning)
    status: pending
  - id: sync-mcp-guard
    content: Optional prestonotes_mcp sync_notes safety check or stderr warning when call-records ahead of Drive
    status: pending
  - id: runlog-read-root-cause
    content: Trace read_doc/parse path for Appendix tab vs Account Summary tab; confirm where agent_run_log lives
    status: pending
  - id: runlog-read-fix
    content: Fix parser or merge so appendix.agent_run_log matches GDoc; extend _heal if needed; runtime stderr if mismatch
    status: pending
  - id: e2e-tester-harness-note
    content: Add one-line to tester-e2e-ucn or 21-extractor to never sync_notes after extract before push
    status: pending
isProject: false
---

# Plan: E2E sync hygiene + `appendix.agent_run_log` read parity

## Context (from recent E2E runs)

- **Call-record “trimming”** — see [FAQ below](#faq-trimming-15-kb); not Cursor-specific.
- **sync_notes before push** — rsync pull can delete repo-only JSON; same class of bug the extract playbook already warns about.
- **read_doc vs run log** — writer appends; `read_doc` JSON sometimes shows `appendix.agent_run_log.entries: []` (partially mitigated by `_heal_appendix_run_log_from_free_text` in `parse_document` on mis-filed bullets).

---

## FAQ: “Trimming … to ≤1.5 KB” {#faq-trimming-15-kb}

**No — it is not for Cursor to read the file.**

- `uv run python -m prestonotes_mcp.call_records lint <customer>` enforces:
  - per-record max **2.5 KB** serialized JSON (`CALL_RECORD_MAX_BYTES` in `prestonotes_mcp/call_records.py` — `write_call_record` rejects over cap);
  - **corpus average ≤ 1536 bytes (1.5 KB)** — if average is higher, **lint exits non-zero** (see `call_records.py` `lint` subcommand around the `avg > 1536` check).
- **Why 1.5 KB:** keep call-record JSON compact so many records fit in downstream context (Account Summary / planning), per TASK-051 / playbook guidance — see `docs/ai/playbooks/extract-call-records.md` and `docs/ai/playbooks/test-call-record-extraction.md`.
- “Trimming a few bytes” in a run means **editing the largest JSON files** (shorter optional arrays, tighter strings) so the **average** passes the gate — **not** a Cursor display limit.

---

## Problem A — `sync_notes` (pull) before push deletes new `call-records`

**Root cause:** `scripts/rsync-gdrive-notes.sh` pull uses `--delete` on the receiver; files that exist only under the repo mirror and not on Drive are removed when Drive is treated as source of truth before those files were pushed.

**Current mitigations (not sufficient alone):**
- `docs/ai/playbooks/extract-call-records.md` Step 1 — push new call-records before next pull.
- E2E `prep-v2` pushes before pull in `e2e-test-customer.sh`.

**Gaps:** Chat flows can still call `sync_notes` in the wrong order; no hard guard in `prestonotes_mcp/server.py` `sync_notes` today.

### Proposed work (Problem A)

| Priority | Action | Files / owners |
|----------|--------|----------------|
| P0 | Re-state **one golden rule** in E2E tester handoff: **after extract, run `e2e-test-push-gdrive-notes.sh` (or equivalent) before any `sync_notes` pull** when new JSON exists. | `docs/ai/playbooks/tester-e2e-ucn.md`, optionally `.cursor/agents/tester.md` §Session |
| P1 | **Optional MCP:** before `sync_notes`, if `call-records/*.json` mtime or hash is newer than last known Drive push, **print a loud stderr warning** (or block behind env flag). | `prestonotes_mcp/server.py` |
| P2 | **Optional:** compare file list vs Drive in a read-only preflight (heavier; may be out of scope). | Future task |

**Success criteria:** E2E runs do not need manual “restore after bad pull” for call-records; or the tool warns first.

---

## Problem B — `read_doc` JSON: empty `appendix.agent_run_log.entries` after successful write

**Observed:** Writer reports appending `appendix.agent_run_log`; `read_doc` / `section_map` sometimes returns **empty** `entries` for that field.

**Likely causes (to confirm in `runlog-read-root-cause` todo):**
- Appendix / Agent Run Log content lives on a **different tab** than the parser’s default Account Summary body.
- **Label line** not matched (parser routes bullets to `appendix.free_text`); **partially addressed** by `_heal_appendix_run_log_from_free_text` in `prestonotes_gdoc/update-gdoc-customer-notes.py` after `parse_document`.
- **Multi-tab merge** (`_merge_tab_section_maps`) may not include Appendix from the tab where the label sits.

### Proposed work (Problem B)

| Priority | Action | Files |
|----------|--------|--------|
| P0 | **Root-cause** with one real doc id: trace `fetch_document` → `parse_document` → which tab’s content includes “Agent Run Log:”. | `prestonotes_gdoc/update-gdoc-customer-notes.py`, MCP `read_doc` if separate |
| P1 | **Fix** parser/merge so `agent_run_log` entries round-trip, or **merge** Appendix from correct tab. | Same + `config/doc-schema.yaml` if label/section |
| P2 | If structure can’t change: **stderr diagnostic** on read when `free_text` has run-log-shaped bullets but `agent_run_log` is empty. | `update-gdoc-customer-notes.py` `read` / MCP layer |

**Success criteria:** After UCN, `read_doc` (with `include_internal` as needed) shows at least the new run-log line in `appendix.agent_run_log.entries` **or** documented as intentionally tab-scoped with a second read path.

---

## Validation

- `_TEST_CUSTOMER` E2E: after step 6 extract, **lint pass** without manual trim unless corpus truly over target; no **unplanned** `sync_notes`-before-push in steps 3/6/7.
- `read_doc` after step 4 and 7: spot-check `appendix.agent_run_log` non-empty or explained.

---

## Out of scope (for this plan)

- Lowering 1.5 KB average (product decision).
- Auto-trimming in `lint` (prefer fixing extraction verbosity).

---

## Related commits / prior art

- Isolated UCN work: `c23878f` (Notes-only lifecycle anchors, appendix run-log **parse heal** for free_text mis-route).
