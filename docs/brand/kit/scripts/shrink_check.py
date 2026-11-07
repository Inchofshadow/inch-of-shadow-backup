#!/usr/bin/env python3
"""The render-and-shrink check (standing rule, Look-01).

A size on a big canvas means nothing until you see it at the size people see it. This
takes a rendered frame at its NATIVE canvas and writes one sheet showing it scaled to the
real display sizes, with the platform safe zone drawn on the 9:16 formats.

    shrink_check.py frame.png --format reel  [--text-px 36] [--out sheet.png]

formats: reel (1080x1920, phone 390pt wide, Meta safe zone 270/672/65)
         post (1080x1350 or 1080x1440, phone feed 390pt wide, grid tile 130pt)
         thumb (16:9, YouTube home 360px, sidebar 168px, mobile search 120px)
         cover (square, store page 300px, playlist row 64px, 32px avatar size)

--text-px is the smallest text on the canvas; the script says how many points it becomes
on a phone and fails under 11pt (Apple's minimum readable size).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.dont_write_bytecode = True

DISPLAY = {
    "reel":  [("phone, full screen", 390), ("in feed preview", 260)],
    "post":  [("phone feed", 390), ("profile grid tile", 130)],
    "thumb": [("YouTube home", 360), ("YouTube sidebar", 168), ("mobile search", 120)],
    "cover": [("store page", 300), ("playlist row", 64), ("avatar size", 32)],
}
SAFE = {"reel": (270, 672, 65)}  # top, bottom, sides on a 1080x1920 canvas
MIN_PT = 11


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path)
    ap.add_argument("--format", required=True, choices=DISPLAY)
    ap.add_argument("--text-px", type=float, help="smallest text size on the native canvas, in px")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    src = Image.open(a.image).convert("RGB")
    w, h = src.size
    sizes = DISPLAY[a.format]
    ok = True

    if a.text_px:
        # the strict test is the place people really read it: a phone for reels and posts,
        # the smallest tile for thumbnails and covers
        label, dw = sizes[0] if a.format in ("reel", "post") else sizes[-1]
        pt = a.text_px * dw / w
        ok = pt >= MIN_PT
        verdict = "OK" if ok else "TOO SMALL"
        print(f"smallest text {a.text_px:g}px on a {w}px canvas = {pt:.1f}pt at '{label}' ({dw}px wide): {verdict} (minimum {MIN_PT}pt)")

    tiles = []
    if a.format in SAFE:
        top, bottom, sides = [v * w / 1080 for v in SAFE[a.format]]
        marked = src.copy()
        d = ImageDraw.Draw(marked, "RGBA")
        for box in [(0, 0, w, top), (0, h - bottom, w, h), (0, top, sides, h - bottom), (w - sides, top, w, h - bottom)]:
            d.rectangle(box, fill=(255, 0, 60, 70))
        tiles.append(("safe zone: red = keep clear", marked.resize((sizes[0][1], round(h * sizes[0][1] / w)), Image.LANCZOS)))
    for label, dw in sizes:
        tiles.append((f"{label}, {dw}px wide", src.resize((dw, max(1, round(h * dw / w))), Image.LANCZOS)))

    pad, label_h = 24, 22
    sheet_w = sum(t.size[0] for _, t in tiles) + pad * (len(tiles) + 1)
    sheet_h = max(t.size[1] for _, t in tiles) + pad * 2 + label_h
    sheet = Image.new("RGB", (sheet_w, sheet_h), (28, 28, 28))
    d = ImageDraw.Draw(sheet)
    x = pad
    for label, t in tiles:
        d.text((x, pad - 4), label, fill=(200, 200, 200))
        sheet.paste(t, (x, pad + label_h))
        x += t.size[0] + pad

    out = a.out or a.image.with_name(a.image.stem + "_shrink-check.png")
    sheet.save(out)
    print(f"sheet written: {out}")
    zone = ", and is the red zone empty" if a.format in SAFE else ""
    print(f"Now LOOK at it: can you read every word at the smallest size{zone}?")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
