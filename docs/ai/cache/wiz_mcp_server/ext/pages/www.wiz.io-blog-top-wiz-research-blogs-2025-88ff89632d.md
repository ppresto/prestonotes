---
url: https://www.wiz.io/blog/top-wiz-research-blogs-2025
source_name: blog_security
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-01-30T08:00:00-05:00
extraction_mode: static_fetch
content_hash: 38b72b6786c5
---

# Top Wiz Research Blogs: 2025 | Wiz Blog

In 2025, the lines between cloud, AI, and software supply chains continued to blur. Wiz Research spent the year tracking how attackers adapted to this shift with the most impactful findings surfacing in three key areas:
Supply chain attacks:
The cloud supply chain emerged as the new frontline, accounting for more than half of our most-read investigations in 2025. Malware campaigns evolved to spread silently across CI/CD systems, package registries, and build pipelines – often relying on the wide adoption of npm and GitHub. In 2026, we may see these campaigns extend into IDE extensions and AI artifacts like models, MCP servers, and skills.
AI exposure:
Our most-read research post of 2025 was the investigation into an exposed DeepSeek database, kicking off a year shaped by the rapid rollout of LLMs and AI developer tools. That wave of adoption led to misconfigurations, token leaks, and pipeline gaps attackers continue to exploit in 2026.
Core infrastructure risk:
Some of our most-read research focused on critical vulnerabilities in widely used software, like IngressNightmare and React2Shell.This showed how much hidden risk still lives in the core software we all rely on. The upside is that AI-enabled vulnerability research is helping bring these issues to light and reduce the risk – as we saw in action at
zeroday.cloud competition
last month.
Top research posts of 2025
Here are the top 10 most-read research posts of the year.
1.
Wiz Research Uncovers Exposed DeepSeek Database Leaking Sensitive Information, Including Chat History
Wiz Research identified a publicly accessible ClickHouse database belonging to DeepSeek, which allowed full control over database operations, including the ability to access internal data. The exposure included over a million lines of log streams containing chat history, secret keys, backend details, and other highly sensitive information.
2.
Shai-Hulud 2.0 Supply Chain Attack: 25K+ Repos Exposing Secrets
A second Shai-Hulud–linked npm supply-chain campaign compromised major packages, some of which were highly prevalent, occurring in roughly 27% of cloud and code environments scanned by Wiz. The blast radius was massive and growing quickly due to widespread automated replication: 25,000+ malicious repos across ~500 GitHub users, accelerating at ~1,000 new repos every 30 minutes.
3.
React2Shell (CVE-2025-55182): Everything You Need to Know About the Critical React Vulnerability
A critical vulnerability was identified in the React Server Components (RSC) "Flight" protocol, affecting the React 19 ecosystem and frameworks that implement it, most notably Next.js. Assigned CVE-2025-55182, this flaw allowed for unauthenticated remote code execution (RCE) on the server due to insecure deserialization. Wiz Research data showed 39% of cloud environments contained vulnerable instances.
4.
IngressNightmare: CVE-2025-1974 - 9.8 Critical Unauthenticated Remote Code Execution Vulnerabilities in Ingress NGINX
Wiz Research discovered CVE-2025-1097, CVE-2025-1098, CVE-2025-24514 and CVE-2025-1974, a series of unauthenticated RCE vulnerabilities in Ingress NGINX Controller for Kubernetes dubbed #IngressNightmare. Exploitation of these vulnerabilities could’ve led to unauthorized access to all secrets stored across all namespaces in the Kubernetes cluster by attackers, which can result in cluster takeover.
5.
Shai-Hulud: Ongoing Package Supply Chain Worm Delivering Data-Stealing Malware
The first Shai-Hulud supply chain attack occurred when malicious versions of multiple popular packages were published to npm. They contained a post-install script that harvested sensitive data and exfiltrated it to attacker-created public GitHub repos named Shai-Hulud. Beyond data theft, the malware exhibited worm-like behaviour: when a compromised package encountered additional npm tokens in its environment, it automatically published malicious versions of any packages it could access, spreading across the npm ecosystem.
6.
RediShell: Critical Remote Code Execution Vulnerability (CVE-2025-49844) in Redis, 10 CVSS score
Wiz Research uncovered a critical RCE vulnerability, CVE-2025-49844 dubbed #RediShell, in the widely used Redis in-memory data structure store. The vulnerability exploits a Use-After-Free (UAF) memory corruption bug that has existed for approximately 13 years in the Redis source code. 75% of cloud environments were potentially impacted.
7.
s1ngularity: supply chain attack leaks secrets on GitHub: everything you need to know
Multiple malicious versions of the widely used Nx build system package were published to the npm registry. These versions contained a post-installation malware script designed to harvest sensitive developer assets, including cryptocurrency wallets, GitHub and npm tokens, SSH keys, and more. The malware leveraged AI command-line tools (including Claude, Gemini, and Q) to aid in their reconnaissance efforts.
8.
GitHub Action tj-actions/changed-files supply chain attack: everything you need to know
A supply chain attack on popular GitHub Action tj-actions/changed-files caused many repositories to leak their secrets. Wiz Research observed first-hand the deployment of the script designed to dump secrets as part of the malicious payload's execution and also identified dozens of impacted public repositories with exposed sensitive secrets.
9.
New GitHub Action supply chain attack: reviewdog/action-setup
In parallel to the supply chain attack on tj-actions/changed-files, Wiz Research discovered an additional supply chain attack on reviewdog/actions-setup@v1 that may have contributed to the compromise of tj-actions/changed-files. This series of attacks targeted Coinbase, who confirmed an unsuccessful attempt to compromise coinbase/agentkit.
10.
Widespread npm Supply Chain Attack: Breaking Down Impact & Scope Across Debug, Chalk, and Beyond
Wiz Research published a forensic analysis of the npm debug/chalk supply-chain incident. Wiz found that during the short 2-hour timeframe in which the malicious versions were available on npm, the malicious code successfully reached 1 in 10 cloud environments. This serves to demonstrate how fast malicious code can propagate in supply chain attacks.
Conclusion
The most-read Wiz Research posts of 2025 highlight how quickly the cloud security landscape is changing. From supply chain attacks to AI-driven risk and core infrastructure flaws, the same theme keeps emerging: complexity creates opportunity for attackers.
As these trends continue into 2026, Wiz Research will stay focused on uncovering real-world exposure and sharing insights that help teams understand where risk is building and how to respond.
See more from Wiz Research
Tags
#
Security