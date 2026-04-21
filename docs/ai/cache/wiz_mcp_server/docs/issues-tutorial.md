# Pull Issues Using Delta Updates Tutorial
*Learn how to pull Issues from Wiz using delta updates with filters for severity, status, and project.*

Category: issues

To maintain efficiency and achieve WIN certification, implement a delta update strategy. This method ensures you retrieve the most current and relevant Issues while minimizing unnecessary data transfer and processing.

In this tutorial, you'll learn how to pull Issues using the [Pull Issues](dev:issues-query) API and implement delta updates in your Issues management system.

## How delta updates work

Delta updates allow you to pull only the Issues that have changed since your last export. You can accomplish this by using the `statusChangedAt` filter in your GraphQL queries to capture all changes, including:

- Newly opened Issues
- Issues whose status changed
- Recently resolved Issues
- Ignored Issues
- In-progress Issues

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `read: Issues`

## Implementation

The following example query retrieves critical and high severity Issues whose status changed after the specified timestamp:

```json Example

  "query": "query IssuesTable($filterBy: IssueFilters, $first: Int, $after: String, $orderBy: IssueOrder) { issues: issuesV2( filterBy: $filterBy first: $first after: $after orderBy: $orderBy ) { nodes { id sourceRule { __typename ... on Control { id name controlDescription: description resolutionRecommendation securitySubCategories { title category { name framework { name } } } risks } ... on CloudEventRule { id name cloudEventRuleDescription: description sourceType type risks securitySubCategories { title category { name framework { name } } } } ... on CloudConfigurationRule { id name cloudConfigurationRuleDescription: description remediationInstructions serviceType risks securitySubCategories { title category { name framework { name } } } } } createdAt updatedAt dueAt type resolvedAt statusChangedAt projects { id name slug businessUnit riskProfile { businessImpact } } status severity entitySnapshot { id type nativeType name status cloudPlatform cloudProviderURL providerId region resourceGroupExternalId subscriptionExternalId subscriptionName subscriptionTags tags createdAt externalId } serviceTickets { externalId name url } notes { createdAt updatedAt text user { name email } serviceAccount { name } } } pageInfo { hasNextPage endCursor } } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "statusChangedAt": {
        "after": "2024-10-22T07:30:28.924Z"
      },
      "severity": [
        "CRITICAL",
        "HIGH"
      ]
    }
  }

```

Key parameters:

- `filterBy`: An object containing filtering criteria:
  - `statusChangedAt.after`: Filters Issues based on their update timestamp. Only includes Issues updated after the specified ISO 8601 timestamp. The filter `statusChangedAt.before` is also available to pull Issues updated before the specified date.
  - `severity`: Filter Issues by the severity of the rule which triggered the Issue. In this example, it's set to filter for critical and high severity rules.

:::success[Done! You have pulled Issues using the Pull Issues API]

:::

## Best practices

We recommend implementing these best practices for your integration:

**Use time-based filtering**

- Use the `statusChangedAt` filter in your GraphQL query variables.
- Set the timestamp to retrieve changes from the last successful run.
- Ensure timestamps are in ISO 8601 format with UTC timezone.

**Track the last successful run**

- Store the timestamp of your last successful integration run.
- Use this stored timestamp for subsequent queries.
- This approach ensures no updates are missed, even if your integration doesn't run exactly every 24 hours.

**Handle pagination**

- Use the `pageInfo` object to handle large result sets.
- Track the `endCursor` for subsequent requests.
- Check `hasNextPage` to determine if more results are available.

## Next steps

- [See Pull Issues API reference](dev:issues-query)
- [See certification process](dev:certification-process)
