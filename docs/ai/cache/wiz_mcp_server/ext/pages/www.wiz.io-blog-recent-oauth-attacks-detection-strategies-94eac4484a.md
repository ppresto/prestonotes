---
url: https://www.wiz.io/blog/recent-oauth-attacks-detection-strategies
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-11-27T11:27:41-05:00
extraction_mode: static_fetch
content_hash: a540fc4720d8
---

# 3 Recent OAuth TTPs + How to Detect Them with Entra ID Logs | Wiz Blog

Attackers don’t just hack in - they log in. Compromised credentials remain the most common path to breach, but as organizations strengthen authentication with MFA and Conditional Access, attackers have adapted, finding new ways to abuse these same mechanisms. The result is a steady evolution of identity-based attack techniques that blur the line between legitimate and malicious access.
Specifically, in this post we’ll expose how adversaries abuse OAuth flows to gain initial access and maintain persistence in Azure environments, and how defenders can uncover these behaviors by analyzing sign-in activity. Drawing from Wiz telemetry, we’ll highlight how widespread these attack patterns are in real-world environments.
At the end of this post, you’ll find an appendix containing ready-to-use KQL queries that help surface suspicious authentication activity directly from your own logs.
Oauth - quick recap:
OAuth is the protocol behind modern authentication and authorization, the system that lets apps securely request access on your behalf. In this post, we’ll focus on the authentication side.
At its core, OAuth issues JWTs called access tokens that link a specific application to a resource, defining exactly what that token can do. The different OAuth flows determine how those tokens are obtained and which credentials are exchanged, and understanding these differences not only helps spot attacks like MFA bypass but also reveals why some flows are far more attractive to attackers than others.
In Azure, there are three main types of tokens generated through OAuth:
Refresh Token
,
Primary Refresh (PRT),
and the focus of our blog post -
Access Token.
An Azure Access Token grants scoped permissions to a specific resource and application. Let’s make this concrete with an example.
When signing in to the
Azure Portal
and navigating to the
Users
tab in Entra, the application (Azure Portal) requests an access token for the
Microsoft Graph API
, since that’s the backend service providing user data (
graph.microsoft.com/users)
.
A GET request to the “Users” tab in Azure portal
Azure’s token response contains a JWT whose claims reveal what’s happening:
Together, they define the OAuth relationship:
App + User + Resource → Token (with scope).
Entra ID sign-in logs capture this relationship too, mirroring key fields from the JWT.
Fields from the JWT token are mapped to the sign in logs
Additional fields like
authenticationProtocol
or
originalTransferMethod
, which are not part of JWT, can hint at which OAuth flow was used, and
clientAppUsed
can reveal legacy clients or specific app types.
Understanding how these JWT claims map to Entra logs is key for detecting misuse, especially when certain app–resource–scope combinations are abused.
Having mapped out how a legitimate OAuth flow looks in Entra ID logs, it’s time to see how that picture changes when an attacker enters the scene.
First Attack: Device Code phishing
Statistics for device code phishing in the wild
This attack focuses on abusing the device code authentication flow, but before diving into how the attack works, it’s important to understand
why it matters
.
Even more concerning, Wiz telemetry shows that fewer than 50% customers enforce Conditional Access (CA) policies that block device code authentication, resulting in only
0.3%
of all device code auth attempts are actually stopped by a “Block” CA rule.
Protocol Overview
The device code flow is an OAuth flow for devices that can’t easily handle browser-based sign-in (smart TVs, printers, or IoT gadgets).
If you’ve ever typed a short code into Netflix to link your new TV, you’ve already used it.
Device code Oauth flow taken from Microsoft's official documentation
The critical security detail, and what makes this attractive to attackers, is that authentication happens on a separate browser/device while the resulting token is returned to whatever client originally requested the code.
The phishing scenario
In device-code phishing the attacker generates a device code, lures a victim to enter it in their browser (phishing), and waits. The victim authenticates normally, sometimes including MFA, but the issued token is delivered to the attacker’s device. The attack is especially convincing because the phishing message often contains a link that points to a Microsoft domain, which lends apparent legitimacy and reduces the victim’s suspicion.
Because the token can include amr (Authentication Methods Reference) claims like
["mfa"]
, defenses that only check for an MFA flag can be bypassed: logs will show an MFA-authenticated session even though the user was socially engineered.
This technique has been observed in the wild -
Storm-2372 device-phishing campaign.
Second attack: Resource Owner Password Credentials (ROPC)
This technique centers on abusing the legacy ROPC authentication flow. Before we get into why this protocol is so attractive to attackers, let’s look at what our telemetry shows.
Wiz data indicates that fewer than 45% of customers enforce Conditional Access (CA) policies that require MFA, which results in failed ROPC authentication, meaning this flow remains widely exposed. As a result, only 0.2% of all ROPC authentication attempts are actually stopped by a “Block” CA rule.
The lack of CA policies is made worse by the following fact:
Protocol Overview
The Resource Owner Password Credentials (ROPC) flow is a legacy OAuth mechanism that exchanges a username and password directly for a token. It skips modern safeguards,
no redirects, no browser consent, and no MFA.
This makes it a favorite for attackers.
Furthermore, ROPC remains accepted by several Microsoft first-party apps that exist in every tenant, even though it’s officially legacy.
Combining these two, and you get an authentication flow ideal for credential-stuffing and brute-force attempts. Error codes (like
50126
for incorrect passwords) often reveal authentication outcomes, MFA prompts, or Conditional Access failures, data that attackers can use to tune their campaigns.
ROPC OAuth flow taken from Microsoft's official documentation
ROPC is not only attractive for automated bots - it's also extremely effective for hands-on-keyboard attackers, wishing to gain persistence and privilege escalation. The real danger isn’t just the use of ROPC, but the
app and resource combination
being targeted. Certain pairs can do more than bypass MFA, they can allow device registration, privilege escalation, or persistence.
Projects like
Entra Scopes
by Dirk-jan Mollema and Fabian Bader show which apps and scopes can be chained for extended access. For example, combining
Azure AD PowerShell
with
Microsoft Graph
can yield significant privileges.
ROPC attack seen by Wiz
Wiz has recently detected a surge in ROPC (Resource Owner Password Credentials) attacks targeting customers across various environments. These campaigns frequently leveraged Azure Active Directory PowerShell applications and attempted access through Azure Resource Manager or Microsoft Graph. The activity commonly used generic user agents such as
Mozilla/5.0
, alongside traffic appearing to originate from infrastructure associated with vendors like Internet Utilities Europe and Asia Limited, LATITUDE-SH, ASMedi, DATAWAGON, and others. While many of the attempts resulted in authentication failures, there were occasional successful token exchanges, highlighting the ongoing risk and sophistication of these brute-force style campaigns.
Third Attack: From access to persistence - registering a device
Attack Overview
Obtaining an access token through device-code phishing or ROPC can be valuable on its own; however, in many organizations the resulting token is blocked by widely adopted Conditional Access policies requiring a registered or joined device for authentication. As a result, even a successfully acquired token may be insufficient to gain access.
There are specific application-and-resource combinations that are permitted by Conditional Access, even without a previously registered device. Paradoxically, one of these combinations enables the registration of a device: an access token issued for the
Microsoft Authentication Broker
application and the
Intune Enrollment
resource can be used to authenticate and initiate the device join process.
This approach enables an attacker to leverage the token to bypass the Conditional Access restriction, register a device, and establish persistence. Once the device is registered, the attacker obtains a
Primary Refresh Token (PRT)
, valid for up to
90 days
, allowing continued access within the organization despite existing security controls.
Sometimes, registering a device is not enough, as there are higher assurance-level Conditional Access controls. To deal with this, attackers often push further to configure WHfB (Windows Hello For Business) on the registered device. WHfB issues TPM-backed, cryptographic credentials that Entra recognizes as a
strong, phishing-resistant, passwordless authentication method
, satisfying higher assurance-level conditional access policies. This makes WHfB extremely valuable to an adversary:
device registration unlocks persistence, but WHfB unlocks the ability to bypass stricter authentication-strength requirements
.
This method was first documented by
Dirk-jan’s research
.
Although ROPC can sometimes provide device-registration permissions, WHfB setup generally requires an MFA-capable token, something ROPC cannot deliver. However, the device-code phishing flow
can
, as it returns MFA-based
amr
claims (e.g.,
["mfa"]
) once the victim completes interactive authentication.
Real-world tooling such as
RoadTx
automates the full sequence: generating a device code, phishing a victim to complete login, exchanging tokens for enrollment permissions, registering the device, and finally provisioning WHfB, all enabled by a single successful social-engineering event.
Entra sign-in log example - ROPC for device registration token
How Wiz Can Help
Wiz Defend provides deep visibility into identity-based attack activity in Entra ID, with real-time detections built to identify the techniques used in device-code phishing, ROPC abuse, and Conditional Access evasion. Rather than focusing only on the final stages of a compromise, such as successful device registration or WHfB provisioning, Wiz surfaces the subtle early signals that indicate an attacker is attempting to gain persistence.
Wiz Defend includes dedicated detection rules that alert on these behaviors:
Unusual Device Code Flow Detected
Sign-in by Entra ID User using ROPC protocol to unusual application and resource
Suspicious ROPC authentication for conditional access policy bypass
Suspicious device registration attempt
These detections analyze authentication context, application/resource pairings, token properties, and device enrollment telemetry to spot activity that deviates from typical tenant behavior. By connecting these signals across identity flows, Wiz helps security teams identify attacker movement
before
a trusted device is established or stronger passwordless authentication methods are configured.
With this early visibility, security teams gain time to contain an attack, resetting credentials, blocking malicious apps, and stopping enrollment activity, before the adversary achieves durable, high-assurance access.
Detections
If you’re planning to roll out your own detection logic, don’t worry - we’ve got you covered.
Attack #1: Device code phishing
This flow usually produces three related sign-in events (all sharing the same Session ID):
2 interactive events — the victim’s browser authentication(s).
1 non-interactive event — the attacker’s client polling/token retrieval.
There is a unique and obvious pattern here: 3 events with the same session ID, with the deviceCodeFlow transferMethod, but with inconsistencies across Locations and UserAgent.
union AADNonInteractiveUserSignInLogs, SigninLogs
| where originalTransferMethod ==
"deviceCodeFlow"
and clientAppUsed ==
"Mobile Apps and Desktop clients"
and [
'status
'][
'errorCode
'] in (
"0"
,
"50199"
)
and isnotempty(
userId
)
and isnotempty(
ipAddress
)
and isnotempty(
location
[
'countryOrRegion
'])
and isnotempty(
userAgent
)
and isnotempty(
sessionId
)
| summarize
set_status_errorCode = make_set([
'status
'][
'errorCode
']),
set_userAgent = make_set(
userAgent
),
set_location_countryOrRegion = make_set(
location
[
'countryOrRegion
']),
max_createdDateTime = max(
createdDateTime
)
by sessionId, userId, userPrincipalName, ipAddress
| where array_length(
set_status_errorCode
) ==
2
and (
array_length
(
set_userAgent
) ==
2
or array_length(
set_location_countryOrRegion
) ==
2
)
The
mixed user agents
(browser + script) in the same session, along with
geolocation mismatches
, make this kind of activity stand out once you know what to look for.
Across all device code authentications,
approximately 1%
exhibit anomalous characteristics, for example, authentications involving
multiple user agents
or
multiple geographic locations
.
Within this subset, authentications that involve
both multiple user agents and multiple countries
are particularly noteworthy:
43%
of these include a
“scripty” user agent
, a pattern that suggests
potentially malicious activity
rather than normal user behavior.
Attack #2: MFA bypass using ROPC
ROPC authentication can be detected using the “authenticationProtocol” field.
Any anomaly with ROPC should be monitored, such as:
Anomalous Location
Anomalous User Agent
Anomalous application and resource
Wiz observed these application and resource combination abuses using ROPC in the last month:
Attack #3: Brute Force using ROPC
When ROPC is used for brute force, the failed attempts (error code 50126) won’t display the protocol in logs. Successful attempts, however, will include the
authenticationProtocol == "ropc"
field, allowing detection through correlation and pattern analysis.
Here’s a KQL example for identifying successful ROPC brute-force attempts:
let
failed_attempts
=
union AADNonInteractiveUserSignInLogs, SigninLogs
| where status
["errorCode"]
== "50126"
and isnotempty(userId)
and tostring(authenticationDetails
["authenticationMethodDetail"]
) == "Password in the cloud"
and
clientAppUsed
==
"Mobile Apps and Desktop clients"
| summarize
min_createdDateTime
= min(createdDateTime),
max_createdDateTime
= max(createdDateTime),
attempt_count
= count()
by bin(createdDateTime, 1d), userId, ipAddress, resourceDisplayName, appDisplayName
| where attempt_count > 15
| extend
time_diff
= datetime_diff(
"hour"
, max_createdDateTime, min_createdDateTime)
| where time_diff < 3 and time_diff > -1
;
union AADNonInteractiveUserSignInLogs, SigninLogs
| where status
["errorCode"]
== "0"
and isnotempty(userId)
and
authenticationProtocol
==
"ropc"
| join
kind
=inner failed_attempts
on
userId, appDisplayName, resourceDisplayName
| extend
time_diff_success
= datetime_diff(
"hour"
, createdDateTime, max_createdDateTime)
| where time_diff_success < 3 and time_diff_success > -1
Attack #4: device registration after ROPC
The following cleaned-up KQL joins ROPC sign-ins to successful device registrations, surfacing registrations that occur soon after an ROPC event (within two days). A short time difference is a strong indicator of abuse:
let
device_reg_ropc
=
union AADNonInteractiveUserSignInLogs, SigninLogs
| where isnotempty(userId)
and status
["errorCode"]
== "0"
and
AuthenticationProtocol
==
"ropc"
and
appId
==
"29d9ed98-a469-4536-ade2-f981bc1d605e"
and
resourceId
==
"d4ebce55-015a-49b5-a083-c84d1797ae8c"
| project
ropc_time
= createdDateTime, userId
;
AuditLogs
| where
result
==
"success"
and
activityDisplayName
==
"Register device"
and isnotempty(initiatedBy
["user"]
["id"]
)
| extend
userId
= tostring(initiatedBy[
"user"
][
"id"
])
| join
kind
=inner device_reg_ropc
on
userId
| extend
time_diff_days
= datetime_diff(
"day"
, createdDateTime, ropc_time)
| where time_diff_days between (0 .. 2)
| project userId, ropc_time, createdDateTime, time_diff_days, activityDisplayName
Attack #5: WHfB registration after suspicious device code
The following cleaned-up KQL joins suspicious device code sign-ins to successful device registrations, surfacing  WHfB registrations that occur soon after the device code authentication event (within the same day). Ending with a test for IP mismatch, since in the Device Code authentication event we will see the victims IP, the WHfB registration event will contain the attackers IP.
let device_code =
union AADNonInteractiveUserSignInLogs, SigninLogs
| where originalTransferMethod ==
"deviceCodeFlow"
and clientAppUsed ==
"Mobile Apps and Desktop clients"
and [
'status
'][
'errorCode
'] in (
"0"
,
"50199"
)
and isnotempty(
userId
)
and isnotempty(
ipAddress
)
and isnotempty(
location
[
"countryOrRegion"
])
and isnotempty(
userAgent
)
and isnotempty(
sessionId
)
| summarize
set_status_errorCode = make_set([
'status
'][
'errorCode
']),
set_userAgent = make_set(
userAgent
),
set_location_countryOrRegion = make_set(
location
[
"countryOrRegion"
]),
max_createdDateTime = max(
createdDateTime
)
by sessionId, userId, userPrincipalName, device_code_ip = ipAddress
| where array_length(
set_status_errorCode
) ==
2
and (
array_length
(
set_userAgent
) ==
2
or array_length(
set_location_countryOrRegion
) ==
2
)
;
AuditLogs
| where result ==
"success"
and activityDisplayName ==
"Add Windows Hello for Business credential"
and isnotempty(
initiatedBy
[
"user"
][
"id"
])
| extend userId = tostring(
initiatedBy
[
"user"
][
"id"
])
| join kind=inner device_code on userId
| extend time_diff_days = datetime_diff(
"day"
, createdDateTime, max_createdDateTime)
| where time_diff_days <
1
and ipAddress != device_code_ip
| project userId, createdDateTime, max_createdDateTime, time_diff_days, device_code_ip, ipAddress, activityDisplayName
Wrapping up
Device Code Phishing and ROPC aren’t exotic zero-days - they’re abuses of legitimate authentication flows. That’s what makes them so dangerous. A single overlooked clue, a quiet ROPC field, an odd session correlation, an unexpected device registration, can mark the line between a blocked attempt and full enterprise compromise.
Don’t wait for a breach report to reveal what your logs already know. Restrict ROPC use by requiring MFA and applying Conditional Access to only allow compliant devices, and turn the KQL detections in this post into live, automated defenses. Your sign-in logs are already telling the story, make sure your
SOC
is listening.
Tags
#
Research
#
Security