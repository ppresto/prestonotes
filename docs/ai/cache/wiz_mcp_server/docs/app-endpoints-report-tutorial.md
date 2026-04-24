# Create Application Endpoint Report Tutorial
*Learn how to create, read, search, update, and rerun Application Endpoint reports using the WIN API.*

Category: app-endpoints

This tutorial will teach you about Application Endpoint reports. It walks you through the steps of creating an Application Endpoint report, reading a report, searching for a report, updating a report, and rerunning a report. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read:reports`
  - `create:reports`
  - `update:reports`
  - `read:endpoint_attack_surfaces`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

Create a report using the `CreateReport` mutation, define the report type as `APPLICATION_ENDPOINTS`, and use filters to refine the report data based on your requirements. See all available filters in the [Create Application Endpoint Report](dev:create-app-endpoint-report) API reference.

The following mutation creates an Application Endpoint report named "Test Application Endpoint Report" that includes:

- `name`: The name of the report, set to "Test Application Endpoint Report."
- `type`: The report type, specified as "APPLICATION_ENDPOINTS" for application endpoint reports.
- `projectId`: The scope of the report; "*" indicates all projects.
- `applicationEndpointsParams`: Contains filters for the application endpoints included in the report:
  - `cloudPlatform`: Filters endpoints by cloud provider, here set to include AWS, Azure, and GCP.
  - `exposureLevel`: Filters for endpoints with high exposure level, set to `["HIGH"]`.
  - `portStatus`: Filters for open ports, set to `["OPEN"]`.
  - `scanSource`: Filters by scan source, here set to include cloud and API security scans.
- `compressionMethod`: Specifies the compression method for the report, set to "GZIP."
- `csvDelimiter`: Specifies the delimiter used in CSV output, set to "US" for US locale formatting.

See the [Create Application Endpoint Report API](dev:create-app-endpoint-report) for more details and to refine your report generation.

```json Example mutation
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test Application Endpoint Report",
      "type": "APPLICATION_ENDPOINTS",
      "projectId": "*",
      "applicationEndpointsParams": {
        "filters": {
          "cloudPlatform": {
            "equals": ["AWS", "Azure", "GCP"]
          },
          "exposureLevel": {
            "equals": ["HIGH"]
          },
          "portStatus": {
            "equals": ["OPEN"]
          },
          "scanSource": {
            "equals": ["CLOUD", "API_SECURITY"]
          }
        }
      },
      "compressionMethod": "GZIP",
      "csvDelimiter": "US"
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

<Nonincrementalreports />

This step shows you how to update a report's parameters.

You can modify existing reports to adjust their parameters, refine filters, or change their names using the [`UpdateReport`](dev:update-app-endpoint-report) mutation. This flexibility allows you to adapt your reports to evolving security requirements or reporting needs without creating new ones from scratch.

Execute the `UpdateReport` mutation with the `override` object to modify an existing report.

The following mutation updates an Application Endpoint report. It changes the report's name to "Updated Application Endpoint Report" and modifies its filters. The updated report will now include:

- `id`: The unique identifier of the report to be updated (e.g., "3765f806-8b33-46c2-a0d0-a98c31f46c0e").
- `override.name`: The new name for the report, "Updated Application Endpoint Report."
- `override.applicationEndpointsParams.filters`: New filter criteria for the application endpoints:
  - `cloudPlatform`: Now set to "AWS" only.
  - `exposureLevel`: Now includes both "HIGH" and "MEDIUM" exposure levels.
  - `relatedIssueSeverity`: Filters for endpoints with critical or high severity issues.
- `override.compressionMethod`: Continues to use "GZIP" compression.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "id": "3765f806-8b33-46c2-a0d0-a98c31f46c0e",
      "override": {
        "name": "Updated Application Endpoint Report",
        "applicationEndpointsParams": {
          "filters": {
            "cloudPlatform": {
              "equals": ["AWS"]
            },
            "exposureLevel": {
              "equals": ["HIGH", "MEDIUM"]
            },
            "relatedIssueSeverity": {
              "equals": ["CRITICAL", "HIGH"]
            }
          }
        },
        "compressionMethod": "GZIP"
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
        "id": "3765f806-8b33-46c2-a0d0-a98c31f46c0e"
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

That's the end of the tutorial. Now, check out the [Create Application Endpoint Report](dev:create-app-endpoint-report) API.
