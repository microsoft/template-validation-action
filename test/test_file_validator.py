import pytest
import os
import sys
from validator.file_validator import FileValidtor
from constants import ItemResultFormat


def test_file_validator_file_found_exist():
    validator = FileValidtor("TestCatalog", False, "LICENSE", [""], "test/data", [""], False, None)
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")

def test_file_validator_file_found_case_non_sensitive():
    validator = FileValidtor("TestCatalog", False, "license", [""], "test/data", [""], False, None)
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="license File")

def test_file_validator_file_not_found_case_sensitive():
    validator = FileValidtor("TestCatalog", False, "license", [""], "test/data", [""], True, None)
    result, message = validator.validate()
    assert result == False
    assert message == ItemResultFormat.FAIL.format(message="license File", detail_messages="- Error: license file is missing.")


def test_file_validator_file_found_case_sensitive():
    validator = FileValidtor("TestCatalog", False, "LICENSE", [""], "test/data", [""], True, None)
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")

def test_file_validator_file_found_mutiple_extension():
    validator = FileValidtor("TestCatalog", False, "LICENSE", ["md", "txt", ""], "test/data", [""], False, None)
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="LICENSE.md File")

def test_file_validator_file_not_found_mutiple_extension():
    validator = FileValidtor("TestCatalog", False, "LICENSE", ["md", "txt"], "test/data", [""], False, None)
    result, message = validator.validate()
    assert result == False
    assert message == ItemResultFormat.FAIL.format(message="LICENSE.md File", detail_messages="- Error: LICENSE.md file is missing.")

def test_file_validator_file_found_in_subfolder():
    validator = FileValidtor("TestCatalog", False, "LICENSE", [""], "test", ["data"], False, None)
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="LICENSE File")

def test_file_validator_file_not_found_in_subfolder():
    validator = FileValidtor("TestCatalog", False, "license", [""], "test", ["data"], True, None)
    result, message = validator.validate()
    assert result == False
    assert message == ItemResultFormat.FAIL.format(message="license File", detail_messages="- Error: license file is missing.")

def test_file_validator_H2Tag_found():
    validator = FileValidtor("TestCatalog", False, "README", ["md"], "test/data", [""], True, ["## Test H2"])
    result, message = validator.validate()
    assert result == True
    assert message == ItemResultFormat.PASS.format(message="README.md File")

def test_file_validator_H2Tag_not_found():
    validator = FileValidtor("TestCatalog", False, "README", ["md"], "test/data", [""], True, ["## Test H2 Not Found"])
    result, message = validator.validate()
    assert result == False
    assert message == ItemResultFormat.FAIL.format(message="README.md File", detail_messages="- Error: ## Test H2 Not Found is missing in README.md.")