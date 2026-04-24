# Custom Report Columns
*Reference documentation for custom column configurations in WIN API reports, including supported data types and formats.*

Category: reference

The `columnSelection` parameter lets you customize which columns appear in your report by accepting an array of enum values. If `columnSelection` is not specified, the report includes only the standard default columns.

:::warning[`columnSelection` overrides the default columns]

When using `columnSelection`, you are defining the complete set of columns for the report. Be sure to include any default columns you want to keep, such as `createdAt`.

:::

## Application Endpoints

<Expandable title="Columns">

Default columns:

- `id`
- `externalId`
- `name`
- `host`
- `port`
- `protocols`
- `projectNames`
- `cloudPlatform`
- `cloudAccount.externalId`
- `cloudAccount.name`
- `tags`
- `firstSeen`
- `updatedAt`
- `portStatus`
- `exposureLevel`
- `scanSources`
- `httpStatusCode`
- `httpStatus`
- `httpTitle`
- `httpContentType`
- `authMethod`
- `authProvider`
- `technologies`
- `resources`
- `relatedIssues.criticalCount`
- `relatedIssues.highCount`
- `relatedIssues.mediumCount`
- `relatedIssues.lowCount`
- `relatedIssues.infoCount`

Optional custom columns:

- `cloudAccount.id`

</Expandable>

## Cloud Configuration Findings

<Expandable title="Columns">

Default columns:

- `Id`
- `AnalyzedAt`
- `ObjectId`
- `ObjectProviderId`
- `ObjectName`
- `ObjectType`
- `ObjectNativeType`
- `ConfigurationRuleName`
- `ConfigurationRuleID`
- `ConfigurationRuleDescription`
- `Severity`
- `CurrentConfigurationValue`
- `ExpectedConfigurationValue`
- `CloudSourceLink`
- `ConfigurationPath`
- `Remediation`
- `ScopeObjectType`
- `ScopeObjectId`
- `ScopeObjectProviderId`
- `ObjectRegion`
- `ProductIds`
- `ObjectCloudPlatform`
- `FirstDetectedAt`
- `LastDetectedAt`
- `ObjectTags`

Optional custom columns\*

- `Category`
- `ConfigurationRuleTags`
- `Framework`
- `IgnoreResolutionReason`
- `IgnoreRuleId`
- `IgnoreRuleName`
- `IgnoreRuleTags`
- `Note`
- `ObjectExternalId`
- `Projects`
- `ResourceStatus`
- `Status`
- `StatusChangedAt`
- `SubCategory`
- `SubscriptionName`

</Expandable>

## Cloud resources

<Expandable title="Columns">

Default columns:

- `id`
- `externalId`
- `name`
- `type`
- `nativeType`
- `technology.name`
- `technology.categories`
- `technology.stackLayer`
- `cloudPlatform`
- `cloudAccount.id`
- `cloudAccount.externalId`
- `cloudAccount.cloudProvider`
- `status`
- `region`
- `regionLocation`
- `tags`
- `projects`
- `createdAt`
- `updatedAt`
- `deletedAt`
- `firstSeen`
- `typeFields.kind`
- `typeFields.instanceType`
- `typeFields.operatingSystem`
- `resourceGroup.id`
- `resourceGroup.externalId`
- `isOpenToAllInternet`
- `isAccessibleFromInternet`

Optional custom columns:

