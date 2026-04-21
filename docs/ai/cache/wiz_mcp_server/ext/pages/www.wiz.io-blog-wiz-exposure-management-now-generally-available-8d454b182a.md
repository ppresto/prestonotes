---
url: https://www.wiz.io/blog/wiz-exposure-management-now-generally-available
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-02T09:02:06-05:00
extraction_mode: static_fetch
content_hash: 714eca086321
---

# Wiz Exposure Management GA Release: Unifying UVM + ASM | Wiz Blog

We're excited to announce the General Availability (GA) of
Wiz Exposure Management
, featuring our powerful new capabilities:
Wiz Unified Vulnerability Management (UVM)
and
Wiz Attack Surface Management (ASM
) both now in GA! This launch enables organizations to unify risk data, validate and prioritize exposures based on true impact, and accelerate remediation across complex environments. Wiz Exposure Management empowers teams to move away from managing endless CVE counts to focusing on true exposures in their environment, achieving prioritized risk reduction everywhere.
The Wiz Approach: Why a Unified Platform is Needed for Exposure Management
Wiz is built on the concept of "Horizontal Security", moving beyond the "Vertical Security" model where siloed tools (for cloud, on-prem, code, SaaS) strip data of context and fragment findings and ownership, making true risk reduction challenging. Our Horizontal Security approach unifies teams on a single platform offering shared context, true risk correlation, consistent policies, and unified remediation workflows from code to cloud and beyond. This delivers critical context on the
Wiz Security Graph
needed to prioritize exposures and scale security effectively.
Wiz extends this horizontal approach beyond the cloud with
exposure management
- creating a single pane of glass covering the entire environment: cloud, on-prem, code, AI, and SaaS. This is enabled by the new GA capabilities allowing customers to:
Centralize External Findings:
Use Wiz UVM to bring in findings from existing security tools (e.g., on-prem vulnerability scanners or code scanners) and immediately prioritize them with context on the Wiz Security Graph.
Validate Exposure and True Exploitability:
Leverage
Wiz ASM
to continuously discover all external exposures, validate the exploitability of critical risks, and prioritize based on real-world attack context.
Wiz Exposure Management enables teams to detect, validate, prioritize, and remediate exposures across their environment.
Hear the impact directly from our customer, Chelsea Weiss, Director of Cybersecurity at Western Union:
The Power of a Unified Platform: Attack Path Example
To truly understand the power of a unified platform, let’s walk through a real-world example. Watch how Wiz’s cloud, code, and runtime scanners, along with the new Wiz UVM and Wiz ASM, converge to detect and prioritize a single, high-risk attack path.
Detect, Unify, and Enrich Risk with Context
Let’s start with Wiz’s
agentless Cloud Scanner
, discovering  risks like sensitive data, misconfigurations, permissions, and secrets- all mapped on the Wiz Security Graph in the example below. We can see that Wiz detected a vulnerability on a VM that is exposed to the internet, and has access to sensitive PII data.
We then add a layer of runtime validation from the
Wiz Sensor.
The Sensor confirms that this vulnerability is actively present at runtime, adding crucial, high-confidence data.
Wiz UVM
also helps us prioritize finding from different tools on the Security Graph. An external scanner finding from Qualys is ingested into Wiz and pulled into this
exact same
Wiz Risk Issue. This provides correlation, allowing you to prioritize the external Qualys finding based on its true environmental impact and the context of the graph, just like how you would prioritize a Wiz Finding.
Step 2: Validate Exposure and Exploitability with Wiz ASM
You can think of
Wiz ASM
as your environment’s best simulated attacker. It continuously validates which resources are truly reachable from the outside and which risks are exploitable. The Attack Surface Scanner tests the endpoint, simulating an attack to confirm real exploitability of vulnerabilities, misconfigurations, and default credentials as well as tests for exposure of sensitive data and secrets. By adding context from Wiz ASM to the same issue, we uncover:
Exposure Validation:
The endpoint is validated to be externally facing, providing the actual screenshot of the exposed Hadoop webpage as proof.
Exploitability Validation:
The scanner tested and validated an unauthenticated remote code execution (RCE). This confirms an attacker could submit malicious applications to the cluster, leading to arbitrary code execution, sensitive data access, and potential full control of the compromised Hadoop cluster without needing credentials.
Step 3: Map Ownership and Trace to Source Code
This entire attack path- the vulnerability, sensitive data, runtime validation, and RCE exploitability validated by
ASM
- converges into one single, high-priority
Wiz Risk Issue.
This consolidated attack path is a critical, validated risk demanding immediate attention.
To accelerate Mean Time to Respond (MTTR), Wiz enriches this attack path with the comprehensive ownership context required to quickly assign and resolve the Risk Issue:
Integration with CMDB
(e.g., ServiceNow) adds ownership metadata and preserves the original UVM external tool tagging, ensuring the service owner is accurately identified.
Suggested owner assignee
such as the Wiz Project owner or the resource owner
Cloud-to-code visibility with
Wiz Code ,
adding the final layer and mapping the vulnerable component back to the specific repository and the responsible developer.
Step 4: Respond and Remediate Faster
The ultimate goal of all this context and prioritization is to achieve the fastest possible
Mean Time to Remediate (MTTR)
and drive down organizational risk. Teams can assign the issue directly in Wiz or trigger integrations with existing workflows (e.g., automatically opening a Jira ticket). Wiz provides
AI remediation guidance
that tells the owner
exactly
what needs to be done. You can include this guidance directly in the ticket, alongside all the Wiz context they need to understand criticality and remediate the issue at its source.
How Wiz Exposure Management Extends to On-Prem
In this scenario, we begin by using
Wiz UVM
to ingest data from an existing on-prem vulnerability scanner, Rapid7. Wiz UVM adds the on-prem machine to the Imported Asset page with all the metadata available from the external scanner. Next,
Wiz ASM
takes over. It uses the network addresses of that imported on-prem machine to actively test for external exposure and assess for exploitable risk.  We can see that ASM validated that the on-prem resource is externally facing on the graph below.
This seamless integration between Wiz UVM and ASM allows customers to rapidly detect exposures and validate the exploitability of risks on any asset, anywhere- not just in the cloud. Not only that, but to extend to any asset customers can bring in their domains to be scanned by the Attack Surface Scanner, or leverage Wiz to uncover subdomains for them.
Continuously Harden Posture and Meet SLAs with Posture Issues
We recently
launched Posture Issues
, which help teams address findings with high-ROI fixes. Unlike Risk Issues (which represent attack paths),
Posture Issues
group findings within a single domain- such as vulnerabilities, secrets, or data- to create high ROI fixes that help move away from individual CVE remediation to an impact-based grouping. For example, in one Posture Issue, you can group all vulnerabilities with a CVSS score of 8 or higher that have a fix and a public exploit, and require to be patched within 14 days. Posture Issues help you meet SLAs, align with internal programs, and move away from a noisy list of CVEs into a list of high-impact fixes that can be assigned, tracked, and worked through efficiently.
Get started with Wiz Exposure Management Today
It’s time to stop managing fragmentation and start managing exposure across your entire environment. Ready to take control of your exposures? Learn more about
Wiz ASM
and
Wiz UVM
in the Wiz Docs. Join us for
a live webinar about Wiz ASM
or
book a live demo
with our team.
Tags
#
Product