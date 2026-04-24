# Imported Assets Schema
*Reference documentation for the imported assets enrichment schema, enabling correlation of third-party assets with Wiz-discovered resources.*

Category: enrichment

Asset correlation is how Wiz links Imported Assets from third-party scanners such as Qualys, Tenable, Snyk, and ServiceNow with Wiz-discovered cloud resources to enrich them with more context.

However, if a corresponding resource is not found in Wiz, a new resource is created from the imported data and added to the Security Graph. This ensures complete visibility, even for assets that Wiz has not discovered directly.

For example, for every Wiz-discovered resource (e.g., a single EC2 instance), there can be multiple Imported Assets that represent the same underlying machine. But if an Imported Asset does not have a corresponding Wiz resource, it will be added as a new resource in the Security Graph.

## Imported Assets vs. resources

An Imported Asset represents an external security tool's perspective on a resource. For instance, a Qualys vulnerability scan conducted on an AWS Virtual Machine (VM) generates Qualys's view as an Imported Asset. These external tools often reveal details not directly exposed by cloud providers.

Examples of Imported Assets:

- **Vulnerability Scanners:** Identifying operating system weaknesses or application-level vulnerabilities on a VM or container.
- **Configuration Management Tools:** Providing insights into the configuration state of a resource, such as compliance with security benchmarks or best practices.

Conversely, a Wiz resource is an entity that Wiz directly discovers and monitors within your environment, such as VM, containers, databases, and network components. Wiz collects their configuration and metadata to construct a holistic security context on the Security Graph.

## How it works

Wiz uses a hierarchy of correlation rules to link Imported Assets to their corresponding Wiz resources. This process involves extracting specific identifiers from the Imported Asset's metadata and matching them against identifiers of Wiz-discovered resources. The correlation mechanism prioritizes rules that offer the highest confidence in a match.

### Correlation logic and algorithm

Wiz's correlation logic operates on a sequential basis, processing rules in a predefined, hierarchical order. The algorithm iterates through these ordered rules, attempting to match an Imported Asset with a Wiz resource. A confidence score is assigned to each potential correlation, and the highest-confidence match is selected.

In the event that no correlation rule results in a successful match, the process does not discard the asset. Instead, Wiz will provision a new resource in the Security Graph based on the information provided by the third-party source.

## Supported cloud assets and identifier

This table outlines the supported methods and identifiers for correlating Imported Assets, the types of assets each method applies to, and relevant examples.

### Virtual machines

| Identifier                | Type                | Supported Asset | Description                                                  |
| :------------------------ | :------------------ | :-------------- | :----------------------------------------------------------- |
| `assetId`                 | `string`            | VM              | A unique identifier assigned to the asset.                   |
| `name`                    | `string`            | VM              | The display name of the virtual machine.                     |
| `hostname`                | `string`            | VM              | The hostname of the VM's operating system.                   |
| `ipAddresses`             | `array` of `string` | VM              | A list of IP addresses associated with the VM.               |
| `fqdns`                   | `array` of `string` | VM              | A list of FQDNs associated with the VM.                      |
| `operatingSystem`         | `enum`              | VM              | The operating system running on the virtual machine.         |
| `serialNumber`            | `string`            | VM              | The serial number reported by the VM's BIOS or firmware.     |
| `biosUUID`                | `string`            | VM              | The universally unique identifier (UUID) from the VM's BIOS. |
| `cloudPlatformIdentifier` | `object`            | VM              | An object containing cloud-specific identifiers.             |
| `  ↳ cloudPlatform`       | `enum`              | VM              | The cloud provider (e.g., AWS, GCP, Azure).                  |
| `  ↳ resourceId`          | `string`            | VM              | The unique resource ID from the cloud provider.              |
| `  ↳ vmInstanceId`        | `string`            | VM              | The specific instance ID assigned by the cloud provider.     |
| `originalObject`          | `object`            | VM              | The complete, raw data object from the source API.           |
| `tags`                    | `object`            | VM              | Key-value pairs assigned to the asset for organization.      |
| `firstSeen`               | `date`              | VM              | The timestamp when the asset was first discovered            |

### About `cloudPlatformIdentifier`

