# Pull Application Endpoints Tutorial
*Learn how to pull Application Endpoints from Wiz using the ApplicationEndpointsTable query with filters for cloud platform, exposure level, and port status.*

Category: app-endpoints

In this tutorial, learn how to pull Application Endpoints from Wiz.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:endpoint_attack_surfaces` permission.

### Pull Application Endpoints

Execute the `ApplicationEndpointsTable` query to return a list of Application Endpoints according to different filters.

The following query returns the first five Application Endpoints where:

- `first`—Pagination value that determines the number of results per page. You must include a value, or the API call fails. In this example, it returns the first 5 results.
- `cloudPlatform.equals`—Filter by specific cloud providers. This example returns endpoints from AWS, Azure, and GCP.
- `exposureLevel.equals`—Filter by exposure level. This example returns endpoints with HIGH and MEDIUM exposure levels.
- `portStatus.equals`—Filter by port status. This example returns endpoints with OPEN ports.
- `hasScreenshot`—Filter by whether the endpoint has a screenshot. This example returns endpoints with screenshots.

See the [Get Application Endpoints API](dev:get-application-endpoints) to further refine your query.

```json Example query
{
  "query": "query ApplicationEndpointsTable($filterBy: ApplicationEndpointFilters, $first: Int, $after: String, $orderBy: ApplicationEndpointOrder) {   applicationEndpoints(filterBy: $filterBy, first: $first, after: $after, orderBy: $orderBy) {     nodes {       id       name       host       port       portStatus       exposureLevel       scanSource       httpStatusCode       hasScreenshot       authenticationMethod       authenticationProvider       technology {         id         name       }       cloudPlatform       cloudAccount {         id         name         externalId       }       resource {         id         name         type       }       firstSeen       updatedAt     }     pageInfo {       hasNextPage       endCursor     }     totalCount   } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "cloudPlatform": {
        "equals": ["AWS", "Azure", "GCP"]
      },
      "exposureLevel": {
        "equals": ["HIGH", "MEDIUM"]
      },
      "portStatus": {
        "equals": ["OPEN"]
      },
      "hasScreenshot": true
    },
    "orderBy": {
      "field": "RELATED_ISSUE_SEVERITY",
      "direction": "DESC"
    }
  }
}
```

A successful request returns the specified number of Application Endpoints according to the requested fields.

:::success

Done!

:::
