---
url: https://www.wiz.io/blog/kenna-sunset-and-the-shift-to-exposure-management
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-23T07:41:51-05:00
extraction_mode: static_fetch
content_hash: 2e3c8ea553fa
---

# Kenna EOL and the Shift to Exposure Management | Wiz Blog

Cisco has officially
announced
the end-of-sale and end-of-life dates for Cisco Vulnerability Management (formerly Kenna Security), including its Vulnerability Intelligence and Application Security Modules. While existing customers have until June 2028 for full end-of-support, this retirement marks a pivotal moment for the industry.
The Sunset of the RBVM Era
For years, Kenna pioneered the
Risk-Based Vulnerability Management (RBVM)
category, using threat intelligence to move security teams away from flat lists of CVEs. However, as organizations have shifted to complex cloud architectures and AI-driven development, the limitations of RBVM have become clear. The tool remained fundamentally focused on vulnerability aggregation - treating
vulnerability management
as a siloed task rather than taking a holistic approach to reducing real exposure across the entire environment.
The Kenna sunset is more than a tool replacement; it is an opportunity for security leaders to rethink their strategy. Many organizations, such as Western Union, have already begun adopting a strategy that moves away from looking at vulnerabilities in isolation and toward a true risk-based, exposure management approach.
The RBVM Challenge: CVE Prioritization in a Vacuum
The fundamental limitation of traditional RBVM is its narrow focus. These tools were designed to manage vulnerabilities CVE in a vacuum. While they can tell you if a vulnerability is considered severe globally based on threat intelligence, they lack the environmental and business context required to tell you if it actually matters to
your
organization. Without this context, you cannot accurately assess the impact, prioritize one over another, or determine the most effective path to remediation.
Traditional scanners and aggregation tools operate in a "Vertical Security" model - they exist in silos. They lack the cloud and environmental context needed to effectively move away from sole vulnerabilities to true exposures. This disconnect leads to massive challenges in prioritization. For example, without a unified view and context of your environment, how can you answer these critical questions:
Exploitability
: Is this vulnerability actually reachable and exploitable from the outside?
Impact
: If exploited, what is the blast radius? What permissions does the machine have? Can it access sensitive data or move laterally to other parts of your network?
Ownership
: Where in the code did this risk originate? Who is the developer responsible for fixing it at the source?
At Wiz, we believe context is everything. To effectively reduce risk, you need a horizontal view that connects the dots between a CVE and the environment context - including permissions, data, misconfigurations, external exposure, secrets, and the code that deployed it. This shift - from managing CVEs in isolation to managing real exposures across the entire attack surface - requires a move away from vertical silos and toward a unified platform.
Kenna EOL as Your Next Step Toward Exposure Management
The Kenna sunset is a strategic opportunity to move from a legacy RBVM approach to a modern
Exposure Management strategy
. Wiz is here to support customers in unifying risk, prioritizing with context, and remediating - all within a single, integrated platform.
Wiz Unified Vulnerability Management (UVM)
doesn't just ingest and unify findings from your on-prem or code scanners. Because it is a native part of the
Wiz Exposure Management
platform, it maps every 3rd party finding onto the Wiz Security Graph to enrich it with deep context that provides you with true exposure prioritization based on its impact on your environment, across on-prem, cloud, and hybrid.
The Power of Context
Imagine your vulnerability scanner identifies a critical vulnerability on a machine. In a traditional RBVM tool, it might be enriched with threat intelligence context, but it remains just another ticket in a pile of thousands, likely sitting in a queue for weeks.
With Wiz Exposure Management, that finding is immediately enriched with four layers of context:
1. Exploitability Validation:
Wiz ASM
(Attack Surface Management) tests the real-world exploitability of risks from the outside no matter if the resource runs in the cloud, on-prem, or hybrid. It tells you immediately if this specific vulnerability is validated to be exploitable from the outside, and which risks attackers can actually reach.
2.
Cloud Context
: The Wiz agentless cloud scanner discovers risks such as sensitive data, misconfigurations, overprivileged permissions, and exposed secrets. Because these are all mapped on the Wiz Security Graph, Wiz can detect if that vulnerable VM is also exposed to the internet, can lead to privilege escalation, or has a direct path to sensitive PII data.
3.
Runtime Context:
Wiz also adds a layer of runtime validation from the
Wiz Sensor
. The Sensor confirms that this vulnerability is actively present at runtime, adding crucial, high-confidence data to the prioritization.
4.
Code Context:
Wiz Code traces the vulnerable component back to its specific repository. It identifies the exact line of code and the developer responsible, so you can fix the issue at the root and prevent it from ever being redeployed.
What was once just a critical vulnerability on a spreadsheet is now a clearly defined attack path. You can see the true impact on your business, truly prioritize based on context, and determine the best path to remediation.
Getting Started with Exposure Management
Transitioning from Kenna doesn’t have to be a multi-month project of re-building legacy workflows. With Wiz, you can get set up in a day and immediately begin burning down your true exposure.
Ready to start prioritizing true exposures? Schedule a
live demo
with our team and learn more about
Wiz UVM
in the Wiz Docs (login required).
Tags
#
Product