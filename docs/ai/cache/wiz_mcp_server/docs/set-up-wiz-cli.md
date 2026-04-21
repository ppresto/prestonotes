# Setting Up Wiz CLI
*Set up Wiz CLI to detect IaC misconfigurations, vulnerabilities, and secrets early in the development lifecycle.*

Category: wiz-cli

:::danger

This guide is intended for WIN partners who want to use the Wiz CLI. If you're a Wiz customer, see the [relevant document](doc:set-up-wiz-cli) in the Guides section.

:::

Follow the steps below to set up the Wiz CLI.

## Before you begin

The prerequisites are:

- A Wiz service account with these scopes:
  - `create:security_scans`
  - `update:security_scans`
- Ensure [these URLs](#required-urls) are accessible from the environment where Wiz CLI will be running.
  - For `file-upload.<WIZ-DC>.app.wiz.io`, change `file-upload` to `cli-results`: `cli-results.<WIZ-DC>.app.wiz.io`
- A Linux, Mac, or Windows host (either local or in the cloud) on which to download Wiz CLI.
- Wiz CLI must be allowed to create a local directory in order to store authentication data.
- The clock of the machine on which the Wiz CLI will be installed must be properly synchronized; otherwise, you may experience "token used before issued" errors. Most systems use [NTP](http://www.ntp.org/) to achieve this, but your mileage may vary.

## Setup steps

%WIZARD_START_CLOSED%

### Get Wiz CLI

Choose whether to run Wiz CLI as a native binary on your host or as a Docker container.

| Option | Best for | 
| :----- | :------- |
| [A: Download binary](#option-a-download-wiz-cli-to-your-host) | Local development, persistent installs, and Windows/macOS environments. |
| [B: Pull Docker image](#option-b-pull-wiz-cli-as-a-docker-image) | CI/CD pipelines, ephemeral environments, and avoiding local dependencies. |

#### Option A: Download Wiz CLI to your host

<Tabs groupId="platform-selection">

    <TabItem value="Linux" label="Linux">

    %WIZARD_START_CLOSED%

    ### Download the Wiz CLI package

    :::success

    To future-proof your scripts, we recommend storing the URL as a variable.

    :::

  - Run this command:

    ```shell AMD64
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64
    ```

    ```shell ARM64
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-arm64
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-no-avx2
    ```

 - Alternatively, download the compressed package (not available for the FIPS release). This reduces download time, especially over slow 
connections:
    
    1. Run this command: 

    ```shell AMD64
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64.gz
    ```

    ```shell ARM64
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-arm64.gz
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-no-avx2.gz
    ```

    2. Uncompress it:

    ```shell 
    gunzip wizcli.gz
    ```

### (Optional) Verify the Wiz CLI signature

:::info

Wiz CLI's GPG public key can be fetched from `downloads.wiz.io` or from Ubuntu's key server with the key ID `CE4AE4BAD12EE02C` and fingerprint 
`61DF 4068 0AB1 A80E 5150 3B61 CE4A E4BA D12E E02C`

:::

1. Import the public key, as described above, from keyserver or from direct link:
    - Direct link:
    
```shell
curl -Lo public_key.asc https://downloads.wiz.io/wizcli/public_key.asc
gpg --import public_key.asc
```

    - Ubuntu's Keyserver:
    
```shell
gpg --keyserver keyserver.ubuntu.com --recv-keys CE4AE4BAD12EE02C
```

2. Download files to perform signature verification:
    
```shell AMD64
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-sha256.sig
```

```shell ARM64
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-arm64-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-arm64-sha256.sig
```

```shell AMD64 non-AVX2
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-no-avx2-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64-no-avx2-sha256.sig
```

3. Verify signature
```shell
gpg --verify /tmp/wizcli-sha256.sig /tmp/wizcli-sha256
```

4. Verify SHA256 (execute this from the same directory where Wiz CLI binary is located):
    
```shell
echo "$(cat /tmp/wizcli-sha256) wizcli" | sha256sum --check
```

### Provide Wiz CLI with executable permissions

Run the following command:

```shell
chmod +x wizcli
```

### Ensure Wiz CLI has the required permissions

Run the following command:

```shell
ls -l wizcli
```

%WIZARD_END% 

 </TabItem>

    <TabItem value="macOS" label="macOS">

    %WIZARD_START_CLOSED%

  ### Download the Wiz CLI package

:::success

To future-proof your scripts, we recommend storing the URL as a variable.

:::

  - Run this command:

    ```shell M1/M2/M3/ARM64
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-arm64
    ```

    ```shell AMD64
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-no-avx2
    ```

 - Alternatively:
    
    1. Run this command to download a compressed package:

    ```shell M1/M2/M3/ARM64
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-arm64.gz
    ```

    ```shell AMD64
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64.gz
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-no-avx2.gz
    ```

    2. Uncompress it:

    ```shell 
    gunzip wizcli.gz
    ```

### (Optional) Verify the Wiz CLI signature

:::info

Wiz CLI's GPG public key can be fetched from `downloads.wiz.io` or from Ubuntu's key server with the key ID `CE4AE4BAD12EE02C` and fingerprint 
`61DF 4068 0AB1 A80E 5150 3B61 CE4A E4BA D12E E02C`

:::

1. Import the public key, as described above, from keyserver or from direct link:
    - Direct link:
    
```shell
curl -Lo public_key.asc https://downloads.wiz.io/wizcli/public_key.asc
gpg --import public_key.asc
```
    - Ubuntu's Keyserver:
    
```shell
gpg --keyserver keyserver.ubuntu.com --recv-keys CE4AE4BAD12EE02C
```

2. Download files to perform signature verification:
    
```shell M1/M2/M3/ARM64
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-arm64-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-arm64-sha256.sig
```

```shell AMD64
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-sha256.sig
```

```shell AMD64 non-AVX2
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-no-avx2-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-darwin-amd64-no-avx2-sha256.sig
```

3. Verify signature
    
```shell
gpg --verify /tmp/wizcli-sha256.sig /tmp/wizcli-sha256
```

4. Verify SHA256 (execute this from the same directory where Wiz CLI binary is located):

```shell
echo "$(cat /tmp/wizcli-sha256) wizcli" | sha256sum --check
```

### Provide Wiz CLI with executable permissions

Run the following command:

```shell
chmod +x wizcli
```

### Ensure Wiz CLI has the required permissions

Run the following command:

```shell
ls -l wizcli
```

%WIZARD_END%

    </TabItem>

    <TabItem value="Windows" label="Windows">

      %WIZARD_START_CLOSED%

  ### Download the Wiz CLI package

:::success

To future-proof your scripts, we recommend storing the URL as a variable.

:::

  - You can use either command prompt or PowerShell. Choose one method:
    
    - Command prompt:

    ```shell AMD64
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64.exe
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64-no-avx2.exe
    ```

    - PowerShell:

    ```shell AMD64
    Invoke-WebRequest -Uri https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64.exe -OutFile wizcli.exe
    ```

    ```shell AMD64 non-AVX2
    Invoke-WebRequest -Uri https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64-no-avx2.exe -OutFile wizcli.exe
    ```

 - Alternatively:
    
    1. Use command prompt to download a compressed package:

    ```shell AMD64
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64.exe.gz
    ```

    ```shell AMD64 non-AVX2
    curl -Lo wizcli.gz https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64-no-avx2.exe.gz
    ```

    2. Uncompress it:

    ```shell 
    gunzip wizcli.gz
    ```

### (Optional) Verify the Wiz CLI signature

:::info

- You will need to install a GPG signature validation tool.
- Wiz CLI's GPG public key can be fetched from `downloads.wiz.io` or from Ubuntu's key server with the key ID `CE4AE4BAD12EE02C` and fingerprint 
`61DF 4068 0AB1 A80E 5150 3B61 CE4A E4BA D12E E02C`

:::

1. Import the public key, as described above, from keyserver or from direct link:
    - Direct link:
    
```shell
curl -Lo public_key.asc https://downloads.wiz.io/wizcli/public_key.asc
gpg --import public_key.asc
```
    - Ubuntu's Keyserver:
    
```shell
gpg --keyserver keyserver.ubuntu.com --recv-keys CE4AE4BAD12EE02C
```

2. Download files to perform signature verification:

```shell AMD64
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64.exe-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64.exe-sha256.sig
```

```shell AMD64 non-AVX2
curl -Lo /tmp/wizcli-sha256 https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64-no-avx2.exe-sha256
curl -Lo /tmp/wizcli-sha256.sig https://downloads.wiz.io/v1/wizcli/latest/wizcli-windows-amd64-no-avx2.exe-sha256.sig
```

3. Verify signature

```shell
gpg --verify /tmp/wizcli-sha256.sig /tmp/wizcli-sha256
```

4. Create a PowerShell script that will be used to validate that the signatures match (execute this from the same directory where the Wiz CLI 
binary is located):

```shell
New-Item validate_gpg.ps1
```

5. Open the file in your preferred editor:

```shell
Start-Process .\validate_gpg.ps1
```

6. Copy the following into the `validate_gpg.ps1` file and save:

```shell
# START SCRIPT validate_gpg.ps1
$wizcliExePath = ".\wizcli.exe" # Or the full path to where you downloaded wizcli.exe
$expectedHashFromFilePath = "$env:TEMP\wizcli-sha256" # Or full path to where you downloaded wizcli-sha256

If (-not (Test-Path $wizcliExePath)) {
    Write-Error "wizcli.exe not found at $wizcliExePath. Please provide the correct path."
    return
}
If (-not (Test-Path $expectedHashFromFilePath)) {
    Write-Error "SHA256 checksum file not found at $expectedH```ashFromFilePath. Please provide the correct path."
    return
}

$expectedHash = (Get-Content -Path $expectedHashFromFilePath -TotalCount 1).Trim()

$actualFileHash = (Get-FileHash -Path $wizcliExePath -Algorithm SHA256).Hash.ToLower()

# Step 4c: Compare the hashes
If ($actualFileHash -eq $expectedHash.ToLower()) {
    Write-Host "SHA256 Verification Successful: The hash of '$wizcliExePath' matches the expected hash." -ForegroundColor Green
} Else {
    Write-Host "SHA256 Verification FAILED!" -ForegroundColor Red
    Write-Host "Expected SHA256: $expectedHash"
    Write-Host "Actual SHA256  : $actualFileHash"
}
# END SCRIPT validate_gpg.ps1
```

7. Execute the script:

```shell
& .\validate_gpg.ps1
```

The expected output is:

```shell
`SHA256 Verification Successful: The hash of '.\wizcli.exe' matches the expected hash.`
````

### Ensure Wiz CLI has the required permissions

Run the following command:

```shell
ls -l wizcli
```

%WIZARD_END% 

    </TabItem>

</Tabs>

:::info[CPU terminology]

- AMD64—The 64-bit CPU architecture that is used in Intel and AMD processors. Also known as x86-64, x64, x86_64, and Intel 64.
- ARM64—The 64-bit ARM CPU architecture. Also known as AArch64.

:::

#### Option B: Pull Wiz CLI as a Docker image

Use this option if you prefer to run Wiz CLI in a containerized environment:

1. To run Wiz CLI as a Docker image, use the following commands, which pull the latest image and tag it with a uniform name (`wizcli:latest`, 
regardless of platform and architecture) that is used in follow-up commands:

```shell Linux (Multi-arch)
docker pull public-registry.wiz.io/wiz-app/wizcli:1
docker tag public-registry.wiz.io/wiz-app/wizcli:1 wizcli:latest
```

2. Verify that Wiz CLI is working by checking its version:

```shell
docker run \
    --rm -it \
    wizcli:latest \
    version
```

Wiz CLI does not currently support scanning Windows images when run as a Docker image on Windows. If this is a critical use case for you, please 
[let us know](doc:support).

### (Optional) Manual version check

To check the full version of the latest release, in the format: `cli: "<VERSION_NUMBER>-<VERSION_HASH>"` (e.g. `cli: "0.19.
2-8d5fc4c47832a0aa7d84533885c09034a855f8fe"`), run the following command:

```shell
curl -L https://downloads.wiz.io/v1/wizcli/latest/wizcli-version
```

If the exact version exists locally on disk, you can avoid downloading the `wizcli` binary again and use the `-z` or `--time-cond` flags in the 
`curl` command above. For example:

```shell Linux (AMD64)
curl -z wizcli -Lo wizcli https://downloads.wiz.io/v1/wizcli/latest/wizcli-linux-amd64
```

### (Optional) Configure a proxy server

If your organization uses proxy servers to limit and/or monitor Internet access, you may need to pass proxy details to the Wiz CLI.

<Expandable title="Linux, Mac, or Windows">

On the machine where the Wiz CLI is installed, create an environment variable using the following command, replacing `<proxy-Hostname>` with the 
domain name or IP address of your proxy server, and optionally `<proxy-Port>` with the server's port:

```text Pick your system 👉

```

```shell Linux or MacOS
export HTTPS_PROXY="http://<proxy-Hostname>:<proxy-Port>"
```

```shell Windows (CLI)
set HTTPS_PROXY=http://<proxy-Hostname>:<proxy-Port>
```

```shell Windows (PowerShell)
$env:HTTPS_PROXY="http://<proxy-Hostname>:<proxy-Port>"
```

Wiz CLI automatically uses these settings for all of its API calls.

</Expandable>

<Expandable title="Docker">

Because Docker commands do not automatically pass environment variables to the container, you must pass proxy details with every call, replacing 
`<proxy-Hostname>` with the domain name or IP address of your proxy server, and optionally `<proxy-Port>` with the server's port:

```shell
docker run \
    <other flags or values>
    -e HTTPS_PROXY="http://<proxy-Hostname>:<proxy-Port>" \
    wizcli:latest \
    <other flags or values>
```

</Expandable>

### (GovCloud and FedRAMP only) Configure the WIZ_ENV environment variable

If you access Wiz from `app.wiz.us` (Wiz for Gov, aka FedRAMP) or `gov.wiz.io` (GovCloud), you must configure the `WIZ_ENV` environment variable; 
otherwise, you will receive a "failed authenticating with credentials: bad credentials" error message when you try to [authenticate to the Wiz API]
(#authenticate-to-the-wiz-api):

```text Choose your OS 👉

```

```shell Linux/MacOS
# for app.wiz.us
export WIZ_ENV=fedramp

# for gov.wiz.io
export WIZ_ENV=gov
```

```shell Windows
# for app.wiz.us
set WIZ_ENV=fedramp

# for gov.wiz.io
set WIZ_ENV=gov
```

### Authenticate to the Wiz API

:::warning

- It is recommended to assign developers the [Developer role](https://app.wiz.io/settings/user-roles#%7E%28cols%7E%28%7E%28%7E%27c-name%7E%27fill%29%7E%28%7E%27c-scopes%7E97%29%29%7Efilters%7E%28search%7E%28contains%7E%27Dev%29%29%29), 
which provides the necessary minimum permissions.
- If you have more than one Wiz tenant, you first need to log in to the desired one via the portal.
- Command line arguments take precedence over environment variables.

:::

 You have two options to authenticate:

  - (Recommended) Set the following environment variables to the Wiz CLI Deployment credentials received through your integration:

  ```shell
  export WIZ_CLIENT_ID=<YOUR_CLIENT_ID>
  export WIZ_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
  ```

  When using this method, the authentication flags (i.e. `--client-id` and `--client-secret`) are not required.
  
  - Pass the Wiz CLI Deployment's credentials in the command itself using the authentication flags. For example:

  ```shell
  wizcli scan dir ./folder --client-id <YOUR_CLIENT_ID> --client-secret <YOUR_CLIENT_SECRET>
  ```

%WIZARD_END%

:::success

Congratulations! You can now use Wiz CLI. Continue reading for some optional and recommended steps.

:::

## Further steps

%WIZARD_START_CLOSED%

### (Recommended) Validate Docker image usage

Ensure Wiz CLI's Docker image scanning and tagging works properly. [Learn about Docker image scanning and tagging]
(doc:scan-and-tag-container-images-with-wiz-cli).

You can use the following sample, which uses a Fedora Linux container image:

```shell Sample commands
docker pull quay.io/fedora/fedora:41
wizcli scan container-image quay.io/fedora/fedora:41
wizcli tag quay.io/fedora/fedora:41 --digest=<IMAGE_DIGEST>
```

### (Optional) Configure the WIZ_DIR environment variable

The `WIZ_DIR` environment variable represents the path to the directory used for all Wiz CLI cache data, which includes the authentication token, 
cluster files, and data correlating scanned and tagged container images. If the provided path is non-writable, scan time may increase, and tagging 
images will fail.

The default value for this variable is `$HOME/.wiz`.

To define this variable in your environment, run one of the following commands:

```text Pick your system 👉

```

```shell Linux or MacOS
export WIZ_DIR="$HOME/.wiz"
```

```shell Windows
# command line
SET WIZ_DIR=%LocalAppData%\Wiz

# PowerShell
$env:WIZ_DIR="${env:LocalAppData}/Wiz"
```

```shell Docker
export WIZ_DIR="<PATH_TO_DIRECTORY>"
```

Furthermore, the examples below use the `$PWD` variable to represent the parent working directory. On Windows (PowerShell), this must be replaced 
by `${PWD}`. For instance:

```shell Docker image (Linux)
docker run \
    --rm -it \
    --mount type=bind,src=$WIZ_DIR,dst=/cli,readonly \
    --mount type=bind,src=$PWD,dst=/scan \
    wizcli:latest \
    scan dir /scan/demo-scenarios-tf
```

```shell Docker image (Windows)
docker run `
    --rm -it `
    --mount type=bind,src=${env:WIZ_DIR},dst=/cli,readonly `
    --mount type=bind,src=${PWD},dst=/scan `
    wizcli:latest `
    scan dir /scan/demo-scenarios-tf
```

### (Optional) Configure the TMPDIR environment variable

By default, Wiz CLI unpacks container images in `/tmp`. To use a different path, set the `TMPDIR` environment variable:

```shell Linux/MacOS
export TMPDIR=<choosen-dir>
```

```shell Windows
set TMPDIR=<choosen-dir>
```

%WIZARD_END%

## Required URLs

For WIN partner service accounts, replace `<WIZ-DC>` with `us17`.

| FQDN                                                                                                                                                  | Purpose                                                                                        |
| :---------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- |
| `agent.<WIZ-DC>.app.wiz.io`                                                                                                                           | Wiz CLI communication with your Wiz tenant                                                     |
| `api.<WIZ-DC>.app.wiz.io`                                                                                                                             | Wiz CLI communication with your Wiz tenant                                                     |
| `auth.app.wiz.io`                                                                                                                                     | Wiz CLI authentication with your Wiz tenant                                                    |
| `outpost-storage.<WIZ-DC>.app.wiz.io`                                                                                                                 | Retrieve Rego libraries and download URLs                                                      |
| `cli-results.<WIZ-DC>.app.wiz.io`                                                                                                                     | Wiz CLI scan results |
| `logs-ingestion.wiz.io`                                                                                                                               | Wiz CLI logging |

## Limits for Wiz Gov

- Full compatibility is guaranteed only for Linux and Docker. These versions provide FIPS-validated cryptography and use Boringcrypto with Golang.
- Compatibility is not guaranteed in macOS and Windows, although Wiz CLI may function. These versions do not include FIPS-validated cryptography.
- The Wiz for Gov backend always uses FIPS-validated cryptography for TLS communications. Therefore, the Wiz backend accepts only FIPS-approved algorithms during TLS negotiation, regardless of the client platform.
