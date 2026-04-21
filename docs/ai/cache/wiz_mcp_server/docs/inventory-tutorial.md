# Pull Cloud Resources Tutorial
*Learn how to pull cloud resources from Wiz using the graphSearch query with filters for resource type, cloud platform, and subscription.*

Category: cloud-resource-inventory

Pulling cloud resources extends Wiz's capabilities to retrieve detailed information about your cloud assets, enabling you to understand their configurations, relationships, and potential security risks. This allows you to discover, assess, and manage your cloud inventory effectively.

## How to Pull Cloud Resources

This tutorial outlines how to use the [`CloudResourcesTable`](dev:pull-cloud-resources-v2) query to retrieve a list of cloud resources based on specified filters.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:resources` permission.

### Pull Cloud Resources

Execute the `CloudResourcesTable` query to return a list of cloud resources according to different filters.

The following query returns the first five cloud resources where:

- `first`—Pagination value that determines the number of results per page. You must include a value, or the API call fails. In this example, it returns the first 5 results.
- `cloudPlatform`—Filter by specific cloud provider. This example returns resources from AWS.
- `hasAdminPrivileges`—Filter resources that possess administrative privileges. This example returns resources with admin privileges.
- `hasSensitiveData`—Filter resources that contain sensitive data. This example returns resources with sensitive data.
- `isAccessibleFromInternet`—Filter resources that are accessible from the public internet. This example returns resources accessible from the internet.

```json Example query
{
  "query": "query CloudResourcesTable($first: Int, $after: String, $filterBy: CloudResourceV2Filters, $orderBy: CloudResourceOrder, $fetchTotalCount: Boolean = true) {  cloudResourcesV2(    first: $first    after: $after    filterBy: $filterBy    orderBy: $orderBy  ) {    totalCount: totalServiceUsageResourceCount @include(if: $fetchTotalCount)    pageInfo {      hasNextPage      endCursor    }    nodes {      id      name      externalId      type      technology {        id        name      }      cloudAccount {        id        name        cloudProvider        externalId      }      cloudPlatform      status      region      regionLocation      tags {        key        value      }      projects {        id        name        slug        isFolder      }      createdAt      updatedAt      deletedAt      firstSeen      lastSeen      typeFields {        ... on CloudResourceV2VirtualMachine {          instanceType          operatingSystem        }        ... on CloudResourceV2Database {          kind        }      }      resourceGroup {        id        name      }      isOpenToAllInternet      isAccessibleFromInternet      hasAccessToSensitiveData      hasAdminPrivileges      hasHighPrivileges      hasSensitiveData      nativeType    }  }}",
  "variables": {
    "first": 5,
    "filterBy": {
      "cloudPlatform": {
        "equals": ["AWS"]
      },
      "hasAdminPrivileges": {
        "equals": true
      },
      "hasSensitiveData": {
        "equals": true
      },
      "isAccessibleFromInternet": {
        "equals": true
      }
    },
    "orderBy": {
      "field": "FIRST_SEEN",
      "direction": "DESC"
    }
  }
}
```

A successful request returns the specified number of cloud resources according to the requested fields.

:::success

Done!

:::
