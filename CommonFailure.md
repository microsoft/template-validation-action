# Common Failure

## File Missing
The file missing error is fairly straightforward. For reference, please see our [Definition of Done](https://github.com/Azure-Samples/azd-template-artifacts/blob/main/docs/development-guidelines/definition-of-done.md) for the required files and structure.

## Azd UP Failure:

Before adding the validation action in your local repo, please ensure you’ve run:
```
azd pipeline config
``` 

### Error BCP332: The provided value (whose length will always be greater than or equal to 15) is too long to assign to a target for which the maximum allowable length is 10

- **Root Cause**: The `maxLength` property defined for a parameter in `main.bicep` is too small for the actual value.

- **Solution**: Increase the `maxLength` value to accommodate longer inputs.

### Principal XXX does not exist in the directory XXX. Check that you have the correct principal ID. If you are creating this principal and then immediately assigning a role, this error might be related to a replication delay. In this case, set the role assignment principalType property to a value, such as ServicePrincipal, User, or Group.  See https://aka.ms/docs-principaltype

- **Root Cause**: The RBAC assignment in `main.bicep` is missing the required `principalType` property. This can result in a replication delay or incorrect assignment.

- **Solution**: Add the `principalType` field, e.g. 'ServicePrincipal', 'User', or 'Group'.

- **Note**: Type 'User' cannot be used in GitHub workflows.
To support both local and CI/CD scenarios, consider adding a parameter to control the RBAC assignment logic. e.g.: Use [CREATE_ROLE_FOR_USER](https://github.com/Azure-Samples/azd-ai-starter/blob/c0c418b0e22ef0a5565e6b03073171f4a72dbb81/infra/main.bicep#L46)

### ERROR: error executing step command 'deploy --all': failed deploying service 'indexer': archive/tar: write too long

- **Root Cause**: This is a known issue affecting both the Azure Developer CLI (azd) and the devcontainers/ci GitHub action.

- **Solution**: 
  - https://github.com/Azure/azure-dev/issues/4803
  - https://github.com/devcontainers/ci/issues/366