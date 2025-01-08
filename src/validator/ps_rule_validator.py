import json
import logging
from validator.validator_base import ValidatorBase
from utils import indent
from constants import ItemResultFormat, Signs, line_delimiter
from severity import Severity


class PSRuleValidator(ValidatorBase):
    def __init__(self, validatorCatalog, rules_file_path, severity=Severity.MODERATE):
        super().__init__("PSRuleValidator", validatorCatalog, severity)
        self.rules_file_path = rules_file_path

    def validate(self):
        logging.debug(f"Validating PSRule JSON file: {self.rules_file_path}")
        messages = []
        try:
            with open(self.rules_file_path, "r") as file:
                data = json.load(file)

            detail_messages = []
            for item in data:
                if item["outcome"] != "Fail":
                    continue
                rule_name = item["ruleName"]
                error_code = item["ref"]
                recommendation = item["info"]["recommendation"]
                reference = (
                    f"reference: {item['info']['annotations']['online version']}"
                )

                item = ItemResultFormat.SUBITEM.format(
                    sign=Signs.BLOCK
                    if Severity.isBlocker(self.severity)
                    else Signs.WARNING,
                    message=f"{rule_name} ({error_code}){line_delimiter}",
                )
                detail_messages.append(
                    indent(line_delimiter.join([item, recommendation, reference]), 4)
                )
            detail_messages = line_delimiter.join(detail_messages)
            if detail_messages:
                messages.append(
                    ItemResultFormat.FAIL.format(
                        sign=Signs.BLOCK
                        if Severity.isBlocker(self.severity)
                        else Signs.WARNING,
                        message="Security Scan",
                        detail_messages=detail_messages,
                    )
                )
                self.result = False
            else:
                self.result = True
                messages.append(
                    ItemResultFormat.PASS.format(
                        sign=Signs.CHECK, message="Security Scan"
                    )
                )
            self.resultMessage = line_delimiter.join(messages)
            return self.result, self.resultMessage
        except Exception as e:
            logging.error(f"Error parsing PSRule JSON file: {e}")
            # Parsing error usually caused by wrong workflow behavior
            self.result = True
            self.resultMessage = ItemResultFormat.PASS.format(
                sign=Signs.CHECK, message="Security scan is not performed"
            )
            return self.result, self.resultMessage
