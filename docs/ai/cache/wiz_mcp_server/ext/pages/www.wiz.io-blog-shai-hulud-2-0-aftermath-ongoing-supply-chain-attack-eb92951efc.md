---
url: https://www.wiz.io/blog/shai-hulud-2-0-aftermath-ongoing-supply-chain-attack
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-01T12:52:01-05:00
extraction_mode: static_fetch
content_hash: 6b29f3bfc211
---

# Shai-Hulud 2.0 Aftermath: Trends, Victimology and Impact | Wiz Blog

Wiz Research
and
Wiz CIRT
have been responding to the Shai-Hulud 2.0 incident (aka Sha1-Hulud) since news first broke on November 24, 2025. As of now we’re continuing to observe active spread, albeit at a significantly lower pace. This gives us an opportunity to step back and share what we’ve learned throughout  this incident, and reflect on the future.
This blog post assumes familiarity with the phases of Sha1-Hulud. For a detailed account of the initial incident, and our recommendations on response, refer to
our previous blog post
.
Infection Trends
Compared to previous supply chain worms like
s1ngularity
and
Shai-Hulud 1.0
, Shai-Hulud 2.0 has managed to stay active the longest. New repositories are still being created over 6 days later. The pace lowered down to tens of new repositories per day, but December 1st, 2025 marked a renewed infection spike with over 200 new repositories in just over 12 hours. It remains to be seen whether this spread pattern will continue, and how long a tail this worm will have.
One of the ways we can model trends is by using the
GHArchive
project, which offers historical data from the GitHub Events API, preserving information about now-deleted repositories and users. However, it can't be used for absolute numbers, as the loss rate under certain conditions can be up to 50%. As a result, our response paired the GitHub API with GHArchive, leaving us with one of the most comprehensive data sets on this incident.
GHArchive still remains useful to easily show the general trends such as pace of creation of new repositories:
Pace of the new public repositories
The dramatic drop across 11/24 reflects the containment activities by PostHog, Postman, AsyncAPI, and the npm team. Extracting from their respective reports:
PostHog
: "By 9:30 AM UTC, we had identified the malicious packages, deleted them, and revoked the tokens used to publish them"
Postman
: "11/24/25, 3:30am PT [11:30 UTC]: containment achieved (all infected versions unpublished)"
AsyncAPI
: "
11:46:00 UTC
— Action taken by the NPM security team to unpublish the malicious packages."
Pace of the new GitHub accounts
It is important to distinguish the new public repositories from the new GitHub users. When the malware is unable to find GitHub credentials locally, it will instead search for an existing repository from a prior victim. Then, it uses the credentials of that prior victim to upload an additional repository under the prior victim's account, with data from the new victim.  The search of these compromised accounts relies on an infamous
“Sha1-Hulud: The Second Coming.”
string, which serves as a
beacon for the exfiltration
.
The second graph shows the number of newly compromised GitHub accounts acting as
secret hosts / spreaders.
The actual amount of compromised instances is higher, and better reflected by the number of repositories created.
Beside the NPM ecosystem, AsyncAPI disclosed that the initial attack has managed to exfiltrate not only NPM token but also an OpenVSX API key. Moreover, there are confirmed
reports
of successful infections from the poisoned AsyncAPI IDE extension:
asyncapi-preview IDE extension
In addition, the Socket team
observed
the malicious Bun-based Shai Hulud v2 payload, which mirrored a compromised npm release, had spilled over into the Java/Maven ecosystem via the
org.mvnpm:posthog-node:4.18.1
package. PostHog and Maven Central confirmed the compromised releases in both npm and Maven due to the automated mirroring mechanism. However, we do not observe active spread of the worm in either the Maven or OpenVSX ecosystems.
Victimology
Most of the uploaded repositories contain an
environment.json
file that includes information on the system on which the malware ran, and the GitHub credential used to exfiltrate the data. Overall, from the corpus of compromised repositories, we managed to retrieve about 24,000 of these files, with about half of those being unique. We employed a basic fingerprinting algorithm to deduce the attributes of the compromised machine based on the variable values. Our numbers suggest that only 23% of the infections occurred on developer machines. Of the infected instances, the absolute majority are Linux machines:
Victim machine types
Victim Operating System distribution
The popularity of Linux is closely correlated to the fact that the majority of the runners are actually containers, supporting the value of attacker attempts to incorporate the container escape (as we reported in the previous blog):
Victim containerization type
Specifically on CI/CD runners, GitHub Actions is the leading platform with Jenkins, GitLab CI, and AWS CodeBuild coming distant second, third, and fourth:
Victim CI/CD platform distribution
Finally, we looked at the malicious package implicated, to gain insights into what packages were the primary vectors. Specifically, the environment variables
npm_package_name
and
npm_package_version
turned out to be most helpful. The distribution of the infecting packages is far from being uniform:
Infection packages
The dominant infection vector is the
@postman/tunnel-agent-0.6.7
package, with
@asyncapi/specs-6.8.3
identified as the second-most frequent. These two packages account for
over 60% of total infections
. This finding shows how mitigation efforts focused on these dependencies led to a profound and rapid reduction in the
Infection Trends
.
This ordering strongly correlates with package prevalence. Specifically,
@postman/tunnel-agent
and
@asyncapi/specs
are the first and third most common packages, directly linking their high prevalence with the scale of the resulting compromise.
Below are prevalence numbers, updated from what was previously shared in our last post:
Package prevalence
Finally, we looked at
npm_lifecycle_event
and
npm_lifecycle_script
variables to correlate the infection stage. As expected, 99% of all infection instances came from the
preinstall
event executing
node setup_bun.js
. Few instances that do not follow this pattern look to be testing attempts.
Leaked Secrets
Before we break down metrics around the leaked secrets, some related facts deserve special attention. First, exfiltration was conducted cross-victim, which indicates that victim data may have been published as a repository on an unaffiliated GitHub user.
This creates a substantial challenge for companies trying to determine if they were impacted, as they'd need access to the entire corpus of leaked data
.
Coverage of Sha1-Hulud emphasized the presence of cloud secrets theft. However, we have observed that the
cloud.json
file intended for this data is never actually populated. Our theory is that the attacker's lack of
try / catch
conditions and multi-cloud support led to a bug where API failure at any of the steps will fail the whole cloud secret extraction block:
let
cloudSecrets = {
aws
: {
secrets
:
await
awsHarvester.harvestSecrets() },
gcp
: {
secrets
:
await
gcpHarvester.listAndRetrieveAllSecrets() },
azure
: {
secrets
:
await
azureHarvester.listAndRetrieveAllSecrets() }
};
Finally, there is an incredible amount of duplication in the leaked data, for instance CI/CD runs might publish identical data across the exposure window. The attacker's use of Trufflehog means there are many unverified secrets in the data that are being used to drive FUD from some camps. That being said, we're still seeing, as a floor, thousands of critical secrets across hundreds of companies. Each of which is a potential onward attack waiting to happen.
Our data corpus consists of over 30,000 total repositories, of those about 70% with distinct contents.json, 50% with distinct truffleSecrets.json files (carrying results of local trufflehog scan), 80% with environment.json files (carrying values of environment variables), and about 400 distinct actionsSecrets.json (carrying workflow secrets).
Following are some of the numbers we observed from on this data:
contents.json
files are a source of (as expected) over 500 GitHub usernames and tokens - this correlates well with the numbers of total GitHub spreader accounts we reported in the sections above.
truffleSecrets.json
files are a source of up to 400,000 unique secrets (based on Raw values), however, since the malware did not use the
–only-verified
flag, only about 2.5% of those are verified. Of those, more than half are JWTs with a short expiration window (only 25 JWT are still valid as of 12/01).
While the secret data is extremely noisy and requires heavy deduplication efforts, it still contains hundreds of valid secrets including cloud, NPM tokens and VCS credentials. To date, these credentials pose an active risk of further supply chain attacks. For example, we observe that over 60% of leaked NPM tokens are still valid.
Updates from the Community
During a major incident like this, we track coverage across impacted companies, security vendors, and independent researchers. Beyond our own analysis and data, we want to highlight useful information that has been shared elsewhere about this incident.
Impacted Companies
PostHog’s
detailed postmortem
provides a “patient zero” perspective. At this point, it is confirmed that the initial access vector in this incident was abuse of
pull_request_target
via
PWN request
.
Postman have
shared an initial response
, including their containment timeline, and
root cause analysis
.
AsyncAPI have publsihed their own
postmortem
that includes the exclusive account on a parallel infection of their OpenVSX IDE
extension
.
Companies including
Trigger.dev
and
Zapier
, who were impacted via the malicious packages, have shared their learnings as well. Zapier’s writeup includes a strong set of controls other impacted companies can crib for mitigation and hardening going forward.
Notable security vendor blogs
Aikido Security’s
excellent analysis
; they were also first to publicize this incident broadly.
Datadog’s
well-written piece
incorporating trend analysis and advanced payload analysis with great visuals.
GitGuardian’s initial
secrets focused analysis
and view into the attacker’s testing activities.
A New Normal for Supply Chain Security?
It has been a year since the Ultralytics attack, but confusion about GitHub Actions security is still palpable. There is a clear message in the series of attacks culminating in Sha1-Hulud: attackers are perfecting credential harvesting operations using the npm ecosystem and GitHub. Given the attackers' increasing sophistication and success so far, we predict continued attacks, both using similar TTPs and leveraging the credential trove harvested to date.
Need help responding to Sha1-Hulud?
Connect with the Wiz Incident Response team for assistance
.
References
Aikido Blogpost
AsyncAPI postmortem analysis
Datadog blogpost
GitGuardian blogpost
PostHog's postmortem analysis
Socket blogpost
Trigger.dev postmortem analysis
Wiz Shai-Hulud 2.0 blogpost
Wiz Shai-Hulud 1.0 blogpost
Wiz IOCs
Tags
#
Research
#
Security
#
Threat Intel