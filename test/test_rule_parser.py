import argparse
import unittest
import json
from unittest.mock import patch, mock_open
from rule_parser import RuleParser
from validator.file_validator import FileValidator
from validator.azd_validator import AzdValidator
from validator.topic_validator import TopicValidator
from validator.azd_command import AzdCommand
from validator.ps_rule_validator import PSRuleValidator
from severity import Severity


class TestParseRules(unittest.TestCase):
    @patch("utils.find_infra_yaml_path")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps({
            "README": {
                "catalog": "Repository Management",
                "ext": [".md"],
                "candidate_path": ["."],
                "assert_in": [
                    "## Features",
                    "## Getting Started",
                    "## Guidance",
                    "## Resources",
                ],
                "case_sensitive": False,
                "validator": "FileValidator",
                "severity": "high",
            },
            "azd up": {
                "catalog": "Functional Requirements",
                "validator": "AzdValidator",
                "severity": "high",
            },
            "azd down": {
                "catalog": "Functional Requirements",
                "validator": "AzdValidator",
                "severity": "moderate",
            },
            "expected_topics": {
                "catalog": "Repository Management",
                "topics": ["azd-templates", "ai-azd-templates"],
                "validator": "TopicValidator",
                "severity": "high",
            },
            "ps rule": {
                "catalog": "Security Requirements",
                "validator": "PSRuleValidator",
                "severity": "moderate",
            },
        }),
    )
    def test_rule_parser(self, mock_file, mock_find_infra_yaml_path):
        mock_find_infra_yaml_path.return_value = [
            "mocked/path/to/infra.yaml",
            "mocked/path/to/infra2.yaml",
        ]
        args = argparse.Namespace(
            validate_azd=True,
            topics="azd-templates,azure",
            repo_path=".",
            psrule_result="mocked/path/to/psrule.output",
            validate_paths=None,
            expected_topics=None,
        )
        parser = RuleParser("dummy_path", args)
        validators = parser.parse()

        self.assertEqual(len(validators), 7)

        file_validator = validators[0]
        self.assertIsInstance(file_validator, FileValidator)
        self.assertEqual(file_validator.catalog, "Repository Management")
        self.assertEqual(file_validator.extensionList, [".md"])
        self.assertEqual(file_validator.candidatePaths, ["."])
        self.assertEqual(
            file_validator.h2Tags,
            ["## Features", "## Getting Started", "## Guidance", "## Resources"],
        )
        self.assertFalse(file_validator.caseSensitive)
        self.assertEqual(file_validator.severity, Severity.HIGH)

        azd_validator = validators[1]
        self.assertIsInstance(azd_validator, AzdValidator)
        self.assertEqual(azd_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_validator.command, AzdCommand.UP)
        self.assertEqual(azd_validator.severity, Severity.HIGH)

        azd_down_validator = validators[2]
        self.assertIsInstance(azd_down_validator, AzdValidator)
        self.assertEqual(azd_down_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_down_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_down_validator.command, AzdCommand.DOWN)
        self.assertEqual(azd_down_validator.severity, Severity.MODERATE)

        azd_up_validator = validators[3]
        self.assertIsInstance(azd_up_validator, AzdValidator)
        self.assertEqual(azd_up_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_up_validator.folderPath, "mocked/path/to/infra2.yaml")
        self.assertEqual(azd_up_validator.command, AzdCommand.UP)
        self.assertEqual(azd_up_validator.severity, Severity.HIGH)

        azd_down_validator = validators[4]
        self.assertIsInstance(azd_down_validator, AzdValidator)
        self.assertEqual(azd_down_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_down_validator.folderPath, "mocked/path/to/infra2.yaml")
        self.assertEqual(azd_down_validator.command, AzdCommand.DOWN)
        self.assertEqual(azd_down_validator.severity, Severity.MODERATE)

        topic_validator = validators[5]
        self.assertIsInstance(topic_validator, TopicValidator)
        self.assertEqual(topic_validator.catalog, "Repository Management")
        self.assertEqual(
            topic_validator.expected_topics, ["azd-templates", "ai-azd-templates"]
        )
        self.assertEqual(topic_validator.severity, Severity.HIGH)

        ps_rule_validator = validators[6]
        self.assertIsInstance(ps_rule_validator, PSRuleValidator)
        self.assertEqual(ps_rule_validator.catalog, "Security Requirements")
        self.assertEqual(
            ps_rule_validator.rules_file_path, "mocked/path/to/psrule.output"
        )
        self.assertEqual(ps_rule_validator.severity, Severity.MODERATE)

    @patch("utils.find_infra_yaml_path")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps({
            "azd up": {
                "catalog": "Functional Requirements",
                "validator": "AzdValidator",
                "severity": "high",
            },
            "azd down": {
                "catalog": "Functional Requirements",
                "validator": "AzdValidator",
                "severity": "moderate",
            },
        }),
    )
    def test_parse_azd_validator(self, mock_file, mock_find_infra_yaml_path):
        mock_find_infra_yaml_path.return_value = ["mocked/path/to/infra.yaml"]
        args = argparse.Namespace(
            validate_azd=True,
            topics=None,
            repo_path=".",
            validate_paths=None,
            expected_topics=None,
        )
        parser = RuleParser("dummy_path", args)
        validators = parser.parse()

        self.assertEqual(len(validators), 2)

        azd_up_validator = validators[0]
        self.assertIsInstance(azd_up_validator, AzdValidator)
        self.assertEqual(azd_up_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_up_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_up_validator.command, AzdCommand.UP)
        self.assertEqual(azd_up_validator.severity, Severity.HIGH)

        azd_down_validator = validators[1]
        self.assertIsInstance(azd_down_validator, AzdValidator)
        self.assertEqual(azd_down_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_down_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_down_validator.command, AzdCommand.DOWN)
        self.assertEqual(azd_down_validator.severity, Severity.MODERATE)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"README": {"validator": "FileValidator", "catalog": "TestCatalog", "ext": [".md"], "assert_in": ["## Default H2"]}}',
    )
    @patch("os.getenv")
    def test_h2tag_env_empty(self, mock_getenv, mock_file):
        # Mock the environment variable to an empty string
        mock_getenv.return_value = "None"

        args = argparse.Namespace(
            validate_azd=False,
            topics=None,
            repo_path=".",
            validate_paths=None,
            expected_topics=None,
        )
        parser = RuleParser("dummy_path", args)
        validators = parser.parse()

        self.assertEqual(len(validators), 1)

        file_validator = validators[0]
        self.assertIsInstance(file_validator, FileValidator)
        self.assertEqual(file_validator.catalog, "TestCatalog")
        self.assertEqual(file_validator.name, "READMEFileValidator")
        self.assertEqual(file_validator.extensionList, [".md"])
        self.assertEqual(file_validator.h2Tags, None)
        self.assertEqual(file_validator.severity, Severity.MODERATE)


if __name__ == "__main__":
    unittest.main()
