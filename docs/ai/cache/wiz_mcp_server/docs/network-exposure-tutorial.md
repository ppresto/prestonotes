# Pull Exposed Resources Tutorial
*Learn how to pull exposed resources from Wiz with filters for exposure type and cloud platform.*

Category: exposed-resources

In this tutorial, learn how to pull exposed resources.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:network_exposure` permission.

### Pull exposed resources

Execute the [`NetworkExposuresTable`](dev:pull-network-exposure) query to return a list of exposed resources according to different filters.

The following query returns the first five exposed resources where:

- `first`—Pagination value that determines the number of results per page. You must include a value, or the API call fails. In this example, it returns the first 5 results.
- `exposedEntity.type`—Filter by specific resource types. This example returns bucket resources.
- `publicInternetExposureFilters.hasApplicationEndpoint`—Filter external exposures with/without an application endpoint. This example returns results with an application endpoint.
- `type`—Filter by network exposure type. This example returns results for resources exposed to the public internet.

```json Example query
{
  "query": "query NetworkExposuresTable($filterBy: NetworkExposureFilters, $first: Int, $after: String) {   networkExposures(filterBy: $filterBy, first: $first, after: $after) {     nodes {       id       exposedEntity {         id         name         type         properties       }       accessibleFrom {         id         name         type         properties       }       sourceIpRange       destinationIpRange       portRange       appProtocols       networkProtocols       path {         id         name         type         properties       }       customIPRanges {         id         name         ipRanges       }       firstSeenAt       applicationEndpoints {         id         name         type         properties       }       type     }     pageInfo {       hasNextPage       endCursor     }     totalCount   } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "exposedEntity": {
        "type": ["BUCKET"]
      },
      "publicInternetExposureFilters": {
        "hasApplicationEndpoint": true
      },
      "type": ["PUBLIC_INTERNET"]
    }
  }
}
```

A successful request returns the specified number of network exposures according to the requested fields.

:::success

Done!

:::
