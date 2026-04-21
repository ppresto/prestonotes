---
url: https://www.wiz.io/blog/wizos-secured-image-adoption-with-ai
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-01T08:00:00-05:00
extraction_mode: static_fetch
content_hash: d8261d72e96f
---

# WizOS: Secured Images Powered by AI | Wiz Blog

Today we’re excited to announce the General Availability of WizOS to help teams eliminate inherited container image risk and build on a foundation that is minimal, secure, and trusted.
Container images are the foundation of modern applications, but they are frequently sourced from public repositories that lack security guarantees and verifiable provenance. This introduces risk to applications in two ways:
Known vulnerability risk:
Container images introduce vulnerabilities that kick off an endless workload of triage and patching for security and engineering teams. According to Wiz research, container base images account for nearly 40% of critical and high severity CVE findings on containers.
Unknown supply chain risk:
As attackers continue to target the open source supply chain and compromise popular package repositories, the risk of introducing compromised packages through publicly sourced container images and packages is on the rise.
WizOS
is addressing both risks at the source: near-zero CVE container image built and maintained by Wiz, with cryptographically verifiable provenance so you can trust what’s entering your supply chain. WizOS includes a secured package repository so that developers can easily customize images while maintaining trust.
We’re thrilled to introduce WizOS to GA with an expanded image catalog and AI-powered platform features designed to accelerate secured image adoption.
Start Secure: Reimagining How We Reduce Risk in the Cloud
From the beginning, Wiz has helped organizations cut through the complexity of cloud risk. Our approach centers on context and prioritization. We combine risk signals and environment context into clear attack paths that matter, enabling customers to achieve milestones like the
Zero Critical Club
.
Unified code-to-cloud scanning and context-driven prioritization have changed the game for addressing critical risks efficiently, but as vulnerabilities continue to multiply and supply chain compromises become more prevalent, the next step is rethinking how this risk gets introduced in the first place.
This is where WizOS comes in. To address supply chain risk and inherited vulnerabilities, we must make the leap from a pure vulnerability management approach to truly starting from a secured foundation. WizOS shifts the security equation by proactively eliminating a major source of inherited risk and supply chain uncertainty before it ever reaches the pipeline. Building on a trusted foundation is the next evolution in securing cloud applications.
The Platform Powering Secured Image Adoption
Adopting secured images requires both migrating existing
container images
and using secured images in new builds. WizOS is backed by the Wiz platform to support organizations in their adoption journey through a full platform approach to secured image adoption:
Gain Visibility:
Use the
Container Image Inventory
in Wiz to gain visibility into every image in your environment. Understand the risk profile of each image - every vulnerability and issue finding associated with it.
Mitigate Critical Risk:
Filter the image inventory to identify which images can be swapped for a WizOS image. Identify images that have associated critical issues and prioritize them for migration.
Start Secure:
Empower development teams to build with images from the WizOS Secured Image Catalog. Images are ready to use off the shelf, with a package manager and shell included, and easily customizable using the Wiz package repository.
Enforce Guardrails:
Leverage Image Trust Policies and the Wiz Admissions Controller to prevent vulnerable new images from reaching production.
Streamlining Secured Image Migration with AI Assistance
You can now use AI capabilities inside the Wiz platform and via Wiz MCP to empower developers in their migration to WizOS images.
Migration Planning and Prioritization with Mika AI
Leverage Mika AI to plan and prioritize your WizOS migration. Mika AI is fully integrated with your container image inventory and the WizOS Secured Image Catalog. Ask Mika to:
Show me the highest risk images that can be swapped for a WizOS image
Create a WizOS image migration plan prioritized based on risk
Calculate the vulnerability reduction I could achieve by migrating to WizOS
Image Swap Assistance with Wiz MCP + WizOS
Leverage the Wiz MCP and your AI coding assistant of choice to implement image swaps directly in the IDE. Wiz MCP can surface the appropriate WizOS images based on context in your dockerfile. Your AI coding assistant can then leverage context from Wiz MCP to suggest and apply edits to your dockerfile to make migration to the WizOS image easy, whether your original images are alpine, docker, ubuntu, or others.
What’s Next
WizOS product development continues in two veins: expanding our image coverage, and further streamlining secured image adoption for organizations. Since public preview, we have expanded our Secured Image Catalog to include coverage for more application images and Kubernetes native images. We will soon provide customers with direct visibility into upcoming images in the catalog and via the Wiz Roadmap Tracker. Wiz customers can submit requests for additional image support in the catalog today.
On the adoption side, we will soon add metrics to the Secured Image Catalog to enable customers to easily track image migration and vulnerability reduction impact from WizOS over time. We also plan to streamline custom image creation with a Custom Image Builder in Wiz that will enable users to select a base image, add desired packages from the Wiz package repository, and generate a script to build the image.
Create custom images in Wiz.
Get Started Today
WizOS is now generally available for Wiz customers. Ready to reduce vulnerabilities and start building on a secure foundation? First, navigate to the
Settings > WizOS
and enable it for your tenant. Then, check out the WizOS quickstart guide. If you previously enabled WizOS via the Preview & Migration Hub, you're all set.
If you’re not yet a Wiz user and want to learn more,
request a demo
today.
Tags
#
Product
#
Wiz Cloud