import logging
from azure.identity import AzureDeveloperCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

def list_resources(resource_group, subscription_id):
    credential = AzureDeveloperCliCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    resources = resource_client.resources.list_by_resource_group(resource_group)

    # Output the list of all resource types
    resource_types = []
    ai_accounts = []
    for resource in resources:
        resource_types.append(resource.type)
        if resource.type == "Microsoft.CognitiveServices/accounts":
            ai_accounts.append(resource.name)
    logging.info(f"List of all resource types in the resource group {resource_group}:")
    for resource_type in resource_types:
        logging.info(resource_type)

    ai_deployments = []
    if ai_accounts:
        for ai_account in ai_accounts:
            cognitive_client = CognitiveServicesManagementClient(
                credential, subscription_id
            )
            deployments = cognitive_client.deployments.list(
                resource_group_name=resource_group, account_name=ai_account
            )

            logging.info(
                f"List of all deployments for the cognitive services account {ai_account}:"
            )
            for deployment in deployments:
                model_format = deployment.properties.model.format
                sku_name = deployment.sku.name
                model_name = deployment.properties.model.name
                model_version = deployment.properties.model.version
                ai_deployment = (
                    f"{model_format}.{sku_name}.{model_name}:{model_version}"
                )
                logging.info(ai_deployment)
                ai_deployments.append(ai_deployment)
    else:
        logging.debug("No Cognitive Services account found.")
    return resource_types, ai_deployments
