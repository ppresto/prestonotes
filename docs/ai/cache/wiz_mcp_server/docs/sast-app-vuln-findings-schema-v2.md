# SAST Application Vulnerability Findings Schema
*JSON schema reference for integrating third-party SAST source code vulnerability findings into Wiz, including field definitions and examples.*

Category: enrichment

:::success[Wiz customers]

Wiz customers that want to use this integration must enable Wiz UVM on the [ Settings > Preview & Migration Hub](https://app.wiz.io/settings/preview-hub) page.

:::

Static Application Security Testing (SAST) findings enrichment is designed for third-party vendors that can scan source code for security vulnerabilities. It's tailored to enhance Wiz's risk management by integrating external SAST scanners. The scans, combined with the Wiz Security Graph, correlate findings to the appropriate cloud assets.

A key feature of this integration is a simplified process for uploading findings. Instead of first pulling all relevant resources and matching findings to them, partners can now upload findings with sufficient identifying information about the asset. If the asset exists in Wiz, the finding will be attached to it; if it does not, the asset will be created.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with SAST Application Vulnerability Findings and the required identifying information.

| Supported resources (entity name)     | Required Identifier                         |
| ------------------------------------- | ------------------------------------------- |
| <ul><li>`REPOSITORY_BRANCH`</li></ul> | Asset Details for the repository or branch. |

## Managing data sources

Correctly managing your data sources is critical for ensuring the accurate lifecycle of vulnerability findings. An inconsistent approach can cause active findings to be resolved incorrectly.

A dataSource should represent a stable, logical group of assets that are scanned together. For example, you might use a single `dataSource` ID for all repositories belonging to a specific business unit or all assets scanned by a particular scanner instance.

:::info

To ensure ASPM accuracy when sending findings, ensure that all results for a specific scan type within a repository are directed to a single `dataSource`.

- **Correct**: All SAST findings for all branches of `repo-A` are in a single `dataSource`.
- **Incorrect**: SAST findings for `repo-A` are split between `dataSource-1` and `dataSource-2`.

You can have more than one type of finding in a data source.

:::

The key is consistency. An asset and its findings should always be reported within the same `dataSource` in every upload.

:::warning[Avoid Data Source Hopping]

If you report a finding for an asset in dataSource-A in one upload, and then report that same asset and finding in dataSource-B in a subsequent upload, Wiz will consider the finding to be missing from dataSource-A and incorrectly mark it as "Resolved".

:::

## Finding life cycle

The following table outlines the finding life cycle for SAST vulnerability data.

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

The SAST Application enrichment schema uses the `assetDetails` object for repository branch identification, similar to the SCA Application enrichment schema.

:::

```json Schema
{
  "$defs": {
    "SASTCodeLibraryLanguage": {
      "enum": ["Java", "Python", "Javascript", "Csharp", "Php", "Go", "Ruby", "Rust", "Clojure", "Swift", "Hcl", "Scala", "Solidity", "Typescript", "Regex", "Ocaml", "Generic", "Yaml", "Html", "Terraform", "Sh", "Dockerfile", "C", "Json", "Kotlin", "Lua", "Julia", "Cpp", "Xml", "Dart", "Lisp", "R", "Scheme", "Apex", "Cairo", "Elixir", "Jsonnet"],
      "type": "string"
    },
    "asset": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": ["details"],
          "title": "details"
        }
      ],
      "properties": {
        "analysisDate": {
          "format": "date-time",
          "type": "string"
        },
        "details": {
          "$ref": "#/$defs/assetDetails"
        },
        "sastFindings": {
          "items": {
            "$ref": "#/$defs/sastFindingV2"
          },
          "type": "array"
        }
      },
      "type": "object"
    },
    "assetDetails": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": ["repositoryBranch"],
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
      "required": ["repository", "vcs", "assetId", "assetName", "branchName"],
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
      "required": ["name", "url"],
      "type": "object"
    },
    "sastFindingV2": {
      "additionalProperties": false,
      "properties": {
        "codeLibraryLanguages": {
          "items": {
            "$ref": "#/$defs/SASTCodeLibraryLanguage"
          },
          "type": "array"
        },
        "commitHash": {
          "type": "string"
        },
        "commitURL": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "endColumn": {
          "minimum": 1,
          "type": "integer"
        },
        "endLine": {
          "minimum": 1,
          "type": "integer"
        },
        "externalFindingLink": {
          "type": "string"
        },
        "filePath": {
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
        "snippet": {
          "type": "string"
        },
        "startColumn": {
          "minimum": 1,
          "type": "integer"
        },
        "startLine": {
          "minimum": 1,
          "type": "integer"
        },
        "weaknesses": {
          "items": {
            "pattern": "^CWE-\\d+$",
            "type": "string"
          },
          "type": "array"
        }
      },
      "required": ["id", "name", "severity"],
      "type": "object"
    },
    "severity": {
      "enum": ["None", "Low", "Medium", "High", "Critical"],
      "type": "string"
    },
    "vcs": {
      "enum": ["AzureDevOps", "BitbucketCloud", "BitbucketDataCenter", "GitHub", "GitLab", "Terraform"],
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

The schema fields define the structure and required information for submitting SAST Application Vulnerability Findings to Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

### Root Level Fields

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                          |
| ----------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId** | `String` | Required     | The unique ID for each Wiz integration.<ul><li>For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.</li><li>For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> |
| **dataSources**   | `Array`  | Required     | Contains an array of data sources. Each data source is an object.                                                                                                                                        |

### Data Source Fields

`dataSources[]`

| **Field**  | **Type** | **Required** | **Description**                                                                    |
| ---------- | -------- | ------------ | ---------------------------------------------------------------------------------- |
| **id**     | `String` | Required     | The ID that uniquely identifies asset findings within a tenant and integration ID. |
| **assets** | `Array`  | Required     | List of assets included in the data source.                                        |

### Asset Fields

`dataSources[].assets[]`

| **Field**                    | **Type** | **Required** | **Description**                                                   |
| ---------------------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **details.repositoryBranch** | `Object` | Required     | Contains identifying information for the repository branch asset. |
| **sastFindings**             | `Array`  | Required     | Contains the SAST vulnerability findings for the asset.           |

### Repository Branch Details

`dataSources[].assets[].details.repositoryBranch`

| **Field**           | **Type** | **Required** | **Description**                                                                                                                                                                                                                                                                                                                      |
| ------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **assetId**         | `String` | Required     | A unique identifier for the asset.                                                                                                                                                                                                                                                                                                   |
| **assetName**       | `String` | Required     | The name of the asset.                                                                                                                                                                                                                                                                                                               |
| **branchName**      | `String` | Required     | The name of the repository branch (e.g., main).                                                                                                                                                                                                                                                                                      |
| **firstSeen**       | `String` | Optional     | The date and time when the asset was first seen, in ISO 8601 format (e.g., "2024-09-26T04:35:11.750Z").                                                                                                                                                                                                                              |
| **lastSeen**        | `String` | Optional     | The date and time when the asset was last seen, in ISO 8601 format (e.g., "2025-06-21T16:10:50.870Z").                                                                                                                                                                                                                               |
| **repository.name** | `String` | Required     | The name of the repository (e.g., myorg/secure-app).                                                                                                                                                                                                                                                                                 |
| **repository.url**  | `String` | Required     | The full URL of the repository. For example:<br/><br/><ul><li>Github: `https://github.com/myorg/secure-app`</li><li>Gitlab: `https://gitlab.com/myorg/secure-app`</li><li>Bitbucket: `https://bitbucket.org/myorg/secure-app`</li><li>Bitbucket datacenter: `https://bitbucket.company.com/projects/PROJ/repos/secure-app`</li></ul> |
| **vcs**             | `String` | Required     | The version control system. Possible values: GitHub, GitLab, AzureDevOps, BitbucketCloud, BitbucketDataCenter.                                                                                                                                                                                                                       |

### SAST Findings

`dataSources[].assets[].sastFindings[]`

| **Field**                | **Type**  | **Required** | **Description**                                                                                               |
| ------------------------ | --------- | ------------ | ------------------------------------------------------------------------------------------------------------- |
| **id**                   | `String`  | Required     | The unique ID of the discovered vulnerability finding (e.g., CWE-89##123352145).                              |
| **name**                 | `String`  | Required     | The name of the vulnerability (e.g., Unsafe Cryptographic Cipher Mode Usage).                                 |
| **severity**             | `String`  | Required     | The severity of the vulnerability. Possible values: "None", "Low", "Medium", "High", "Critical".              |
| **filePath**             | `String`  | Required     | The path to the file in the repository where the vulnerability was found (e.g., `test_runner/blog/tests.py`). |
| **description**          | `String`  | Optional     | Detailed description of the vulnerability.                                                                    |
| **remediation**          | `String`  | Optional     | Remediation guidance for fixing the vulnerability.                                                            |
| **weaknesses**           | `Array`   | Optional     | Array of CWE (Common Weakness Enumeration) identifiers (e.g., ["CWE-89"]).                                    |
| **commitHash**           | `String`  | Optional     | The commit hash where the vulnerability was detected.                                                         |
| **commitURL**            | `String`  | Optional     | URL to the specific commit where the vulnerability was detected.                                              |
| **externalFindingLink**  | `String`  | Optional     | A URL to the finding in the external tool for more details.                                                   |
| **startLine**            | `Integer` | Optional     | The line number where the vulnerability starts (minimum value: 1).                                            |
| **endLine**              | `Integer` | Optional     | The line number where the vulnerability ends (minimum value: 1).                                              |
| **codeLibraryLanguages** | `Array`   | Optional     | Programming languages detected in the code (e.g., ["Python"]).                                                |

## Example

This example JSON payload demonstrates how to format SAST vulnerability findings for submission to Wiz.

```json Example
{
  "integrationId": "55c176cc-d155-43a2-98ed-aa56873a1ca1",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-833333343",
      "analysisDate": "2023-09-07T15:50:00Z",
      "assets": [
        {
          "analysisDate": "2025-06-21T16:10:50.870Z",
          "details": {
            "repositoryBranch": {
              "assetId": "090cfd15-5098-4f91-96e4-92eabf45ab26",
              "assetName": "example-org/secure-app:main",
              "branchName": "main",
              "isDefault": true,
              "firstSeen": "2024-09-26T04:35:11.750Z",
              "lastSeen": "2025-06-21T16:10:50.870Z",
              "repository": {
                "name": "example-org/secure-app",
                "url": "https://github.com/example-org/secure-app",
                "isPublic": false,
                "isArchived": false,
                "isDisabled": false,
                "labels": ["production", "security-critical"]
              },
              "vcs": "GitHub"
            }
          },
          "sastFindings": [
            {
              "id": "CWE-327##a1b2c3d4e5f6",
              "name": "Unsafe Cryptographic Cipher Mode Usage",
              "severity": "High",
              "description": "The application uses ECB mode for encryption, which does not provide semantic security. ECB mode encrypts identical plaintext blocks into identical ciphertext blocks, making it vulnerable to pattern analysis attacks.",
              "remediation": "Replace ECB mode with a secure cipher mode such as GCM or CBC with proper IV handling. Use AES-256-GCM for authenticated encryption or AES-256-CBC with HMAC for encryption with separate authentication.",
              "weaknesses": ["CWE-327"],
              "filePath": "src/crypto/encryption_utils.py",
              "startLine": 45,
              "endLine": 48,
              "startColumn": 5,
              "endColumn": 42,
              "commitHash": "a1b2c3d4e5f67890abcdef1234567890abcdef12",
              "commitURL": "https://github.com/example-org/secure-app/commit/a1b2c3d4e5f67890abcdef1234567890abcdef12",
              "externalFindingLink": "https://scanner.example.com/findings/a1b2c3d4e5f6",
              "codeLibraryLanguages": ["Python"],
              "snippet": "cipher = AES.new(key, AES.MODE_ECB)\nencrypted = cipher.encrypt(data)"
            },
            {
              "id": "CWE-89##b2c3d4e5f6g7",
              "name": "SQL Injection Vulnerability",
              "severity": "Critical",
              "description": "User-controlled input is directly concatenated into a SQL query without proper sanitization or parameterization, allowing attackers to inject arbitrary SQL commands.",
              "remediation": "Use parameterized queries or prepared statements instead of string concatenation. Replace the current implementation with SQLAlchemy's parameter binding or use ORM methods that automatically handle parameterization.",
              "weaknesses": ["CWE-89", "CWE-943"],
              "filePath": "src/database/user_queries.py",
              "startLine": 112,
              "endLine": 114,
              "startColumn": 9,
              "endColumn": 65,
              "commitHash": "b2c3d4e5f67890abcdef1234567890abcdef1234",
              "commitURL": "https://github.com/example-org/secure-app/commit/b2c3d4e5f67890abcdef1234567890abcdef1234",
              "externalFindingLink": "https://scanner.example.com/findings/b2c3d4e5f6g7",
              "codeLibraryLanguages": ["Python"],
              "snippet": "query = \"SELECT * FROM users WHERE username = '\" + username + \"'\"\nresult = db.execute(query)"
            },
            {
              "id": "CWE-798##c3d4e5f6g7h8",
              "name": "Hardcoded Credentials",
              "severity": "High",
              "description": "Hardcoded credentials were found in the source code. This poses a significant security risk as the credentials are exposed to anyone with access to the codebase.",
              "remediation": "Remove hardcoded credentials from the source code. Use environment variables, secure configuration management systems, or secret management services like AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault.",
              "weaknesses": ["CWE-798"],
              "filePath": "src/config/database_config.py",
              "startLine": 23,
              "endLine": 23,
              "commitHash": "c3d4e5f67890abcdef1234567890abcdef123456",
              "commitURL": "https://github.com/example-org/secure-app/commit/c3d4e5f67890abcdef1234567890abcdef123456",
              "externalFindingLink": "https://scanner.example.com/findings/c3d4e5f6g7h8",
              "codeLibraryLanguages": ["Python"]
            }
          ]
        }
      ]
    }
  ]
}
```

## CWEs Supported by Wiz

Wiz supports a wide range of Common Weakness Enumeration (CWE) identifiers for enrichment.

<Cwes />

## Generate finding description

Creating descriptive, informative vulnerability findings helps security teams understand and prioritize findings. Use the following template and variables for generating consistent, actionable descriptions that display effectively in the Wiz portal.

```
The SAST vulnerability `{Name}` with severity `{severity}` was found in file `{filePath}` at line {startLine}.

{Description}

The vulnerability can be remediated by: {Remediation}
```

More information:

<Expandable title="Vulnerability Findings visibility in the Wiz portal">

<Vulfindingswizportal />

</Expandable>

<Expandable title="Finding description example in Wiz">

The following image shows an example SAST Vulnerability Finding in Wiz that includes a description of the vulnerability with code location details:

![](https://docs-assets.wiz.io/images/cwe-finding-example-in-wiz-360442c7.webp)

</Expandable>
