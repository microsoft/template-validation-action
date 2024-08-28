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

    @patch('subprocess.run')
    def test_azd_up_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd up", output="azd up failed")
        validator = AzdValidator("AzdUpCatalog", ".", True, False)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)

    @patch('subprocess.run')
    def test_azd_down_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="azd down success", returncode=0)
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertTrue(validator.result)
        self.assertIn(Signs.CHECK, validator.resultMessage)

    @patch('subprocess.run')
    def test_azd_down_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "azd down", output="azd down failed")
        validator = AzdValidator("AzdDownCatalog", ".", False, True)
        validator.validate()
        self.assertFalse(validator.result)
        self.assertIn(Signs.BLOCK, validator.resultMessage)
