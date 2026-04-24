# Issues Webhook Reference
*Reference documentation for the Issues webhook payload structure, including template variables and customization options.*

Category: webhook

When setting up an Issues webhook integration, you'll receive webhook notifications in JSON format. You can customize both the structure of the JSON payload and its content using [supported template variables](#template-variables).

<Emptyfieldhandling />

## Default request body

The following shows an example webhook payload with sample values:

```json Default request body
{
  "trigger": {
    "source": "ISSUE",
    "type": "Created",
    "ruleId": "",
    "ruleName": "Manual",
    "updatedFields": "",
    "changedBy": ""
  },
  "issue": {
    "id": "92c4a90f-11d7-4bc3-a20b-21253a5e1c87",
    "status": "OPEN",
    "severity": "LOW",
    "created": "2023-03-15T12:08:09.708375Z",
    "projects": "Acme Prod App, ACME_Labs, "
  },
  "resource": {
    "id": "arn:aws:ec2:us-east-2:010101010101:instance/i-01010101010101010",
    "name": "wiz-test-v1",
    "type": "virtualMachine",
    "cloudPlatform": "AWS",
    "subscriptionId": "010101010101",
    "subscriptionName": "AWS ACME TEST",
    "region": "eu-central-1",
    "status": "Active",
    "cloudProviderURL": "https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1#InstanceDetails:instanceId=i-01010101010101010"
  },
  "control": {
    "id": "wtest-id-0000",
    "name": "Wiz Mock Data for Testing",
    "description": "",
    "severity": "LOW",
    "risks": []
  }
}
```

## Template request body

