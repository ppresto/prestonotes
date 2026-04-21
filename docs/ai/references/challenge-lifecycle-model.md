# Challenge lifecycle model

Canonical states and diagram: **`docs/project_spec.md` §7.4**. Persistence and MCP behavior: **`prestonotes_mcp/journey.py`**, tools **`update_challenge_state`** (write) and **`read_challenge_lifecycle`** (read) in **`prestonotes_mcp/server.py`**.

---

## States (§7.4 vocabulary)

| State | Meaning (for synthesis) |
|-------|---------------------------|
| **`identified`** | First surfaced in discovery / early calls; customer may not yet agree it is a priority. |
| **`acknowledged`** | Customer agrees the problem is real and worth addressing. |
| **`in_progress`** | Active work: POC, remediation, internal alignment, or recurring technical motion tied to the challenge. |
| **`resolved`** | Outcome achieved or problem no longer applicable; close the loop with evidence. |
| **`reopened`** | Was resolved; new evidence shows recurrence or scope expansion. |
| **`stalled`** | No material progress for an extended period (diagram: **60+ days** without movement). |

On-disk JSON: **`MyNotes/Customers/<Customer>/AI_Insights/challenge-lifecycle.json`** — per challenge id: **`current_state`** and append-only **`history`** entries `{ "state", "at", "evidence" }`.

---

## Lifecycle diagram (from spec §7.4)

```
identified → acknowledged → in_progress → resolved
                                ↑               ↓
                             reopened ←────────┘
                                
in_progress → stalled (if no movement for 60+ days)
```

---

## How call records map to transitions

Per-call JSON (**`docs/project_spec.md` §7.1**) carries **`challenges_mentioned[]`** with **`id`**, **`description`**, and **`status`**.

| Signal in call records | Typical transition |
|------------------------|---------------------|
| New **`challenges_mentioned`** id first appears | Treat as **`identified`** (or **`in_progress`** if the transcript shows active work already underway — cite evidence). |
| Customer agrees / prioritizes the pain | `identified` → `acknowledged`, or skip to `in_progress` when the transcript justifies skipping acknowledgment. |
| Active POC / workshops / engineering work on the theme | Move toward or reinforce **`in_progress`**. |
| Confirmed outcome, shipped fix, or explicit “solved / not pursuing” | Toward **`resolved`**. |
| Recurrence after resolution | `resolved` → `reopened` → `in_progress` path. |
| Long gap with no progress and no scheduled follow-through | Toward **`stalled`** (prefer explicit customer tone or dates; align with playbook 60-day rule). |

**Stable ids:** Reuse the same **`ch-…`** id across calls when the narrative clearly refers to the same underlying challenge. If two ids describe one problem, pick a **canonical** id in the timeline narrative and propose **`update_challenge_state`** only for the canonical id; note the alias in markdown (do not invent merges without user confirmation).

**Synthesizer rule:** When your timeline **fixes** lifecycle state drift (e.g., call record **`status`** inconsistent with dates), present a **table** of proposed **`update_challenge_state`** rows (`challenge_id`, `new_state`, `evidence` quoting **`call_id`** or short quote). **Stop for approval** before invoking the tool.
