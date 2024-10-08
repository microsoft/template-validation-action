import unittest
from level import Level

class TestLevel(unittest.TestCase):

    def test_validate_low(self):
        self.assertEqual(Level.validate(Level.LOW), Level.LOW)

    def test_validate_moderate(self):
        self.assertEqual(Level.validate(Level.MODERATE), Level.MODERATE)

    def test_validate_high(self):
        self.assertEqual(Level.validate(Level.HIGH), Level.HIGH)

    def test_validate_invalid(self):
        self.assertEqual(Level.validate(999), Level.MODERATE)

    def test_lt_comparison(self):
        self.assertTrue(Level.LOW < Level.MODERATE)
        self.assertTrue(Level.MODERATE < Level.HIGH)
        self.assertFalse(Level.HIGH < Level.MODERATE)
        self.assertFalse(Level.MODERATE < Level.LOW)
    
    def test_gt_comparison(self):
        self.assertTrue(Level.HIGH > Level.MODERATE)
        self.assertTrue(Level.MODERATE > Level.LOW)
        self.assertFalse(Level.LOW > Level.MODERATE)
        self.assertFalse(Level.MODERATE > Level.HIGH)

    def test_isBlocker(self):
        self.assertTrue(Level.isBlocker(Level.HIGH))
        self.assertFalse(Level.isBlocker(Level.MODERATE))
        self.assertFalse(Level.isBlocker(Level.LOW))

if __name__ == '__main__':
    unittest.main()