- `providerUniqueId`
- `codeToCloudPipelineStage`
- `technology.id`
- `technology.description`
- `technology.deploymentModel`
- `technology.status`
- `technology.note`
- `technology.ownerName`
- `technology.ownerHeadquartersCountryCode`
- `technology.isBillableWorkload`
- `technology.businessModel`
- `technology.popularity`
- `technology.instanceEntityType`
- `technology.instanceEntityTypes`
- `technology.instanceNativeTypes`
- `technology.onlyServiceUsageSupported`
- `technology.propertySections`
- `technology.hasApplicationFingerprint`
- `technology.isEndOfLife`
- `technology.isSensitive`
- `technology.isThreatTarget`
- `technology.isEndOfLifeSupported`
- `technology.supportsTagging`
- `technology.supportedIaCPlatforms`
- `technology.isCloudService`
- `technology.isAppliance`
- `technology.isDataScanSupported`
- `technology.isSupportedByVendor`
- `technology.isSupportedByCommunity`
- `technology.isGenerallyAvailable`
- `technology.supportedOperatingSystems`
- `technology.primaryDnsName`
- `cloudAccount.name`
- `cloudOrganization.id`
- `codeRepository.id`
- `codeRepository.name`
- `codeRepository.type`
- `codeRepository.properties`
- `versionDetails.version`
- `versionDetails.versionsBehindLatest.major`
- `versionDetails.versionsBehindLatest.minor`
- `versionDetails.versionsBehindLatest.version`
- `versionDetails.minorVersion`
- `versionDetails.majorVersion`
- `lastSeen`
- `typeFields.ipAddresses`
- `typeFields.image.id`
- `typeFields.image.name`
- `typeFields.image.type`
- `typeFields.image.properties`
- `typeFields.containerRepository.id`
- `typeFields.containerRepository.name`
- `typeFields.containerRepository.type`
- `typeFields.containerRepository.properties`
- `typeFields.operatingSystemDistribution.id`
- `typeFields.operatingSystemDistribution.name`
- `typeFields.operatingSystemDistribution.description`
- `typeFields.operatingSystemDistribution.categories`
- `typeFields.operatingSystemDistribution.stackLayer`
- `typeFields.operatingSystemDistribution.deploymentModel`
- `typeFields.operatingSystemDistribution.status`
- `typeFields.operatingSystemDistribution.note`
- `typeFields.operatingSystemDistribution.ownerName`
- `typeFields.operatingSystemDistribution.ownerHeadquartersCountryCode`
- `typeFields.operatingSystemDistribution.isBillableWorkload`
- `typeFields.operatingSystemDistribution.businessModel`
- `typeFields.operatingSystemDistribution.popularity`
- `typeFields.operatingSystemDistribution.instanceEntityType`
- `typeFields.operatingSystemDistribution.instanceEntityTypes`
- `typeFields.operatingSystemDistribution.instanceNativeTypes`
- `typeFields.operatingSystemDistribution.onlyServiceUsageSupported`
- `typeFields.operatingSystemDistribution.propertySections`
- `typeFields.operatingSystemDistribution.hasApplicationFingerprint`
- `typeFields.operatingSystemDistribution.isEndOfLife`
- `typeFields.operatingSystemDistribution.isSensitive`
- `typeFields.operatingSystemDistribution.isThreatTarget`
- `typeFields.operatingSystemDistribution.isEndOfLifeSupported`
- `typeFields.operatingSystemDistribution.supportsTagging`
- `typeFields.operatingSystemDistribution.supportedIaCPlatforms`
- `typeFields.operatingSystemDistribution.isCloudService`
- `typeFields.operatingSystemDistribution.isAppliance`
- `typeFields.operatingSystemDistribution.isDataScanSupported`
- `typeFields.operatingSystemDistribution.isSupportedByVendor`
- `typeFields.operatingSystemDistribution.isSupportedByCommunity`
- `typeFields.operatingSystemDistribution.isGenerallyAvailable`
- `typeFields.operatingSystemDistribution.supportedOperatingSystems`
- `typeFields.operatingSystemDistribution.primaryDnsName`
- `typeFields.baseContainerImage.id`
- `typeFields.baseContainerImage.name`
- `typeFields.baseContainerImage.type`
- `typeFields.baseContainerImage.properties`
- `resourceGroup.name`
- `hasAccessToSensitiveData`
- `hasAdminPrivileges`
- `hasHighPrivileges`
- `hasSensitiveData`
- `issueAnalytics.issueCount`
- `issueAnalytics.informationalSeverityCount`
- `issueAnalytics.lowSeverityCount`
- `issueAnalytics.mediumSeverityCount`
- `issueAnalytics.highSeverityCount`
- `issueAnalytics.criticalSeverityCount`
- `applicationServices`
- `iacDetails.iacStatus`
- `iacDetails.iacDetectionMethod`
- `iacDetails.iacPlatform`
- `iacDetails.iacDriftDetectionMethod`
- `owners`
- `graphEntity.providerUniqueId`
- `graphEntity.properties`
- `graphEntity.providerData`
- `isAvailableOnGraph`
- `revisions`

