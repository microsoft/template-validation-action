import unittest
from unittest.mock import patch
from validator.playwright_validator import PlaywrightTestValidator
from constants import ItemResultFormat, Signs
from severity import Severity


class TestPlaywrightTestValidator(unittest.TestCase):
    @patch("os.walk")
    @patch("subprocess.run")
    def test_validate_with_successful_tests(self, mock_run, mock_walk):
        mock_walk.return_value = [("./.github/workflows", [], ["playwright-test.yaml"])]
        mock_run.return_value.returncode = 0

        validator = PlaywrightTestValidator("ValidatorCatalog", "./test", Severity.LOW)
        result, message = validator.validate()

        self.assertTrue(result)
        self.assertEqual(
            message,
            ItemResultFormat.PASS.format(
                sign=Signs.CHECK, message="All Playwright tests passed."
            ),
        )

    @patch("os.walk")
    @patch("subprocess.run")
    def test_validate_with_failed_tests(self, mock_run, mock_walk):
        mock_walk.return_value = [("./.github/workflows", [], ["playwright-test.yaml"])]
        mock_run.return_value.returncode = 1

        validator = PlaywrightTestValidator(
            "ValidatorCatalog", "./test/e2e", Severity.LOW
        )
        result, message = validator.validate()

        self.assertFalse(result)
        self.assertEqual(
            message,
            ItemResultFormat.FAIL.format(
                sign=Signs.WARNING,
                message="Playwright GitHub Action tests failed",
                detail_messages="One or more Playwright tests did not pass.",
            ),
        )

    @patch("os.walk")
    def test_validate_with_missing_yaml(self, mock_walk):
        mock_walk.return_value = [("./.github/workflows", [], [])]

        validator = PlaywrightTestValidator(
            "ValidatorCatalog", "./test/e2e", Severity.LOW
        )
        result, message = validator.validate()

        self.assertFalse(result)
        self.assertEqual(
            message,
            ItemResultFormat.FAIL.format(
                sign=Signs.WARNING,
                message="Playwright GitHub Action is missing",
                detail_messages="No `playwright-test.yaml` or `.yml` found in the repository.",
            ),
        )

    @patch("os.walk", side_effect=Exception("Unexpected Error"))
    def test_validate_with_error_during_execution(self, mock_walk):
        validator = PlaywrightTestValidator(
            "ValidatorCatalog", "./test/e2e", Severity.LOW
        )
        result, message = validator.validate()

        self.assertFalse(result)
        self.assertIn("An error occurred during validation", message)


if __name__ == "__main__":
    unittest.main()
