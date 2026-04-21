# Pull Vulnerabilities Using Delta Updates Tutorial
*Learn how to pull Vulnerability Findings from Wiz using delta updates with filters for severity and CVE.*

Category: vulnerabilities

To maintain efficiency and achieve WIN certification, implement a delta update strategy. This method ensures you retrieve the most current and relevant vulnerability data while minimizing unnecessary data transfer and processing.

In this tutorial, you'll learn how to pull vulnerabilities using the [Pull Vulnerabilities](dev:vulnerability-finding) API. This tutorial will guide you through implementing delta updates in your vulnerability management system.

## How delta updates work

Delta updates allow you to pull only the changed vulnerabilities since your last export. You can accomplish this by using the `updatedAt` filter in your GraphQL queries to capture all changes, including:

- Newly opened vulnerabilities
- Vulnerabilities whose status changed
- Recently resolved vulnerabilities
- Ignored findings
- Modified vulnerability information

:::info

The `updatedAt` timestamp for a vulnerability is only modified when its properties change, such as its status. Re-detecting a vulnerability will update the `lastDetectedAt` timestamp but will not affect `updatedAt`.

:::

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read: vulnerabilities`

## Implementation

Here's an example query that retrieves vulnerabilities whose status changed after the specified timestamp:

```json Example
 "query": "query VulnerabilityFindingsPage($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String, $orderBy: VulnerabilityFindingOrder) { vulnerabilityFindings( filterBy: $filterBy first: $first after: $after orderBy: $orderBy ) { nodes { id portalUrl name CVEDescription CVSSSeverity score exploitabilityScore severity nvdSeverity weightedSeverity impactScore dataSourceName hasExploit hasCisaKevExploit status vendorSeverity firstDetectedAt lastDetectedAt resolvedAt description remediation detailedName version fixedVersion detectionMethod link locationPath resolutionReason epssSeverity epssPercentile epssProbability validatedInRuntime layerMetadata { id details isBaseLayer } projects { id name slug businessUnit riskProfile { businessImpact } } ignoreRules { id name enabled expiredAt } cvssv2 { attackVector attackComplexity confidentialityImpact integrityImpact privilegesRequired userInteractionRequired } cvssv3 { attackVector attackComplexity confidentialityImpact integrityImpact privilegesRequired userInteractionRequired } relatedIssueAnalytics { issueCount criticalSeverityCount highSeverityCount mediumSeverityCount lowSeverityCount informationalSeverityCount } cnaScore vulnerableAsset { ... on VulnerableAssetBase { id type name region providerUniqueId cloudProviderURL cloudPlatform status subscriptionName subscriptionExternalId subscriptionId tags hasLimitedInternetExposure hasWideInternetExposure isAccessibleFromVPN isAccessibleFromOtherVnets isAccessibleFromOtherSubscriptions } ... on VulnerableAssetVirtualMachine { operatingSystem ipAddresses imageName nativeType computeInstanceGroup { id externalId name replicaCount tags } } ... on VulnerableAssetServerless { runtime } ... on VulnerableAssetContainerImage { imageId scanSource registry { name externalId } repository { name externalId } executionControllers { id name entityType externalId providerUniqueId name subscriptionExternalId subscriptionId subscriptionName ancestors { id name entityType externalId providerUniqueId } } } ... on VulnerableAssetContainer { ImageExternalId VmExternalId ServerlessContainer PodNamespace PodName NodeName } } } pageInfo { hasNextPage endCursor } } }",
  "variables": {
    "first": 1,
    "filterBy": {
      "updatedAt": {
        "after": "2024-10-22T07:30:28.924Z"
      }
    }
  }
```

Key parameters:

- `filterBy`: An object containing filtering criteria:
  - `updatedAt.after`: Filters vulnerabilities based on their update timestamp. Use with `after` to only include vulnerabilities updated after the specified ISO 8601 timestamp. The filter `updatedAt.before` is also available to pull vulnerabilities updated before the specified date.

Here's an example query that also retrieves vulnerabilities based on the severity of their [associated Issues](dev:vulnerabilities#prioritize-by-number-of-related-issues):

```json Example
 "query": "query VulnerabilityFindingsPage($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String, $orderBy: VulnerabilityFindingOrder) { vulnerabilityFindings( filterBy: $filterBy first: $first after: $after orderBy: $orderBy ) { nodes { id portalUrl name CVEDescription CVSSSeverity score exploitabilityScore impactScore dataSourceName hasExploit hasCisaKevExploit status vendorSeverity firstDetectedAt lastDetectedAt resolvedAt description remediation detailedName version fixedVersion detectionMethod link locationPath resolutionReason epssSeverity epssPercentile epssProbability validatedInRuntime layerMetadata { id details isBaseLayer } projects { id name slug businessUnit riskProfile { businessImpact } } ignoreRules { id name enabled expiredAt } cvssv2 { attackVector attackComplexity confidentialityImpact integrityImpact privilegesRequired userInteractionRequired } cvssv3 { attackVector attackComplexity confidentialityImpact integrityImpact privilegesRequired userInteractionRequired } relatedIssueAnalytics { issueCount criticalSeverityCount highSeverityCount mediumSeverityCount lowSeverityCount informationalSeverityCount } cnaScore vulnerableAsset { ... on VulnerableAssetBase { id type name region providerUniqueId cloudProviderURL cloudPlatform status subscriptionName subscriptionExternalId subscriptionId tags hasLimitedInternetExposure hasWideInternetExposure isAccessibleFromVPN isAccessibleFromOtherVnets isAccessibleFromOtherSubscriptions } ... on VulnerableAssetVirtualMachine { operatingSystem ipAddresses imageName nativeType computeInstanceGroup { id externalId name replicaCount tags } } ... on VulnerableAssetServerless { runtime } ... on VulnerableAssetContainerImage { imageId scanSource registry { name externalId } repository { name externalId } executionControllers { id name entityType externalId providerUniqueId name subscriptionExternalId subscriptionId subscriptionName ancestors { id name entityType externalId providerUniqueId } } } ... on VulnerableAssetContainer { ImageExternalId VmExternalId ServerlessContainer PodNamespace PodName NodeName } } } pageInfo { hasNextPage endCursor } } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "relatedIssueSeverity": ["CRITICAL"],
      "updatedAt": {
        "after": "2024-10-22T07:30:28.924Z"
      }
    },
    "orderBy": {
      "field": "RELATED_ISSUE_SEVERITY",
      "direction": "DESC"
  }
}
```

Key parameters:

- `relatedIssueSeverity`: Filters vulnerabilities based on their related Issues' severity levels. Currently set to include only "CRITICAL" Issue.
- `orderBy`: Specifies the sorting criteria for the results:
  - `field`: The field to sort by, set to "RELATED_ISSUE_SEVERITY".
  - `direction`: The sort direction, set to "DESC" (descending order).

:::success[Done! You have pulled vulnerabilities using the Pull Vulnerabilities API]

:::

## Best practices for implementation

<Deltaupdatesbestpractices />

## Next steps

- [See Pull Vulnerabilities API reference](dev:vulnerability-finding)
- [See certification process](dev:certification-process)
