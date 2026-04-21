# Pull Hosted Technologies Tutorial
*Learn how to pull hosted technologies from Wiz using an API query with filters for technology type and cloud platform.*

Category: hosted-tech

In this tutorial, learn how to pull hosted technologies detected by Wiz in your cloud environment.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read:inventory`

### Pull hosted technologies

Execute the `HostedTechnologiesTable` query to return a list of hosted technologies according to different filters.

The following query returns the first five hosted technologies, where:

- `first`—Pagination value that determines the number of results per page. You must include a value or the API call fails. This example returns the first 5 results.
- `resource.cloudPlatform`—Filter the results based on the desired cloud provider(s). This example returns technologies from AWS.
- `technologyV2.category.stackLayer`—Filter by technology stack layer. This example returns technologies in the application and data layer.
- `fetchTotalCount`—Whether to include the total count of hosted technologies in the response.

For more information and to refine your query, see the [Get Hosted Technologies API](dev:pull-hosted-tech) reference.

```json Example query
{
  "query": "query HostedTechnologiesTable($filterBy: HostedTechnologyFilters, $first: Int, $after: String, $fetchTotalCount: Boolean = true) {   hostedTechnologies(filterBy: $filterBy, first: $first, after: $after) {     totalCount @include(if: $fetchTotalCount)     nodes {       id       externalId       name       technology {         id         name         icon         description         categories {           id           name         }         stackLayer         deploymentModel         status         businessModel         supportsTagging         popularity         ownerHeadquartersCountryCode         ownerName         onlyServiceUsageSupported         isSupportedByVendor         isSupportedByCommunity         isGenerallyAvailable         isAppliance         isCloudService         isDataScanSupported         isEndOfLifeSupported         isSensitive         isBillableWorkload         hasApplicationFingerprint         note       }       resource {         id         externalId         name         type         nativeType         cloudPlatform         cloudAccount {           id           externalId           name           cloudProvider         }         region         regionLocation         status         projects {           id           name           slug           isFolder         }         tags {           key           value         }         isOpenToAllInternet         isAccessibleFromInternet         hasAccessToSensitiveData         hasAdminPrivileges         hasHighPrivileges         hasSensitiveData       }       versionDetails {         version         releaseDate         isEndOfLife         isLatest         latestVersion         latestVersionReleaseDate         endOfLifeDate         majorVersion         hasExtendedSupport         edition       }       detectionMethods       installedPackages       firstSeen       updatedAt       deletedAt       configurationScanAnalytics {         successPercentage         failCount         passCount         errorCount         notAssessedCount         totalCount       }       validatedInRuntime       isOfficiallyMaintained       isSystemRestartRequired       evidence {         packageNames         libraryNames         installedProgramNames         windowsServiceNames         filePaths       }     }     pageInfo {       hasNextPage       endCursor     }   } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "resource": {
        "cloudPlatform": ["AWS"]
      },
      "technologyV2": {
        "category": {
          "stackLayer": ["APPLICATION_AND_DATA"]
        }
      }
    },
    "fetchTotalCount": true
  }
}
```

A successful request returns the specified number of hosted technologies according to the requested fields:

```json Example response
{
  "data": {
    "hostedTechnologies": {
      "totalCount": 1247,
      "nodes": [
        {
          "id": "ht-12345",
          "externalId": "ext-ht-12345",
          "name": "Apache HTTP Server",
          "technology": {
            "id": "1001",
            "name": "Apache HTTP Server",
            "icon": "https://assets.wiz.io/technology-icons/apache.svg",
            "description": "The Apache HTTP Server is a free and open-source cross-platform web server software.",
            "categories": [
              {
                "id": "15",
                "name": "Web Servers"
              }
            ],
            "stackLayer": "APPLICATION_AND_DATA",
            "deploymentModel": "SERVER_APPLICATION",
            "status": "SANCTIONED",
            "businessModel": "OPEN_SOURCE",
            "supportsTagging": true,
            "popularity": "VERY_COMMON",
            "ownerHeadquartersCountryCode": "US",
            "ownerName": "Apache Software Foundation",
            "onlyServiceUsageSupported": false,
            "isSupportedByVendor": true,
            "isSupportedByCommunity": true,
            "isGenerallyAvailable": true,
            "isAppliance": false,
            "isCloudService": false,
            "isDataScanSupported": true,
            "isEndOfLifeSupported": true,
            "isSensitive": false,
            "isBillableWorkload": true,
            "hasApplicationFingerprint": true,
            "note": null
          },
          "resource": {
            "id": "res-67890",
            "externalId": "i-0123456789abcdef0",
            "name": "web-server-01",
            "type": "VIRTUAL_MACHINE",
            "nativeType": "instance",
            "cloudPlatform": "AWS",
            "cloudAccount": {
              "id": "acc-12345",
              "externalId": "123456789012",
              "name": "Production Account",
              "cloudProvider": "AWS"
            },
            "region": "us-east-1",
            "regionLocation": "US East (N. Virginia)",
            "status": "Active",
            "projects": [
              {
                "id": "proj-123",
                "name": "Web Services",
                "slug": "web-services",
                "isFolder": false
              }
            ],
            "tags": [
              {
                "key": "Environment",
                "value": "Production"
              }
            ],
            "isOpenToAllInternet": false,
            "isAccessibleFromInternet": true,
            "hasAccessToSensitiveData": false,
            "hasAdminPrivileges": false,
            "hasHighPrivileges": false,
            "hasSensitiveData": false
          },
          "versionDetails": {
            "version": "2.4.41",
            "releaseDate": "2019-08-14T00:00:00Z",
            "isEndOfLife": false,
            "isLatest": false,
            "latestVersion": "2.4.58",
            "latestVersionReleaseDate": "2023-10-19T00:00:00Z",
            "endOfLifeDate": null,
            "majorVersion": "2.4",
            "hasExtendedSupport": false,
            "edition": "Standard"
          },
          "detectionMethods": ["PACKAGE_MANAGER", "PROCESS_ANALYSIS"],
          "installedPackages": ["apache2", "apache2-utils"],
          "firstSeen": "2023-01-15T10:30:00Z",
          "updatedAt": "2023-12-01T14:22:00Z",
          "deletedAt": null,
          "configurationScanAnalytics": {
            "successPercentage": 85.5,
            "failCount": 2,
            "passCount": 12,
            "errorCount": 1,
            "notAssessedCount": 0,
            "totalCount": 15
          },
          "validatedInRuntime": true,
          "isOfficiallyMaintained": true,
          "isSystemRestartRequired": false,
          "evidence": {
            "packageNames": ["apache2"],
            "libraryNames": ["libapache2-mod-php"],
            "installedProgramNames": ["httpd"],
            "windowsServiceNames": [],
            "filePaths": ["/etc/apache2/apache2.conf"]
          }
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "eyJmaWVsZHMiOlt7IkZpZWxkIjoiaWQiLCJWYWx1ZSI6Imh0LTEyMzQ1In1dfQ=="
      }
    }
  }
}
```

## Next step

That's the end of the tutorial. Now, check out the [Get Hosted Technologies](dev:pull-hosted-tech) API.
