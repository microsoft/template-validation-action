import unittest
from result_aggregator import ResultAggregator
from level import Level


class TestResultAggregator(unittest.TestCase):
    def test_add_result_and_generate_summary(self):
        aggregator = ResultAggregator()

        # Add mock results
        aggregator.add_result(
            "repository_management_readme", Level.MODERATE, True, "- [x] README.md File"
        )
        aggregator.add_result(
            "repository_management_license", Level.MODERATE, True, "- [x] LICENSE.md File"
        )
        aggregator.add_result(
            "repository_management_security", Level.MODERATE, False, "- :warning: SECURITY.md File"
        )
        aggregator.add_result(
            "source_code_structure_azure_dev", Level.MODERATE, True, "- [x] azure-dev.yaml File"
        )
        aggregator.add_result("functional_requirements_azd_up", Level.MODERATE, True, "- [x] azd up")
        aggregator.add_result(
            "security_requirements_msdo", Level.MODERATE, False, "- :warning: MSDO validation failed"
        )

        summary = aggregator.generate_summary()

        expected_summary = """# AI Gallery Standard Validation: NON-CONFORMING, Severity: Moderate

## Repository Management:
- [x] README.md File
- [x] LICENSE.md File
- :warning: SECURITY.md File

## Source code structure and conventions:
- [x] azure-dev.yaml File

## Functional Requirements:
- [x] azd up

## Security Requirements:
- :warning: MSDO validation failed"""

        self.assertEqual(summary, expected_summary)


if __name__ == "__main__":
    unittest.main()
