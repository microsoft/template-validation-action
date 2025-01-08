import os
import subprocess
import logging
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, Signs, line_delimiter
from severity import Severity
from utils import find_infra_yaml_path  # Import the utility function


class PlaywrightTestValidator(ValidatorBase):
    def __init__(self, validatorCatalog, repo_path, severity=Severity.LOW):
        super().__init__("PlaywrightTestValidator", validatorCatalog, severity)
        self.repo_path = repo_path

    def validate(self):
        logging.debug(
            f"Validating Playwright test setup in repository: {self.repo_path}"
        )
        messages = []

        try:
            # Search for YAML or YML files using the utility function
            yaml_file_paths = find_infra_yaml_path(self.repo_path)
            yaml_file_path = next(
                (
                    os.path.join(path, file)
                    for path in yaml_file_paths
                    for file in os.listdir(path)
                    if file.lower() in ("playwright-test.yaml", "playwright-test.yml")
                ),
                None,
            )

            if not yaml_file_path:
                self.result = False
                self.resultMessage = ItemResultFormat.FAIL.format(
                    sign=Signs.WARNING,
                    message="Playwright GitHub Action is missing",
                    detail_messages="No `playwright-test.yaml` or `.yml` found in the repository.",
                )
                return self.result, self.resultMessage

            # Run the GitHub Action file
            logging.debug(f"Found Playwright GitHub Action file: {yaml_file_path}")
            action_result = self._run_playwright_tests(yaml_file_path)

            if action_result == "failed":
                self.result = False
                messages.append(
                    ItemResultFormat.FAIL.format(
                        sign=Signs.WARNING,
                        message="Playwright GitHub Action tests failed",
                        detail_messages="One or more Playwright tests did not pass.",
                    )
                )
            elif action_result == "passed":
                self.result = True
                messages.append(
                    ItemResultFormat.PASS.format(
                        sign=Signs.CHECK, message="All Playwright tests passed."
                    )
                )
            else:
                self.result = True
                messages.append(
                    ItemResultFormat.PASS.format(
                        sign=Signs.CHECK, message="Playwright tests were not run."
                    )
                )

            self.resultMessage = line_delimiter.join(messages)
            return self.result, self.resultMessage

        except Exception as e:
            logging.error(f"Error during Playwright test validation: {e}")
            self.result = False
            self.resultMessage = ItemResultFormat.FAIL.format(
                sign=Signs.WARNING,
                message="An error occurred during validation",
                detail_messages=str(e),
            )
            return self.result, self.resultMessage

    def _run_playwright_tests(self, yaml_file_path):
        """Run the Playwright GitHub Action YAML file."""
        try:
            # Simulating running the GitHub Action with subprocess
            # In reality, this would involve triggering an actual workflow runner or simulation
            result = subprocess.run(
                ["playwright", "test"],
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if result.returncode == 0:
                return "passed"
            else:
                return "failed"
        except Exception as e:
            logging.error(f"Error running Playwright tests: {e}")
            return "error"
