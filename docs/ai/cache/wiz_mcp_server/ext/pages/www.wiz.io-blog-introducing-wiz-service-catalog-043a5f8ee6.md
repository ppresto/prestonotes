---
url: https://www.wiz.io/blog/introducing-wiz-service-catalog
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-01T08:48:46-05:00
extraction_mode: static_fetch
content_hash: 3dffdb767416
---

# Wiz Service Catalog: Expand Risk Visibility & Ownership | Wiz Blog

When ownership breaks down, remediation slows down. Modern cloud environments are complex: distributed microservices, APIs, containers, and ephemeral components make it hard for developers to understand and manage the security posture of the services they own, and hard for security teams to find the right owners for fixes.
That’s where the
Wiz Service Catalog
comes in. It gives security, platform, and development teams a shared view of cloud risk, aligned with the way applications are actually built and operated.
We’re excited to announce that the Service Catalog is now generally available for all Wiz customers. Building on the capabilities we
introduced during public preview
, this feature helps teams align risk visibility to how applications are built and maintained. The Service Catalog makes it easier to understand and prioritize threats across your service and its dependent components, identify the right owners for remediation, and kick off automated, dev-first workflows for fast remediation.
Complete view of a service in Wiz Service Catalog.
A Shared View of Cloud Risk
The Wiz Service Catalog helps teams identify ownership and accelerate remediation by mapping how applications are structured. Wiz automatically groups related cloud resources into services—logical units that reflect how teams build and run applications, like “payments” or your devs’ favorite acronym-turned name.
Service discovery is automatic. Wiz detects services using built-in discovery rules, following best-practice tagging conventions and supporting popular tools like Helm and ArgoCD. Once identified, you can review, accept, and add services to your catalog across your entire environment.
Wiz also identifies occurrences of the same security risk across multiple locations or environments, helping to identify the root issue across multiple deployments. This allows developers to act on the risk itself, rather than the deployment characteristics—so every team member can focus on the root cause of risks tied to the services they own, and take action faster.
Like Wiz projects, each service includes the resources it depends on, the environment it runs in, who owns it, and all the relevant security findings tied to it. Services can be used alongside projects to further focus scope and add clarity for ownership: you may use projects for business units or departments, and services help you narrow your focus even further for specific development teams.
See Risk Across Your Service’s Entire Dependency Tree
Powered by the Wiz Security Graph, the Service Catalog maps out related cloud assets, data stores, networking endpoints, repositories, and code, uncovering the full dependency tree of your services and exposing relationships that might otherwise remain hidden.
This context helps both security and development teams understand shared dependencies, assess impact, and prioritize fixes. And by linking infrastructure, code repositories, and CI/CD pipelines, Wiz traces risks back to their source—down to the repository and responsible developer—so your team can validate remediation with confidence.
The result: deeper visibility, clearer accountability, and faster action.
Service with related resources.
Service-Level Insights for Security Teams
Once you have a complete view of a service and its dependencies, Service Insights help you take the next step: understanding risk in context.
Use service insights to answer critical questions about AI services:
Which AI services have exposed secrets?
Which AI-enabled services access sensitive data?
Which AI services have vulnerabilities?
You can use service insights to visualize potential attack paths and trigger automated workflows, like remediating overprivileged accounts connected to AI services. These insights also make it easier to answer key leadership questions, such as assessing overall AI-related risk posture across your environment.
AI service with secret findings, critical issues, and running EOL technologies.
Frictionless Remediation for Developers
Finally, remediation itself. Wiz takes a developer-first approach to remediation. Vulnerabilities are grouped by component, showing how many resources use each component and which updates resolve the issue. Developers can prioritize the most impactful fixes without waiting for security handoffs.
With a unified view of service-level issues, developers can self-serve remediation and integrate notifications directly into their workflows, whether via tickets, chat, or automation. And since ownership is clear, issues get to the right person, every time.
Fix it once—at the source—not 20 times downstream.
Service Catalog: Available today
The Wiz Service Catalog is now generally available to all customers, with no additional licensing required. Go to
Service Catalog
today to define your services and see your environment in a new light.
Tags
#
Product