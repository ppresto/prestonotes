# Pull Projects Tutorial
*Learn how to pull Projects from Wiz using the projects query with filters for project name and hierarchy.*

Category: projects

In this tutorial, learn how to pull Wiz Projects.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:projects` permission

## Pull Projects

Execute the `ProjectsTable` query to return a list of the Wiz Projects customers have created in their respective tenants.

:::info[Project-scoped integrations]

For project-scoped integrations, you must specify which Projects the integration can access using the Project filter. For more information, see [Project-scoped integrations](dev:projects#project-scoped-integrations).

:::

The following query returns the first five Projects, where:

- `first`—Pagination value that determines the number of results per page. You must include a value, or the API call fails. In this example, it returns the first 5 results.
- `includeArchived`—Filter Projects that are/are not archived.
- `isFolder`—Filter Projects that are/are not Folder Projects.
- `root`—Determines whether to include top-level Projects.
- `impact`—Filter by business impact.
- `field`—The type of field to order the results by.
- `direction`—The order direction.
- `ancestorProjects` - The project's ancestors, starting from the direct parent till the furthest ancestor.

See the [Pull Projects API](dev:pull-projects) reference for more information and to refine your query.

```json Example query
{
  "query": "query ProjectsTable($filterBy: ProjectFilters, $first: Int, $after: String, $orderBy: ProjectOrder) {   projects(filterBy: $filterBy, first: $first, after: $after, orderBy: $orderBy) {     nodes {       id       name       isFolder       archived       businessUnit       description     }}}",
  "variables": {
    "first": 5,
    "filterBy": {
      "includeArchived": false,
      "isFolder": false,
      "root": false,
      "impact": "MBI"
    },
    "orderBy": {
      "field": "BUSINESS_IMPACT",
      "direction": "ASC"
    }
  }
}
```

A successful request returns the specified number of Projects according to the requested fields.

:::success

Done!

:::
