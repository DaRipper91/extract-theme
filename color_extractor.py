#!/usr/bin/env python3
import os
import sys
import tempfile
import argparse
import requests
from colorthief import ColorThief
from PIL import Image

class ColorExtractor:
    def __init__(self, input_source, output_dir=None, palette_path=None):
        self.input_source = input_source
        self.output_dir = os.path.expanduser(output_dir or "~/ops/color-tools/output")
        self.palette_path = os.path.expanduser(palette_path or "~/Colors/vibrant_palette.md")
        self.temp_dir = tempfile.mkdtemp()
        self.image_path = None
        self.palette = []
        self.hex_palette = []

    def prepare_image(self):
        if self.input_source.startswith(('http://', 'https://')):
            print(f"Downloading image from {self.input_source}...")
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.input_source, stream=True, headers=headers)
            if response.status_code == 200:
                self.image_path = os.path.join(self.temp_dir, "input_image")
                with open(self.image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            else:
                print(f"Error: Could not download image (Status: {response.status_code})")
                sys.exit(1)
        else:
            self.image_path = os.path.expanduser(self.input_source)
            if not os.path.exists(self.image_path):
                print(f"Error: File {self.image_path} not found.")
                sys.exit(1)

    def extract_colors(self):
        print("Extracting colors...")
        color_thief = ColorThief(self.image_path)
        # Extract more than 16 to ensure we have enough variety
        raw_palette = color_thief.get_palette(color_count=20, quality=1)
        
        # Sort by brightness (simple sum of RGB)
        self.palette = sorted(raw_palette, key=lambda c: sum(c))
        
        # Hex versions
        self.hex_palette = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.palette]

    def get_rgb_str(self, color):
        return f"{color[0]},{color[1]},{color[2]}"

    def get_hex_0x(self, color):
        return f"0x{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    def generate_configs(self):
        bg = self.palette[0]
        fg = self.palette[-1]
        
        # Heuristic for 16 colors: 
        # We'll take the first 8 for normal, and last 8 for bright (excluding extreme bg/fg if possible)
        # But let's just use 16 colors from the middle of the sorted palette
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
            f.write(f'foreground = "{self.get_hex_0x(fg)}"\n\n')
            
            f.write("[colors.normal]\n")
            names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
            for i, name in enumerate(names):
                f.write(f'{name} = "{self.get_hex_0x(colors_16[i])}"\n')
            
            f.write("\n[colors.bright]\n")
            for i, name in enumerate(names):
                f.write(f'{name} = "{self.get_hex_0x(colors_16[i+8])}"\n')
        print(f"Generated Alacritty theme: {alacritty_path}")

        # 2. Konsole
        konsole_path = os.path.join(self.output_dir, "extracted.colorscheme")
        with open(konsole_path, 'w') as f:
            f.write("[Background]\n")
            f.write(f"Color={self.get_rgb_str(bg)}\n")
            f.write("[Foreground]\n")
            f.write(f"Color={self.get_rgb_str(fg)}\n")
            for i in range(8):
                f.write(f"[Color{i}]\nColor={self.get_rgb_str(colors_16[i])}\n")
                f.write(f"[Color{i}Intense]\nColor={self.get_rgb_str(colors_16[i+8])}\n")
            f.write("\n[General]\nDescription=Extracted Theme\nOpacity=1\n")
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
        import shutil
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
