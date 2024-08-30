from validator.validator_base import *
from constants import *
import os
import logging


class FileValidator(ValidatorBase):
    def __init__(self, validatorCatalog, fileName, extensionList, rootFolder, folderList = [""], h2Tags = None, caseSensitive = False, errorAsWarning = False, isFolderAllowed = False):
        super().__init__(f"{fileName}FileValidator", validatorCatalog, errorAsWarning)
        self.fileName = fileName
        self.extensionList = extensionList
        self.rootFolder = rootFolder
        self.folderList = folderList
        self.caseSensitive = caseSensitive
        self.h2Tags = h2Tags
        self.isFolderAllowed = isFolderAllowed
        self.errorAsWarning = errorAsWarning

    def validate(self):
        logging.debug(f"{self.name}: Checking for file {self.fileName} with {self.extensionList} "
                      f"under {self.rootFolder} in {self.folderList} with case sensitive {self.caseSensitive}..")
        self.result = False
        messages = []
        potential_name = self.fileName if self.extensionList[0] == "" else self.fileName + "." + self.extensionList[0]

        for root, dirs, files in os.walk(self.rootFolder):
            # print('{}; {}; {}'.format(root, dirs, files))
            for folder in self.folderList:
                candidateFolder = self.rootFolder if folder == "" else os.path.join(self.rootFolder, folder)
                if ((self.caseSensitive == False and candidateFolder.lower() == root.lower()) or (self.caseSensitive == True and root == candidateFolder)):
                    for extension in self.extensionList:
                        candidateFile = self.fileName if extension == "" else self.fileName + "." + extension
                        for file in files:
                            if ((self.caseSensitive == False and file.lower() == candidateFile.lower()) or (self.caseSensitive == True and file == candidateFile)):
                                self.result = True
                                logging.debug(f"- {file} is found in {root}.")
                                subMessages = []
                                if self.h2Tags is not None:
                                    with open(os.path.join(root, file), 'r') as fileContent:
                                        content = fileContent.read()
                                        for tag in self.h2Tags:
                                            if (self.caseSensitive == False and tag.lower() not in content.lower()) or (self.caseSensitive == True and tag not in content) :
                                                self.result = False
                                                subMessages.append(ItemResultFormat.SUBITEM.format(sign=Signs.WARNING if self.errorAsWarning else Signs.BLOCK, message=f"Error: {tag} is missing in {file}."))
                                    fileContent.close()
                                if self.result:
                                    messages.append(ItemResultFormat.PASS.format(message=f"{potential_name} File"))
                                else:
                                    messages.append(ItemResultFormat.FAIL.format(message=f"{potential_name} File",
                                                                                 detail_messages=line_delimiter.join(subMessages)))
                                self.message = line_delimiter.join(messages)
                                return self.result, self.message
                    if (self.isFolderAllowed == True and self.fileName in dirs):
                        self.result = True
                        messages.append(ItemResultFormat.PASS.format(message=f"{self.fileName} Folder"))
                        self.message = line_delimiter.join(messages)
                        return self.result, self.message

        errorMessage = f"{potential_name} File or {self.fileName} Folder" if self.isFolderAllowed else f"{potential_name} File"
        detailMessage = f"Error: {potential_name} file or {self.fileName} folder is missing." if self.isFolderAllowed else f"Error: {potential_name} file is missing."
        messages.append(ItemResultFormat.FAIL.format(message=errorMessage,
                                                     detail_messages=ItemResultFormat.SUBITEM.format(sign=Signs.WARNING if self.errorAsWarning else Signs.BLOCK, message=detailMessage)))

        self.message = line_delimiter.join(messages)
        return self.result, self.message
