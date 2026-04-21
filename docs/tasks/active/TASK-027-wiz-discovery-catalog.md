# TASK-027 — Wiz discovery catalog (`win_apis_doc_index.json` + ledger waves)

**Status:** `[x] COMPLETE`  
**Opened:** 2026-04-20  
**Slug:** `task-wiz-discovery-catalog`

---

## Legacy Reference

- **Cache layout:** [`docs/ai/cache/wiz_mcp_server/README.md`](../../ai/cache/wiz_mcp_server/README.md).
- **Index artifact:** [`docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`](../../ai/cache/wiz_mcp_server/win_apis_doc_index.json) (path may be generated — verify in repo).
- **Manager:** [`scripts/wiz_doc_cache_manager.py`](../../../../scripts/wiz_doc_cache_manager.py) (`seed-from-index`, `refresh-loop`, manifest).
- **Protocol:** [`docs/ai/references/wiz-doc-lookup-protocol.md`](../../ai/references/wiz-doc-lookup-protocol.md).

---

## Goal

Maintain a **discovered doc catalog** in **`win_apis_doc_index.json`** and align **refresh / materialization waves** with **ledger** entries (what was refreshed when, and why new URLs appeared).

---

## Deliverable

- [x] Process doc or playbook section: how to **regenerate or extend** `win_apis_doc_index.json` from **wiz-local** `win_apis` (or equivalent) and when to run **`seed-from-index`** / **`refresh-loop`**.
- [x] **Ledger linking:** template line(s) for appending to customer or ops ledger when a wave adds URLs or changes the catalog (reference wave id + manifest diff summary).

---

## Acceptance criteria — “no new URLs in two waves”

Treat as **healthy catalog stability** when:

- [x] **Wave *N* and wave *N+1*** both run with the same discovery inputs (same tenant, same index version) and **no net new doc URLs** enter `win_apis_doc_index.json` / manifest **unless** Wiz shipped new tutorials (expected churn).
- [x] If new URLs **do** appear, they are **classified**: expected product update vs drift / misconfiguration (wrong category, duplicate doc_name). *(No new URLs/doc names observed in evidence run.)*
- [x] **Evidence:** export or diff of manifest + index before/after stored in **`Output / Evidence`** for the run (path or artifact name).

---

## Checklist

- [x] Confirm canonical paths for `manifest.json`, `win_apis_doc_index.json`, and `mcp_materializations/` under `docs/ai/cache/wiz_mcp_server/`.
- [x] Document **minimum** refresh order: index → seed/manifest → materialize (if applicable) → vector ingest (if TASK-031 in use).
- [x] Add **rollback** guidance: restore index from git or known-good backup if a wave poisoned entries.
- [ ] Optional: script or `make` target that prints **URL delta** between two manifest snapshots (future task if not trivial).

---

## Output / Evidence

- **Artifacts:** paths to before/after `win_apis_doc_index.json` or manifest snippets; ledger entry text used.
- **Proof of “two clean waves”:** two dated `refresh-loop` (or equivalent) logs with **zero unexpected new URLs**.
- **Commands (examples):**

```bash
python scripts/wiz_doc_cache_manager.py seed-from-index --help
python scripts/wiz_doc_cache_manager.py refresh-loop --help
```
### Completion evidence (2026-04-20)

- Playbook process section added:
  - `docs/ai/playbooks/load-product-intelligence.md` section `2.53) Discovery wave run order and rollback`
- Two-wave same-input refresh evidence:
  - `uv run python scripts/wiz_doc_cache_manager.py refresh-loop --max-waves 2 --include-all --base-delay-seconds 0.5 --min-delay-seconds 0.5 --max-delay-seconds 1.5 --sleep-between-waves-seconds 0.5`
  - Output (run 1): `wave=1 processed=115 ... remaining_non_cached=44`, `wave=2 processed=115 ... remaining_non_cached=44`
  - Output (run 2): identical wave-level counts and no net-new IDs reported
- Before/after catalog proof from temp snapshots:
  - `/tmp/win_apis_doc_index.before.json` vs `docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`
  - `/tmp/wiz_manifest.before.json` vs `docs/ai/cache/wiz_mcp_server/manifest.json`
  - Comparison output:
    - `index_doc_names_before 51`
    - `index_doc_names_after 51`
    - `index_added 0`
    - `index_removed 0`
    - `manifest_ids_before 115`
    - `manifest_ids_after 115`
    - `manifest_added 0`
    - `manifest_removed 0`
- Ledger linking template added in playbook section 2.53:
  - `WIZ-DISCOVERY-WAVE <YYYY-MM-DD>-<N>: index_delta=+<a>/-<b>, manifest_delta=+<c>/-<d>, decision=<stop|continue>, notes=<why>`
