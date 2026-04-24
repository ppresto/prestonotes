# Service Accounts Management Tutorial
*Learn how to pull service accounts from Wiz using the Get Service Accounts API with filters for scope and project assignment.*

Category: users

This tutorial will teach you how to retrieve service accounts using the Wiz API.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read:service_accounts`

### Retrieve service accounts

This step shows you how to retrieve a list of service accounts in your environment using the [`ServiceAccountsTable`](dev:get-service-accounts) query. You can filter by type, status, and other criteria.

Example requests:

<Expandable title="Get all active service accounts">

```json Example
{
  "query": "query ServiceAccountsTable($first: Int, $after: String, $filterBy: ServiceAccountFilters, $orderBy: ServiceAccountOrder) { serviceAccounts(first: $first, after: $after, filterBy: $filterBy, orderBy: $orderBy) { nodes { id enabled name clientId scopes lastRotatedAt expiresAt description integration { id name typeConfiguration { type iconUrl } } type lastLoginAt deletedAt createdAt createdBy { id name email } updatedAt updatedBy { id email } assignedProjects { id name } internal } pageInfo { hasNextPage endCursor } totalCount } }",
  "variables": {
    "first": 20,
    "filterBy": {
      "enabled": true,
      "deleted": false
    },
    "orderBy": {
      "field": "NAME",
      "direction": "ASC"
    }
  }
}
```

Key parameters:

- `enabled`: Filter by whether the service account is enabled or disabled
- `deleted`: Filter by whether the service account is deleted
- `first`: The number of results to return (pagination)
- `orderBy`: Sort results by field (NAME, CREATED_AT, UPDATED_AT) and direction (ASC, DESC)

</Expandable>

<Expandable title="Get service accounts by type">

```json Example
{
  "query": "query ServiceAccountsTable($first: Int, $after: String, $filterBy: ServiceAccountFilters, $orderBy: ServiceAccountOrder) { serviceAccounts(first: $first, after: $after, filterBy: $filterBy, orderBy: $orderBy) { nodes { id enabled name clientId scopes type createdAt lastLoginAt assignedProjects { id name } } pageInfo { hasNextPage endCursor } totalCount } }",
  "variables": {
    "first": 50,
    "filterBy": {
      "type": [
        "THIRD_PARTY",
        "SENSOR"
      ],
      "enabled": true
    }
  }
}
```

Key parameters:

- `type`: Filter service accounts by type. Available types:
  - `THIRD_PARTY`: Custom Integration (GraphQL API) service accounts
  - `SENSOR`: Runtime Sensor service accounts
  - `KUBERNETES_ADMISSION_CONTROLLER`: Admission Controller service accounts
  - `BROKER`: Wiz Broker service accounts
  - `KUBERNETES_CONNECTOR`: Kubernetes Connector service accounts
  - `FIRST_PARTY`: First-party integrations
  - `INTEGRATION`: Built-in integrations
  - `WIZ_AI_AGENT`: Wiz AI Agent service accounts

</Expandable>

<Expandable title="Get service accounts with time-based filters">

```json Example
{
  "query": "query ServiceAccountsTable($first: Int, $after: String, $filterBy: ServiceAccountFilters, $orderBy: ServiceAccountOrder) { serviceAccounts(first: $first, after: $after, filterBy: $filterBy, orderBy: $orderBy) { nodes { id name clientId scopes lastRotatedAt expiresAt lastLoginAt createdAt } pageInfo { hasNextPage endCursor } totalCount } }",
  "variables": {
    "first": 20,
    "filterBy": {
      "createdAt": {
        "after": "2024-01-01T00:00:00.000Z"
      },
      "lastLoginAt": {
        "after": "2024-10-01T00:00:00.000Z"
      },
      "expiresAt": {
        "before": "2025-12-31T23:59:59.000Z"
      }
    },
    "orderBy": {
      "field": "CREATED_AT",
      "direction": "DESC"
    }
  }
}
```

Key parameters:

- `createdAt`: Filter by service account creation time
- `lastLoginAt`: Filter by service account last login time
- `expiresAt`: Filter by service account expiration time
- `lastRotatedAt`: Filter by credentials last rotation time

All time filters support `after` and `before` properties with ISO 8601 format timestamps.

</Expandable>

:::success[Done! You have retrieved service accounts using the ServiceAccountsTable query]

:::

## Next steps

- [See Get Service Accounts API reference](dev:get-service-accounts)
- [See Service Accounts API reference](dev:users)
