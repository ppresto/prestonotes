# Pull Secret Findings Tutorial
*Learn how to pull Secret Findings from Wiz using an API query with filters for secret type and severity.*

Category: secret-findings

This tutorial will teach you how to use the [Get Secret Findings](dev:get-secret-findings) API. You'll learn how to filter, sort, and retrieve secret findings data to identify exposed credentials across your cloud environment.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read:secret_instances`

## Basic query

Here's a basic example that retrieves the first 10 secret findings:

```json Example
{
  "query": "query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) { secretInstances(filterBy: $filterBy first: $first after: $after orderBy: $orderBy) { nodes { id name type confidence severity isEncrypted isManaged externalId status firstSeenAt lastSeenAt lastModifiedAt lastUpdatedAt resolvedAt validationStatus passwordDetails { isComplex length entropy } rule { id name type validityCheckSupported isAiPowered } projects { id name slug isFolder } secretDataEntities { id name type } relatedIssueAnalytics { issueCount informationalSeverityCount lowSeverityCount mediumSeverityCount highSeverityCount criticalSeverityCount } resource { ...SecretFindingResourceDetails cloudAccount { id externalId name cloudProvider } tags { key value } } } pageInfo { hasNextPage endCursor } totalCount @include(if: $fetchTotalCount) } } fragment SecretFindingResourceDetails on SecretInstanceResource { id name type externalId status nativeType region typedProperties { ... on SecretInstanceResourceRepositoryBranch { repository { id name } } } }",
  "variables": {
    "first": 10,
    "orderBy": {
      "field": "RELATED_ISSUE_SEVERITY",
      "direction": "DESC"
    }
  }
}
```

Key parameters:

- `first`: The number of results to return (maximum 500).
- `orderBy`: Specifies the sorting criteria for the results:
  - `field`: The field to sort by, set to "RELATED_ISSUE_SEVERITY".
  - `direction`: The sort direction, set to "DESC" (descending order).

## Filter by secret type

This example shows how to filter secret findings by specific secret types:

```json Example
{
  "query": "query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) { secretInstances(filterBy: $filterBy first: $first after: $after orderBy: $orderBy) { nodes { id name type confidence severity isEncrypted isManaged externalId status firstSeenAt lastSeenAt lastModifiedAt lastUpdatedAt resolvedAt validationStatus passwordDetails { isComplex length entropy } rule { id name type validityCheckSupported isAiPowered } projects { id name slug isFolder } secretDataEntities { id name type } relatedIssueAnalytics { issueCount informationalSeverityCount lowSeverityCount mediumSeverityCount highSeverityCount criticalSeverityCount } resource { ...SecretFindingResourceDetails cloudAccount { id externalId name cloudProvider } tags { key value } } } pageInfo { hasNextPage endCursor } totalCount @include(if: $fetchTotalCount) } } fragment SecretFindingResourceDetails on SecretInstanceResource { id name type externalId status nativeType region typedProperties { ... on SecretInstanceResourceRepositoryBranch { repository { id name } } } }",
  "variables": {
    "first": 20,
    "filterBy": {
      "type": {
        "equals": ["CLOUD_KEY", "SAAS_API_KEY", "PRIVATE_KEY"]
      },
      "severity": {
        "equals": ["CRITICAL", "HIGH"]
      }
    },
    "orderBy": {
      "field": "SEVERITY",
      "direction": "DESC"
    }
  }
}
```

Key parameters:

- `filterBy`: An object containing filtering criteria:
  - `type.equals`: Filters secret findings by specific secret types (Cloud Keys, SaaS API Keys, Private Keys).
  - `severity.equals`: Filters by severity levels (Critical and High only).

## Filter by validation status

This example shows how to filter secret findings by their validation status:

```json Example
{
  "query": "query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) { secretInstances(filterBy: $filterBy first: $first after: $after orderBy: $orderBy) { nodes { id name type confidence severity isEncrypted isManaged externalId status firstSeenAt lastSeenAt lastModifiedAt lastUpdatedAt resolvedAt validationStatus passwordDetails { isComplex length entropy } rule { id name type validityCheckSupported isAiPowered } projects { id name slug isFolder } secretDataEntities { id name type } relatedIssueAnalytics { issueCount informationalSeverityCount lowSeverityCount mediumSeverityCount highSeverityCount criticalSeverityCount } resource { ...SecretFindingResourceDetails cloudAccount { id externalId name cloudProvider } tags { key value } } } pageInfo { hasNextPage endCursor } totalCount @include(if: $fetchTotalCount) } } fragment SecretFindingResourceDetails on SecretInstanceResource { id name type externalId status nativeType region typedProperties { ... on SecretInstanceResourceRepositoryBranch { repository { id name } } } }",
  "variables": {
    "first": 15,
    "filterBy": {
      "validationStatus": {
        "equals": ["VALID"]
      },
      "status": {
        "equals": ["OPEN"]
      }
    },
    "orderBy": {
      "field": "VALIDATION_STATUS",
      "direction": "DESC"
    }
  }
}
```

