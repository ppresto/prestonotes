# Create Cloud Resource Inventory Report Tutorial
*Learn how to create, read, search, update, and rerun Cloud Resource Inventory reports using the WIN API.*

Category: cloud-resource-inventory

This tutorial will teach you about Cloud Resource Inventory Reports. It walks you through the steps of creating a report, reading a report, searching for a report, updating it, and rerunning it. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read:reports`
  - `create:reports`
  - `update:reports`
  - `read:resources`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

Create a report using the `CreateReport` mutation, define the report type, target specific asset types, and use filters to refine the report data. See the [Create Inventory Report API reference](dev:create-inventory-report-v2#variables) to view all the available filters.

Execute the `CreateReport` mutation to generate a report based on specified parameters.

The following mutation creates an incremental cloud resource inventory report named "Test Cloud Resources Report V2" that runs every 24 hours, starting on June 4, 2025, at 15:53:59Z. This report includes:

- `name`: The name of the report, set to "Test Cloud Resources Report V2."
- `type`: The report type, specified as "CLOUD_RESOURCE_V2" for cloud resource inventory.
- `projectId`: Defines the scope of the report; "\*" indicates all projects.
- `cloudResourceV2Params`: Contains filters for the cloud resources included in the report:
  - `cloudPlatform`: Filters resources by cloud provider, here set to include only AWS.
  - `hasAdminPrivileges`: Filters for resources that have administrative privileges, set to `true`.
  - `hasSensitiveData`: Filters for resources that contain sensitive data, set to `true`.
- `incremental`: When set to `true`, creates an incremental report that runs periodically. In this example, it's set to `true`.
- `compressionMethod`: Specifies the compression method for the report, set to "GZIP."
- `runIntervalHours`: Defines how often the incremental report runs, set to `24` hours.
- `runStartsAt`: The timestamp for when the incremental report starts running, set to "2025-06-04T15:53:59Z."

See the [Create Report API](dev:create-inventory-report-v2) for more details and to refine your report generation.

```json Example mutation
{
  "query": "mutation CreateReport($input: CreateReportInput!) {  createReport(input: $input) {    report {      id    }  } }",
  "variables": {
    "input": {
      "name": "Test Cloud Resources Report V2",
      "type": "CLOUD_RESOURCE_V2",
      "projectId": "*",
      "cloudResourceV2Params": {
        "filters": {
          "cloudPlatform": {
            "equals": ["AWS"]
          },
          "hasAdminPrivileges": {
            "equals": true
          },
          "hasSensitiveData": {
            "equals": true
          }
        }
      },
      "incremental": true,
      "compressionMethod": "GZIP",
      "runIntervalHours": 24,
      "runStartsAt": "2025-06-04T15:53:59Z"
    }
  }
}
```

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

:::warning[This step is for non-incremental reports only]

:::

This step shows you how to update a report's parameters.

You can modify existing reports to adjust their parameters, refine filters, or change their names using the [`UpdateReport`](dev:update-inventory-report-v2) mutation. This flexibility allows you to adapt your reports to evolving security requirements or reporting needs without creating new ones from scratch.

Execute the `UpdateReport` mutation with the `override` object to modify an existing report.

The following mutation updates a cloud resource inventory report. It changes the report's name to "Updated Report" and modifies its filters. The updated report will now include:

- `id`: The unique identifier of the report to be updated (e.g., "695acc0f-9002-4a6d-b662-0dd9e785e7a8").
- `override.name`: The new name for the report, "Updated Report."
- `override.cloudResourceV2Params.filters`: New filter criteria for the cloud resources:
  - `cloudPlatform`: Now set to "Azure."
  - `hasAdminPrivileges`: Now set to `false`.
  - `hasSensitiveData`: Now set to `false`.
- `override.incremental`: Changes the report from incremental to non-incremental, set to `false`.
- `override.compressionMethod`: Continues to use "GZIP" compression.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {  updateReport(input: $input) {    report {      id    }  } }",
  "variables": {
    "input": {
      "override": {
        "name": "Updated Report",
        "cloudResourceV2Params": {
          "filters": {
            "cloudPlatform": {
              "equals": ["Azure"]
            },
            "hasAdminPrivileges": {
              "equals": false
            },
            "hasSensitiveData": {
              "equals": false
            }
          }
        },
        "incremental": false,
        "compressionMethod": "GZIP"
      },
      "id": "695acc0f-9002-4a6d-b662-0dd9e785e7a8"
    }
  }
}
```

A successful request returns an `id` field that contains a new report ID. Example response.

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
