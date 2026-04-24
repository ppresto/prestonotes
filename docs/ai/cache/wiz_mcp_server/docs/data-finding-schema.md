# Data Findings Schema
*JSON schema reference for integrating third-party data security findings into Wiz, including supported assets and field definitions.*

Category: enrichment

Data Findings enrichment is designed for third-party vendors capable of conducting periodic scans. It's tailored to enhance Wiz's risk management by integrating external Data finding scanners. The scans, with the Wiz Security Graph, correlate findings to the appropriate cloud assets.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with Data Findings and the required identifier.

| Supported resources (entity name)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Required Identifier                |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------- |
| <ul><li> [`AI_DATASET`](dev:sec-graph-obj-normalization#ai-dataset) </li><li> [`DATABASE`](dev:sec-graph-obj-normalization#database-server) </li><li> [`DB_SERVER`](dev:sec-graph-obj-normalization#database-server) </li> <li>[`BUCKET`](dev:sec-graph-obj-normalization#bucket)</li> <li> [`SERVERLESS`](dev:sec-graph-obj-normalization#serverless)</li><li> [`VIRTUAL_DRIVE`](dev:sec-graph-obj-normalization#virtual-drive)</li><li> [`VIRTUAL_MACHINE`](dev:sec-graph-obj-normalization#virtual-machine)</li><li> [`FILE_SYSTEM_SERVICE - in PREVIEW`](dev:sec-graph-obj-normalization#file-system-service)</li></ul> | Workload provider ID, such as ARN. |

:::info[Supported cloud service providers]

Wiz currently supports Data Finding enrichment of these [cloud service providers](https://www.wiz.io/partners).

:::

## Finding life cycle

The finding life cycle shows how Data Findings flows from external scanners through the Wiz platform, from initial discovery to remediation tracking. This visualization helps understand how your scan data integrates with Wiz's security workflows.

| Step                            | Description                                                                                                                                                                                                                                                                                                                        |
| :------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frequency of File Uploads**   | We recommend uploading files every 24 hours, aligning with Wiz's typical 24-hour environment scan cycle for customers.                                                                                                                                                                                                             |
| **Organizing data sources**     | All findings should be categorized under their respective "Data Source". <br/> <br/> For clarity and organization, we recommend designating the subscription ID as the "Data Source" label. <br/> <br/> This helps identify VMs related to a specific subscription and, subsequently, the data findings detected within those VMs. |
| **Reporting data findings**     | When you upload a data finding based on its unique ID, Wiz will automatically mark it as "unresolved". <br/> <br/> Only report existing data findings. If a customer has addressed a specific data finding, then exclude that data finding ID from your subsequent upload.                                                         |
| **Automatic Resolution in Wiz** | If you fail to report a new or existing data finding for a particular VM, Wiz will automatically classify that finding as "resolved." Additionally, any Wiz Issues associated with that particular finding will also be marked as "resolved".                                                                                      |

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema

The Data Finding schema defines the JSON structure expected by Wiz's API when submitting vulnerability data. Understanding this schema is essential for creating valid payloads that will be properly processed and incorporated into the Security Graph.

```json Schema
{
  "$defs": {
    "asset": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": ["assetIdentifier"],
          "title": "assetLookupIdentifier"
        }
      ],
      "properties": {
        "analysisDate": {
          "format": "date-time",
          "type": "string"
        },
        "assetIdentifier": {
          "$ref": "#/$defs/assetIdentifier"
        },
        "dataFindings": {
          "items": {
            "$ref": "#/$defs/dataFinding"
          },
          "type": "array"
        }
      },
      "type": "object"
    },
    "assetIdentifier": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": ["providerId"],
          "title": "assetIdentifierWithProviderId"
        },
        {
          "required": ["networkAddress", "cloudPlatform"],
          "title": "assetIdentifierWithNetworkAddress"
        },
        {
          "required": ["endpointUrl", "cloudPlatform"],
          "title": "assetIdentifierWithEndpointUrl"
        }
      ],
      "properties": {
        "cloudPlatform": {
          "$ref": "#/$defs/cloudPlatform"
        },
        "endpointUrl": {
          "type": "string"
        },
        "networkAddress": {
          "type": "string"
        },
        "providerId": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "cloudPlatform": {
      "enum": ["ACK", "AKS", "AWS", "Alibaba", "Azure", "AzureDevOps", "BitbucketCloud", "BitbucketDataCenter", "Cloudflare", "Databricks", "EKS", "Firemon", "GCP", "GKE", "GenericDB", "GitHub", "GitLab", "IBM", "Kubernetes", "LKE", "Linode", "MongoDBAtlas", "OCI", "OKE", "Okta", "OpenAI", "OpenShift", "OpenStack", "Snowflake", "Terraform", "Vercel", "Wiz", "vSphere"],
      "type": "string"
    },
    "dataCategory": {
      "enum": ["PII", "PHI", "Financial", "DigitalIdentity", "Other", "Secrets", "Lineage", "StaleData", "Logs"],
      "type": "string"
    },
    "dataClassifier": {
      "enum": ["BUILTIN-1", "BUILTIN-101", "BUILTIN-102", "BUILTIN-118", "BUILTIN-119", "BUILTIN-122", "BUILTIN-125", "BUILTIN-126", "BUILTIN-139", "BUILTIN-141", "BUILTIN-158", "BUILTIN-162", "BUILTIN-174", "BUILTIN-178", "BUILTIN-182", "BUILTIN-186", "BUILTIN-20", "BUILTIN-232", "BUILTIN-25", "BUILTIN-255", "BUILTIN-265", "BUILTIN-266", "BUILTIN-267", "BUILTIN-271", "BUILTIN-274", "BUILTIN-286", "BUILTIN-32", "BUILTIN-38", "BUILTIN-39", "BUILTIN-42", "BUILTIN-43", "BUILTIN-436", "BUILTIN-46", "BUILTIN-5", "BUILTIN-53", "BUILTIN-57", "BUILTIN-92", "BUILTIN-99", "EXTERNAL-1"],
      "type": "string"
    },
    "dataFinding": {
      "additionalProperties": false,
      "properties": {
        "dataCategory": {
          "$ref": "#/$defs/dataCategory"        },
        "dataClassifierId": {
          "$ref": "#/$defs/dataClassifier"
        },
        "externalFindingLink": {
          "type": "string"
        },
        "id": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "severity": {
          "$ref": "#/$defs/severity"
        },
        "source": {
          "deprecated": true,
          "type": "string"
        }
      },
      "required": ["name", "dataCategory", "dataClassifierId"],
      "type": "object"
    },
    "dataSource": {
      "additionalProperties": false,
      "properties": {
        "analysisDate": {
          "format": "date-time",
          "type": "string"
        },
        "assets": {
          "items": {
            "$ref": "#/$defs/asset"
          },
          "type": "array"
        },
        "id": {
          "type": "string"
        }
      },
      "required": ["id", "assets"],
      "type": "object"
    },
    "severity": {
      "enum": ["None", "Low", "Medium", "High", "Critical"],
      "type": "string"
    }
  },
  "$id": "https://wiz.io/ingestionmodel.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "properties": {
    "dataSources": {
      "items": {
        "$ref": "#/$defs/dataSource"
      },
      "type": "array"
    },
    "integrationId": {
      "type": "string"
    }
  },
  "required": ["integrationId", "dataSources"],
  "title": "Wiz Ingestion Model",
  "type": "object"
}
```

## Schema fields

The schema fields define the structure and required information for Data Findings in Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

### Root Level Fields

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                          |
| ----------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId** | `String` | Required     | The unique ID for each Wiz integration.<ul><li>For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.</li><li>For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> |
| **dataSources**   | `Array`  | Required     | Contains an array of data sources. Each data source is an object.                                                                                                                                        |

### Data Source Fields

`dataSources[]`

| **Field**        | **Type**          | **Required** | **Description**                                                                                                                      |
| ---------------- | ----------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **id**           | `String`          | Required     | The ID that uniquely identifies asset findings within a tenant and integration ID. Can be subscription ID.                           |
| **analysisDate** | `ISO 8601 string` | Optional     | The date the scan was performed.                                                                                                     |
| **assets**       | `Array`           | Required     | List of assets included in the data source. Each asset is an object. [See supported assets](#supported-cloud-assets-and-identifier). |

### Asset Fields

`dataSources[].assets[]`

| **Field**           | **Type** | **Required** | **Description**                                                                     |
| ------------------- | -------- | ------------ | ----------------------------------------------------------------------------------- |
| **assetIdentifier** | `Object` | Required     | Contains identifiers for a specific asset.                                          |
| **networkAddress**  | `String` | Optional     | The IP address of the asset.                                                        |
| **endpointURL**     | `String` | Optional     | The Endpoint URL of the asset.                                                      |
| **dataFindings**    | `Array`  | Required     | Contains an array of data findings related to the asset. Each finding is an object. |

### Asset Identifier Fields

`dataSources[].assets[].assetIdentifier`

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                                                                               |
| ----------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **cloudPlatform** | `String` | Required     | The cloud platform that was scanned. Possible values: "AWS", "Azure", "GCP", "OCI", "Alibaba Cloud", "Linode".                                                                                                                                                |
| **providerId**    | `String` | Required     | A unique identifier assigned to a specific cloud asset by the cloud service provider when the asset is created, allowing for the identification and differentiation of the asset within the cloud computing ecosystem. Includes ARN—AWS, Resource group—Azure |

### Data Findings

`dataSources[].assets[].dataFindings[]`

| **Field**               | **Type** | **Required** | **Description**                                                                                             |
| ----------------------- | -------- | ------------ | ----------------------------------------------------------------------------------------------------------- |
| **id**                  | `String` | Required     | The unique ID of the discovered data finding.                                                               |
| **name**                | `String` | Required     | The name of the data finding classifier, for example, Bank Account Number.                                  |
| **severity**            | `String` | Required     | The severity of the data finding. Possible values: "info", "Low", "Medium", "High", "Critical".             |
| **externalFindingLink** | `String` | Optional     | A link to the source of the external finding.                                                               |
| **dataCategory**        | `String` | Required     | The category of the data finding. Possible values: "PII", "PHI", "Financial", "DigitalIdentity", "Other".   |
| **dataClassifierId**    | `String` | Required     | The Classification Rule ID. [See the list of supported Classification Rule IDs](dev:data-classifier-types). |
| **source**              | `String` | Required     | The name of the product that detected the finding.                                                          |

## Example

This example JSON payload demonstrates how to format Data Findings properly for submission to Wiz. It illustrates key fields and their proper usage.

```json Example
{
  "integrationId": "wizt-12345",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-8CB96C2BC202D055",
      "analysisDate": "2023-06-08T08:50:00Z",
      "assets": [
        {
          "assetIdentifier": {
            "cloudPlatform": "GCP",
            "providerId": "https://www.googleapis.com/storage/v1/b/s456456456"
          },
          "dataFindings": [
            {
              "id": "17",
              "name": "GDPR - Personal Sensitive test1",
              "source": "ParnterX",
              "externalFindingLink": "https://test.123",
              "severity": "Low",
              "dataCategory": "PII",
              "dataClassifierId": "LineageGuid1"
            },
            {
              "id": "12",
              "name": "Electronic PII",
              "source": "ParnterX",
              "externalFindingLink": "https://test.123",
              "severity": "Medium",
              "dataCategory": "PHI"
            }
          ]
        },
        {
          "assetIdentifier": {
            "cloudPlatform": "AWS",
            "providerId": "arn:aws:ec2:us-west-2:1234234234:instance/i-0c345634565"
          },
          "dataFindings": [
            {
              "id": "13",
              "name": "CreaditCard - Personal Sensitive",
              "source": "ParnterX",
              "externalFindingLink": "https://test.1236",
              "severity": "High",
              "dataCategory": "Financial",
              "dataClassifierId": "LineageGuid2"
            },
            {
              "id": "14",
              "name": "CreaditCard - Personal Sensitive",
              "source": "ParnterX",
              "externalFindingLink": "https://test.123",
              "severity": "Critical",
              "dataCategory": "DigitalIdentity",
              "dataClassifierId": "LineageGuid3"
            }
          ]
        }
      ]
    }
  ]
}
```

## Supported Classification Rule IDs

[See the list of Wiz-defined Classifier Rule IDs for Data Findings](dev:data-classifier-types).

:::info

If you don't find a match, insert "EXTERNAL-1".

:::
