import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies before importing ColorExtractor
sys.modules["requests"] = MagicMock()
sys.modules["colorthief"] = MagicMock()
sys.modules["PIL"] = MagicMock()

from color_extractor import ColorExtractor

class TestColorExtractor(unittest.TestCase):
    def setUp(self):
        # We need an instance of ColorExtractor.
        # It requires an input_source, which it uses to create a temp dir.
        self.extractor = ColorExtractor("dummy_source")

    def test_get_rgb_str_standard(self):
        color = (100, 150, 200)
        expected = "100,150,200"
        self.assertEqual(self.extractor.get_rgb_str(color), expected)

    def test_get_rgb_str_boundaries(self):
        # Test lower boundary
        self.assertEqual(self.extractor.get_rgb_str((0, 0, 0)), "0,0,0")
        # Test upper boundary
        self.assertEqual(self.extractor.get_rgb_str((255, 255, 255)), "255,255,255")

    def test_get_rgb_str_list_input(self):
        color = [10, 20, 30]
        expected = "10,20,30"
        self.assertEqual(self.extractor.get_rgb_str(color), expected)

if __name__ == "__main__":
    unittest.main()
