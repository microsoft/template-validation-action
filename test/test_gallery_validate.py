# test_gallery_validate.py

import unittest
from unittest.mock import patch, MagicMock
import os
from gallery_validate import (
    check_msdo_result,
    find_cicd_workflow_file,
    check_topic_existence,
    check_for_actions_in_workflow_file,
    check_folder_existence,
    check_repository_management,
    check_source_code_structure,
    check_functional_requirements,
    check_security_requirements,
    find_infra_yaml_path,
    internal_validator
)
from utils import indent
from constants import Signs

class TestGalleryValidate(unittest.TestCase):

    @patch('gallery_validate.loader.load_sarif_file')
    @patch('os.path.isfile')
    def test_check_msdo_result_with_errors(self, mock_isfile, mock_load_sarif_file):
        mock_isfile.return_value = True
        mock_load_sarif_file.return_value = MagicMock(get_records_grouped_by_severity=MagicMock(return_value={
            "error": [{"Code": "AZR-000001", "Description": "Error description\nDetailed description"}]
        }))

        result, message = check_msdo_result("dummy_path")
        
        self.assertFalse(result)
        self.assertIn(f"    {Signs.BLOCK} error: AZR-000001 - Error description\n    Detailed description", message)

    @patch('gallery_validate.loader.load_sarif_file')
    @patch('os.path.isfile')
    def test_check_msdo_result_with_warnings(self, mock_isfile, mock_load_sarif_file):
        mock_isfile.return_value = True
        mock_load_sarif_file.return_value = MagicMock(get_records_grouped_by_severity=MagicMock(return_value={
            "warning": [{"Code": "AZR-000002", "Description": "Warning description\nDetailed description"}]
        }))

        result, message = check_msdo_result("dummy_path")
        
        self.assertTrue(result)
        self.assertIn(f"    {Signs.BLOCK} warning: AZR-000002 - Warning description\n    Detailed description", message)

    @patch('gallery_validate.loader.load_sarif_file')
    @patch('os.path.isfile')
    def test_check_msdo_result_with_no_issues(self, mock_isfile, mock_load_sarif_file):
        mock_isfile.return_value = True
        mock_load_sarif_file.return_value = MagicMock(get_records_grouped_by_severity=MagicMock(return_value={}))

        result, message = check_msdo_result("dummy_path")
        
        self.assertTrue(result)
        self.assertIn(Signs.CHECK, message)

    @patch('gallery_validate.loader.load_sarif_file')
    @patch('os.path.isfile')
    def test_check_msdo_result_with_missing_file(self, mock_isfile, mock_load_sarif_file):
        mock_isfile.return_value = False

        result, message = check_msdo_result("dummy_path")
        
        self.assertFalse(result)
        self.assertIn(f"  {Signs.BLOCK} Error: Scan result is missing.", message)

    @patch('os.listdir')
    @patch('gallery_validate.check_folder_existence')
    def test_find_cicd_workflow_file(self, mock_check_folder_existence, mock_listdir):
        mock_check_folder_existence.return_value = (True, "")
        mock_listdir.return_value = ['workflow1.yml', 'workflow2.yml', 'not_a_workflow.txt']

        result = find_cicd_workflow_file("dummy_repo_path")
        
        self.assertEqual(result, ['workflow1.yml', 'workflow2.yml'])

    def test_check_topic_existence_with_missing_topics(self):
        actual_topics = None
        expected_topics = ["topic1", "topic2"]

        result, message = check_topic_existence(actual_topics, expected_topics)
        
        self.assertFalse(result)
        self.assertIn("Error: topics string is NULL.", message)

    def test_check_topic_existence_with_all_topics(self):
        actual_topics = "topic1,topic2"
        expected_topics = ["topic1", "topic2"]

        result, message = check_topic_existence(actual_topics, expected_topics)
        
        self.assertTrue(result)
        self.assertNotIn("Error", message)

    def test_check_topic_existence_with_missing_expected_topic(self):
        actual_topics = "topic1"
        expected_topics = ["topic1", "topic2"]

        result, message = check_topic_existence(actual_topics, expected_topics)
        
        self.assertFalse(result)
        self.assertIn("Error: topic2 is missing in topics", message)

    @patch('os.path.isdir')
    def test_check_folder_existence(self, mock_isdir):
        mock_isdir.return_value = True

        result, message = check_folder_existence("dummy_repo_path", "dummy_folder")
        
        self.assertTrue(result)
        self.assertIn(Signs.CHECK, message)

    @patch('os.path.isdir')
    def test_check_folder_existence_with_missing_folder(self, mock_isdir):
        mock_isdir.return_value = False

        result, message = check_folder_existence("dummy_repo_path", "dummy_folder")
        
        self.assertFalse(result)
        self.assertIn(Signs.BLOCK, message)

    @patch('gallery_validate.FileValidator.validate')
    @patch('gallery_validate.check_topic_existence')
    def test_check_repository_management(self, mock_validate, mock_check_topic_existence):
        mock_validate.return_value = (True, "Validation passed")
        mock_check_topic_existence.return_value = (True, "Validation passed")

        result, message = check_repository_management("dummy_repo_path", "dummy_topics")
        
        self.assertTrue(result)
        self.assertIn("Validation passed", message)
    
    def test_check_source_code_structure(self):
        pass

    @patch('gallery_validate.AzdValidator.validate')
    def test_check_functional_requirements(self, mock_validate):
        mock_validate.return_value = (True, "Validation passed")

        result, message = check_functional_requirements(["dummy_infra_yaml_path"], True, True)
        
        self.assertTrue(result)
        self.assertIn("Validation passed", message)

    @patch('gallery_validate.check_msdo_result')
    @patch('gallery_validate.check_for_actions_in_workflow_file')
    @patch('gallery_validate.find_cicd_workflow_file')
    def test_check_security_requirements(self, mock_find_cicd_workflow_file, mock_check_for_actions_in_workflow_file, mock_check_msdo_result):
        mock_find_cicd_workflow_file.return_value = ["workflow1.yml"]
        mock_check_for_actions_in_workflow_file.return_value = (True, "Action found")
        mock_check_msdo_result.return_value = (True, "MSDO result passed")

        result, message = check_security_requirements("dummy_repo_path", "dummy_msdo_result_file")
        
        self.assertTrue(result)
        self.assertIn(Signs.CHECK, message)
        self.assertIn("MSDO result passed", message)

    @patch('gallery_validate.find_infra_yaml_path')
    @patch('gallery_validate.check_repository_management')
    @patch('gallery_validate.check_source_code_structure')
    @patch('gallery_validate.check_functional_requirements')
    @patch('gallery_validate.check_security_requirements')
    @patch('os.path.isdir')
    def test_internal_validator(self, mock_isdir, mock_check_security_requirements, mock_check_functional_requirements, mock_check_source_code_structure, mock_check_repository_management, mock_find_infra_yaml_path):
        mock_isdir.return_value = True
        mock_find_infra_yaml_path.return_value = ["dummy_infra_yaml_path"]
        mock_check_repository_management.return_value = (True, "Repo management passed")
        mock_check_source_code_structure.return_value = (True, "Source code structure passed")
        mock_check_functional_requirements.return_value = (True, "Functional requirements passed")
        mock_check_security_requirements.return_value = (True, "Security requirements passed")

        result, message = internal_validator("dummy_repo_path", True, True, "dummy_topics", "dummy_msdo_result_file")
        
        self.assertTrue(result)
        self.assertIn("Repo management passed", message)
        self.assertIn("Source code structure passed", message)
        self.assertIn("Functional requirements passed", message)
        self.assertIn("Security requirements passed", message)

if __name__ == '__main__':
    unittest.main()