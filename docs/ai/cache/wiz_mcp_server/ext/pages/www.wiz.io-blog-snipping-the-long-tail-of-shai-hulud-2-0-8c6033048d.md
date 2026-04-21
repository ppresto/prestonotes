---
url: https://www.wiz.io/blog/snipping-the-long-tail-of-shai-hulud-2-0
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-30T10:21:30-05:00
extraction_mode: static_fetch
content_hash: 0a7de24db66b
---

# Snipping the Long Tail of Shai-Hulud 2.0 | Wiz Blog

Since the discovery of
Shai-Hulud 2.0
(aka sha1-hulud), Wiz Research has tracked a persistent "long tail" of infections. To date,
this incident has impacted over ⅓ of the Fortune 100
, among hundreds of other organizations.
While primary containment occurred in late November, the worm lingered in environments for weeks due to overlooked supply chain dependencies. Building on our previous reports on the
initial incident
and
victimology
, this update details:
Persistence Mechanics
: How private registries and IDE extensions kept the worm alive.
“Snipping the Tail"
: How Wiz Research helped mitigate the worm’s persistence.
Unrotated
Secrets
: A status report on the leaked credentials that remain valid today.
The Trust Wallet Link
: Analyzing a $7M exploit’s potential connection to sha1-hulud.
The Shape of the Long Tail
At the peak of the sha1-hulud outbreak on November 24th, GHArchive recorded
13,686 new repositories
containing exfiltrated victim data. GHArchive generally captures 50% of GitHub activity, matching Wiz’s capture of over twenty-five thousand repositories in the first day of the incident. While aggressive containment by the npm team and ecosystem partners
triggered an immediate crash
in new infections, the worm did not disappear.
Instead, we entered a month-long "long tail" period. From November 25th to December 24th, the infection rate stabilized at a persistent level of approximately
100-200 new compromised repositories every day
.
On December 24th, Wiz Research moved to "snip the tail." By coordinating with the AsyncAPI team to publish a clean version (v1.1.0) of their OpenVSX extension, we forced an update across the IDE ecosystem. The impact was immediate: by December 29th, daily new repositories plummeted to just
a handful
.
Daily pace of new public repositories (log scale)
Why the Worm Lingered
Our analysis identifies two primary drivers for this persistence, even after the malicious packages were purged from the public npm registry:
Private Registries & Cached Packages (5% of cases):
Internal mirrors and local caches continued serving "poisoned" versions that had already been revoked upstream.
The OpenVSX "Zombie" Extension (90%+ of cases):
The malicious
asyncapi-preview v1.0.1
extension remained active on developer machines because no higher version existed to trigger an automatic update … until our intervention on Dec 24th.
The Double-Edged Sword of Private Registries & Cached Packages
Roughly 5% of infections in the long tail were traceable to Private Registries & cached packages.
Private registries (e.g., Sonatype Nexus, JFrog Artifactory) are a common security recommendation for governing third-party code. However, they introduce upstream
desynchronization risk
. In this campaign, some private registries failed to purge the malicious sha1-hulud packages after they were revoked from the official npm registry. As a result, these registries continued to serve "poisoned" packages to internal developers for weeks after the public threat was neutralized.
Persistence via Local Cache
We also identified instances where the malware persisted through the local npm cache. While the npm CLI typically validates versions against the registry, specific configurations bypass this check:
--offline
: Forces npm to use the local cache exclusively.
--prefer-offline
: Prioritizes the local cache, only hitting the registry if a package is missing.
In high-velocity CI/CD environments where these flags are a common performance enhancement, the "removal" of a package from the public registry is irrelevant if a malicious copy is already pinned in the local build environment.
OpenVSX asyncapi-preview (v1.0.1)
Over 90% of long-tail infections originated from a single source: the
malicious asyncapi-preview v1.0.1 extension
. Despite being pulled from the OpenVSX Registry on November 26th, the extension remained active on developer machines.
Our analysis found a recurring indicator in victim exfiltration logs:
"_PACOTE_NO_PREPARE_": "git+ssh://git@github.com/asyncapi/cli.git#2efa4dff59bc3d3cecdf897ccf178f99b115d63d"
This commit hash points
directly to the malicious fork
used in the original Shai-Hulud attack. The persistence mechanism was simple: because the registry "rolled back" to v1.0.0, IDEs saw no reason to update or overwrite the installed (malicious) v1.0.1.
On December 23rd, Wiz Research reported this issue to the AsyncAPI security contact. On December 24th, the AsyncAPI team published a clean version 1.1.0 of the extension to the OpenVSX registry. IDEs with the malicious version installed automatically updated to the clean version, which has removed the majority of outstanding infections.
Unremediated Secrets
One month post-incident, the cleanup is far from complete. While platform-specific tokens (npm/GitHub) have seen aggressive revocation, critical infrastructure and AI credentials remain exposed.
Wiz Research Dataset Scope
: Our analysis covers
>29,000 leaked repositories and >12,000 unique compromised machines
, representing almost the entire victim population.
As of December 28th, our telemetry on the "unrotated" landscape reveals dangerous remnants:
Credential Type
Revocation Rate
Status / Outstanding Risk
GitHub Tokens
>95%
Dozens remain valid.
npm Tokens
>90%
Roughly a dozen remain valid.
Cloud Credentials
~50%
Hundreds of long-lived keys remain valid.
AI API Keys
Low
>200 valid keys (OpenAI, Gemini).
SaaS/Dev Tools
Low
Dozens of valid keys (Slack, Cloudflare, Airtable).
The Trust Wallet Incident, a High-Stakes Case Study
On December 25th, Trust Wallet
reported $7 million in thefts
resulting from a malicious update (
v2.68
) to their browser extension. Trust Wallet is continuing their investigation, and has stated they will cover user losses.
While the investigation is ongoing, Wiz Research has identified indicators suggesting this breach may be a direct downstream consequence of the sha1-hulud incident.
Update 12/30 16:10 UTC:
Shortly after publication of this blog post, Trust Wallet
released an initial post-mortem
, stating "we have high confidence that the Browser Extension v2.68 incident is likely related to the industry-wide Sha1-Hulud incident in November"
The most compelling evidence lies in the specific secrets exfiltrated during the Shai-Hulud campaign. Our dataset confirms that Trust Wallet was a victim, and among other data, the following credentials leaked:
GitHub Token
: A valid token with
admin:enterprise
scope over the
trustwallet
GitHub organization.
Web Store Credentials
: A Chrome Web Store Client ID, Client Secret, and refresh token exfiltrated from GitHub Action secrets.
The leak of these two assets provides multiple viable paths to hijacking the browser extension's distribution pipeline.
Thematic and Temporal Alignment
There are additional indications of a potential connection within the naming and timing of the attack.
Naming Conventions:
The domain used in the Trust Wallet exploit followed the specific
Dune
mythology naming convention established by the Shai-Hulud threat actor.
A Dune reference on the domain used for exfiltration.
Timeline:
The malicious domain was
registered on December 8th
, aligned with the sha1-hulud attack transitioning into targeted exploitation of harvested secrets.
While
circumstantial
until the post-mortem is released, the overlap between the exfiltrated secrets and the nature of the Trust Wallet exploit is significant. It serves as a stark reminder: In supply chain attacks,
exfiltrated secrets present an ongoing threat
, regardless of when the initial worm is contained.
Recommendations
The persistence of sha1-hulud proves that "removal from registry" is not the "end of the incident." To prevent "zombie" malware from lingering, we recommend the following structural shifts:
1. Own Your Private Registry Governance
Using a private registry (i.e Artifactory, Nexus) shifts responsibility for security hygiene from the public registry (npm) to your organization.
Sync Revocations
: Ensure your registry mirrors are configured to cross-reference upstream metadata frequently. If a package is "unpublished" or "revoked" on npm, your internal mirror should reflect that status immediately. Unfortunately, this often requires custom automation.
Audit "Pull-Through" Caches
: Periodically scan internal caches for packages that no longer exist in public repositories, as this is a leading indicator of a risky or malicious package.
2. Neutralize the Cache
CI/CD performance optimizations like
--prefer-offline
can become security liabilities.
Build Hygiene
: In high-stakes production builds, avoid using local caches that skip registry validation.
Dependency Cooldowns
: When caching packages, the tradeoff favors
dependency cooldowns
even further.
Force Updates
: If a supply chain incident is suspected, force a clean build by clearing local npm/yarn/pnpm caches across your build fleet.
3. Comprehensive Secret Rotation
The Shai-Hulud dataset shows that organizations (and platforms) were quick to rotate VCS tokens but slow to rotate the broader set of leaked keys.
Assess all leaks for criticality
. A leaked Chrome Web Store secret can be just as devastating as a leaked AWS key. Triage and remediate in order of risk.
4. Beware Orphaned Malicious Versions
As demonstrated by our work with AsyncAPI, a forced version bump can be necessary to remove installed malicious packages. If you are a maintainer, always publish a clean, higher-versioned update to trigger the auto-update mechanisms in IDEs and developer environments.
Tags
#
Research
#
Security
#
Threat Intel