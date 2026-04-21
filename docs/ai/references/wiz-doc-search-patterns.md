# Wiz Docs Search Patterns Cache

Last updated: 2026-02-25

Use these query patterns with `wiz_search_wiz_docs` to maximize product coverage.

## Core Product Discovery
- Wiz products overview and architecture (Cloud, Code, Defend, Runtime Sensor)
- Getting started page product/solution links and deep links
- Licenses, deployments, and connect/configure overview

## Cloud Platform Coverage
- Wiz Cloud architecture and cloud graph model
- Agentless scanning, registry scanning, malware detection, risk assessment
- Attack surface / network exposure / application endpoints
- Kubernetes and container security coverage
- AWS, Azure, GCP service and integration coverage

## Code Security Coverage
- SAST, SCA, IaC, container image scanning in Wiz Code
- VCS connectors, pull-request scans, scheduled scans, repo coverage
- UVM/ASPM third-party scanner integrations (Snyk, Semgrep, SonarQube, etc.)
- Remediation workflows, AI-assisted triage, and developer workflows

## Defend / Runtime / Response Coverage
- Defend get-started, runtime sensor deployment, and telemetry model
- Real-time threat detection, detections vs threats, and rule categories
- Incident readiness, response actions, and SecOps integration patterns

## Integration and Automation Coverage
- Integration APIs, webhooks (issues/detections/threats), automation rules
- SIEM/SOAR/ticketing patterns and payload references
- Terraform/provider docs and API explorer references

## Release and Change Tracking
- Changelog pages by week and special bulletins
- Product Updates and roadmap references

## Per-URL Deep Crawl Pattern
- For each cached URL, run a targeted query:
  - "Starting from <url>, list linked docs pages up to N levels deep and include links."
- If docs search returns low-quality matches, pivot to focused category prompts:
  - "<product/category> linked docs from <url> with direct docs.wiz.io links"
- Append all new `docs.wiz.io/docs/*` and `docs.wiz.io/changelog/*` links to the link ledger with:
  - `status` (`mcp_discovered`, `fetched_200`, `429_rate_limited`)
  - `depth` estimate
  - `discovered_from` URL

### Depth Policy
- Default: depth **5** (recommended for recurring refresh runs).
- Deep audit mode: depth **9** only when:
  - major docs IA/restructure suspected, or
  - quarterly full-audit run is requested.
- Stop early if two consecutive depth waves produce no new links.
