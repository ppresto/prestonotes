# Cloud Configuration Findings Tutorial
*Learn how to pull Cloud Configuration Findings from Wiz using the configurationFindings query with filters for severity, status, and cloud platform.*

Category: ccf

In this tutorial, learn how to pull Cloud Configuration Findings:

- [Pull Cloud Configuration Findings](#pull-cloud-configuration-findings): Use to pull small amounts of findings
- [Pull Cloud Configuration Findings incrementally](#pull-cloud-configuration-findings-incrementally): Use to pull daily updates incrementally

## Prerequisites

- Valid Bearer token—[Get a token](dev:generate-api-token)
- Wiz service account with `read:cloud_configuration`

%WIZARD_START_CLOSED%

### Pull Cloud Configuration Findings

Execute the `CloudConfigurationFindingsPage` query to return a list of Cloud Configuration Findings according to different filters, such as rule, resource, or security framework.

The following query returns the first five Cloud Configuration Rules, where:

- `first`—Pagination value that determines the number of results per page. You must include a value or the API call fails. This example returns the first 5 results.
- `resource.cloudPlatform`—Filter the results based on the desired cloud provider(s). This example returns findings from AWS.
- `severity`—Filter the results by severity level. This example returns findings with high severity.
- `includeDeleted`—Whether to filter deleted resources. [Learn how Wiz handles deleted resources](dev:limitations#handling-deleted-resources).

For more information and to refine your query, see the [Get Cloud Configuration Findings API](dev:configuration-finding) reference.

```json Example query
{
  "query": "query CloudConfigurationFindingsPage(   $filterBy: ConfigurationFindingFilters   $first: Int   $after: String   $orderBy: ConfigurationFindingOrder ) {   configurationFindings(     filterBy: $filterBy     first: $first     after: $after     orderBy: $orderBy   ) {     nodes {       id       targetExternalId   deleted    targetObjectProviderUniqueId       firstSeenAt       severity       result       status       remediation       resource {         id         providerId         name         nativeType         type         region         subscription {           id           name           externalId           cloudProvider         }         projects {           id           name           riskProfile {             businessImpact           }         }         tags {           key           value         }       }       rule {         id         graphId         name         description         remediationInstructions         functionAsControl       }       securitySubCategories {         id         title         category {           id           name           framework {             id             name           }         }       }     }     pageInfo {       hasNextPage       endCursor     }   } }",
  "variables": {
    "first": 5,
    "filterBy": {
      "resource": {
        "cloudPlatform": ["AWS"]
      },
      "severity": ["HIGH"],
      "includeDeleted": false
    }
  }
}
```

A successful request returns the specified number of Cloud Configuration Rules according to the requested fields:

````json Example response
{
  "data": {
    "configurationFindings": {
      "nodes": [
        {
          "id": "191cc8f8-9e00-5655-90b0-72a8515688e1",
          "targetExternalId": "arn:aws:rds:us-east-1:998231069301:db:database-1",
          "deleted": false,
          "targetObjectProviderUniqueId": "arn:aws:rds:us-east-1:998231069301:db:database-1",
          "firstSeenAt": "2022-10-02T19:38:06.157828Z",
          "severity": "HIGH",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "866f66ed-0fd7-5e29-94ef-3d86e8567113",
            "providerId": "arn:aws:rds:us-east-1:998231069301:db:database-1",
            "name": "database-1",
            "nativeType": "rds/PostgreSQL/instance",
            "type": "DB_SERVER",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "b7cf19cf-8fc7-4760-860c-55aec1ef2a0e",
            "graphId": "61005e0f-1405-5788-a33e-def039318787",
            "name": "RDS PostgreSQL instance should be upgraded to protect against local file read vulnerability",
            "description": "This rule checks whether the RDS PostgreSQL Instance version is vulnerable to the local file read vulnerability.  \nThis rule fails if the `EngineVersion` is a vulnerable version. To view the list of vulnerable versions, see the Rego code.  \nAs per the AWS security bulletin [AWS-2022-004](https://aws.amazon.com/security/security-bulletins/AWS-2022-004/), vulnerable PostgreSQL clusters might inadvertently allow authenticated users to gain local file read permissions on the host machine and obtain credentials for an unknown internal AWS service, due to a vulnerability in a third-party extension named `log_fdw`, which is pre-installed by default in Amazon Aurora PostgreSQL and Amazon RDS for PostgreSQL.  \nIt is recommended to upgrade the RDS instance from the deprecated and vulnerable version.",
            "remediationInstructions": "Perform the following command to upgrade the RDS instance via AWS CLI:  \n```  \naws rds modify-db-instance --db-instance-identifier {{`instanceId`}} --engine-version <desiredVersion> --apply-immediately  \n```",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-7",
              "title": "Baseline Configuration",
              "category": {
                "id": "wct-id-4",
                "name": "3 Baseline Configuration",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-9",
              "title": "Patch Management",
              "category": {
                "id": "wct-id-2",
                "name": "1 Patch Management",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-5",
              "title": "Vulnerability Assessment",
              "category": {
                "id": "wct-id-3",
                "name": "2 Vulnerability Assessment",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-9622",
              "title": "Unpatched software version",
              "category": {
                "id": "wct-id-1174",
                "name": "8 Application & Software Management",
                "framework": {
                  "id": "wf-id-53",
                  "name": "Wiz for Risk Assessment"
                }
              }
            }
          ]
        },
        {
          "id": "f1541ced-6606-52bf-8a94-67f50f15b1a0",
          "targetExternalId": "testoronprivate",
          "targetObjectProviderUniqueId": "arn:aws:s3:::testoronprivate",
          "firstSeenAt": "2023-07-05T16:43:34.432962Z",
          "severity": "HIGH",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "6973f0a8-76a5-5741-aad4-59737240c32e",
            "providerId": "arn:aws:s3:::testoronprivate",
            "name": "testoronprivate",
            "nativeType": "bucket",
            "type": "BUCKET",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "bdb6c792-6bba-4952-ad27-95a8ac0683f9",
            "graphId": "b702de76-5662-593a-8e3b-8a91277fbb95",
            "name": "S3 Bucket 'Block Public Access' settings should block the creation of new public ACLs",
            "description": "This rule checks whether the Block Public Access setting that blocks the creation of new public Access Control Lists (ACLs) is enabled, either on the account level or the bucket level.  \nThis rule fails if `accountPublicAccessBlockConfiguration.BlockPublicAcls` and `bucketPublicAccessBlock[_].BlockPublicAcls` are both not set to `true`.  \nThis rule skips S3 Buckets where the Bucket level Block Public Access configurations were not scanned successfully.  \nPublic Access to an S3 Bucket can be set using ACLs, IAM policies, or by using both methods. Using the Block Public Access settings ensures that S3 Buckets that should not be public remain that way, regardless of the policies or ACLs attached to them.\nIt is recommended to make use of these settings in order to help protect S3 buckets from unintentional exposure due to improper use of policies or ACLs.\n>**Note**  \nS3 ACLs are a legacy access control mechanism that predates IAM, and AWS recommends using S3 Bucket policies or IAM policies for access control.  \nFor this reason, it is recommended to enable this block on an account-level, to ensure the use of ACLs to grant public access is blocked for all existing and new buckets in the entire account.   \nTo check if this setting is enabled on the account-level only, see `S3-027`.",
            "remediationInstructions": "Perform the following command to enable the Block Public Access setting that blocks the creation of new public ACLs via AWS CLI:  \n```  \naws s3api put-public-access-block \\\n    --bucket {{`bucketName`}} \\\n    --public-access-block-configuration \"BlockPublicAcls=true,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false\"  \n```\n>**Note**\nIn it's default format, this command will also disable all other Public Access Settings.  \nEnsure that you enable all settings as required by your organization by setting them to `true`.  ",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-3",
              "title": "Exposure Management",
              "category": {
                "id": "wct-id-5",
                "name": "4 Exposure Management",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-8364",
              "title": "Resource with public exposure",
              "category": {
                "id": "wct-id-1172",
                "name": "5 Network & API Design",
                "framework": {
                  "id": "wf-id-53",
                  "name": "Wiz for Risk Assessment"
                }
              }
            }
          ]
        },
        {
          "id": "e1ec730e-4692-5e2c-b912-952e642de1d0",
          "targetExternalId": "testoronprivate",
          "targetObjectProviderUniqueId": "arn:aws:s3:::testoronprivate",
          "firstSeenAt": "2023-07-05T16:43:34.408882Z",
          "severity": "HIGH",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "6973f0a8-76a5-5741-aad4-59737240c32e",
            "providerId": "arn:aws:s3:::testoronprivate",
            "name": "testoronprivate",
            "nativeType": "bucket",
            "type": "BUCKET",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "64689a7d-7c2e-4bcb-b87a-60482041e3d8",
            "graphId": "f934a2cc-8e94-5b55-92a5-2b4a5644f17b",
            "name": "S3 Bucket level 'Block Public Access' setting should block public access through Policies",
            "description": "This rule checks whether the Block Public Access setting that blocks public access through Policies is enabled, either on the account level or the bucket level.  \nThis rule fails if `accountPublicAccessBlockConfiguration.RestrictPublicBuckets` and `bucketPublicAccessBlock[_].RestrictPublicBuckets` are both not set to `true`.  \nThis rule skips S3 Buckets where the Bucket level Block Public Access configurations were not scanned successfully.  \nPublic Access to an S3 Bucket can be set using ACLs, IAM policies, or by using both methods.  \nUsing the Block Public Access settings ensures that S3 Buckets that should not be public remain that way, regardless of the policies or ACLs attached to them.  \nIt is recommended to make use of these settings in order to help protect S3 buckets from unintentional exposure due to improper use of policies or ACLs.",
            "remediationInstructions": "Perform the following command to enable the Block Public Access setting that blocks public access through Policies via AWS CLI:  \n```  \naws s3api put-public-access-block \\\n    --bucket {{`bucketName`}}  \\\n    --public-access-block-configuration \"BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=true\"  \n```\n>**Note**\nIn it's default format, this command will also disable all other Public Access Settings.  \nEnsure that you enable all settings as required by your organization by setting them to `true`.  ",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-3",
              "title": "Exposure Management",
              "category": {
                "id": "wct-id-5",
                "name": "4 Exposure Management",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-8364",
              "title": "Resource with public exposure",
              "category": {
                "id": "wct-id-1172",
                "name": "5 Network & API Design",
                "framework": {
                  "id": "wf-id-53",
                  "name": "Wiz for Risk Assessment"
                }
              }
            }
          ]
        },
        {
          "id": "840573c3-464b-5e53-9521-66e548b82433",
          "targetExternalId": "testoronprivate",
          "targetObjectProviderUniqueId": "arn:aws:s3:::testoronprivate",
          "firstSeenAt": "2023-07-05T16:43:34.302485Z",
          "severity": "HIGH",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "6973f0a8-76a5-5741-aad4-59737240c32e",
            "providerId": "arn:aws:s3:::testoronprivate",
            "name": "testoronprivate",
            "nativeType": "bucket",
            "type": "BUCKET",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "3a1ff8a0-14c5-4f3e-a25a-6765c2a8aec6",
            "graphId": "f3047a02-df3f-5042-9b5e-3df7ce22a0ba",
            "name": "S3 Bucket level 'Block Public Access' setting should block public access through ACLs",
            "description": "This rule checks whether the Block Public Access setting that blocks public access through Access Control Lists (ACLs) is enabled, either on the account level or the bucket level.  \nThis rule fails if `accountPublicAccessBlockConfiguration.IgnorePublicAcls` and `bucketPublicAccessBlock[_].IgnorePublicAcls` are both not set to true.  \nThis rule skips S3 Buckets where the Bucket level Block Public Access configurations were not scanned successfully.  \nPublic Access to an S3 Bucket can be set using ACLs, IAM policies, or by using both methods.  \nUsing the Block Public Access settings ensures that S3 Buckets that should not be public remain that way, regardless of the policies or ACLs attached to them.  \nIt is recommended to make use of these settings in order to help protect S3 buckets from unintentional exposure due to improper use of policies or ACLs.  \n>**Note**  \nS3 ACLs are legacy access control mechanisms that predate IAM, and AWS recommends using S3 Bucket policies or IAM policies for access control.  \nFor this reason, it is recommended to enable this block on an account-level, to ensure the use of ACLs to grant public access is blocked for all existing and new buckets in the entire account.  \nTo check if this setting is enabled on the account-level only, see `S3-028`.",
            "remediationInstructions": "Perform the following command to enable the Block Public Access setting that blocks public access through ACLs via AWS CLI:  \n```  \naws s3api put-public-access-block \\\n    --bucket {{`bucketName`}}  \\\n    --public-access-block-configuration \"BlockPublicAcls=false,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false\"  \n```\n>**Note**\nIn it's default format, this command will also disable all other Public Access Settings.  \nEnsure that you enable all settings as required by your organization by setting them to `true`.  \n",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-3",
              "title": "Exposure Management",
              "category": {
                "id": "wct-id-5",
                "name": "4 Exposure Management",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            },
            {
              "id": "wsct-id-8364",
              "title": "Resource with public exposure",
              "category": {
                "id": "wct-id-1172",
                "name": "5 Network & API Design",
                "framework": {
                  "id": "wf-id-53",
                  "name": "Wiz for Risk Assessment"
                }
              }
            }
          ]
        },
        {
          "id": "d85aafc0-1795-568a-ae5c-68d9673b5359",
          "targetExternalId": "testoronprivate",
          "targetObjectProviderUniqueId": "arn:aws:s3:::testoronprivate",
          "firstSeenAt": "2023-01-26T16:58:37.249565Z",
          "severity": "HIGH",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "6973f0a8-76a5-5741-aad4-59737240c32e",
            "providerId": "arn:aws:s3:::testoronprivate",
            "name": "testoronprivate",
            "nativeType": "bucket",
            "type": "BUCKET",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "8f7a2c3f-7830-4225-a36d-b6fccd2e54c5",
            "graphId": "576a13c1-4245-5ced-9476-c58dbf04aff2",
            "name": "S3 Bucket ACL should not allow global 'READ' access",
            "description": "This rule checks whether the S3 Bucket allows global `READ` access.  \nThis rule fails if the `URI` field is set to `http://acs.amazonaws.com/groups/global/AuthenticatedUsers` or `http://acs.amazonaws.com/groups/global/AllUsers`, and if the `Permission` field is set to `FULL_CONTROL` or `READ`.  \nBy default, all Amazon S3 buckets and objects are private. Only the resource owner, which is the AWS account that created the bucket, can access that bucket.\nEven though the bucket may be private, if it has global read access, everyone can make it public, which can cause data leakage.",
            "remediationInstructions": "Perform the following command to remove the S3 global `READ` access via AWS CLI:  \n```  \naws s3api put-bucket-acl  \n  --bucket {{`bucketName`}}  \n  --acl private  \n```",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-5223",
              "title": "AC-3 ACCESS ENFORCEMENT (Moderate | Low)",
              "category": {
                "id": "wct-id-920",
                "name": "AC Access Control",
                "framework": {
                  "id": "wf-id-39",
                  "name": "FedRAMP (Moderate and Low levels)"
                }
              }
            },
            {
              "id": "wsct-id-4302",
              "title": "1.i Policy on the Use of Network Services",
              "category": {
                "id": "wct-id-893",
                "name": "1 Access Control, Network and Teleworking",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-4342",
              "title": "5.i Identification of Risks Related to External Parties",
              "category": {
                "id": "wct-id-897",
                "name": "5 External Third Party",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-4414",
              "title": "10.j Access Control to Program Source Code",
              "category": {
                "id": "wct-id-902",
                "name": "10 Cryptography",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-84",
              "title": "3 Access to systems and assets is controlled, incorporating the principle of least functionality",
              "category": {
                "id": "wct-id-372",
                "name": "12 Protective Technology (PR.PT)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-6254",
              "title": "IAM-14 Strong Authentication",
              "category": {
                "id": "wct-id-1067",
                "name": "10 - IAM Identity & Access Management",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-6557",
              "title": "Identity-based exposure",
              "category": {
                "id": "wct-id-1171",
                "name": "4 Identity Management",
                "framework": {
                  "id": "wf-id-53",
                  "name": "Wiz for Risk Assessment"
                }
              }
            },
            {
              "id": "wsct-id-9235",
              "title": "AC-3  Access enforcement",
              "category": {
                "id": "wct-id-1389",
                "name": "AC Access control",
                "framework": {
                  "id": "wf-id-70",
                  "name": "Canadian PBMM (ITSG-33)"
                }
              }
            },
            {
              "id": "wsct-id-3727",
              "title": "CC6.1-3 Manages Identification and Authentication",
              "category": {
                "id": "wct-id-835",
                "name": "CC6 Logical and Physical Access Controls",
                "framework": {
                  "id": "wf-id-5",
                  "name": "SOC 2"
                }
              }
            },
            {
              "id": "wsct-id-7268",
              "title": "SC-4 INFORMATION IN SHARED RESOURCES",
              "category": {
                "id": "wct-id-1192",
                "name": "SC SYSTEM AND COMMUNICATIONS PROTECTION",
                "framework": {
                  "id": "wf-id-48",
                  "name": "NIST SP 800-53 Revision 4"
                }
              }
            },
            {
              "id": "wsct-id-6268",
              "title": "IVS-08 Network Architecture Documentation - Identify and document high-risk environments.",
              "category": {
                "id": "wct-id-1069",
                "name": "12 - IVS Infrastructure & Virtualization Security",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-600",
              "title": "A.9.1.2 Access to networks and network services",
              "category": {
                "id": "wct-id-586",
                "name": "A.9 Access control",
                "framework": {
                  "id": "wf-id-3",
                  "name": "ISO/IEC 27001"
                }
              }
            },
            {
              "id": "wsct-id-6245",
              "title": "IAM-05 Least Privilege - Employ the least privilege principle when implementing information\nsystem access.",
              "category": {
                "id": "wct-id-1067",
                "name": "10 - IAM Identity & Access Management",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-7300",
              "title": "SC-8 TRANSMISSION CONFIDENTIALITY AND INTEGRITY",
              "category": {
                "id": "wct-id-1192",
                "name": "SC SYSTEM AND COMMUNICATIONS PROTECTION",
                "framework": {
                  "id": "wf-id-48",
                  "name": "NIST SP 800-53 Revision 4"
                }
              }
            },
            {
              "id": "wsct-id-4312",
              "title": "1.s Use of System Utilities",
              "category": {
                "id": "wct-id-893",
                "name": "1 Access Control, Network and Teleworking",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-4415",
              "title": "10.k Change Control Procedures",
              "category": {
                "id": "wct-id-902",
                "name": "10 Cryptography",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-54",
              "title": "4 Access permissions are managed, incorporating the principles of least privilege and separation of duties",
              "category": {
                "id": "wct-id-367",
                "name": "7 Identity Management, Authentication and Access Control (PR.AC)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-4318",
              "title": "1.y Teleworking",
              "category": {
                "id": "wct-id-893",
                "name": "1 Access Control, Network and Teleworking",
                "framework": {
                  "id": "wf-id-16",
                  "name": "HITRUST CSF v9.5.0"
                }
              }
            },
            {
              "id": "wsct-id-3734",
              "title": "CC6.1-10 Restricts Access to Information Assets",
              "category": {
                "id": "wct-id-835",
                "name": "CC6 Logical and Physical Access Controls",
                "framework": {
                  "id": "wf-id-5",
                  "name": "SOC 2"
                }
              }
            },
            {
              "id": "wsct-id-3733",
              "title": "CC6.1-9 Restricts  Logical Access",
              "category": {
                "id": "wct-id-835",
                "name": "CC6 Logical and Physical Access Controls",
                "framework": {
                  "id": "wf-id-5",
                  "name": "SOC 2"
                }
              }
            },
            {
              "id": "wsct-id-5209",
              "title": "Data Security",
              "category": {
                "id": "wct-id-422",
                "name": "8 Data Security",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz"
                }
              }
            }
          ]
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "eyJmaWVsZHMiOlt7IkZpZWxkIjoiQW5hbHl6ZWRBdCIsIlZhbHVlIjoiMjAyMy0wNy0xOVQxMjoxMjoxMi42MTMwMDhaIn1dfQ=="
      }
    }
  }
}
````

:::success

Done! You have pulled Cloud Configuration Findings using some of the available filters.

:::

### Pull Cloud Configuration Findings incrementally

To monitor and track new or resolved Cloud Configuration Findings, use the `updatedAt` filter to pull daily updates incrementally. This enables you to identify changes in the status of findings, such as transitions from `OPEN` to `RESOLVED`, and surface findings that have been updated within the last 24 hours.

The following example query:

- Retrieves Cloud Configuration Findings whose status is either open or resolved that were updated within the last 24 hours.
- Captures updates to the resource object (relevant to the finding) or to the finding itself (including severity changes, ignored status changes, resource deletion, or compliance framework updates).
- Pulls both `PASSED` or `FAILED` findings as long as they were updated during the time specified.

You can further refine your query based on the [available fields](dev:configuration-finding#fields) and [variables](dev:configuration-finding#variables).

```json Example request
{
  "first": 5,
  "filterBy": {
    "updatedAt": {
      "after": "2025-04-19T21:00:00.000Z"
    },
    "status": ["OPEN", "RESOLVED"]
  }
}
```

A successful request returns the specified number of Cloud Configuration Findings according to the requested fields:

````json Example response
{
  "data": {
    "configurationFindings": {
      "nodes": [
        {
          "id": "319e2ce5-1ae9-53fa-91a0-3ffa73161d79",
          "targetExternalId": "arn:aws:rds:us-east-1:998231069301:snapshot:rds:database-1-2024-04-30-03-25",
          "targetObjectProviderUniqueId": "arn:aws:rds:us-east-1:998231069301:snapshot:rds:database-1-2024-04-30-03-25",
          "firstSeenAt": "2024-04-30T04:01:33.145593Z",
          "severity": "MEDIUM",
          "result": "PASS",
          "status": "RESOLVED",
          "remediation": null,
          "resource": {
            "id": "b8be3027-ce01-55fe-8c8d-9af100abe1b2",
            "providerId": "arn:aws:rds:us-east-1:998231069301:snapshot:rds:database-1-2024-04-30-03-25",
            "name": "rds:database-1-2024-04-30-03-25",
            "nativeType": "rds#snapshot",
            "type": "SNAPSHOT",
            "region": "us-east-1",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": []
          },
          "rule": {
            "id": "288042af-3f9b-4b55-b03b-2bc9b5513747",
            "graphId": "c859306f-ef87-5328-81af-5fc093a36877",
            "name": "RDS Instance Snapshot should be encrypted",
            "description": "This rule checks if the RDS Database Instance Snapshot is not encrypted at rest.  \nThis rule fails if `Encrypted` is set to `false` and `Status` is `available`.  \nRDS database instance snapshots are backups for RDS instances and can be used to restore the instance.  \nIt is recommended to enable encryption at rest for the snapshot in order to protect the data they contain, especially if it stores sensitive data.\n>**Note**  \n>See Cloud Configuration Rule `RDS-004` to see if the DB instance is encrypted. Rule `Snapshot-001` checks if the DB Cluster Snapshot is encrypted.",
            "remediationInstructions": "Perform the following command to encrypt the RDS Cluster Instance via AWS CLI:\n```\naws rds copy-db-snapshot \\\n    --source-db-snapshot-identifier {{dbSnapshotId}} \\\n    --target-db-snapshot-identifier {{dbSnapshotId}}-encrypted \\\n    --region {{region}} \\\n    --kms-key-id <value>\n```\nTo encrypt the snapshot with an AWS-managed key use the alias `aws/rds`. For a customer-managed key insert the key ARN or key ID in the `--kms-key-id` parameter.\n\n\nOnce the new and encrypted snapshot is available, it is safe to delete the source snapshot.  \n\nUse the following to delete the unencrypted snapshot:\n```\naws rds delete-db-snapshot \\\n    --db-snapshot-identifier {{dbSnapshotId}} \\\n    --region {{region}}\n```",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-14856",
              "title": "IDM-07 Access to cloud customer data",
              "category": {
                "id": "wct-id-2305",
                "name": "5.7 Identity and Access Management (IDM)",
                "framework": {
                  "id": "wf-id-111",
                  "name": "C5 - Cloud Computing Compliance Criteria Catalogue"
                }
              }
            },
            {
              "id": "wsct-id-14883",
              "title": "OPS-14 Logging and Monitoring - Storage of the Logging Data",
              "category": {
                "id": "wct-id-2304",
                "name": "5.6 Operations (OPS)",
                "framework": {
                  "id": "wf-id-111",
                  "name": "C5 - Cloud Computing Compliance Criteria Catalogue"
                }
              }
            },
            {
              "id": "wsct-id-11328",
              "title": "52c appropriate encryption, cleansing and auditing of devices;",
              "category": {
                "id": "wct-id-1928",
                "name": "20 Implementation of controls - Data leakage",
                "framework": {
                  "id": "wf-id-90",
                  "name": "APRA CPG 234"
                }
              }
            },
            {
              "id": "wsct-id-12421",
              "title": "AC-4(4) Information Flow Enforcement | Flow Control of Encrypted Information",
              "category": {
                "id": "wct-id-678",
                "name": "AC Access Control",
                "framework": {
                  "id": "wf-id-4",
                  "name": "NIST SP 800-53 Revision 5"
                }
              }
            },
            {
              "id": "wsct-id-14623",
              "title": "06.d Data Protection and Privacy of Covered Information",
              "category": {
                "id": "wct-id-2255",
                "name": "6.01 Compliance with Legal Requirements - Compliance",
                "framework": {
                  "id": "wf-id-109",
                  "name": "HITRUST CSF v11.2"
                }
              }
            },
            {
              "id": "wsct-id-14832",
              "title": "CRY-03 Encryption of sensitive data for storage",
              "category": {
                "id": "wct-id-2306",
                "name": "5.8 Cryptography and Key Management (CRY)",
                "framework": {
                  "id": "wf-id-111",
                  "name": "C5 - Cloud Computing Compliance Criteria Catalogue"
                }
              }
            },
            {
              "id": "wsct-id-2441",
              "title": "SC-28 Protection of Information at Rest",
              "category": {
                "id": "wct-id-695",
                "name": "SC System And Communications Protection",
                "framework": {
                  "id": "wf-id-4",
                  "name": "NIST SP 800-53 Revision 5"
                }
              }
            },
            {
              "id": "wsct-id-5209",
              "title": "Data Security",
              "category": {
                "id": "wct-id-2132",
                "name": "Data Security",
                "framework": {
                  "id": "wf-id-105",
                  "name": "Wiz (Legacy)"
                }
              }
            },
            {
              "id": "wsct-id-6560",
              "title": "Insufficiently encrypted data",
              "category": {
                "id": "wct-id-422",
                "name": "Data Security",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz for Risk Assessment"
                }
              }
            },
            {
              "id": "wsct-id-14374",
              "title": "3.5 Enable Encryption at Rest - Level 1 (Manual)",
              "category": {
                "id": "wct-id-2207",
                "name": "3 Amazon RDS",
                "framework": {
                  "id": "wf-id-107",
                  "name": "CIS AWS Database Services Benchmark v1.0.0"
                }
              }
            },
            {
              "id": "wsct-id-7741",
              "title": "RDS.4 RDS cluster snapshots and database snapshots should be encrypted at rest",
              "category": {
                "id": "wct-id-1244",
                "name": "28 Relational Database Service (RDS)",
                "framework": {
                  "id": "wf-id-50",
                  "name": "AWS Foundational Security Best Practices controls"
                }
              }
            },
            {
              "id": "wsct-id-12419",
              "title": "AC-4(2) Information Flow Enforcement | Processing Domains",
              "category": {
                "id": "wct-id-678",
                "name": "AC Access Control",
                "framework": {
                  "id": "wf-id-4",
                  "name": "NIST SP 800-53 Revision 5"
                }
              }
            }
          ],
          "ignoreRules": null
        },
        {
          "id": "bb0084ca-aacf-5d90-bf67-523a84d679d5",
          "targetExternalId": "i-0b2c436cb6e8cb846",
          "targetObjectProviderUniqueId": "arn:aws:ec2:us-east-2:998231069301:instance/i-0b2c436cb6e8cb846",
          "firstSeenAt": "2024-04-30T04:01:29.78729Z",
          "severity": "NONE",
          "result": "FAIL",
          "status": "OPEN",
          "remediation": "To monitor an instance system reboot scheduled event for the EC2 instance, follow [this link](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instances-status-check_sched.html).\n",
          "resource": {
            "id": "36c7b515-a9fc-5f08-b2dd-26b1aaf6fa54",
            "providerId": "arn:aws:ec2:us-east-2:998231069301:instance/i-0b2c436cb6e8cb846",
            "name": "Demo events findings",
            "nativeType": "virtualMachine",
            "type": "VIRTUAL_MACHINE",
            "region": "us-east-2",
            "subscription": {
              "id": "94e76baa-85fd-5928-b829-1669a2ca9660",
              "name": "wiz-integrations",
              "externalId": "998231069301",
              "cloudProvider": "AWS"
            },
            "projects": [
              {
                "id": "83b76efe-a7b6-5762-8a53-8e8f59e68bd8",
                "name": "Project 2",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "af52828c-4eb1-5c4e-847c-ebc3a5ead531",
                "name": "project 4",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              },
              {
                "id": "d6ac50bb-aec0-52fc-80ab-bacd7b02f178",
                "name": "Project1",
                "riskProfile": {
                  "businessImpact": "MBI"
                }
              }
            ],
            "tags": [
              {
                "key": "Name",
                "value": "Demo events findings"
              }
            ]
          },
          "rule": {
            "id": "d4926f50-d41c-455e-b3c5-465b3b3ae5fa",
            "graphId": "cbd7519c-c7b4-5619-b2b1-c7fc25fff556",
            "name": "EC2 instance with an upcoming system reboot scheduled event",
            "description": "This rule checks whether there is a system reboot scheduled event for the EC2 instance.  \nThis rule fails if there is at least one `Events` element whose `Code` field is set to `system-reboot`.  \nThis event indicates that at the scheduled time, the EC2 instance host is rebooted. Be aware of system reboot scheduled events to avoid unexpected data loss and downtime.\n>**Note**  \n>This rule does not indicate any misconfiguration and is informational only.",
            "remediationInstructions": "To monitor an instance system reboot scheduled event for the EC2 instance, follow [this link](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instances-status-check_sched.html).\n",
            "functionAsControl": false
          },
          "securitySubCategories": [
            {
              "id": "wsct-id-6165",
              "title": "CEK-01 Encryption and Key Management Policy and Procedures - Establish, document, approve, communicate, apply, evaluate and maintain\npolicies and procedures for Cryptography, Encryption and Key Management. Review\nand update the policies and procedures at least annually.",
              "category": {
                "id": "wct-id-1062",
                "name": "5 - CEK Cryptography, Encryption & Key Management",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-76",
              "title": "9 Response plans (Incident Response and Business Continuity) and recovery plans (Incident Recovery and Disaster Recovery) are in place and managed",
              "category": {
                "id": "wct-id-370",
                "name": "10 Information Protection Processes and Procedures (PR.IP)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-6164",
              "title": "CCC-09 Change Restoration - Define and implement a process to proactively roll back changes to\na previous known good state in case of errors or security concerns.",
              "category": {
                "id": "wct-id-1061",
                "name": "4 - CCC Change Control and Configuration Management",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-6322",
              "title": "UEM-08 Storage Encryption - Protect information from unauthorized disclosure on managed endpoint\ndevices with storage encryption.",
              "category": {
                "id": "wct-id-1074",
                "name": "17 - UEM Universal Endpoint Management",
                "framework": {
                  "id": "wf-id-14",
                  "name": "CSA CCM v4.0.5"
                }
              }
            },
            {
              "id": "wsct-id-5540",
              "title": "Operationalization",
              "category": {
                "id": "wct-id-2136",
                "name": "Operationalization",
                "framework": {
                  "id": "wf-id-105",
                  "name": "Wiz (Legacy)"
                }
              }
            },
            {
              "id": "wsct-id-689",
              "title": "5 Mechanisms (e.g., failsafe, load balancing, hot swap) are implemented to achieve resilience requirements in normal and adverse situations",
              "category": {
                "id": "wct-id-372",
                "name": "12 Protective Technology (PR.PT)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-37",
              "title": "5 Resilience requirements to support delivery of critical services are established",
              "category": {
                "id": "wct-id-363",
                "name": "2 Business Environment (ID.BE)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-6836",
              "title": "CM-7 LEAST FUNCTIONALITY",
              "category": {
                "id": "wct-id-1181",
                "name": "CM CONFIGURATION MANAGEMENT",
                "framework": {
                  "id": "wf-id-48",
                  "name": "NIST SP 800-53 Revision 4"
                }
              }
            },
            {
              "id": "wsct-id-71",
              "title": "4 Backups of information are conducted, maintained, and tested periodically",
              "category": {
                "id": "wct-id-370",
                "name": "10 Information Protection Processes and Procedures (PR.IP)",
                "framework": {
                  "id": "wf-id-13",
                  "name": "NIST CSF v1.1"
                }
              }
            },
            {
              "id": "wsct-id-635",
              "title": "A.12.3.1 Information backup",
              "category": {
                "id": "wct-id-589",
                "name": "A.12 Operations security",
                "framework": {
                  "id": "wf-id-3",
                  "name": "ISO/IEC 27001"
                }
              }
            },
            {
              "id": "wsct-id-10421",
              "title": "Informational configuration",
              "category": {
                "id": "wct-id-940",
                "name": "Operationalization",
                "framework": {
                  "id": "wf-id-1",
                  "name": "Wiz for Risk Assessment"
                }
              }
            }
          ],
          "ignoreRules": null
        }
      ],
      "pageInfo": {
        "hasNextPage": false,
        "endCursor": "eyJmaWVsZHMiOlt7IkZpZWxkIjoiQW5hbHl6ZWRBdCIsIlZhbHVlIjoiMjAyNC0wNC0zMFQwNDowMToyNS43NTM4ODRaIn0seyJGaWVsZCI6IklkIiwiVmFsdWUiOiJiYjAwODRjYS1hYWNmLTVkOTAtYmY2Ny01MjNhODRkNjc5ZDUifV19"
      }
    }
  }
}
````

<br />

:::success

Done! You have pulled Cloud Configuration Findings incrementally.

:::

%WIZARD_END%

## Next steps

- [See Pull Cloud Configuration Findings API reference](dev:configuration-finding)
- [See certification process](dev:certification-process)
