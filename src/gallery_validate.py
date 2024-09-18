import os
import argparse
import subprocess
import logging
import yaml
from sarif import loader
from validator.file_validator import *
from validator.azd_validator import *
from constants import *
from utils import indent

root_folder = "."
github_folder = ".github"
workflows_folder = "workflows"
markdown_file_extension = "md"
yaml_file_extensions = ["yaml", "yml"]
azure_dev_workflow_file = "azure-dev"
code_of_conduct_file = "CODE_OF_CONDUCT"
contributing_file = "CONTRIBUTING"
issue_template_file = "ISSUE_TEMPLATE"
license_file = "LICENSE"
readme_file = "README"
security_file = "SECURITY"
infra_yaml_file = "azure"

infra_folder_path = "infra"
devcontainer_folder_path = ".devcontainer"
cicd_workflow_folder_path = ".github/workflows"

# The H2 tag list to be checked in README.md
readme_h2_tags = [
    "## Features",
    "## Getting Started",
    "## Guidance",
    "## Resources"
]

severity_error = "error"
severity_error_exceptions = ["AZR-000283"]

expected_topics = ["azd-templates", "ai-azd-templates"]

security_actions = ['microsoft/security-devops-action',
                    'github/codeql-action/upload-sarif']


def check_msdo_result(msdo_result_file):
    logging.debug(f"Checking for msdo result: {msdo_result_file}...")
    result = True
    message = ""

    if msdo_result_file is not None and os.path.isfile(msdo_result_file):
        subMessages = []
        sarif_data = loader.load_sarif_file(msdo_result_file)
        report = sarif_data.get_records_grouped_by_severity()
        for severity in report:
            items_of_severity = report.get(severity, [])
            for item in items_of_severity:
                if severity == severity_error and item['Code'] not in severity_error_exceptions:
                    result = result and False
                    subMessages.append(
                        ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"{severity}: {item['Code']} - {indent(item['Description'], 4)}"))
                elif item['Code'] in severity_error_exceptions:
                    subMessages.append(
                        ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"warning: {item['Code']} - {indent(item['Description'], 4)}"))
                else:
                    subMessages.append(
                        ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"{severity}: {item['Code']} - {indent(item['Description'], 4)}"))

        if result and len(subMessages) == 0:
            message = ItemResultFormat.PASS.format(
                message="Security scan")
        elif len(subMessages) > 0:
            message = ItemResultFormat.WARNING.format(
                message="Security scan", detail_messages=ItemResultFormat.DETAILS.format(message=line_delimiter.join(subMessages)))
        else:
            message = ItemResultFormat.FAIL.format(
                message="Security scan", detail_messages=ItemResultFormat.DETAILS.format(message=line_delimiter.join(subMessages)))

    else:
        result = False
        message = ItemResultFormat.WARNING.format(
            message="Security scan", detail_messages=ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"Error: Scan result is missing."))

    return result, message


def check_for_actions_in_workflow_file(repo_path, file_name, actions):
    logging.debug(f"Checking for steps in {file_name}...")
    result = True
    messages = []

    with open(os.path.join(repo_path, file_name), 'r') as file:
        content = yaml.safe_load(file)

    def check_steps(steps, action):
        for step in steps:
            if isinstance(step, dict) and 'uses' in step:
                used_action = step['uses'].split('@')[0]
                if used_action == action:
                    return True
        return False

    if 'jobs' in content:
        for job in content['jobs'].values():
            if 'steps' in job:
                for action in actions:
                    if not check_steps(job['steps'], action):
                        result = result and False
                        messages.append(
                            ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"Error: {action} is missing in {file_name}."))
    return result, line_delimiter.join(messages)


def find_cicd_workflow_file(repo_path):
    # return all yaml files in the /github/workflows folder as a list
    result, message = check_folder_existence(
        repo_path, cicd_workflow_folder_path)
    list = []
    if result:
        list = [f for f in os.listdir(os.path.join(
            repo_path, cicd_workflow_folder_path)) if f.endswith('.yml')]

    logging.debug(f"Found {len(list)} workflow files in {repo_path}.")
    return list