This template shows the default structure using template variables. For a complete list of all available variables you can use in your custom payload, see the [Template variables](#template-variables) section below.

```json Template request body
{
  "trigger": {
    "source": "{{triggerSource}}",
    "type": "{{triggerType}}",
    "ruleId": "{{ruleId}}",
    "ruleName": "{{ruleName}}",
    "updatedFields": "{{#changedFields}} {{name}} field was changed from {{previousValue}} to {{newValue}}, {{/* changedFields */}}",
    "changedBy": "{{changedBy}}"
  },
  "issue": {
    "id": "{{issue.id}}",
    "status": "{{issue.status}}",
    "severity": "{{issue.severity}}",
    "created": "{{issue.createdAt}}",
    "projects": "{{#issue.projects}}{{name}}, {{/* issue.projects */}}"
  },
  "resource": {
    "id": "{{issue.entitySnapshot.providerId}}",
    "name": "{{issue.entitySnapshot.name}}",
    "type": "{{issue.entitySnapshot.nativeType}}",
    "cloudPlatform": "{{issue.entitySnapshot.cloudPlatform}}",
    "subscriptionId": "{{issue.entitySnapshot.subscriptionExternalId}}",
    "subscriptionName": "{{issue.entitySnapshot.subscriptionName}}",
    "region": "{{issue.entitySnapshot.region}}",
    "status": "{{issue.entitySnapshot.status}}",
    "cloudProviderURL": "{{issue.entitySnapshot.cloudProviderURL}}"
  },
  "control": {
    "id": "{{issue.control.id}}",
    "name": "{{issue.control.name}}",
    "description": "{{issue.control.descriptionPlainText}}",
    "severity": "{{issue.control.severity}}",
    "risks": {{issue.control.risks}}{{^issue.control.risks}}[]{{/* issue.control.risks */}}
  }
}
```

## Template variables

When configuring webhooks, the following objects and their template variables are available. Each object represents a different aspect of the triggered event:

| Object                                        | Description                                                                                     |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [Trigger object](#trigger-object-variables)   | Represents the cause of the webhook firing, including automation rule details and changes made. |
| [Issue object](#issue-object-variables)       | Represents the Issue itself and its properties.                                                 |
| [Resource object](#resource-object-variables) | Represents the affected cloud resource (VM, container, etc.) where Wiz detected the Issue.      |
| [Control object](#control-object-variables)   | Represents the Control that generated the Issue.                                                |

### Trigger object variables

Represents the cause of the webhook firing, including automation rule details and changes made.

| Variable             | Type/Example Format             | Description                                    |
| -------------------- | ------------------------------- | ---------------------------------------------- |
| `{{triggerSource}}`  | string                          | Source of the trigger                          |
| `{{triggerType}}`    | string                          | Type of trigger event                          |
| `{{ruleId}}`         | string                          | ID of the automation rule                      |
| `{{ruleName}}`       | string                          | Name of the automation rule                    |
| `{{#changedFields}}` | "field was changed from X to Y" | List of updated fields (requires #)            |
| `{{changedBy}}`      | string                          | User that initiated the change                 |
| `{{triggeredBy}}`    | string                          | The user or Automation Rule that ran an Action |

#### Changed Fields Format

```
{{#changedFields}} {{name}} field was changed from {{previousValue}} to {{newValue}}, {{/* changedFields */}}
```

### Issue Object Variables

Represents the Issue itself and its properties.

| Variable              | Example Format | Description                       |
| --------------------- | -------------- | --------------------------------- |
| `{{issue.id}}`        | string         | Unique identifier of the Issue    |
| `{{issue.status}}`    | string         | Current status of the Issue       |
| `{{issue.severity}}`  | string         | Severity level of the Issue       |
| `{{issue.createdAt}}` | ISO 8601       | Creation timestamp                |
| `{{issue.evidence}}`  | JSON           | Evidence details (see note below) |

#### Evidence structure

The `{{issue.evidence}}` JSON includes the following graph objects:

- Finding
- Configuration Finding
- Hosted Technology
- Malware Instance
- Secret Finding
- Access Role Permission
- User Account
- Service Account
- Endpoint
- Security Event Finding
- Lateral Movement Finding
- Namespace
- Kubernetes Cluster
- Authentication Configuration
- File Descriptor Finding

#### Notes and comments

```
{{#issue.notes}}{{user.email}}-{{text}}, {{/* issue.notes */}}
```

Includes:

- Ignore Reason
- Ignore Comment
- Ignore Until date

#### Service tickets

```
{{#issue.serviceTickets}}{{name}}, {{/* issue.serviceTickets */}}
```

#### Projects

Basic format:

```
{{#issue.projects}}{{name}}, {{/* issue.projects */}}
```

Extended formats:

```
Project name and description:
{{#issue.projects}}{{name}}:{{description}}, {{/* issue.projects */}}

Project name and owners:
{{#issue.projects}}{{name}}-owners:{{#projectOwners}}{{email}}, {{/* projectOwners */}}{{/* issue.projects */}}

Project name and business impact:
{{#issue.projects}}{{name}}-business impact:{{#riskProfile}}{{businessImpact}}, {{/* riskProfile */}}{{/* issue.projects */}}
```

### Resource Object Variables

Represents the affected cloud resource.

| Variable                                           | Type/Example Format | Description                       |
| -------------------------------------------------- | ------------------- | --------------------------------- |
| `{{issue.entitySnapshot.providerId}}`              | string              | Cloud provider's resource ID      |
| `{{issue.entitySnapshot.name}}`                    | string              | Resource name                     |
| `{{issue.entitySnapshot.nativeType}}`              | string              | Native resource type              |
| `{{issue.entitySnapshot.type}}`                    | string              | Resource type                     |
| `{{issue.entitySnapshot.cloudPlatform}}`           | string              | Cloud platform identifier         |
| `{{issue.entitySnapshot.subscriptionExternalId}}`  | string              | Subscription ID                   |
| `{{issue.entitySnapshot.subscriptionName}}`        | string              | Subscription name                 |
| `{{issue.entitySnapshot.region}}`                  | string              | Resource region                   |
| `{{issue.entitySnapshot.status}}`                  | string              | Resource status                   |
| `{{issue.entitySnapshot.cloudProviderURL}}`        | string              | URL to resource in cloud console  |
| `{{issue.entitySnapshot.createdAt}}`               | ISO 8601            | Creation time of primary resource |
| `{{issue.entitySnapshot.externalId}}`              | string              | External identifier               |
| `{{issue.entitySnapshot.resourceGroupExternalId}}` | string              | Resource group ID                 |
| `{{issue.entitySnapshot.kubernetesClusterId}}`     | string              | K8s cluster ID                    |
| `{{issue.entitySnapshot.kubernetesClusterName}}`   | string              | K8s cluster name                  |
| `{{issue.entitySnapshot.kubernetesNamespaceName}}` | string              | K8s namespace name                |
| `{{issue.entitySnapshot.containerServiceId}}`      | string              | Container service ID              |
| `{{issue.entitySnapshot.containerServiceName}}`    | string              | Container service name            |

#### JSON structure fields

The following fields return JSON and should not be wrapped in quotes when used in request bodies:

- `{{issue.entitySnapshot.tags}}`
- `{{issue.entitySnapshot.subscriptionTags}}`
- `{{issue.entitySnapshot.cloudProviderOriginalJson}}`

### Control object variables

Represents the Control that generated the Issue.

| Variable                                              | Type/Example Format | Description                          |
| ----------------------------------------------------- | ------------------- | ------------------------------------ |
| `{{issue.control.id}}`                                | string              | Control identifier                   |
| `{{issue.control.name}}`                              | string              | Control name                         |
| `{{issue.control.descriptionPlainText}}`              | string              | Control description                  |
| `{{issue.control.severity}}`                          | string              | Control severity level               |
| `{{issue.control.risks}}`                             | JSON Array          | Associated risks                     |
| `{{issue.control.resolutionRecommendation}}`          | string              | Resolution recommendation            |
| `{{issue.control.resolutionRecommendationPlainText}}` | string              | Plain text resolution recommendation |
| `{{issue.control.sourceCloudConfigurationRule.id}}`   | string              | Source cloud configuration rule ID   |
| `{{issue.control.sourceCloudConfigurationRule.name}}` | string              | Source cloud configuration rule name |

## Portal link format

To create a link back to the Wiz portal to view the Issue:

```
https://{{wizDomain}}/issues#~(issue~'{{issue.id}})
```

## Important notes

1. All date fields follow ISO 8601 format (`YYYY-MM-DDThh:mm:ss.sTZD`)
2. Variables with `#` require both opening and closing tags (e.g., `{{#issue.projects}}` and `{{/* issue.projects */}}`)
3. For specific tag values, use dot notation: `issue.entitySnapshot.tags.TagName` or `issue.entitySnapshot.subscriptionTags.TagName`
4. JSON structure variables (`issue.evidence`, `issue.entitySnapshot.tags`, `issue.entitySnapshot.subscriptionTags`, and `issue.entitySnapshot.cloudProviderOriginalJson`) should not be wrapped in quotes in request bodies
5. All template variables must be surrounded by double curly braces in integrations
