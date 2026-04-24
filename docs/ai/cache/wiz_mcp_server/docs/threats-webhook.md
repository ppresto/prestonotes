# Threats Webhook Reference
*Reference documentation for the Threats webhook payload structure, including field definitions and example payloads.*

Category: webhook

This document defines the webhook payload structure that will be sent when exporting a Threat. It cannot be customized.

<Emptyfieldhandling />

## Default request body

The following shows an example webhook payload with sample values:

```json Default request body
{
  "trigger": {
    "source": "THREATS",
    "type": "Manually Triggered",
    "ruleId": "",
    "ruleName": "Manual",
    "updatedFields": "",
    "changedBy": ""
  },
  "threat": {
    "id": "d5efcc30-da2e-55c8-9998-f3e34fa9b9c5",
    "title": "Azure Mass Storage Account Access Keys Retrieval",
    "description": "Multiple Azure storage account access keys unusually retrieved by airflow-builder within a short timeframe",
    "status": "IN_PROGRESS",
    "severity": "CRITICAL",
    "created": "2025-06-22T00:23:27.61428Z",
    "resolutionNote": "",
    "projects": "Wiz Factory Prod, Acme Azure App, test_cmg, Wiz Inc, Acme, Payment Apps, Wiz Prod, ACME corp, App A, Azure: Wiz-Demo-Scenarios, EBC_Labs, ",
    "threatURL": "https://demo.wiz.io/threats#~(issue~'d5efcc30-da2e-55c8-9998-f3e34fa9b9c5)",
    "resolvedAt": "",
    "updatedAt": "2025-06-22T02:07:24.128701Z",
    "cloudPlatform": "Azure",
    "cloudAccounts": [
      {
        "id": "16ab320e-c38f-5d89-ad9e-9a0c8c699282",
        "name": "Wiz - Demo-Scenarios"
      }
    ],
    "cloudOrganizations": [],
    "actors": [
      {
        "externalId": "4f2537f5-ff4b-43c0-97e6-c6a3bb81431b",
        "id": "ebc059d2-7d53-5c88-9d8d-a3c3ead33a7e",
        "name": "4f2537f5-ff4b-43c0-97e6-c6a3bb81431b",
        "nativeType": "Microsoft Entra ID Application Service Principal",
        "type": "Service Account"
      }
    ],
    "resources": [
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra/providers/microsoft.compute/disks/pii-data",
        "id": "78a48474-253a-50fa-aad6-57f4f483dc7f",
        "name": "PII-DATA",
        "nativeType": "Disk",
        "type": "Volume"
      },
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra-northeurope/providers/microsoft.network/networksecuritygroups/apptest54nsg",
        "id": "6575237b-e380-5869-8a4c-0f0229d038d8",
        "nativeType": "Network Security Group (NSG)",
        "type": "Firewall"
      },
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra-northeurope/providers/microsoft.compute/virtualmachines/apptest54",
        "id": "26362d2c-1ec1-540a-bdc0-422310fcc0c4",
        "name": "APPTEST54",
        "nativeType": "Compute Virtual Machine",
        "type": "Virtual Machine"
      },
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra-northeurope/providers/microsoft.network/networkinterfaces/apptest54vmnic",
        "id": "0cb2f97f-a9fa-568d-b341-996295f7fbae",
        "name": "APPTEST54VMNIC",
        "nativeType": "Network Interface",
        "type": "Network Interface"
      },
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra-northeurope/providers/microsoft.network/publicipaddresses/apptest54publicip",
        "id": "8e480595-811a-565b-b90c-c36cce20c289",
        "nativeType": "Public IP Address",
        "type": "Network Address"
      },
      {
        "externalId": "/subscriptions/fee3535b-9616-486f-a476-6a500a08a02b/resourcegroups/cloud_infra/providers/microsoft.storage/storageaccounts/clientdatakeys2",
        "id": "141d1d2b-a844-598c-b97a-e1fb3ddd99c0",
        "nativeType": "Storage Account",
        "type": "Storage Account"
      }
    ],
    "tdrNames": "Unusual Disk SAS Token Generated, Network security group set to allow ingress for any IP and administrative ports, Resource Created in an Unused Region, Azure Mass Storage Account Access Keys Retrieval, Service Principal Used After Long Period of Inactivity, ",
    "detectionIds": "d2b29793-3623-5298-9278-161602a6806d, 2289aaee-2f74-5bbd-a546-c93b6f70e694, 457a6177-816e-5987-9267-343db4b7d019, e0194ba7-aae1-5de6-9ce1-cfbce4771fd7, 1c1b0fa5-4d28-561c-8f5b-86b4ed04d645, ",
    "mitreTechniques": null,
    "mitreTactics": null,
    "notes": ""
  }
}
```

