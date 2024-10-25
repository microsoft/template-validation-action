import unittest
from unittest.mock import patch, mock_open
from validator.ps_rule_validator import PSRuleValidator
from severity import Severity
from constants import ItemResultFormat, Signs


class TestPSRuleValidator(unittest.TestCase):
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"outcome": "Fail", "ruleName": "Rule1", "ref": "Error1", "info": {"recommendation": "Do this", "annotations": {"online version": "http://example.com"}}}]',
    )
    def test_validate_with_failure(self, mock_file):
        validator = PSRuleValidator("ValidatorCatalog", "dummy_path", Severity.HIGH)
        result, message = validator.validate()

        self.assertFalse(result)
        self.assertEqual(
            message,
            ItemResultFormat.FAIL.format(
                sign=Signs.BLOCK,
                message="Security Scan",
                detail_messages="  - [ ] :x: Rule1 (Error1)\n    \n    Do this\n    reference: http://example.com",
            ),
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"outcome": "Fail", "ruleName": "Rule1", "ref": "Error1", "info": {"recommendation": "Do this", "annotations": {"online version": "http://example.com"}}}, {"outcome": "Fail", "ruleName": "Rule2", "ref": "Error2", "info": {"recommendation": "Do that", "annotations": {"online version": "http://example.com"}}}]'
    )
    def test_validate_with_multiple_failures(self, mock_file):
        validator = PSRuleValidator("ValidatorCatalog", "dummy_path", Severity.HIGH)
        result, message = validator.validate()

        self.assertFalse(result)
        self.assertEqual(
            message,
            ItemResultFormat.FAIL.format(
                sign=Signs.BLOCK,
                message="Security Scan",
                detail_messages="  - [ ] :x: Rule1 (Error1)\n    \n    Do this\n    reference: http://example.com\n  - [ ] :x: Rule2 (Error2)\n    \n    Do that\n    reference: http://example.com",
            ),
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"outcome": "Pass", "ruleName": "Rule1", "ref": "Error1", "info": {"recommendation": "Do this", "annotations": {"online version": "http://example.com"}}}]',
    )
    def test_validate_with_no_failures(self, mock_file):
        validator = PSRuleValidator("ValidatorCatalog", "dummy_path", Severity.HIGH)
        result, message = validator.validate()

        self.assertTrue(result)
        self.assertEqual(
            message,
            ItemResultFormat.PASS.format(sign=Signs.CHECK, message="Security Scan"),
        )

    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    def test_validate_with_empty_file(self, mock_file):
        validator = PSRuleValidator("ValidatorCatalog", "dummy_path", Severity.HIGH)
        result, message = validator.validate()

        self.assertTrue(result)
        self.assertEqual(
            message,
            ItemResultFormat.PASS.format(sign=Signs.CHECK, message="Security Scan"),
        )

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_validate_with_invalid_json(self, mock_file):
        validator = PSRuleValidator("ValidatorCatalog", "dummy_path", Severity.HIGH)
        result, message = validator.validate()
        self.assertTrue(result)
        self.assertEqual(message, "- [x] <b>Security scan is not performed</b>.")


if __name__ == "__main__":
    unittest.main()
