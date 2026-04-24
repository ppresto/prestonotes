# Get IaC Findings Tutorial
*Learn how to pull IaC Configuration Findings using the IaCFindingsTable query with filters for severity, status, platform, and more.*

Category: iac-findings

In this tutorial, learn how to pull IaC Configuration Findings from Wiz.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:iac_findings` permission

### Pull IaC Findings

Execute the `IaCFindingsTable` query to return a paginated list of IaC Configuration Findings according to different filters, such as severity, status, cloud platform, or IaC platform.

The following query returns the first five IaC Findings, where:

- `first`—Pagination value that determines the number of results per page. You must include a value or the API call fails. In this example, it returns the first 5 results.
- `severity`—Filter the results based on finding severity. This example returns CRITICAL and HIGH severity findings.
- `status`—Filter by finding status. This example returns OPEN findings that have not yet been addressed.
- `resource.iacPlatform`—Filter by IaC platform type. This example returns findings from Terraform files.
- `resource.cloudPlatform`—Filter by target cloud platform. This example returns findings on AWS resources.
- `orderBy`—Sort results by a specific field. This example sorts by `ANALYZED_AT` in descending order.

See the [Get IaC Findings API](dev:get-iac-findings) reference for more information and to refine your query.

```json Example query
{
  "query": "query IaCFindingsTable($filterBy: IaCFindingFilters, $orderBy: IaCFindingOrder, $after: String, $first: Int) { iacFindings(filterBy: $filterBy after: $after first: $first orderBy: $orderBy) { nodes { ...IaCFinding } pageInfo { endCursor hasNextPage } totalCount } } fragment IaCFinding on IaCFinding { id name expectedContent foundContent matchContent status severity firstSeenAt lastSeenAt filePath startLine endLine platform cloudPlatform fileURL vcsPlatform remediationInstructions fileRemediation { filePath } resourceGraphEntity { providerUniqueId id type name properties } repository { id name } branch { id name } rule { ...CloudConfigurationFindingRule risks threats } } fragment CloudConfigurationFindingRule on CloudConfigurationRule { cloudProvider id shortId name serviceType builtin subjectEntityType description enabled severity targetNativeTypes supportsNRT originalConfigurationRuleOverridden control { lastSuccessfulRunAt id originalControl { id severity } likelihoodSeverity impactSeverity } scopeProject { id name slug isFolder riskProfile { businessImpact } } tags { key value } opaPolicy iacMatchers { id type remediationInstructions } securitySubCategories { id title category { id } } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "severity": {
        "equals": ["CRITICAL", "HIGH"]
      },
      "status": {
        "equals": ["OPEN"]
      },
      "resource": {
        "iacPlatform": {
          "equals": ["TERRAFORM"]
        },
        "cloudPlatform": {
          "equals": ["AWS"]
        }
      }
    },
    "orderBy": {
      "field": "ANALYZED_AT",
      "direction": "DESC"
    }
  }
}
```

A successful request returns the specified number of IaC findings according to the requested fields.

:::success

Done!

:::
