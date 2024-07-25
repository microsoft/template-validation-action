# microsoft/template-validation-action
Microsoft Template Validation Action is a github action used to validate if a github repository meets the requirement of [Definition of done](https://github.com/Azure-Samples/azd-template-artifacts/blob/main/docs/development-guidelines/definition-of-done.md#definition-of-done-dod) of Ai-Gallery template.

## Usage
See [azure.yaml](https://github.com/microsoft/template-validation-action/blob/main/action.yml)

### Step by Step
1. Clone your repo to local
```
git clone YOUR-REPOSITORY-URL 
```
2. Install [AZD](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=winget-windows%2Cbrew-mac%2Cscript-linux&pivots=os-windows)
3. In the local repo folder, run:
```
azd pipeline config
```
4. In any workflow yml file under `.github/workflows` folder, add `microsoft/template-validation-action` action. The following is a sample yaml:
```
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
    env:
      AZURE_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
      AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
      AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - id: validation
        uses: microsoft/template-validation-action@v0.0.3
        with:
          repositoryURL: https://github.com/Azure-Samples/azd-ai-starter
          branch: main

      - name: print result
        run: cat ${{ steps.validation.outputs.resultFile }}

```

