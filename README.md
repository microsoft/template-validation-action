# microsoft/template-validation-action

The Microsoft Template Validation Action is a GitHub action used to validate whether a GitHub repository meets the requirements of the [Definition of Done (DoD)](https://github.com/Azure-Samples/azd-template-artifacts/blob/main/docs/development-guidelines/definition-of-done.md#definition-of-done-dod) for AI-Gallery templates.

## Usage

Refer to the [azure.yaml](https://github.com/microsoft/template-validation-action/blob/main/action.yml)

### Step-by-Step Guide

1. Clone your repository locally:

    ```sh
    git clone YOUR-REPOSITORY-URL 
    ```

2. Install [AZD](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=winget-windows%2Cbrew-mac%2Cscript-linux&pivots=os-windows)

3. In the local repository folder, run:

    ```
    azd pipeline config
    ```

4. Add the `microsoft/template-validation-action` action to any workflow YAML file under the `.github/workflows` folder. Below is a sample YAML configuration:


    ```yaml
    name: Template Validation Sample Workflow
    on: 
      workflow_dispatch:

    permissions:
      contents: read
      id-token: write
      pull-requests: write

    jobs:
      template_validation_job:
        runs-on: ubuntu-latest
        name: template validation
        steps:
          - uses: actions/checkout@v4

          - uses: microsoft/template-validation-action@v0.1
            env:
              AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
              AZURE_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
              AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
              AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
              AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

          - name: print result
            run: cat ${{ steps.validation.outputs.resultFile }}
    ```

### Other examples

#### Run in Subfolder

Suppose there is a folder at root-level, called `ai-template`, where the `azure.yml` configuration is found:

```yaml
  - uses: microsoft/template-validation-action@v0.1
    with:
      workingDirectory: ./ai-template
    env:
      AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
      AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
      AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### Customized Validation Rules

By default, the action validates all paths, unless specific paths are configured. You can find the reference input name in the [#Inputs] table below. 

```yaml
  - uses: microsoft/template-validation-action@v0.1
    with:
      validatePaths: "README.md, LICENSE, ISSUE_TEMPLATE"
      topics: "azure, chatgpt, javascript"
      validateAzd: false
      securityAction: "PSRule"
    env:
      README_H2_TAG: "Getting Started, Guidance"
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### Validate Azd in GitHub Runner Environment
```yaml
  # Install any dependencies for the template. For example, java
  - uses: actions/setup-java@v2
    with:
      distribution: 'temurin'
      java-version: '17'
      cache: 'maven'

  - uses: microsoft/template-validation-action@v0.1
    with:
      validateAzd: true
      useDevContainer: false
    env:
      AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
      AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
      AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Name                      | Required | Description                       |
| ------------------------- | -------- | ----------------------------------|
| workingDirectory         | false    | The directory to run the validation in. Defaults to `.` (the root of the repository). Use this if your template is in a subdirectory. |
| validatePaths             | false    | A comma-separated list of static files or folder path to check for existence. Defaults to `README.md, LICENSE, SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, ISSUE_TEMPLATE.md, azure-dev.yaml, azure.yaml, infra, .devcontainer`. Leave empty to skip this check. |
| topics                    | false    | A comma-separated list of topics to check for in the repository. Defaults to `azd-template, ai-azd-template`. Leave empty to skip this check. |
| validateAzd               | false    | Whether to validate the deployment functionality with Azure Developer CLI (azd). Defaults to `true`. Set to `false` to skip azd validation. |
| useDevContainer           | false    | Whether to use a development container for validation. Defaults to `true`. |
| securityAction            | false    | Specify the security action to use. Defaults to ``. Available values: `PSRule` for microsoft/PSRule action. Leave empty to skip this check. |

## Outputs

| Name         | Description                                             |
| ------------ | ------------------------------------------------------- |
| resultFile   | Path to the file containing the validation results.     |

## Action Environment Variables

| Environment Variable Name   | Description                                                             |
| --------------------------- | ----------------------------------------------------------------------- |
| AZURE_CLIENT_ID             | Azure Client ID for authentication. Required for azd validation.        |
| AZURE_TENANT_ID             | Azure Tenant ID for authentication. Required for azd validation.        |
| AZURE_SUBSCRIPTION_ID       | Azure Subscription ID for authentication. Required for azd validation.  |
| AZURE_ENV_NAME              | Azure environment name. Required for azd validation.                    |
| AZURE_LOCATION              | Azure location for resources. Required for azd validation.              |
| GITHUB_TOKEN                | GitHub token for authentication. Required for GitHub topics validation. |
| README_H2_TAG               | Expected H2 tag(s) in the README file for validation.                   |

## Built-in Rules

* When a YAML filename is assigned to validatePaths, the .yml extension is also acceptable. 
* When ISSUE_TEMPLATE.md is not explicitly assigned to validatePaths, an ISSUE_TEMPLATE folder is also acceptable.
