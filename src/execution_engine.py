class ExecutionEngine:
    def __init__(self, validators):
        self.validators = validators

    def execute(self):
        results = []
        for validator in self.validators:
            try:
                validator.validate()
                results.append(
                    (validator.catalog, validator.result, validator.resultMessage)
                )
            except Exception as e:
                results.append((validator.catalog, False, str(e)))
        return results


# Example usage
if __name__ == "__main__":
    from parse_rules import RuleParse
    import os

    rules_file_path = os.path.join(os.path.dirname(__file__), "rules.json")
    parser = RuleParse(rules_file_path)
    validators = parser.parse()

    engine = ExecutionEngine(validators)
    results = engine.execute()

    for result in results:
        print(f"Catalog: {result[0]}, Result: {result[1]}, Message: {result[2]}")
