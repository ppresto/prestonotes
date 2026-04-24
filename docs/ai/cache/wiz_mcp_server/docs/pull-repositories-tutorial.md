# Pull Version Control Repositories Tutorial
*Learn how to pull version control repositories from Wiz using an API query with filters for VCS type and branch.*

Category: version-control-repositories

In this tutorial, learn how to pull version control resources such as repository branches detected by Wiz.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read:resources`

### Pull repositories

Execute the [`VersionControlResources`](dev:pull-repositories) query to return a list of repository branches detected by Wiz according to different filters.

The following example query returns the first five repository branches, where:

- `first`—Pagination value that determines the number of results per page. You must include a value or the API call fails. In this example, it returns the first 5 results.
- `type`—Is set to `REPOSITORY_BRANCH`.

```json Example query
query VersionControlResources($first: Int, $after: String, $filterBy: VersionControlResourceFilters) {
  versionControlResources(first: $first, after: $after, filterBy: $filterBy) {
    nodes {
      id
      cloudPlatform
      providerID
      type
      repository {
        id
        name
        url
      }
    }
  }
}
"variables": {
    "first": 5,
    "filterBy": {
      "type": [
        "REPOSITORY_BRANCH"
      ]
  }
}
```

A successful request returns the specified number of detected repository branches according to the requested fields.

:::success

Done!

:::
