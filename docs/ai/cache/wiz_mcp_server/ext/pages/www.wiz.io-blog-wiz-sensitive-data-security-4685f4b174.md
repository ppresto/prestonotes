---
url: https://www.wiz.io/blog/wiz-sensitive-data-security
source_name: blog_datasecurity
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-04-22T12:01:14-04:00
extraction_mode: static_fetch
content_hash: aff365540cf8
---

# Wiz Data Security: Where is My Data and Who Can Access It?  | Wiz Blog

Cloud data security starts with a deceptively simple question:
Where is my sensitive data, and who has access to it?
For most teams, answering that isn’t straightforward. Data is sprawled across cloud accounts, services, and environments. Access is often indirect, inherited, or forgotten. And traditional tools rarely show both the data and the access context in one place.
This blog kicks off the
Wiz Data Foundations
series—an overview into how Wiz helps organizations discover, classify, and act on data risks in the cloud. In this first post, we’ll focus on the
visibility
layer:
Surfacing where your sensitive data lives
Understanding how it’s exposed
And identifying
who can access it
We’ll cover classification and response in upcoming parts.
Visibility Starts with Context
Before diving into access, it’s helpful to understand how Wiz surfaces data security insights in the first place. Wiz performs an
agentless
scan across your environment across all
supported data services
. Sensitive data detection and classification is built into the platform and available out-of-the-box.
Data insights are surfaced through:
Findings
– raw, granular detections (e.g. a file with PII )
Issues
– correlated risks that include context (e.g. sensitive data + public exposure + no encryption)
Introducing the Data Stores Treemap: A New Way to See Where Your Sensitive Data Lives
Start with the big picture: The new
Data Stores Treemap
gives you a visual breakdown of where sensitive data lives across your environment. It’s grouped by resource type, environment, and sensitivity level—helping you spot trends and outliers instantly.
✅
Example: See how much sensitive data is stored in S3 buckets across production vs dev environments.
This is just one way Wiz helps teams understand the landscape before zooming in.
Who Has Access to My Sensitive Data?
Once you know
where
the data is, the next question is
who can get to it?
Wiz provides multiple workflows, depending on your goal:
Option 1: Start with a Specific Data Store
If you’re looking at a particular resource—like an S3 bucket—you can view all identities with access from the
Datastore page
.
✅
Click into a datastore → Identity tab → See access level, path (direct, inherited), and whether the access is risky.
Use this when you’re focused on a critical asset and want to audit its exposure.
Identify access for a specific datastore
Option 2: Explore Access Entitlements by Identity
If you want to understand access patterns across users, head to the
Identity Entitlements
view.
Filter by identity type (e.g., human vs machine)
Sort by access level (read/write/admin)
See how access was granted (policy, trust relationship, etc.)
Filter down further (e.g., identities without MFA that have write access to sensitive resources)
✅
Great for answering questions like: “Who can write to sensitive storage and how did they get that access?”
Option 3: Investigate a Specific Identity
If you’re interested in a particular user or service account, start from their
Identity Profile
page. You’ll see a full list of resources they can access, including those with sensitive data.
✅
From here, explore access relationships, filter by sensitivity, or see if access spans environments or accounts.
You can also ask custom questions right on this page.
Want to know if a specific role has write access to unencrypted databases? Write your own query inline and go.
Option 4: Dive into the Security Graph (When You Need to Go Deep)
The
Security Graph
gives you ultimate flexibility. Ask a question—any question—and build a path-based query to explore relationships across data, identity, exposure, and risk.
✅
Example: “Show me identities with transitive access to sensitive data via a public-facing role.”
It’s powerful but designed for targeted exploration when you need full control.
Bonus: Dashboards and Insights
Surface org-wide trends, coverage metrics, and top data risks directly in Wiz
dashboards.
It’s an easy way to track high-level KPIs or share with leadership. You can quickly view publicly accessible resources, data related issues, identity insights and more on the data dashboard.
Looking ahead
With agentless scanning and prebuilt insights, Wiz gives you a full picture of your sensitive data exposure—what exists, where it lives, and who can get to it. You can start from data, identity, or relationships—and explore as broadly or as deeply as needed. We're continuously innovating to ensure Wiz customers can answer critical data security questions—quickly, intuitively, and in the way that works best for them.
In upcoming posts, we’ll go deeper into how Wiz classifies sensitive data and how teams can take action using the Wiz 5R framework. Stay tuned—or check back soon to explore the full series.
See Wiz in action
Discover how Wiz DSPM helps you secure your critical data . You can request a personalized demo to address your  specific requirements.
Get a Demo
Tags
#
Wiz Cloud
#
Security
#
Compliance
#
Data Security