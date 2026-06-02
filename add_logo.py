#!/usr/bin/env python3
"""
Add AniketG AI logo to top-right corner of generated images.
Usage: python3 add_logo.py <image.png>
       python3 add_logo.py --batch <projects_folder>
"""
from PIL import Image
import sys
import os
from pathlib import Path

LOGO_PATH = Path.home() / "Desktop/online-work-site/AniketG_Ai_logo.png"
LOGO_SIZE_RATIO = 0.09   # 9% of image width
MARGIN = 22              # pixels from edge

def add_logo(image_path, logo_path=LOGO_PATH, overwrite=True):
    img = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    logo_w = int(img.width * LOGO_SIZE_RATIO)
    logo_h = int(logo_w * (logo.height / logo.width))
    logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)

    x = img.width - logo_w - MARGIN
    y = MARGIN

    img.paste(logo_resized, (x, y), logo_resized)

    out_path = image_path if overwrite else str(image_path).replace(".png", "_logo.png")
    img.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"  ✓ {os.path.basename(out_path)}")

def batch(folder):
    pngs = list(Path(folder).rglob("*.png"))
    pngs = [p for p in pngs if "Thumbnail" in str(p) or any(
        f"_{str(i).zfill(2)}" in str(p) or f"_{i}." in str(p) for i in range(1, 20)
    )]
    print(f"Found {len(pngs)} images. Adding logo...")
    for p in pngs:
        add_logo(p)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_logo.py <image.png>")
        print("       python3 add_logo.py --batch <folder>")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        folder = sys.argv[2] if len(sys.argv) > 2 else "."
        batch(folder)
    else:
        add_logo(sys.argv[1])
