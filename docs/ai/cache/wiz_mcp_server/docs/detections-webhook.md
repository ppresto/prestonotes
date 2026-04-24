# Detections Webhook Reference
*Reference documentation for the Detections webhook payload structure, including field definitions and example payloads.*

Category: webhook

This document defines the webhook payload structure that will be sent when exporting a Detection. It cannot be customized.

<Emptyfieldhandling />

## Default request body

The following shows an example webhook payload with sample values:

```json Default request body
{
  "trigger": {
    "source": "DETECTIONS",
    "type": "Created",
    "ruleId": "a08fe977-3f54-48bf-adcf-f76994739c1f",
    "ruleName": "Detections Webhook Test Rule"
  },
  "id": "6a440e9b-c8d8-5482-a0e9-da714359aecf",
  "threatId": "733edfe5-db25-5b14-ac58-dc69d6005c81",
  "threatURL": "https://test.wiz.io/issues#~(issue~'733edfe5-db25-5b14-ac58-dc69d6005c81)",
  "title": "Timestomping technique was detected",
  "description": "Process executed the touch binary with the relevant command line flag used to modify files date information such as creation time, and last modification time. This could indicate the presence of a threat actor achieving defense evasion using the Timestomping technique.",
  "severity": "MEDIUM",
  "createdAt": "2025-01-21T18:52:16.819883668Z",
  "tdrId": "46fd0cdc-252e-5e69-be6e-66e4851d7ae4",
  "tdrSource": "WIZ_SENSOR",
  "mitreTactics": ["TA0005"],
  "mitreTechniques": ["T1070.006"],
  "cloudAccounts": [
    {
      "cloudPlatform": "AWS",
      "externalId": "134653897021",
      "id": "5d67ed02-738e-5217-b065-d93642dd2629"
    }
  ],
  "cloudOrganizations": [],
  "timeframe": {
    "start": "2025-01-21T18:52:15.838Z",
    "end": "2025-01-21T18:52:15.838Z"
  },
  "actors": [
    {
      "externalId": "test-actor",
      "id": "4e1bd57f-49b2-47a8-a4a7-0e66fe0b770e",
      "name": "test-actor",
      "nativeType": "Microsoft Entra ID Application Service Principal",
      "type": "SERVICE_ACCOUNT"
    }
  ],
  "resources": [
    {
      "cloudAccount": {
        "cloudPlatform": "AWS",
        "externalId": "134653897021",
        "id": "5d67ed02-738e-5217-b065-d93642dd2629"
      },
      "externalId": "test-container",
      "id": "da259b23-de77-5adb-8336-8c4071696305",
      "name": "test-container",
      "nativeType": "ecs#containerinstance",
      "region": "us-east-1",
      "type": "CONTAINER"
    }
  ],
  "primaryResource": {
    "cloudAccount": {
      "cloudPlatform": "AWS",
      "externalId": "134653897021",
      "id": "5d67ed02-738e-5217-b065-d93642dd2629"
    },
    "externalId": "test-container",
    "id": "da259b23-de77-5adb-8336-8c4071696305",
    "name": "test-container",
    "nativeType": "ecs#containerinstance",
    "region": "us-east-1",
    "type": "CONTAINER"
  },
  "triggeringEventsCount": 1,
  "triggeringEvents": [
    {
      "actor": {
        "id": "4e1bd57f-49b2-47a8-a4a7-0e66fe0b770e"
      },
      "actorIP": "168.1.1.1",
      "actorIPMeta": {
        "autonomousSystemNumber": 8075,
        "autonomousSystemOrganization": "MICROSOFT-CORP-MSN-AS-BLOCK",
        "country": "United States",
        "isForeign": true,
        "reputation": "Benign",
        "reputationSource": "Recorded Future"
      },
      "category": "Detection",
      "cloudPlatform": "AWS",
      "cloudProviderUrl": "https://console.aws.amazon.com/cloudtrail/home?region=us-east-1#/events/Ptrace##test-container-SensorRuleEngine##sen-id-142-bd820642-34f2-4d3c-90b6-c384df0fd528",
      "description": "The program /usr/bin/bash executed the program /usr/bin/touch on container test-container",
      "eventTime": "2025-01-21T18:52:15.838Z",
      "externalId": "Ptrace##test-container-SensorRuleEngine##sen-id-142-bd820642-34f2-4d3c-90b6-c384df0fd528",
      "id": "2b46aa0d-9f46-5cb9-a6ae-e83ca514144a",
      "name": "Timestomping technique was detected",
      "origin": "WIZ_SENSOR",
      "resources": [
        {
          "externalId": "test-container",
          "id": "da259b23-de77-5adb-8336-8c4071696305",
          "name": "test-container",
          "nativeType": "ecs#containerinstance",
          "region": "us-east-1",
          "type": "CONTAINER"
        }
      ],
      "runtimeDetails": {
        "processTree": [
          {
            "command": "touch -r /usr/bin /tmp/uga",
            "container": {
              "externalId": "test-container",
              "id": "da259b23-de77-5adb-8336-8c4071696305",
              "imageExternalId": "sha256:dcad76015854d8bcab3041a631d9d25d777325bb78abfa8ab0882e1b85ad84bb",
              "imageId": "d18500ef-c0f7-5028-8c4c-1cd56c3a6652",
              "name": "test-container"
            },
            "executionTime": "2025-01-21T18:52:15.838Z",
            "hash": "a0d0c6248d07a8fa8e3b6a94e218ff9c8c372ad6",
            "id": "1560",
            "path": "/usr/bin/touch",
            "size": 109616,
            "userId": "0",
            "username": "root"
          },
          {
            "command": "/bin/bash -x -c touch -r /usr/bin /tmp/uga",
            "container": {
              "externalId": "test-container",
              "id": "da259b23-de77-5adb-8336-8c4071696305",
              "imageExternalId": "sha256:dcad76015854d8bcab3041a631d9d25d777325bb78abfa8ab0882e1b85ad84bb",
              "imageId": "d18500ef-c0f7-5028-8c4c-1cd56c3a6652",
              "name": "test-container"
            },
            "executionTime": "2025-01-21T18:52:15.838Z",
            "hash": "91fbd9d8c65de48dc82a1064b8a4fc89f5651778",
            "id": "1560",
            "path": "/usr/bin/bash",
            "size": 1265648,
            "userId": "0",
            "username": "root"
          }
        ]
      },
      "source": "WizSensorAlert##RuleEngine",
      "status": "Success"
    }
  ]
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
    "ruleName": "{{ruleName}}"
  },
  "id": "{{detection.id}}",
  "threatId": "{{detection.issue.id}}",
  "threatURL": {{#detection.issue.url}}"{{detection.issue.url}}"{{/* detection.issue.url */}}{{^detection.issue.url}}null{{/* detection.issue.url */}},
  "title": "{{detection.rule.name}}",
  "description": {{#detection.description}}"{{detection.description}}"{{/* detection.description */}}{{^detection.description}}null{{/* detection.description */}},
  "severity": "{{detection.severity}}",
  "createdAt": "{{detection.createdAt}}",
  "tdrId": "{{detection.rule.id}}",
  "tdrSource": "{{detection.rule.sourceType}}",
  "mitreTactics": {{detection.rule.MITRETactics}}{{^detection.rule}}null{{/* detection.rule */}},
  "mitreTechniques": {{detection.rule.MITRETechniques}}{{^detection.rule}}null{{/* detection.rule */}},
  "cloudAccounts": {{detection.cloudAccounts}},
  "cloudOrganizations": {{detection.cloudOrganizations}},
  "timeframe": {
    "start": "{{detection.startedAt}}",
    "end": "{{detection.endedAt}}"
  },
  "actors": {{detection.actors}},
  "primaryActor": {{#detection.primaryActor}}{{detection.primaryActor}}{{/* detection.primaryActor */}}{{^detection.primaryActor}}null{{/* detection.primaryActor */}},
  "resources": {{detection.resources}},
  "primaryResource": {{#detection.primaryResource}}{{detection.primaryResource}}{{/* detection.primaryResource */}}{{^detection.primaryResource}}null{{/* detection.primaryResource */}},
  "triggeringEventsCount": {{detection.triggeringEventsCount}},
  "triggeringEvents": {{detection.triggeringEvents}}
}
```

