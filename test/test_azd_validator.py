import unittest
import subprocess
from unittest.mock import patch, MagicMock
from validator.azd_validator import AzdValidator
from constants import Signs

class TestAzdValidator(unittest.TestCase):
    @patch('subprocess.run')
    def test_azd_up_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="azd up success", returncode=0)
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    def test_azd_up_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd up", output="azd up failed")
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    def test_azd_down_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="azd down success", returncode=0)
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    def test_azd_down_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd down", output="azd down failed")
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    def test_validate_retry_logic_ETXTBSY(self, mock_runCommand):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: spawn ETXTBSY"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: spawn ETXTBSY"),
            MagicMock(returncode=0, stdout="azd up success")
        ]

        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()

        # Check that runCommand was called 3 times
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 3)

    @patch('subprocess.run')
    def test_validate_retry_logic_DOCKER(self, mock_runCommand):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            MagicMock(returncode=0, stdout="azd up success")
        ]

        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()

        # Check that runCommand was called 3 times
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 3)

    @patch('subprocess.run')
    def test_validate_retry_logic_finally_failed(self, mock_runCommand):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
        ]

        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()

        # Check that runCommand was called 3 times
        self.assertFalse(validator.result)
        self.assertEqual(mock_runCommand.call_count, 4)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertIn("Cannot connect to the Docker daemon", validator.resultMessage)


    @patch('subprocess.run')
    def test_replace_backslashes_in_output(self, mock_runCommand):
        # Simulate subprocess output with backslashes
        mock_runCommand.side_effect = subprocess.CalledProcessError(1, "azd down", output="azd down failed with \\\"error\\\": \\\"message\\\"")

        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()

        # Check that the result is successful
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        # Verify that backslashes are replaced in the output
        self.assertIn('\\"error\\": \\"message\\"', validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 1)
