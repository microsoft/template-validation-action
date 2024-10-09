import unittest
from severity import Severity


class TestSeverity(unittest.TestCase):
    def test_validate_low_string(self):
        self.assertEqual(Severity.validate("LOW"), Severity.LOW)

    def test_validate_moderate_string(self):
        self.assertEqual(Severity.validate("MODERATE"), Severity.MODERATE)

    def test_validate_high_string(self):
        self.assertEqual(Severity.validate("HIGH"), Severity.HIGH)

    def test_validate_low(self):
        self.assertEqual(Severity.validate(Severity.LOW), Severity.LOW)

    def test_validate_moderate(self):
        self.assertEqual(Severity.validate(Severity.MODERATE), Severity.MODERATE)

    def test_validate_high(self):
        self.assertEqual(Severity.validate(Severity.HIGH), Severity.HIGH)

    def test_validate_invalid(self):
        self.assertEqual(Severity.validate(999), Severity.MODERATE)

    def test_lt_comparison(self):
        self.assertTrue(Severity.LOW < Severity.MODERATE)
        self.assertTrue(Severity.MODERATE < Severity.HIGH)
        self.assertFalse(Severity.HIGH < Severity.MODERATE)
        self.assertFalse(Severity.MODERATE < Severity.LOW)

    def test_gt_comparison(self):
        self.assertTrue(Severity.HIGH > Severity.MODERATE)
        self.assertTrue(Severity.MODERATE > Severity.LOW)
        self.assertFalse(Severity.LOW > Severity.MODERATE)
        self.assertFalse(Severity.MODERATE > Severity.HIGH)

    def test_isBlocker(self):
        self.assertTrue(Severity.isBlocker(Severity.HIGH))
        self.assertFalse(Severity.isBlocker(Severity.MODERATE))
        self.assertFalse(Severity.isBlocker(Severity.LOW))


if __name__ == "__main__":
    unittest.main()