def check_topic_existence(actual_topics, expected_topics):
    logging.debug(f"Checking for topics...")
    messages = []
    result = True

    subMessages = []
    if actual_topics is None:
        result = False
        subMessages.append(ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"Error: topics string is NULL."))
    else:
        actual_topics_list = actual_topics.replace('"', '').split(",")
        for topic in expected_topics:
            if topic not in actual_topics_list:
                result = result and False
                subMessages.append(ItemResultFormat.SUBITEM.format(sign=Signs.WARNING, message=f"Error: {topic} is missing in topics."))

    if result:
        messages.append(ItemResultFormat.PASS.format(
            message=f"Topics on repo contains {expected_topics}"))
    else:
        messages.append(ItemResultFormat.WARNING.format(
            message=f"Topics on repo contains {expected_topics}", detail_messages=line_delimiter.join(subMessages)))

    return result, line_delimiter.join(messages)


def check_folder_existence(repo_path, folder_name):
    logging.debug(f"Checking for {folder_name}...")
    messages = []
    if not os.path.isdir(os.path.join(repo_path, folder_name)):
        messages.append(ItemResultFormat.FAIL.format(
            message=f"{folder_name} Folder", detail_messages=ItemResultFormat.SUBITEM.format(sign=Signs.BLOCK, message=f"Error: {folder_name} folder is missing.")))
        return False, line_delimiter.join(messages)
    else:
        messages.append(ItemResultFormat.PASS.format(
            message=f"{folder_name} Folder"))
        return True, line_delimiter.join(messages)


def check_repository_management(repo_path, topics):

    repository_management_validators = [
        FileValidator("repository_management", readme_file, [markdown_file_extension], repo_path, [""], readme_h2_tags),
        FileValidator("repository_management", license_file, [markdown_file_extension, ""], repo_path),
        FileValidator("repository_management", security_file, [markdown_file_extension], repo_path, ["", github_folder]),
        FileValidator("repository_management", code_of_conduct_file, [markdown_file_extension], repo_path, [github_folder, ""]),
        FileValidator("repository_management", contributing_file, [markdown_file_extension], repo_path, ["", github_folder]),
        FileValidator("repository_management", issue_template_file, [markdown_file_extension, ""], repo_path, [github_folder], None, False, False, True)
    ]

    final_result = True
    final_messages = [""]
    final_messages.append("## Repository Management:")

    for validator in repository_management_validators:
        result, message = validator.validate()
        final_result = final_result and result
        final_messages.append(message)

    # sample topics: "azd-templates,azure"
    result, message = check_topic_existence(topics, expected_topics)
    # Missing topics does not block the validation
    # final_result = final_result and result
    final_messages.append(message)

    return final_result, line_delimiter.join(final_messages)


def check_source_code_structure(repo_path, infra_yaml_path):
    source_code_structure_validators = [
        FileValidator("source_code_structure", azure_dev_workflow_file, yaml_file_extensions, repo_path, [
            os.path.join(github_folder, workflows_folder)]),
        FileValidator("source_code_structure", infra_yaml_file, yaml_file_extensions, infra_yaml_path),
    ]

    source_code_structure_folders = [
        os.path.join(infra_yaml_path, infra_folder_path),
        devcontainer_folder_path
    ]

    final_result = True
    final_messages = [""]
    final_messages.append("## Source code structure and conventions:")

    for validator in source_code_structure_validators:
        result, message = validator.validate()
        final_result = final_result and result
        final_messages.append(message)

    for file_name in source_code_structure_folders:
        result, message = check_folder_existence(repo_path, file_name)
        final_result = final_result and result
        final_messages.append(message)

    return final_result, line_delimiter.join(final_messages)


def check_functional_requirements(infra_yaml_paths, check_azd_up, check_azd_down):
    final_result = True
    final_messages = [""]
    final_messages.append("## Functional Requirements:")

    # check for the existence of the files
    for infra_yaml_path in infra_yaml_paths:
        azd_validator = AzdValidator("AzdCatalog", infra_yaml_path, check_azd_up, check_azd_down)
        result, message = azd_validator.validate()
        final_result = final_result and result
        final_messages.append(message)

    return final_result, line_delimiter.join(final_messages)


