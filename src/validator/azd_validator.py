import os
import subprocess
import logging
import re
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
    def __init__(self, validatorCatalog, folderPath, check_azd_up=True, check_azd_down=True, errorAsWarning=False):
        super().__init__(f"AzdValidator", validatorCatalog, errorAsWarning)
        self.folderPath = folderPath
        self.check_azd_up = check_azd_up
        self.check_azd_down = check_azd_down
        self.resource_group = None

    @retry(3, retryable_error_messages)
    def validate(self):
        self.result = True
        self.messages = []
        if self.check_azd_up:
            result, message = self.validate_up()
            self.result = self.result and result
            self.messages.append(message)
            # self.messages.append(self.list_resources())
            self.list_resources()

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

    def extract_resource_group(self, stdout):
        match = re.search(r'\(✓\) Done: Resource group: ([\w-]+) \(\d+\.\d+s\)', stdout)
        if match:
            self.resource_group = match.group(1)
            logging.debug(f"Extracted resource group: {self.resource_group}")

    def list_resources(self):
        try:
            if not self.resource_group:
                get_rg_command = "azd env get-value AZURE_RESOURCE_GROUP"
                rgResult = subprocess.run(get_rg_command, shell=True, text=True, capture_output=True)
                if rgResult.returncode == 0:
                    self.resource_group = rgResult.stdout.strip()
            get_subs_command = "azd env get-value AZURE_SUBSCRIPTION_ID"
            subs = subprocess.run(get_subs_command, shell=True, text=True, capture_output=True).stdout.strip()

            resources, ai_deployments = list_resources(self.resource_group, subs)
            return ItemResultFormat.DETAILS.format(
                message=indent(
                    f"List of all resource types in the resource group {self.resource_group}:\n{line_delimiter.join(resources)}\n List of all AI deployments:\n{line_delimiter.join(ai_deployments)}"
                )
            )
        except Exception as e:
            logging.warning(f"Failed to list resources: {e}")
            pass
        return ""

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
            self.extract_resource_group(result.stdout)
            return True, ItemResultFormat.PASS.format(message=message)
        except subprocess.CalledProcessError as e:
            logging.debug(f"{e.stdout}")
            logging.debug(f"{e.stderr}")
            return False, ItemResultFormat.AZD_FAIL.format(message=message, detail_messages=ItemResultFormat.DETAILS.format(message=indent(e.stdout.replace("\\", "").replace("\"", "\\\""))))
