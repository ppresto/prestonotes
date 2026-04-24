# SCA Application Vulnerability Findings Schema
*JSON schema reference for integrating third-party SCA open-source component vulnerability findings into Wiz, including field definitions and examples.*

Category: enrichment

:::success[Wiz customers]

Wiz customers that want to use this integration must enable Wiz UVM on the [ Settings > Preview & Migration Hub](https://app.wiz.io/settings/preview-hub) page.

:::

Software Composition Analysis (SCA) findings enrichment is designed for third-party vendors that can scan for vulnerabilities in open-source software components. It's tailored to enhance Wiz's risk management by integrating external SCA scanners. The scans, combined with the Wiz Security Graph, correlate findings to the appropriate cloud assets.

A key feature of this integration is a simplified process for uploading findings. Instead of first pulling all relevant resources and matching findings to them, partners can now upload findings with sufficient identifying information about the asset. If the asset exists in Wiz, the finding will be attached to it; if it does not, the asset will be created.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with SCA Application Vulnerability Findings and the required identifying information.

| Supported resources (entity name)     | Required Identifier                         |
| ------------------------------------- | ------------------------------------------- |
| <ul><li>`REPOSITORY_BRANCH`</li></ul> | Asset Details for the repository or branch. |

## Managing data sources

Correctly managing your data sources is critical for ensuring the accurate lifecycle of vulnerability findings. An inconsistent approach can cause active findings to be resolved incorrectly.

A dataSource should represent a stable, logical group of assets that are scanned together. For example, you might use a single `dataSource` ID for all repositories belonging to a specific business unit or all assets scanned by a particular scanner instance.

:::info

To ensure ASPM accuracy when sending findings, ensure that all results for a specific scan type within a repository are directed to a single `dataSource`.

- **Correct**: All SCA findings for all branches of `repo-A` are in a single `dataSource`.
- **Incorrect**: SCA findings for `repo-A` are split between `dataSource-1` and `dataSource-2`.

You can have more than one type of finding in a data source.

:::

The key is consistency. An asset and its findings should always be reported within the same `dataSource` in every upload.

:::warning[Avoid Data Source Hopping]

If you report a finding for an asset in dataSource-A in one upload, and then report that same asset and finding in dataSource-B in a subsequent upload, Wiz will consider the finding to be missing from dataSource-A and incorrectly mark it as "Resolved".

:::

## Finding life cycle

The following table outlines the finding life cycle for SCA vulnerability data.

| Finding step                    | Description                                                                                                                                                                                                                                        |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **File upload frequency**       | <ul><li>We recommend to upload files every 24 hours to align with Wiz's scanning cycle. Regardless, findings that aren't refreshed within 7 days will be removed.</li></ul>                                                                        |
| **Data source organization**    | <ul><li>All findings must be categorized under the appropriate "Data Source". Data Source helps breaking down the customer environment to more manageable sections. Each section should be mutually exclusive and consistent.</li></ul>            |
| **Event scanning support**      | <ul><li>Supports 24-hour cycle scans and event-triggered scans (e.g., on a new commit).</li><li>Results from event-triggered scans can be uploaded every 5 minutes.</li></ul>                                                                      |
| **Vulnerability reporting**     | <ul><li>For each vulnerability finding you upload based on its unique ID, Wiz will mark it as "unresolved".</li><li>Only report existing vulnerabilities. If a vulnerability has been fixed, omit that finding ID from your next upload.</li></ul> |
| **Automatic resolution in Wiz** | <ul><li>Unreported vulnerabilities are automatically marked as "resolved".</li><li>Associated Issues for unreported vulnerabilities are also marked as "resolved".</li></ul>                                                                       |

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema

The schema defines the JSON structure expected by Wiz's API. Understanding this schema is essential for creating valid payloads.

:::info

Unlike the other Vulnerability Finding enrichment schemas (DAST & ASM, SAST Application, etc.), the SCA Application enrichment schema uses the `assetDetails` object instead of the `assetIdentifier` (which will be deprecated).

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
        "isEnrichmentOnly": {
          "type": "boolean"
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
    "assetDetails": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": [
            "repositoryBranch"
          ],
          "title": "assetDetailsRepositoryBranch"
        }
      ],
      "properties": {
        "repositoryBranch": {
          "$ref": "#/$defs/assetRepositoryBranch"
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
    "assetRepositoryBranch": {
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
        "branchName": {
          "minLength": 1,
          "type": "string"
        },
        "firstSeen": {
          "format": "date-time",
          "type": "string"
        },
        "isDefault": {
          "type": "boolean"
        },
        "lastSeen": {
          "format": "date-time",
          "type": "string"
        },
        "originalObject": {
          "type": "object"
        },
        "repository": {
          "$ref": "#/$defs/repository"
        },
        "vcs": {
          "$ref": "#/$defs/vcs"
        }
      },
      "required": [
        "repository",
        "vcs",
        "assetId",
        "assetName",
        "branchName"
      ],
      "type": "object"
    },
    "repository": {
      "additionalProperties": false,
      "properties": {
        "isArchived": {
          "type": "boolean"
        },
        "isDisabled": {
          "type": "boolean"
        },
        "isPublic": {
          "type": "boolean"
        },
        "labels": {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        "name": {
          "minLength": 1,
          "type": "string"
        },
        "url": {
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "name",
        "url"
      ],
      "type": "object"
    },
    "vcs": {
      "enum": [
        "AzureDevOps",
        "BitbucketCloud",
        "BitbucketDataCenter",
        "GitHub",
        "GitLab",
        "Terraform"
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

The schema fields define the structure and required information for submitting SCA Application Vulnerability Findings to Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

### Root Level Fields

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                          |
| ----------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId** | `String` | Required     | The unique ID for each Wiz integration.<ul><li>For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.</li><li>For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> |
| **dataSources**   | `Array`  | Required     | Contains an array of data sources. Each data source is an object.                                                                                                                                        |

### Data Source fields

`dataSources[]`

| **Field**                       | **Type**  | **Required** | **Description**                                                                    |
| ------------------------------- | --------- | ------------ | ---------------------------------------------------------------------------------- |
| **id**                          | `String`  | Required     | The ID that uniquely identifies asset findings within a tenant and integration ID. |
| **assets**                      | `Array`   | Required     | List of assets included in the data source.                                        |
| **analysisDate**                | `String`  | Optional     | The date and time of the analysis, in ISO 8601 format.                             |
| **isEnrichmentOnly**            | `Boolean` | Optional     | Set this flag to tell Wiz to ingest a resource but no finding. Uploads with this flag are not counted in pricing, but will fail if a user tries to upload it as a finding.                            |
| **vulnerabilityFindingPolicies** | `Array`   | Optional     | List of [vulnerability finding policies](#vulnerability-finding-policy-fields) for the data source. |

### Asset fields

`dataSources[].assets[]`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **details.repositoryBranch** | `Object` | Required     | Details about the [repository branch](#repository-branch-fields) asset. |
| **vulnerabilityFindings**    | `Array`  | Required     | Contains the [vulnerability findings](#vulnerability-finding-fields) for the asset.                |

### Vulnerability Finding Policy fields

`dataSources[].vulnerabilityFindingPolicies[]`

| **Field**       | **Type** | **Required** | **Description**                                                                                      |
| --------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **policyId**    | `String` | Required     | The unique identifier of the policy.                                                                 |
| **name**        | `String` | Required     | The name of the policy.                                                                              |
| **severity**    | `String` | Required     | The severity of the policy. Possible values: "None", "Low", "Medium", "High", "Critical".            |
| **description** | `String` | Optional     | A description of the policy.                                                                         |
| **remediation** | `String` | Optional     | Remediation guidance for the policy violation.                                                       |

### Repository Branch fields

`dataSources[].assets[].details.repositoryBranch`

| **Field**          | **Type**  | **Required** | **Description**                                                                                             |
| ------------------ | --------- | ------------ | ----------------------------------------------------------------------------------------------------------- |
| **assetId**        | `String`  | Required     | A unique identifier for the asset.                                                                          |
| **assetName**      | `String`  | Required     | The name of the asset.                                                                                      |
| **branchName**     | `String`  | Required     | The name of the repository branch (e.g., main).                                                             |
| **repository**     | `Object`  | Required     | [Object](#repository-fields) containing details about the repository.                                       |
| **vcs**            | `String`  | Required     | The version control system. Possible values: GitHub, GitLab, AzureDevOps, BitbucketCloud, BitbucketDataCenter, Terraform. |
| **firstSeen**      | `String`  | Optional     | The date and time when the asset was first seen, in ISO 8601 format (e.g., "2024-09-26T04:35:11.750Z").     |
| **isDefault**      | `Boolean` | Optional     | Indicates if this is the default branch.                                                                    |
| **lastSeen**       | `String`  | Optional     | The date and time when the asset was last seen, in ISO 8601 format (e.g., "2025-06-21T16:10:50.870Z").      |
| **originalObject** | `Object`  | Optional     | The original object from the source.                                                                        |

### Repository fields

`dataSources[].assets[].details.repositoryBranch.repository`

| **Field**      | **Type**  | **Required** | **Description**                                                                                                                                                                                                                                                                                                                                                          |
| -------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **name**       | `String`  | Required     | The name of the repository (e.g., areionsectest/golden-image-node).                                                                                                                                                                                                                                                                                                      |
| **url**        | `String`  | Required     | The full URL of the repository. For example:<br/><br/><ul><li>Github: `https://github.com/test-wiz-sec/web-testing-app`</li><li>Gitlab: `https://gitlab.com/iac-test2/terraform/Connect`</li><li>Bitbucket: `https://bitbucket.org/wiz-io/fake_commited_secrets`</li><li>Bitbucket datacenter: `https://bitbucket.wcode.bmrf.io/projects/PUB/repos/sample_repo`</li></ul> |
| **isArchived** | `Boolean` | Optional     | Indicates if the repository is archived.                                                                                                                                                                                                                                                                                                                                 |
| **isDisabled** | `Boolean` | Optional     | Indicates if the repository is disabled.                                                                                                                                                                                                                                                                                                                                 |
| **isPublic**   | `Boolean` | Optional     | Indicates if the repository is public.                                                                                                                                                                                                                                                                                                                                   |
| **labels**     | `Array`   | Optional     | List of labels associated with the repository.                                                                                                                                                                                                                                                                                                                           |

### Vulnerability Finding fields

`dataSources[].assets[].vulnerabilityFindings[]`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                                              |
| --------------------------- | --------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **name**                    | `String`  | Required     | The name of the vulnerability (e.g., CVE-2024-9506).                                                                         |
| **description**             | `String`  | Optional     | The description of the vulnerability finding.                                                                                |
| **externalDetectionSource** | `String`  | Optional     | The detection method that discovered the vulnerability. See the schema for possible values.                                  |
| **externalFindingLink**     | `String`  | Optional     | A link to the source of the external finding.                                                                                |
| **id**                      | `String`  | Optional     | The unique ID of the discovered vulnerability finding.                                                                       |
| **originalObject**          | `Object`  | Optional     | The original object from the source.                                                                                         |
| **policyReference**         | `Object`  | Optional     | [Object](#policy-reference-fields) containing details about the policy that caused the vulnerability.                        |
| **remediation**             | `String`  | Optional     | Remediation guidance for the vulnerability.                                                                                  |
| **scaFinding**              | `Object`  | Optional     | [Object](#sca-finding-fields) containing SCA-specific finding information.                                                   |
| **severity**                | `String`  | Optional     | The severity of the vulnerability. Possible values: "None", "Low", "Medium", "High", "Critical".                             |
| **targetComponent**         | `Object`  | Optional     | [Object](#target-component-fields) identifying the specific component affected by the vulnerability.                         |
| **validatedAtRuntime**      | `Boolean` | Optional     | Indicates if the vulnerability was validated at runtime.                                                                     |

### Policy Reference fields

`dataSources[].assets[].vulnerabilityFindings[].policyReference`

| **Field**             | **Type** | **Required** | **Description**                                                                                        |
| --------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------ |
| **policyId**          | `String` | Required     | The unique identifier of the policy that was violated.                                                 |
| **status**            | `String` | Required     | The status of the policy violation. Possible values: "Open", "Resolved", "InProgress".                 |
| **firstDetectedAt**   | `String` | Required     | The date and time when the policy violation was first detected, in ISO 8601 format.                    |
| **evidence**          | `String` | Optional     | Evidence supporting the policy violation.                                                              |
| **sourceUrl**         | `String` | Optional     | A URL linking to more information about the policy or violation in the external system.                |
| **violationId**       | `String` | Optional     | The unique identifier of the specific policy violation.                                                |
| **violationSeverity** | `String` | Optional     | The severity of the violation. Possible values: "None", "Low", "Medium", "High", "Critical".           |

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

| **Field**          | **Type** | **Required** | **Description**                                                                                                                                              |
| ------------------ | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **name**           | `String` | Optional     | The name of the vulnerable product.                                                                                                                          |
| **version**        | `String` | Optional     | The version of the vulnerable product.                                                                                                                       |
| **fixedVersion**   | `String` | Optional     | The version of the product that fixes the vulnerability.                                                                                                     |
| **packageManager** | `String` | Optional     | The package manager for the product. Possible values: "Yum", "Apt", "Apk", "Portage", "Zypper", "Nix", "Snap", "Homebrew", "KB", "VIB", "NonManaged". |

### SCA Finding fields

`dataSources[].assets[].vulnerabilityFindings[].scaFinding`

| **Field**        | **Type** | **Required** | **Description**                                                                                                                                          |
| ---------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **codeLanguage** | `String` | Optional     | The programming language of the code library. Possible values: "C#", "Golang", "Java", "Javascript", "PHP", "Python", "Ruby", "Rust", "Swift".           |
| **reachability** | `String` | Optional     | The reachability status of the vulnerability. Possible values: "Unsupported", "Unknown", "NotReachable", "Reachable".                                    |

## Example

This example JSON payload demonstrates how to format SCA vulnerability findings for submission to Wiz.

```json Example
{
  "integrationId": "wizt-12345",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-833333333",
      "analysisDate": "2023-09-07T15:50:00Z",
      "assets": [
        {
          "analysisDate": "2025-06-21T16:10:50.870Z",
          "details": {
            "repositoryBranch": {
              "assetId": "090cfd15-5098-4f91-96e4-92eabf45ab26",
              "assetName": "areionsectest/golden-image-node:package1.json",
              "branchName": "main",
              "firstSeen": "2024-09-26T04:35:11.750Z",
              "lastSeen": "2025-06-21T16:10:50.870Z",
              "repository": {
                "name": "areionsectest/golden-image-node",
                "url": "https://github.com/areionsectest/golden-image-node"
              },
              "vcs": "GitHub"
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
              "validatedAtRuntime": true,
              "scaFinding": {
                "filePath": "package1.json"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Generate finding description

Creating descriptive, informative vulnerability findings helps security teams understand and prioritize findings. Use the following template and variables for generating consistent, actionable descriptions that display effectively in the Wiz portal.

```
The vulnerability `{Name}` was found in the `{Details Name}` with vendor severity `{severity}`.

The vulnerability can be remediated by running `{Remediation}`
```

More information:

<Expandable title="Vulnerability Findings visibility in the Wiz portal">

<Vulfindingswizportal />

</Expandable>

<Expandable title="Finding description example in Wiz">

The following image shows an example Vulnerability Finding in Wiz that includes a description of the vulnerability:

![](https://docs-assets.wiz.io/images/cwe-finding-example-in-wiz-360442c7.webp)

</Expandable>
