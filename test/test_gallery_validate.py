import unittest
from unittest.mock import patch
import argparse
from gallery_validate import main

class TestGalleryValidate(unittest.TestCase):
    @patch("gallery_validate.ResultAggregator")
    @patch("gallery_validate.ExecutionEngine")
    @patch("gallery_validate.RuleParser")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main(
        self, mock_parse_args, MockRuleParser, MockExecutionEngine, MockResultAggregator
    ):
        mock_parse_args.return_value = argparse.Namespace(
            repo_path="dummy_repo_path",
            validate_paths=None,
            validate_azd=True,
            topics="azd-templates,azure",
            expected_topics=None,
            msdoresult="dummy_msdo_result_file",
            output=None,
            debug=True,
        )

        mock_rule_parser = MockRuleParser.return_value
        mock_rule_parser.parse.return_value = ["validator1", "validator2"]

        expected_results = [
            ("validator1", True, "Validation passed"),
            ("validator2", False, "Validation failed"),
        ]
        mock_execution_engine = MockExecutionEngine.return_value
        mock_execution_engine.execute.return_value = expected_results

        mock_result_aggregator = MockResultAggregator.return_value
        mock_result_aggregator.generate_summary.return_value = "Summary"

        main()

        mock_parse_args.assert_called_once()
        mock_rule_parser.parse.assert_called_once()

        MockExecutionEngine.assert_called_once_with(["validator1", "validator2"])
        mock_execution_engine.execute.assert_called_once()

        for result in expected_results:
            mock_result_aggregator.add_result.assert_any_call(*result)

        mock_result_aggregator.generate_summary.assert_called_once()

        self.assertEqual(
            mock_result_aggregator.generate_summary.return_value, "Summary"
        )

if __name__ == "__main__":
    unittest.main()