def check_security_requirements(repo_path, msdo_result_file):
    final_result = True
    final_messages = [""]
    final_messages.append("## Security Requirements (only for production):")
    final_messages.append("The following recommendations should be considered before productionizing this application.")

    # check for security action
    msdo_integrated_result = False
    msdo_integrated_messages = []
    msdo_integrated_messages.append(
        "Not found security check related actions in the CI/CD pipeline.")
    for file in find_cicd_workflow_file(repo_path):
        result, message = check_for_actions_in_workflow_file(
            repo_path, os.path.join(cicd_workflow_folder_path, file), security_actions)
        msdo_integrated_result = msdo_integrated_result or result
        msdo_integrated_messages.append(message)

    # MSDO integration is not blocking the validation
    # final_result = final_result and msdo_integrated_result
    if msdo_integrated_result:
        final_messages.append(ItemResultFormat.PASS.format(
            message="microsoft/security-devops-action is integrated to the CI/CD pipeline"))
    else:
        final_messages.append(ItemResultFormat.WARNING.format(message="microsoft/security-devops-action is integrated to the CI/CD pipeline",
                                                              detail_messages=ItemResultFormat.DETAILS.format(message=line_delimiter.join(msdo_integrated_messages))))

    result, message = check_msdo_result(msdo_result_file)
    # MSDO result is not blocking the validation
    # final_result = final_result and result
    final_messages.append(message)

    return final_result, line_delimiter.join(final_messages)


def find_infra_yaml_path(repo_path):
    infra_yaml_paths = []
    for root, dirs, files in os.walk(repo_path):
        for extension in yaml_file_extensions:
            if infra_yaml_file + "." + extension in files:
                infra_yaml_paths.append(root)
    return infra_yaml_paths if len(infra_yaml_paths) > 0 else [repo_path]


def internal_validator(repo_path, check_azd_up, check_azd_down, topics):
    if not os.path.isdir(repo_path):
        raise Exception(f"Error: The path {repo_path} is not a valid directory.")
        return

    final_result = True
    final_message = []
    infra_yaml_paths = find_infra_yaml_path(repo_path)

    result, message = check_repository_management(repo_path, topics)
    final_result = final_result and result
    final_message.append(message)

    result, message = check_source_code_structure(repo_path, infra_yaml_paths[0])
    final_result = final_result and result
    final_message.append(message)

    result, message = check_functional_requirements(
        infra_yaml_paths, check_azd_up, check_azd_down)
    final_result = final_result and result
    final_message.append(message)

    return final_result, line_delimiter.join(final_message)


def main():
    parser = argparse.ArgumentParser(
        description="Validate the repo with the standards of https://azure.github.io/ai-apps/.")
    parser.add_argument('repo_path', type=str,
                        help="The path to the repo to validate.")
    parser.add_argument('--azdup', action='store_true',
                        help="Check infra code with azd up.")
    parser.add_argument('--azddown', action='store_true',
                        help="Check infra code with azd up.")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging.")
    parser.add_argument('--topics', type=str, help="The topics to be checked.")
    parser.add_argument('--msdoresult', type=str,
                        help="The output file path of microsoft security devops analysis.")
    parser.add_argument('--output', type=str, help="The output file path.")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(message)s', level=log_level)

    logging.debug(
        f"Repo path: {args.repo_path} azdup: {args.azdup} azddown: {args.azddown} debug: {args.debug} topics: {args.topics} msdo: {args.msdoresult} output: {args.output}")

    result, message = internal_validator(
        args.repo_path, args.azdup, args.azddown, args.topics)

    if result:
        message = final_result_format.format(result="PASSED", message=message)
    else:
        message = final_result_format.format(result="FAILED", message=message)

    logging.warning(message)

    if args.output:
        with open(args.output, 'w') as file:
            file.write(message)
        file.close()

    # if not result:
    #    raise Exception(f"Validation failed as following: \n {message}")


if __name__ == "__main__":
    main()
