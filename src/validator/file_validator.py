from validator.validator_base import ValidatorBase
from constants import line_delimiter, ItemResultFormat, Signs
from severity import Severity
import os
import logging


class FileValidator(ValidatorBase):
    def __init__(
        self,
        validatorCatalog,
        fileName,
        extensionList,
        rootFolder,
        candidatePaths=[""],
        h2Tags=None,
        caseSensitive=False,
        severity=Severity.HIGH,
        isFolderAllowed=False,
    ):
        super().__init__(f"{fileName}FileValidator", validatorCatalog, severity)
        self.fileName = fileName
        self.extensionList = extensionList
        self.rootFolder = rootFolder
        self.candidatePaths = candidatePaths
        self.caseSensitive = caseSensitive
        self.h2Tags = (
            [h2Tag.strip() for h2Tag in h2Tags] if h2Tags is not None else None
        )
        self.isFolderAllowed = isFolderAllowed
        self.severity = severity

    def validate(self):
        logging.debug(
            f"{self.name}: Checking for file {self.fileName} with {self.extensionList} "
            f"under {self.rootFolder} in {self.candidatePaths} with case sensitive {self.caseSensitive}.."
        )
        self.result = False
        messages = []
        potential_name = (
            self.fileName
            if self.extensionList[0] == ""
            else self.fileName + self.extensionList[0]
        )

        for root, dirs, files in os.walk(self.rootFolder):
            # print('{}; {}; {}'.format(root, dirs, files))
            for folder in self.candidatePaths:
                candidateFolder = (
                    self.rootFolder
                    if folder == "."
                    else root
                    if folder == "*"
                    else os.path.join(self.rootFolder, folder)
                )
                if (
                    self.caseSensitive is False
                    and candidateFolder.lower() == root.lower()
                ) or (self.caseSensitive is True and root == candidateFolder):
                    for extension in self.extensionList:
                        candidateFile = (
                            self.fileName
                            if extension == ""
                            else self.fileName + extension
                        )
                        for file in files:
                            if (
                                self.caseSensitive is False
                                and file.lower() == candidateFile.lower()
                            ) or (self.caseSensitive is True and file == candidateFile):
                                self.result = True
                                logging.debug(f"- {file} is found in '{root}'.")
                                subMessages = []
                                if self.h2Tags is not None:
                                    with open(
                                        os.path.join(root, file), "r"
                                    ) as fileContent:
                                        content = fileContent.read()
                                        for tag in self.h2Tags:
                                            if (
                                                self.caseSensitive is False
                                                and tag.lower() not in content.lower()
                                            ) or (
                                                self.caseSensitive is True
                                                and tag not in content
                                            ):
                                                self.result = False
                                                subMessages.append(
                                                    ItemResultFormat.SUBITEM.format(
                                                        sign=Signs.BLOCK
                                                        if Severity.isBlocker(
                                                            self.severity
                                                        )
                                                        else Signs.WARNING,
                                                        message=f"{tag} is missing in {file}.",
                                                    )
                                                )
                                    fileContent.close()
                                if self.result:
                                    messages.append(
                                        ItemResultFormat.PASS.format(
                                            message=f"{potential_name} File"
                                        )
                                    )
                                else:
                                    messages.append(
                                        ItemResultFormat.FAIL.format(
                                            sign=Signs.BLOCK
                                            if Severity.isBlocker(self.severity)
                                            else Signs.WARNING,
                                            message=f"{potential_name} File",
                                            detail_messages=line_delimiter.join(
                                                subMessages
                                            ),
                                        )
                                    )
                                self.resultMessage = line_delimiter.join(messages)
                                return self.result, self.resultMessage
                    if self.isFolderAllowed is True and self.fileName in dirs:
                        self.result = True
                        messages.append(
                            ItemResultFormat.PASS.format(
                                message=f"{self.fileName} Folder"
                            )
                        )
                        self.resultMessage = line_delimiter.join(messages)
                        return self.result, self.resultMessage

        errorMessage = (
            f"{potential_name} File or {self.fileName} Folder"
            if self.isFolderAllowed
            else f"{potential_name} File"
        )
        detailMessage = (
            f"{potential_name} file or {self.fileName} folder is missing."
            if self.isFolderAllowed
            else f"{potential_name} file is missing."
        )
        messages.append(
            ItemResultFormat.FAIL.format(
                sign=Signs.BLOCK
                if Severity.isBlocker(self.severity)
                else Signs.WARNING,
                message=errorMessage,
                detail_messages=ItemResultFormat.SUBITEM.format(
                    sign=Signs.BLOCK
                    if Severity.isBlocker(self.severity)
                    else Signs.WARNING,
                    message=detailMessage,
                ),
            )
        )

        self.resultMessage = line_delimiter.join(messages)
        return self.result, self.resultMessage
