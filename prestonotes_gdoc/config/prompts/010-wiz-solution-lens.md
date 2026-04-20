# Wiz Solution Lens for Customer Notes

Purpose:
- Ground customer-notes analysis in what Wiz actually solves.
- Translate customer pain, weak workflows, and tool sprawl into realistic Wiz-aligned outcomes.
- Improve mutation quality for `Goals`, `Risk`, `Workflows / Processes`, `Challenges`, and `Upsell Path`.

## Why this lens exists

Customer notes/transcripts describe current-state pain and fragmented workflows.
Wiz notes updates should interpret those signals through the lens of:
- what the customer is trying to improve,
- which workflows are inefficient/manual today,
- how Wiz can improve those workflows in practical, evidence-backed ways.

## Core Wiz outcomes to map against

- **Visibility and context unification**
  - Cloud, workloads, identities, code, and data context in one graph.
  - Better ownership context for remediation and prioritization.

- **Prioritization and remediation velocity**
  - Move from raw vulnerability volume to risk-based, owner-ready action.
  - Reduce manual triage/routing and improve MTTR/SLA adherence.

- **Vulnerability and secrets coverage**
  - Runtime/workload, cloud, and code-level findings.
  - Include vulnerability, secrets, and policy/compliance context.

- **AI security**
  - AI asset/posture/attack-surface visibility and risk context.

- **Runtime security and Kubernetes/container strength**
  - Strong runtime and K8s/container coverage for workload risk and response.

- **API security and external attack surface**
  - API and internet-exposed surface visibility/validation.
  - Useful for external exposure investigations and attack-path context.

- **DSPM and CIEM**
  - Data exposure/governance context and identity-entitlement risk reduction.

- **Shift-left and software supply-chain**
  - Wiz Code scans for repo posture, SCA/SAST/secrets/DSPM.
  - Developer-identity and repo-context support.
  - SBOM outcomes from repositories and running workloads.
  - Zero-vulnerability image programs (for example with hardened base-image strategy such as WizOS workflows where applicable).

- **Detection and response acceleration**
  - Agentless ingestion of CSP control-plane and data-plane logs.
  - Supports CDR/TDR detection and investigation workflows.

## Workflow interpretation guidance

When reading notes, detect and preserve the customer's real process flow:
- current trigger,
- tools/scripts used today,
- people/team handoffs,
- output artifacts (reports, tickets, audit evidence),
- bottlenecks/pain points,
- desired improved future flow.
- time between steps (wait states, queue time, approval lag),
- resources required at each step (team effort, manual spreadsheet/report work),
- security coverage gaps not accounted for (missing owner context, weak prioritization, blind spots).

Do not force a single Wiz-native workflow format.
Each customer may have unique legacy processes; the goal is to show how Wiz can improve them.

Workflow signal library (allow-based):
- Terms are cues only; they are not sufficient by themselves.
- Confirm process semantics before adding a workflow:
  - at least two linked actions in order,
  - clear actor/handoff or ownership transition,
  - a stated output/outcome or downstream dependency.
- Prefer process evidence that also carries operating context:
  - timing/latency between steps,
  - effort/resource burden,
  - security/control gaps and where they appear in the flow.
- Assign a stable workflow name from customer language and reuse that name across runs.
- Enrich workflows over time by appending newly learned details to the same named workflow context, not by replacing prior detail.

## Mutation-planning behavior

- Use this lens to produce better candidates.
- Keep evidence-first behavior (no invention).
- Prefer allow-based promotions:
  - if clear pattern exists, propose mutation;
  - if weak/ambiguous, keep `no_evidence`.
- For workflow findings, separate:
  - `Use Cases / Requirements` (explicit customer requirements across lifecycle stages),
  - `Workflows / Processes` (how work happens today and where it breaks).
- Never place process narratives in `Use Cases / Requirements`.
- `Workflows / Processes` entries must be paragraph-style narrative, not `->` arrow chains.
- Analyze workflow drift over time (steps/handoffs/tools/owners/output changes) and use that drift to find emerging coverage gaps.
- Promote workflow coverage gaps into `Challenge Tracker`; promote strategic recurring gap themes into `Goals`.
- When gaps imply clear product-fit expansion, propose `Upsell Path` candidates with SKU-first wording.
- Every new `Goals` candidate must map to one or more active challenge themes.
- Do not rewrite existing `Goals`; append new ones only when strong recurring themes justify it.
