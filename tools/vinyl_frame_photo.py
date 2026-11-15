#!/usr/bin/env python3
"""Vinyl frame on a real record photo (dance-lane DSP covers, Amir 2026-11-12).

The record / sleeve photos are AI bases (raw_render.py, Amir's go 11-12, prompts in
artwork/edits/vinyl-frame/README.md). His cover art is placed LOCALLY on top at full
resolution: only scaled and masked, never sent through AI.

Bases and their measured geometry (1024 px source; circle fitted to the record edge,
sleeve front measured by threshold):
  disc-a, disc-b    top-down record; art circle = 90% of the record (2c)
  sleeve-a, sleeve-b  front-on blank sleeve with the record sliding out right

Usage:
  python3 tools/vinyl_frame_photo.py <art> --base disc-a --out <new.jpg> [--size 3000]
Refuses to overwrite an existing --out.
"""
import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parents[1] / "artwork" / "edits" / "vinyl-frame"
SS = 2

# crop = square (x0, y0, side) in base px; circle = (cx, cy, r) of the record; rect = sleeve front
BASES = {
    "disc-a": {"file": "base-disc-a.png", "crop": (47, 34, 920), "circle": (507.1, 493.9, 405.1)},
    "disc-b": {"file": "base-disc-b.png", "crop": (48, 32, 920), "circle": (507.8, 492.3, 413.0)},
    "sleeve-a": {"file": "base-sleeve-a.png", "crop": (40, 41, 920), "rect": (83, 202, 688, 801)},
    "sleeve-b": {"file": "base-sleeve-b.png", "crop": (41, 19, 960), "rect": (75, 200, 685, 799)},
}


def circle_mask(d):
    m = Image.new("L", (d * SS, d * SS), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * SS - 1, d * SS - 1], fill=255)
    return m.resize((d, d), Image.LANCZOS)


def compose(art, key, S):
    b = BASES[key]
    base = Image.open(HERE / b["file"]).convert("RGB")
    x0, y0, side = b["crop"]
    k = S / side
    can = base.crop((x0, y0, x0 + side, y0 + side)).resize((S, S), Image.LANCZOS)
    if "circle" in b:
        cx, cy, r = b["circle"]
        ra = r * 0.90
        d = int(round(2 * ra * k))
        px, py = int(round((cx - ra - x0) * k)), int(round((cy - ra - y0) * k))
        # thin soft shadow where the art meets the vinyl
        sh = Image.new("L", (S, S), 0)
        sh.paste(circle_mask(d + 10), (px - 5, py - 3))
        can.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.6)))
        can.paste(art.resize((d, d), Image.LANCZOS), (px, py), circle_mask(d))
    else:
        l, t, rr, bb = b["rect"]
        w, h = (rr - l) * k, (bb - t) * k
        s = int(round(min(w, h)))
        px = int(round((l - x0) * k + (w - s) / 2))
        py = int(round((t - y0) * k + (h - s) / 2))
        can.paste(art.resize((s, s), Image.LANCZOS), (px, py))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--base", choices=sorted(BASES), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=3000)
    a = ap.parse_args()
    if os.path.exists(a.out):
        sys.exit(f"refused: {a.out} exists (never overwrite)")
    out = compose(Image.open(a.art).convert("RGB"), a.base, a.size)
    out.save(a.out, "JPEG", quality=95, subsampling=0)
    print("wrote", a.out, out.size)


if __name__ == "__main__":
    main()
