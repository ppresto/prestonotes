# CustomerStateUpdate.json (extractor → orchestrator handoff)

**Purpose:** Contract for the **delta** object the **Stage 1 extractor** (or orchestrator step that wraps it) passes to **Stage 3 domain advisors** (`23`–`27`) before **`20-orchestrator`** merges outputs. On-disk name is conventional: **`CustomerStateUpdate.json`** (or the same shape inlined in chat).

**Authority:** Shape aligns with **`docs/project_spec.md` §6** (Stage 3 inputs) and **§9 TASK-015 / TASK-016**. Refine fields when the extractor implementation lands; advisors must tolerate **optional** keys and empty arrays.

## Recommended shape (JSON object)

| Field | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `customer` | string | yes | Same name as `MyNotes/Customers/<Customer>/` folder |
| `source_call_ids` | string[] | yes | Call ids (§7.1) that produced this delta; may be one id |
| `generated_at` | string (ISO-8601) | yes | When the delta was produced |
| `challenges` | object[] | no | Subset or rollup of §7.1 `challenges_mentioned` — at least `id`, `description`, `status` when present |
| `gaps` | object[] | no | Free-form gap statements the customer cares about (e.g. `{ "id": "gap-001", "text": "...", "domain_hint": "soc" }`). Advisors may ignore `domain_hint` and classify themselves |
| `current_stack` | string[] | no | Technologies / vendors mentioned (CSPs, IDPs, scanners, etc.) |
| `products_discussed` | string[] | no | Wiz SKUs or modules mentioned on the call |
| `architecture_diagram_paths` | string[] | no | **ASM (rule 26):** Repo- or customer-relative paths to **image** files under **`MyNotes/Customers/<Customer>/`** (e.g. `diagrams/arch.png`). Empty or omitted if none |

## Example (minimal)

```json
{
  "customer": "Acme Corp",
  "source_call_ids": ["2026-04-15-discovery-1"],
  "generated_at": "2026-04-16T12:00:00Z",
  "challenges": [
    { "id": "ch-001", "description": "No unified runtime threat detection in cloud", "status": "identified" }
  ],
  "gaps": [
    { "id": "gap-001", "text": "Incident response playbooks not integrated with cloud alerts" }
  ],
  "current_stack": ["AWS", "Azure", "Splunk"],
  "products_discussed": ["Wiz Cloud", "Wiz Sensor"],
  "architecture_diagram_paths": ["diagrams/acme-high-level.png"]
}
```

## Advisor output

Each advisor returns a single JSON object documented in **`.cursor/rules/23-domain-advisor-soc.mdc`** through **`27-domain-advisor-ai.mdc`** (`domain`, `gaps_analyzed`, `recommendations[]`, `no_match_gaps[]`).
