# Account health score

Source: **`docs/project_spec.md` §9 TASK-012** (verbatim definitions below). The **Run Journey Timeline** playbook that originally owned this rubric was retired by **TASK-047**; the Health line now lives in the optional **Health** section of **`docs/ai/playbooks/run-account-summary.md`**.

Use this rubric in **`Run Account Summary for [CustomerName]`** when you assign a single **Health:** line (see `docs/ai/references/exec-summary-template.md` §1). Pick **one** band: 🟢 Green, 🟡 Yellow, 🔴 Red, or ⚪ Unknown. If bands conflict, apply **the most severe** band that is fully supported by evidence from call records (and optional ledger context).

---

## Definitions (verbatim from spec)

- **🟢 Green:** Active engagement, no stalled challenges, positive sentiment, clear next steps
- **🟡 Yellow:** One of: stalled challenge, missed follow-up, cautious sentiment, unclear next step
- **🔴 Red:** Two or more yellow signals, or: champion departure, competitive threat, budget lost
- **⚪ Unknown:** Fewer than 2 calls or no recent data

---

## Operational notes (non-normative)

- **“Stalled challenge”** aligns with lifecycle **`stalled`** or with §7.4 intent (no movement for 60+ days) when the JSON file does not yet reflect **`stalled`** — cite the dated gap when inferring.
- **“Missed follow-up”** means an **`action_items`** commitment or clear next step from a prior call lacks a later call record or narrative closure by the agreed horizon (cite **`due`** dates and subsequent calls).
- **“Champion departure”** requires evidence in **`participants`** deltas, explicit statements, or role changes across **`read_call_records`** — not rumor.
- **“No recent data”** for ⚪ Unknown: use when you cannot establish a meaningful current-state read (e.g., no calls in a long window and none scheduled in records, or exports are missing).

When in doubt between Yellow and Red, choose **Yellow** unless **two independent yellow-class signals** or an explicit **red-class** signal from the spec list is documented.