</Expandable>

## Compliance assessment

<Expandable title="Columns">

Default columns:

- `Resource Name`
- `Cloud Provider ID`
- `Object Type`
- `Native Type`
- `Tags`
- `Subscription`
- `Projects`
- `Cloud Provider`
- `Policy ID`
- `Policy Short Name`
- `Policy Name`
- `Policy Type`
- `Severity`
- `Result`
- `Compliance Check Name (Wiz Subcategory)`
- `Category`
- `Framework`
- `Remediation Steps`
- `Assessed At`
- `Created At`
- `Updated At`
- `Subscription Name`
- `Subscription Provider ID`
- `Resource ID`
- `Resource Region`
- `Resource Cloud Platform`

Optional custom columns

- `Ignore Reason`
- `Issue/Finding ID`
- `Policy Description`
- `Policy Tags`
- `Project Names`
- `Resource Group Name`
- `Subscription Status`

</Expandable>

## Hosted technologies

<Expandable title="Columns">

Default columns:

- `id`
- `externalId`
- `name`
- `technology.name`
- `technology.categories`
- `technology.stackLayer`
- `technology.ownerName`
- `technology.businessModel`
- `resource.id`
- `resource.externalId`
- `resource.name`
- `resource.type`
- `resource.nativeType`
- `resource.cloudPlatform`
- `resource.cloudAccount.id`
- `resource.cloudAccount.externalId`
- `resource.cloudAccount.cloudProvider`
- `resource.status`
- `resource.region`
- `resource.regionLocation`
- `resource.tags`
- `resource.projects`
- `resource.typeFields.operatingSystem`
- `resource.isOpenToAllInternet`
- `resource.isAccessibleFromInternet`
- `versionDetails.version`
- `versionDetails.isEndOfLife`
- `versionDetails.isLatest`
- `versionDetails.endOfLifeDate`
- `detectionMethods`
- `firstSeen`
- `updatedAt`
- `deletedAt`

Optional custom columns:

