# DAST & Attack Surface Findings Schema
*JSON schema reference for integrating third-party DAST and attack surface vulnerability findings into Wiz, including field definitions and examples.*

Category: enrichment

Dynamic Application Security Testing (DAST) enrichment is designed for third-party vendors capable of conducting dynamic vulnerability scans on
attack surfaces. It's tailored to enhance Wiz's risk management by integrating external CWE & CVE scanners. The scans, with the Wiz Security Graph, 
correlate findings to the appropriate cloud assets.

A key feature of this integration is a simplified process for uploading findings. Instead of first pulling all relevant resources and matching 
findings to them, partners can now upload findings with sufficient identifying information about the asset. If the asset exists in Wiz, the finding 
is attached to it.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with DAST Vulnerability Findings and the required identifying information.

| Supported resources (entity name) | Required Identifier                |
| --------------------------------- | ---------------------------------- |
| <ul><li>`APPLICATION_ENDPOINT`</li></ul>      | Based on the [asset details](#asset-details-fields)    |

Application endpoints are an internally-defined Wiz inventory item that defines a discovered external exposure. Partners and customers can add findings to existing application endpoints by using identifiers as described in the schema.

External exposures discovered outside of Wiz can be nominated for validation and added as application endpoints in the system. When an external exposure is nominated, Wiz scans for it and adds the endpoint if found. In this case, Wiz drops the information initially uploaded for nomination, and replaces it with information from its own scan.

If an application endpoint isn't reachable by the Wiz scanner, the item associated with it is dropped and not added to the system.

## Finding life cycle

The finding life cycle describes how vulnerability data flows from external scanners through the Wiz platform, from initial
discovery to remediation tracking. The following table outlines the finding life cycle:

| Finding step                    | Description                                                                                                                                                                                                                                        |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **File upload frequency**       | <ul><li>We recommend to upload files every 24 hours to align with Wiz's scanning cycle. Regardless, findings that aren't refreshed within 7 days will be removed.</li></ul>                                                                        |
| **Data source organization**    | <ul><li>All findings must be categorized under the appropriate "Data Source". Data Source helps breaking down the customer environment to more manageable sections. Each section should be mutually exclusive and consistent.</li></ul>            |
| **Event scanning support**      | <ul><li>Supports 24-hour cycle scans and event-triggered scans.</li><li>Results from event-triggered scans can be uploaded every 5 minutes.</li></ul>                                                                                              |
| **Vulnerability reporting**     | <ul><li>For each Vulnerability Finding you upload based on its unique ID, Wiz will mark it as "unresolved".</li><li>Only report existing vulnerabilities. If a vulnerability has been fixed, omit that finding ID from your next upload.</li></ul> |
| **Automatic resolution in Wiz** | <ul><li>Unreported vulnerabilities are automatically marked as "resolved".</li><li>Associated Issues for unreported vulnerabilities are also marked as "resolved".</li></ul>                                                                       |

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema

The schema defines the JSON structure expected by Wiz's API. Understanding this schema is essential for creating valid payloads.

:::info

The Attack Surface enrichment schema uses the `assetDetails` object for endpoint identification.

:::

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
        "attackSurfaceFindings": {
          "items": {
            "$ref": "#/$defs/attackSurfaceFinding"
          },
          "type": "array"
        },
        "details": {
          "$ref": "#/$defs/assetDetails"
        },
        "vulnerabilityFindings": {
          "items": {
            "$ref": "#/$defs/vulnerabilityFinding"
          },
          "type": "array"
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
        },
        "vulnerabilityFindingPolicies": {
          "items": {
            "$ref": "#/$defs/vulnerabilityFindingPolicy"
          },
          "type": "array"
        }
      },
      "required": [
        "id",
        "assets"
      ],
      "type": "object"
    },
    "vulnerabilityFindingPolicy": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "type": "string"
        },
        "name": {
          "minLength": 1,
          "type": "string"
        },
        "policyId": {
          "type": "string"
        },
        "remediation": {
          "type": "string"
        },
        "severity": {
          "$ref": "#/$defs/severity"
        }
      },
      "required": [
        "policyId",
        "name",
        "severity"
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
    "attackSurfaceFinding": {
      "additionalProperties": false,
      "properties": {
        "assessmentDetails": {
          "type": "string"
        },
        "description": {
          "type": "string"
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
        "remediation": {
          "type": "string"
        },
        "severity": {
          "$ref": "#/$defs/severity"
        },
        "type": {
          "$ref": "#/$defs/attackSurfaceFindingType"
        },
        "vulnerabilities": {
          "items": {
            "pattern": "(?i)^(cve-\\d+)",
            "type": "string"
          },
          "type": "array"
        },
        "weaknesses": {
          "items": {
            "pattern": "^CWE-\\d+$",
            "type": "string"
          },
          "type": "array"
        }
      },
      "required": [
        "id",
        "name",
        "description",
        "assessmentDetails",
        "remediation",
        "severity",
        "externalFindingLink",
        "type"
      ],
      "type": "object"
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
    "vulnerabilityFinding": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "type": "string"
        },
        "detailedName": {
          "deprecated": true,
          "type": "string"
        },
        "externalDetectionSource": {
          "$ref": "#/$defs/detectionMethod"
        },
        "externalFindingLink": {
          "type": "string"
        },
        "fixedVersion": {
          "deprecated": true,
          "type": "string"
        },
        "id": {
          "type": "string"
        },
        "name": {
          "minLength": 1,
          "type": "string"
        },
        "originalObject": {
          "type": "object"
        },
        "policyReference": {
          "$ref": "#/$defs/vulnerabilityFindingPolicyReference"
        },
        "remediation": {
          "type": "string"
        },
        "scaFinding": {
          "$ref": "#/$defs/scaFinding"
        },
        "severity": {
          "$ref": "#/$defs/severity"
        },
        "source": {
          "deprecated": true,
          "type": "string"
        },
        "targetComponent": {
          "$ref": "#/$defs/targetComponent"
        },
        "validatedAtRuntime": {
          "type": "boolean"
        },
        "version": {
          "deprecated": true,
          "type": "string"
        }
      },
      "required": [
        "name"
      ],
      "type": "object"
    },
    "detectionMethod": {
      "enum": [
        "Package",
        "DefaultPackage",
        "Library",
        "ConfigFile",
        "OpenPort",
        "StartupService",
        "Configuration",
        "ClonedRepository",
        "OS",
        "ArtifactsOnDisk",
        "WindowsRegistry",
        "InstalledProgram",
        "FilePath",
        "WindowsService",
        "InstalledProgramByService",
        "HostedDatabaseScan",
        "ExternalNetworkScan",
        "CloudAPI",
        "ThirdPartyAgent",
        "AIModel",
        "SASTScan",
        "IDEExtension"
      ],
      "type": "string"
    },
    "vulnerabilityFindingPolicyReference": {
      "additionalProperties": false,
      "properties": {
        "evidence": {
          "type": "string"
        },
        "firstDetectedAt": {
          "format": "date-time",
          "type": "string"
        },
        "policyId": {
          "type": "string"
        },
        "sourceUrl": {
          "type": "string"
        },
        "status": {
          "$ref": "#/$defs/vulnerabilityFindingPolicyStatus"
        },
        "violationId": {
          "type": "string"
        },
        "violationSeverity": {
          "$ref": "#/$defs/severity"
        }
      },
      "required": [
        "policyId",
        "status",
        "firstDetectedAt"
      ],
      "type": "object"
    },
    "scaFinding": {
      "additionalProperties": false,
      "properties": {
        "codeLanguage": {
          "$ref": "#/$defs/scaCodeLibraryLanguage"
        },
        "filePath": {
          "deprecated": true,
          "type": "string"
        },
        "reachability": {
          "$ref": "#/$defs/vulnerabilityReachability"
        }
      },
      "type": "object"
    },
    "targetComponent": {
      "oneOf": [
        {
          "additionalProperties": false,
          "properties": {
            "library": {
              "$ref": "#/$defs/vulnerableLibrary"
            }
          },
          "required": [
            "library"
          ],
          "title": "TargetComponentLibrary"
        },
        {
          "additionalProperties": false,
          "properties": {
            "product": {
              "$ref": "#/$defs/vulnerableProduct"
            }
          },
          "required": [
            "product"
          ],
          "title": "TargetComponentProduct"
        }
      ],
      "type": "object"
    },
    "vulnerableLibrary": {
      "additionalProperties": false,
      "properties": {
        "filePath": {
          "type": "string"
        },
        "fixedVersion": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "version": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "vulnerableProduct": {
      "additionalProperties": false,
      "properties": {
        "fixedVersion": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "packageManager": {
          "$ref": "#/$defs/linuxPackageManager"
        },
        "version": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "linuxPackageManager": {
      "enum": [
        "Yum",
        "Apt",
        "Apk",
        "Portage",
        "Zypper",
        "Nix",
        "Snap",
        "Homebrew",
        "KB",
        "VIB",
        "NonManaged"
      ],
      "type": "string"
    },
    "scaCodeLibraryLanguage": {
      "enum": [
        "C#",
        "Golang",
        "Java",
        "Javascript",
        "PHP",
        "Python",
        "Ruby",
        "Rust",
        "Swift"
      ],
      "type": "string"
    },
    "vulnerabilityReachability": {
      "enum": [
        "Unsupported",
        "Unknown",
        "NotReachable",
        "Reachable"
      ],
      "type": "string"
    },
    "vulnerabilityFindingPolicyStatus": {
      "enum": [
        "Open",
        "Resolved",
        "InProgress"
      ],
      "type": "string"
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
    },
    "attackSurfaceFindingType": {
      "enum": [
        "Misconfiguration",
        "DefaultCredentials",
        "ExploitabilityValidation",
        "DAST"
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

The schema fields define the structure and required information for submitting DAST Vulnerability Findings to Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

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
| **isEnrichmentOnly** | `Boolean`       | Optional     | Indicates whether this data source is for enrichment only.                                                                           |
| **vulnerabilityFindingPolicies** | `Array`           | Optional     | List of [Vulnerability Finding policies](#vulnerability-finding-policy-fields) for the data source. |

### Asset fields

`dataSources[].assets[]`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **analysisDate** | `ISO 8601 string` | Optional     | The date and time when the scan was performed, in ISO 8601 format: `yyyy-MM-ddTHH:mm:ssZ`. |
| **details** | `Object` | Optional     | Contains identifying information about the asset. See Asset details below. |
| **attackSurfaceFindings**    | `Array`  | Optional     | Contains the [Attack Surface Findings](#attack-surface-finding-fields) for the asset.                |
| **vulnerabilityFindings**    | `Array`  | Optional     | Contains the [Vulnerability Findings](#vulnerability-finding-fields) for the asset.                |

### Asset details fields

`dataSources[].assets[].details`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **endpoint** | `Object` | Required     | Contains identifying information for the endpoint. |

### Asset Endpoint fields

`dataSources[].assets[].details.endpoint`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **assetId**                  | `String` | Required     | A unique identifier for the asset.                                                                                            |
| **assetName**                | `String` | Required     | The name of the asset endpoint.                                                                             |
| **firstSeen**                | `String` | Optional     | The first time the asset was seen. Format: `yyyy-MM-ddTHH:mm:ssZ`.                                                             |
| **host**                     | `String` | Required     | The host of the endpoint.                                                                                          |
| **originalObject**           | `Object` | Optional     | The original object from the source.                                                                                          |
| **port**                     | `Integer` | Required     | The port number of the endpoint. Valid range: 1-65535.                                                                                       |
| **protocol**                 | `String` | Required     | The protocol used by the endpoint. Possible values: "HTTP", "HTTPS", "Other", "RDP", "SSH", "WinRM".                                                                       |

### Attack Surface Finding fields

`dataSources[].assets[].attackSurfaceFindings[]`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **id**                      | `String`  | Required     | The unique ID of the discovered Attack Surface Finding.                                                                                                                                                                                                                               |
| **name**                    | `String`  | Required     | The name of the finding.                                                                                                                                                                                                           |
| **description**             | `String`  | Required     | A description of the finding.                                                                                                                                                                                                                                                        |
| **assessmentDetails** | `String`  | Required     | Details about the assessment that discovered the finding.                                                                                  |
| **remediation**             | `String`  | Required     | The remediation for the finding.                                                                                                                                                                                                                                               |
| **severity**                | `String`  | Required     | The severity of the finding. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                                                                                           |
| **type** | `String`  | Required     | The type of Attack Surface Finding. Possible values:<br/>- `Misconfiguration`: A misconfigured service<br/>- `DefaultCredentials`: Default credentials<br/>- `ExploitabilityValidation`: A specific CVE that is externally validated<br/>- `DAST`: A general weakness that has been tested and confirmed, e.g. a QAL injection|
| **externalFindingLink**     | `String`  | Required     | A link to the source of the external finding.                                                                                                                                                                                                                                        |
| **vulnerabilities** | `Array`  | Optional     | An array of CVE identifiers associated with the finding. Each value must match the pattern `(?i)^(cve-\\d+)`. |
| **weaknesses** | `Array`  | Optional     | An array of CWE identifiers associated with the finding. Each value must match the pattern `^CWE-\\d+$`. |

### Vulnerability Finding fields

`dataSources[].assets[].vulnerabilityFindings[]`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **name**                    | `String`  | Required     | The name of the Vulnerability Finding.                                                                                                                                                                                                           |
| **id**                      | `String`  | Optional     | The unique ID of the Vulnerability Finding.                                                                                                                                                                                                                               |
| **description**             | `String`  | Optional     | A description of the Vulnerability Finding.                                                                                                                                                                                                                                                        |
| **remediation**             | `String`  | Optional     | The remediation for the finding.                                                                                                                                                                                                                                               |
| **severity**                | `String`  | Optional     | The severity of the finding. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                                                                                           |
| **externalFindingLink**     | `String`  | Optional     | A link to the source of the external finding.                                                                                                                                                                                                                                        |
| **externalDetectionSource** | `String`  | Optional     | The detection method. Possible values: "Package", "DefaultPackage", "Library", "ConfigFile", "OpenPort", "StartupService", "Configuration", "ClonedRepository", "OS", "ArtifactsOnDisk", "WindowsRegistry", "InstalledProgram", "FilePath", "WindowsService", "InstalledProgramByService", "HostedDatabaseScan", "ExternalNetworkScan", "CloudAPI", "ThirdPartyAgent", "AIModel", "SASTScan", "IDEExtension". |
| **policyReference**         | `Object`  | Optional     | Reference to a [Vulnerability Finding policy](#vulnerability-finding-policy-reference-fields).                                                                                                                                                                                                                                        |
| **scaFinding**              | `Object`  | Optional     | Contains [SCA finding details](#sca-finding-fields).                                                                                                                                                                                                                                        |
| **targetComponent**         | `Object`  | Optional     | The [target component](#target-component-fields) affected by the vulnerability.                                                                                                                                                                                                                                        |
| **validatedAtRuntime**      | `Boolean` | Optional     | Indicates whether the finding was validated at runtime.                                                                                                                                                                                                                                        |
| **originalObject**          | `Object`  | Optional     | The original object from the source.                                                                                                                                                                                                                                        |
| **detailedName**            | `String`  | Optional     | Deprecated. A detailed name for the finding.                                                                                                                                                                                                                                        |
| **fixedVersion**            | `String`  | Optional     | Deprecated. The version that fixes the vulnerability.                                                                                                                                                                                                                                        |
| **source**                  | `String`  | Optional     | Deprecated. The source of the finding.                                                                                                                                                                                                                                        |
| **version**                 | `String`  | Optional     | Deprecated. The version of the affected component.                                                                                                                                                                                                                                        |

### Vulnerability Finding Policy Reference fields

`dataSources[].assets[].vulnerabilityFindings[].policyReference`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **policyId**                | `String`  | Required     | The ID of the referenced policy.                                                                                                                                                                                                                                                         |
| **status**                  | `String`  | Required     | The status of the policy violation. Possible values: "Open", "Resolved", "InProgress".                                                                                                                                                                                                                                                              |
| **firstDetectedAt**         | `ISO 8601 string`  | Required     | The date and time when the violation was first detected. Format: `yyyy-MM-ddTHH:mm:ssZ`.                                                                                                                                                                                                                                                         |
| **evidence**                | `String`  | Optional     | Evidence supporting the finding.                                                                                                                                                                                                                                                         |
| **sourceUrl**               | `String`  | Optional     | URL to the source of the finding.                                                                                                                                                                                                                                                      |
| **violationId**             | `String`  | Optional     | The unique ID of the violation.                                                                                                                                                                                                                                                            |
| **violationSeverity**       | `String`  | Optional     | The severity of the violation. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                                                                                                                                            |

### SCA Finding fields

`dataSources[].assets[].vulnerabilityFindings[].scaFinding`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **codeLanguage**            | `String`  | Optional     | The programming language. Possible values: "C#", "Golang", "Java", "Javascript", "PHP", "Python", "Ruby", "Rust", "Swift".                                                                                                                                                                                                                                                         |
| **filePath**                | `String`  | Optional     | The file path of the SCA finding.                                                                                                                                                                                                                                                              |

### Target Component fields

`dataSources[].assets[].vulnerabilityFindings[].targetComponent`

The target component is a oneOf type that can be either a library or a product.

#### Library target component

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **library.name**            | `String`  | Optional     | The name of the vulnerable library.                                                                                                                                                                                                                                                         |
| **library.version**         | `String`  | Optional     | The version of the vulnerable library.                                                                                                                                                                                                                                                              |
| **library.fixedVersion**    | `String`  | Optional     | The version that fixes the vulnerability.                                                                                                                                                                                                                                                         |
| **library.filePath**        | `String`  | Optional     | The file path of the library.                                                                                                                                                                                                                                                      |

#### Product target component

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **product.name**            | `String`  | Optional     | The name of the vulnerable product.                                                                                                                                                                                                                                                         |
| **product.version**         | `String`  | Optional     | The version of the vulnerable product.                                                                                                                                                                                                                                                              |
| **product.fixedVersion**    | `String`  | Optional     | The version that fixes the vulnerability.                                                                                                                                                                                                                                                         |
| **product.packageManager**  | `String`  | Optional     | The Linux package manager. Possible values: "Yum", "Apt", "Apk", "Portage", "Zypper", "Nix", "Snap", "Homebrew", "KB", "VIB", "NonManaged".                                                                                                                                                                                                                                                      |

### Vulnerability Finding Policy fields

`dataSources[].vulnerabilityFindingPolicies[]`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **policyId**                | `String`  | Required     | The unique ID of the policy.                                                                                                                                                                                                                                                         |
| **name**                    | `String`  | Required     | The name of the policy.                                                                                                                                                                                                                                                              |
| **description**             | `String`  | Optional     | A description of the policy.                                                                                                                                                                                                                                                         |
| **remediation**             | `String`  | Optional     | The remediation for the policy.                                                                                                                                                                                                                                                      |
| **severity**                | `String`  | Required     | The severity of the policy. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                                                                                                                                            |

## Example

This example JSON payload demonstrates how to properly format DAST Vulnerability Findings for submission to Wiz. It shows the practical implementation of the schema for Attack Surface Findings, illustrating key fields and their proper usage for reporting security issues discovered during dynamic application security testing.

```json Example
{
  "integrationId": "5f8f3594-3294-483b-b5e9-713b7e9212cb",
  "dataSources": [
    {
      "id": "scanner-instance-alpha",
      "analysisDate": "2023-10-27T14:30:00Z",
      "assets": [
        {
          "analysisDate": "2023-10-27T14:30:00Z",
          "details": {
            "endpoint": {
              "assetId": "srv-prod-055",
              "assetName": "Production Web Server",
              "firstSeen": "2023-01-15T08:00:00Z",
              "host": "192.168.10.55",
              "port": 443,
              "protocol": "HTTPS"
            }
          },
          "attackSurfaceFindings": [
            {
              "id": "FIND-2023-001",
              "name": "Weak SSL/TLS Cipher Suites",
              "description": "The remote web server supports the use of weak SSL/TLS cipher suites.",
              "assessmentDetails": "Detected support for RC4 and 3DES suites on port 443.",
              "remediation": "Reconfigure the web server to disable weak ciphers and protocols.",
              "severity": "Medium",
              "type": "Misconfiguration",
              "externalFindingLink": "https://my.app/vuln/detail/FIND-2023-001",
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

## Generate finding description

Creating descriptive, informative Vulnerability Findings helps security teams understand and prioritize findings. Use the following template and variables for generating consistent, actionable descriptions that display effectively in the Wiz portal.

```
The vulnerability`{Name}`  was found in the  `{Details Name}` with vendor severity `{severity}`.

The vulnerability can be remediated by running  `{Remediation}`
```

More information:

<Expandable title="Vulnerability Findings visibility in the Wiz portal">

<Vulfindingswizportal />

</Expandable>

<Expandable title="Finding description example in Wiz">

The following image shows an example Vulnerability Finding in Wiz that includes a description of the vulnerability:

![](https://docs-assets.wiz.io/images/application-vulnerability-findings-schema-a103494-Screenshot_2023-10-08_at_11.46.07.webp)

</Expandable>
