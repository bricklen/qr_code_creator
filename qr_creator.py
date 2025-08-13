#!/usr/bin/env python3
"""
qrcli.py — tiny CLI to turn a URL (or any text) into a QR code.

Defaults to emitting a UTF-8 text/ANSI QR to STDOUT.
Optional formats:
  --to-png  → PNG bytes (to STDOUT or file via --out)
  --to-svg  → SVG XML  (to STDOUT or file via --out)

Examples
--------
$ ./qrcli.py --input https://example.com
$ ./qrcli.py --input https://example.com --to-png > code.png
$ ./qrcli.py --input https://example.com --to-svg --out code.svg
$ ./qrcli.py --input 'WIFI:S:MyNet;T:WPA;P:s3cr3t;;'

Requires: Python 3.8+, and `qrcode` (with Pillow for PNG).
  pip install 'qrcode[pil]'

SVG output does not require Pillow, but installing Pillow is fine.
"""
from __future__ import annotations
import argparse
import sys
import io
import re
from typing import Optional

# Third-party deps
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
    from qrcode.image.svg import SvgImage, SvgPathImage, SvgFragmentImage
except Exception as e:
    sys.stderr.write("Error: missing dependency. Install with: pip install 'qrcode[pil]'\n")
    raise


EC_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def build_qr(data: str, level: str, box_size: int, border: int) -> qrcode.QRCode:
    qr = qrcode.QRCode(
        version=None,  # auto-fit
        error_correction=EC_LEVELS[level],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr


def emit_text(qr: qrcode.QRCode, use_unicode: bool = True) -> str:
    """Render the QR to text for terminals.

    If use_unicode is True, use full block (█) + spaces for crisper output.
    Otherwise, use two-char cells (##/  ) for broader compatibility.
    """
    m = qr.get_matrix()  # list[list[bool]] with border already applied

    if use_unicode:
        black = "█"
        white = " "
        lines = ["".join(black if cell else white for cell in row) for row in m]
    else:
        black = "##"
        white = "  "
        lines = ["".join(black if cell else white for cell in row) for row in m]

    return "\n".join(lines) + "\n"


def emit_png(qr: qrcode.QRCode) -> bytes:
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()


def emit_svg(qr: qrcode.QRCode, style: str = "path") -> str:
    """Return SVG as a string. style ∈ {"rect", "path", "frag"}."""
    if style == "rect":
        factory = SvgImage
    elif style == "frag":
        factory = SvgFragmentImage
    else:
        factory = SvgPathImage
    img = qr.make_image(image_factory=factory)
    bio = io.BytesIO()
    img.save(bio)
    return bio.getvalue().decode("utf-8")


def sanitize_filename(text: str) -> str:
    """Convert input text to a safe filename by removing special characters."""
    # Remove/replace characters that are problematic in filenames
    filename = re.sub(r'[^\w\s-]', '', text)  # Keep only word chars, spaces, hyphens
    filename = re.sub(r'[-\s]+', '-', filename)  # Replace spaces/multiple hyphens with single hyphen
    filename = filename.strip('-')  # Remove leading/trailing hyphens
    return filename[:50] if filename else "qrcode"  # Limit length, fallback if empty


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Generate a QR code from input text/URL.")
    p.add_argument("-i", "--input", required=True, help="Input text / URL to encode")
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--to-png", action="store_true", help="Emit PNG bytes")
    fmt.add_argument("--to-svg", action="store_true", help="Emit SVG XML")
    p.add_argument("--out", help="Output file path (default: auto-generated from input or STDOUT for text)")
    p.add_argument("--level", choices=list(EC_LEVELS.keys()), default="M", help="Error correction level (L/M/Q/H)")
    p.add_argument("--box-size", type=int, default=10, help="Pixels per module for raster outputs (PNG/text density)")
    p.add_argument("--border", type=int, default=4, help="Border modules around the QR")
    p.add_argument("--ascii", action="store_true", help="Use ASCII-compatible text renderer (no unicode blocks)")
    p.add_argument("--svg-style", choices=["path", "rect", "frag"], default="path", help="SVG drawing style")

    args = p.parse_args(argv)

    qr = build_qr(args.input, args.level, args.box_size, args.border)

    # Determine output target and filename
    if args.out:
        output_file = args.out
        to_file = output_file != "-"
    else:
        # Auto-generate filename for PNG/SVG, use stdout for text
        if args.to_png or args.to_svg:
            base_name = sanitize_filename(args.input)
            extension = ".png" if args.to_png else ".svg"
            output_file = base_name + extension
            to_file = True
        else:
            output_file = "-"
            to_file = False

    if args.to_png:
        payload = emit_png(qr)
        if to_file:
            with open(output_file, "wb") as f:
                f.write(payload)
        else:
            # write binary to stdout (allow shell redirection)
            sys.stdout.buffer.write(payload)
        return 0

    if args.to_svg:
        svg = emit_svg(qr, style=args.svg_style)
        if to_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(svg)
        else:
            sys.stdout.write(svg)
        return 0

    # Default: text to STDOUT
    text = emit_text(qr, use_unicode=(not args.ascii))
    if to_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

