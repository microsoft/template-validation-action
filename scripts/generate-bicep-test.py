import os
import re
import glob


def generate_test_bicep(main_bicep_path):
    # Read the main.bicep file
    with open(main_bicep_path, "r") as file:
        main_bicep_content = file.read()

    # Find the targetScope
    target_scope_pattern = re.compile(r"targetScope\s*=\s*\'(\w+)\'")
    target_scope_match = target_scope_pattern.search(main_bicep_content)
    target_scope = target_scope_match.group(1) if target_scope_match else "subscription"

    # Find all parameter definitions and allowed values
    param_pattern = re.compile(r"param\s+(\w+)\s+(\w+)\s*(?!\s*=\s*'.*')(\n|\/|$)")
    allowed_pattern = re.compile(
        r"@allowed\(\[\s*([^\]]+)\s*\]\)(?:\s*@\w+\([^\)]*\))*\s*param\s+(\w+)\s+(\w+)"
    )

    params = param_pattern.findall(main_bicep_content)
    allowed_params = allowed_pattern.findall(main_bicep_content)

    # Generate the main.test.bicep content
    test_bicep_content = f"""// This file is for doing static analysis and contains sensible defaults
// for PSRule to minimise false-positives and provide the best results.
// This file is not intended to be used as a runtime configuration file.

targetScope = '{target_scope}'

module test 'main.bicep' = {{
  name: 'test'
  params: {{
"""

    # Add parameters to the test file content
    for param_name, param_type, _ in params:
        # Check if the parameter has allowed values
        allowed_value = None
        for allowed_values, allowed_param_name, allowed_param_type in allowed_params:
            if param_name == allowed_param_name:
                allowed_value = (
                    allowed_values.split()[-1].split(",")[0].strip(" ").strip("'")
                )
                break

        if allowed_value:
            test_bicep_content += f"    {param_name}: '{allowed_value}'\n"
        elif param_type == "string":
            test_bicep_content += f"    {param_name}: 'test'\n"
        elif param_type == "int":
            test_bicep_content += f"    {param_name}: 1\n"
        elif param_type == "bool":
            test_bicep_content += f"    {param_name}: true\n"
        else:
            test_bicep_content += f"    {param_name}: null\n"

    # Close the params block and module block
    test_bicep_content += """  }
}
"""

    # Write the generated content to main.test.bicep
    test_bicep_path = os.path.join(os.path.dirname(main_bicep_path), "main.test.bicep")
    with open(test_bicep_path, "w") as file:
        file.write(test_bicep_content)

    print(f"{test_bicep_path} file generated successfully.")


def main():
    # Recursively find all main.bicep files in the current directory
    for main_bicep_path in glob.glob("**/main.bicep", recursive=True):
        generate_test_bicep(main_bicep_path)


if __name__ == "__main__":
    print("Generating test files...")
    main()
