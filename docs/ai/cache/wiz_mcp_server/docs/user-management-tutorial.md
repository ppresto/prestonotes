# Pull Users Tutorial
*Learn how to pull users from Wiz using the Get Users query with filters for role and project assignment.*

Category: users

In this tutorial, learn how to pull Wiz Users.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:users` permission

## Pull Users

Execute the [`UsersTable`](dev:user-management) query to return a list of Wiz users according to different filters, such as type of authentication, role, and assigned projects.

The following query returns the first five users, where:

- `first`—Pagination value that determines the number of results per page. You must include a value, or the API call fails. In this example, it returns the first 5 results.
- `authProviderType`—Filter users by provider type. This example returns users of type Wiz.

You can further refine your query using the available [fields](dev:user-management) and [variables](dev:user-management#variables) to retrieve the users that meet your specific criteria.

```json Example query
{
  "query": "query UsersTable($first: Int $after: String $filterBy: UserFilters) {     users(first: $first after: $after filterBy: $filterBy) {       nodes {         id         name         email         lastLoginAt         deletedAt         createdAt         expiresAt         status         selectedPortalView         identityProviderV2 {           id           name         }         identityProviderTypeV2         effectiveAssignedProjects {           id           name         }         effectiveRole {           id           name           scopes         }       }       pageInfo {         endCursor         hasNextPage       }       totalCount     }   }",
  "variables": {
    "first": 5,
    "filterBy": {
      "authProviderTypeV2": ["WIZ"]
    }
  }
}
```

A successful request returns the specified number of users according to the requested fields.

:::success

Done!

:::
