# Daily Activity Logs — AI meeting summary prepend

This document describes the **only** supported AI write to the **Daily Activity Logs** section of a customer Notes Google Doc.

## Purpose

After Granola sync (transcript + manual notes in `_MASTER_TRANSCRIPT_*.txt`), an LLM or Cursor session can draft a meeting recap. **`Update Customer Notes`** must add one recap per transcript meeting in lookback that is **not** already present in Daily Activity (see `docs/ai/playbooks/update-customer-notes.md` Step 6 / Step 8). The block is inserted on the **Daily Activity Logs** tab (after an **Anchors - …** line when present), ordered **newest meeting date first** among dated **HEADING_3** blocks, without deleting team notes.

## Transcript-availability guardrail

- Only create AI recap prepends when the meeting has substantive transcript content.
- If a meeting block contains `[No Transcript Data]` (or equivalent empty transcript body), **skip** `prepend_daily_activity_ai_summary` for that meeting.
- Do not create placeholders for missing transcripts.

## Schema

- **Section key:** `daily_activity_logs` (H1 **Daily Activity Logs** on the **Daily Activity Logs** document tab — same title as the tab chip; see `prestonotes_gdoc/config/doc-schema.yaml`). Legacy single-tab docs without that tab still anchor the H1 on **Account Summary**.
- **Field key:** `free_text`
- **Action:** `prepend_daily_activity_ai_summary`

## Mutation JSON

One or more prepends in a file; each is applied in order. A mutations file may contain **only** this action to bypass planner key-field coverage checks; **`Update Customer Notes`** normally mixes these objects into the **same** mutations JSON as other sections so one `write` applies the full plan.

```json
{
  "mutations": [
    {
      "section_key": "daily_activity_logs",
      "field_key": "free_text",
      "action": "prepend_daily_activity_ai_summary",
      "heading_line": "### Apr 13, 2026 - AI - Bi-weekly w/ Sapna",
      "body_markdown": "- First bullet\n- Second bullet\n\n### Subtopic\n\n- Detail",
      "evidence_date": "2026-04-13",
      "reasoning": "Post-call AI summary from transcript + Granola manual notes.",
      "source": "granola_transcript_sync"
    }
  ]
}
```

### Field rules

| Field | Required | Notes |
|--------|----------|--------|
| `heading_line` | Yes | One line; optional markdown `###` is stripped in the Doc; the title paragraph uses **HEADING_3** (no literal `###` in the document). |
| `body_markdown` | Yes | Subset: top-level `- **Label:**` / `- **Label**` (label ≤ 72 chars) becomes a **bold** label paragraph with **no list bullet**; same-line text after `**Label:**` is a normal paragraph under it. Leading spaces + `- ` stay **nested bullets**. Other `**bold**` spans apply as usual. In-body `###` prefixes are stripped. **Do not** include transcript or `_Source:` / “paraphrased” footer lines — provenance is only in `reasoning`, `source`, and `evidence_date` (the writer strips common `_Source:` footers if present). Max length `MAX_DAILY_ACTIVITY_AI_BODY_CHARS` in `update-gdoc-customer-notes.py` (200_000). |
| `evidence_date` | Yes | `YYYY-MM-DD` — meeting or summary date (same requirement as other mutating actions). |
| `reasoning` | Recommended | Audit trail. |

### Duplicate guard

If the **normalized** first line of the new `heading_line` (markdown `#` stripped) matches the **normalized** first line of **any** existing Daily Activity paragraph entry, the mutation is **skipped** (prevents double-insert from reruns).

## CLI

```bash
uv run prestonotes_gdoc/update-gdoc-customer-notes.py write \
  --doc-id "<DOC_ID>" \
  --config prestonotes_gdoc/config/doc-schema.yaml \
  --mutations /path/to/mutations.json
```

Use `--dry-run` first. The write path ensures an H1 **Daily Activity Logs** exists on the **Daily Activity Logs** tab when that tab is present (creates a minimal heading if missing). If the doc has no such tab, the H1 is ensured on **Account Summary** instead.

## Meeting summary templates (LLM)

See `docs/ai/references/granola-meeting-summary-templates.md` for the SE/AM runbook (templates **T1–T5**): account, discovery, technical eval, QBR/EBR, general — pick one template per run and trim unused sections before sending to the LLM.

## Related

- Granola sync includes manual notes: `scripts/granola-sync.py` (default: rsync pull → edit repo `MyNotes/` → rsync push on changes; see script header).
- Core guardrail: `.cursor/rules/core.mdc` (Customer notes & MyNotes — TASK-007)
