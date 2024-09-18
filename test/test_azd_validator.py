import unittest
import subprocess
from unittest.mock import patch, MagicMock
from validator.azd_validator import AzdValidator
from constants import Signs
from utils import indent

class TestAzdValidator(unittest.TestCase):
    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_azd_up_success(self, mock_run, mock_list_resources):
        mock_run.return_value = MagicMock(stdout="azd up success", returncode=0)
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)
        mock_list_resources.assert_called_once()

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_azd_up_failure(self, mock_run, mock_list_resources):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd up", output="azd up failed")
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)
        mock_list_resources.assert_called_once()

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_azd_down_success(self, mock_run, mock_list_resources):
        mock_run.return_value = MagicMock(stdout="azd down success", returncode=0)
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)
        mock_list_resources.assert_not_called()

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_azd_down_failure(self, mock_run, mock_list_resources):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd down", output="azd down failed")
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertEqual(mock_run.call_count, 1)
        mock_list_resources.assert_not_called()

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_validate_retry_logic_ETXTBSY(self, mock_runCommand, mock_list_resources):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: spawn ETXTBSY"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: spawn ETXTBSY"),
            MagicMock(returncode=0, stdout="azd up success")
        ]
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        # Check that runCommand was called 3 times
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 3)
        self.assertEqual(mock_list_resources.call_count, 3)

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_validate_retry_logic_DOCKER(self, mock_runCommand, mock_list_resources):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            MagicMock(returncode=0, stdout="azd up success")
        ]
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        # Check that runCommand was called 3 times
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 3)
        self.assertEqual(mock_list_resources.call_count, 3)

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_validate_retry_logic_finally_failed(self, mock_runCommand, mock_list_resources):
        # Simulate a retryable error
        mock_runCommand.side_effect = [
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
            subprocess.CalledProcessError(1, "azd up", output="Retryable error message: Cannot connect to the Docker daemon"),
        ]
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        # Check that runCommand was called 4 times
        self.assertFalse(validator.result)
        self.assertEqual(mock_runCommand.call_count, 4)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        self.assertIn("Cannot connect to the Docker daemon", validator.resultMessage)
        self.assertEqual(mock_list_resources.call_count, 4)

    @patch('validator.azd_validator.AzdValidator.list_resources')
    @patch('subprocess.run')
    def test_replace_backslashes_in_output(self, mock_runCommand, mock_list_resources):
        # Simulate subprocess output with backslashes
        mock_runCommand.side_effect = subprocess.CalledProcessError(1, "azd down", output="azd down failed with \\\"error\\\": \\\"message\\\"")
        mock_list_resources.return_value = None
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        # Check that the result is unsuccessful
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
        # Verify that backslashes are replaced in the output
        self.assertIn("\"error\": \"message\"", validator.resultMessage)
        self.assertEqual(mock_runCommand.call_count, 1)
        self.assertEqual(mock_list_resources.call_count, 1)

    @patch('validator.azd_validator.list_resources')
    @patch('subprocess.run')
    def test_list_resources(self, mock_run, mock_list_resources):
        # Mock the subprocess calls for resource group and subscription ID
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="mocked-resource-group"),
            MagicMock(returncode=0, stdout="mocked-subscription-id")
        ]
        # Mock the list_resources function
        mock_list_resources.return_value = (["resource1", "resource2"], ["deployment1", "deployment2"])

        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        result = validator.list_resources()

        # Check that the subprocess calls were made correctly
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call("azd env get-value AZURE_RESOURCE_GROUP", shell=True, text=True, capture_output=True)
        mock_run.assert_any_call("azd env get-value AZURE_SUBSCRIPTION_ID", shell=True, text=True, capture_output=True)

        # Check that the list_resources function was called with the correct arguments
        mock_list_resources.assert_called_once_with("mocked-resource-group", "mocked-subscription-id")

        # Check the result of the list_resources method
        expected_result = indent("List of all resource types in the resource group mocked-resource-group:\nresource1\nresource2\n List of all AI deployments:\ndeployment1\ndeployment2", 2)
        self.assertIn(expected_result, result)
