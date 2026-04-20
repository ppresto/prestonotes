# Call type taxonomy (extractor)

Canonical enum values match **`project_spec.md` §7.3** and **`prestonotes_mcp/call_records.py`** (`_CALL_TYPES`). The extractor **`call_type`** field must be exactly one of these strings.

## Types

| `call_type` | When to use | Signals to use | What to extract first |
|-------------|--------------|------------------|------------------------|
| **`discovery`** | First 1–2 substantive customer calls; problem framing, vendor evaluation early | New stakeholders, “current state” tours, pain lists, no prior Wiz contract narrative | Pain points, org map, stack, decision process, success criteria |
| **`technical_deep_dive`** | Architecture, security design, integration, POC scoping | Deep dives on APIs, agents, network, IaC, data flow; SE-led whiteboarding | Requirements, constraints, environments, risks, POC scope |
| **`campaign`** | Ongoing relationship after initial wins; cadence calls | Standing attendees, status sections, “since last time”, ticket throughput | Deltas vs prior call, challenge state changes, action item follow-ups |
| **`exec_qbr`** | QBR, business review, renewal prep with execs | SVP/CISO/VP outcomes, roadmap slides, value metrics, renewal dates | Value realized, strategic alignment, risks, expansion signals |
| **`poc_readout`** | POC results readout or decision meeting | Findings deck, “results”, go/no-go, remediation backlog | Customer reaction, blockers, next phase, commercial hints |
| **`renewal`** | Commercial renewal / true-up / SKU expansion | Pricing, contract end, competitive bids, legal/procurement | License scope, expansion SKUs, risk to renewal |
| **`internal`** | Wiz-only prep or planning (no customer on line) | “Internal”, prep for customer, AE/SE sync without customer | Strategy only — not customer-facing facts unless clearly labeled as customer-sourced from another artifact |

## Edge cases

1. **Exec joins a technical deep dive:** If the primary agenda is technical, use **`technical_deep_dive`**; put exec quotes in **`verbatim_quotes`** and exec concerns in **`key_topics`**. Upgrade to **`exec_qbr`** only when the meeting is **framed** as a business review / renewal / value ceremony.
2. **Customer + partner on the line:** Classify by **primary buyer** intent. Note partner in **`participants`** with accurate `company`.
3. **Support / break-fix:** If it is **incident-oriented** but with customer staff, prefer **`campaign`** (ongoing ops) unless it is clearly a **POC** decision — then **`poc_readout`** or **`technical_deep_dive`**.
4. **Multiple meetings in one `.txt`:** Rare if Granola per-call export is used. If headers show two distinct `MEETING:` / `DATE:` blocks, split into **two** call records with distinct **`call_id`** values and the same **`raw_transcript_ref`** only if both meetings share one file — otherwise prefer splitting files upstream.

## Anti-patterns

- Do **not** label customer-facing calls **`internal`**.
- Do **not** use **`discovery`** for call 10+ just because topics are “new” — long-running accounts usually want **`campaign`** or **`exec_qbr`**.
- Do **not** invent **`renewal`** without explicit commercial or contract language in the transcript.

## Filename hint (Granola → MyNotes)

Per **`scripts/granola-sync.py`**, per-call files are typically:

`Transcripts/YYYY-MM-DD-<slug>.txt` (with optional `-<8char>` suffix if titles collide).

Use the **basename** as **`raw_transcript_ref`**.
