# Wiz CLI Versioning
*Learn about Wiz CLI versioning structure, release cadence, Docker image tagging, and version support policy.*

Category: wiz-cli

This page covers Wiz CLI versioning, release cadence, support policy, and Product Updates.

The version number format of Wiz CLI is `<major.minor.patch-commithash>`, in general accordance with [SemVer](https://semver.org/) principles. For example, version "0.10.21-bb46070" indicates the Wiz CLI's major version number is "0", the minor version number is "10", the patch number is "21", and the commit hash is "bb46070".

## Major version

A major version of Wiz CLI includes significant new features and/or significant changes to existing features. Major releases may also contain breaking changes, such as feature deprecation.

- The release cadence for major Wiz CLI versions is not fixed.
- A new major version increments the major version number by one (e.g. "**1**.0123", "**2**.0.0")

## Minor version

A minor version of Wiz CLI includes bug fixes and/or selected new features.

- The release cadence for minor Wiz CLI versions is not fixed.
- A new minor version with new features increments the minor version numbering by one (e.g. "1.**1**.678", "1.**2**.2111").

## Patch version

A patch version of Wiz CLI includes bug fixes, stability improvements, and small additions. This design ensures nothing breaks in between patch versions.

- The release cadence for patch Wiz CLI versions is not fixed.
- A new patch version with new features increments the patch version numbering by one (e.g. "1.1.**100**", "1.1.**101**").

## Docker Wiz CLI image tags

To identify each Wiz CLI in the Wiz CLI repository, the image is assigned a tag that is identical to the Wiz CLI version number.

```text
wiziocli.azurecr.io/wizcli:0.17.8-bb54998
```

:::success

The `latest` tag points to the latest released version of Wiz CLI.

:::

## Support policy

Wiz provides support for the previous major version of Wiz CLI for up to three months following the release of the current major version. For example, if Wiz CLI v1.0 was released in June 2023 and Wiz CLI v2.0 was released in May 2024, then v1.0 would be supported until August 2024.

:::info

All supported Wiz CLI versions are available in the Wiz CLI release table and the Wiz CLI image repository.

:::
