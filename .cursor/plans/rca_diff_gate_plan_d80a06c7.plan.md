---
name: UCN Context Coverage Plan
overview: Minimal, high-impact prompt/playbook edits only: tighten UCN evidence-to-section routing instructions so required sections are explicitly evaluated every run, while preserving existing preflight mutate-or-skip semantics.
todos:
  - id: tighten-ucn-read-path
    content: Add concise must-check evidence cues in update-customer-notes.md so UCN explicitly evaluates challenge/contact/cloud/metadata/DAL sections before planning mutations
    status: pending
  - id: tighten-ucn-section-coverage
    content: Add a compact evidence-routing checkpoint table in update-customer-notes.md requiring mutate-or-evidence-backed-skip per critical section
    status: pending
  - id: add-must-keep-instruction-set
    content: Keep one canonical checklist block in update-customer-notes.md and remove duplicated wording elsewhere by linking to it
    status: pending
  - id: preserve-preflight-contract
    content: Keep one-line clarification in update-customer-notes.md and tester-e2e-ucn.md that preflight is coverage accounting (not sufficiency)
    status: pending
isProject: false
---

# UCN Context and Data Completeness Plan

## Goals
- Keep `ucn-planner-preflight` behavior as-is: it validates section coverage decisions (`mutate` or `skip`) and does not force writes when evidence is absent.
- Reduce missed context in `Update Customer Notes` so the model consistently uses all relevant in-scope evidence.
- Improve section mapping quality (especially Contacts, Challenge Tracker, Cloud Environment tools, Account Metadata, and Daily Activity) without adding new tooling.

## Scope of Changes
- Update only existing prompt/playbook files already in the flow.
- No new rules, no new files, no script changes.
- Keep harness scope unchanged (1–5; no extraction/summary re-add).

## Implementation Steps

### Step 1 — Highest-impact UCN prompt edit (single canonical block)
- Update [`/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/update-customer-notes.md`](/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/update-customer-notes.md):
  - Tighten Step 4/6 language so model must explicitly check all relevant sources before Step 8 planning.
  - Add concise “must-check evidence cues” for the observed miss set: named stakeholders, challenge language, tool names, metadata signals, DAL meeting blocks.
  - Keep existing lookback and mutate-or-skip behavior unchanged.

### Step 2 — Add explicit evidence-routing checkpoint (same file)
- In the same playbook, add one compact checkpoint table requiring, for each critical section, either:
  - mutation planned, or
  - evidence-backed skip reason tied to the transcript cue.
- Critical sections in checkpoint:
  - `challenge_tracker`
  - `contacts.free_text`
  - `cloud_environment` tool buckets (`platforms`, `devops_vcs`, `security_tools`, `aspm_tools`, `ticketing`, `languages`)
  - `account_motion_metadata`
  - `daily_activity_logs`

### Step 3 — Minimal anti-duplication pass
- Update wording only in existing docs that mention validation:
  - [`/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/update-customer-notes.md`](/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/update-customer-notes.md)
  - [`/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/tester-e2e-ucn.md`](/Users/patrick.presto/Projects/prestoNotes/docs/ai/playbooks/tester-e2e-ucn.md)
- Explicitly distinguish:
  - planner preflight = section coverage accounting (`mutate` or valid `skip`)
  - UCN planning quality = complete evidence scan and correct section routing
- Ensure other docs point to the single canonical checklist block instead of repeating it.

## Validation Plan
- Review updated UCN instructions against the recent miss set:
  - Contacts blank despite names in transcripts
  - Challenge Tracker empty despite challenge language
  - Cloud tool fields under-filled despite explicit tool mentions
  - Metadata fields missing despite explicit statements
  - DAL recap parity misses
- Confirm instructions still allow valid `skip` when evidence truly does not exist.

## Risks and Mitigations
- Risk: over-constraining language could force low-quality writes.
  - Mitigation: preserve mutate-or-skip contract and evidence-threshold language.
- Risk: instruction duplication across files.
  - Mitigation: keep detailed read/routing guidance centralized in `update-customer-notes.md`; other files reference it briefly.

## Deliverables
- Updated prompt/playbook files only (no new files/rules/scripts).
- One canonical, compact must-check + evidence-routing checkpoint in `update-customer-notes.md`.
- Preserved preflight mutate-or-skip contract with stronger anti-omission instructions.