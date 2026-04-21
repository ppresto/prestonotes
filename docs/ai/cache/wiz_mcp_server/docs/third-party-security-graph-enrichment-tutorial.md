# Third-Party Security Graph Enrichment Tutorial (V1)
*Learn how to upload external security data to Wiz using the V1 enrichment API with resource ID matching.*

Category: enrichment

:::info

This tutorial shows you how to work with a V1 schema, which requires an extra step that is not necessary for V2 schemas. If you're using a V2 schema, see our [updated tutorial](dev:enrichment-tutorial-v2) for more information.

:::

In this tutorial, learn how to upload Data Findings to enrich the Wiz <Glossary id="Security Graph" />. You don't need to create your own schema for this tutorial—we will provide an outline that you can use.

If you prefer to skip the step-by-step tutorial, you can explore the [upload security scan file](dev:script-upload-security-scan-file) script example. It demonstrates all the required components and can serve as a starting point for your own customizations.

<Calloutlimitations />

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)

- Required scopes:
  - `create:external_data_ingestion`
  - `read:system_activities`
  - `read:resources`

## External enrichment steps

%WIZARD_START_CLOSED%

### Retrieve resource information

Before uploading enrichment data, retrieve information about the resources you want to enrich to link your data properly to the Wiz Security Graph.

In this tutorial, we'll use Data Findings enrichment as an example, and upload a finding to a resource, but you can apply similar steps for any enrichment type by using the appropriate API and schema.

<Expandable title="See enrichment type APIs">

| Enrichment Type                                           | API to Use                                                 | Description                                                                                                                                                                                                                          |
| :-------------------------------------------------------- | :--------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - Runtime Events<br/>- DSPM<br/>- Custom Tags<br/>- Vulnerability Findings (V1) | [Pull Cloud Resources V2](dev:pull-cloud-resources-v2)           | Identify the existing cloud-managed resources in the target environment. Retrieves key information like `externalId` needed for enrichment.                                                                      |
| SAST Application Vulnerabilities (V1)                          | [Pull Version Control Repositories](dev:pull-repositories) | Retrieve list of detected version control repositories. This provides the repository ID needed to associate vulnerability findings with the correct resource.                                                                        |
| DAST/ASM Vulnerabilities (V1)                                 | [Pull Exposed Resources](dev:pull-network-exposure)        | Retrieve list of exposed resources. Filter for Application Endpoints using `filterBy.publicInternetExposureFilters.hasApplicationEndpoint = true`. Application Endpoints contain information necessary to confirm external exposure. |

</Expandable>

Execute the below example GraphQL query to retrieve a resource.

```json Example query
{
  "query": "query CloudResourcesTable($first: Int, $after: String, $filterBy: CloudResourceV2Filters, $orderBy: CloudResourceOrder, $fetchTotalCount: Boolean = true) { cloudResourcesV2( first: $first after: $after filterBy: $filterBy orderBy: $orderBy ) { totalCount: totalServiceUsageResourceCount @include(if: $fetchTotalCount) pageInfo { hasNextPage endCursor } nodes { id name externalId type cloudPlatform } } }",
  "variables": {
    "first": 1,
    "filterBy": {
      "type": {
        "equals": [
          "BUCKET"
        ]
      }
    }
  }
}
```

After running the query, extract the resource information from the response. For this example, fetch the `externalId` field which is the resource identifier (also known as `providerId` in the Data Findings schema). This field provides the information needed to start building the enrichment JSON.

### Prepare the enrichment JSON

After retrieving the `externalId` field, it's time to prepare the enrichment JSON that will be uploaded to Wiz. This JSON contains information about data findings to upload. It also contains identifiers which are required to ensure that the enrichment data is properly associated with the correct cloud resource in the Wiz platform.

The identifiers are also required to ensure that the uploaded data doesn't become stale. Stale data automatically resolves or is removed after 7 days with no updates. Read about the [finding lifecycle](dev:enrichment#finding-lifecycle).

The `integrationId` identifies who performed the upload, while the `dataSources.id` uniquely identifies a specific scan scope. For example:

- The `integrationId` identifies from which third-party vendor the enrichment was sourced from.
- The `dataSources.id` identifies the specific scan scope (e.g., "prod-data-scan" vs. "dev-data-scan"). For Data Findings enrichments, it's recommended to use the subscription ID as the data source label.

