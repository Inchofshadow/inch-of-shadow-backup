#!/usr/bin/env python3
"""Dance-lane marks, round 3 (Amir 2026-11-12: "completely different idea").

The square art stays full bleed (or nearly); the vinyl is a MARK, not a frame.
Local only (Pillow + numpy), no AI.

  ring     thin ivory lead-out rings drawn over the full-bleed art (no record shown)
  grooves  fine concentric grooves pressed over the whole art, like the cover is cut in vinyl
  band     art at 92% on top, a black groove band along the bottom (the record edge seen side-on)
  corner   full-bleed art with a black record quarter rising from the bottom-left corner

Usage: python3 tools/vinyl_mark.py <art> --style ring --out <new.jpg> [--size 3000]
Refuses to overwrite an existing --out.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

IVORY = (233, 226, 214)
WARM_BLACK = (15, 13, 12)
SS = 2


def radial(S, cx, cy):
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    return np.sqrt((x - cx) ** 2 + (y - cy) ** 2)


def style_ring(art, S):
    can = art.resize((S, S), Image.LANCZOS).convert("RGB")
    ov = Image.new("L", (S * SS, S * SS), 0)
    d = ImageDraw.Draw(ov)
    c = S * SS / 2
    for rr, w, a in ((0.470, 30, 240), (0.447, 6, 170), (0.432, 4, 120)):
        r = rr * S * SS
        d.ellipse([c - r, c - r, c + r, c + r], outline=a, width=w * SS)
    ov = ov.resize((S, S), Image.LANCZOS)
    can.paste(IVORY, (0, 0), ov)
    return can


def style_grooves(art, S):
    a = np.asarray(art.resize((S, S), Image.LANCZOS).convert("RGB"), np.float32)
    r = radial(S, S / 2, S / 2) / (S / 2)
    g = np.sin(r * 90 * np.pi) * 0.5 + 0.5                    # fine rings
    ang = np.arctan2(*np.mgrid[0:S, 0:S].astype(np.float32)[::-1] - S / 2)
    sheen = ((np.cos(2 * (ang + np.pi / 4)) + 1) / 2) ** 8      # vinyl sheen wedges
    shade = 1 - 0.30 * g + 0.45 * sheen * np.clip(r, 0, 1)
    out = np.clip(a * shade[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def groove_strip(w, h):
    y = np.arange(h, dtype=np.float32)[:, None]
    x = np.arange(w, dtype=np.float32)[None, :]
    v = 16 + 9 * np.sin(y / h * 40 * np.pi) + 4 * np.sin(y / h * 13 * np.pi + 1)
    v = v + 70 * np.exp(-((x / w - 0.32) / 0.10) ** 2) * (y / h)  # one light streak
    v = np.repeat(np.clip(v, 0, 255)[..., None], 3, -1) * np.array([1, .98, .96])
    return Image.fromarray(v.astype(np.uint8))


def style_band(art, S):
    can = Image.new("RGB", (S, S), WARM_BLACK)
    A = int(S * 0.86)
    can.paste(art.resize((A, A), Image.LANCZOS), ((S - A) // 2, 0))
    bh = S - A
    can.paste(groove_strip(S, bh), (0, A))
    # thin ivory lead-in line at the top of the band
    ImageDraw.Draw(can).rectangle([0, A, S, A + max(2, S // 1000)], fill=(60, 56, 52))
    return can


def style_corner(art, S):
    sm = np.asarray(art.resize((300, 300)), np.int32)
    sc = sm.max(-1) - sm.min(-1)
    ys, xs = np.where(sc > np.percentile(sc, 99.7))
    accent = tuple(int(v) for v in sm[ys, xs].mean(0))
    can = art.resize((S, S), Image.LANCZOS).convert("RGB")
    R = int(S * 0.40)
    n = 2 * R
    r = radial(n, R, R) / R
    ang = np.arctan2(*np.mgrid[0:n, 0:n].astype(np.float32)[::-1] - R)
    v = 16 + 6 * np.sin(r * 90 * np.pi) + 90 * (((np.cos(2 * (ang + np.pi / 4)) + 1) / 2) ** 10) * r
    v[r < 0.33] = 0
    v = np.where((r < 0.33) & (r > 0.30), 40, v)
    lab = r < 0.30
    rgb = np.repeat(np.clip(v, 0, 255)[..., None], 3, -1).astype(np.uint8)
    rgb[lab] = accent
    disc = Image.fromarray(rgb)
    m = Image.new("L", (n * SS, n * SS), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n * SS - 1, n * SS - 1], fill=255)
    m = m.resize((n, n), Image.LANCZOS)
    pos = (-R, S - R)                     # centre on the bottom-left corner
    sh = Image.new("L", (S, S), 0)
    sh.paste(m, (pos[0] + 12, pos[1] - 12))
    can.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(S * 0.01)).point(lambda q: int(q * .7)))
    can.paste(disc, pos, m)
    return can


BASE_DISC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artwork", "edits", "vinyl-frame", "base-disc-a.png")
DISC_CIRCLE = (507.1, 493.9, 405.1)       # fitted record edge on base-disc-a (1024 px)


def accent_of(art):
    sm = np.asarray(art.resize((300, 300)), np.int32)
    sc = sm.max(-1) - sm.min(-1)
    ys, xs = np.where(sc > np.percentile(sc, 99.7))
    return np.array([int(v) for v in sm[ys, xs].mean(0)], np.float32)


def photo_record(n, accent, mirror=False):
    """The AI record photo (Amir's go 11-12) cut to its circle at n px; label tinted with the
    cover's accent, keeping the photo's own light (multiply)."""
    cx, cy, r = DISC_CIRCLE
    base = Image.open(BASE_DISC).convert("RGB").crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    if mirror:                            # keep the photo's sheen on the side facing into the cover
        base = base.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.asarray(base.resize((n, n), Image.LANCZOS), np.float32)
    rr = radial(n, n / 2, n / 2) / (n / 2)
    lab = rr < 0.335
    lum = a[..., :1].mean(-1, keepdims=True) if False else a.mean(-1, keepdims=True)
    tint = accent[None, None, :] * np.clip(lum / max(lum[lab].mean(), 1) * 0.95, 0, 1.4)
    a = np.where(lab[..., None], tint, a)
    hole = rr < 0.022
    a[hole] = 0
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    m = Image.new("L", (n * SS, n * SS), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n * SS - 1, n * SS - 1], fill=255)
    return img, m.resize((n, n), Image.LANCZOS)


def corner_photo(art, S, R_frac, where):
    can = art.resize((S, S), Image.LANCZOS).convert("RGB")
    R = int(S * R_frac)
    disc, m = photo_record(2 * R, accent_of(art), mirror=where.startswith("bl"))
    pos = {"bl": (-R, S - R), "br": (S - R, S - R), "bl-low": (-R // 3, S - R // 2)}[where]
    sh = Image.new("L", (S, S), 0)
    sh.paste(m, (pos[0] + int(S * .006), pos[1] - int(S * .006)))
    can.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(S * 0.012)).point(lambda q: int(q * .75)))
    can.paste(disc, pos, m)
    return can


STYLES = {
    "c1": lambda art, S: corner_photo(art, S, 0.40, "bl"),
    "c3": lambda art, S: corner_photo(art, S, 0.40, "br"),
    "c4": lambda art, S: corner_photo(art, S, 0.42, "bl-low"),
"ring": style_ring, "grooves": style_grooves, "band": style_band, "corner": style_corner}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--style", choices=sorted(STYLES), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=3000)
    a = ap.parse_args()
    if os.path.exists(a.out):
        sys.exit(f"refused: {a.out} exists (never overwrite)")
    out = STYLES[a.style](Image.open(a.art).convert("RGB"), a.size)
    out.save(a.out, "JPEG", quality=95, subsampling=0)
    print("wrote", a.out, out.size)


if __name__ == "__main__":
    main()
