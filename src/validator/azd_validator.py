import os
import subprocess
import logging
import re
from validator.validator_base import ValidatorBase
from list_azd_resources import list_resources
from constants import ItemResultFormat, line_delimiter, Signs
from utils import indent, retry
from validator.azd_command import AzdCommand
from severity import Severity

# defines string array of retryable error messages
retryable_error_messages = ["Cannot connect to the Docker daemon", "spawn ETXTBSY"]


class AzdValidator(ValidatorBase):
    def __init__(
        self,
        validatorCatalog,
        folderPath,
        command: AzdCommand,
        severity=Severity.HIGH,
    ):
        super().__init__("AzdValidator", validatorCatalog, severity)
        self.folderPath = folderPath
        self.command = command
        self.resource_group = None

    @retry(3, retryable_error_messages)
    def validate(self):
        self.result = True
        self.messages = []

        if self.command == AzdCommand.UP:
            result, message = self.validate_up()
            self.result = self.result and result
            self.messages.append(message)
            self.list_resources()

        elif self.command == AzdCommand.DOWN:
            result, message = self.validate_down()
            self.result = self.result and result
            self.messages.append(message)

        self.resultMessage = line_delimiter.join(self.messages)
        return self.result, self.resultMessage

    def refresh_az_login(self):
        """Refresh az CLI login using azd's credentials to ensure az is authenticated
        in the same process context before running azd up."""
        try:
            client_id = os.environ.get("AZURE_CLIENT_ID", "")
            tenant_id = os.environ.get("AZURE_TENANT_ID", "")
            if not client_id or not tenant_id:
                return
            # Use azd auth token to get a fresh access token, then use it for az login
            token_result = subprocess.run(
                "azd auth token --output json",
                shell=True, text=True, capture_output=True,
                stdin=subprocess.DEVNULL,
            )
            if token_result.returncode != 0:
                logging.warning("Failed to get azd auth token for az login refresh")
                return
            import json
            token_data = json.loads(token_result.stdout)
            access_token = token_data.get("token", "")
            if not access_token:
                return
            az_result = subprocess.run(
                f'az login --service-principal -u "{client_id}" --tenant "{tenant_id}" --allow-no-subscriptions -t "{access_token}"',
                shell=True, text=True, capture_output=True,
                stdin=subprocess.DEVNULL,
            )
            if az_result.returncode == 0:
                logging.info("Successfully refreshed az CLI login")
            else:
                logging.warning(f"az login refresh failed: {az_result.stderr}")
        except Exception as e:
            logging.warning(f"Failed to refresh az login: {e}")

    def validate_up(self):
        logging.debug(f"Running azd up in {self.folderPath}")
        try:
            self.use_local_tf_backend()
        except Exception as e:
            logging.warning(f"Failed to update tf backend: {e}")

        self.refresh_az_login()
        return self.runCommand("azd up", "--no-prompt")

    def extract_resource_group(self, stdout):
        match = re.search(r"\(✓\) Done: Resource group: ([\w-]+) \(\d+\.\d+s\)", stdout)
        if match:
            self.resource_group = match.group(1)
            logging.debug(f"Extracted resource group: {self.resource_group}")

    def list_resources(self):
        try:
            if not self.resource_group:
                get_rg_command = "azd env get-value AZURE_RESOURCE_GROUP"
                rgResult = subprocess.run(
                    get_rg_command, shell=True, text=True, capture_output=True
                )
                if rgResult.returncode == 0:
                    self.resource_group = rgResult.stdout.strip()
            get_subs_command = "azd env get-value AZURE_SUBSCRIPTION_ID"
            subs = subprocess.run(
                get_subs_command, shell=True, text=True, capture_output=True
            ).stdout.strip()

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
        with open(provider_file, "r") as file:
            content = file.read()
        modified_content = content.replace('backend "azurerm" {}', 'backend "local" {}')

        with open(provider_file, "w") as file:
            file.write(modified_content)
        logging.info(f"Replace azurerm backend with local backend in {provider_file}.")

    def runCommand(self, command, arguments):
        message = (
            f"{command}"
            if self.folderPath == "."
            else f"{command} in {self.folderPath}"
        )
        try:
            result = subprocess.run(
                " ".join([command, arguments]),
                cwd=self.folderPath,
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                stdin=subprocess.DEVNULL,
            )
            logging.info(f"{result.stdout}")
            self.extract_resource_group(result.stdout)
            return True, ItemResultFormat.PASS.format(message=message)
        except subprocess.CalledProcessError as e:
            logging.info(f"{e.stdout}")
            logging.warning(f"{e.stderr}")
            return False, ItemResultFormat.AZD_FAIL.format(
                sign=Signs.BLOCK
                if Severity.isBlocker(self.severity)
                else Signs.WARNING,
                message=message,
                detail_messages=ItemResultFormat.DETAILS.format(
                    message=indent(e.stdout.replace("\\", ""))
                ),
            )