- `configurationScanAnalytics.errorCount`
- `configurationScanAnalytics.failCount`
- `configurationScanAnalytics.notAssessedCount`
- `configurationScanAnalytics.passCount`
- `configurationScanAnalytics.successPercentage`
- `configurationScanAnalytics.totalCount`
- `evidence.filePaths`
- `evidence.installedProgramNames`
- `evidence.libraryNames`
- `evidence.packageNames`
- `evidence.windowsServiceNames`
- `graphEntity.firstSeen`
- `graphEntity.hasOriginalObject`
- `graphEntity.id`
- `graphEntity.lastSeen`
- `graphEntity.name`
- `graphEntity.originalObject`
- `graphEntity.peripheralData`
- `graphEntity.projects`
- `graphEntity.properties`
- `graphEntity.providerData`
- `graphEntity.providerUniqueId`
- `graphEntity.type`
- `installedPackages`
- `isOfficiallyMaintained`
- `isSystemRestartRequired`
- `resource.cloudAccount.name`
- `resource.codeRepository.firstSeen`
- `resource.codeRepository.hasOriginalObject`
- `resource.codeRepository.id`
- `resource.codeRepository.lastSeen`
- `resource.codeRepository.name`
- `resource.codeRepository.originalObject`
- `resource.codeRepository.peripheralData`
- `resource.codeRepository.projects`
- `resource.codeRepository.properties`
- `resource.codeRepository.providerData`
- `resource.codeRepository.providerUniqueId`
- `resource.codeRepository.type`
- `resource.graphEntity.firstSeen`
- `resource.graphEntity.hasOriginalObject`
- `resource.graphEntity.id`
- `resource.graphEntity.lastSeen`
- `resource.graphEntity.name`
- `resource.graphEntity.originalObject`
- `resource.graphEntity.peripheralData`
- `resource.graphEntity.projects`
- `resource.graphEntity.properties`
- `resource.graphEntity.providerData`
- `resource.graphEntity.providerUniqueId`
- `resource.graphEntity.type`
- `resource.hasAccessToSensitiveData`
- `resource.hasAdminPrivileges`
- `resource.hasHighPrivileges`
- `resource.hasSensitiveData`
- `resource.typeFields.executionController.firstSeen`
- `resource.typeFields.executionController.hasOriginalObject`
- `resource.typeFields.executionController.id`
- `resource.typeFields.executionController.lastSeen`
- `resource.typeFields.executionController.name`
- `resource.typeFields.executionController.originalObject`
- `resource.typeFields.executionController.peripheralData`
- `resource.typeFields.executionController.projects`
- `resource.typeFields.executionController.properties`
- `resource.typeFields.executionController.providerData`
- `resource.typeFields.executionController.providerUniqueId`
- `resource.typeFields.executionController.type`
- `resource.typeFields.image.externalId`
- `resource.typeFields.image.id`
- `resource.typeFields.image.name`
- `resource.typeFields.image.providerUniqueId`
- `resource.typeFields.kubernetesCluster.firstSeen`
- `resource.typeFields.kubernetesCluster.hasOriginalObject`
- `resource.typeFields.kubernetesCluster.id`
- `resource.typeFields.kubernetesCluster.lastSeen`
- `resource.typeFields.kubernetesCluster.name`
- `resource.typeFields.kubernetesCluster.originalObject`
- `resource.typeFields.kubernetesCluster.peripheralData`
- `resource.typeFields.kubernetesCluster.projects`
- `resource.typeFields.kubernetesCluster.properties`
- `resource.typeFields.kubernetesCluster.providerData`
- `resource.typeFields.kubernetesCluster.providerUniqueId`
- `resource.typeFields.kubernetesCluster.type`
- `resource.typeFields.kubernetesNamespace.firstSeen`
- `resource.typeFields.kubernetesNamespace.hasOriginalObject`
- `resource.typeFields.kubernetesNamespace.id`
- `resource.typeFields.kubernetesNamespace.lastSeen`
- `resource.typeFields.kubernetesNamespace.name`
- `resource.typeFields.kubernetesNamespace.originalObject`
- `resource.typeFields.kubernetesNamespace.peripheralData`
- `resource.typeFields.kubernetesNamespace.projects`
- `resource.typeFields.kubernetesNamespace.properties`
- `resource.typeFields.kubernetesNamespace.providerData`
- `resource.typeFields.kubernetesNamespace.providerUniqueId`
- `resource.typeFields.kubernetesNamespace.type`
- `resource.typeFields.virtualMachine.firstSeen`
- `resource.typeFields.virtualMachine.hasOriginalObject`
- `resource.typeFields.virtualMachine.id`
- `resource.typeFields.virtualMachine.lastSeen`
- `resource.typeFields.virtualMachine.name`
- `resource.typeFields.virtualMachine.originalObject`
- `resource.typeFields.virtualMachine.peripheralData`
- `resource.typeFields.virtualMachine.projects`
- `resource.typeFields.virtualMachine.properties`
- `resource.typeFields.virtualMachine.providerData`
- `resource.typeFields.virtualMachine.providerUniqueId`
- `resource.typeFields.virtualMachine.type`
- `snippets`
- `technology.deploymentModel`
- `technology.description`
- `technology.hasApplicationFingerprint`
- `technology.id`
- `technology.instanceEntityType`
- `technology.instanceEntityTypes`
- `technology.instanceNativeTypes`
- `technology.isAppliance`
- `technology.isBillableWorkload`
- `technology.isCloudService`
- `technology.isDataScanSupported`
- `technology.isEndOfLife`
- `technology.isEndOfLifeSupported`
- `technology.isGenerallyAvailable`
- `technology.isSensitive`
- `technology.isSupportedByCommunity`
- `technology.isSupportedByVendor`
- `technology.isThreatTarget`
- `technology.note`
- `technology.onlyServiceUsageSupported`
- `technology.ownerHeadquartersCountryCode`
- `technology.popularity`
- `technology.primaryDnsName`
- `technology.propertySections`
- `technology.status`
- `technology.supportedIaCPlatforms`
- `technology.supportedOperatingSystems`
- `technology.supportsTagging`
- `validatedInRuntime`
- `versionDetails.edition`
- `versionDetails.hasExtendedSupport`
- `versionDetails.latestVersion`
- `versionDetails.latestVersionReleaseDate`
- `versionDetails.majorVersion`
- `versionDetails.releaseDate`

