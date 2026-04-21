# Update Issue Tutorial
*Learn how to update Issue status, add comments, and manage Issue notes using the WIN API.*

Category: issues

In this tutorial, learn how to update Wiz Issues.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `update:write:issue_due_at`
  - `write:issue_status`
  - `write:service_ticket`
  - `write:issue_comments`

### Update Issue

Execute the [`UpdateIssue`](dev:update-issues) mutation to update a specific Issue in the Wiz environment. You can modify various properties including status, due date, and add notes.

:::info[Issue Status: REJECTED vs. RESOLVED]

- **REJECTED**: Use when manually marking an Issue as not requiring action (false positive, exception, won't fix). You must provide a `resolutionReason` when setting status to REJECTED.
- **RESOLVED**: Resolution behavior varies by Issue type:
  - **Graph Control and Cloud Configuration Issues**: Only Wiz can resolve these automatically during scan cycles when it detects the risks have been remediated.
  - **Threat Detection Issues**: These can be resolved manually or will auto-resolve after 90 days with no new detections. You must provide a `resolutionReason` when setting status to RESOLVED. [Learn more about Threat Detection Issue resolution](dev:threats-and-detections#managing-threat-resolution).

:::

The following mutation updates an Issue, where:

- `issueId`—The unique identifier of the Issue to update (required)
- `patch`—Object containing the properties to update
- `status`—Updated status value
- `resolutionReason`—Reason for rejection
- `dueAt`—Date when the Issue is due to be resolved (ISO 8601 format)
- `note`—Additional information about the Issue

```json Example: Update Issue Status
{
  "query": "mutation UpdateIssue($issueId: ID!, $patch: UpdateIssuePatch, $override: UpdateIssuePatch) { updateIssue(input: { id: $issueId, patch: $patch, override: $override }) { issue { id note status dueAt resolutionReason } } }",
  "variables": {
    "issueId": "842ec39e-b907-4c32-b6e5-2c3dd9fd43c0",
    "patch": {
      "status": "IN_PROGRESS"
    }
  }
}
```

```json Example: Reject an Issue with Reason
{
  "query": "mutation UpdateIssue($issueId: ID!, $patch: UpdateIssuePatch, $override: UpdateIssuePatch) { updateIssue(input: { id: $issueId, patch: $patch, override: $override }) { issue { id note status dueAt resolutionReason } } }",
  "variables": {
    "issueId": "842ec39e-b907-4c32-b6e5-2c3dd9fd43c0",
    "patch": {
      "status": "REJECTED",
      "resolutionReason": "FALSE_POSITIVE",
      "note": "This is a false positive because..."
    }
  }
}
```

```json Example: Set Issue Due Date
{
  "query": "mutation UpdateIssue($issueId: ID!, $patch: UpdateIssuePatch, $override: UpdateIssuePatch) { updateIssue(input: { id: $issueId, patch: $patch, override: $override }) { issue { id note status dueAt resolutionReason } } }",
  "variables": {
    "issueId": "842ec39e-b907-4c32-b6e5-2c3dd9fd43c0",
    "patch": {
      "dueAt": "2023-12-31T23:59:59Z"
    }
  }
}
```

A successful request returns the updated Issue with all the requested fields.

```json Response Example
{
  "data": {
    "updateIssue": {
      "issue": {
        "id": "842ec39e-b907-4c32-b6e5-2c3dd9fd43c0",
        "note": "This is a test note",
        "status": "IN_PROGRESS",
        "dueAt": "2023-12-31T23:59:59Z",
        "resolutionReason": null
      }
    }
  }
}
```

:::success

Done!

:::
