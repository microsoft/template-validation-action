import unittest
from unittest.mock import patch, MagicMock
import os
import argparse
from gallery_validate import main
from parse_rules import RuleParse
from execution_engine import ExecutionEngine
from result_aggregator import ResultAggregator


class TestGalleryValidate(unittest.TestCase):
    @patch("gallery_validate.ResultAggregator")
    @patch("gallery_validate.ExecutionEngine")
    @patch("gallery_validate.RuleParse")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main(
        self, mock_parse_args, MockRuleParse, MockExecutionEngine, MockResultAggregator
    ):
        mock_parse_args.return_value = argparse.Namespace(
            repo_path="dummy_repo_path",
            azdup=True,
            azddown=True,
            debug=True,
            topics="azd-templates,azure",
            msdoresult="dummy_msdo_result_file",
            output=None,
        )

        mock_rule_parser = MockRuleParse.return_value
        mock_rule_parser.parse.return_value = ["validator1", "validator2"]

        mock_execution_engine = MockExecutionEngine.return_value
        mock_execution_engine.execute.return_value = [
            ("validator1", True, "Validation passed"),
            ("validator2", False, "Validation failed"),
        ]

        mock_result_aggregator = MockResultAggregator.return_value
        mock_result_aggregator.generate_summary.return_value = "Summary"

        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_called_once_with("Summary")


if __name__ == "__main__":
    unittest.main()
