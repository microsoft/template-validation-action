from abc import abstractmethod


class ValidatorBase:
    def __init__(self, name, catalog, level):
        self.name = name
        self.catalog = catalog
        self.level = level
        self.result = False
        self.resultMessage = "Validation not performed."

    @abstractmethod
    def validate(self):
        pass
