from abc import abstractmethod


class ValidatorBase:
    def __init__(self, name, catalog, severity):
        self.name = name
        self.catalog = catalog
        self.severity = severity
        self.result = False
        self.resultMessage = "Validation not performed"

    @abstractmethod
    def validate(self):
        pass