</Expandable>

## IaC Findings

<Expandable title="Columns">

Default standard columns:

- `id`
- `rule.name`
- `rule.shortId`
- `severity`
- `status`
- `firstSeenAt`
- `lastSeenAt`
- `platform`
- `filePath`
- `repository.id`
- `repository.name`
- `cloudPlatform`

Optional custom columns:

- `branch.id`
- `branch.name`
- `endLine`
- `entityType`
- `expectedContent`
- `fileRemediation.after`
- `fileRemediation.before`
- `fileRemediation.endLine`
- `fileRemediation.endPos`
- `fileRemediation.filePath`
- `fileRemediation.remediationType`
- `fileRemediation.startLine`
- `fileRemediation.startPos`
- `fileURL`
- `foundContent`
- `matchContent`
- `name`
- `nativeType`
- `remediationInstructions`
- `resourceGraphEntity.id`
- `rule.cloudProvider`
- `rule.id`
- `rule.severity`
- `startLine`
- `updatedAt`
- `vcsDetails.codeAuthors`
- `vcsDetails.codeOwners`
- `vcsPlatform`
- `wizUrl`

</Expandable>

## Issues

<Expandable title="Columns">

Default standard columns:

- `Cloud Provider URL`
- `Container Service`
- `Control ID`
- `Created At`
- `Description`
- `Due At`
- `Issue ID`
- `Kubernetes Cluster`
- `Kubernetes Namespace`
- `Note`
- `Project IDs`
- `Project Names`
- `Provider ID`
- `Remediation Recommendation`
- `Resolution`
- `Resolved Time`
- `Resource external ID`
- `Resource Name`
- `Resource original JSON`
- `Resource OS`
- `Resource Platform`
- `Resource Region`
- `Resource Status`
- `Resource Tags`
- `Resource Type`
- `Resource vertex ID`
- `Risks`
- `Severity`
- `Status`
- `Status Changed At`
- `Subscription ID`
- `Subscription Name`
- `Threats`
- `Ticket URLs`
- `Title`
- `Updated At`
- `Wiz URL`

Default detailed columns:

Includes all standard columns, plus `evidence`.

Optional custom columns:

All columns from standard and detailed.

</Expandable>

## Secret Findings

<Expandable title="Columns">

Default columns:

- `id`
- `type`
- `name`
- `externalId`
- `confidence`
- `severity`
- `isEncrypted`
- `isManaged`
- `path`
- `snippet`
- `rule.id`
- `rule.name`
- `rule.type`
- `resource.id`
- `resource.name`
- `resource.type`
- `resource.externalId`
- `resource.cloudAccount.id`
- `resource.cloudAccount.externalId`
- `resource.cloudAccount.name`
- `resource.cloudAccount.cloudProvider`
- `resource.nativeType`
- `resource.region`
- `resource.status`
- `resource.tags`
- `status`
- `projects`
- `firstSeenAt`
- `lastModifiedAt`
- `lastUpdatedAt`
- `resolvedAt`

Optional custom columns:

