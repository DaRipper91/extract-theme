# Extract-Theme: Color Palette Pipeline

A powerful CLI tool to transform any image or URL into a functional terminal color scheme.

## 🚀 Overview
The `extract-theme` tool utilizes k-means clustering via `ColorThief` to identify dominant colors in an image. It then maps these colors to ANSI terminal slots and generates configuration files for Alacritty, Konsole, and Starship.

## 🛠 Features
- **URL Support**: Directly process online wallpapers.
- **Local Files**: Work with your local image collection.
- **Multi-Format Output**: Generates TOML for Alacritty/Starship and `.colorscheme` for Konsole.
- **Automatic Logging**: Appends new palettes to your central `vibrant_palette.md` reference.
- **Zero-Config Dependencies**: Uses `uv run` to handle Python libraries on-the-fly.

## 📋 Pipeline Details
1. **Preparation**: Downloads remote images or resolves local paths.
2. **Extraction**: Analyzes the image to extract a 20-color raw palette.
3. **Sorting**: Orders colors by brightness to intelligently assign Background, Foreground, and ANSI slots.
4. **Generation**:
   - `alacritty_theme.toml`: Hex codes in `0xRRGGBB` format.
   - `extracted.colorscheme`: RGB decimal format for KDE Konsole.
   - `starship_palette.toml`: Hex codes for custom prompt palettes.
5. **Persistence**: Logs the results to `~/Colors/vibrant_palette.md`.

## 📖 Usage
Run the following command in your terminal:
```fish
extract-theme <image_path_or_url>
```

### Examples
```fish
# From a URL
extract-theme https://example.com/wallpaper.jpg

# From a local file
extract-theme ~/Pictures/Wallpapers/dark-forest.png
```

## 🔧 Integration
- **Alacritty**: Add `import = ["~/ops/color-tools/output/alacritty_theme.toml"]` to your `alacritty.toml`.
- **Konsole**: Move the `.colorscheme` file to `~/.local/share/konsole/`.
- **Starship**: Import the palette file in your `starship.toml` and set `palette = "extracted"`.
