# Create Compliance Assessment Report Tutorial
*Learn how to create, read, search, update, and rerun Compliance Assessment reports using the WIN API.*

Category: compliance-assessment

This tutorial will teach you about Compliance Assessment reports. It walks you through the steps of creating a report, reading a report, searching for a report, updating a report, and rerunning a report. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read: reports`
  - `create:reports`
  - `update: reports`
  - `read:cloud_configuration`
  - `read:host_configuration`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

This step guides you through creating a Compliance Assessment report using the `CreateReport` mutation. You'll learn how to define the report type and use filters to refine the report data. See the [Create Compliance Assessment Report](dev:create-compliance-report) API reference to view all the available filters.

Example report request:

```json Example request
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test Compliance Report",
      "type": "COMPLIANCE_ASSESSMENTS",
      "runIntervalHours": 168,
      "runStartsAt": "2024-05-10T06:00:00.000Z",
      "csvDelimiter": "US",
      "complianceAssessmentsParams": {
        "securityFrameworkIds": ["wf-id-50"]
      }
    }
  }
}
```

Key parameters:

- `name`: A descriptive name for your compliance report.
- `type`: The type of report to generate. `"COMPLIANCE_ASSESSMENTS"` is required to create a Compliance Assessment report
- `runIntervalHours`: How often to run the report in hours (168 = weekly).
- `runStartsAt`: When to start running the report.
- `csvDelimiter`: CSV delimiter standard (US = comma).
- `complianceAssessmentsParams`: Parameters specific to compliance assessment reports.
  - `securityFrameworkIds`: Array of framework IDs to include in the report (e.g., `wf-id-50`).

<Reportid />

### Check report status and get report URL

<Checkreportstatus />

### (Optional) Search for a report

<Searchreports />

### (Optional) Update report parameters

<Nonincrementalreports />

This step shows you how to update a report's parameters.

Use the [`UpdateReport`](dev:update-compliance-report) mutation in the following code sample with the `override.complianceAssessmentParams` object. By leveraging the filters within the param object, you can adjust the report's parameters to refine the output as needed.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "override": {
        "complianceAssessmentsParams": {
          "result": [
            "FAIL"
          ],
          "securityFrameworkIds": [
            "wf-id-50"
          ]
        },
        "name": "Updated test-compliance report"
      },
      "id": "fb0ef074-b550-433b-a3d8-918064f7f4b3"
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

## Next step

That's the end of the tutorial. Now, check out the [Create Compliance Assessment Report](dev:create-compliance-report) API.
