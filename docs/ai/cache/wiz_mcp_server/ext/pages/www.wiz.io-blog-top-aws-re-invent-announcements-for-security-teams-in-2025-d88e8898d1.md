---
url: https://www.wiz.io/blog/top-aws-re-invent-announcements-for-security-teams-in-2025
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-08T16:54:29-05:00
extraction_mode: static_fetch
content_hash: 114f05d0eaa6
---

# Top AWS re:Invent Announcements for Security Teams in 2025 | Wiz Blog

AWS’s largest event of the year is re:Invent, which occurred just after Thanksgiving from Dec 2-5 this year.  The weeks prior are referred to as “pre:Invent” where more than double the normal number of announcements happens and then during the conference further announcements are made.  In this post I've selected my favorite announcements of the past 3 weeks.
Top security announcements
AWS login
The new
aws login
command allows you to get credentials into a CLI (or other applications) by using your browser session.  This type of functionality had existed previously for AWS Identity Center users, using
aws sso login
, or through various open-source tools, such as Nike’s
gimme-aws-creds
, but this can now be used for all sorts of account access scenarios and without the previous configuration complications.
Link
Interestingly, when I looked at how this was being implemented, I noticed functionality that was added to the AWS SDK
earlier this year
that records in the user-agent how credentials are acquired.  So you can see in your CloudTrail logs whether an application is using credentials acquired from
this
, the IMDS, or somewhere else.
IAM Outbound Identity Federation
This allows you to authenticate to non-AWS services using your AWS principals. Previously, this was often done with a
pre-signed request
for sts get-caller-identity, which was an awkward use of that ability.  This can now be accomplished in a more generic and purpose-built way using JWT.
Link
One unexpected benefit of this feature is that the JWT includes information about the AWS Org ID, OU path, and principal tags for the principal.
Flat-rate pricing plans with no overages
This one isn’t quite as exciting to enterprises as it is to individuals, as my main interest here is finally being able to get rid of the small monthly charges from hosting a static site on AWS and not have to worry about a spike in my bill if that site gets unexpected attention.  This new feature is limited to the services related to a static website and in addition to some paid tiers, it also offers a free tier with 5GB of S3 storage, WAF access, and other benefits, for a free way to host static sites on AWS.
Link
Transfer accounts to a different org
The need for this next capability is rare for most companies as it usually only happens during mergers and acquisitions, but this has historically been a frustrating experience when it is needed. If you needed to move one or more accounts from one AWS Organization to another, previously you needed to detach those accounts so they would be stand-alone accounts, and then invite them to the new organization.  This meant setting up billing information for the accounts just for a few minutes of isolation, no longer having them protected via SCPs, and no longer having an organization CloudTrail log.  Now you can finally just move them from one Organization to another without making them stand-alone.  Moving AWS accounts between Orgs will still be painful as others have
documented
, but at least one frustrating part is easier.
Link
Other honorable mentions
IAM Policy Autopilot
This new tool generates IAM policies for applications, and in opposition to the way others have attempted to solve this problem recently, AWS is using deterministic analysis (meaning they are not using an LLM).
Link
IAM temporary delegation
This one is not immediately exciting as it is limited to “customer onboarding for ISV Accelerate Partners”, but this IAM temporary delegation looks like it is laying the foundation for teams to do
JIT privileged cloud access
.
Link
Org level S3 Block Public Access
This quality of life improvement adds the account level setting to now being at the org level.
Link
TLS proxy
For those that do TLS inspection, AWS now provides a proxy service for this.
Link
re:Inforce being merged into re:Invent
This was not announced through the usual means, but an update was made to the re:Inforce
FAQ
for when the next re:Inforce would be. Since 2019, re:Inforce has been AWS’s large conference focused on security, but with security also being an important part of re:Invent, they’ve decided to merge them.
Tags
#
Research
#
Security