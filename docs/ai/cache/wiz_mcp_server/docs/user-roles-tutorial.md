# Pull User Roles Tutorial
*Learn how to pull user roles from Wiz using the userRoles query with filters for role type and permissions.*

Category: users

In this tutorial, learn how to retrieve user roles from your Wiz environment using the Wiz API. User roles define the permissions and access levels that can be assigned to users in your organization.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `read:users` permission

## Retrieve User Roles

Execute the [`UserRolesTable`](dev:get-user-roles) query to return a list of user roles and their associated information, such as name, description, scopes, and permissions.

### Basic query

The following query retrieves all user roles in your environment:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {}
  }
}
```

### Filter by role type

<Expandable title="Get only built-in roles">

Use the `builtin` filter to retrieve only system-defined roles:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "builtin": true
    }
  }
}
```

Key parameters:

- `builtin: true`: Returns only built-in system roles
- `builtin: false`: Returns only custom user-created roles

</Expandable>

<Expandable title="Get only custom roles">

Use the `builtin` filter set to `false` to retrieve only user-created custom roles:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "builtin": false
    }
  }
}
```

This is useful for auditing custom roles created by your organization.

</Expandable>

### Filter by scope type

<Expandable title="Get project-scoped roles">

Use the `isProjectScoped` filter to retrieve roles that are limited to specific projects:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "isProjectScoped": true
    }
  }
}
```

Key parameters:

- `isProjectScoped: true`: Returns only project-scoped roles
- `isProjectScoped: false`: Returns only global roles

</Expandable>

<Expandable title="Get global roles">

Use the `isProjectScoped` filter set to `false` to retrieve roles that apply across all projects:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "isProjectScoped": false
    }
  }
}
```

Global roles are typically used for organization-wide permissions.

</Expandable>

### Filter by permission level

<Expandable title="Get roles with specific permissions">

Use the `scopePermission` filter to find roles that contain specific permission levels:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "scopePermission": ["admin", "read"]
    }
  }
}
```

Available permission levels:

- `admin`: Administrative permissions (full control)
- `read`: Read-only permissions
- `update`: Update/modify permissions
- `create`: Create new resources permissions
- `delete`: Delete resources permissions
- `write`: Write/modify permissions (broader than update)

</Expandable>

### Combined filters

<Expandable title="Get built-in project-scoped admin roles">

Combine multiple filters to get very specific results:

```json Example
{
  "query": "query UserRolesTable($filterBy: UserRoleFilters) { userRolesV2(filterBy: $filterBy) { id name description scopes builtin isProjectScoped updatedAt updatedBy { id name } createdAt createdBy { id name } } }",
  "variables": {
    "filterBy": {
      "builtin": true,
      "isProjectScoped": true,
      "scopePermission": ["admin"]
    }
  }
}
```

This query returns built-in roles that are project-scoped and contain administrative permissions.

</Expandable>

:::success

You've successfully learned how to retrieve user roles using the Wiz API! You can now query roles by type, scope, and permissions to understand your organization's access control structure.

:::

## Next Steps

- [Get User Roles API Reference](dev:get-user-roles) - Complete API documentation
- [Pull Users Tutorial](dev:user-management-tutorial) - Learn how to retrieve user information
- [Pull Service Accounts Tutorial](dev:service-accounts-tutorial) - Manage service account access
- [Get Service Accounts API Reference](dev:get-service-accounts) - Complete API documentation
