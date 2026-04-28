---
name: E2E push-before-pull one-liner
overview: Add a single clear line to the E2E harness doc so operators never run `sync_notes` (pull) after extract until new call-records are pushed to Drive.
todos:
  - id: e2e-one-liner
    content: "Add one line to `docs/ai/playbooks/tester-e2e-ucn.md` (or `.cursor/rules/21-extractor.mdc` if better) — after extract, push local call-records before any `sync_notes` pull."
    status: completed
isProject: false
---

# Plan: One-liner — push before pull (call-records)

**Problem:** A `sync_notes` pull before push can remove repo-only `call-records/*.json` (rsync delete on the mirror). Chat flows can still do the wrong order without a visible rule in the E2E harness doc.

**Change:** Add **one line** in [`docs/ai/playbooks/tester-e2e-ucn.md`](../../docs/ai/playbooks/tester-e2e-ucn.md) (Prerequisites or Contract) stating the golden rule: **after extract produces or updates call-records, run the repo push-to-Drive path before any `sync_notes` pull** when that JSON is not yet on Drive.

**Done when:** The playbook reads unambiguously in one line; no other files required for this plan.

**Deferred (not in this plan):** MCP `sync_notes` warnings, `read_doc` / `appendix.agent_run_log` parsing fixes, FAQ on call-record size limits, broader validation steps — track separately if needed.