:::warning

Template variables not wrapped by quotation marks have a JSON structure. Do not wrap them in quotation marks.

:::

## Webhook payload object reference

The webhook payload contains several object types that represent different aspects of a detection event. Here are the core objects and their purposes:

| Object                                           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Detection Payload](#webhook-payload-properties) | Represents the root object of a security detection, including its source, severity, associated threat, creation timestamp, and detection timeframe (start/end times).                                                                                                                                                                                                                                                                                                                                                 |
| [Cloud Account](#cloud-account-object)           | Represents a cloud service provider account associated with the detection, containing provider details and account identifiers.                                                                                                                                                                                                                                                                                                                                                                                       |
| [Cloud Organization](#cloud-organization-object) | Represents the broader cloud organization structure, containing provider information and organizational identifiers.                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Actor](#actor-object)                           | Represents the entity responsible for initiating the event, such as the container or process that performed the action. Contains identifying properties like the actor's unique IDs, name, type, and native type classification. This helps distinguish between legitimate and suspicious activities based on which specific identity, workload or process initiated an event. For example, this helps identify when normally benign events (like database connections) come from unexpected containers or processes. |
| [Resource](#resource-object)                     | Represents the affected cloud or Kubernetes resources involved in the detection, including their identifiers, status, and location information.                                                                                                                                                                                                                                                                                                                                                                       |
| [Triggering Event](#triggering-event-object)     | Represents events that triggered the detection, including the event timestamp, actors involved, and affected resources.                                                                                                                                                                                                                                                                                                                                                                                               |
| [Process Tree](#process-tree-object)             | Represents the hierarchy of processes involved in the triggering event, including process execution timestamp, execution details, and container information.                                                                                                                                                                                                                                                                                                                                                          |
| [Actor IP Meta](#actor-ip-meta-object)           | Represents detailed metadata about IP addresses associated with actors, including geographical and reputation information.                                                                                                                                                                                                                                                                                                                                                                                            |

## Webhook payload properties

When a Detection is exported, the webhook payload will contain these objects and properties.

### Detection payload object

Represents the root object of a security detection, including its source, severity, associated threats, creation timestamp, and detection timeframe (start/end times).

| Property              | Type                                                              | Description                                                             |
| --------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
| id                    | string                                                            | Unique identifier for the detection.                                    |
| source                | string                                                            | Source of the detection, will be "DETECTIONS".                          |
| threatId              | string                                                            | ID of the associated threat.                                            |
| threatURL             | string                                                            | URL linking to more details on the threat.                              |
| title                 | string                                                            | Title or summary of the detection.                                      |
| description           | string                                                            | Description providing more details on the detection.                    |
| severity              | string                                                            | Severity level of the detection.                                        |
| createdAt             | string                                                            | ISO8601 timestamp for when detection was created.                       |
| tdrId                 | string                                                            | TDR identifier.                                                         |
| tdrSource             | string                                                            | TDR source.                                                             |
| mitreTactic           | string                                                            | MITRE tactic related to detection.                                      |
| mitreTechnique        | string                                                            | MITRE technique related to detection.                                   |
| cloudAccounts         | array of [Cloud Account Objects](#cloud-account-object)           | List of associated cloud accounts.                                      |
| cloudOrganizations    | array of [Cloud Organization Objects](#cloud-organization-object) | List of associated cloud organizations.                                 |
| detectionUrl          | string                                                            | URL linking to more details on the detection.                           |
| timeframe             | object                                                            | Object containing start and end timestamps for the detection timeframe. |
| trigger               | object                                                            | Details on the trigger including source, type, ruleId, and ruleName.    |
| actors                | array of [Actor Objects](#actor-object)                           | List of actor details.                                                  |
| primaryActorId        | string                                                            | ID of primary actor.                                                    |
| resources             | array of [Resource Objects](#resource-object)                     | List of resource details.                                               |
| primaryResourceId     | string                                                            | ID of primary resource.                                                 |
| triggeringEventsCount | string                                                            | Count of events that triggered detection.                               |
| triggeringEvents      | array of [Triggering Event Objects](#triggering-event-object)     | List of event details.                                                  |

### Cloud Account object

Represents a cloud service provider account associated with the detection, containing provider details and account identifiers.

| Property      | Type   | Description                    |
| ------------- | ------ | ------------------------------ |
| cloudProvider | string | Name of cloud provider.        |
| externalId    | string | External ID for cloud account. |
| name          | string | Name of the cloud account.     |

### Cloud Organization object

Represents the broader cloud organization structure, containing provider information and organizational identifiers.

| Property      | Type   | Description                         |
| ------------- | ------ | ----------------------------------- |
| cloudProvider | string | Name of cloud provider.             |
| externalId    | string | External ID for cloud organization. |
| name          | string | Name of the cloud organization.     |

### Actor object

Represents the entity responsible for initiating the event, such as the container or process that performed the action. Contains identifying properties like the actor's unique IDs, name, type, and native type classification. This helps distinguish between legitimate and suspicious activities based on which specific identity, workload or process initiated an event. For example, this helps identify when normally benign events (like database connections) come from unexpected containers or processes.

| Property         | Type   | Description                                                            |
| ---------------- | ------ | ---------------------------------------------------------------------- |
| id               | string | Actor ID.                                                              |
| externalId       | string | External ID.                                                           |
| providerUniqueId | string | Unique identifier from the provider.                                   |
| name             | string | Name of the actor.                                                     |
| type             | string | Type of the actor.                                                     |
| nativeType       | string | Native type classification                                             |
| actingAs         | object | Object containing id, name, type, and nativeType for assumed identity. |

### Resource object

Represents the affected cloud or Kubernetes resources involved in the detection, including their identifiers, status, and location information.

| Property                | Type   | Description                                |
| ----------------------- | ------ | ------------------------------------------ |
| id                      | string | Resource ID.                               |
| externalId              | string | External ID.                               |
| providerUniqueId        | string | Unique identifier from the provider.       |
| name                    | string | Name of the resource.                      |
| type                    | string | Type of resource.                          |
| nativeType              | string | Native type classification.                |
| region                  | string | Geographic region.                         |
| status                  | string | Current status of the resource.            |
| cloudAccount            | object | Associated cloud account information.      |
| kubernetesNodeId        | string | ID of the Kubernetes node.                 |
| kubernetesNodeName      | string | Name of the Kubernetes node.               |
| kubernetesNamespaceId   | string | ID of the Kubernetes namespace.            |
| kubernetesNamespaceName | string | Name of the Kubernetes namespace.          |
| kubernetesClusterId     | string | ID of the Kubernetes cluster.              |
| kubernetesClusterName   | string | Name of the Kubernetes cluster.            |
| cloudProviderUrl        | string | URL to resource in cloud provider console. |

### Triggering Event object

Represents events that triggered the detection, including the event timestamp, actors involved, and affected resources.

| Property          | Type                                                  | Description                                |
| ----------------- | ----------------------------------------------------- | ------------------------------------------ |
| id                | string                                                | Event ID.                                  |
| name              | string                                                | Name of the event.                         |
| description       | string                                                | Description of the event.                  |
| cloudProviderUrl  | string                                                | URL to event in cloud provider console.    |
| cloudPlatform     | string                                                | Cloud platform where event occurred.       |
| origin            | string                                                | Origin of the event.                       |
| eventTime         | string                                                | ISO8601 timestamp of when event occurred.  |
| source            | string                                                | Source of the event.                       |
| category          | string                                                | Event category.                            |
| status            | string                                                | Status of the event.                       |
| actor             | [Actor Object](#actor-object)                         | Actor associated with event.               |
| actorIp           | string                                                | IP address of the actor.                   |
| actorIpMeta       | [Actor IP Meta Object](#actor-ip-meta-object)         | Metadata object containing IP information. |
| resources         | array of [Resource Objects](#resource-object)         | Resource objects affected by event.        |
| subjectResourceId | string                                                | ID of the primary affected resource.       |
| subjectResourceIp | string                                                | IP of the primary affected resource.       |
| processTree       | array of [Process Tree Objects](#process-tree-object) | Process tree leading to event.             |

### Process Tree object

Represents the hierarchy of processes involved in the triggering event, including process execution timestamp, execution details, and container information.

| Property      | Type    | Description                                               |
| ------------- | ------- | --------------------------------------------------------- |
| cmdline       | string  | Process command line.                                     |
| containerInfo | object  | Container metadata including id, name, and image details. |
| exePath       | string  | Executable path.                                          |
| exeSha1       | string  | Executable SHA1 hash.                                     |
| exeSize       | integer | Executable size in bytes.                                 |
| execTime      | string  | ISO8601 timestamp when process executed.                  |
| pid           | integer | Process ID.                                               |
| uid           | integer | User ID that executed process.                            |
| username      | string  | Username that executed process.                           |

### Actor IP Meta object

Represents detailed metadata about IP addresses associated with actors, including geographical and reputation information.

| Property                     | Type    | Description                                    |
| ---------------------------- | ------- | ---------------------------------------------- |
| country                      | string  | Country of origin for IP.                      |
| autonomousSystemNumber       | integer | ASN number.                                    |
| autonomousSystemOrganization | string  | Organization associated with ASN (ASO).        |
| reputation                   | string  | IP reputation rating.                          |
| reputationDescription        | string  | Description of IP reputation.                  |
| reputationSource             | string  | Source of reputation data.                     |
| relatedAttackGroupNames      | string  | Attack groups associated with IP.              |
| isForeign                    | boolean | Whether IP is from foreign source.             |
| customIPRanges               | object  | Object containing custom IP range definitions. |

## Additional notes

- Timestamps are ISO8601 format: YYYY-MM-DDThh:mm:ssZ
- Objects with ID references only contain the ID value, full details are found in the main object list (e.g. actor IDs within events point to the main actors array).