:::warning[Maintain consistent data source IDs for recurring scans]

The data source ID uniquely identifies a specific scan scope:

- Use different IDs for different environments (e.g., one for production, another for development).
- Always use the same data source ID when scanning the same resource repeatedly.
- Using different IDs for the same resource will cause your findings to become stale and auto-resolve after 7 days of no updates, potentially losing important security information.s

:::

The enrichment JSON follows a specific structure that maps your data to Wiz's expected format. This mapping ensures that Wiz can properly ingest, process, and display the information you're providing. Properly formatted JSON is critical for successful integration with the Wiz API and will prevent potential errors during the upload process.

Copy and save the example enrichment JSON below as `enrichment_test_file_tutorial.json`.

```json Example enrichment
{
  "integrationId": "<INTEGRATION_ID>",
  "dataSources": [
    {
      "id": "data-findings-vendor1-customer2-prod-394",
      "analysisDate": "2025-12-27T00:24:46Z",
      "assets": [
        {
          "assetIdentifier": {
            "providerId": "<EXTERNAL_ID>"
          },
          "dataFindings": [
            {
              "id": "17",
              "name": "GDPR - Personal Sensitive test1",
              "severity": "Low",
              "dataCategory": "PII",
              "dataClassifierId": "BUILTIN-1",
              "externalFindingLink": "https://test.123"
            }
          ]
        }
      ]
    }
  ]
}
```

In the file, replace these placeholders:

| Parameter          | Description                                                                                                                                                                                                                                    |
| :----------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<INTEGRATION_ID>` | This is the unique ID for each Wiz integration: <br/> <br/> <ul><li>For WIN partners—Sent by Wiz during the integration initiation process.</li><li>For Wiz customers—Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> <br/> |
| `<EXTERNAL_ID>`    | Replace with the `externalId` copied previously. This is the `providerId` in the Data Findings schema (e.g., ARN for AWS resources).                                                                                                           |

You have successfully prepared an enrichment JSON which associates a test data finding with a specific cloud resource. In the next step, you'll request an upload slot from Wiz.

### Request to upload a file to Wiz

To initiate a file upload, request a new upload slot. When successful, the system will return an upload ID and AWS S3 Bucket Presigned URL to which you can upload a file.

Request an upload slot by executing `RequestSecurityScanUpload` query below. Replace `<FILE_NAME>` in the query with the actual file name you intend to upload. Enter the name of the file we created previously: `enrichment_test_file_tutorial.json`.

```json RequestFileUpload query
{
  "query": "query RequestSecurityScanUpload($filename: String!) { requestSecurityScanUpload(filename: $filename) { upload { id url systemActivityId } }}",
  "variables": {
    "filename": "<FILE_NAME>.json"
  }
}
```

A successful response will look like the example below. Extract the following from the response data:

- `id`: The upload request ID.
- `url`: The presigned AWS S3 Bucket URL to use for your file upload.
- `systemActivityId`: The system Activity ID you can use to check the status of your request.

```json Example response
{
  "data": {
    "requestSecurityScanUpload": {
      "upload": {
        "id": "17768",
        "url": "https://prod-55555-file-upload.s3.us-east-2.amazonaws.com/62d0f20dfgdfgdfg67b-8d8d-c8ed1be58872/17768_Finding.json?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS32CYTU5MSCR6CHV%2F20221003%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20221003T104010Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=dfe59a1ab3352e810707cfe7631e821162a942ea4u1503393f18722ecefb0022",
        "systemActivityId": "7eb8dac6-efa2-5095-9eaf-20776b213777"
      }
    }
  }
}
```

You have successfully requested an upload slot from Wiz and received a presigned URL, along with information. In the next step, you'll upload the enrichment JSON to the presigned URL.

### Upload the file to the presigned AWS S3 Bucket URL

Choose a method to upload the security scan file to the presigned AWS S3 Bucket URL:

<Expandable title="(Recommended) Use a custom script">

Run the below script to upload the security scan file to the presigned AWS S3 Bucket URL you received from the previous step. Replace these placeholders in the script:

- `YOUR-SECURITY-FINDING-FILE-PATH` with the location of your enrichment JSON.
- `PRE-SIGN-URL` with the presigned URL copied previously.

```python
# Python 3.6+
# pip(3) install requests
import requests
import logging


FILE_PATH = 'YOUR-SECURITY-FINDING-FILE-PATH'  # e.g. /Users/Desktop/upload-scan.json

