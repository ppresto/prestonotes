---
url: https://www.wiz.io/blog/securing-critical-infrastructure-in-cloud-era
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-10-30T08:00:00-04:00
extraction_mode: static_fetch
content_hash: afac10cdf54b
---

# Securing U.S. Critical Infrastructure in the Cloud Era | Wiz Blog

The US’s critical infrastructure (CI), systems ranging from those that deliver electricity, clean water, and healthcare, to financial services, is undergoing a fundamental transformation. The controls for physical equipment, like pumps at a water utility or switches on the power grid, are moving from self-contained, private data centers to the interconnected cloud.
That shift brings innovation and efficiency, and as
recent NSA guidance suggests
, can also unlock security advantages. But it also introduces different risk dynamics. The importance of these systems becomes starkly clear when they fail, as we’ve seen in
recent cyberattacks impacting airports across Europe.
At Wiz, we see these threats firsthand. We protect millions of cloud workloads across the public and private sectors, including critical industries like manufacturing, energy, and healthcare. We believe protecting essential services requires a modern approach that combines smart policy with the right technology.
The Modern Threat to Critical Infrastructure
From our vantage point securing thousands of cloud environments, we see three trends emerging that every policymaker needs to understand, each proven by real-world events:
The Erosion of Traditional Defenses:
Cybersecurity once meant building digital walls around a physical location. As critical operations move to the cloud, those walls have effectively dissolved, leaving the traditional defensive model obsolete. Critical infrastructure services, often defined by operational technology or confined to a physical area, were late to adopt the cloud.
While famously on-prem, adoption is accelerating:
98% of financial services now use the cloud
and a
2024 SANS survey
found 26% of industrial organizations are connecting even their sensitive OT systems. This landscape is made up of cloud services, software, and user accounts.
The risk isn’t a single flaw, but the problematic combination of multiple vulnerabilities and weaknesses. A public-facing application, a permissive identity, and a connection to a sensitive database can together form a clear attack path to an operator's most critical systems. Traditional security models often miss this context.
Sophisticated Global Adversaries:
From nation-states to global crime syndicates, hackers have adapted their tactics for the cloud. As CISA has warned, groups like the state-sponsored
Volt Typhoon
and
Scattered Spider
are no longer just breaking down the front door. They now focus on stealing legitimate employee credentials and using a company’s own IT tools against it to move around undetected. This technique signals a clear strategy: gain a foothold in critical systems, and wait.
The Blurring Line Between Digital and Physical Worlds:
The physical separation between a company's IT network (like email) and its operational technology (OT) that controls machinery is no longer black and white. The 2021
Colonial Pipeline
ransomware attack is the perfect example. The hack started on the IT network, but the fear that it could spread to the systems controlling the pipeline forced a physical shutdown, leading to fuel shortages across the East Coast. This event was a watershed moment, showing that digital vulnerabilities can have massive real-world consequences.
The Current Policy Foundation
In the last few years, the U.S. government has taken meaningful steps to address these threats:
Executive Order 14028 (Improving the Nation's Cybersecurity)
:
This landmark directive pushed federal agencies toward a "Zero Trust" model (which trusts no one by default) and promoted the use of a
Software Bill of Materials (SBOMs)
, which is like a list of ingredients for software so you know what's inside.
The Cyber Incident Reporting for Critical Infrastructure Act
:
This law requires CI operators to report major cyberattacks and ransomware payments to the government, providing crucial data on the threats we face.
Sector-Specific Rules: Agencies like the
Transportation Security Administration
and
Environmental Protection Agency
(procurement checklist) have issued cybersecurity rules for pipelines, while the
North American Electric Reliability Corporation Critical Infrastructure Protection
standards have long governed the electricity sector. Additionally, state-level regulations such as those proposed by the
New York Public Service Commission
and
New York Department of Financial Services
are seeking to ensure the resiliency of our digital infrastructure.
These policies represent a critical first step, but the speed of the technology will almost always outpace policy action. Today’s cyber regulations were largely designed for a static, perimeter-based on-premise world that is rapidly disappearing.
This raises a critical question: If technology is moving so fast, what stops new policies from becoming stale?
The answer is to shift from static, prescriptive rules to an adaptive, outcome-driven framework. All too often, governments mandate a specific tool or checklist. Wiz proposes a process-oriented set of solutions. The US President’s call for “rules-as-code” in his
June Executive Order on cybersecurity
is a sign of progress; however, ensuring technical indicators are focused on security outcomes will be critical.
The focus must be on continuously building resilience.  This includes requiring modern security capabilities and practices like near-real time visibility and Infrastructure-as-Code (IaC), funding modernization of legacy systems, and creating permanent structures for collaboration. This approach creates a framework for resiliency designed to evolve with technology and threats because it is based on outcomes rather than processes.
A Multi-Level Government Action Plan for CI Security
So, where do we go from here? The challenge is immense, but the path forward doesn't have to be. It requires a shared commitment and specific, actionable policies across every level of government.
Federal Government
Reconsider Regulations for the Cloud Age:
Congress should direct federal agencies–including the Department of Energy, Department of Homeland Security, and Department of the Treasury–to update their sector-specific rules. Instead of prescribing outdated, perimeter-based security, regulations embolden public-private partnerships that improve security outcomes. They should also require operators to maintain
continuous visibility
into their cloud environments and adopt standards that reflect modern threats. These regulatory standards should be linked through common aligned baselines to avoid conflicting directions for the many platforms in the supply chain that support multiple critical infrastructure providers.
Fund Security Modernization and Training:
Many smaller utilities and local operators lack the budget and staff to keep up with evolving cyber threats. The federal government should
continue to modernize
grant programs in the U.S. Department of Homeland Security to specifically support the adoption of cloud-native security tools and provide cybersecurity training for the CI workforce.
Supercharge Threat Intelligence Sharing:
Congress should reauthorize long-standing legal authorities, such as
CISA 2015
, that recently lapsed to ensure rapid cyber threat information sharing. As threats continue to accelerate, collaboration is more important than ever. Without these authorities, legal barriers can slow critical information from reaching the people who need it most.
State and Local Governments
Establish State-Level CI Cybersecurity Commissions:
Governors and state legislatures should create dedicated cybersecurity commissions as seen in
Texas
,
Virginia
,
North Carolina
,
Georgia
, and
Maryland
. These bodies would bring together public utility commissions, state agencies, and private operators to collaborate on statewide security baselines, share information, and coordinate response efforts.
Integrate Cyber Attacks into Emergency Drills:
Local emergency managers are on the front lines. They should incorporate cyber-physical attack scenarios into their regular planning and drills. Practicing these scenarios builds resilience where it matters most.
Use State Buying Power to Drive Security:
States should adopt procurement policies requiring software vendors to provide an SBOM to the state on-demand for any product sold to state agencies or regulated infrastructure. This will ensure data are quickly available to authorities if a potential threat arises without creating the risk of thousands of repositories across the nation. Critically, these policies should also encourage the use of IaC, ensuring that security is scanned and embedded
before
infrastructure is ever deployed to the cloud.
Facilitate Coordinated Resiliency Support:
National Guard, state cyber defense teams and other experts can be leveraged to examine the resiliency of critical services in the state–particularly those entities that have limited internal resources. The resulting analyses could be utilized for targeted upgrades to critical infrastructure or inform the state and local grant programs. More broadly, the state should seek creative solutions focused on backstops that provide visibility, continuous monitoring, and automated risk assessment of these environments.
International Cooperation
Establishing Norms to Protect Civilian Infrastructure:
Cyberattacks cross borders instantly. Building on successes like the Counter Ransomware Initiative, the U.S. State Department should lead an international effort to solidify global norms that declare civilian CI off-limits for state-sponsored cyberattacks, just as physical attacks on such targets are treated under the laws of armed conflict.
Harmonize Global Incident Reporting:
A multinational energy company may face different cyber incident reporting rules in every country it operates. The U.S. should work with key allies to harmonize these requirements, making it easier for companies to comply and providing a clearer global picture of threats.
Our Commitment
Securing our nation's CI against a new generation of threats is a national security imperative. It requires a sophisticated understanding of both the technology and the evolving policy landscape. Wiz stands ready to provide our expertise and partner with government agencies and CI operators, to develop and implement the effective security strategies needed to protect our most essential services.
Get a demo
Tags
#
Security
#
Public Sector