## Template request body

The body of the HTTP request that will be POSTed to the webhook URL. You cannot customize the payload.

```json Template request body
{
  "trigger": {
    "source": "{{triggerSource}}",
    "type": "{{triggerType}}",
    "ruleId": "{{ruleId}}",
    "ruleName": "{{ruleName}}",
    "updatedFields": "{{#changedFields}}{{name}} field was changed from {{previousValuePrettified}} to {{newValuePrettified}} {{/* changedFields */}}",
    "changedBy": "{{changedBy}}"
  },
  "threat": {
    "id": "{{issue.id}}",
    "title": "{{issue.enrichedMainDetection.rule.name}}",
    "description": "{{issue.enrichedMainDetection.description}}",
    "status": "{{issue.status}}",
    "severity": "{{issue.severity}}",
    "created": "{{issue.createdAt}}",
    "resolutionNote": "{{issue.resolutionNote}}",
    "projects": "{{#issue.projects}}{{name}}, {{/* issue.projects */}}",
    "threatURL": "https://{{wizDomain}}/threats#~(issue~'{{issue.id}})",
    "resolvedAt": "{{issue.resolvedAt}}",
    "updatedAt": "{{issue.updatedAt}}",
    "cloudPlatform" : "{{issue.entitySnapshot.cloudPlatform}}",
    "cloudAccounts": {{issue.enrichedCloudAccounts}},
    "cloudOrganizations": {{issue.enrichedCloudOrganizations}},
    "actors": {{issue.enrichedThreatActors}},
    "resources": {{issue.enrichedThreatResources}},
    "tdrNames": "{{#issue.enrichedDetections}}{{rule.name}}, {{/* issue.enrichedDetections */}}",
    "detectionIds": "{{#issue.enrichedDetections}}{{id}}, {{/* issue.enrichedDetections */}}",
    "mitreTechniques": {{issue.enrichedThreatMitreTechniques}}{{^issue.enrichedThreatMitreTechniques}}null{{/* issue.enrichedThreatMitreTechniques */}},
    "mitreTactics": {{issue.enrichedThreatMitreTactics}}{{^issue.enrichedThreatMitreTactics}}null{{/* issue.enrichedThreatMitreTactics */}},
    "notes": "{{#issue.notes}}{{user.email}}-{{text}}, {{/* issue.notes */}}"
  }
}
```

:::warning

Template variables not wrapped by quotation marks have a JSON structure. Do not wrap them in quotation marks.

:::

## Webhook payload object reference

The webhook payload contains several object types that represent different aspects of a Threat. Here are the core objects and their purposes:

| Object                                             | Description                                                                                                                       |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [Trigger](#trigger-object)                         | Contains information about the event that triggered the webhook, such as whether it was manual or from an automation rule.        |
| [Threat](#threat-object)                           | The main object containing all the details of the exported Threat, including its status, severity, associated entities, and more. |
| [Cloud Accounts](#cloud-accounts-object)           | Represents a cloud service provider account associated with the Threat.                                                           |
| [Cloud Organizations](#cloud-organizations-object) | Represents the broader cloud organization structure associated with the Threat.                                                   |
| [Actors](#actors-object)                           | Represents the entity (e.g., service principal, user) that is a part of the Threat graph.                                         |
| [Resources](#resources-object)                     | Represents the affected cloud resources (e.g., virtual machine, storage account) involved in the Threat.                          |

## Webhook payload properties

When a Threat is exported, the webhook payload will contain these objects and properties.

### Root Object

The top-level object in the webhook payload.

| Property | Type                              | Description                                         |
| -------- | --------------------------------- | --------------------------------------------------- |
| trigger  | [Trigger object](#trigger-object) | Details about the event that triggered the webhook. |
| threat   | [Threat object](#threat-object)   | The detailed Threat data.                           |

### Trigger object

Contains information about the event that triggered the webhook.

| Property      | Type   | Description                                                                 |
| ------------- | ------ | --------------------------------------------------------------------------- |
| source        | string | The source of the trigger. For this webhook, the value is always `THREATS`. |
| type          | string | The type of trigger, e.g., `Manually Triggered` or `Rule Triggered`.        |
| ruleId        | string | If triggered by a rule, the unique identifier of that rule.                 |
| ruleName      | string | The name of the trigger, e.g., `Manual` or the name of the automation rule. |
| updatedFields | string | A description of fields that were changed, triggering the webhook.          |
| changedBy     | string | The user or system that initiated the change.                               |

### Threat object

The main object containing all the details of the exported Threat.

| Property           | Type                                                                | Description                                                              |
| :----------------- | :------------------------------------------------------------------ | :----------------------------------------------------------------------- |
| id                 | string                                                              | Unique identifier for the Threat.                                        |
| title              | string                                                              | The title of the Threat.                                                 |
| description        | string                                                              | A detailed description of the Threat.                                    |
| status             | string                                                              | The current status of the Threat (e.g., `IN_PROGRESS`, `RESOLVED`).      |
| severity           | string                                                              | The severity level of the Threat (e.g., `CRITICAL`, `HIGH`).             |
| created            | string                                                              | ISO 8601 timestamp for when the Threat was created.                      |
| resolutionNote     | string                                                              | The note added when the Threat was resolved.                             |
| projects           | string                                                              | A comma-separated list of projects associated with the Threat.           |
| threatURL          | string                                                              | A direct URL to the Threat in the UI.                                    |
| resolvedAt         | string                                                              | ISO 8601 timestamp for when the Threat was resolved.                     |
| updatedAt          | string                                                              | ISO 8601 timestamp for the last time the Threat was updated.             |
| cloudPlatform      | string                                                              | The cloud platform where the Threat was detected (e.g., `Azure`, `AWS`). |
| cloudAccounts      | array of [Cloud Accounts objects](#cloud-accounts-object)           | List of associated cloud accounts.                                       |
| cloudOrganizations | array of [Cloud Organizations objects](#cloud-organizations-object) | List of associated cloud organizations.                                  |
| actors             | array of [Actors objects](#actors-object)                           | List of actors involved in the Threat.                                   |
| resources          | array of [Resources objects](#resources-object)                     | List of resources involved in the Threat.                                |
| tdrNames           | string                                                              | A comma-separated list of the names of the underlying detection rules.   |
| detectionIds       | string                                                              | A comma-separated list of the IDs of the underlying detections.          |
| mitreTechniques    | array of string                                                     | A list of MITRE ATT&CK technique IDs.                                    |
| mitreTactics       | array of string                                                     | A list of MITRE ATT&CK technique IDs.                                    |
| notes              | string                                                              | A comma-separated list of notes added to the Threat.                     |

### Cloud Accounts object

Represents a cloud service provider account associated with the Threat.

| Property | Type   | Description                                  |
| -------- | ------ | -------------------------------------------- |
| id       | string | The unique identifier for the cloud account. |
| name     | string | The name of the cloud account.               |

### Cloud Organizations object

Represents the broader cloud organization structure associated with the Threat.

| Property | Type   | Description                                       |
| -------- | ------ | ------------------------------------------------- |
| id       | string | The unique identifier for the cloud organization. |
| name     | string | The name of the cloud organization.               |

### Actors object

Represents the entity (e.g., service principal, user) that is a part of the Threat graph.

| Property   | Type   | Description                                                           |
| ---------- | ------ | --------------------------------------------------------------------- |
| externalId | string | The ID of the actor as defined in the cloud provider.                 |
| id         | string | The internal unique identifier for the actor.                         |
| name       | string | The name of the actor.                                                |
| nativeType | string | The specific type of the actor from the cloud provider's perspective. |
| type       | string | The general type of the actor (e.g., `Service Account`).              |

### Resources object

Represents the affected cloud resources (e.g., virtual machine, storage account) involved in the Threat.

| Property   | Type   | Description                                                              |
| ---------- | ------ | ------------------------------------------------------------------------ |
| externalId | string | The full resource identifier from the cloud provider.                    |
| id         | string | The internal unique identifier for the resource.                         |
| name       | string | The name of the resource.                                                |
| nativeType | string | The specific type of the resource from the cloud provider's perspective. |
| type       | string | The general type of the resource (e.g., `Virtual Machine`).              |

---

## Additional notes

- Timestamps are in ISO 8601 format: `YYYY-MM-DDTHH:mm:ss.SSSSSSZ`
- Fields that are arrays of objects, such as `actors` and `resources`, will contain the full object details within the array.
