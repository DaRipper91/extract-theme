import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Mock dependencies before importing the module
sys.modules['requests'] = MagicMock()
sys.modules['colorthief'] = MagicMock()
sys.modules['PIL'] = MagicMock()

import color_extractor

class TestColorExtractor(unittest.TestCase):
    def setUp(self):
        self.input_source = "test_image.png"

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_configs_default_path(self, mock_file, mock_makedirs, mock_exists):
        extractor = color_extractor.ColorExtractor(self.input_source)
        extractor.palette = [(0,0,0)] * 20
        extractor.generate_configs()

        expected_dir = os.path.expanduser("~/ops/color-tools/output")
        mock_makedirs.assert_called_with(expected_dir, exist_ok=True)
        mock_file.assert_any_call(os.path.join(expected_dir, "alacritty_theme.toml"), 'w')

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_configs_custom_path(self, mock_file, mock_makedirs, mock_exists):
        custom_dir = "/tmp/custom_output"
        extractor = color_extractor.ColorExtractor(self.input_source, output_dir=custom_dir)
        extractor.palette = [(0,0,0)] * 20
        extractor.generate_configs()

        mock_makedirs.assert_called_with(custom_dir, exist_ok=True)
        mock_file.assert_any_call(os.path.join(custom_dir, "alacritty_theme.toml"), 'w')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_vibrant_palette_default_path(self, mock_file, mock_exists):
        extractor = color_extractor.ColorExtractor(self.input_source)
        extractor.palette = [(0,0,0)] * 20
        mock_exists.return_value = True

        extractor.update_vibrant_palette()

        expected_path = os.path.expanduser("~/Colors/vibrant_palette.md")
        mock_file.assert_called_with(expected_path, 'a')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_vibrant_palette_custom_path(self, mock_file, mock_exists):
        custom_palette = "/tmp/my_palette.md"
        extractor = color_extractor.ColorExtractor(self.input_source, palette_path=custom_palette)
        extractor.palette = [(0,0,0)] * 20
        mock_exists.return_value = True

        extractor.update_vibrant_palette()

        mock_file.assert_called_with(custom_palette, 'a')

    @patch('color_extractor.argparse.ArgumentParser.parse_args')
    @patch('color_extractor.ColorExtractor')
    def test_main_no_update(self, mock_extractor_class, mock_parse_args):
        # Setup
        mock_args = MagicMock()
        mock_args.input = "test.png"
        mock_args.output_dir = "/tmp/out"
        mock_args.palette_file = "/tmp/pal"
        mock_args.no_update = True
        mock_parse_args.return_value = mock_args

        mock_extractor_instance = mock_extractor_class.return_value

        # Run
        color_extractor.main()

        # Verify
        mock_extractor_class.assert_called_with("test.png", output_dir="/tmp/out", palette_path="/tmp/pal")
        mock_extractor_instance.update_vibrant_palette.assert_not_called()

    @patch('color_extractor.argparse.ArgumentParser.parse_args')
    @patch('color_extractor.ColorExtractor')
    def test_main_with_update(self, mock_extractor_class, mock_parse_args):
        # Setup
        mock_args = MagicMock()
        mock_args.input = "test.png"
        mock_args.output_dir = "/tmp/out"
        mock_args.palette_file = "/tmp/pal"
        mock_args.no_update = False
        mock_parse_args.return_value = mock_args

        mock_extractor_instance = mock_extractor_class.return_value

        # Run
        color_extractor.main()

        # Verify
        mock_extractor_instance.update_vibrant_palette.assert_called_once()

if __name__ == '__main__':
    unittest.main()
