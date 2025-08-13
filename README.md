# QR Code Creator

A tiny CLI tool to turn a URL (or any text) into a QR code.

## Features

- Generate QR codes from any text or URL
- Multiple output formats:
  - UTF-8 text/ANSI QR to STDOUT (default)
  - PNG image files
  - SVG vector graphics
- Customizable error correction levels
- Configurable box size and border
- ASCII-compatible text output option

## Installation

Requires Python 3.8+ and the `qrcode` library with Pillow for PNG support:

```bash
pip install 'qrcode[pil]'
```

SVG output does not require Pillow, but installing Pillow is recommended.

## Usage

### Basic Usage

```bash
# Generate text QR code to terminal
python qr_creator.py -i "https://example.com"

# Generate PNG with auto-generated filename (https-example-com.png)
python qr_creator.py -i "https://example.com" --to-png

# Generate PNG and save to specific file
python qr_creator.py -i "https://example.com" --to-png --out code.png

# Generate SVG with auto-generated filename (https-example-com.svg)
python qr_creator.py -i "https://example.com" --to-svg

# WiFi QR code example
python qr_creator.py -i 'WIFI:S:MyNet;T:WPA;P:s3cr3t;;'
```

### Command Line Options

```bash
python qr_creator.py -h
```

**Required:**
- `-i, --input TEXT` - Input text or URL to encode

**Output Format (mutually exclusive):**
- `--to-png` - Emit PNG bytes
- `--to-svg` - Emit SVG XML

**Optional:**
- `--out FILE` - Output file path (default: auto-generated from input for PNG/SVG, STDOUT for text)
- `--level {L,M,Q,H}` - Error correction level (default: M)
- `--box-size INT` - Pixels per module for raster outputs (default: 10)
- `--border INT` - Border modules around the QR (default: 4)
- `--ascii` - Use ASCII-compatible text renderer (no unicode blocks)
- `--svg-style {path,rect,frag}` - SVG drawing style (default: path)
- `-h, --help` - Show help message and exit

**Auto-Generated Filenames:**
When `--out` is not specified, PNG and SVG files are automatically saved with filenames based on the input text (special characters removed, limited to 50 characters). Text output goes to STDOUT by default.

### Examples

```bash
# Basic text QR to terminal
python qr_creator.py -i "Hello World"

# PNG output with auto-generated filename (Hello-World.png)
python qr_creator.py -i "Hello World" --to-png

# PNG output to specific file
python qr_creator.py -i "https://github.com" --to-png --out github.png

# SVG output with auto-generated filename (https-github-com.svg)
python qr_creator.py -i "https://github.com" --to-svg

# High error correction with custom border
python qr_creator.py -i "Important data" --level H --border 2

# ASCII-only output (no unicode)
python qr_creator.py -i "https://example.com" --ascii
```

## Error Correction Levels

- **L** - Low (~7% recovery)
- **M** - Medium (~15% recovery) - Default
- **Q** - Quartile (~25% recovery) 
- **H** - High (~30% recovery)
