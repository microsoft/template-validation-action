import argparse
import unittest
import json
from unittest.mock import patch, mock_open
from parse_rules import RuleParser
from validator.file_validator import FileValidator
from validator.azd_validator import AzdValidator
from validator.topic_validator import TopicValidator


class TestParseRules(unittest.TestCase):
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
                    "error_as_warning": False,
                },
                "azd up": {
                    "catalog": "Functional Requirements",
                    "validator": "AzdValidator",
                    "error_as_warning": False,
                },
                "expected_topics": {
                    "catalog": "Repository Management",
                    "topics": ["azd-templates", "ai-azd-templates"],
                    "validator": "TopicValidator",
                    "error_as_warning": True,
                },
            }
        ),
    )
    def test_parse_rules(self, mock_file):
        args = argparse.Namespace(
            azdup=True, azddown=True, topics="azd-templates,azure"
        )
        parser = RuleParser("dummy_path", args)
        validators = parser.parse()

        self.assertEqual(len(validators), 3)

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
        self.assertFalse(file_validator.errorAsWarning)

        azd_validator = validators[1]
        self.assertIsInstance(azd_validator, AzdValidator)
        self.assertEqual(azd_validator.catalog, "Functional Requirements")
        self.assertFalse(azd_validator.errorAsWarning)

        topic_validator = validators[2]
        self.assertIsInstance(topic_validator, TopicValidator)
        self.assertEqual(topic_validator.catalog, "Repository Management")
        self.assertEqual(
            topic_validator.expected_topics, ["azd-templates", "ai-azd-templates"]
        )
        self.assertTrue(topic_validator.errorAsWarning)


if __name__ == "__main__":
    unittest.main()
