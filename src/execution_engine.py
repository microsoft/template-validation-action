class ExecutionEngine:
    def __init__(self, validators):
        self.validators = validators

    def execute(self):
        results = []
        for validator in self.validators:
            try:
                validator.validate()
                results.append((
                    validator.catalog,
                    validator.severity,
                    validator.result,
                    validator.resultMessage,
                ))
            except Exception as e:
                results.append((validator.catalog, validator.severity, False, str(e)))
        return results
