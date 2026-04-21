# Vulnerability Findings Schema
*Enrich Wiz by uploading all your vulnerability findings with a simplified process.*

Category: enrichment

Vulnerability Finding enrichment is designed for third-party vendors capable of conducting periodic scans. It's tailored to enhance Wiz's risk management by integrating external CVE scanners. The scans, with the Wiz Security Graph, correlate findings to the appropriate cloud assets.

A key feature of this integration is a simplified process for uploading findings. Instead of first pulling all relevant resources and matching findings to them, partners can now upload findings with sufficient identifying information about the asset. If the asset exists in Wiz, the finding will be attached to it; if it does not, the asset will be created.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with Vulnerability Findings and the required identifier.

| Supported resources (entity name)                                                                         | Required Identifier                |
| :-------------------------------------------------------------------------------------------------------- | :--------------------------------- |
| <ul><li>`VIRTUAL_MACHINE`</li><li> `NETWORK_ADDRESS`</li><li> `APPLICATION_ENDPOINT`</li></ul> | Based on the [asset details](#asset-details) |

## Finding life cycle

The finding life cycle shows how vulnerability data flows from external scanners through the Wiz platform, from initial discovery to remediation tracking. This visualization helps understand how your scan data integrates with Wiz's security workflows.

<Findinglifecycle />

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema

The schema defines the JSON structure expected by Wiz's API. Understanding this schema is essential for creating valid payloads that will be properly processed and incorporated into Wiz.

```json Schema
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://wiz.io/ingestionmodel.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "integrationId",
    "dataSources"
  ],
  "properties": {
    "integrationId": {
      "type": "string"
    },
    "dataSources": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/dataSource"
      }
    }
  },
  "$defs": {
    "dataSource": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "assets"
      ],
      "properties": {
        "id": {
          "type": "string"
        },
        "analysisDate": {
          "type": "string",
          "format": "date-time"
        },
        "assets": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/asset"
          }
        }
      }
    },
    "asset": {
      "type": "object",
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
          "type": "string",
          "format": "date-time"
        },
        "details": {
          "$ref": "#/$defs/assetDetails"
        },
        "vulnerabilityFindings": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/vulnerabilityFinding"
          }
        }
      }
    },
    "assetDetails": {
      "type": "object",
      "additionalProperties": false,
      "oneOf": [
        {
          "required": ["virtualMachine"]
        },
        {
          "required": ["networkAddress"]
        },
        {
          "required": ["assetEndpoint"]
        }
      ],
      "properties": {
        "networkAddress": {
          "$ref": "#/$defs/assetNetworkAddress"
        },
        "virtualMachine": {
          "$ref": "#/$defs/assetVirtualMachine"
        },
        "assetEndpoint": {
          "$ref": "#/$defs/assetEndpoint"
        }
      }
    },
    "assetNetworkAddress": {
      "type": "object",
      "required": ["assetId", "name", "addressType", "address"],
      "additionalProperties": false,
      "properties": {
        "assetId": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "addressType": {
          "type": "string",
          "enum": ["IPV4", "IPV6", "DNS", "URL"]
        },
        "address": {
          "type": "string"
        },
        "firstSeen": {
          "type": "string",
          "format": "date-time"
        },
        "originalObject": {
          "type": "object"
        },
        "tags": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
    },
    "assetVirtualMachine": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "assetId": {
          "type": "string"
        },
        "biosUUID": {
          "type": "string"
        },
        "cloudPlatformIdentifier": {
          "type": "object",
          "required": ["cloudPlatform"],
          "additionalProperties": false,
          "properties": {
            "cloudPlatform": {
              "type": "string",
              "enum": ["ACK", "AKS", "AWS", "Alibaba", "Azure", "AzureDevOps", "BitbucketCloud", "BitbucketDataCenter", "Cloudflare", "Databricks", "EKS", "Firemon", "GCP", "GKE", "GenericDB", "GitHub", "GitLab", "IBM", "Kubernetes", "LKE", "Linode", "MongoDBAtlas", "OCI", "OKE", "Okta", "OpenAI", "OpenShift", "OpenStack", "Snowflake", "Terraform", "Wiz", "vSphere"]
            },
            "resourceId": {
              "type": "string"
            },
            "vmInstanceId": {
              "type": "string"
            }
          }
        },
        "firstSeen": {
          "type": "string",
          "format": "date-time"
        },
        "fqdns": {
          "description": "Fully qualified domain names",
          "items": {
            "format": "hostname",
            "type": "string"
          },
          "type": "array"
        },
        "hostname": {
          "type": "string"
        },
        "ipAddresses": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "name": {
          "type": "string"
        },
        "networkInterfaces": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "macAddress": {
                "type": "string"
              },
              "name": {
                "type": "string"
              },
              "networkAddresses": {
                "type": "array",
                "items": {
                  "$ref": "#/$defs/assetNetworkAddress"
                }
              }
            }
          }
        },
        "operatingSystem": {
          "type": "string",
          "enum": ["Linux", "Windows", "Unknown", "MacOS"]
        },
        "originalObject": {
          "type": "object"
        },
        "serialNumber": {
          "type": "string"
        },
        "tags": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
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
      }
    },
    "detectionMethod": {
      "type": "string",
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
      ]
    },
    "severity": {
      "type": "string",
      "enum": [
        "None",
        "Low",
        "Medium",
        "High",
        "Critical"
      ]
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
    "targetComponent": {
      "additionalProperties": false,
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
          "title": "targetComponentLibrary"
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
          "title": "targetComponentProduct"
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
        "version": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "vulnerabilityFinding": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "name"
      ],
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
          "type": "string",
          "minLength": 1
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
        "severity": {
          "$ref": "#/$defs/severity"
        },
        "source": {
          "type": "string",
          "deprecated": true
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
      }
    },
    "vulnerabilityFindingPolicyReference": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "policyId",
        "status",
        "firstDetectedAt"
      ],
      "properties": {
        "firstDetectedAt": {
          "type": "string",
          "format": "date-time"
        },
        "policyId": {
          "type": "string"
        },
        "sourceUrl": {
          "type": "string"
        },
        "violationId": {
          "type": "string"
        }
      }
    }
  }
}
```

## Schema fields

The schema fields define the structure and required information for submitting Vulnerability Findings to Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

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

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **details** | `Object` | Required     | Contains identifying information about the asset. |
| **vulnerabilityFindings**    | `Array`  | Required     | Contains the vulnerability findings for the asset.                |

### Asset details fields

`dataSources[].assets[].details`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **networkAddress** | `Object` | Optional     | Contains identifying information for the network address asset. |
| **virtualMachine** | `Object` | Optional     | Contains identifying information for the virtual machine asset. |
| **assetEndpoint** | `Object` | Optional     | Contains identifying information for the asset endpoint. |

### Network Address fields

`dataSources[].assets[].details.networkAddress`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **assetId**                  | `String` | Required     | A unique identifier for the asset.                                                                                            |
| **name**                     | `String` | Required     | The name of the asset. For example, the hostname.                                                                             |
| **addressType**              | `String` | Required     | The type of address. Possible values: "IPV4", "IPV6", "DNS", "URL".                                                             |
| **address**                  | `String` | Required     | The actual network address value (e.g., `192.0.2.1`).                                                                        |
| **firstSeen**                | `String` | Optional     | The first time the asset was seen. Format: `yyyy-MM-ddTHH:mm:ssZ`.                                                             |
| **originalObject**           | `Object` | Optional     | The original object from the source.                                                                                          |
| **tags**                     | `Object` | Optional     | Key-value pairs assigned to the asset for organization.                                                                       |

### Virtual Machine fields

`dataSources[].assets[].details.virtualMachine`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **assetId**                  | `String` | Required     | A unique identifier for the asset.                                                                                            |
| **name**                     | `String` | Required     | The name of the asset. For example, the hostname.                                                                             |
| **cloudPlatformIdentifier**  | `Object` | Optional     | The cloud platform identifier of the virtual machine. See [Cloud Platform Identifier](#cloud-platform-identifier-fields) for more details. |
| **biosUUID**                 | `String` | Optional     | The BIOS UUID of the virtual machine.                                                                                                                                                                      |
| **serialNumber**             | `String` | Optional     | The serial number of the virtual machine.                                                                                       |
| **firstSeen**                | `String` | Optional     | The first time the asset was seen. Format: `yyyy-MM-ddTHH:mm:ssZ`.                                                             |
| **fqdns**                | `Array` | Optional     | Globally unique Fully Qualified Domain Names that resolve to the virtual machine.                                                 |
| **hostname**                     | `String` | Optional     | The hostname of the virtual machine.                                                                                          |
| **ipAddresses**              | `Array`  | Optional     | The IP addresses of the virtual machine.                                                                                       |
| **networkInterfaces**        | `Array`  | Optional     | The network interfaces of the virtual machine. See [Network Interfaces](#network-interface-fields) for more details.                     |
| **operatingSystem**          | `String` | Optional     | The operating system of the virtual machine. Possible values: "Linux", "Windows", "Unknown", "MacOS".                                                                                      |
| **originalObject**           | `Object` | Optional     | The original object from the source.                                                                                          |
| **tags**                     | `Object` | Optional     | Key-value pairs assigned to the asset for organization.                                                                       |

### Asset Endpoint fields

`dataSources[].assets[].details.assetEndpoint`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **assetId**                  | `String` | Optional     | A unique identifier for the asset.                                                                                            |
| **assetName**                | `String` | Optional     | The name of the asset endpoint.                                                                             |
| **firstSeen**                | `String` | Optional     | The first time the asset was seen. Format: `yyyy-MM-ddTHH:mm:ssZ`.                                                             |
| **host**                     | `String` | Optional     | The host of the endpoint.                                                                                          |
| **originalObject**           | `Object` | Optional     | The original object from the source.                                                                                          |
| **port**                     | `Integer` | Optional     | The port number of the endpoint. Valid range: 1-65535.                                                                                       |
| **protocol**                 | `String` | Optional     | The protocol used by the endpoint. Possible values: "HTTP", "HTTPS", "Other", "RDP", "SSH", "WinRM".                                                                       |

### Cloud Platform Identifier fields

`dataSources[].assets[].details.virtualMachine.cloudPlatformIdentifier`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **cloudPlatform**            | `String` | Required     | The cloud platform that was scanned (e.g., AWS, Azure, GCP)                                 |
| **vmInstanceId**             | `String` | Optional     | The unique instance ID assigned by the cloud provider. For example, the EC2 instance ID for AWS.                                                                                           |
| **resourceId**               | `String` | Required     | A unique identifier assigned to a specific cloud asset by the cloud service provider when the asset is created, allowing for the identification and differentiation of the asset within the cloud computing ecosystem. (e.g. ARN—AWS, Resource group—Azure) |

### Network Interface fields

`dataSources[].assets[].details.virtualMachine.networkInterfaces[]`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **macAddress**               | `String` | Optional     | The MAC address of the network interface.                                                                                       |
| **name**                     | `String` | Optional     | The name of the network interface.                                                                                              |
| **networkAddresses**         | `Array`  | Optional     | The network addresses of the network interface. See [Network Addresses](#network-address-fields) for more details.                   |

### Vulnerability Finding fields

`dataSources[].assets[].vulnerabilityFindings[]`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                      |
| --------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **id**                      | `String`  | Optional     | The unique ID of the discovered vulnerability finding.                                                                                                                                                                                                                               |
| **name**                    | `String`  | Required     | The name of the Vulnerability, for example CVE-2021-25288.                                                                                                                                                                                                                           |
| **description**             | `String`  | Optional     | A description of the finding.                                                                                                                                                                                                                                                        |
| **externalDetectionSource** | `String`  | Optional     | The external source type that detected the vulnerability. See the schema for possible values.                                                                                  |
| **externalFindingLink**     | `String`  | Optional     | A link to the source of the external finding.                                                                                                                                                                                                                                        |
| **originalObject**          | `Object`  | Optional     | The original object from the source system.                                                                                                                                                                                                                                        |
| **policyReference**         | `Object`  | Optional     | [Object](#policy-reference-fields) containing details about the policy that caused the vulnerability.                                     |
| **remediation**             | `String`  | Optional     | The remediation for the vulnerability.                                                                                                                                                                                                                                               |
| **severity**                | `String`  | Optional     | The severity of the vulnerability. Possible values: "None", "Low", "Medium", "High", "Critical".                                                                                                                                           |

### Policy Reference fields

`dataSources[].assets[].vulnerabilityFindings[].vulnerabilityFindingPolicyReference`

| **Field**            | **Type** | **Required** | **Description**                                                                                      |
| -------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **policyId**         | `String` | Required     | The unique identifier of the policy that was violated.                                               |
| **firstDetectedAt**  | `String` | Required     | The date and time when the policy violation was first detected, in ISO 8601 format.                  |
| **violationId**      | `String` | Optional     | The unique identifier of the specific policy violation.                                              |
| **sourceUrl**        | `String` | Optional     | A URL linking to more information about the policy or violation in the external system.              |

### Target Component fields

`dataSources[].assets[].vulnerabilityFindings[].targetComponent`

The target component object identifies the specific component affected by the vulnerability. It can be either a library or a product.

| **Field**    | **Type** | **Required** | **Description**                                                                                      |
| ------------ | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **library**  | `Object` | Optional     | [Object](#vulnerable-library-fields) containing details about a vulnerable library component.        |
| **product**  | `Object` | Optional     | [Object](#vulnerable-product-fields) containing details about a vulnerable product component.        |

**Note:** One of `library` or `product` must be provided.

### Vulnerable Library fields

`dataSources[].assets[].vulnerabilityFindings[].targetComponent.library`

| **Field**        | **Type** | **Required** | **Description**                                                                                      |
| ---------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **name**         | `String` | Optional     | The name of the vulnerable library.                                                                  |
| **version**      | `String` | Optional     | The version of the vulnerable library.                                                               |
| **fixedVersion** | `String` | Optional     | The version of the library that fixes the vulnerability.                                             |
| **filePath**     | `String` | Optional     | The file path where the vulnerable library is located.                                               |

### Vulnerable Product fields

`dataSources[].assets[].vulnerabilityFindings[].targetComponent.product`

| **Field**        | **Type** | **Required** | **Description**                                                                                      |
| ---------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **name**         | `String` | Optional     | The name of the vulnerable product.                                                                  |
| **version**      | `String` | Optional     | The version of the vulnerable product.                                                               |
| **fixedVersion** | `String` | Optional     | The version of the product that fixes the vulnerability.                                             |

## Example

This example JSON payload demonstrates how to properly format Vulnerability Findings for submission to Wiz. It shows the practical implementation of the schema for CVE-based package vulnerabilities, illustrating key fields and their proper usage for reporting vulnerable software components.

```json Example
{
  "integrationId": "55c176cc-d155-43a2-98ed-aa56873a1ca1",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-833333333",
      "analysisDate": "2023-09-07T15:50:00Z",
      "assets": [
        {
          "analysisDate": "2025-06-21T16:10:50.870Z",
          "details": {
            "virtualMachine": {
              "originalObject": {
                "test-string": "data"
              },
              "assetId": "Some-vm-123",
              "name": "java-web-server",
              "biosUUID": "ec25b8b2-bc76-5468-4088-b113fe58ee67",
              "operatingSystem": "Windows",
              "ipAddresses": [
                "10.1.2.3"
              ],
              "firstSeen": "2023-01-15T10:30:00Z",
              "fqdns": [
                "web-01.prod.example.com"
              ],
              "tags": {
                "owner": "david",
                "Project": "Cloud Migration"
              }
            }
          },
          "vulnerabilityFindings": [
            {
              "id": "CVE-2024-9506##@vue/compiler-sfc##2.7.16",
              "name": "CVE-2024-9506",
              "description": "A cross-site scripting (XSS) vulnerability in @vue/compiler-sfc allows attackers to execute arbitrary code in the context of the user's browser.",
              "externalDetectionSource": "Library",
              "externalFindingLink": "https://nvd.nist.gov/vuln/detail/CVE-2024-9506",
              "originalObject": {
                "scanner": "example-scanner",
                "scanId": "scan-12345"
              },
              "policyReference": {
                "policyId": "policy-critical-cve",
                "firstDetectedAt": "2024-10-15T08:30:00Z",
                "violationId": "violation-98765",
                "sourceUrl": "https://example.com/policies/critical-cve"
              },
              "remediation": "Update @vue/compiler-sfc to a newer version than 2.7.16",
              "severity": "High",
              "targetComponent": {
                "library": {
                  "name": "@vue/compiler-sfc",
                  "version": "2.7.16",
                  "fixedVersion": "2.7.17",
                  "filePath": "/app/node_modules/@vue/compiler-sfc"
                }
              },
              "validatedAtRuntime": true
            }
          ]
        }
      ]
    }
  ]
}
```

## (Optional) Generate a description

In order to generate a helpful description string (as seen in the image below), use the following structure and variables:

```
The {detectionMethod} `{detailedName}` version `{version}` in `{PIP/NPN and etc}` located at `{file_plath}` and is vulnerable to  `{CVE}`. which exists in version < `{Fix version}`.

The vulnerability was found in the `{}` with vendor severity `{severity}`.

The vulnerability can be remediated by updating the library to version `{fix version}` or higher, using `{remediation command}`.
```

The following image shows an example vulnerability finding in Wiz that includes a description of the vulnerability:

<Vulfindingswizportal />

![Example of a Vulnerability Finding with a description.](https://docs-assets.wiz.io/images/data-findings-schema-draft-208aa1a-Untitled.webp)
