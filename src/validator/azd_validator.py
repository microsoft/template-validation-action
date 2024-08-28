import os
import subprocess
import logging
from validator.validator_base import ValidatorBase
from constants import *
from utils import indent

class AzdValidator(ValidatorBase):
    def __init__(self, validatorCatalog, folderPath, check_azd_up=True, check_azd_down=True, errorAsWarning=False):
        super().__init__(f"AzdValidator", validatorCatalog, errorAsWarning)
        self.folderPath = folderPath
        self.check_azd_up = check_azd_up
        self.check_azd_down = check_azd_down
    
    def validate(self):
        self.result = True
        self.messages = []
        if self.check_azd_up:
            result, message = self.validate_up()
            self.result = self.result and result
            self.messages.append(message)
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
            return False, ItemResultFormat.FAIL.format(message=message, detail_messages=ItemResultFormat.DETAILS.format(message=indent(e.stdout)))

from validator.azd_validator import AzdValidator

def internal_validator(repo_path, check_azd_up, check_azd_down, topics, msdo_result_file):
    if not os.path.isdir(repo_path):
        raise Exception(f"Error: The path {repo_path} is not a valid directory.")
        return

    final_result = True
    final_message = []
    infra_yaml_paths = find_infra_yaml_path(repo_path)

    result, message = check_repository_management(repo_path, topics)
    final_result = final_result and result
    final_message.append(message)

    result, message = check_source_code_structure(repo_path, infra_yaml_paths[0])
    final_result = final_result and result
    final_message.append(message)

    if check_azd_up:
        for infra_yaml_path in infra_yaml_paths:
            azd_up_validator = AzdValidator("AzdUpCatalog", infra_yaml_path, "azd up --no-prompt")
            azd_up_validator.validate()
            final_result = final_result and azd_up_validator.result
            final_message.append(azd_up_validator.resultMessage)
            if check_azd_down:
                azd_down_validator = AzdValidator("AzdDownCatalog", infra_yaml_path, "azd down --force --purge --no-prompt")
                azd_down_validator.validate()
                final_result = final_result and azd_down_validator.result
                final_message.append(azd_down_validator.resultMessage)

    result, message = check_security_requirements(repo_path, msdo_result_file)
    final_result = final_result and result
    final_message.append(message)

    return final_result, line_delimiter.join(final_message)