Key parameters:

- `validationStatus.equals`: Filters secret findings by validation status (Valid secrets only).
- `status.equals`: Filters by finding status (Open findings only).

## Filter by resource type and code repository

This example shows how to filter secret findings by resource type and specific code repository:

```json Example
{
  "query": "query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) { secretInstances(filterBy: $filterBy first: $first after: $after orderBy: $orderBy) { nodes { id name type confidence severity isEncrypted isManaged externalId status firstSeenAt lastSeenAt lastModifiedAt lastUpdatedAt resolvedAt validationStatus passwordDetails { isComplex length entropy } rule { id name type validityCheckSupported isAiPowered } projects { id name slug isFolder } secretDataEntities { id name type } relatedIssueAnalytics { issueCount informationalSeverityCount lowSeverityCount mediumSeverityCount highSeverityCount criticalSeverityCount } resource { ...SecretFindingResourceDetails cloudAccount { id externalId name cloudProvider } tags { key value } } } pageInfo { hasNextPage endCursor } totalCount @include(if: $fetchTotalCount) } } fragment SecretFindingResourceDetails on SecretInstanceResource { id name type externalId status nativeType region typedProperties { ... on SecretInstanceResourceRepositoryBranch { repository { id name } } } }",
  "variables": {
    "first": 25,
    "filterBy": {
      "resourceType": {
        "equals": ["VIRTUAL_MACHINE", "CONTAINER_IMAGE", "REPOSITORY"]
      },
      "codeRepository": {
        "equals": ["e0afa51c-9a71-5a42-86b1-e09fd101ae3a"]
      }
    },
    "orderBy": {
      "field": "TYPE",
      "direction": "ASC"
    }
  }
}
```

Key parameters:

- `resourceType.equals`: Filters secret findings by resource types (VMs, Container Images, Repositories).
- `codeRepository.equals`: Filters by specific code repository ID.

## Pull Secret Findings using delta updates

Using a delta update strategy ensures you retrieve only the most current and relevant findings, and minimizes unnecessary data transfer and processing.

You can implement a delta strategy by using the `lastUpdatedAt` filter in your GraphQL queries to capture changes incrementally, including:

- Newly opened Secret Findings
- Secret Findings whose status has changed
- Recently resolved Secret Findings
- Ignored Secret Findings
- Modified Secret Finding information

The following example query:

- Pulls only Secret Findings that were updated since the specified date.
- Retrieves Secret Findings whose status is either open or resolved.
- Captures updates to the resource object (relevant to the finding) or to the finding itself (including severity changes, validation status changes, or resource deletion).

You can further refine your query based on the available fields and variables in the [Get Secret Findings API reference](./get-secret-findings).

```json Example request
{
  "query": "query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) { secretInstances(filterBy: $filterBy first: $first after: $after orderBy: $orderBy) { nodes { id name type confidence severity isEncrypted isManaged externalId status firstSeenAt lastSeenAt lastModifiedAt lastUpdatedAt resolvedAt validationStatus passwordDetails { isComplex length entropy } rule { id name type validityCheckSupported isAiPowered } projects { id name slug isFolder } secretDataEntities { id name type } relatedIssueAnalytics { issueCount informationalSeverityCount lowSeverityCount mediumSeverityCount highSeverityCount criticalSeverityCount } resource { ...SecretFindingResourceDetails cloudAccount { id externalId name cloudProvider } tags { key value } } } pageInfo { hasNextPage endCursor } totalCount @include(if: $fetchTotalCount) } } fragment SecretFindingResourceDetails on SecretInstanceResource { id name type externalId status nativeType region typedProperties { ... on SecretInstanceResourceRepositoryBranch { repository { id name } } } }",
  "variables": {
    "first": 10,
    "filterBy": {
      "lastUpdatedAt": {
        "after": "2025-11-15T00:00:00.000Z"
      },
      "status": {
        "equals": ["OPEN", "RESOLVED"]
      }
    },
    "orderBy": {
      "field": "CREATED_AT",
      "direction": "DESC"
    }
  }
}
```

Key filter parameters:

- `lastUpdatedAt.after`: Filters secret findings updated after the specified timestamp (ISO 8601 format).
- `status.equals`: Filters by finding status (Open and Resolved findings).
- `orderBy.field`: Sorts results by creation date in descending order.

:::success

Done! You have learned how to query Secret Findings using the API, including how to pull findings incrementally

:::

## Next steps

- [See Get Secret Findings API reference](./get-secret-findings)
