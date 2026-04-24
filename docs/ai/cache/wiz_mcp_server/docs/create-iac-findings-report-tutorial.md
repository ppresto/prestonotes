# Create IaC Findings Report Tutorial
*Learn how to create, read, search, update, and rerun IaC Findings reports using the WIN API.*

Category: iac-findings

This tutorial will teach you about IaC Findings reports. It walks you through the steps of creating an IaC Findings report, reading a report, searching for a report, updating a report, and rerunning a report. [Learn about Wiz reports](dev:reports).

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)
- Wiz service account with the following permissions:
  - `read:reports`
  - `create:reports`
  - `update:reports`
  - `read:iac_findings`

## Basic workflow

%WIZARD_START_CLOSED%

### Create a report

Create a report using the `CreateReport` mutation, define the report type as `IAC_FINDINGS`, and use filters to refine the report data based on your requirements. See all available filters in the [Create IaC Findings Report](dev:create-iac-findings-report) API reference.

The following mutation creates an IaC Findings report named "Test IaC Findings Report" that includes:

- `name`: The name of the report, set to "Test IaC Findings Report."
- `type`: The report type, specified as "IAC_FINDINGS" for IaC findings reports.
- `projectId`: The scope of the report; "*" indicates all projects.
- `iacFindingsParams`: Contains filters for the IaC findings included in the report:
  - `severity`: Filters findings by severity, here set to include CRITICAL and HIGH.
  - `status`: Filters for open findings, set to `["OPEN"]`.
  - `resource.cloudPlatform`: Filters by cloud provider, here set to include AWS, Azure, and GCP.
  - `resource.iacPlatform`: Filters by IaC platform, here set to TERRAFORM.
- `compressionMethod`: Specifies the compression method for the report, set to "GZIP."
- `csvDelimiter`: Specifies the delimiter used in CSV output, set to "US" for US locale formatting.

See the [Create IaC Findings Report API](dev:create-iac-findings-report) for more details and to refine your report generation.

```json Example mutation
{
  "query": "mutation CreateReport($input: CreateReportInput!) {   createReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "name": "Test IaC Findings Report",
      "type": "IAC_FINDINGS",
      "projectId": "*",
      "iacFindingsParams": {
        "filters": {
          "severity": {
            "equals": ["CRITICAL", "HIGH"]
          },
          "status": {
            "equals": ["OPEN"]
          },
          "resource": {
            "cloudPlatform": {
              "equals": ["AWS", "Azure", "GCP"]
            },
            "iacPlatform": {
              "equals": ["TERRAFORM"]
            }
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

You can modify existing reports to adjust their parameters, refine filters, or change their names using the [`UpdateReport`](dev:update-iac-findings-report) mutation. This flexibility allows you to adapt your reports to evolving security requirements or reporting needs without creating new ones from scratch.

Execute the `UpdateReport` mutation with the `override` object to modify an existing report.

The following mutation updates an IaC Findings report. It changes the report's name to "Updated IaC Findings Report" and modifies its filters. The updated report will now include:

- `id`: The unique identifier of the report to be updated (e.g., "c244b00e-aba2-4763-8490-1d6bdf3c6c12").
- `override.name`: The new name for the report, "Updated IaC Findings Report."
- `override.iacFindingsParams.filters`: New filter criteria for the IaC findings:
  - `severity`: Now includes CRITICAL, HIGH, and MEDIUM severities.
  - `status`: Filters for OPEN and RESOLVED findings.
  - `resource.cloudPlatform`: Now set to "AWS" only.
- `override.compressionMethod`: Continues to use "GZIP" compression.

```json Update example
{
  "query": "mutation UpdateReport($input: UpdateReportInput!) {   updateReport(input: $input) {     report {       id     }   } }",
  "variables": {
    "input": {
      "id": "c244b00e-aba2-4763-8490-1d6bdf3c6c12",
      "override": {
        "name": "Updated IaC Findings Report",
        "iacFindingsParams": {
          "filters": {
            "severity": {
              "equals": ["CRITICAL", "HIGH", "MEDIUM"]
            },
            "status": {
              "equals": ["OPEN", "RESOLVED"]
            },
            "resource": {
              "cloudPlatform": {
                "equals": ["AWS"]
              }
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
        "id": "c244b00e-aba2-4763-8490-1d6bdf3c6c12"
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

That's the end of the tutorial. Now, check out the [Create IaC Findings Report](dev:create-iac-findings-report) API.
