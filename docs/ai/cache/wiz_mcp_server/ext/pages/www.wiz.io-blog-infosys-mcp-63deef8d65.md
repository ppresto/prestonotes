---
url: https://www.wiz.io/blog/infosys-mcp
source_name: blog_ai
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-02-20T12:28:34-05:00
extraction_mode: static_fetch
content_hash: d15991e7a6eb
---

# Wiz MCP & Infosys: Agentic Security | Wiz Blog

In the era of AI-driven development, the cloud attack surface is expanding faster than traditional security operations can reasonably keep up. Cloud environments evolve continuously, infrastructure is increasingly ephemeral, and security teams are asked to respond in near-real time. This widening gap is driving interest in the next evolution of cloud security operations:
Agentic Security
.
Agentic Security represents a shift from reactive alert handling toward an operational model where intelligent agents assist with detection, investigation, and remediation, while keeping humans firmly in control. Rather than replacing security teams, agents help reduce manual effort in the most time-consuming phases of security operations.
The purpose of this post is to outline a practical reference architecture for agentic cloud security operations.
Specifically, it illustrates how standardized security context from Wiz, AI-driven agents, and orchestration platforms can work together to support faster investigation and remediation while preserving human-in-the-loop governance, accountability, and control.
In this reference architecture, Infosys Cyber Next, powered by Infosys Topaz Fabric, serves as the central orchestration layer for this architecture. It unifies observability to build a shared security context, enabling the deployment of AI agents for automation and content engineering across the enterprise defense ecosystem.
From Visibility to Agency
Achieving an agentic security operating model requires more than raw visibility or static alerts. It requires
agency
, the ability for tools to reason over security context, collaborate across systems, and propose informed actions.
In this reference architecture, the
Wiz Security Graph
provides deep, contextual insight into cloud risk, while the
Wiz Remote MCP Server
exposes that context through a standardized, AI‑friendly interface. The Infosys Cyber Next platform coordinates specialized agents that operate across the security lifecycle.
Together, this ecosystem enables organizations to:
Bridge the gap between AI systems
and security data using Wiz MCP as a standard interface
Deploy specialized agents
focused on specific phases of the security lifecycle
Maintain human‑in‑the‑loop governance
to ensure responsible and auditable operations
The Core Enabler: Wiz Remote MCP Server
At the center of this architecture is the
Wiz Remote MCP Server
, which exposes the Wiz Security Graph through the Model Context Protocol (
MCP
).
Rather than returning isolated findings or static alerts, Wiz MCP provides rich, interconnected security context that downstream tools and agents can reason over, including:
Internet exposure and attack paths
Data sensitivity and toxic combinations
Identity relationships and privilege‑escalation risk
Asset relationships, ownership, and blast radius
This context allows AI‑powered systems to assess not just
what
is misconfigured, but
why it matters
, grounding automated analysis in real business risk.
Unlike traditional APIs that rely on rigid, hard‑coded integrations, MCP enables authorized tools to query the Wiz Security Graph in a consistent and scalable way. This makes Wiz MCP well‑suited as a common interface between security data and emerging AI‑driven workflows.
Operationalizing Agentic Security with Infosys Cyber Next
In this reference architecture,
Infosys Cyber Next
retrieves high‑fidelity security insights from
Wiz‑powered agents
, using MCP tools such as get_secops_agent_analysis, without requiring complex point‑to‑point integrations.
Infosys Cyber Next also integrates with ITSM and CMDB MCP servers to enrich security findings with organizational context, such as business ownership and operational impact.
The result is a unified orchestration layer where multiple agents collaborate, transforming isolated alerts into intelligence‑driven actions.
The Multi‑Agent Architecture
To manage the complexity of modern cloud environments, this architecture is designed around a
specialized multi‑agent system
. Each agent has a clearly defined role, reducing overlap and limiting scope.
1. Discovery Agent
Role:
Continuous monitoring and signal detection
Function:
The Discovery Agent continuously queries the Wiz MCP Server to identify new signals from the Security Graph. It filters noise, highlights high‑risk changes or
attack paths
, and flags issues that require deeper analysis. It does not solve the problem; it isolates the signal.
2. Investigation Agent
Role:
Context gathering and impact analysis
Function:
Triggered by the Discovery Agent, the Investigation Agent serves as the central analyst. It queries Wiz MCP for deep technical context and collaborates with other MCP servers in the ecosystem, including:
ITSM/CMDB MCPs:
To identify asset ownership, business context, and potential impact
The output is a consolidated impact assessment that combines technical risk with organizational relevance.
3. Remediation Agent
Role:
Strategy mapping and action proposal
Function:
Using the full impact assessment, the Remediation Agent determines an appropriate remediation strategy. It maps issues to pre‑approved Cloud Service Provider (
CSP
) native functions or scripts (such as AWS Lambda functions) and prepares an execution plan for human review.
An Agentic Workflow in Action: Intelligent S3 Remediation
To make this architecture more concrete, consider a common and high‑risk scenario:
public S3 bucket exposure containing sensitive data
.
Phase 1: Detection
Agent:
Discovery Agent
Action:
The agent queries the Wiz MCP Server and identifies a new critical finding: an S3 bucket (finance-logs-prod) exposed to the public and located on an active attack path. The issue is flagged as critical and passed to the Investigation Agent.
Phase 2: Context and Impact Analysis
Agent:
Investigation Agent
Action:
The agent builds a comprehensive view of the issue:
Wiz MCP:
Confirms the bucket contains PII and high‑sensitivity data
ITSM/CMDB MCP:
Identifies the Finance Analytics Team as the business owner
Output:
A structured impact assessment indicating critical PII exposure, confirmed ownership, and low risk of service disruption if access is restricted to a specific VPC endpoint.
Phase 3: Strategy and Proposal
Agent:
Remediation Agent
Action:
Based on the assessment, the agent determines the appropriate response:
Selection:
Identifies BlockPublicAccess as the recommended control
CSP Mapping:
Locates the approved remediation function
Plan Generation:
Drafts a remediation proposal outlining the change and expected outcome
Phase 4: Execution and Governance (Human‑in‑the‑Loop)
Agent:
Remediation Agent (Interface)
Action:
The remediation plan is presented to a human security engineer through a collaboration tool such as Slack or Microsoft Teams.
Request:
“Public PII exposure detected. The Investigation Agent confirms ownership by Finance Analytics. I recommend applying BlockPublicAccess due to an active attack path. Please review and approve.”
Outcome:
After reviewing, the engineer approves the fix. The agent invokes the approved CSP function, securing the bucket in minutes.
Responsible AI: Speed with Control
Agentic security does not imply uncontrolled automation. This reference architecture is designed with governance at its core:
Human‑in‑the‑Loop:
High‑impact actions always require explicit human approval
Auditability:
Agent reasoning and actions are logged to support compliance and post‑incident review
Least Privilege:
Agents operate with scoped permissions,Discovery and Investigation agents are read‑only, while the Remediation Agent is limited to invoking specific, pre‑approved functions
A Blueprint for Agentic Cloud Security
The Wiz Remote MCP Server provides a standardized interface for accessing deep cloud security context powered by the Wiz Security Graph. When combined with platforms like Infosys Cyber Next, this architecture illustrates how organizations can move beyond siloed alerts toward a shared context plane where risks are understood, prioritized, and addressed more efficiently.
This blueprint reflects an
emerging operational pattern
rather than a fully autonomous security model. It highlights how agentic analysis can reduce investigation overhead while preserving human judgment and accountability.
The Impact: Measurable Security Outcomes
When adopted thoughtfully, agentic architectures like this can help organizations:
Accelerate engineering velocity:
Standardized access to security context reduces the need for custom integrations when building security workflows
Maximize tool ROI:
A unified orchestration layer reduces context switching and improves efficiency across existing tools
Democratize security decision‑making:
Clear, contextual insights help operators understand the impact of remediation before changes are made
Reduce MTTR:
By automating context gathering and analysis, agents eliminate investigation lag and allow teams to focus on resolution
Agentic security is still evolving, but architectures like this offer a practical blueprint for how AI‑assisted operations can augment security teams, helping them move faster without sacrificing control.
MCP Prompt Examples
1. Investigation Agent: Contextual Deep-Dive
This prompt defines the persona for the Investigation phase, focusing on gathering technical and business context once a signal is detected.
System Prompt:
You are a specialized Investigation Agent for Infosys Cyber Next. Your goal is to transform a Wiz issue or threat into a high-fidelity impact assessment using the Wiz MCP server and integrated ITSM context.
CRITICAL: You must verify both technical risk via the Wiz Security Graph and business ownership via ITSM/CMDB tools.
Step 1: Technical Context
Use wiz_get_issue_data_by_id to extract the "Toxic Combination" details.
Use get_secops_agent_analysis to check if a threat is malicious.
Step 2: Business Context
Query the CMDB MCP server: "Identify owner and environment for resource “finance-prod-storage".
Step 3: Impact Synthesis
Correlate the Wiz "Attack Path" with the business criticality to determine if this is a "Production-Critical" escalation.
User Query Example:
"Investigate the critical S3 finding for bucket 'finance-logs-prod'. Cross-reference with CMDB to find the owner and provide a full impact assessment."
2. Remediation Agent: Strategy & Proposal
This prompt focuses on the Remediation phase, where the agent moves from "what happened" to "how to fix it" while keeping a human in the loop.
System Prompt:
You are a specialized Remediation Agent. Your role is to map validated security gaps to pre-approved organizational guardrails.
REMEDIATION PROTOCOL:
Analyze Gaps
: Review the Investigation Agent's output (e.g., "Public exposure on S3").
Map to Policy:
Identify the CSP-native fix (e.g., AWS PutBucketPublicAccessBlock).
Draft Proposal:
Generate a clear "Human-in-the-Loop" request via email.
Format:
[Risk] + [Business Impact] + [Proposed Action] + [Approval Request].
Safety Check:
Ensure the remediation does not break existing VPC endpoints or required service access.
CRITICAL:
You are in "Proposal Mode." You may generate CLI commands or Lambda payloads, but you must not execute until receiving a signed approval token.
User Query Example:
"Based on the S3 bucket exposure finding, generate a remediation plan for 'finance-prod-storage'. Provide the AWS CLI commands to enable Block Public Access and versioning, and draft the approval message for the Finance Analytics lead."
3. Combined Workflow: The "Quick-Action" Prompt
A streamlined prompt used for rapid response within the Infosys Cyber Next interface.
Prompt:
"Provide potential remediation for cloud resource “finance-prod-storage”. Check Wiz MCP for existing open issues, prioritize them by severity, and provide the specific JSON policy required to enforce HTTPS-only access (Encryption in Transit) as per our compliance standards."
Tags
#
AI