#!/usr/bin/env python3
import os
import sys
import tempfile
import argparse
import requests
import shutil
from colorthief import ColorThief

class ColorExtractor:
    def __init__(self, input_source, output_dir=None, palette_path=None):
        self.input_source = input_source
        self.output_dir = os.path.expanduser(output_dir or "~/ops/color-tools/output")
        self.palette_path = os.path.expanduser(palette_path or "~/Colors/vibrant_palette.md")
        self.temp_dir = tempfile.mkdtemp()
        self.image_path = None
        self.palette = []

    def prepare_image(self):
        if self.input_source.startswith(('http://', 'https://')):
            response = requests.get(self.input_source, timeout=10)
            img_path = os.path.join(self.temp_dir, "downloaded_image")
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.image_path = img_path
        else:
            self.image_path = os.path.abspath(self.input_source)

    def extract_colors(self):
        color_thief = ColorThief(self.image_path)
        # Extract 16 colors for a full terminal palette
        self.palette = color_thief.get_palette(color_count=16, quality=1)

    def get_hex_0x(self, rgb):
        return f"0x{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def get_rgb_str(self, rgb):
        return f"{rgb[0]},{rgb[1]},{rgb[2]}"

    def generate_configs(self):
        if not self.palette:
            return

        bg = self.palette[0]
        fg = self.palette[-1]
        colors_16 = self.palette[:16]

        if len(colors_16) < 16:
            # Fallback if too few colors
            colors_16 = (colors_16 * 2)[:16]

        os.makedirs(self.output_dir, exist_ok=True)

        # 1. Alacritty
        alacritty_path = os.path.join(self.output_dir, "alacritty_theme.toml")
        with open(alacritty_path, 'w') as f:
            f.write("[colors.primary]\n")
            f.write(f'background = "{self.get_hex_0x(bg)}"\n')
            f.write(f'foreground = "{self.get_hex_0x(fg)}"\n')
            f.write("\n[colors.normal]\n")
            for i, c in enumerate(colors_16[:8]):
                names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
                f.write(f'{names[i]} = "{self.get_hex_0x(c)}"\n')
            f.write("\n[colors.bright]\n")
            for i, c in enumerate(colors_16[8:]):
                names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
                f.write(f'{names[i]} = "{self.get_hex_0x(c)}"\n')
        print(f"Generated Alacritty theme: {alacritty_path}")

        # 2. Konsole
        konsole_path = os.path.join(self.output_dir, "extracted.colorscheme")
        with open(konsole_path, 'w') as f:
            f.write("[Background]\n")
            f.write(f"Color={self.get_rgb_str(bg)}\n")
            f.write("[Foreground]\n")
            f.write(f"Color={self.get_rgb_str(fg)}\n")
            # Simplified Konsole color map
            for i, c in enumerate(colors_16[:8]):
                f.write(f"[Color{i}]\nColor={self.get_rgb_str(c)}\n")
        print(f"Generated Konsole colorscheme: {konsole_path}")

        # 3. Starship
        starship_path = os.path.join(self.output_dir, "starship_palette.toml")
        with open(starship_path, 'w') as f:
            f.write("[palettes.extracted]\n")
            f.write(f'bg = "#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"\n')
            f.write(f'fg = "#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"\n')
            for i, c in enumerate(colors_16):
                f.write(f'color{i} = "#{c[0]:02x}{c[1]:02x}{c[2]:02x}"\n')
        print(f"Generated Starship palette: {starship_path}")

        print("\n--- Usage Tips ---")
        print(f"Alacritty: Add 'import = [\"{alacritty_path}\"]' to your alacritty.toml")
        print(f"Konsole: Copy 'extracted.colorscheme' (from {self.output_dir}) to ~/.local/share/konsole/")
        print(f"Starship: Add 'palette = \"extracted\"' and import '{starship_path}' to your starship.toml")

    def update_vibrant_palette(self):
        if os.path.exists(self.palette_path):
            with open(self.palette_path, 'a') as f:
                f.write(f"\n## Extracted from {os.path.basename(self.input_source)}\n")
                f.write(f"- **Background**: `#{self.palette[0][0]:02x}{self.palette[0][1]:02x}{self.palette[0][2]:02x}`\n")
                f.write(f"- **Foreground**: `#{self.palette[-1][0]:02x}{self.palette[-1][1]:02x}{self.palette[-1][2]:02x}`\n")
                for i, c in enumerate(self.palette[1:9]): # Just show a few
                    f.write(f"- **Color {i}**: `#{c[0]:02x}{c[1]:02x}{c[2]:02x}`\n")
            print(f"Updated {self.palette_path}")

    def cleanup(self):
        shutil.rmtree(self.temp_dir)

def main():
    parser = argparse.ArgumentParser(description="Extract terminal color schemes from an image or URL.")
    parser.add_argument("input", help="Path to local image or URL")
    parser.add_argument("--output-dir", "-o",
                        default="~/ops/color-tools/output",
                        help="Directory to save generated configs (default: %(default)s)")
    parser.add_argument("--palette-file", "-p",
                        default="~/Colors/vibrant_palette.md",
                        help="Path to vibrant_palette.md (default: %(default)s)")
    parser.add_argument("--no-update", action="store_true",
                        help="Don't update the vibrant palette file")

    args = parser.parse_args()
    
    extractor = ColorExtractor(args.input, output_dir=args.output_dir, palette_path=args.palette_file)
    try:
        extractor.prepare_image()
        extractor.extract_colors()
        extractor.generate_configs()
        if not args.no_update:
            extractor.update_vibrant_palette()
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main()