- `applicationServices`
- `codeToCloudPipelineStage`
- `endOffset`
- `environments`
- `hasLeaked`
- `ignoreRules`
- `lastSeenAt`
- `lastValidatedAt`
- `leakage.metadata.executionPath`
- `leakage.metadata.incidentAt`
- `leakage.metadata.ipAddress`
- `leakage.metadata.operatingSystem`
- `leakage.metadata.publishedAt`
- `leakage.metadata.systemName`
- `leakage.metadata.userName`
- `lineNumber`
- `osPackageName`
- `passwordDetails.entropy`
- `passwordDetails.isComplex`
- `passwordDetails.length`
- `relatedApplicationServices`
- `relatedIssueAnalytics.criticalSeverityCount`
- `relatedIssueAnalytics.highSeverityCount`
- `relatedIssueAnalytics.informationalSeverityCount`
- `relatedIssueAnalytics.issueCount`
- `relatedIssueAnalytics.lowSeverityCount`
- `relatedIssueAnalytics.mediumSeverityCount`
- `resolutionReason`
- `resource.cloudProviderURL`
- `resource.typedProperties.encryptedAtRest`
- `resource.typedProperties.image.externalId`
- `resource.typedProperties.image.id`
- `resource.typedProperties.image.name`
- `resource.typedProperties.image.nativeType`
- `resource.typedProperties.image.providerUniqueId`
- `resource.typedProperties.isDefaultBranch`
- `resource.typedProperties.isManaged`
- `resource.typedProperties.loggingEnabled`
- `resource.typedProperties.networkProperties.hasLimitedInternetExposure`
- `resource.typedProperties.networkProperties.hasWideInternetExposure`
- `resource.typedProperties.networkProperties.isAccessibleFromOtherSubscriptions`
- `resource.typedProperties.networkProperties.isAccessibleFromOtherVnets`
- `resource.typedProperties.networkProperties.isAccessibleFromVPN`
- `resource.typedProperties.registry.externalId`
- `resource.typedProperties.registry.id`
- `resource.typedProperties.registry.name`
- `resource.typedProperties.repository.archived`
- `resource.typedProperties.repository.externalId`
- `resource.typedProperties.repository.id`
- `resource.typedProperties.repository.name`
- `resource.typedProperties.repository.platform`
- `resource.typedProperties.repository.public`
- `resource.typedProperties.repositoryExternalId`
- `resource.typedProperties.runtime`
- `resource.typedProperties.serverlessContainer`
- `resource.typedProperties.versioningEnabled`
- `resource.typedProperties.vmExternalId`
- `rule.confidence`
- `rule.contentRegex`
- `rule.description`
- `rule.enabled`
- `rule.isAiPowered`
- `rule.keyValueContentRegex`
- `rule.originalSecretDetectionRuleOverridden`
- `rule.pathRegex`
- `rule.quickContentRegex`
- `rule.remediationInstructions`
- `rule.severity`
- `rule.targetPlatforms`
- `rule.validityCheckDescription`
- `rule.validityCheckSupported`
- `scanType`
- `secretDataEntities`
- `secretDataId`
- `sharingVisibility`
- `sshAuthorizedKeyDetails.comment`
- `startOffset`
- `traits`
- `validationDetails.validationResponseBody`
- `validationDetails.validationResponseStatusCode`
- `validationStatus`
- `vcsCodeAuthors`
- `vcsCodeOwners`
- `vcsDetails.initialCommitHash`

</Expandable>

## Vulnerabilities

<Expandable title="Columns">

Default columns:

- `ID`
- `WizURL`
- `Name`
- `CVSSSeverity`
- `HasExploit`
- `HasCisaKevExploit`
- `FindingStatus`
- `Score`
- `Severity`
- `VendorSeverity`
- `NvdSeverity`
- `FirstDetected`
- `LastDetected`
- `ResolvedAt`
- `ResolutionReason`
- `Remediation`
- `LocationPath`
- `DetailedName`
- `Version`
- `FixedVersion`
- `DetectionMethod`
- `Link`
- `Projects`
- `AssetID`
- `AssetName`
- `AssetRegion`
- `ProviderUniqueId`
- `CloudProviderURL`
- `CloudPlatform`
- `Status`
- `SubscriptionExternalId`
- `SubscriptionId`
- `SubscriptionName`
- `Tags`
- `ExecutionControllers`
- `ExecutionControllersSubscriptionExternalIds`
- `ExecutionControllersSubscriptionNames`
- `ExecutionControllersKubernetesClusterNames`
- `CriticalRelatedIssuesCount`
- `HighRelatedIssuesCount`
- `MediumRelatedIssuesCount`
- `LowRelatedIssuesCount`
- `InfoRelatedIssuesCount`
- `OperatingSystem`
- `IpAddresses`

