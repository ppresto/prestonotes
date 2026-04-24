---
url: https://www.wiz.io/blog/the-agile-fedramp-playbook-part-3-preventative-risk-management-by-building-secure
source_name: blog_public_sector
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-02-27T10:33:55-05:00
extraction_mode: static_fetch
content_hash: 8c68ae11fbfe
---

# Agile FedRAMP Playbook 3: Secure by Design Risk Prevention | Wiz Blog

Stopping Risk at the Source
In
Part 2 of our FedRAMP series
, we discussed how to manage risks already living in production. And while the ideal state for managing a Plan of Action and Milestones (POA&M) is to ensure that vulnerabilities and misconfigurations are never introduced into production in the first place, meeting that bar is easier said than done.
In seeking our own FedRAMP authorization, Wiz's approach included strengthening security checks earlier in the software development lifecycle while also driving efficiencies in identifying and remediating the inevitable items that end up on a POA&M. In this part of our series, we’ll break down how we were able to integrate security across the SDLC, reducing the number of risks entering the production authorization boundary, while accelerating our ability to innovate more quickly.
Engineering Security: Mapping Agile Development to FedRAMP
In modern cloud (and AI) development, cloud resources boil down to code. Between application code, infrastructure-as-code (
IAC
) templates defining cloud resources,
container images
, and virtual machine images, the line between applications and the infrastructure they sit on has largely vanished. This leaves security teams with the challenge of stopping risky builds before they reach the production authorization boundary.
Figure 1:  Wiz visualizes the "vanishing line" between applications and infrastructure, tracing production risks to their source in code to support FedRAMP requirements
For organizations pursuing a
FedRAMP authorization
—be it via the
FedRAMP Rev 5
or the
FedRAMP 20x
framework— the goal remains the same: ensuring security is baked into the development process rather than brought in post-deployment. This shift isn’t just a technical upgrade; it’s a policy pivot towards Speed-to-Mission. Wiz helps software providers operationalize the vision set forth by the White House and CISA for the future of secure software adoption, and aligns with federal efforts to move FedRAMP from a compliance regime to a continuous security assurance framework.
FedRAMP Rev 5:
This framework emphasizes formal engineering principles taken from NIST SP 800-53r5. Controls such as
SA-8 (Security and Privacy Engineering Principles)
and
SA-11 (Developer Security Testing and Evaluation)
require organizations to demonstrate that they have integrated security throughout the system development life cycle.
FedRAMP 20x:
This newer FedRAMP framework prioritizes automation and rapid feedback loops. Key Security Indicators (KSIs) such as
CMT-03 (Automated Testing and Validation)
and
PIY-04
(CISA Secure by Design) focus on building security through persistent testing, validation, and integrated security considerations throughout the SDLC. This allows agencies to verify the “Secure-by-Design” integrity of their software supply chain. Instead of agencies inheriting vendor risk, they can now enforce upstream accountability before a single line of code is deployed.
Organizations need tools that can help them meet these requirements through automated "guardrails" that empower developers without slowing down the mission.
How Wiz Code for Gov Enables “Secure-by-Design”
Wiz Code for Governmen
t (Wiz Code for Gov) offers visibility, remediation, and policy capabilities that can help organizations meet these needs. Wiz Code for Gov extends Wiz’s unified policy engine across the entire development lifecycle, starting from scanning for vulnerabilities, data findings, secrets, and IaC misconfigurations in code repositories, or in the pipeline through a
CLI tool
to stop risky builds before they reach the production authorization boundary.
Figure 2:  Wiz CLI identifies risks locally to ensure only validated configurations reach the FedRAMP boundary, assisting with SA-10 (Developer Configuration Management) requirements
This modernized approach directly supports the vision of
OMB M-24-15
, shifting the federal posture from Point-in-Time Compliance to Continuous Engineering. Wiz provides the blueprint for what the GSA (General Services Administration) calls Continuous Authorization.
It’s an approach that also follows the core pillars of a
secure SDLC
:
1. Proactive Prevention: Code and Application Security
Security starts during coding. To catch potential issues before they’re pushed into your organization’s preferred repository, the Wiz CLI runs locally, giving developers immediate feedback on their code as they are coding it. Wiz also integrates with VCS and
CI/CD tools
to run the same checks at each stage of the build pipeline, catching any potential issues that may have been missed in the stage prior. These checks can look for vulnerabilities, IaC misconfigurations, secrets, sensitive data, and malware, and provide devs with results from scans directly in the repository where they do their work – while sharing the results back in Wiz for security teams.
Rev 5 Impact:
Directly supports
SA-10 (Developer Configuration Management), CM-2 (Baseline Configuration),
and other controls by ensuring only hardened, authorized configurations are eligible for deployment.
20x Impact:
Directly supports
KSI-CMT-03 (Automated Testing and Validation)
and other KSIs by validating code integrity before it impacts the runtime environment.
2. Automated Guardrails: Pipeline and Registry Security
Wiz acts as an automated gatekeeper by integrating directly into CI/CD pipelines and container registries. This allows Wiz to scan images and IAC templates for the same risks identified by the version control scanners in the pipeline before resources are promoted to the production environment. Security teams can set guardrails based on organizational policies to audit or block builds that fail these policies.
Rev 5 Impact:
Supports various controls including
SI-2 (Flaw Remediation)
and
SA-11 (Developer Security Testing and Evaluation)
. Blocking a "Critical" risk at the registry level eliminates the 30-day "ticking clock" of a production POA&M.
20x Impact:
Provides the machine-readable evidence required for automated vulnerability gating KSIs.
3. Accelerated Traceability: ASPM and Code-to-Cloud Traceability
Wiz helps accelerate visibility between DevOps and the Production authorization boundary by mapping production findings back to their origin in the development environment. Using Application Security Posture Management (
ASPM
), Wiz traces live cloud risks to the specific repository, line of code, and responsible developer.
With Wiz Exposure Management, Wiz serves as a central hub for application security, ingesting and normalizing findings from both native Wiz scanners and third-party AppSec tools. This bidirectional visibility, tracing Cloud-to-Code for root cause and Code-to-Cloud for attack path analysis, transforms security from a reactive patching exercise into a proactive engineering fix.
Feature
Legacy Approach
Agile Framework through Wiz for Gov
Security Gates
Manual reviews before a release
Automated CI/CD guardrails
Vulnerability Fixes
Found in production; 30 days to fix (depending upon severity)
Found in build; fixed in minutes
Rev 5 Alignment
Periodic testing usually separate from DevOps sprint cycle
Continuous Engineering with testing built into development (SA-8)
20x Alignment
Inconsistent manual reporting
Automated KSIs (SD-01, SD-02)
Success Metric
Activity-based (Number of scans/Total vulnerabilities)
Outcome-based (Mean Time to Remediate and reduction of Toxic Combinations)
Turning Prevention into Speed and Trust
Part of the challenge with FedRAMP isn’t just pursuing the initial authorization: it’s maintaining an authorization with the
Significant Change Request (SCR)
process. When launching new capabilities, organizations must prove to their third-party assessment organization (3PAO) and their Authorizing Officials (AOs)  that the security posture of the system is maintained.
Wiz Code for Gov drives preventative risk management by transforming security from a bottleneck into a high-velocity compliance engine:
Stop Secrets at the Source:
Wiz Code for Gov prevents hardcoded credentials from entering the authorization boundary by scanning at the CLI and VCS levels. This eliminates one of the most common high-risk findings before it ever requires a formal incident response or a mandated POA&M entry. This supports several controls and KSIs, including Rev 5's
IA-5(7) (Authenticator Management | No Embedded Unencrypted Static Authenticators)
.
Generate Continuous Evidence:
Wiz automatically generates a machine-readable Software Bill of Materials (
SBOM
) and
SCA
reports during the build phase. Beyond just a report, Wiz provides the bidirectional traceability to show exactly where those libraries indicated in the SBOM are running within your production boundary. This provides 3PAOs with real-time visibility into third-party libraries and dependencies, enabling a "Report Once, Distribute to All" model that eliminates manual spreadsheet tracking. These capabilities support the intent behind many FedRAMP controls, including Rev 5’s
CM-8(2) (Information System Component Inventory | Automated Maintenance)
and
CM-8(3) (Information System Component Inventory | Automated Unauthorized Component Detection)
.
Streamline Significant Change Requests (SCRs):
By enforcing a unified policy engine across the entire development lifecycle, teams can demonstrate that new code meets established security baselines by providing a unified view of all native and third-party findings before deployment. This proactive validation provides the 3PAOs, AOs and the PMO with documented proof that security guardrails were active throughout the change process, significantly accelerating the approval of new features.
Acceleration with Code-to-Cloud visibility
Preventative risk management shouldn’t just be viewed as a security best practice, but rather as a mission accelerator. Automated guardrails and accelerated traceability act as a critical force multiplier for resource-constrained organizations. These capabilities allow small security teams to enforce enterprise-grade standards across complex cloud environments without manual oversight. By building "Secure-by-Design," you reduce the friction of compliance and keep your engineering teams focused on delivering mission-critical features.
In the final part of our series, we will look at
Reactive Risk Management.
We’ll discuss how to use cloud context to accelerate incident response and satisfy the rigorous requirements of FedRAMP's IR control family.
Tags
#
Public Sector