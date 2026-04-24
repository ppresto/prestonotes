---
url: https://www.wiz.io/blog/validated-external-risk-issues-zero-day-soc-alerts
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-30T07:49:21-05:00
extraction_mode: static_fetch
content_hash: fdaad69bf612
---

# Validated External Risk Issues: SOC Alerts for Zero-Days | Wiz Blog

The ultimate goal of modern security is simple: removing exploitable risk before attackers can find and weaponize it. High-profile threats continually prove the importance of quickly detecting if you are exploitable to risk so you can remove it and ensure you are protected in the face of zero-day vulnerabilities.
To help cloud security and SOC teams bridge this gap, we’ve introduced
Validated External Risk Issues-
SOC-level alerts that indicate an attack path has been verified by Wiz’s agentless Attack Surface Scanner to be exploitable from the outside-in. This proactive alert represents a clear and open door for attackers and should be treated as a threat- demanding immediate SOC attention to remove the risk before an incident unfolds.
Addressing React2Shell with Validated External Risk Issues
The
recent disclosure
of a critical unauthenticated Remote Code Execution (RCE) vulnerability affecting React and Next.js applications- dubbed React2Shell- serves as a prime example of how teams can leverage these ASM findings and External Validated Risk Issues to stay ahead of high-profile threats by cutting through noise, focusing on true exploitable risk, and responding before the threat becomes an incident.
The critical RCE vulnerability, tracked as CVE-2025-55182/CVE-2025-66478 allows attackers to execute arbitrary commands by exploiting improper deserialization, posing a risk of full server compromise with a single HTTP request. The Wiz Research Team observed active exploitation attempts across environments almost immediately, with 50% of our customers with ASM Finding showing signs of compromise, demanding defenders to quickly assess risk, understand impact, and remove active threat.
Wiz ASM: SOC-Level Alerts without the crisis
This urgency emphasizes the importance of quickly being able to detect where you are exploitable and at risk, knowing that an attacker may be only hours away from finding it. But, in sprawling cloud environments, finding all vulnerable instances is hard enough on its own, let alone identifying the few that are truly exploitable.
This is why
Attack Surface Management (ASM)
provides the crucial visibility needed for SecOps and SOC teams to proactively identify and address exploitable risks, serving as a pre-breach SOC-level alert to stay confident in the face of urgency. So rather than being woken up at 3:00 AM to a breach notification,  ASM Validated External Risk Issues enable teams to identify exactly where they are exposed and exploitable, what is its impact, and who needs to fix the risk- so they can close the security hole before it becomes an active threat.
By operating from the attacker’s perspective,
Wiz ASM
continuously and agentlessly scans the external attack surface to find exactly what is exposed and exploitable to risks such as vulnerabilities, misconfigurations, and default credentials. The power of this proactive monitoring was proven with React2Shell. Within hours of the disclosure, the Wiz Research team deployed a dedicated ASM rule to provide customers with validated findings, identifying the specific assets truly exploitable to CVE-2025-55182 from the internet. Our team added a new Risk Issue to provide defenders with the instant visibility and full context required to remediate the exposure before it can be exploited.
Because these are high-fidelity, SOC-level alerts, teams can trust that an ASM finding represents a verified risk requiring immediate action. Each alert is enriched with the context necessary to prioritize based on business impact and identify risk owners for fast remediation, effectively transforming a potential crisis into a manageable task.
Why Context-Aware ASM is Crucial for Addressing High Profile Threats
Context-aware ASM is required to ensure full visibility, accurate prioritization, and fast remediation of exploitable risk by:
Eliminating Blind Spots:
Teams rely on ASM to uncover blind spots before a threat arises. Wiz ASM leverages cloud context and analyzes complex cloud network configurations to automatically discover shadow assets that fall outside standard domains- such as ec2-xx-xx-xx-xx.compute.com- ensuring no assets remain unknown.
Impact-Based Prioritization:
Context allows teams to prioritize risk based on potential impact. By correlating findings on the Security Graph, Wiz answers critical questions: Is the asset in production? Can an attacker use it to move laterally, escalate privileges, or access sensitive data? This ensures teams focus on the risks with true potential blast radius.
Rapid Remediation:
Once an exploitable risk is verified, the clock is ticking. Wiz uses cloud and code context to instantly identify the owner, such as the application owner and developer. By knowing exactly who needs to fix the issue and where, teams can route and resolve exploitable risks quickly.
Extending protection from high-profile threats with a unified code-to-cloud platform
By integrating ASM into their core security strategy, SecOps and SOC teams gain the pre-breach alerts needed to act with precision and confidence in the face of a zero-day vulnerability. In addition, Wiz helps teams address threats like React2Shell beyond external attack surface scanning with code-to-runtime capabilities helping you protect all the way from prevention to detection. Read
this blog
for more technical information on the vulnerability and
this blog
about Wiz ASM.
Tags
#
Product