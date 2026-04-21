---
url: https://www.wiz.io/blog/wiz-runtime-sensor-for-your-windows-environment
source_tool: browser_render_plus_web_fetch
fetched_at: 2026-02-27T23:44:00Z
freshness_state: fresh
retrieval_status: ok
classification: content-dominant
extraction_mode: hybrid_browser_assisted_static
render_wait_seconds: 2
selector_used: main
content_length_chars: 8200
extract_quality_notes: full article body captured; previous truncation removed
---

# Cloud-native Security for your Windows environment: Announcing the Wiz Runtime Sensor for Windows

## Core Article Body

Today, Wiz announced Public Preview support for the Wiz Runtime Sensor on Windows, extending runtime detection and response parity from Linux and container workloads to Windows environments.

The post frames this as completing the Windows security lifecycle in Wiz by combining:
- agentless visibility across code/pipeline/cloud
- runtime telemetry from Windows workloads
- unified attack context in Wiz Defend

### Key points called out

- **Unified hybrid coverage**
  - Windows and Linux VM visibility
  - Kubernetes parity including Windows nodes
  - Multi-cloud and hybrid support

- **Design goals for Windows stability**
  - Minimal kernel footprint with logic pushed to user space
  - Memory-safe implementation (Rust emphasis)
  - Predictable resource usage profile

- **Detection and response outcomes**
  - Runtime events correlated with cloud control plane signals
  - Threat timeline context for investigation
  - Support for custom runtime detections and automated response actions
  - Forensics capture for investigation context

- **Runtime risk validation**
  - Prioritize vulnerabilities actually loaded/executed in memory
  - Reduce backlog noise by focusing on exploitable runtime exposure

### Notable references in page content

- `https://www.wiz.io/blog/wiz-defend-general-availability`
- `https://www.wiz.io/blog/custom-runtime-rules-and-response-policies`
- `https://www.wiz.io/blog/ai-powered-wiz-forensics`
- `https://docs.wiz.io/docs/windows`

## Additional Context Extracted

The page also includes standard blog navigation, related-articles sections, and marketing CTA/footer content. These were retained only where they contributed direct product context.

