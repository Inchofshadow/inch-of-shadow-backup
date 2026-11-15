#!/usr/bin/env python3
"""Vinyl record frame for dance-lane DSP covers (Amir, 2026-11-12).

Every electronic-lane release gets its square art wrapped in a record frame on
Spotify / Apple Music / Symphonic stores; IG, SoundCloud and Bandcamp keep the
plain square. The art itself is never changed: it is only scaled and masked.
Local only (Pillow + numpy), no AI.

Styles:
  disc    - 2c: black 12-inch record on warm black, art circle = 90% of the record
  sleeve  - full square art as the sleeve, black record sliding out on the right
  emboss  - R-017: record circle pressed into platinum paper, art inside
  circle  - rule-safer: plain art circle on warm black (no record details)

Usage:
  python3 tools/vinyl_frame.py <art.jpg> --style disc --out <new.jpg> [--size 3000]
         [--bg #0F0D0C] [--paper #D6D1C8] [--label #RRGGBB]
Never pass an --out that already exists (refused) so his files are never overwritten.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WARM_BLACK = "#0F0D0C"   # M2 dark
PLATINUM = "#D6D1C8"     # M2 light
SS = 2                   # supersampling for smooth circle edges


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def circle_mask(size, box, blur=0):
    m = Image.new("L", (size * SS, size * SS), 0)
    ImageDraw.Draw(m).ellipse([v * SS for v in box], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m


def record_disc(d, cx_off=0.0, seed=7):
    """RGBA image d x d: black vinyl with grooves, a lead-out ring and a soft sheen."""
    n = d * SS
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    c = (n - 1) / 2
    dx, dy = x - c, y - c
    r = np.sqrt(dx * dx + dy * dy) / (n / 2)          # 0 centre .. 1 edge
    ang = np.arctan2(dy, dx)
    rng = np.random.default_rng(seed)
    base = np.full((n, n), 16.0, np.float32)
    # fine grooves: many thin rings with slight random depth
    freq = 420
    grooves = np.sin(r * freq * np.pi) * 4.0 + np.sin(r * freq * 0.37 * np.pi + 1.3) * 2.5
    base += grooves
    # band gaps between "tracks"
    for g in (0.80, 0.88, 0.95):
        base -= 5.0 * np.exp(-((r - g) / 0.0035) ** 2)
    # outer lip
    base += 10.0 * np.exp(-((r - 0.985) / 0.006) ** 2)
    # anisotropic sheen: two opposite light wedges (light from top-left)
    sheen = (np.cos(2 * (ang + np.pi / 4)) + 1) / 2
    sheen = sheen ** 6
    base += sheen * 95 * np.clip(r, 0, 1)
    base += ((np.cos(2 * (ang + np.pi / 4 + 0.35)) + 1) / 2) ** 14 * 40 * np.clip(r, 0, 1)
    base += rng.normal(0, 1.2, (n, n)).astype(np.float32)
    base = np.clip(base, 0, 255)
    rgb = np.stack([base * 1.0, base * 0.98, base * 0.97], -1).astype(np.uint8)
    img = Image.fromarray(rgb).convert("RGBA")
    a = Image.new("L", (n, n), 0)
    ImageDraw.Draw(a).ellipse([0, 0, n - 1, n - 1], fill=255)
    img.putalpha(a)
    return img.resize((d, d), Image.LANCZOS)


def art_circle(art, d):
    """Art scaled so its full width = circle diameter, masked to a circle."""
    a = art.resize((d, d), Image.LANCZOS).convert("RGBA")
    a.putalpha(circle_mask(d, [0, 0, d - 1, d - 1]))
    return a


def shadow(canvas_size, box, blur, strength, offset=(0, 0)):
    m = circle_mask(canvas_size, [box[0] + offset[0], box[1] + offset[1],
                                  box[2] + offset[0], box[3] + offset[1]], blur)
    return m.point(lambda v: int(v * strength))


def style_disc(art, S, bg):
    can = Image.new("RGB", (S, S), hex_rgb(bg))
    D = int(S * 0.88)                       # record
    A = int(D * 0.90)                       # art circle = 90% of record (2c)
    o = (S - D) // 2
    sh = shadow(S, [o, o, o + D, o + D], S * 0.02, 0.85, (0, int(S * 0.012)))
    can.paste((0, 0, 0), (0, 0), sh)
    can.paste(rec := record_disc(D), (o, o), rec)
    oa = (S - A) // 2
    # thin dark ring where art meets vinyl
    can.paste((6, 6, 6), (0, 0), circle_mask(S, [oa - 6, oa - 6, oa + A + 6, oa + A + 6]))
    ac = art_circle(art, A)
    can.paste(ac, (oa, oa), ac)
    return can


def style_circle(art, S, bg):
    """Rule-safer variant: the art as a plain circle on warm black, no grooves, sheen or sleeve."""
    can = Image.new("RGB", (S, S), hex_rgb(bg))
    A = int(S * 0.88)
    oa = (S - A) // 2
    ac = art_circle(art, A)
    can.paste(ac, (oa, oa), ac)
    return can


def style_sleeve(art, S, bg, label):
    can = Image.new("RGB", (S, S), hex_rgb(bg))
    W = int(S * 0.70)                       # sleeve = the full square art
    sx, sy = int(S * 0.035), (S - W) // 2
    D = int(W * 0.95)                       # record slightly smaller than sleeve
    rx = int(S * 0.662) - D // 2            # slid out right: label edge peeks past the sleeve
    ry = sy + (W - D) // 2
    sh = shadow(S, [rx, ry, rx + D, ry + D], S * 0.015, 0.8, (int(S * 0.006), int(S * 0.01)))
    can.paste((0, 0, 0), (0, 0), sh)
    rec = record_disc(D)
    # centre label: solid colour sampled from the art + spindle hole
    L = int(D * 0.33)
    lab = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    ImageDraw.Draw(lab).ellipse([0, 0, L - 1, L - 1], fill=hex_rgb(label) + (255,))
    h = int(D * 0.024)
    ImageDraw.Draw(lab).ellipse([L // 2 - h // 2, L // 2 - h // 2, L // 2 + h // 2, L // 2 + h // 2],
                                fill=(0, 0, 0, 0))
    rec.alpha_composite(lab, ((D - L) // 2, (D - L) // 2))
    can.paste(rec, (rx, ry), rec)
    # sleeve shadow onto the record, then the sleeve (art untouched, only scaled)
    ssh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(ssh).rectangle([sx + int(S * 0.008), sy, sx + W + int(S * 0.012), sy + W], fill=200)
    can.paste((0, 0, 0), (0, 0), ssh.filter(ImageFilter.GaussianBlur(S * 0.008)))
    can.paste(art.resize((W, W), Image.LANCZOS), (sx, sy))
    return can


def style_emboss(art, S, paper):
    pr = np.array(hex_rgb(paper), np.float32)
    rng = np.random.default_rng(3)
    tex = rng.normal(0, 3.0, (S, S)).astype(np.float32)
    tex = np.array(Image.fromarray(np.clip(tex + 128, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.2)), np.float32) - 128
    base = np.clip(pr[None, None, :] + tex[..., None] * 1.6, 0, 255)
    can = Image.fromarray(base.astype(np.uint8))
    D = int(S * 0.86)
    o = (S - D) // 2
    box = [o, o, o + D, o + D]
    # pressed-in circle: dark inner edge top-left, light inner edge bottom-right
    inside = circle_mask(S, box)
    dark = ImageChops_sub(circle_mask(S, box, 0), circle_mask(S, [b + (12 if i < 2 else 12) for i, b in enumerate(box)], 6))
    light = ImageChops_sub(circle_mask(S, box, 0), circle_mask(S, [b - 12 for b in box], 6))
    can.paste((90, 86, 80), (0, 0), dark.point(lambda v: int(v * 0.55)))
    can.paste((250, 248, 244), (0, 0), light.point(lambda v: int(v * 0.65)))
    # faint grooves pressed into the paper ring between edge and art
    A = int(D * 0.90)
    oa = (S - A) // 2
    n = S
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((x - n / 2) ** 2 + (y - n / 2) ** 2)
    ring = (r > A / 2) & (r < D / 2 - 14)
    g = np.sin(r / (D / 2) * 260 * np.pi)
    arr = np.array(can, np.float32)
    arr[ring] -= (g[ring, None] * 3.5 + 6)
    can = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    # inner deboss around the art circle
    can.paste((70, 66, 62), (0, 0), shadow(S, [oa, oa, oa + A, oa + A], 10, 0.6, (6, 8)))
    ac = art_circle(art, A)
    can.paste(ac, (oa, oa), ac)
    _ = inside
    return can


def ImageChops_sub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--style", choices=["disc", "sleeve", "emboss", "circle"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=3000)
    ap.add_argument("--bg", default=WARM_BLACK)
    ap.add_argument("--paper", default=PLATINUM)
    ap.add_argument("--label", default=None, help="sleeve label colour; default = sampled most saturated area of the art")
    a = ap.parse_args()
    if os.path.exists(a.out):
        sys.exit(f"refused: {a.out} exists (never overwrite)")
    art = Image.open(a.art).convert("RGB")
    S = a.size
    if a.style == "disc":
        out = style_disc(art, S, a.bg)
    elif a.style == "sleeve":
        lab = a.label
        if not lab:
            arr = np.array(art.resize((300, 300)), np.int32)
            score = arr.max(-1) - arr.min(-1)          # most saturated area of the art
            ys, xs = np.where(score > np.percentile(score, 99.7))
            col = arr[ys, xs].mean(0).astype(int)
            lab = "#%02X%02X%02X" % tuple(col)
            print("label colour sampled:", lab)
        out = style_sleeve(art, S, a.bg, lab)
    elif a.style == "circle":
        out = style_circle(art, S, a.bg)
    else:
        out = style_emboss(art, S, a.paper)
    out.convert("RGB").save(a.out, "JPEG", quality=95, subsampling=0, icc_profile=None)
    print("wrote", a.out, out.size)


if __name__ == "__main__":
    main()
