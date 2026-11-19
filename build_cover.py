#!/usr/bin/env python3
"""GTA 6 Cover Art — deterministic sample covers, offline, no network.

Draws a Vice City sunset "photo" (gradient sky, sun, skyline, palms,
ocean) with Pillow + DejaVu fonts, then composes it into three cover
exports: 1080x1080, 1080x1350, 1920x1080. Same input -> same bytes.
Run: python3 build_cover.py  (writes out/*.png and screenshots/*.png)
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
SHOT = os.path.join(ROOT, "screenshots")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_photo(w, h, seed=42):
    """Synthetic Vice City sunset photo, deterministic."""
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    top, mid, low = (26, 8, 64), (255, 94, 98), (255, 176, 66)
    for y in range(h):
        t = y / h
        c = lerp(top, mid, t * 1.6) if t < 0.62 else lerp(mid, low, (t - 0.62) / 0.38)
        d.line([(0, y), (w, y)], fill=c)
    # sun
    cx, cy, r = int(w * 0.68), int(h * 0.34), int(w * 0.13)
    sun = Image.new("RGB", (w, h), (0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 130))
    sun = sun.filter(ImageFilter.GaussianBlur(r // 4))
    img = Image.blend(img, Image.composite(sun, Image.new("RGB", (w, h), (0, 0, 0)), sun.convert("L")), 0.9)
    d = ImageDraw.Draw(img)
    # ocean
    oy = int(h * 0.68)
    for y in range(oy, h):
        t = (y - oy) / (h - oy)
        d.line([(0, y), (w, y)], fill=lerp((255, 140, 90), (12, 20, 60), t))
    for i in range(60):
        x = rnd.randint(0, w)
        y = rnd.randint(oy + 4, h - 4)
        d.line([(x, y), (x + rnd.randint(20, 90), y)], fill=(255, 220, 180), width=2)
    # skyline
    x = 0
    while x < w:
        bw = rnd.randint(int(w * 0.05), int(w * 0.11))
        bh = rnd.randint(int(h * 0.08), int(h * 0.24))
        d.rectangle([x, oy - bh, x + bw, oy], fill=(16, 10, 40))
        for wy in range(oy - bh + 8, oy - 6, 14):
            for wx in range(x + 6, x + bw - 6, 12):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 210, 110))
        x += bw + rnd.randint(2, 10)
    # palms
    for px, ph in [(int(w * 0.08), int(h * 0.22)), (int(w * 0.92), int(h * 0.26))]:
        d.line([(px, oy), (px + (8 if px < w // 2 else -8), oy - ph)], fill=(10, 8, 30), width=10)
        for a in range(5):
            ang = math.pi * (0.15 + a * 0.17)
            ex = px + int(math.cos(ang) * ph * 0.55) * (1 if px < w // 2 else -1)
            ey = oy - ph - int(math.sin(ang) * ph * 0.35)
            d.line([(px, oy - ph), (ex, ey)], fill=(10, 8, 30), width=7)
    return img


def halftone(img, step=9):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for y in range(0, h, step):
        for x in range(0, w, step):
            if (x // step + y // step) % 2 == 0:
                d.ellipse([x, y, x + 3, y + 3], fill=(255, 255, 255, 28))
    return img


def cover(w, h, title_size):
    img = make_photo(w, h)
    img = halftone(img)
    d = ImageDraw.Draw(img, "RGBA")
    # vignette
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-w // 4, -h // 4, w * 5 // 4, h * 5 // 4], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w // 8))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    img = Image.composite(img, black, vig.point(lambda p: 255 - int((255 - p) * 0.45)))
    d = ImageDraw.Draw(img, "RGBA")
    # top band
    d.rectangle([0, 0, w, int(h * 0.10)], fill=(0, 0, 0, 110))
    f_small = font(max(20, int(w * 0.028)))
    d.text((int(w * 0.04), int(h * 0.035)), "ROCKSTAR  •  VICE CITY", font=f_small, fill=(255, 255, 255))
    # title block, bottom
    f_title = font(title_size)
    f_sub = font(max(24, int(w * 0.032)))
    lines = ["GRAND THEFT", "AUTO VI"]
    total = sum(d.textbbox((0, 0), s, font=f_title)[3] for s in lines)
    y = int(h * 0.60)
    for s in lines:
        bb = d.textbbox((0, 0), s, font=f_title)
        tw = bb[2] - bb[0]
        # outline
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, 3)]:
            d.text(((w - tw) // 2 + dx, y + dy), s, font=f_title, fill=(0, 0, 0))
        d.text(((w - tw) // 2, y), s, font=f_title, fill=(255, 255, 255))
        y += bb[3] - bb[1] + 4
    tag = "VICE CITY  •  2026"
    bb = d.textbbox((0, 0), tag, font=f_sub)
    d.text(((w - (bb[2] - bb[0])) // 2, y + 28), tag, font=f_sub, fill=(255, 196, 0))
    d.text((int(w * 0.04), int(h * 0.965)), "A LUCIA & JASON STORY", font=f_small, fill=(255, 255, 255))
    return img


def ui_mock(w=1280, h=800):
    img = Image.new("RGB", (w, h), (18, 18, 24))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 64], fill=(255, 196, 0))
    d.text((24, 16), "GTA VI COVER STUDIO", font=font(28), fill=(0, 0, 0))
    photo = make_photo(560, 560).resize((560, 560))
    img.paste(photo, (40, 100))
    d.rectangle([640, 100, 1240, 700], fill=(38, 38, 48))
    d.text((664, 120), "1. Upload your photo", font=font(26), fill=(255, 255, 255))
    d.text((664, 170), "2. Pick a preset: Sunset / Neon / Beach", font=font(26), fill=(255, 255, 255))
    d.text((664, 220), "3. Export 1080x1080 / 1080x1350 / 1920x1080", font=font(26), fill=(255, 255, 255))
    for i, label in enumerate(["1080x1080", "1080x1350", "1920x1080"]):
        x = 664 + i * 190
        d.rounded_rectangle([x, 300, x + 170, 360], radius=8, fill=(255, 196, 0))
        d.text((x + 18, 318), label, font=font(20), fill=(0, 0, 0))
    d.text((664, 420), "GRAND THEFT AUTO VI", font=font(34), fill=(255, 255, 255))
    d.text((664, 470), "VICE CITY  •  2026", font=font(26), fill=(255, 196, 0))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SHOT, exist_ok=True)
    specs = [
        ("cover-1080x1080.png", 1080, 1080, 120),
        ("cover-1080x1350.png", 1080, 1350, 110),
        ("cover-1920x1080.png", 1920, 1080, 150),
    ]
    for name, w, h, ts in specs:
        img = cover(w, h, ts)
        img.save(os.path.join(OUT, name), optimize=True)
        img.save(os.path.join(SHOT, name), optimize=True)
        print(name, img.size, os.path.getsize(os.path.join(OUT, name)))
    ui = ui_mock()
    ui.save(os.path.join(SHOT, "ui-1280x800.png"), optimize=True)
    print("ui-1280x800.png", ui.size, os.path.getsize(os.path.join(SHOT, "ui-1280x800.png")))


if __name__ == "__main__":
    main()
