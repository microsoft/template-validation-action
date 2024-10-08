import unittest
from validator.file_validator import FileValidator
from constants import ItemResultFormat, Signs
from level import Level


def test_file_validator_file_found_exist():
    validator = FileValidator(
        "TestCatalog", "LICENSE", [""], "test/data", ["."], None, False
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")


def test_file_validator_file_found_case_non_sensitive():
    validator = FileValidator(
        "TestCatalog", "license", [""], "test/data", ["."], None, False
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="license File")


def test_file_validator_file_not_found_case_sensitive():
    validator = FileValidator(
        "TestCatalog", "license", [""], "test/data", ["."], None, True
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="license File",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.BLOCK, message="license file is missing."
        ),
    )


def test_file_validator_file_found_case_sensitive():
    validator = FileValidator(
        "TestCatalog", "LICENSE", [""], "test/data", ["."], None, True
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")


def test_file_validator_file_found_multiple_extension():
    validator = FileValidator(
        "TestCatalog", "LICENSE", [".md", ".txt", ""], "test/data", ["."], None, False
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="LICENSE.md File")


def test_file_validator_file_not_found_multiple_extension():
    validator = FileValidator(
        "TestCatalog", "LICENSE", [".md", ".txt"], "test/data", ["."], None, False
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="LICENSE.md File",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.BLOCK, message="LICENSE.md file is missing."
        ),
    )


def test_file_validator_file_found_in_subfolder():
    validator = FileValidator(
        "TestCatalog", "LICENSE", [""], "test", ["data"], None, False
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")


def test_file_validator_file_not_found_in_subfolder():
    validator = FileValidator(
        "TestCatalog", "license", [""], "test", ["data"], None, True
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="license File",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.BLOCK, message="license file is missing."
        ),
    )


def test_file_validator_H2Tag_found_case_non_sensitive():
    validator = FileValidator(
        "TestCatalog", "README", [".md"], "test/data", ["."], ["## Test h2"], False
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="README.md File")


def test_file_validator_H2Tag_found_case_sensitive():
    validator = FileValidator(
        "TestCatalog", "README", [".md"], "test/data", ["."], ["## Test H2"], True
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="README.md File")


def test_file_validator_H2Tag_not_found_case_non_sensitive():
    validator = FileValidator(
        "TestCatalog",
        "README",
        [".md"],
        "test/data",
        ["."],
        ["## Test h2 Not Found"],
        False,
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="README.md File",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.BLOCK,
            message="## Test h2 Not Found is missing in README.md.",
        ),
    )


def test_file_validator_H2Tag_not_found_case_sensitive():
    validator = FileValidator(
        "TestCatalog",
        "README",
        [".md"],
        "test/data",
        ["."],
        ["## Test H2 Not Found"],
        True,
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="README.md File",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.BLOCK,
            message="## Test H2 Not Found is missing in README.md.",
        ),
    )


def test_file_validator_folder_allowed_and_exists():
    validator = FileValidator(
        "TestCatalog",
        "ISSUE_TEMPLATE",
        ["md"],
        "test/data",
        ["."],
        None,
        False,
        Level.MODERATE,
        True,
    )
    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="ISSUE_TEMPLATE Folder")


def test_file_validator_folder_allowed_but_not_exists():
    validator = FileValidator(
        "TestCatalog",
        "NON_EXISTENT_FOLDER",
        [".md"],
        "test/data",
        ["."],
        None,
        False,
        Level.MODERATE,
        True,
    )
    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        message="NON_EXISTENT_FOLDER.md File or NON_EXISTENT_FOLDER Folder",
        detail_messages=ItemResultFormat.SUBITEM.format(
            sign=Signs.WARNING,
            message="NON_EXISTENT_FOLDER.md file or NON_EXISTENT_FOLDER folder is missing.",
        ),
    )


if __name__ == "__main__":
    unittest.main()
