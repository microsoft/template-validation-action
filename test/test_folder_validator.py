import unittest
from validator.folder_validator import FolderValidator
from constants import ItemResultFormat, Signs

class TestFolderValidator(unittest.TestCase):

    def test_folder_validator_folder_exists(self):
        validator = FolderValidator("TestCatalog", "ISSUE_TEMPLATE", ["test/data"])
        result, message = validator.validate()
        self.assertTrue(result)
        self.assertEqual(message, ItemResultFormat.PASS.format(message="ISSUE_TEMPLATE Folder found in test/data"))

    def test_folder_validator_folder_not_exists(self):
        validator = FolderValidator("TestCatalog", "non_existent_folder", ["test/data"])
        result, message = validator.validate()
        self.assertFalse(result)
        self.assertEqual(message, ItemResultFormat.FAIL.format(
            message="non_existent_folder Folder", detail_messages=ItemResultFormat.SUBITEM.format(sign=Signs.BLOCK, message="Error: non_existent_folder folder is missing in all candidate folders.")))

if __name__ == "__main__":
    unittest.main()
