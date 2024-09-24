import os
import argparse
import logging
from rule_parser import RuleParser
from execution_engine import ExecutionEngine
from result_aggregator import ResultAggregator


def main():
    parser = argparse.ArgumentParser(
        description="Validate the repo with the standards of https://azure.github.io/ai-apps/."
    )
    parser.add_argument("repo_path", type=str, help="The path to the repo to validate.")
    parser.add_argument(
        "--validate_paths",
        type=str,
        help="A comma-separated list of the file or folder path to check for existence.",
    )
    parser.add_argument(
        "--validate_azd",
        action="store_true",
        help="Whether to validate the deployment functionality with Azd CLI.",
    )
    parser.add_argument(
        "--topics", type=str, help="A comma-separated list of the actual topics."
    )
    parser.add_argument(
        "--expected_topics",
        type=str,
        help="A comma-separated list of topics to check for.",
    )
    parser.add_argument(
        "--msdoresult",
        type=str,
        help="The output file path of microsoft security devops analysis.",
    )
    parser.add_argument("--output", type=str, help="The output file path.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="%(message)s", level=log_level)

    logging.debug(
        f"Repo path: {args.repo_path} validate_paths: {args.validate_paths} validate_azd: {args.validate_azd} debug: {args.debug} topics: {args.topics} expected_topics: {args.expected_topics} msdo: {args.msdoresult} output: {args.output}"
    )

    # Parse rules and generate validators
    rules_file_path = os.path.join(os.path.dirname(__file__), "rules.json")
    parser = RuleParser(rules_file_path, args)
    validators = parser.parse()

    # Execute validators
    engine = ExecutionEngine(validators)
    results = engine.execute()

    # Aggregate results
    aggregator = ResultAggregator()
    for result in results:
        aggregator.add_result(result[0], result[1], result[2])

    summary = aggregator.generate_summary()

    # Output the summary
    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(summary)


if __name__ == "__main__":
    main()
