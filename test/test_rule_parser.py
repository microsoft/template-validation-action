import argparse
import unittest
import json
from unittest.mock import patch, mock_open
from rule_parser import RuleParser
from validator.file_validator import FileValidator
from validator.azd_validator import AzdValidator
from validator.topic_validator import TopicValidator
from validator.azd_command import AzdCommand
from level import Level


class TestParseRules(unittest.TestCase):
    @patch("utils.find_infra_yaml_path")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            {
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
                    "level": "high",
                },
                "azd up": {
                    "catalog": "Functional Requirements",
                    "validator": "AzdValidator",
                    "level": "high",
                },
                "expected_topics": {
                    "catalog": "Repository Management",
                    "topics": ["azd-templates", "ai-azd-templates"],
                    "validator": "TopicValidator",
                    "level": "high",
                },
            }
        ),
    )
    def test_rule_parser(self, mock_file, mock_find_infra_yaml_path):
        mock_find_infra_yaml_path.return_value = ["mocked/path/to/infra.yaml"]
        args = argparse.Namespace(
            validate_azd=True,
            topics="azd-templates,azure",
            repo_path=".",
            validate_paths=None,
            expected_topics=None,
        )
        parser = RuleParser("dummy_path", args)
        validators = parser.parse()

        self.assertEqual(len(validators), 4)

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
        self.assertEqual(file_validator.level, Level.HIGH)

        azd_validator = validators[1]
        self.assertIsInstance(azd_validator, AzdValidator)
        self.assertEqual(azd_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_validator.command, AzdCommand.UP)
        self.assertEqual(azd_validator.level, Level.HIGH)

        azd_validator = validators[2]
        self.assertIsInstance(azd_validator, AzdValidator)
        self.assertEqual(azd_validator.catalog, "Functional Requirements")
        self.assertEqual(azd_validator.folderPath, "mocked/path/to/infra.yaml")
        self.assertEqual(azd_validator.command, AzdCommand.DOWN)
        self.assertEqual(azd_validator.level, Level.HIGH)

        topic_validator = validators[3]
        self.assertIsInstance(topic_validator, TopicValidator)
        self.assertEqual(topic_validator.catalog, "Repository Management")
        self.assertEqual(
            topic_validator.expected_topics, ["azd-templates", "ai-azd-templates"]
        )
        self.assertEqual(topic_validator.level, Level.HIGH)


if __name__ == "__main__":
    unittest.main()
