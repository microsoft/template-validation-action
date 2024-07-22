from abc import ABC, abstractmethod

class ValidatorBase:
    def __init__(self, name, catalog, errorAsWarning=False):
        self.name = name
        self.catalog = catalog
        self.errorAsWarning = errorAsWarning
        self.result = False
        self.resultMessage = "Validation not performed."
    
    @abstractmethod
    def validate(self):
        pass