The `cloudPlatformIdentifier` field is only used for **cloud-hosted** virtual machines - specifically:

- **AWS** (EC2 instances)
- **Azure** (Azure Virtual Machines)
- **GCP** (Google Compute Engine instances)

If your VM runs **on-prem** or in **private infrastructure** (such as VMware vSphere, Hyper-V, or bare metal), you should not include this field.

When omitted, the system automatically categorizes the asset as **Private Infrastructure**.

Why it matters:

The `cloudPlatformIdentifier` allows us to link your VM to its native cloud metadata—such as resource IDs, instance IDs, and provider-specific tags—for better correlation, tracking, and automation.

## Examples

### Azure machine

- **`resourceId`** = The full **Azure Resource Manager (ARM) ID** of the VM (includes subscription, resource group, provider, and resource name).
- **`vmInstanceId`** = The **Azure VM unique instance ID**, which is different from the resource name and stays the same even if the VM is renamed.

```json Example
{
  "assetId": "vm-az-001",
  "cloudPlatformIdentifier": {
    "cloudPlatform": "Azure",
    "resourceId": "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/rg-prod-vms/providers/Microsoft.Compute/virtualMachines/appserver01",
    "vmInstanceId": "1b6a8c12-34cd-4c9d-91d2-5678d123abcd"
  },
  "name": "appserver01",
  "hostname": "appserver01",
  "ipAddresses": ["10.0.2.4", "52.174.12.45"],
  "operatingSystem": "Windows",
  "firstSeen": "2025-08-14T09:20:15Z",
  "tags": {
    "Environment": "Production",
    "Owner": "Finance"
  }
}

```

### AWS machine

- **`resourceId`** = The **Amazon Resource Name (ARN)** for the EC2 instance.
- **`vmInstanceId`** = The **EC2 instance ID** (e.g., `i-0123456789abcdef0`), the unique identifier AWS assigns to each instance.
```json Example
{
  "assetId": "vm-aws-001",
  "cloudPlatformIdentifier": {
    "cloudPlatform": "AWS",
    "resourceId": "arn:aws:ec2:us-east-1:123456789012:instance/i-0abc123def456gh7",
    "vmInstanceId": "i-0abc123def456gh7"
  },
  "name": "web-backend",
  "hostname": "ec2-ip-172-31-16-45",
  "ipAddresses": ["172.31.16.45", "34.201.56.89"],
  "operatingSystem": "Linux",
  "firstSeen": "2025-08-12T14:05:33Z",
  "tags": {
    "Environment": "Staging",
    "Application": "WebApp"
  }
}

```

### On-prem machine

For on-prem machines, don't use `cloudPlatformIdentifier`. When `cloudPlatformIdentifier` is omitted; it defaults to Private Infrastructure.

### Network address

| Identifier       | Type     | Supported Asset | Description                                                          |
| ---------------- | -------- | --------------- | -------------------------------------------------------------------- |
| `assetId`        | `string` | Network Address | A unique identifier assigned to the asset.                           |
| `name`           | `string` | Network Address | A user-defined name for the network address.                         |
| `address`        | `string` | Network Address | The actual network address value (e.g., `192.0.2.1`).                |
| `addressType`    | `enum`   | Network Address | The type of address. Supported values: `IPV4`, `IPV6`, `DNS`, `URL`. |
| `originalObject` | `object` | Network Address | The complete, raw data object from the source API.                   |
| `tags`           | `object` | Network Address | Key-value pairs assigned to the asset for organization.              |
| `firstSeen`      | `date`   | Network Address | The timestamp when the asset was first discovered.                   |

### Discrepancies and conflict handling

In situations where discrepancies or conflicting information exist between an Imported Asset and a Wiz resource for the same identifier, Wiz prioritizes the information provided by the cloud provider within the Wiz resource.

For example, if a vulnerability scanner reports a different operating system version than what the cloud provider metadata indicates, the cloud provider's information will take precedence for core resource attributes.

