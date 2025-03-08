import subprocess
import logging
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, line_delimiter, Signs
from utils import indent
from severity import Severity
import re


class PlaywrightTestValidator(ValidatorBase):
    def __init__(
        self,
        validatorCatalog,
        folderPath,
        severity=Severity.LOW,
    ):
        super().__init__("PlaywrightTestValidator", validatorCatalog, severity)
        self.folderPath = folderPath

    def validate(self):
        self.result = True
        self.messages = []

        result, message = self.playwright_test()
        self.result = self.result and result
        self.messages.append(self.replace_words(self.escape_ansi(message), "|", "-"))

        self.resultMessage = line_delimiter.join(self.messages)
        return self.result, self.resultMessage

    def playwright_test(self):
        logging.debug(f"Running playwright test in {self.folderPath}")
        return self.runCommand(
            "npx playwright test", "--pass-with-no-tests --quiet --reporter list"
        )

    def escape_ansi(self, line):
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        logging.debug("Escaping ansi characters in line")
        return ansi_escape.sub("", line)

    def replace_words(self, line, word, replacement):
        logging.debug(f"removing {word} with {replacement} from line")
        return line.replace(word, replacement)

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
            )
            logging.info(f"{result.stdout}")
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
