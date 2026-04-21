# Create Data Findings Report Tutorial
*Learn how to create, read, search, update, and rerun Data Findings reports using the WIN API.*

Category: data-findings

This tutorial will teach you about Data Findings reports. It walks you through the steps of creating a Data Findings report, reading a report, searching for a report, updating a report, and rerunning a report. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read: reports`
  - `create:reports`
  - `update: reports`
  - `read:data_findings`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a report using the `CreateReport` mutation. You'll learn how to define the report type and use filters to refine the report data. See the [Create Data findings Report](dev:create-data-findings-report-v2) API reference to view all the available filters.

Example report request:

```json Example request
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Acme_data-findings_test-report",
      "type": "DATA_SCAN",
      "projectId": "*",
      "dataFindingsParams": {
        "filters": {
          "graphEntityType": ["BUCKET", "VIRTUAL_MACHINE"],
          "severity": ["CRITICAL"]
        }
      }
    }
  }
}
```

Key parameters:

- `type`: The type of report to generate. `"DATA_SCAN"` is required to create a Data Findings report.
- `projectID`: Scope the report to project ID. For all projects, use `*`. If the integration is scoped to specific Wiz Projects, you must specify the Wiz Project IDs. [Learn more](dev:projects#project-scoped-integrations).
- `graphEntityType`: Search data findings by graph entity type according to Wiz Security Graph object normalization. In this example, it's set to include buckets and virtual machines.
- `severity`: Filters Data Findings based on their severity. In this case, it's set to include only critical Data Findings.

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

<Nonincrementalreports />

This step shows you how to update a report's parameters.

To update a report's parameters:

Use the [`UpdateReport`](dev:update-data-findings-report-v2) mutation in the following code sample with the `override.dataFindingsParams` object. By leveraging the filters within the param object, you can adjust the report's parameters to refine the output as needed. For instance, you could update the `status` parameter to filter for only Data Findings that are open.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "dataFindingsParams": {
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

That's the end of the tutorial. Now, check out the [Create Data Findings Report](dev:create-data-findings-report-v2) API.
