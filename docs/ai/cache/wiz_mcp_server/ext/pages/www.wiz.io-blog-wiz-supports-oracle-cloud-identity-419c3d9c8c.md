---
url: https://www.wiz.io/blog/wiz-supports-oracle-cloud-identity
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-22T08:00:00-05:00
extraction_mode: static_fetch
content_hash: a9500efce513
---

# Wiz Adds OCI IAM to Unified Cloud Identity Graph | Wiz Blog

Identity is the backbone of cloud security. It defines who can access what, and it’s often the difference between a secure environment and an open door. Until now, organizations running workloads in Oracle Cloud Infrastructure (
OCI
) lacked a way to see its unique IAM model side-by-side with AWS, Azure, and GCP.
Wiz now supports OCI IAM, giving customers visibility into OCI identities, permissions, and policies — all normalized into Wiz’s unified security graph.
Why It Matters
OCI introduces a distinct identity and access management model, with constructs like Identity Domains, Compartments, and natural-language policies. While powerful for operators, these differences have made it hard for security teams to consistently assess permissions, enforce guardrails, and reduce risk across clouds.
The result: OCI often became a blind spot in
multi-cloud
identity governance.
With Wiz, that blind spot disappears. We translate OCI’s IAM into the same model we already use for AWS, Azure, and GCP. Security teams can:
Detects excessive permissions and
toxic combinations
.
Analyze access consistently across all four major clouds.
Run unified controls and threat analysis without juggling cloud-specific tools.
What You Can Do With It
OCI IAM in Wiz unlocks new visibility and control for customers:
Complete visibility into OCI identities
See every user, group, and service principal, including the domains or compartments they belong to and the exact permissions they inherit.
Understand access paths and risks
Visualize how a user reaches a resource through groups, policies, and compartments. Easily spot overly broad groups or missing MFA.
Track keys and service accounts
Identify unrotated or unused OCI API keys and customer secret keys before they become hidden risks.
Ensure cross-cloud consistency
Because permissions are normalized, OCI entitlements appear alongside AWS, Azure, and GCP. You can finally answer critical questions like:
“Which identities have admin rights across all four clouds?”
How We Did It
Bringing OCI into Wiz required solving several unique challenges. Here’s how we made it simple for customers — without losing the depth of OCI’s IAM model:
Identity Domains → Wiz Organizations
OCI domains isolate users, groups, and apps. We map them into Wiz’s organization layer to preserve isolation while making them visible in context.
Compartments → Wiz Subscriptions
OCI resources live in nested compartments, which complicates permission evaluation. We flatten and analyze the full hierarchy so you see the true scope of access.
Policies Written in Natural Language → Structured Rules
OCI policies read like plain English (“Allow group Admins to manage all-resources in compartment Finance”). Wiz parses these into structured rules for consistent analysis across clouds.
Permissions Tied to Verbs → Wiz Access Types
OCI’s verbs (inspect, read, use, manage) bundle many actions. We normalize them into Wiz’s access categories (List, Read, Write, High Privilege, Admin), enabling toxic combo checks and threat analysis.
Resource Types → Wiz Objects
Buckets, instances, and other OCI services are mapped into Wiz objects, so you can compare them side-by-side with AWS, Azure, and GCP.
Concept
AWS
Azure
GCP
OCI
Root Account / Directory
Account
Tenant
Organization
Identity Domain
Hierarchy
Org Units
Management Groups
Folders/Projects
Compartments
Permissions
IAM Policies
RBAC
IAM Roles/Policies
Verbs (inspect/read/use/manage)
What’s Next
This launch is just the start. We’re continuing to expand our OCI coverage:
Dynamic Groups and federation support.
Deeper integration into Wiz’s cross-cloud policies.
Continued alignment of OCI features with AWS, Azure, and GCP.
With OCI support, Wiz gives you one identity model, one graph, and one place to see and secure access everywhere. OCI IAM is no longer a blind spot — it’s part of the same unified experience you already use for AWS, Azure, and GCP.
Tags
#
Wiz Cloud
#
Product & Company News
#
Security