def uploadfiletos3 (url):
    print(f'# Step 2 - Upload to S3')
    FILE_PATH  =  '/Users/Desktop/upload-scan.json'

    with open(FILE_PATH) as object_file:
                object_text = object_file.read()
    response = requests.put(url, data=object_text)
    if response.status_code != 200:
            raise Exception(f'Error: Received {response.status_code} status code while uploading {FILE_PATH} '
                        f'to S3 at URL: {url} ')
    print(f'Upload file succeeded\n')


def main():
    UP_LOAD_URL = 'PRE-SIGN-URL'
    uploadfiletos3 (UP_LOAD_URL)

if __name__ == '__main__':
    main()
```

</Expandable>

<Expandable title="Use AWS Explorer for Visual Studio">

To upload a security scan file using AWS Explorer for Visual Studio, [follow AWS' documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html).

</Expandable>

You have successfully uploaded your enrichment JSON to Wiz via the presigned URL. It may take up to 12 hours for Wiz to fully ingest the enrichment. In the next step, you'll check the enrichment status.

### Get enrichment status

In this step, execute the `SystemActivity` query to retrieve information about the enrichment's status.

To check the status of the Security Finding enrichment, execute the `SystemActivity` query, replacing `<systemActivityId>` with the system Activity ID you copied from the step [request to upload a file to Wiz](#step-3-request-to-upload-a-file-to-wiz).

```json SystemActivity query
{ "query": "query SystemActivity($id: ID!) {
          systemActivity(id: $id) {
              id
              status
              statusInfo
              result {
                  ...on SystemActivityEnrichmentIntegrationResult{
                      dataSources {
                          ... IngestionStatsDetails
                      }
                      findings {
                          ... IngestionStatsDetails
                      }
                      events {
                          ... IngestionStatsDetails
                      }
                      tags {
                          ...IngestionStatsDetails
          }
                  }
              }
              context {
                  ... on SystemActivityEnrichmentIntegrationContext{
                      fileUploadId
                  }
              }
          }
      }

      fragment IngestionStatsDetails on EnrichmentIntegrationStats {
          incoming
          handled
      }",
  "variables": {
    "id": "<systemActivityId>"
  }
}
```

A successful API call returns information about the enrichment's status such as the system activity details, status indicators, processing results, and contextual information about the upload.

| Field                | Description                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **systemActivity**   | Represents a particular activity in the system.                                                                                             |
|   **id**             | A unique identifier for the system activity. In this case, it is `9ff180ba-b7ef-5fa5-12345678`.                                             |
|   **status**         | Represents the current status of the activity. Here, it's `SKIPPED`, indicating that this particular upload operation finished.             |
|   **statusInfo**     | Provides additional information about the status. It's `null` in this example, meaning no extra details are provided.                       |
|   **result**         | Contains results concerning the data sources and findings.                                                                                  |
|     **dataSources**  | An object that provides insight into the data sources that were considered during the security system activity.                             |
|       **incoming**   | Indicates the number of data sources or inputs that were ready for the scan. In this instance, there was 1 data source.                     |
|       **handled**    | Represents how many of the incoming data sources were actually processed. All (1) were handled in this scenario.                            |
|     **findings**     | An object that provides details about potential Issues, vulnerabilities, or threats that were detected during the security system activity. |
|       **incoming**   | Signifies the number of potential Issues or findings identified. Here, there were 3 findings detected.                                      |
|       **handled**    | Indicates the number of findings for which Wiz was able to identify and associate with a known resource.                                    |
|   **context**        | Provides additional details about the system activity.                                                                                      |
|     **fileUploadId** | An identifier related to the data or file that was uploaded for the scan. Here, the ID is `275553`.                                         |

Below is an example response:

```json Example response
{
  "data": {
    "systemActivity": {
      "id": "9ff180ba-b7ef-5fa5-12345678",
      "status": "SKIPPED",
      "statusInfo": null,
      "result": {
        "dataSources": {
          "incoming": 1,
          "handled": 1
        },
        "findings": {
          "incoming": 3,
          "handled": 2
        }
      },
      "context": {
        "fileUploadId": "275553"
      }
    }
  }
}
```

%WIZARD_END%

:::success

Done! You have successfully created an enrichment JSON, uploaded it to Wiz, and checked the enrichment's status.

:::
