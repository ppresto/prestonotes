# Create Configuration Findings Report Tutorial
*Learn how to create, read, search, update, and rerun Cloud Configuration Findings reports using the WIN API.*

Category: ccf

This tutorial will teach you about Configuration Findings reports. It walks you through the steps of creating a Configuration Findings report, reading a report, and searching for a report. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read: reports`
  - `create:reports`
  - `update: reports`
  - `read:cloud_configuration`

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a report using the `CreateReport` mutation. You'll learn how to define the report type and use filters to refine the report data. See the [Create Configuration Findings Report](dev:create-ccr-report) API reference to view all the available filters.

The following example report request creates an incremental Configuration Findings report that targets critical findings and updates every 24 hours.

```json Example
"query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test CCR Report",
      "type": "CONFIGURATION_FINDINGS",
      "incremental": true,
      "csvDelimiter": "US",
      "configurationFindingParams": {
        "filters": {
          "severity": [
            "CRITICAL"
          ],
          "hasRemediationInstructions": true
        }
      },
      "runStartsAt": "2024-10-09T20:00:00Z",
      "runIntervalHours": 24
    }
  }
```

Key parameters:

- `type`: Specifies the report type. For Configuration Findings reports, set to `"CONFIGURATION_FINDINGS"`.
- `severity`: Filters findings based on their severity level. In this example, it's set to `["CRITICAL"]` to only include critical findings.
- `hasRemediationInstructions`: When set to true, only includes findings that have remediation instructions available.
- `incremental`: When set to true, creates an incremental report that runs periodically.
- `runIntervalHours`: Specifies the interval in hours between each run of the incremental report. Here, it's set to 24 hours (daily).
- `runStartsAt`: Specifies the start time for the first run of the incremental report in ISO 8601 format.
- `csvDelimiter`: Specifies the delimiter used in CSV output. Here, it's set to "US" for US locale formatting.

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

<Nonincrementalreports />

This step shows you how to update a report's parameters.

To update a report's parameters:

Use the [`UpdateReport`](dev:update-ccr-report) mutation in the following code sample with the `override.configurationFindingParams` object. By leveraging the filters within the param object, you can adjust the report's parameters to refine the output as needed. For instance, you could update the `status` parameter to filter for only Cloud Configuration Findings that are open.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "configurationFindingParams": {
          "filters": {
            "status": ["OPEN"]
          }
        }
      }
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

That's the end of the tutorial. Now, check out the [Create Configuration Findings Report](dev:create-ccr-report) API.
