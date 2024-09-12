import os
import argparse
import logging
from parse_rules import RuleParse
from execution_engine import ExecutionEngine
from result_aggregator import ResultAggregator


def main():
    parser = argparse.ArgumentParser(
        description="Validate the repo with the standards of https://azure.github.io/ai-apps/."
    )
    parser.add_argument("repo_path", type=str, help="The path to the repo to validate.")
    parser.add_argument(
        "--azdup", action="store_true", help="Check infra code with azd up."
    )
    parser.add_argument(
        "--azddown", action="store_true", help="Check infra code with azd down."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("--topics", type=str, help="The topics to be checked.")
    parser.add_argument(
        "--msdoresult",
        type=str,
        help="The output file path of microsoft security devops analysis.",
    )
    parser.add_argument("--output", type=str, help="The output file path.")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="%(message)s", level=log_level)

    logging.debug(
        f"Repo path: {args.repo_path} azdup: {args.azdup} azddown: {args.azddown} debug: {args.debug} topics: {args.topics} msdo: {args.msdoresult} output: {args.output}"
    )

    # Parse rules and generate validators
    rules_file_path = os.path.join(os.path.dirname(__file__), "rules.json")
    parser = RuleParse(rules_file_path, args)
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
    else:
        print(summary)


if __name__ == "__main__":
    main()
