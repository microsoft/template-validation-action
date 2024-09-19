import logging
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, Signs, line_delimiter


class TopicValidator(ValidatorBase):
    def __init__(
        self, catalog, name, expected_topics, actual_topics, error_as_warning=False
    ):
        super().__init__("TopicValidator", catalog, error_as_warning)
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
                    sign=Signs.WARNING, message="Error: topics string is NULL."
                )
            )
        else:
            actual_topics_list = self.actual_topics.replace('"', "").split(",")
            for topic in self.expected_topics:
                if topic not in actual_topics_list:
                    result = result and False
                    subMessages.append(
                        ItemResultFormat.SUBITEM.format(
                            sign=Signs.WARNING,
                            message=f"Error: {topic} is missing in topics.",
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
                ItemResultFormat.WARNING.format(
                    message=f"Topics on repo contains {self.expected_topics}",
                    detail_messages=line_delimiter.join(subMessages),
                )
            )

        self.result = result
        self.resultMessage = line_delimiter.join(messages)
        return result, self.resultMessage
