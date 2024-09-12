import os
import logging
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, Signs, line_delimiter


class FolderValidator(ValidatorBase):
    def __init__(
        self, validatorCatalog, folderName, candidatePaths, errorAsWarning=False
    ):
        super().__init__(
            f"{folderName}FolderValidator", validatorCatalog, errorAsWarning
        )
        self.folderName = folderName
        self.candidatePaths = candidatePaths

    def validate(self):
        logging.debug(f"Checking for {self.folderName} folder in candidate folders...")
        messages = []
        folder_found = False

        for candidate_folder in self.candidatePaths:
            folder_path = os.path.join(candidate_folder, self.folderName)
            if os.path.isdir(folder_path):
                messages.append(
                    ItemResultFormat.PASS.format(
                        message=f"{self.folderName} Folder"
                    )
                )
                folder_found = True
                break

        if not folder_found:
            messages.append(
                ItemResultFormat.FAIL.format(
                    message=f"{self.folderName} Folder",
                    detail_messages=ItemResultFormat.SUBITEM.format(
                        sign=Signs.BLOCK,
                        message=f"Error: {self.folderName} folder is missing.",
                    ),
                )
            )
            result = False
        else:
            result = True

        self.result = result
        self.resultMessage = line_delimiter.join(messages)
        return result, self.resultMessage
