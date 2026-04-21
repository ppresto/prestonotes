# Third-Party Security Graph Enrichment Tutorial (V2)
*Learn how to upload external security data to Wiz using the V2 enrichment API with simplified resource matching.*

Category: enrichment

If using the [V2 enrichment schemas](dev:enrichment#high-level-workflow), you no longer need to retrieve information about the resources you want to enrich and match your findings to their IDs. You can simply upload findings directly.

This tutorial shows you an example of how to work with the V2 schemas. We'll upload attack surface findings using the DAST/Attack Surface Findings V2 schema to enrich the Wiz <Glossary id="Security Graph" />. We provide an example schema for your use, but feel free to use your own schema instead.

<Calloutlimitations />

## Prerequisites

- Valid `Bearer token`—[Get a token](dev:generate-api-token)

- Required scopes:
  - `create:external_data_ingestion`
  - `read:system_activities`

## External enrichment steps

%WIZARD_START_CLOSED%

### Prepare the enrichment JSON

The DAST/Attack Surface Findings V2 schema uses a simplified process for uploading findings. Instead of first pulling all relevant resources and matching findings to them, you can now upload findings with sufficient identifying information about the asset. If the asset exists in Wiz, the finding is attached to it.

The enrichment JSON contains information about findings to upload. It also contains identifiers which are required to ensure that the enrichment data is properly associated with the correct cloud resource in the Wiz platform.

The identifiers are also required to ensure that the uploaded data doesn't become stale. Stale data automatically resolves or is removed after 7 days with no updates. Read about the [finding lifecycle](dev:enrichment#finding-lifecycle).

The `integrationId` identifies who performed the upload, while the `dataSources.id` uniquely identifies a specific scan scope. For example:

- The `integrationId` identifies the third-party vendor the enrichment was sourced from.
- The `dataSources.id` identifies the specific scan scope (e.g., "prod-web-scan" vs. "dev-web-scan").

:::warning[Maintain consistent data source IDs for recurring scans]

The data source ID uniquely identifies a specific scan scope:

- Use different IDs for different environments (e.g., one for production, another for development).
- Always use the same data source ID when scanning the same resource repeatedly.
- Using different IDs for the same resource will cause your findings to become stale and auto-resolve after 7 days of no updates, potentially losing important security information.

:::

The enrichment JSON follows a specific structure that maps your data to Wiz's expected format. This mapping ensures that Wiz can properly ingest, process, and display the information you're providing. Properly formatted JSON is critical for successful integration with the Wiz API and will prevent potential errors during the upload process.

Copy and save the example enrichment JSON below as `enrichment_test_file_tutorial.json`.

```json Example enrichment
{
  "integrationId": "55c176cc-d155-43a2-98ed-aa56873a1ca1",
  "dataSources": [
    {
      "id": "dast-acme-corp-prod-web",
      "analysisDate": "2025-12-15T14:30:00Z",
      "assets": [
        {
          "details": {
            "endpoint": {
              "assetId": "endpoint-7f3a9b2c-4e1d-4a8f-9c3b-2d5e6f7a8b9c",
              "assetName": "api.example.com",
              "host": "api.example.com",
              "port": "443",
              "protocol": "HTTPS"
            }
          },
          "attackSurfaceFindings": [
            {
              "id": "FIND-2025-001",
              "name": "Weak SSL/TLS Cipher Suites",
              "description": "The remote web server supports the use of weak SSL/TLS cipher suites.",
              "assessmentDetails": "Detected support for RC4 and 3DES suites on port 443.",
              "remediation": "Reconfigure the web server to disable weak ciphers and protocols.",
              "severity": "Medium",
              "type": "Misconfiguration",
              "externalFindingLink": "https://my.app/vuln/detail/FIND-2025-001",
              "vulnerabilities": [
                "CVE-2023-12345"
              ],
              "weaknesses": [
                "CWE-327"
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

:::info[Note]

WIN partners should replace the `integrationId` value above with the ID sent by Wiz during the integration initiation process.

:::

This example enrichment JSON associates a test finding with a specific endpoint asset. In the next step, you'll request an upload slot from Wiz.

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

To check the status of the Security Finding enrichment, execute the `SystemActivity` query, replacing `<systemActivityId>` with the system Activity ID you copied from the step [request to upload a file to Wiz](#step-2-request-to-upload-a-file-to-wiz).

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
|   **id**             | A unique identifier for the system activity. In this case, it is `9ff180ba-b7ef-5fa5-12345678`.                                             |
|   **status**         | Represents the current status of the activity. Here, it's `SKIPPED`, indicating that this particular upload operation finished.             |
|   **statusInfo**     | Provides additional information about the status. It's `null` in this example, meaning no extra details are provided.                       |
|   **result**         | Contains results concerning the data sources and findings.                                                                                  |
|     **dataSources**  | An object that provides insight into the data sources that were considered during the security system activity.                             |
|       **incoming**   | Indicates the number of data sources or inputs that were ready for the scan. In this instance, there was 1 data source.                     |
|       **handled**    | Represents how many of the incoming data sources were actually processed. All (1) were handled in this scenario.                            |
|     **findings**     | An object that provides details about potential Issues, vulnerabilities, or threats that were detected during the security system activity. |
|       **incoming**   | Signifies the number of potential Issues or findings identified. Here, there were 3 findings detected.                                      |
|       **handled**    | Indicates the number of findings for which Wiz was able to identify and associate with a known resource.                                    |
|   **context**        | Provides additional details about the system activity.                                                                                      |
|     **fileUploadId** | An identifier related to the data or file that was uploaded for the scan. Here, the ID is `275553`.                                         |

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
