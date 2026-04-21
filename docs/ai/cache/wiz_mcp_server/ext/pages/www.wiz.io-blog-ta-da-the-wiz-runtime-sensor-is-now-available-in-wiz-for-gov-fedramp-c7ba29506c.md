---
url: https://www.wiz.io/blog/ta-da-the-wiz-runtime-sensor-is-now-available-in-wiz-for-gov-fedramp
source_name: blog_public_sector
fetched_at: 2026-03-02T17:52:04Z
published_at: 2024-10-14T11:14:31-04:00
extraction_mode: static_fetch
content_hash: b3d1c3232c41
---

# Wiz Adds Runtime Sensor to its Wiz for Gov Platform   | Wiz Blog

We are excited to announce the addition of the Wiz Runtime Sensor to Wiz for Gov, expanding our full-featured Cloud Native Application Protection Platform (CNAPP) for government customers. Our commitment to the
FedRAMP authorization process
allows us to offer the same product experience across both commercial and FedRAMP environments.
Wiz was born in the cloud and is laser-focused on enhancing the cloud security posture for all our users. Our agentless-first approach ensures complete visibility across any cloud environment, and the addition of the
runtime sensor
unlocks use cases that require deep, real-time context. By combining agentless and runtime capabilities, we provide our customers with a unified platform for both proactive and reactive security strategies.
Wiz enables us to combine the reactive and proactive aspects of cloud security in a single source of truth. We rely on the visibility that Wiz provides to surface the unknowns and provide actionable signals from noise, allowing us to prioritize our efforts. With the Wiz Sensor, we are adding active, real-time telemetry that gives my team intelligent insight to drive better actions. By leveraging Wiz, we can support and accelerate our cloud transformation without doubling the security team because my team is more efficient and able to focus on strategic work. Wiz simplifies our security challenges and will allow us to more than double our cloud environment over the coming years without scaling complexity.
Joel Cardella, Director, Cybersecurity Engineering, Dexcom
We have developed a lightweight runtime component specifically designed for the cloud by creating an eBPF-based sensor that is built to protect cloud-native, highly ephemeral workloads. Additionally, because eBPF sensors run in a restricted environment within the kernel, they cannot crash or degrade the performance of the host. Despite being lightweight, the sensor enables a broad range of use cases, including improving risk prioritization, deepening real-time threat detection, and adding runtime protection for container hosts and VMs.
Bringing the runtime sensor to Wiz for Gov has been one of our top priorities because our government focused customers deserve a comprehensive CNAPP to protect their most sensitive environments. Wiz addresses dozens of use cases, providing a natural path for tool consolidation as the platform is adopted and operationalized. Historically, options for cloud-native security products on the FedRAMP marketplace have been limited, especially when specific solutions like container security or runtime protection are required. FedRAMP controls, CMMC, Binding Operational Directives (BOD) 22-01 and 23-01, and NIST SP 800-53r5 result in requirements for cloud service providers to the U.S. government that prescribe use of runtime security.
Linking individual intrusion detection tools into a system-wide intrusion detection system provides additional coverage and effective detection capabilities. The information contained in one intrusion detection tool can be shared widely across the organization, making the system-wide detection capability more robust and powerful.”
SI-4(01), NIST SP 800-53r5
Often, organizations must base their technology choice on solutions that adhere to these mandates, versus choosing the best fit for their needs and overall security posture. The limited tooling options make it difficult to correlate runtime events with cloud events, let alone consider correlating cloud infrastructure risk. The Wiz for Gov CNAPP eliminates this pain point and many others by simplifying, improving, and democratizing security for all organizations. At the core of Wiz is the Security Graph, which visualizes and simplifies complex relationships between resources, identities, permissions, network, runtime, and cloud telemetry. These relationships amplify the power of runtime security with Wiz.
Here’s how the Wiz Runtime Sensor simplifies and improves security:
Ease of deployment:
The lightweight eBPF based senser can be deployed on VMs with a single click from the console or use a unified Helm chart to deploy the sensor as a DaemonSet for Kubernetes environments.
Validation of vulnerabilities in runtime:
The sensor Enriches Wiz’s agentless vulnerability assessment using runtime workload signals to identify vulnerabilities affecting active packages that are being used by the workload, so security teams can focus remediation efforts. This validation, with Software Bill of Materials (SBOM), allows teams to identify all software installed in the cloud environment and distinguish between what is actively in use. This aligns with improved asset visibility and vulnerability detection outlined in BOD 23-01.
Hybrid file integrity monitoring (FIM):
Detect breaches early, expose security gaps, and simplify compliance with the speed and depth of runtime FIM, combined with the coverage of agentless FIM. Control both by defining unified policies or using pre-configured rules and respond by creating a finding, an issue, or automated blocking.
Real-time detection:
Detect and respond in real-time on the virtual machine. Create custom threat detection rules or use predefined rules to detect and block malware, reverse shells, container drift, log tampering, container escapes, and more. These detections bring in additional cloud context to determine risk and prioritize threats for security teams. Additionally, having the full context of the detection allows teams to quickly triage and identify the root cause.
Runtime response policies:
Response policies allow users to automate the response actions (blocking) for high-certainty threats at runtime. Blocking provides immediate defense, stopping malicious activities before they can cause significant damage. By automating this process, security teams can respond instantly to threats without manual intervention, freeing up their time to focus on more strategic tasks rather than continuously monitoring and reacting to threats.
Expand cloud detection and response:
Correlate threats across workload runtime signal, cloud activity, and audit logs in a unified, contextual view to uncover attacker movement within a cloud environment so cloud defenders can rapidly respond to limit the impact of a potential incident and use cloud context to prioritize threats.
Enable cloud threat hunting and forensics:
Collect, retain, and hunt over runtime execution data. The sensor captures execution data and full process tree information for every protected host, helping teams pinpoint the root cause of incidents and streamline investigations.
Wiz is committed to providing a unified CNAPP that combines agentless visibility with the power of runtime monitoring, empowering users with both proactive and reactive security measures. The addition of the eBPF-based runtime sensor to Wiz for Gov extends our capabilities in FedRAMP environments, ensuring that organizations can meet stringent compliance requirements and directives. Wiz enables government agencies and commercial partners to confidently adopt modern cloud technology quickly and securely.
See Wiz in action
Discover how Wiz can help you secure your cloud infrastructure effortlessly. Request a personalized demo to explore our powerful features and see how we can address your specific security needs.
Get a Demo
Tags
#
Product
#
Public Sector