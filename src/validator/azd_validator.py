import os
import subprocess
import logging
from validator.validator_base import ValidatorBase
from list_azd_resources import list_resources
from constants import ItemResultFormat, line_delimiter
from utils import indent, retry

# defines string array of retryable error messages
retryable_error_messages = [
    "Cannot connect to the Docker daemon",
    "spawn ETXTBSY"
]

class AzdValidator(ValidatorBase):
    def __init__(self, validatorCatalog, folderPath, check_azd_up=True, check_azd_down=True, list_resources=False, errorAsWarning=False):
        super().__init__(f"AzdValidator", validatorCatalog, errorAsWarning)
        self.folderPath = folderPath
        self.check_azd_up = check_azd_up
        self.check_azd_down = check_azd_down
        self.list_resources = list_resources

    @retry(3, retryable_error_messages)
    def validate(self):
        self.result = True
        self.messages = []
        if self.check_azd_up:
            result, message = self.validate_up()
            self.result = self.result and result
            self.messages.append(message)
            if self.list_resources:
                self.messages.append(self.list_resources())

        if self.check_azd_down:
            result, message = self.validate_down()
            self.result = self.result and result
            self.messages.append(message)
        self.resultMessage = line_delimiter.join(self.messages)
        return self.result, self.resultMessage
    
    def validate_up(self):
        logging.debug(f"Running azd up in {self.folderPath}")
        try:
            self.use_local_tf_backend()
        except Exception as e:
            logging.warning(f"Failed to update tf backend: {e}")

        return self.runCommand("azd up", "--no-prompt")

    def list_resources(self):
        get_rg_command = "azd env get-value AZURE_RESOURCE_GROUP"
        get_subs_command = "azd env get-value AZURE_SUBSCRIPTION_ID"
        rg = subprocess.run(get_rg_command, shell=True, text=True, capture_output=True).stdout.strip()
        subs = subprocess.run(get_subs_command, shell=True, text=True, capture_output=True).stdout.strip()

        resources, ai_deployments = list_resources(rg, subs)
        return ItemResultFormat.DETAILS.format(
            message=indent(
                f"List of all resource types in the resource group {rg}:\n{line_delimiter.join(resources)}\n List of all deployments for the cognitive services account {ai_account}:\n{line_delimiter.join(ai_deployments)}"
            )
        )

    def validate_down(self):
        logging.debug(f"Running azd down in {self.folderPath}")
        return self.runCommand("azd down", "--force --purge --no-prompt")

    def use_local_tf_backend(self):
        provider_file = os.path.join(self.folderPath, "infra", "provider.tf")
        if not os.path.exists(provider_file):
            return
        with open(provider_file, 'r') as file:
            content = file.read()
        modified_content = content.replace('backend "azurerm" {}', 'backend "local" {}')
        
        with open(provider_file, 'w') as file:
            file.write(modified_content)
        logging.debug(f"Replace azurerm backend with local backend in {provider_file}.")

    def runCommand(self, command, arguments):
        message = f"{command}" if self.folderPath == "." else f"{command} in {self.folderPath}"
        try:
            result = subprocess.run(
                " ".join([command, arguments]), cwd=self.folderPath, capture_output=True, text=True, check=True, shell=True)
            logging.debug(f"{result.stdout}")
            return True, ItemResultFormat.PASS.format(message=message)
        except subprocess.CalledProcessError as e:
            logging.debug(f"{e.stdout}")
            logging.debug(f"{e.stderr}")
            return False, ItemResultFormat.AZD_FAIL.format(message=message, detail_messages=ItemResultFormat.DETAILS.format(message=indent(e.stdout.replace("\\", ""))))
