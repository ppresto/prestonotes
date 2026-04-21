# Audit Logs Tutorial
*Learn how to pull Wiz Audit Logs using the AuditLogTable query with filters for status, user type, timestamp, and action.*

Category: audit-logs

In this tutorial, learn how to pull Wiz Audit Logs.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the `admin:audit` permission

### Pull Audit Logs

Execute the `AuditLogTable` query to return a list of Audit Log events according to different filters, such as type of user, action, or date.

The following query returns the first five Audit Logs, where:

- `first`—Pagination value that determines the number of results per page. You must include a value or the API call fails. In this example, it returns the first 5 results.
- `status`—Filter the results based on the Audit Log event status. This example returns events that were denied access.
- `userType`—Filter Audit Logs entries by the type of user. This example returns events for Wiz service accounts.
- `timestamp.after`—Filter for Audit Log entries created after the specified date period.
- `action`—Filter Audit Log entries by a specific action type. This example returns "login" events.

See the [Get Audit Log API](dev:audit-log) reference for more information and to refine your query.

```json Example query
{
  "query": "query AuditLogTable($first: Int $after: String $filterBy: AuditLogEntryFilters){     auditLogEntries(first: $first after: $after filterBy: $filterBy) {       nodes {         id         action         requestId         status         timestamp         actionParameters         userAgent         sourceIP         serviceAccount {           id           name         }         user {           id           name         }       }       pageInfo {         hasNextPage         endCursor       }     }   }",
  "variables": {
    "first": 5,
    "filterBy": {
      "status": ["ACCESS_DENIED"],
      "userType": ["SERVICE_ACCOUNT"],
      "timestamp": {
        "after": "2022-09-01T11:28:07.404058Z"
      },
      "action": "login"
    }
  }
}
```

A successful request returns the specified number of open Audit Log events according to the requested fields.

:::success

Done!

:::
