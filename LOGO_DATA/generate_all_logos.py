#!/usr/bin/env python3
"""
ANIKET_AI — Logo Variant Generator
Input: AniketG_Ai_logo_Transprent.png
Output: All needed variants auto-generated
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

LOGO_DIR = Path(__file__).parent
SOURCE   = LOGO_DIR / "AniketG_Ai_logo_Transprent.png"
COVER    = LOGO_DIR / "Cover_AniketG_Ai.png"
PROFILE  = LOGO_DIR / "Profile_AniketG_Ai.png"

def save(img, name):
    path = LOGO_DIR / name
    img.save(path, optimize=True)
    size_kb = os.path.getsize(path) // 1024
    print(f"  ✅ {name} ({img.size[0]}×{img.size[1]}, {size_kb}KB)")
    return path

def on_color(logo_rgba, bg_hex, size, name):
    """Logo on solid color background"""
    bg = Image.new("RGBA", size, bg_hex)
    logo = logo_rgba.copy()
    logo.thumbnail((int(size[0]*0.7), int(size[1]*0.7)), Image.LANCZOS)
    x = (size[0] - logo.size[0]) // 2
    y = (size[1] - logo.size[1]) // 2
    bg.paste(logo, (x, y), logo)
    return bg.convert("RGB")

def main():
    print("🎨 ANIKET_AI — Logo Variant Generator")
    print("=" * 50)

    if not SOURCE.exists():
        print(f"❌ Source not found: {SOURCE}")
        return

    logo = Image.open(SOURCE).convert("RGBA")
    print(f"📥 Source: {logo.size[0]}×{logo.size[1]}")
    print()

    # ── 1. Logo on white (for light backgrounds)
    img = on_color(logo, (255, 255, 255, 255), (800, 400), "Logo_white.png")
    save(img, "Logo_white.png")

    # ── 2. Logo on black (for dark backgrounds)
    img = on_color(logo, (0, 0, 0, 255), (800, 400), "Logo_black.png")
    save(img, "Logo_black.png")

    # ── 3. Instagram profile square 1080×1080
    img = on_color(logo, (10, 10, 20, 255), (1080, 1080), "Logo_square_1080.png")
    save(img, "Logo_square_1080.png")

    # ── 4. Watermark small (transparent, for ads)
    wm = logo.copy()
    wm.thumbnail((200, 80), Image.LANCZOS)
    # 40% opacity
    r, g, b, a = wm.split()
    a = a.point(lambda x: int(x * 0.4))
    wm = Image.merge("RGBA", (r, g, b, a))
    save(wm, "Watermark_small.png")

    # ── 5. Favicon 32×32
    fav = logo.copy()
    fav.thumbnail((32, 32), Image.LANCZOS)
    bg = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    x = (32 - fav.size[0]) // 2
    y = (32 - fav.size[1]) // 2
    bg.paste(fav, (x, y), fav)
    save(bg, "Favicon_32x32.png")

    # ── 6. Favicon 16×16
    fav = logo.copy()
    fav.thumbnail((16, 16), Image.LANCZOS)
    bg = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    x = (16 - fav.size[0]) // 2
    y = (16 - fav.size[1]) // 2
    bg.paste(fav, (x, y), fav)
    save(bg, "Favicon_16x16.png")

    # ── 7. OG Image 1200×630 (website share preview)
    og = Image.new("RGB", (1200, 630), (8, 9, 15))
    logo_resized = logo.copy()
    logo_resized.thumbnail((400, 200), Image.LANCZOS)
    x = (1200 - logo_resized.size[0]) // 2
    y = (630 - logo_resized.size[1]) // 2 - 40
    og.paste(logo_resized, (x, y), logo_resized)
    save(og, "OG_image.png")

    # ── 8. LinkedIn Banner 1584×396
    banner = Image.new("RGB", (1584, 396), (8, 9, 15))
    logo_b = logo.copy()
    logo_b.thumbnail((280, 140), Image.LANCZOS)
    banner.paste(logo_b, (100, (396 - logo_b.size[1])//2), logo_b)
    save(banner, "Banner_LinkedIn.png")

    # ── 9. Twitter Banner 1500×500
    banner = Image.new("RGB", (1500, 500), (8, 9, 15))
    logo_b = logo.copy()
    logo_b.thumbnail((300, 150), Image.LANCZOS)
    banner.paste(logo_b, (100, (500 - logo_b.size[1])//2), logo_b)
    save(banner, "Banner_Twitter.png")

    # ── 10. Facebook Cover 820×312
    banner = Image.new("RGB", (820, 312), (8, 9, 15))
    logo_b = logo.copy()
    logo_b.thumbnail((200, 100), Image.LANCZOS)
    banner.paste(logo_b, (60, (312 - logo_b.size[1])//2), logo_b)
    save(banner, "Banner_Facebook.png")

    # ── 11. YouTube Banner 2560×1440
    banner = Image.new("RGB", (2560, 1440), (8, 9, 15))
    logo_b = logo.copy()
    logo_b.thumbnail((600, 300), Image.LANCZOS)
    x = (2560 - logo_b.size[0]) // 2
    y = (1440 - logo_b.size[1]) // 2
    banner.paste(logo_b, (x, y), logo_b)
    save(banner, "Banner_YouTube.png")

    print()
    print(f"✅ All {11} variants generated in:")
    print(f"   {LOGO_DIR}")
    print()
    print("📁 Open folder:")
    print(f"   open '{LOGO_DIR}'")

if __name__ == "__main__":
    main()
