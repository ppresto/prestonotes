---
url: https://www.wiz.io/blog/fedramp-high-playbook-part-2-continuous-monitoring
source_name: blog_public_sector
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-02-20T06:51:03-05:00
extraction_mode: static_fetch
content_hash: 06fdd59ba929
---

# FedRAMP ConMon: Shifting to Continuous Monitoring | Wiz Blog

The Shift from "Periodic" to "Continuous"
In the
first part of our FedRAMP series
, we explored Wiz’s accelerated journey to FedRAMP High. However, seasoned CSPs (Cloud Service Providers) know that obtaining the FedRAMP authorization is only the beginning. The real challenge lies in maintaining that security posture through ongoing FedRAMP Continuous Monitoring (ConMon).
Traditionally, compliance monitoring has been synonymous with "point-in-time" scanning. Organizations would run a scan, generate a report, and spend weeks manually reconciling security posture against requirements. In a FedRAMP environment, this reactive, manual approach is not sustainable amidst an evolving threat landscape.
FedRAMP
Rev 5 processes necessitate a robust ConMon program built around monthly reporting, and ongoing FedRAMP reforms are pushing ConMon towards data-driven automated validation of risk, a move that directly supports the goals of
Executive Order 14028
on Improving the Nation’s Cybersecurity. To meet these stringent requirements and the Executive Order’s mandates for increased visibility into cybersecurity data without paralyzing software development, organizations must move away from disparate tools and spreadsheets. Effective ConMon today demands a proactive risk management strategy built on automated visibility and deep architectural context, allowing teams to identify and remediate vulnerabilities before they can be exploited.
Visibility: You Can’t Protect What You Can’t See
The foundation of proactive
risk management
is a complete, automated inventory with context on how different resources connect. FedRAMP stresses the importance of having accurate inventory assessments through Rev 5’s
CM-8 (Information System Component Inventory)
control, requiring organizations to maintain an accurate account of all system components.  The same is true if your organization is pursuing the newer FedRAMP 20x assessment, with Key Security Indicator (KSI) PI-00 requiring an up-to-date asset inventory or code defining all deployed assets.
Figure 1: Wiz for Gov helps not only quickly helps build SBOMs, but to provide quick, accessible visibility into many different technologies deployed, assisting to meet the intent behind many NIST SP 800-53r5 based FedRAMP Rev 5 controls as well as the newer FedRAMP 20x KSIs
In a dynamic cloud environment, manual spreadsheets are obsolete from almost the moment they are generated. Wiz for U.S. Government (
Wiz for Gov
) provides an agentless, accurate view of cloud environments within minutes. This isn't just a list of virtual machines; it’s a deep map of:
Identities
(Who has access?)
Workloads
(What is running?)
Data
(Where is the sensitive information?)
Network
(How is it exposed?)
Figure 2: Automating discovery and identification of what is running, who has access, where sensitive information resides, and how these resources are exposed are critical in reducing the effort required to meet monthly FedRAMP ConMon requirements
Prioritization: Beyond the CVE
The "noise" of traditional
vulnerability management
is the antagonist of agility. A standard
vulnerability scan
might return 10,000 "High" or "Critical" Common Vulnerabilities and Exposures (CVEs) based upon the Common Vulnerability Scoring System (CVSS). For a FedRAMP environment, the
Plan of Action and Milestones (POA&M)
process requires you to track and remediate these within strict timelines (30 days for CVEs with a High CVSS score). Without upfront risk adjustment, this requirement can quickly become burdensome.
Helpfully, NIST SP 800-53r5, the primary basis for the FedRAMP baseline controls in Rev 5 assessments, does not view vulnerability severity as synonymous with risk.  Instead, risk is defined as “[a] measure of the extent to which an entity is threatened by a potential circumstance or event, and typically is a function of: (i) the adverse impact, or magnitude of harm, that would arise if the circumstance or event occurs; and (ii) the likelihood of occurrence.”
This definition underscores that, without the context of impact and potential of occurrence, it is not possible to understand the impact on risk reduction by focusing solely on the CVSS score of a
CVE
.  If you treat every CVE as equal, your engineering team will spend the majority of their time on maintenance at the expense of innovation.
New initiatives around FedRAMP, including the 20x program, double down on this broader view of risk through POA&M risk adjustment, explicitly moving away from simple vulnerability reporting to a more prioritized approach to risk remediation and mitigation.  Wiz for Gov provides accelerated access to details necessary for these risk adjustments through the Wiz Security Graph, effectively automating the evidentiary burden for Information System Security Officers who must justify POA&M remediation timelines to their Authorizing Officials. Instead of a flat list, Wiz identifies "Toxic Combinations." For example:
Low Risk:
A High-severity CVE on an internal, isolated server. (Low Likelihood, Low impact)
Critical Risk:
The same High-severity CVE on a server that is
publicly exposed
and has a
high-privileged identity
attached to it. (High Likelihood, High impact)
By prioritizing remediation based on the NIST 800-53r5 definition of risk, organizations can implement FedRAMP Rev5's RA-5 (Vulnerability Monitoring) and RA-07 (Risk Response) controls, managing vulnerabilities in accordance with their risk tolerance and focusing on the top issues that actually represent a path for an attacker.
Figure 3: With thousands of preconfigured rules out of the box and the ability to custom define, Wiz for Gov quickly automates risk discovery and assessment, providing prioritized findings based upon identified toxic combinations that pose the greatest risk to organizations
The newer FedRAMP 20x framework expands upon this methodology for prioritizing risk remediation based upon impact through KSIs such as
SC-06
and
MLA-05
which call for risk-informed, prioritized approaches for security patching and vulnerability remediation.
Automating the ConMon Cycle
Continuous monitoring isn't just about finding risks; it’s about the "Agile Foundation" previously discussed in
Lesson Three of Part 1
. Wiz for Gov helps automate the evidence collection needed for monthly ConMon reports. This table highlights several of these FedRAMP controls.
FedRAMP Rev 5 Requirement
Wiz for Gov Capability
Configuration Settings (CM-6)
Continuous assessment against CIS benchmarks and FedRAMP-specific configuration baselines
Information System Component Inventory (CM-8)
Automated, real-time discovery of all cloud resources and technologies
Vulnerability Scanning (RA-5)
Agentless scanning of operating systems, applications, and libraries without performance impact
Risk Response(RA-7)
Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance
Protection of Information at Rest (SC-28)
Discovery and protection of sensitive data to protect against unauthorized disclosure
Turning "Audit Time" into "Uptime"
By using Wiz for Gov to handle the heavy lifting of proactive risk management, Wiz has been able to significantly reduce the administrative burden of our own FedRAMP High ConMon. This automation allows our security team to act as partners to our developers, providing them with clear, prioritized instructions rather than "walls of red" in a spreadsheet.
In the next part of this series, we will look at
Preventative Risk Management
, and how we "shift left" to build securely by design within the software development lifecycle to stop these risks from reaching production in the first place.
Tags
#
Public Sector