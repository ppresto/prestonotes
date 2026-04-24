# Create Vulnerabilities Report Tutorial
*Learn how to create, read, search, update, and rerun Vulnerabilities reports using the WIN API.*

Category: vulnerabilities

This tutorial will teach you about Vulnerabilities Reports. It walks you through the steps of creating a Vulnerabilities report, reading a report, searching for a report, updating it, and rerunning it. [Learn about Wiz reports](dev:reports).

<Vulnissueexposure />

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read:reports`
  - `create:reports`
  - `update:reports`
  - `read:vulnerabilities`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a report using the `CreateReport` mutation. You'll learn how to define the report type, target specific asset types, and use filters to refine the report data. See the [Create Vulnerabilities Report API reference](dev:create-vuln-report#variables) to view all the available filters.

Example report requests:

<Expandable title="(Recommended) Incremental report that targets critical vulnerabilities on virtual machines, containers, repository branches and updates every 24 hours">

```json Example
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test Vulnerabilities Report",
      "type": "VULNERABILITIES",
      "projectId": "*",
      "compressionMethod": "GZIP",
      "vulnerabilityParams": {
        "type": "COMPACT",
        "filters": {
          "assetType": [
            "VIRTUAL_MACHINE",
            "CONTAINER",
            "REPOSITORY_BRANCH"
          ],
          "vendorSeverity": [
            "CRITICAL"
          ],
          "hasFix": true
        }
      },
      "incremental": true,
      "runIntervalHours": 24,
      "runStartsAt": "2025-12-09T20:00:00Z"
    }
  }
```

Key parameters:

- `type`: Is one of the following values: `"COMPACT"`, `"DETAILED"`.
- `assetType`: The type of asset object(s) to appear in the vulnerability report. In this example, it's set to include virtual machines, containers, and repository branches.
- `vendorSeverity`: Filters vulnerabilities based on their severity. In this case, it's set to "CRITICAL" to only include critical vulnerabilities.
- `hasFix`: When set to true, only includes vulnerabilities that have a known fix available.
- `incremental`: When set to true, creates an incremental report that runs periodically.
- `runIntervalHours`: Specifies the interval in hours between each run of the incremental report. Here, it's set to 24 hours (daily).
- `runStartsAt`: Specifies the start time for the first run of the incremental report in ISO 8601 format.

</Expandable>

<Expandable title="Non-incremental report that targets all vulnerabilities with critical severity on virtual machines and container images">

```json Example
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test Vulnerabilities Report",
      "type": "VULNERABILITIES",
      "projectId": "*",
      "compressionMethod": "GZIP",
      "vulnerabilityParams": {
        "type": "COMPACT",
        "filters": {
          "assetType": [
            "VIRTUAL_MACHINE",
            "CONTAINER_IMAGE"
          ],
          "vendorSeverity": [
            "CRITICAL"
          ]
        }
      },
      "incremental": false
    }
  }
```

Key parameters:

- `type`—Is one of the following values: "COMPACT", "DETAILED".
- `assetType`—The type of asset object(s) to appear in the vulnerability report. Possible values: `["VIRTUAL_MACHINE", "CONTAINER", "CONTAINER_IMAGE", "REPOSITORY_BRANCH", "SERVERLESS"]`. ⚠︎ If not specified, then defaults to `["VIRTUAL_MACHINE"]`.
  - In this example, it's set to include virtual machines and container images.
- `vendorSeverity`: Filters vulnerabilities based on their severity. In this case, it's set to "CRITICAL" to only include critical vulnerabilities.
- `incremental`: When set to true, creates an incremental report that runs periodically. In this example, it's set to false.

</Expandable>

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

Use the [`UpdateReport`](dev:update-vulnerabilities-report) mutation in the following code sample with the `override.vulnerabilityParams` object. By leveraging the filters within the param object, you can adjust the report's parameters to refine the output as needed. For instance, you could update the date parameter and the name.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "vulnerabilityParams": {
          "type": "DETAILED",
          "assetType": "VIRTUAL_MACHINE"
        },
        "name": "Test report name"
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

That's the end of the tutorial. Now, check out the [Create Vulnerabilities Report](dev:create-vuln-report) API.
