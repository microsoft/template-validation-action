import unittest
from unittest.mock import MagicMock
from execution_engine import ExecutionEngine
from validator.file_validator import FileValidator
from validator.azd_validator import AzdValidator

class TestExecutionEngine(unittest.TestCase):
    def test_execute_validators(self):
        # Mock validators
        file_validator = MagicMock(spec=FileValidator)
        file_validator.catalog = "FileValidator"
        file_validator.validate.return_value = None
        file_validator.result = True
        file_validator.resultMessage = "File validation passed."

        azd_validator = MagicMock(spec=AzdValidator)
        azd_validator.catalog = "AzdValidator"
        azd_validator.validate.return_value = None
        azd_validator.result = True
        azd_validator.resultMessage = "Azd validation passed."

        validators = [file_validator, azd_validator]

        engine = ExecutionEngine(validators)
        results = engine.execute()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("FileValidator", True, "File validation passed."))
        self.assertEqual(results[1], ("AzdValidator", True, "Azd validation passed."))

if __name__ == "__main__":
    unittest.main()