---
url: https://www.wiz.io/blog/adding-wiz-code-to-fedramp
source_name: blog_public_sector
fetched_at: 2026-03-02T17:52:04Z
published_at: 2024-12-09T07:00:01-05:00
extraction_mode: static_fetch
content_hash: 532ac87a1b2e
---

# Wiz Adds Code Security to its FedRAMP Offering | Wiz Blog

Wiz Code is now generally available for customers as part of
Wiz’s FedRAMP authorized offering, Wiz for Government
! The addition of Wiz Code into our FedRAMP offering reconfirms our commitment to unify application & cloud security for all users; enabling our government and regulatory-focused customers to shift security to the left by extending security coverage to applications, infrastructure, and configurations at every stage of development.
Securing the Supply Chain: Lifecycle of Code
Wiz Code
helps to secure the cloud-native development lifecycle, from code to cloud to runtime. Wiz Code extends Wiz for Gov’s capabilities by enabling security teams to apply the same policies from their cloud environments to development workflows and pipelines and natively scan for vulnerabilities in third-party code libraries, as well as identify license compliance issues, insecure base images, IaC misconfigurations, and exposed secrets.
In addition, Wiz Code extends Wiz Cloud’s capabilities by accelerating the remediation of cloud risks from source code. By connecting to code repositories and CI/CD pipelines, Wiz correlates data and maps critical cloud risks in the Wiz Security Graph back to their source code repository and development owner. This decreases remediation time by giving security & development teams a shared view of their most critical risks cloud-to-code, and making it clear who is responsible for specific issues. A unified view of cloud & application security accelerates remediations, breaks down siloes, and drives more efficient collaboration between teams.
A history of siloed development
The cloud is now code. Modern DevOps practices like containerization and infrastructure as code (IaC) have blurred the lines between applications and cloud infrastructure. However, application & cloud security are still treated as separate concerns; operating in siloed tools and business functions. This disconnect has led to the duplication of efforts, gaps in security coverage, inefficiencies with multiple point-solutions, and a higher total cost of ownership—all while leaving the critical issues unresolved and teams overwhelmed by alert noise.
The use of siloed scanning tools between code and production brings a lack of unified visibility and context to understand how code configurations impact the broader production environment. Any misconfigurations identified in production become difficult to trace back to the code repository and developer, which compounds and slows down remediation efforts.
Within highly regulated and government environments, further challenges exist as new code deployment and production operating environments need to be accountable against an authorization to operate (ATO). These ATO controls are documented within the NIST Special Publication (SP) documentation family, and specify system processes and requirements organizations must account for during regular audits.
“Systems, system components, and system services may deviate significantly from the functional and design specifications created during the requirements and design stages of the system development life cycle. Therefore, updates to threat modeling and vulnerability analyses of those systems, system components, and system services during development and prior to delivery are critical to the effective operation of those systems, components, and services..."
SA-11(2) NIST SP 800-53r5, FedRAMP Security Controls Baseline- Moderate
Reducing Application Risk while Accelerating Time to Deployment
Development speed has increased. With the adoption of agile development practice and developers beginning to embrace AI code-completion assistants, development teams are committing code at a velocity that is faster than ever. The use of multiple, siloed legacy solutions cannot keep up; often slowing down developers with a large volume of alerts and decreasing overall productivity.
Wiz Code provides prioritized real-time security feedback and fix suggestions
directly within developer workflows
. Wiz Code integrates into different steps of the development lifecycle:  IDE, pull requests, and CLI workflows – to remediate existing risks and prevent the deployment of new risks. By scanning their code against the same cloud, host, vulnerability, and other cloud security rules, organizations can weave security directly into the development lifecycle; reducing time to deployment, and scaling modernized security for the cloud.
Using Wiz Code, organizations can break down silos by reducing the use of multiple scanning tools; lessening the security debt carried into the next sprint cycle
To accelerate remediation of risks identified within their cloud environments, organizations can enrich their Wiz Security Graph with Wiz Code to build an inventory of code repositories and developer identities. The inclusion of these data into the Security Graph correlates findings in code (e.g., CVEs/KEVs, secrets, IaC) with misconfigurations in version control and CI/CD, for a unified, and comprehensive, risk assessment. This quickly connects critical issues found back to their code components for more efficient remediation.
“Risk management is a holistic activity that affects every aspect of the organization including the mission and business planning activities, the enterprise architecture, the SDLC processes, and the systems engineering activities that are integral to those system life cycle processes.”
NIST SP 800-37r2, Risk Management Framework for Information Systems and Organizations
These advantages enable continuous monitoring of code to cloud with development guardrails to help prevent the introduction of misconfigurations and vulnerabilities. This sets the foundation for a secure software supply chain that is not isolated to purely within the DevOps factory, but contains the necessary context to enable developers to understand how their code impacts the broader security posture of the production cloud environment. This is a critical step towards enabling stronger collaboration between teams across the cloud-native development lifecycle, and is critical when moving towards a continuous Authorization to Operate (cATO), where feedback between SOC, AppSec, DevOps, GRC, and other teams is necessary to
continuously monitor production cloud environments
.
Addressing new use cases through Wiz Code
One policy engine for code, cloud, and runtime:
Wiz Code expands the Wiz unified policy engine that enforces security controls consistently across the entire development lifecycle. This includes SCA and SBOM, as well as scanning for open-source CVE vulnerabilities, malware, exposed secrets, IaC misconfigurations, and sensitive data. By correlating findings across code, cloud, and runtime, Wiz merges them into a single view, helping teams identify root causes and address issues faster and more effectively.
WizCLI scan in a pre-commit git hook: contextualizing an exposed secret finding
The same risk seen from the Wiz Security Graph
Code-to-Cloud and Cloud-to-Code mapping with the Wiz Security Graph:
Wiz Code uses the Security Graph to connect code repositories and CI/CD pipelines, to cloud environments and back. This capability enables security teams to prioritize the most critical issues, mapping them across the entire stack—from misconfigurations in cloud infrastructure to vulnerabilities in third-party libraries and exposed secrets. Additionally, Wiz Code highlights ownership context, making it clear which development teams are responsible for specific issues. This accelerates remediation, eliminates silos, and drives efficient collaboration.
Accelerated remediation of misconfigurations and vulnerabilities in the cloud:
Wiz Code is deeply embedded into developer workflows and generates one-click fix suggestions, so developers don’t have to leave their favorite tools. This empowers organizations to fix cloud issues in code faster, reducing their window of exposure and exploitation. The ability to trace risks back to the repository and the developer that introduced them allows teams to quickly apply fixes and compare before/after states, ensuring the issue is fully remediated.
Starting secure in code with Wiz guardrails:
Wiz Code offers real-time security feedback, enriched with cloud insights, directly in the IDE and pull requests. This helps developers anticipate the impact vulnerabilities or exposed secrets will have once their code is deployed. By ensuring robust code security from the start, development teams can avoid accumulating security debt, keeping their sprint cycles focused on value delivery while maintaining a high level of security.
Extending security posture management to the pipeline:
Wiz Code extends Wiz’s CSPM capabilities to developer environments like version control and CI/CD systems. By integrating configuration data from developer tools into the Security Graph, Wiz Code provides more accurate risk prioritization, helping teams focus on critical attack paths. In addition, security teams can assess their degree of compliance with emerging frameworks such as OWASP TOP10 CI/CD Risks or OpenSSF Source Code Management Best Practices.
Scaling the cloud through unified visibility
The quick integration of Wiz Code into the Wiz for Gov offering comes shortly after the addition of the
Wiz Runtime Sensor
, moving closer to feature and product parity between the experiences for development teams leveraging either the Wiz Commercial or Wiz for Government offerings.  This standardizes code security, and unlocks toolsets and capabilities previously unavailable to these regulated environments.
The addition of Wiz Code to the Wiz for Gov FedRAMP offering enables cloud builders and defenders to engage together in a collective effort to reduce risk and accelerate cloud development. The guardrails within the IDE and CI/CD SDLC pipeline provided by Wiz Code become a critical anchor for an organization's migration to a
secure software supply chain
. When this anchor is leveraged alongside Wiz’s innovative continuous monitoring CNAPP solution offered through Wiz Cloud, organizations with government regulated environments can secure their entire cloud-native application lifecycle, from code to runtime.
Tags
#
Product
#
Public Sector
#
Wiz Code