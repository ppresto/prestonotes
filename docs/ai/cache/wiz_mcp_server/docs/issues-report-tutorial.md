# Create Issues Report Tutorial
*Learn how to create, read, search, update, and rerun Issues reports using the WIN API.*

Category: issues

This tutorial will teach you about Issues Reports. It walks you through the steps of creating an Issues report, reading a report, searching for a report, updating a report, and rerunning a report. [Learn about Wiz reports](dev:reports).

<Vulnissueexposure />

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read: reports`
  - `create:reports`
  - `update: reports`
  - `read:issues`
  - `read:threat_issues`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a report using the `CreateReport` mutation. You'll learn how to define the report type and use filters to refine the report data. See the [Create Issues Report](dev:create-issues-report) API reference to view all the available filters.

Example report requests:

<Expandable title="(Recommended) Incremental report that targets critical Issues on all Projects and updates every 24 hours">

```json Incremental example
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Acme_Issues_Test_Report",
      "type": "ISSUES",
      "projectId": "*",
      "compressionMethod": "GZIP",
      "issueParams": {
        "type": "STANDARD",
        "issueFilters": {
          "status": ["OPEN"],
          "severity": ["CRITICAL"]
        }
      },
      "incremental": true,
      "runIntervalHours": 24,
      "runStartsAt": "2024-11-13T07:00:00.000Z"
    }
  }
}
```

Key parameters:

- `type`: Set to "ISSUES" to create an Issues report.
- `projectId`: Set to `*` to include all Wiz Projects.
- `issueParams.type`: Set to "STANDARD" for standard Issue reporting.
- `issueFilters.status`: Filters for Issues with "OPEN" status
- `issueFilters.severity`: Filters for Issues with "CRITICAL" severity
- `incremental`: When set to true, creates an incremental report that runs periodically.
- `compressionMethod`: Required field that specifies how the report is compressed. Must be set to `GZIP`.
- `runIntervalHours`: Specifies the interval in hours between each run of the incremental report (24 hours).
- `runStartsAt`: Specifies the start time for the first run of the incremental report in ISO 8601 format.

</Expandable>

<Expandable title="(Recommended) One-time full report targeting critical cloud platform Issues in AWS and GCP with available remediation">

```json Full example
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test Issues Report",
      "type": "ISSUES",
      "projectId": "*",
      "incremental": false,
      "issueParams": {
        "type": "STANDARD",
        "issueFilters": {
          "status": ["OPEN"],
          "relatedEntity": {
            "cloudPlatform": ["AWS", "GCP"]
          },
          "severity": ["CRITICAL"],
          "hasRemediation": true,
          "hasServiceTicket": false
        }
      }
    }
  }
}
```

Key parameters:

- `type`: Set to "ISSUES" to create an Issues report.
- `projectId`: Set to `*` to include all Wiz Projects.
- `incremental`: Set to false for a one-time full report.
- `issueParams.type`: Set to "STANDARD" for standard Issue reporting.
- `issueFilters.status`: Filters for Issues with "OPEN" status.
- `issueFilters.relatedEntity.cloudPlatform`: Targets Issues in AWS and GCP environments.
- `issueFilters.severity`: Filters for Issues with "CRITICAL" severity.
- `issueFilters.hasRemediation`: Only includes Issues with available remediation steps.
- `issueFilters.hasServiceTicket`: Excludes Issues that already have service tickets.

</Expandable>

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

<Nonincrementalreports />

<br />

This step shows you how to update a report's parameters.

To update a report's parameters:

Use the [`UpdateReport`](dev:update-issues-report) mutation in the following code sample with the `override.issueParams` object. By leveraging the filters within the param object, you can adjust the report's parameters to refine the output as needed. For instance, you could update the name and the timeframe to only include Issues created after a specific date.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "issueParams": {
          "type": "DETAILED",
          "issueFilters": {
            "status": ["OPEN"],
            "severity": ["CRITICAL"],
            "relatedEntity": {
              "cloudPlatform": ["AWS", "GCP"]
            },
            "hasRemediation": true,
            "hasServiceTicket": false,
            "createdAt": {
              "after": "2026-01-22T07:30:28.924Z"
            }
          }
        },
        "name": "Updated Risk Issues Report"
      },
      "id": "f21d14f5-3de4-4fef-80ea-a7346945c159"
    }
  }
}
```

A successful request returns an `id` field that contains a report ID. Example response.

```json Example response
{
  "data": {
    "updateReport": {
      "report": {
        "id": "f21d14f5-3de4-4fef-80ea-a7346945c159"
      }
    }
  }
}
```

A report's presigned URL always points to the data from when the report was originally generated. To see updated data, you must rerun the report to regenerate the data and then obtain a new presigned URL.

:::success[Done! You have updated a report's filters]

To view the updated report:

1. [Rerun the report](#step-5-optional-rerun-a-report) to refresh the report's data.
2. [Get the report's new presigned URL](#step-2-check-report-status-and-get-report-url).

:::

### (Optional) Rerun a report

<Rerunreport />

%WIZARD_END%

## Next step

That's the end of the tutorial. Now, check out the [Create Issues Report](dev:create-issues-report) API.
