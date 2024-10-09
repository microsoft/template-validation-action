import logging
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, Signs, line_delimiter
from severity import Severity


class TopicValidator(ValidatorBase):
    def __init__(
        self, catalog, name, expected_topics, actual_topics, severity=Severity.MODERATE
    ):
        super().__init__("TopicValidator", catalog, severity)
        self.name = name
        self.expected_topics = expected_topics
        self.actual_topics = actual_topics

    def validate(self):
        logging.debug("Checking for topics...")
        messages = []
        result = True

        subMessages = []
        if self.actual_topics is None:
            result = False
            subMessages.append(
                ItemResultFormat.SUBITEM.format(
                    sign=Signs.BLOCK
                    if Severity.isBlocker(self.severity)
                    else Signs.WARNING,
                    message="topics string is NULL.",
                )
            )
        else:
            actual_topics_list = self.actual_topics.replace('"', "").split(",")
            for topic in self.expected_topics:
                if topic not in actual_topics_list:
                    result = result and False
                    subMessages.append(
                        ItemResultFormat.SUBITEM.format(
                            sign=Signs.BLOCK
                            if Severity.isBlocker(self.severity)
                            else Signs.WARNING,
                            message=f"{topic} is missing in topics.",
                        )
                    )

        if result:
            messages.append(
                ItemResultFormat.PASS.format(
                    message=f"Topics on repo contains {self.expected_topics}"
                )
            )
        else:
            messages.append(
                ItemResultFormat.FAIL.format(
                    sign=Signs.BLOCK
                    if Severity.isBlocker(self.severity)
                    else Signs.WARNING,
                    message=f"Topics on repo contains {self.expected_topics}",
                    detail_messages=line_delimiter.join(subMessages),
                )
            )

        self.result = result
        self.resultMessage = line_delimiter.join(messages)
        return result, self.resultMessage
