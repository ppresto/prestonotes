---
url: https://www.wiz.io/blog/wiz-zeroday-cloud-hacking-competition-behind-the-scenes
source_name: blog_ai
fetched_at: 2026-03-02T17:52:04Z
published_at: 2025-12-16T10:30:00-05:00
extraction_mode: static_fetch
content_hash: 8a6d83b69db0
---

# Zero‑Days in the Age of AI: Behind the Scenes of ZeroDay.cloud 2025, with a Record High of CVEs in Critical Cloud Infra | Wiz Blog

The
zeroday.cloud
competition may be over, but the race is just beginning.
Last week in London, Wiz Research hosted a first-of-its-kind cloud hacking competition in partnership with AWS, Microsoft, and Google Cloud. Over two days, the world’s top researchers came together to test the security of the open-source technologies powering modern cloud and AI infrastructure.
The takeaway: AI is accelerating vulnerability discovery for both defenders and attackers, ushering in a new era of zero-days.
The Results
In just two days, researchers uncovered critical Remote Code Execution (RCE) vulnerabilities across the foundational layers of cloud infrastructure. They earned $320,000 in rewards and achieved an 85 percent success rate across all live hacking attempts.
In total, this event produced what is, to date, one of the
highest counts of publicly disclosed CVEs
specifically affecting foundational open‑source components used in critical cloud infrastructure — from databases to container runtimes. These findings reveal both the depth of modern attack surfaces and the importance of focused defensive research.
Researchers demonstrated vulnerabilities in the world's most popular databases: Redis, PostgreSQL, and MariaDB - the very vaults where the cloud stores its most critical information.
An RCE here enables attackers to target any application built on top of them, from websites to mobile apps, and seize the "keys to the kingdom.” This grants unauthorized access to every scrap of underlying data, including user information, passwords, secrets, and sensitive PII.
The most severe exploit targeted the foundation of the cloud itself: the Linux
operating system. The vulnerability allows for a Container Escape, often enabling attackers to break out of an isolated cloud service, dedicated to one specific user, and spread to the underlying infrastructure that manages all users. This breaks the core promise of cloud computing: the guarantee that different customers running on the same hardware remain separate and inaccessible to one another. This further reinforces that containers shouldn’t be the sole security barrier in multi-tenant environments.
Researchers also attempted to demonstrate exploits for vLLM and Ollama, the de facto standards for running open-source AI models. One of the exploits would’ve let attackers gain direct access to major enterprises' private AI artifacts including models, datasets and prompts. However, the researchers’ attempts were unsuccessful in the time allotted.
The Takeaway
Cloud and AI infrastructure are now squarely part of the modern attack surface. And as zeroday.cloud made clear, the race is on. Attackers and defenders alike are using AI to discover vulnerabilities faster than ever, turning what used to take months into a matter of hours. Staying ahead means matching that speed, with the same urgency and innovation driving the technologies we’re trying to protect. The prompt validation and support from project maintainers and our cloud partners, demonstrated that the industry is ready to tackle these threats together.
Behind the Scenes of Day 1: $200,000 total awarded
Redis:
Yoni Sherez – SUCCESSFUL – $30,000 awarded
PostgreSQL:
Daniel Firer – SUCCESSFUL – $30,000 awarded
Grafana:
Team Bugz Bunnies (Paul Gerste & Moritz Sanft) – SUCCESSFUL – $10,000 awarded (authenticated RCE)
Redis:
Emil Lerner – SUCCESSFUL – $30,000 awarded
PostgreSQL:
Team Xint Code – SUCCESSFUL – $30,000 awarded
Redis:
Team Skateboarding Dog – SUCCESSFUL – $30,000 awarded
Linux Kernel:
Team CCC (Faith from Zellic & Pumpkin from DEVCORE Research Team) – SUCCESSFUL – $40,000 awarded
Behind the Scenes of Day 2: $120,000 total awarded
Redis:
Daniel Firer – SUCCESSFUL – $30,000 awarded
PostgreSQL:
Team Bugz Bunnies (Paul Gerste & Moritz Sanft) – SUCCESSFUL – $30,000 awarded
Redis:
Team Xint Code – SUCCESSFUL – $30,000 awarded
vLLM:
Bohdan Ivanenko – TIME LIMIT EXCEEDED
MariaDB:
Team Xint Code – SUCCESSFUL – $30,000 awarded
Ollama:
Team Bugz Bunnies (Paul Gerste & Moritz Sanft) – TIME LIMIT EXCEEDED
Team Xint Code crowned
zeroday.cloud champion
Tags
#
Research
#
AI
#
Product & Company News