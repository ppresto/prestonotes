---
url: https://www.wiz.io/blog/wiz-spotify-backstage
source_name: blog_news
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-02-06T08:00:01-05:00
extraction_mode: static_fetch
content_hash: 1964966ede1d
---

# Wiz + Spotify Backstage: Security at the Developer’s Desk | Wiz Blog

Every developer has a mental map of their services. You know what you own. You know what’s on fire. You know what used to be on fire but someone swears is “fine now.” And when something breaks, you usually know where to look first.
Security issues don’t always show up on that same map. A risk pops up somewhere else, described in a different language, detached from the services, projects, and ownership models developers actually use. Now the first question isn’t how to fix it—it’s whether it even belongs to you.
That’s why we’re excited to announce the Wiz and Spotify Backstage plugin, now in General Availability. The plugin surfaces Wiz Issues and Vulnerabilities directly in the Spotify Backstage portal by mapping Wiz projects to Backstage components.
For each component, developers can search findings by rule, resource, or CVE, and quickly see vulnerability counts and severity at a glance. When it’s time to take action - whether that’s remediation, investigation, or guidance - developers can jump straight from Backstage into Wiz with full context.
How Wiz maps risk to ownership
The Wiz plugin for Backstage works to solve the age old problem of unclear ownership in security. At the core of this is the
Service Catalog
, giving developers the context they need to see risk in action, understand impact, and know exactly which services they own.
Services in Wiz provide the horizontal view, showing developers the resources that make up an application or microservice across environments. Services can also be combined with Wiz Projects, which sit above services vertically and define boundaries, access, and governance across teams and accounts -- like by business unit or geographic team. Together, they make ownership clear so developers can act quickly, without wading through dashboards or filling out tickets.
How Projects and Services Work Together
The Wiz and Spotify Backstage plugin brings this ownership-first model into the developer portal. Risk is mapped by Project and surfaced next to the Backstage components developers already use every day, so findings show up where developers are reasoning about their systems and each developer sees the right findings for the systems they own.
For example, a developer might open a Backstage component representing a public-facing website. The plugin shows that this component has multiple vulnerable resources in Wiz, and by exploring the Wiz platform, they can see that these resources are running on an internet-exposed load balancer visualized in the Wiz Security Graph. The developer can immediately assess the risk and, with one click, jump into Wiz to understand impact and start remediation—without leaving Backstage.
Bringing Security to the Development Desk
The Wiz plugin for Backstage further democratizes security by bringing findings directly into the tools developers know and use daily:
See Issues and Vulnerabilities by Component:
Each Backstage component defines how Wiz pulls Issues and Vulnerabilities from its associated Projects in Wiz. The plugin then shows all related issues and vulnerabilities right next to the component, giving developers an instant view of the risks affecting the components they own.
Search and Filter Issues:
Inside the Backstage portal, developers can search by rule, resource, or CVE, making it easy to identify and focus on remediating the Issues and vulnerabilities most relevant to their work.
Understand impact quickly:
The plugin shows a total count of vulnerabilities per component, along with their severity, the Issues they’re related to, remediation status, and when the vulnerability was first and last detected - helping teams prioritize without leaving Backstage.
Remediate and Respond Seamlessly:
To investigate Issues and vulnerabilities deeper, or when remediation is needed, one click takes developers into Wiz with full context, remediation guidance, and the code-to-cloud pipeline to understand impact, triage, and remediate quickly.
Wiz plugin for Backstage in action
By bringing security closer to developer workflows and aligning Issues and Vulnerabilities to the projects developers care about and own, the Wiz plugin for Backstage makes security an enabler, keeping momentum with the pace of development.
Install the Wiz plugin for Backstage today, to bring security into your developer portal. Joint customers can follow the guide in the
Wiz Docs
(login required) to get started.
Tags
#
Product & Company News
#
Wiz Platform