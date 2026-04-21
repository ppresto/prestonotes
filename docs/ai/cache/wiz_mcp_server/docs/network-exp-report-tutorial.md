# Create Network Exposure Report Tutorial
*Learn how to create, read, search, update, and rerun Exposed Resources reports using the WIN API.*

Category: exposed-resources

This tutorial will teach you about Network Exposure Reports. It walks you through the steps of creating a Network Exposure report, reading a report, searching for a report, updating it, and rerunning it. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read:reports`
  - `create:reports`
  - `update:reports`
  - `read:network_exposure`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a report using the `CreateReport` mutation. You'll learn how to define the report type, target specific asset types, and use filters to refine the report data. See the [Create Network Exposure Report API reference](dev:create-external-network-report) to view all the available filters.

Example report request for a scheduled network exposure report that will run periodically:

```json Example
{
  "query": "mutation CreateReport($input: CreateReportInput!) { createReport(input: $input) { report { id } } }",
  "variables": {
    "input": {
      "name": "Test Network Exposure Report",
      "type": "NETWORK_EXPOSURE",
      "projectId": "*",
      "runIntervalHours": 25,
      "runStartsAt": "2025-05-11T12:07:43Z"
    }
  }
}
```

Key parameters:

- `name`—A descriptive name for the report. In this example, it is set to `Test Network Exposure Report`.
- `type`—The type of report to create. For network exposure reports, this value should be `NETWORK_EXPOSURE`.
- `projectId`—The ID of the project for which to generate the report. Using `*` targets all projects.
- `runIntervalHours`—Specifies the interval in hours for recurring report generation. In this example, the report will run every 25 hours.  
  `runStartsAt`—Defines the timestamp for the first report execution. The format should be in ISO 8601 UTC (e.g., YYYY-MM-DDTHH:MM:SSZ). In this example, the first run is scheduled for `2025-05-11T12:07:43Z`.

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

:::warning[This step is for non-incremental reports only]

:::

This step shows you how to update a report's parameters.

To update a report's parameters:

Use the [`UpdateReport`](dev:update-network-exposure-report) mutation in the following code sample with the `override` object. You can adjust the report's parameters to refine the output as needed. For instance, you could update the date parameter and the name.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "name": "Updated Test Network Exposure Report",
        "runStartsAt": "2025-05-11T12:07:43Z",
        "runIntervalHours": 25
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

That's the end of the tutorial. Now, check out the [Create Network Exposure Report](dev:create-external-network-report) API.
