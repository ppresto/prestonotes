---
url: https://www.wiz.io/blog/aws-re-invent-2025
source_name: blog_news
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-03T08:30:00-05:00
extraction_mode: static_fetch
content_hash: 92ac4237dd14
---

# Wiz Product Announcements at re:Invent 2025 | Wiz Blog

AWS re:Invent is about rethinking what's possible in the cloud. This year’s agenda is jam-packed with sessions about AI, infrastructure innovations, and of course, security. As we catch up with customers, meet new members of the cloud security community, join sessions, and of course,
welcome everyone to our coz(zz)y show floor home base
, we’re excited to recap the product releases we unveiled throughout the event.
This week, we launched new features and capabilities that strengthen visibility from code to cloud, help security and engineers work better together to keep cloud environments secure, and provide a more transparent roadmap experience. From WizOS to AI-powered SAST, each feature builds on Wiz’s agentless model to help teams protect everything they build and run in the cloud.
Wiz product launches at re:Invent expand code to cloud visibility
Strengthen Secure Development
The Wiz Security Graph gives teams a shared language to see risk clearly, prioritize what matters, and act fast across their entire cloud environment. Last year, we extended that visibility with Wiz Code, giving risk insights from code repositories through the CI/CD pipeline so security teams can understand their risk posture throughout the full application lifecycle.
Introducing Wiz Code SAST
Wiz SAST
expands Wiz Code into proprietary code analysis, giving teams visibility into vulnerabilities in the code they write and the cloud environments where that code actually runs. Once scanned, SAST findings flow into the Wiz Security Graph, where they’re enriched with runtime workload exposure, data access, identity privileges, and attack path insights.
An AI triage agent helps AppSec teams quickly understand whether a finding is exploitable or likely a false positive, and the AI remediation engine gives developers targeted code fix suggestions in PRs, accelerating resolution and reducing back-and-forth.
By bringing SAST into the same AppSec unified operating model as SCA, secrets, and IaC, teams can detect issues earlier and resolve them with the cloud context and workflows they’ve come to expect from Wiz.
SAST AI Agent for triaging and explaining findings in code.
Start Secure with WizOS, Now GA
WizOS
reimagines secure development starting at the foundation: secured container images. Nearly 40% of critical and high-severity CVE findings on containers come from the base image layer. WizOS solves this by providing secure, trusted container images built and continuously maintained by Wiz with near-zero CVEs. It shifts the security paradigm from
scanning and fixing
to
starting secure
, eliminating a huge workload of patching for DevOps teams and reducing vulnerability load for security.
WizOS is backed by the unparalleled visibility of the Wiz platform to make adopting secured images seamless. Wiz provides visibility into all existing container images and their risk posture, proactively identifies WizOS image swap opportunities, and prioritizes them based on risk. WizOS is now GA, with an expanded image catalog and a new integration into Mika AI to provide AI-powered migration planning, guidance, and prioritization directly in Wiz.
Leverage Mika AI to plan and prioritize your WizOS migration
Bridge Engineering and Security Visibility with Service Catalog, Now GA
Finally, to help make it easier for engineering and security teams to work together, we’re also releasing the
Wiz Service Catalog
into general availability. The Wiz Service Catalog organizes cloud resources into logical services such as a payments or registration service (or your devs’ favorite code-name…), bringing a development team-centric and application-level view into the Wiz platform.
Service Catalog clarifies ownership by mapping service owners to findings and helps developers manage the security posture of what they own, including discovery of related resources (service dependencies) and applying code-to-cloud context within the service lens.
Together, these capabilities give security, platform, and development teams a shared view of cloud risk, aligning security with the way applications are actually built and operated.
Complete view of a service in Wiz Service Catalog.
Detect Exploitable Risk: Exposure Management Now GA
As we continue to extend Wiz to give more visibility across cloud environments, we also are investing further in capabilities to help teams to prioritize critical risk beyond the cloud.
Wiz Exposure Management
, now generally available, takes our comprehensive approach to the next level, giving teams complete control over their exposure across their entire environment-cloud, on-prem, code, SaaS, and AI. Exposure Management allows organizations to detect, validate, and prioritize the exposures that matter with context, driving measurable risk reduction.
We first talked about Exposure Management earlier this year. It's an umbrella approach that brings together every risk across any infrastructure that determines whether an exposure is actually exploitable and identifies its true impact on the environment. With Wiz, teams can unify a range of different signals from across their stack to help answer the question:
“Which exposures are truly exploitable and represent real attack paths in our environment?”
Exposure Management at Wiz includes both
Wiz Unified Vulnerability Management (UVM)
and
Wiz Attack Surface Management (ASM)
to surface true exposure, or the issues that form viable attack paths that threat actors could actually exploit.
Wiz UVM
centralizes vulnerability data from all of your scanners — including third parties — into a single tool for prioritization. It centralizes vulnerability findings from cloud, on-prem, and application environments into the Wiz Security Graph, enriching them with context, and enabling vulnerability management teams to consolidate insights and understand the highest priority risks, assign ownership, and drive faster remediation at scale. It extends beyond vulnerabilities to risks like secrets and data to evolve towards proactive exposure remediation.
Wiz ASM
shows you everything attackers can see from the public internet, helping teams understand who owns each exposed asset, what it connects to, and how it impacts business risk. It identifies which risks are actually reachable and exploitable from the outside, marking these issues as "external risk" to show which risks are "hours away from being found by attackers".
Together, Wiz Exposure Management capabilities ensure you know the attack paths that matter: the risks you need to tackle first, their owners, and the business impact of reducing those threats.
What’s ahead
Every launch here at re:Invent builds on the same foundation: the Wiz Security Graph. It’s what connects builders and defenders, visibility and action, code to cloud.
As we continue to innovate and deliver more features that provide visibility, enable prioritization, and drive faster remediation, we also are investing in more ways to help our customers stay up to date with our platform innovations.
Our
Roadmap Tracker
, now generally available, centralizes the latest and greatest updates directly from our product team, so you always have a clear view of upcoming features and priorities.
Check it out and let our teams know what feedback you have on our upcoming innovations and what you’d like to see next!
Check out the full details of all our re:Invent 2025 announcements:
Wiz Exposure Management GA
Introducing Wiz SAST
WizOS GA
Wiz Service Catalog GA
Tags
#
Product & Company News
#
Wiz Cloud
#
Wiz Code