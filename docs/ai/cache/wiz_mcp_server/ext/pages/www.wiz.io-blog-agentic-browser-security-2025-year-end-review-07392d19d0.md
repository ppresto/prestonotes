---
url: https://www.wiz.io/blog/agentic-browser-security-2025-year-end-review
source_name: blog_ai
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-01-16T12:23:17-05:00
extraction_mode: static_fetch
content_hash: b924e1812537
---

# Agentic Browser Security: 2025 Year-End Review | Wiz Blog

An Agentic Browser is an AI-powered co-pilot that not only reads the web, it acts on it. By understanding page content and executing multi-step tasks autonomously, these agents can book flights, shop, and fill out forms without step-by-step human guidance. In 2025, this technology moved rapidly from experimental prototype to mainstream production.
But that autonomy brings major risks along. As we
recently observed in TechCrunch
:
The risk is high given [Agentic Browsers'] access to sensitive data like email and payment information, even though that access is also what makes them powerful. That balance will evolve, but today the trade-offs are still very real.
We’ve spent the last year tracking this space. Here is how we reached that conclusion, the offensive and defensive research we’ve been monitoring, and how the "autonomy vs. access" matrix will shape the future of browsing.
The Year of Agentic Browsers
Generative AI has been integrated into browsers since the early days of LLMs. The Brave browser launched a
browser-integrated AI assistant in 2023
, shortly after the launch of ChatGPT. However, 2025 was the year AI Browsers went mainstream:
A timeline of Agentic Browser launches in 2025
These launches have come with
impressive demo videos
and bold promises of a future where you never have to "manually" browse again.
The Year in Attacks on Agentic Browser
The rapid growth of agentic browsers has been met with a concurrent surge in security research:
February:
Shortly following the ChatGPT Operator preview, Johann Rehberger demonstrated
Zero-Interaction Exfiltration
, using hidden instructions on a GitHub page to command the AI to leak private data without user input.
August:
Guardio Labs published “
Scamlexity
,” revealing that AI browsers lack the "skepticism" needed to spot phishing. In tests, Perplexity’s Comet successfully purchased items from fake storefronts and clicked phishing links on behalf of the user.
August-October:
Brave turned their research on to competing AI Browsers, disclosing
Indirect Prompt Injection in Perplexity Comet
,
prompt injections in screenshots
impacting Comet & Fellou, and
prompt injection in Opera Neon
.
September:
Tenable disclosed the “
Gemini Trifecta
,” proving that browsers could be tricked into leaking sensitive data via background API calls.
October:
LayerX demonstrated a "one-click" hijack of Perplexity’s Comet ("
CometJacking
") using crafted URL query parameters to exfiltrate emails and calendar data.  They also disclosed "
Tainted Memories
," a CSRF vulnerability in OpenAI’s Atlas that allowed attackers to "poison" the long-term memory of the AI, creating persistent malicious instructions that survived across sessions.
November:
Cato Networks published “
HashJack
,” an indirect prompt injection technique that hides instructions in URL fragments (after the #).
December:
A Google researcher disclosed “
Task Injection
” in OpenAI's Operator. This tricks the agent into believing a malicious sub-task (like solving a fake CAPTCHA that actually triggers a file download) is a legitimate part of achieving the user's original goal.
Manufacturer’s Guidance
The developers of these Agentic Browsers have not been passive. They have moved from simple "Ask before acting" prompt-based security to multi-layered security architectures. We are seeing a convergence around
Human-in-the-Loop (HITL)
as the guardrail, while the real technical differentiation now lies in
Reinforcement Learning
,
Architectural Isolation
and
Secondary LLM Critics
.
The table below outlines the defensive posture documented as of the end of 2025:
Browser
Human-in-the-Loop (HITL)
Architectural Isolation
Automated Red Teaming & Reinforcement Learning
Classifiers & Critics
Access Restrictions
Google (Gemini in Chrome)
Default: Confirmations for payments, messages, and sensitive site entry.
Default: "Origin Sets" restrict agent to task-relevant sites only.
Default: Automated red-teaming generating malicious sandboxed sites.
Default: "User Alignment Critic" (2nd model) vets every proposed action.
Default: URL redaction and markdown sanitization.
OpenAI (Atlas)
Default: "Watch Mode" (pauses if tab is inactive). Mandatory confirm for emails/buys.
Optional: "Logged Out Mode" for browsing without session credentials.
Default: "RL-trained Attacker" proactively hunts for vulnerabilities.
Default: Rapid Response Loop to block active attack campaigns.
Default: Prohibits broad "do whatever" prompts; requires scoping.
Anthropic (Claude in Chrome)
Default: Mandatory confirmation for publishing or data sharing.
—
Default: Adversarial RL training and scaled expert human red teaming.
Default: "Constitutional Classifiers" scan all untrusted content.
Default: Blocks high-risk sites (Banking/Adult) and uses site-level permissions.
Perplexity (Comet)
Default: Required for actions flagged by the detector.
Default: "Trust Boundary Enforcement" isolating web content.
Feature: Synthetic training pipeline generates malicious data for hardening.
Default: Hybrid Detection (Fast classifier + Reasoning LLM for edge cases).
—
Brave (Leo)
Default: Required for actions flagged by the alignment checker.
Default: Isolated browser profile (separate cookies/storage).
—
Default: Alignment Checker (2nd model) compares agent plan to user intent.
Default: No access to non-HTTPS, internal pages, or Safe Browsing sites.
Opera (Neon)
Default: Pauses for transactions or downloads.
Default: "Tasks" (self-contained mini-browsers for projects).
—
Default: Prompt processing/analysis for malicious traits.
Default: Blacklisting of high-risk pages (Banking) by default.
The Browser Co. (Dia)
Default: Manual review for all "Write" actions (forms/drafts).
Default: Tool limiting; passwords and sensitive UI are hidden from AI.
—
Default: Strips instructions from URLs before model processing.
Default: Navigation Ban (cannot visit new sites autonomously).
The Defense-in-Depth Model
To make sense of this table, it helps to think of the security model as a series of filters. No single layer is a "silver bullet" against prompt injection, but together they raise the cost of an attack significantly.
Ideally, we will see these vendors continue to learn from each other, and constantly pushing forward the state of the art.
Where this leaves us
We get a clear and consistent message from the front lines. OpenAI’s CISO, Dane Stuckey, identified recently that
prompt injection remains a frontier, unsolved security problem
.
While manufacturers are racing to build layered controls, the technical reality is that as long as an agent is working against untrusted web content, it can be manipulated.
When reasoning about these risks, the quick framework is the
Autonomy and Access Matrix
. Agentic browsers occupy the most dangerous quadrant: they possess the autonomy to act and high-level access to the sensitive data stored in your browser.
Simple AI Risk Framework: Autonomy x Access
We are likely reliving a familiar cycle in browser security history. But is it the
"Flash" era
, where the technology is so structurally porous that it will eventually be abandoned? Or the
early browser era
, simply enduring the "growing pains" of bugs that will eventually be solved by the multi-layered sandboxing we see vendors currently prototyping?
In December 2025, Gartner issued a definitive directive recommending that CISOs
block the use of AI browsers
for now. While this aligns with a "security-first" posture, it risks creating a "Department of No" culture that stifles innovation. Kane Narraway, a security leader,
offered a more nuanced take
:
You can totally block them today, and it’s probably recommended, but have a plan for when it isn’t an option anymore, and start building this into your roadmaps for 2026.
We cannot reach frontier capabilities without these risks. The goal is not to avoid the technology forever, but to celebrate the current transparency around its flaws while making responsible decisions.
If you are experimenting with Agentic Browsers today, follow these three rules:
Isolate the Context:
Use dedicated, isolated browser profiles that do not share credentials with your primary work email or banking.
Preserve the Human:
Never disable "Human-in-the-Loop" confirmations when working with a privileged agentic browser session.
Limit the Blast Radius:
Restrict agent use to low-stakes tasks (e.g., research, public data gathering) where a "hallucinated" or "injected" action carries lower cost.
Tags
#
Research
#
AI