Default detailed columns:

Includes all default columns (above) and the following:

`CVEDescription`  
`Description`  
`ExploitabilityScore`  
`ImpactScore`  

Optional custom columns:

- `AI Model Evidence`
- `Affected By Settings`
- `Asset has limited internet exposure`
- `Asset has wide internet exposure`
- `Asset is accessible from VPN`
- `Asset is accessible from other VNets`
- `Asset is accessible from other subscriptions`
- `Asset was detected On-Prem`
- `AssetExternalId`
- `AssetNativeType`
- `AssetType`
- `Attack Complexity (CVSS V2)`
- `Attack Complexity (CVSS V3)`
- `Attack Complexity (CVSS V4)`
- `Attack Requirements (CVSS V4)`
- `Attack Vector (CVSS V2)`
- `Attack Vector (CVSS V3)`
- `Attack Vector (CVSS V4)`
- `Availability Impact (CVSS V2)`
- `Availability Impact (CVSS V3)`
- `CISA KEV Due Date`
- `CISA KEV Release Date`
- `CNAScore`
- `CVEDescription`
- `Code Library Language`
- `Code To Cloud Pipeline Stage`
- `ComputeInstanceGroupExternalId`
- `ComputeInstanceGroupName`
- `ComputeInstanceGroupReplicaCount`
- `ComputeInstanceGroupTags`
- `Confidentiality Impact (CVSS V2)`
- `Confidentiality Impact (CVSS V3)`
- `Container Registry`
- `Container Repository`
- `Description`
- `End of Life Date`
- `ExploitabilityScore`
- `Exploitation Probability (EPSS)`
- `Exploitation Probability Percentile (EPSS)`
- `Exploitation Probability Severity (EPSS)`
- `Fix Date`
- `Has One Click Remediation`
- `Image layer hash`
- `ImpactScore`
- `Initial Access Potential`
- `Integrity Impact (CVSS V2)`
- `Integrity Impact (CVSS V3)`
- `Is Client Side`
- `Is Common Dependency`
- `Is High Profile Threat`
- `Is Malicious Package`
- `Is Operating System End of Life`
- `IsOSDiskSource`
- `Library Dependency Trees`
- `LineNumber`
- `NVDScore`
- `Operating System Distribution`
- `Privileges Required (CVSS V2)`
- `Privileges Required (CVSS V3)`
- `Privileges Required (CVSS V4)`
- `Published Date`
- `RecommendedVersion`
- `ResourceGroupExternalId`
- `RuntimeValidationResult`
- `Scan Source`
- `Scope (CVSS V3)`
- `ServiceNames`
- `Source`
- `SourceVolumeExternalId`
- `StatusUpdatedAt`
- `Technology Name`
- `Transitivity`
- `UniqueContainerImageReferenceTags`
- `UniqueContainerNames`
- `UniqueContainerTags`
- `UniqueContainerVmTags`
- `UpdatedAt`
- `UsedInCodeResult`
- `User Interaction (CVSS V4)`
- `User Interaction Required (CVSS V2)`
- `User Interaction Required (CVSS V3)`
- `Vector String (CVSS V2)`
- `Vector String (CVSS V3)`
- `Vector String (CVSS V4)`
- `VendorScore`
- `Virtual Machine Image External ID`
- `Virtual Machine Image Name`
- `Virtual Machine Image Provider ID`
- `VulnerabilityCategory`
- `Vulnerable System Availability Impact (CVSS V4)`
- `Vulnerable System Confidentiality Impact (CVSS V4)`
- `Vulnerable System Integrity Impact (CVSS V4)`

</Expandable>
