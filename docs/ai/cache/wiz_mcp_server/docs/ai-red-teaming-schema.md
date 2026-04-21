# AI Red Team Findings Schema
*JSON schema reference for integrating third-party AI red team findings into Wiz, including field definitions and examples for adversarial simulation results on AI endpoints.*

Category: enrichment

AI Red Team Findings enrichment is designed for third-party vendors capable of performing adversarial simulations on a customer's public-facing AI endpoints to test the security of AI workloads. The third-party can then upload the results to Wiz. This maps risks such as prompt injections and model hallucinations directly to the exposed assets, allowing for correlated risk visibility.

## Workflow

Uploading Red Team Findings is a two-step process:

1. **Discovery**: Pull the list of [Application Endpoints](dev:get-application-endpoints) from Wiz to identify valid targets.

2. **Assessment & Upload**: Perform attack simulations on these specific endpoints and upload the findings using the schema below.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with AI Findings and the required identifying information.

| Supported resources (entity name) | Required Identifier                |
| --------------------------------- | ---------------------------------- |
| <ul><li>`APPLICATION_ENDPOINT`</li></ul>      | Based on the [asset details](#asset-details-fields)    |

Application endpoints are an internally-defined Wiz inventory item that defines a discovered external exposure. Partners and customers can add findings to existing application endpoints by using identifiers as described in the schema.

External exposures discovered outside of Wiz can be nominated for validation and added as application endpoints in the system. When an external exposure is nominated, Wiz scans for it and adds the endpoint if found. In this case, Wiz drops the information initially uploaded for nomination, and replaces it with information from its own scan.

If an application endpoint isn't reachable by the Wiz scanner, the item associated with it is dropped and not added to the system.

## Finding life cycle

The finding life cycle describes how vulnerability data flows from external scanners through the Wiz platform, from initial discovery to remediation tracking. The following table outlines the finding life cycle:

| Finding step                    | Description                                                                                                                                                                                                                                        |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **File upload frequency**       | <ul><li>We recommend to upload files every 24 hours to align with Wiz's scanning cycle. Regardless, findings that aren't refreshed within 7 days will be removed.</li></ul>                                                                        |
| **Data source organization**    | <ul><li>All findings must be categorized under the appropriate "Data Source". Data Source helps breaking down the customer environment to more manageable sections. Each section should be mutually exclusive and consistent.</li></ul>            |
| **Event scanning support**      | <ul><li>Supports 24-hour cycle scans and event-triggered scans.</li><li>Results from event-triggered scans can be uploaded every 5 minutes.</li></ul>                                                                                              |
| **AI Finding reporting**        | <ul><li>For each AI Finding you upload based on its unique ID, Wiz will mark it as "unresolved".</li><li>Only report existing vulnerabilities. If an AI finding has been fixed, omit that finding ID from your next upload.</li></ul>              |
| **Automatic resolution in Wiz** | <ul><li>Unreported vulnerabilities are automatically marked as "resolved".</li><li>Associated Issues for unreported vulnerabilities are also marked as "resolved".</li></ul>                                                                       |

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema

The schema defines the JSON structure expected by Wiz's API. Understanding this schema is essential for creating valid payloads.

```json Schema
{
  "$defs": {
    "asset": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": [
            "details"
          ],
          "title": "details"
        }
      ],
      "properties": {
        "analysisDate": {
          "format": "date-time",
          "type": "string"
        },
        "aiSecurityFindings": {
          "items": {
            "$ref": "#/$defs/aiSecurityFinding"
          },
          "type": "array"
        },
        "details": {
          "$ref": "#/$defs/assetDetails"
        }
      },
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
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "id",
        "assets"
      ],
      "type": "object"
    },
    "severity": {
      "enum": [
        "None",
        "Low",
        "Medium",
        "High",
        "Critical"
      ],
      "type": "string"
    },
    "aiSecurityFinding": {
      "additionalProperties": false,
      "properties": {
        "category": {
          "$ref": "#/$defs/aiSecurityFindingCategory"
        },
        "description": {
          "minLength": 1,
          "type": "string"
        },
        "evidence": {
          "minLength": 1,
          "type": "string"
        },
        "externalFindingLink": {
          "minLength": 1,
          "type": "string"
        },
        "id": {
          "minLength": 1,
          "type": "string"
        },
        "name": {
          "minLength": 1,
          "type": "string"
        },
        "severity": {
          "$ref": "#/$defs/severity"
        }
      },
      "required": [
        "id",
        "name",
        "severity",
        "category",
        "evidence",
        "externalFindingLink",
        "description"
      ],
      "type": "object"
    },
    "aiSecurityFindingCategory": {
      "enum": [
        "ModelRisk",
        "AgentRisk",
        "McpRisk",
        "ModelAssessment",
        "RedTeaming",
        "AiCompliance"
      ],
      "type": "string"
    },
    "assetDetails": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": [
            "endpoint"
          ],
          "title": "assetDetailsEndpoint"
        }
      ],
      "properties": {
        "endpoint": {
          "$ref": "#/$defs/assetEndpoint"
        }
      },
      "type": "object"
    },
    "assetEndpoint": {
      "additionalProperties": false,
      "properties": {
        "assetId": {
          "minLength": 1,
          "type": "string"
        },
        "assetName": {
          "minLength": 1,
          "type": "string"
        },
        "firstSeen": {
          "format": "date-time",
          "type": "string"
        },
        "host": {
          "minLength": 1,
          "type": "string"
        },
        "originalObject": {
          "type": "object"
        },
        "path": {
          "type": "string"
        },
        "port": {
          "maximum": 65535,
          "minimum": 1,
          "type": "integer"
        },
        "protocol": {
          "$ref": "#/$defs/protocol"
        }
      },
      "required": [
        "assetId",
        "assetName",
        "host",
        "port",
        "protocol"
      ],
      "type": "object"
    },
    "protocol": {
      "enum": [
        "HTTP",
        "HTTPS",
        "Other",
        "RDP",
        "SSH",
        "WinRM"
      ],
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
      "minLength": 1,
      "type": "string"
    }
  },
  "required": [
    "integrationId",
    "dataSources"
  ],
  "title": "Wiz Ingestion Model",
  "type": "object"
}
```

## Schema fields

The following tables breakdown the schema fields and their requirements.

### Root level fields

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                          |
| ----------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId** | `String` | Required     | The unique ID for each Wiz integration.<ul><li>For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.</li><li>For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> |
| **dataSources**   | `Array`  | Required     | Contains an array of data sources. Each data source is an object.                                                                                                                                        |

### Data source fields

`dataSources[]`

| **Field**        | **Type**          | **Required** | **Description**                                                                                                                      |
| ---------------- | ----------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **id**           | `String`          | Required     | The ID that uniquely identifies asset findings within a tenant and integration ID. Can be a subscription ID.                         |
| **analysisDate** | `ISO 8601 string` | Optional     | The date and time when the scan was performed, in ISO 8601 format: `yyyy-MM-ddTHH:mm:ssZ`.                                           |
| **assets**       | `Array`           | Required     | List of assets included in the data source. Each asset is an object. [See supported assets](#supported-cloud-assets-and-identifier). |

### Asset fields

`dataSources[].assets[]`

| **Field**              | **Type**          | **Required** | **Description**                                                                             |
| ---------------------- | ----------------- | ------------ | ------------------------------------------------------------------------------------------- |
| **analysisDate**       | `ISO 8601 string` | Optional     | The date and time when the scan was performed, in ISO 8601 format: `yyyy-MM-ddTHH:mm:ssZ`.  |
| **details**            | `Object`          | Optional     | Contains identifying information about the asset. See [Asset details](#asset-details-fields) below. |
| **aiSecurityFindings** | `Array`           | Optional     | Contains the [AI Findings](#ai-security-findings-fields) for the asset.                                                     |

### Asset details fields

`dataSources[].assets[].details`

| **Field**    | **Type** | **Required** | **Description**                              |
| ------------ | -------- | ------------ | -------------------------------------------- |
| **endpoint** | `Object` | Required     | Contains identifying information for the [endpoint](#asset-endpoint-fields). |

### Asset Endpoint fields

`dataSources[].assets[].details.endpoint`

| **Field**          | **Type**  | **Required** | **Description**                                                                              |
| ------------------ | --------- | ------------ | -------------------------------------------------------------------------------------------- |
| **assetId**        | `String`  | Required     | A unique identifier for the asset.                                                           |
| **assetName**      | `String`  | Required     | The name of the asset endpoint.                                                              |
| **firstSeen**      | `String`  | Optional     | The first time the asset was seen. Format: `yyyy-MM-ddTHH:mm:ssZ`.                           |
| **host**           | `String`  | Required     | The host of the endpoint.                                                                    |
| **path**           | `String`  | Optional     | The path of the endpoint.                                                                    |
| **originalObject** | `Object`  | Optional     | The original object from the source.                                                         |
|  **path**          | `String`  | Optional     | The path of the endpoint.<br/><br/>**Note**: The Application Endpoints API does not return a separate path field. For endpoints with a path component (e.g. https://example.com:443/api), parse the path from the name field by stripping the protocol://host:port prefix, and pass it in the enrichment schema's endpoint path field.                                                                    |
| **port**           | `Integer` | Required     | The port number of the endpoint. Valid range: 1-65535.                                       |
| **protocol**       | `String`  | Required     | The protocol used by the endpoint. Possible values: "HTTP", "HTTPS", "Other", "RDP", "SSH", "WinRM". |

### AI Security Findings fields

`dataSources[].assets[].aiSecurityFindings[]`

| **Field**               | **Type** | **Required** | **Description**                                                                                                                                                       |
| ----------------------- | -------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **id**                  | `String` | Required     | The unique ID of the discovered AI Finding.                                                                                                                           |
| **name**                | `String` | Required     | The name of the finding.                                                                                                                                              |
| **description**         | `String` | Required     | A description of the finding.                                                                                                                                         |
| **severity**            | `String` | Required     | The severity of the finding. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                            |
| **category**            | `String` | Required     | The type of AI Findings Category. Possible values: "ModelRisk", "AgentRisk", "McpRisk", "ModelAssessment", "RedTeaming", "AiCompliance".                              |
| **evidence**            | `String` | Required     | Evidence of the AI Finding.                                                                                                                                           |
| **externalFindingLink** | `String` | Required     | A link to the source of the external finding.                                                                                                                         |

## Example

This example JSON payload demonstrates how to properly format AI Findings for submission to Wiz.

```json Example
{
  "integrationId": "55c176cc-d155-43a2-98ed-aa56873a1ca1",
  "dataSources": [
    {
      "id": "ingestionmodel-attacksurface2",
      "analysisDate": "2025-04-08T10:30:00Z",
      "assets": [
        {
          "details": {
            "endpoint": {
              "assetId": "example-asset-id",
              "assetName": "example site!",
              "host": "wiki.exampleofexamples.com",
              "port": 443,
              "path": "/ai-agent",
              "protocol": "HTTPS",
              "firstSeen": "2025-04-08T10:30:00Z",
              "originalObject": {}
            }
          },
          "aiSecurityFindings": [
            {
              "id": "finding-1",
              "name": "Prompt Injection Vulnerability",
              "severity": "High",
              "category": "ModelAssessment",
              "evidence": "Model accepted malicious prompt without filtering",
              "externalFindingLink": "https://partner.example.com/findings/1",
              "description": "The model endpoint is vulnerable to prompt injection attacks"
            }
          ]
        }
      ]
    }
  ]
}
```