However, for specific types of information, such as tags, Wiz adopts a comprehensive approach where all provided values (from both the imported source and Wiz's discovery) are displayed, offering a complete picture.

## Limitations

Limited to 10,000 assets per upload. If you need more, send a request to your WIN contact.

## Schema

The schema defines the JSON structure expected by Wiz's API. Understanding this schema is essential for creating valid payloads that will be properly processed and incorporated into Wiz

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
            "virtualMachine"
          ],
          "title": "assetDetailsVirtualMachine"
        },
        {
          "required": [
            "networkAddress"
          ],
          "title": "assetDetailsNetworkAddress"
        }
      ],
      "properties": {
        "networkAddress": {
          "$ref": "#/$defs/assetNetworkAddress"
        },
        "virtualMachine": {
          "$ref": "#/$defs/assetVirtualMachine"
        }
      },
      "type": "object"
    },
    "assetNetworkAddress": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": [
            "addressType",
            "address",
            "assetId",
            "name"
          ],
          "title": "assetDeprecatedNetworkAddressType"
        },
        {
          "required": [
            "dns",
            "assetId",
            "name"
          ],
          "title": "assetDNSNetworkAddress"
        },
        {
          "required": [
            "url",
            "assetId",
            "name"
          ],
          "title": "assetURLNetworkAddress"
        },
        {
          "required": [
            "ipAddress",
            "assetId",
            "name"
          ],
          "title": "assetIPAddressNetworkAddress"
        }
      ],
      "properties": {
        "address": {
          "deprecated": true,
          "type": "string"
        },
        "addressType": {
          "$ref": "#/$defs/networkAddressType",
          "deprecated": true
        },
        "assetId": {
          "type": "string"
        },
        "cloudPlatform": {
          "$ref": "#/$defs/cloudPlatform"
        },
        "dns": {
          "type": "string"
        },
        "firstSeen": {
          "format": "date-time",
          "type": "string"
        },
        "ipAddress": {
          "type": "string"
        },
        "isPublic": {
          "type": "boolean"
        },
        "name": {
          "type": "string"
        },
        "originalObject": {
          "type": "object"
        },
        "tags": {
          "additionalProperties": {
            "type": "string"
          },
          "type": "object"
        },
        "url": {
          "type": "string"
        },
        "vmCloudInstanceId": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "assetVirtualMachine": {
      "additionalProperties": false,
      "properties": {
        "assetId": {
          "type": "string"
        },
        "biosUUID": {
          "type": "string"
        },
        "cloudPlatformIdentifier": {
          "$ref": "#/$defs/cloudPlatformIdentifier"
        },
        "firstSeen": {
          "format": "date-time",
          "type": "string"
        },
        "fqdns": {
          "description": "Fully qualified domain names",
          "items": {
            "pattern": "^(?:[_a-z0-9](?:[_a-z0-9-]{0,61}[a-z0-9])?\\.)+(?:[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?)?$",
            "type": "string"
          },
          "type": "array"
        },
        "hostname": {
          "type": "string"
        },
        "ipAddresses": {
          "description": "IPv4 or IPv6 addresses",
          "items": {
            "anyOf": [
              {
                "format": "ipv4",
                "type": "string"
              },
              {
                "format": "ipv6",
                "type": "string"
              }
            ],
            "type": "string"
          },
          "type": "array"
        },
        "name": {
          "minLength": 1,
          "type": "string"
        },
        "networkInterfaces": {
          "items": {
            "$ref": "#/$defs/networkInterface"
          },
          "type": "array"
        },
        "operatingSystem": {
          "$ref": "#/$defs/operatingSystem",
          "deprecated": true
        },
        "originalObject": {
          "type": "object"
        },
        "osInfo": {
          "$ref": "#/$defs/oSInfo"
        },
        "serialNumber": {
          "type": "string"
        },
        "tags": {
          "additionalProperties": {
            "type": "string"
          },
          "type": "object"
        }
      },
      "required": [
        "assetId",
        "name",
        "firstSeen"
      ],
      "type": "object"
    },
    "cloudPlatformIdentifier": {
      "additionalProperties": false,
      "properties": {
        "cloudPlatform": {
          "$ref": "#/$defs/cloudPlatform"
        },
        "resourceId": {
          "type": "string"
        },
        "vmInstanceId": {
          "type": "string"
        }
      },
      "required": [
        "cloudPlatform"
      ],
      "type": "object"
    },
    "networkInterface": {
      "additionalProperties": false,
      "anyOf": [
        {
          "required": [
            "name"
          ],
          "title": "networkInterfaceName"
        },
        {
          "required": [
            "macAddress"
          ],
          "title": "networkInterfaceMacAddress"
        },
        {
          "required": [
            "networkAddresses"
          ],
          "title": "networkInterfaceNetworkAddresses"
        }
      ],
      "properties": {
        "macAddress": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "networkAddresses": {
          "items": {
            "$ref": "#/$defs/networkAddress"
          },
          "type": "array"
        }
      },
      "type": "object"
    },
    "operatingSystem": {
      "enum": [
        "Linux",
        "Windows",
        "Unknown",
        "MacOS"
      ],
      "type": "string"
    },
    "oSInfo": {
      "additionalProperties": false,
      "properties": {
        "osFamily": {
          "$ref": "#/$defs/operatingSystem"
        },
        "technology": {
          "$ref": "#/$defs/technology"
        }
      },
      "required": [
        "osFamily"
      ],
      "type": "object"
    },
    "technology": {
      "additionalProperties": false,
      "properties": {
        "edition": {
          "minLength": 1,
          "type": "string"
        },
        "techId": {
          "type": "integer"
        },
        "version": {
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "techId"
      ],
      "type": "object"
    },
    "networkAddress": {
      "additionalProperties": false,
      "oneOf": [
        {
          "required": [
            "addressType",
            "address",
            "name"
          ],
          "title": "DeprecatedNetworkAddressType"
        },
        {
          "required": [
            "dns",
            "name"
          ],
          "title": "DNSNetworkAddress"
        },
        {
          "required": [
            "url",
            "name"
          ],
          "title": "URLNetworkAddress"
        },
        {
          "required": [
            "ipAddress",
            "name"
          ],
          "title": "IPAddressNetworkAddress"
        }
      ],
      "properties": {
        "address": {
          "deprecated": true,
          "type": "string"
        },
        "addressType": {
          "$ref": "#/$defs/networkAddressType",
          "deprecated": true
        },
        "cloudPlatform": {
          "$ref": "#/$defs/cloudPlatform"
        },
        "dns": {
          "type": "string"
        },
        "ipAddress": {
          "anyOf": [
            {
              "format": "ipv4",
              "type": "string"
            },
            {
              "format": "ipv6",
              "type": "string"
            }
          ],
          "type": "string"
        },
        "isPublic": {
          "type": "boolean"
        },
        "name": {
          "type": "string"
        },
        "url": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "networkAddressType": {
      "enum": [
        "IPV4",
        "IPV6",
        "DNS",
        "URL"
      ],
      "type": "string"
    },
    "cloudPlatform": {
      "enum": [
        "ACK",
        "AKS",
        "AWS",
        "Alibaba",
        "Azure",
        "AzureDevOps",
        "BitbucketCloud",
        "BitbucketDataCenter",
        "Cloudflare",
        "Crusoe",
        "Databricks",
        "DigitalOcean",
        "EKS",
        "Firemon",
        "GCP",
        "GKE",
        "GenericDB",
        "GitHub",
        "GitLab",
        "IBM",
        "Kubernetes",
        "LKE",
        "Linode",
        "MongoDBAtlas",
        "Nebius",
        "OCI",
        "OKE",
        "OVHCloud",
        "Okta",
        "OpenAI",
        "OpenShift",
        "OpenStack",
        "Snowflake",
        "Terraform",
        "Vercel",
        "Wiz",
        "vSphere"
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

The schema fields define the structure and required information for Imported Assets in Wiz. The following tables outline all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

### Root Level fields

| **Field**         | **Type** | **Required** | **Description**                                                                                                                                                                                          |
| ----------------- | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId** | `String` | Required     | The unique ID for each Wiz integration.<ul><li>For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.</li><li>For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`.</li></ul> |
| **dataSources**   | `Array`  | Required     | Contains an array of data source objects.                                                                                                                                                                |

### Data Source fields

`dataSources[]`

| **Field**                        | **Type**  | **Required** | **Description**                                                                    |
| -------------------------------- | --------- | ------------ | ---------------------------------------------------------------------------------- |
| **id**                           | `String`  | Required     | The ID that uniquely identifies asset findings within a tenant and integration ID. |
| **assets**                       | `Array`   | Required     | List of assets included in the data source.                                        |
| **analysisDate**                 | `String`  | Optional     | The timestamp indicating when the analysis was performed, in ISO 8601 format.      |
| **isEnrichmentOnly**             | `Boolean` | Optional     | Set this flag to tell Wiz to ingest a resource but no finding. Uploads with this flag are not counted in pricing, but will fail if a user tries to upload it as a finding.                    |
| **vulnerabilityFindingPolicies** | `Array`   | Optional     | An array of [vulnerability finding policy](#vulnerability-finding-policy-fields) objects. |

### Vulnerability Finding Policy fields

`dataSources[].vulnerabilityFindingPolicies[]`

| **Field**       | **Type** | **Required** | **Description**                                                                                  |
| --------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------ |
| **policyId**    | `String` | Required     | The unique identifier for the vulnerability finding policy.                                      |
| **name**        | `String` | Required     | The name of the policy.                                                                          |
| **severity**    | `String` | Required     | The severity level. Possible values: "None", "Low", "Medium", "High", "Critical".                |
| **description** | `String` | Optional     | A description of the policy.                                                                     |
| **remediation** | `String` | Optional     | Remediation guidance for the policy.                                                             |

### Asset fields

`dataSources[].assets[]`

| **Field**       | **Type** | **Required** | **Description**                                                   |
| --------------- | -------- | ------------ | ----------------------------------------------------------------- |
| **details**     | `Object` | Required     | Contains identifying information for the asset. Must include either [virtualMachine](#virtual-machine-fields) or [networkAddress](#network-address-fields). |
| **analysisDate** | `String` | Optional     | The timestamp when the asset was analyzed, in ISO 8601 format.    |

### Virtual Machine fields

`dataSources[].assets[].details.virtualMachine`

| **Field**                   | **Type**  | **Required** | **Description**                                                                                      |
| --------------------------- | --------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **assetId**                 | `String`  | Required     | A unique identifier for the virtual machine asset.                                                   |
| **name**                    | `String`  | Required     | The name of the virtual machine.                                                                     |
| **firstSeen**               | `String`  | Required     | The timestamp when the asset was first discovered, in ISO 8601 format.                               |
| **biosUUID**                | `String`  | Optional     | The BIOS UUID of the virtual machine.                                                                |
| **cloudPlatformIdentifier** | `Object`  | Optional     | An [object](#cloud-platform-identifier-fields) containing cloud-specific identifiers for the VM.     |
| **fqdns**                   | `Array`   | Optional     | A list of fully qualified domain names associated with the VM.                                       |
| **hostname**                | `String`  | Optional     | The hostname of the VM's operating system.                                                           |
| **ipAddresses**             | `Array`   | Optional     | An array of IPv4 or IPv6 addresses associated with the virtual machine.                              |
| **networkInterfaces**       | `Array`   | Optional     | An array of [network interface](#network-interface-fields) objects associated with the VM.           |
| **originalObject**          | `Object`  | Optional     | The original raw data object for the asset from the source API.                                      |
| **osInfo**                  | `Object`  | Optional     | An [object](#os-info-fields) containing operating system information.                                |
| **serialNumber**            | `String`  | Optional     | The serial number reported by the VM's BIOS or firmware.                                             |
| **tags**                    | `Object`  | Optional     | Key-value pairs of tags associated with the asset.                                                   |

### Cloud Platform Identifier fields

`dataSources[].assets[].details.virtualMachine.cloudPlatformIdentifier`

| **Field**        | **Type** | **Required** | **Description**                                                                                                       |
| ---------------- | -------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| **cloudPlatform** | `String` | Required     | The cloud provider. See the schema for the list of possible values (e.g., "AWS", "Azure", "GCP").                     |
| **resourceId**   | `String` | Optional     | The unique resource ID from the cloud provider (e.g., ARN for AWS, ARM ID for Azure).                                 |
| **vmInstanceId** | `String` | Optional     | The specific instance ID assigned by the cloud provider (e.g., EC2 instance ID for AWS).                              |

### OS Info fields

`dataSources[].assets[].details.virtualMachine.osInfo`

| **Field**      | **Type** | **Required** | **Description**                                                                             |
| -------------- | -------- | ------------ | ------------------------------------------------------------------------------------------- |
| **osFamily**   | `String` | Required     | The operating system family. Possible values: "Linux", "Windows", "Unknown", "MacOS".       |
| **technology** | `Object` | Optional     | An [object](#technology-fields) containing technology details about the operating system.   |

### Technology fields

`dataSources[].assets[].details.virtualMachine.osInfo.technology`

| **Field**   | **Type**  | **Required** | **Description**                                |
| ----------- | --------- | ------------ | ---------------------------------------------- |
| **techId**  | `Integer` | Required     | The technology identifier.                     |
| **edition** | `String`  | Optional     | The edition of the technology.                 |
| **version** | `String`  | Optional     | The version of the technology.                 |

### Network Interface fields

`dataSources[].assets[].details.virtualMachine.networkInterfaces[]`

At least one of `name`, `macAddress`, or `networkAddresses` must be provided.

| **Field**           | **Type** | **Required** | **Description**                                                                                      |
| ------------------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **name**            | `String` | Optional     | The name of the network interface.                                                                   |
| **macAddress**      | `String` | Optional     | The MAC address of the network interface.                                                            |
| **networkAddresses** | `Array`  | Optional     | An array of network address objects for this interface.     |

### Network Address fields

`dataSources[].assets[].details.networkAddress`

One of `dns`, `url`, or `ipAddress` must be provided along with `assetId` and `name`.

| **Field**           | **Type**  | **Required** | **Description**                                                                                      |
| ------------------- | --------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| **assetId**         | `String`  | Required     | A unique identifier for the network address asset.                                                   |
| **name**            | `String`  | Required     | A user-defined name for the network address.                                                         |
| **dns**             | `String`  | Optional     | The DNS name. Required if using DNS address type.                                                    |
| **url**             | `String`  | Optional     | The URL. Required if using URL address type.                                                         |
| **ipAddress**       | `String`  | Optional     | The IP address (IPv4 or IPv6). Required if using IP address type.                                    |
| **cloudPlatform**   | `String`  | Optional     | The cloud provider associated with this network address.                                             |
| **firstSeen**       | `String`  | Optional     | The timestamp when the asset was first discovered, in ISO 8601 format.                               |
| **isPublic**        | `Boolean` | Optional     | Indicates whether the network address is publicly accessible.                                        |
| **originalObject**  | `Object`  | Optional     | The original raw data object for the asset from the source API.                                      |
| **tags**            | `Object`  | Optional     | Key-value pairs of tags associated with the asset.                                                   |
| **vmCloudInstanceId** | `String`  | Optional     | The cloud instance ID of the associated virtual machine.                                             |

## Example

This example JSON payload demonstrates how to format Imported Assets properly for submission to Wiz. It illustrates key fields and their proper usage.

```json Example
{
  "integrationId": "wizt-12345",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-833333333",
      "analysisDate": "2023-09-07T15:50:00Z",
      "assets": [
        {
          "details": {
            "virtualMachine": {
              "assetId": "Some-vm-123",
              "name": "java-web-server",
              "firstSeen": "2023-01-15T10:30:00Z",
              "biosUUID": "ec25b8b2-bc76-5468-4088-b113fe58ee67",
              "hostname": "java-web-server.example.com",
              "ipAddresses": [
                "10.1.2.3"
              ],
              "osInfo": {
                "osFamily": "Windows"
              },
              "tags": {
                "owner": "Owner-name",
                "Project": "Cloud Migration"
              },
              "originalObject": {
                "source-data": "example"
              }
            }
          }
        }
      ]
    }
  ]
}
```

## Example Imported Asset in Wiz

The following is an example of an Imported Asset as it appears in Wiz.

![](https://docs-assets.wiz.io/images/example-external-source-asset--831328b9.webp)
