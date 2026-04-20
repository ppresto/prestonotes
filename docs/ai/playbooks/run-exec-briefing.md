# Playbook: Run Exec Briefing

Trigger (exact):

- `Run Exec Briefing for [CustomerName]`

Purpose: produce a **single-page** briefing an executive or manager can read in under two minutes. **Plain language only** — no product jargon, internal codenames, or acronyms the customer did not use. **No internal-only notes** (draft hypotheses, debugging, or “model thinks” language). This is **not** a full account summary; it is the **exec-facing core** described in [`docs/ai/references/exec-summary-template.md`](../references/exec-summary-template.md) (start with **§1 The 30-Second Brief**; add **at most one** compact table from §2 or §3 only if the user explicitly asks for a “one-pager with tables” and it still fits one page).

> **Writes:** None by default. This playbook is **read-only** (MCP reads and local mirrors). Optional **`log_run`** only if the user asks to record the run.

> **Source hygiene:** Prefer **`read_transcript_index`** + **`read_call_records`** + bounded **`read_transcripts`** for quotes; avoid loading legacy **`_MASTER_TRANSCRIPT_*.txt`** wholesale per `docs/project_spec.md` §2.

---

## Communication rule

Tell the user what you are doing in plain English. Start each step with: `"Step X of 5 — [what I'm doing]"`. Follow `.cursor/rules/15-user-preferences.mdc` for formatting.

---

## Step 1 of 5 — Confirm customer and freshness

1. Confirm **`[CustomerName]`** matches **`MyNotes/Customers/[CustomerName]/`** (or use **`list_customers`** / **`get_customer_status`** if unsure).
2. If exports may be stale, call **`sync_notes`** (or run **`./scripts/rsync-gdrive-notes.sh`** from repo root) before deep reads.

**Tell user:** "Step 1 of 5 — Customer context ready."

---

## Step 2 of 5 — Resolve the notes document

1. **`discover_doc`** with `customer_name=[CustomerName]` for **`doc_id`**.
2. If discovery fails, stop with what is missing (sync path, spelling, or bootstrap).

**Tell user:** "Step 2 of 5 — Document identity resolved."

---

## Step 3 of 5 — Read exec-relevant sections

1. **`read_doc`** with the resolved **`doc_id`** (include internal sections only if the user wants internal prep; default **exec-safe** framing).
2. Skim **Account Summary** / exec headings and **Challenge Tracker** only as needed to ground the brief — do not reproduce the entire doc.

**Tell user:** "Step 3 of 5 — Exec-relevant notes loaded."

---

## Step 4 of 5 — Ground in recent facts

1. **`read_ledger`** — last **5** rows unless the user asks for more.
2. **`read_call_records`** — most recent **2–3** calls (dates, types, one-liners) to anchor “where we are” and “next move.”
3. Use **`read_transcripts`** only for a **short** quote if a claim must be verbatim.

**Tell user:** "Step 4 of 5 — Recent calls and ledger grounded the brief."

---

## Step 5 of 5 — Write the one-page exec briefing

Produce output that follows **[`exec-summary-template.md`](../references/exec-summary-template.md) §1** (≤ **3 sentences**, one paragraph): **who they are**, **what problem they care about**, **where they are in the journey**, **one clear next move** — all in language a non-security VP would understand.

- Apply **evidence tags** from `docs/project_spec.md` §7.5 wherever you state a fact.
- If (and only if) the user asked for tables on the same page, add **one** small table from template §2 *or* §3, capped so the **entire** response still fits **one printed page**.

**Tell user:** "Step 5 of 5 — Exec briefing complete."

---

## Done criteria (self-check before you finish)

- [ ] Trigger used exactly: **`Run Exec Briefing for [CustomerName]`**
- [ ] Fits **one page** (brief + optional one small table)
- [ ] **No jargon**; no internal-only commentary
- [ ] **§1 template rules** satisfied (≤ 3 sentences for the opening brief)
- [ ] Evidence tags on material facts
