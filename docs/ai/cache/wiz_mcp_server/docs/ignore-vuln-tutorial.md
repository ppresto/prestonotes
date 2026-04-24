# Ignore Vulnerability Finding Tutorial
*Learn how to ignore Vulnerability Findings in Wiz using the Ignore Vulnerability Finding API.*

Category: vulnerabilities

To effectively manage your Vulnerability Findings, there might be instances where you need to acknowledge and exclude a specific finding from your remediation efforts. This tutorial outlines how to use the [Ignore Vulnerability Finding](dev:ignore-vulnerability-finding) API to mark a finding as ignored. While the Wiz portal refers to this action as "ignoring" a finding, the underlying API utilizes the status of `REJECTED` to represent this state. You can also use this API to unignore a previously ignored finding. Do this by setting the status to `OPEN`.

The API allows you to ignore one Vulnerability Finding at a time. It can't be used for bulk updates.

## Understanding the ignore action

Ignoring a vulnerability finding allows you to change its status to `REJECTED` and specify a `resolutionReason`, such as `EXCEPTION`. You can also add a `note` to provide context for this action. This is useful for findings that are deemed non-applicable, false positives, or accepted risks within your environment.

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the permission `update:vulnerabilities`

## Implementation

The following are examples of how to ignore a finding and how to unignore a finding.

<Expandable title="Ignore a finding">

Here's an example API mutation to update the status of a vulnerability finding to `REJECTED` with the resolution reason `EXCEPTION` and an associated note:

```json Example
{
  "query": "mutation UpdateVulnerabilityFindingStatus($input: UpdateFindingStatusInput!) { updateVulnerabilityFindingStatus(input: $input) { vulnerabilityFinding { id status resolutionReason note { ...FindingNote } } } }\nfragment FindingNote on VulnerabilityFindingNote { id text createdAt updatedAt user { id email } serviceAccount { id name } }",
  "variables": {
    "input": {
      "status": "OPE",
      "resolutionReason": "EXCEPTION",
      "note": "This finding has been reviewed and is deemed an acceptable risk."
    }
  }
}
```

Key parameters within the `input` object:

- `status`: Set this to `"REJECTED"` to ignore the vulnerability finding.
- `resolutionReason`: Specify the reason for rejecting the finding. Common values include:
  - `FALSE_POSITIVE`: The finding is incorrect.
  - `EXCEPTION`: The risk is accepted.
  - `NOT_APPLICABLE`: The finding does not apply to the affected asset.
  - `BY_DESIGN`: The finding is an inherent characteristic or limitation of the system.
- `note`: Add any relevant context or justification for ignoring the finding.

</Expandable>

<Expandable title="Unignore a finding">

Here's an example API mutation to update the status of a vulnerability finding to `OPEN`. No resolution reason is required. A note is optional.

```json Example
{
  "query": "mutation UpdateVulnerabilityFindingStatus($input: UpdateFindingStatusInput!) { updateVulnerabilityFindingStatus(input: $input) { vulnerabilityFinding { id status resolutionReason note { ...FindingNote } } } }\nfragment FindingNote on VulnerabilityFindingNote { id text createdAt updatedAt user { id email } serviceAccount { id name } }",
  "variables": {
    "input": {
      "status": "REJECTED",
      "resolutionReason": "EXCEPTION",
      "note": "This finding has been reviewed and is deemed an acceptable risk."
    }
  }
}
```

Key parameter within the `input` object:

- `status`: Set this to `"OPEN"` to unignore the vulnerability finding.

</Expandable>

The `query` includes a GraphQL mutation named `UpdateVulnerabilityFindingStatus` which takes an `UpdateFindingStatusInput`. The response includes details of the updated `vulnerabilityFinding`, such as its `id`, new `status`, `resolutionReason`, and any associated `note`.

A successful API call returns a response similar to the one below:

```json Example response
{
"data": {
  "updateVulnerabilityFindingStatus": {
    "vulnerabilityFinding": {
      "id": "a3351ed2-0585-509c-95a0-4de06baccb2e",
      "status": "REJECTED",
      "portalUrl": "",
      "resolutionReason": "RISK_ACCEPTED",
      "note": {
        "id": "72fc8361-2945-4053-b422-54500fba3652",
        "text": "This finding has been reviewed and is deemed an acceptable risk.",
        "createdAt": "2025-05-15T12:31:09.111045515Z",
        "updatedAt": "2025-05-15T12:31:09.112272306Z",
        "user": {
          "id": "john.doe@wiz.io",
          "email": "john.doe@wiz.io"
        },
        "serviceAccount": null
      }
    }
  }
}
```

:::success

Done! You have successfully ignored a Vulnerability Finding using the API.

:::

## Next steps

- [See Vulnerability Finding API reference](dev:ignore-vulnerability-finding)
- [Best practices for Vulnerability Findings](dev:vuln-best-practices)
