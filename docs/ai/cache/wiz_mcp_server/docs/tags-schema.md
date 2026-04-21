# Custom Tag Enrichment Schema
*JSON schema reference for enriching Wiz cloud assets with custom tags from third-party systems like CMDB.*

Category: enrichment

Use custom tag enrichment to tag assets from third-party systems, such as CMDB.

## Supported cloud assets and identifier

The table below shows which cloud assets can be enriched with custom tags and the required identifier.

| Supported resources (entity name)                                                           | Required Identifier                |
| :------------------------------------------------------------------------------------------ | :--------------------------------- |
| All objects, except container images, application endpoints, and other non-cloud resources. | Workload provider ID, such as ARN. |

## Custom tag lifecycle

| Aspect                       | Details                                                                                                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Default Expiry               | 7 days                                                                                                                                                   |
| Recommended Upload Frequency | Every 24 hours (aligns with Wiz's typical 24-hour environment scan cycle)                                                                                |
| Tag Tracking                 | Once uploaded, tags are tracked in Wiz alongside cloud assets                                                                                            |
| Tag Refreshing               | Must be refreshed every 7 days to remain in Wiz, even if the resource still exists in the cloud environment                                              |
| Tag Format                   | Wiz automatically adds **"custom/"** prefix with `/` as a delimiter<br/>Example: A tag `Key: "Foo"` and `Value: "Boo"` will appear as `"custom/Foo:Boo"` |
| Prefix Modification          | Contact WIN support to modify the prefix                                                                                                                 |
| Appearance Time              | Up to 24 hours for custom tags to appear on resources after enrichment data has been uploaded or sent via API                                            |

## Limitations

[External enrichments are subject to limitations](dev:limitations#external-enrichment-limitations).

## Schema fields

The schema fields define the structure and required information for submitting custom tags to Wiz. This table outlines all available fields, their requirements, and descriptions to ensure your integration provides the necessary data for proper correlation with cloud resources (assets).

| **Field**                               | **Required/Optional** | **Description**                                                                                                                                                                                                                                               |
| --------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **integrationId**<br/>`String`          | Required              | The unique ID for each Wiz integration.<br/>• For WIN partners: You will get a dedicated integration ID towards completion of the development. Until then, please use the ID for Wiz customers.<br/>• For Wiz customers: Use `55c176cc-d155-43a2-98ed-aa56873a1ca1`. |
| **dataSources**<br/>`Array`             | Required              | Contains an array of data sources. Each data source is an object.                                                                                                                                                                                             |
| **id**<br/> `String`                    | Required              | The ID that uniquely identifies asset findings within a tenant and integration ID. Can be subscription ID.                                                                                                                                                    |
| **analysisDate**<br/> `ISO 8601 string` | Optional              | The date the scan was performed.                                                                                                                                                                                                                              |
| **assets**<br/> `Array`                 | Required              | List of assets included in the data source. Each asset is an object. [See supported assets](#supported-cloud-assets-and-identifier).                                                                                                                          |
| **assetIdentifier**<br/> `Object`       | Required              | Contains identifiers for a specific asset.                                                                                                                                                                                                                    |
| **cloudPlatform**<br/> `String`         | Optional              | The cloud platform that was scanned. Possible values: "AWS", "Azure", "GCP", "OCI", "Alibaba Cloud", "Linode". Omit this field for on-prem/bare metal assets.                                                                                                                                               |
| **providerId**<br/> `String`            | Required              | A unique identifier assigned to a specific cloud asset by the cloud service provider when the asset is created, allowing for the identification and differentiation of the asset within the cloud computing ecosystem. Includes ARN—AWS, Resource group—Azure |
| **customTags**<br/> `Array`             | Optional              | Contains an array of custom tags. Each tag is an object.                                                                                                                                                                                                      |
| **key**<br/> `String`                   | Required              | The key of the tag.                                                                                                                                                                                                                                           |
| **value**<br/> `String`                 | Required              | The value of the tag.                                                                                                                                                                                                                                         |
| **networkAddress**<br/> `String`        | Optional              | The IP address of the asset.                                                                                                                                                                                                                                  |
| **endpointURL**<br/> `String`           | Optional              | The Endpoint URL of the asset.                                                                                                                                                                                                                                |

## Schema

The custom tag schema defines the JSON structure expected by Wiz's API when submitting custom tags. Understanding this schema is essential for creating valid payloads that will be properly processed and incorporated into the Security Graph.

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
        "customTags": {
          "items": {
            "$ref": "#/$defs/keyValue"
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
    "keyValue": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "type": "string"
        },
        "value": {
          "type": "string"
        }
      },
      "required": ["key", "value"],
      "type": "object"
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

## Example

This example JSON payload demonstrates how to properly format custom tag enrichment data for submission to Wiz. It shows how to include multiple custom tags for a cloud asset, illustrating the correct structure for the integration ID, data sources, asset identifier, and tag key-value pairs.

```json Example
{
  "integrationId": "000c0c7b-5f59-46ea-a305-934a15b94930",
  "dataSources": [
    {
      "id": "29A4E640-4BFD-4779-856756756",
      "analysisDate": "2023-08-02T16:50:00Z",
      "assets": [
        {
          "assetIdentifier": {
            "cloudPlatform": "AWS",
            "providerId": "arn:aws:ec2:eu-central-1:9123455:instance/i-04ea5a462c85555"
          },
          "customTags": [
            {
              "key": "App",
              "value": "Spotify"
            },
            {
              "key": "Owner",
              "value": "Beyoncé"
            }
          ]
        }
      ]
    }
  ]
}
```
