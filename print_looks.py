#!/usr/bin/env python3
"""
print_looks.py
--------------
The Inch of Shadow style library as a tool (board ticket Look-11, Amir 2026-09-20).

Puts a photo through a named print or darkroom process. Local only (Pillow + numpy):
no AI, no upload, no cost. The picture is never redrawn, so it is a safe path for photos
of Amir (face rule: AI never changes his face). Deterministic: same photo in, same
print out. Output keeps the input size; source metadata is not carried over.

    python3 print_looks.py photo.jpg --look riso
    python3 print_looks.py photo.jpg --look cyanotype --out out/night.jpg
    python3 print_looks.py photo.jpg --sheet            # all looks, numbered, to pick by eye
    python3 print_looks.py --list

Rules and history of each look: docs/brand/style-library.md. One borrowed look per release,
on top of the constant brand (type, moods, placement, face rules stay).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

SEED = 7
rng = np.random.default_rng(SEED)
FONT = Path(__file__).resolve().parent / "docs" / "brand" / "fonts" / "Marcellus-Regular.ttf"


def K(im) -> float:
    """Scale factor: the looks were tuned on a 1000px-wide image."""
    return im.size[0] / 1000.0


def lum(im):
    return np.asarray(im.convert("L"), dtype=np.float32) / 255.0


def printable(im, strength=0.6, gamma=0.75):
    """Open the shadows the way a printer would before a hard process: part histogram
    equalisation, part gamma lift. Without it a dark photo turns into a black page."""
    g = im.convert("L")
    eq = np.asarray(ImageOps.equalize(g), np.float32) / 255
    l = np.asarray(g, np.float32) / 255
    mixed = (1 - strength) * l + strength * eq
    return np.clip(mixed, 0, 1) ** gamma


def grain(shape, amount):
    return rng.normal(0, amount, shape).astype(np.float32)


def to_img(a):
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def duotone(l, dark, light):
    d, lt = np.array(dark, np.float32) / 255, np.array(light, np.float32) / 255
    return to_img(d[None, None, :] + (lt - d)[None, None, :] * l[..., None])


def curve(l, contrast=1.0, pivot=0.5):
    return np.clip((l - pivot) * contrast + pivot, 0, 1)


def xerox(im):
    l = printable(im.filter(ImageFilter.GaussianBlur(0.8 * K(im))), 0.65, 0.8)
    l = curve(l, 2.6, 0.55) + grain(l.shape, 0.14)
    l = (l > 0.5).astype(np.float32)
    streak = 1 - 0.10 * (rng.random(im.size[0]) > 0.985)[None, :].repeat(im.size[1], 0)     # toner streaks
    l = np.clip(l * streak, 0, 1)
    l = np.asarray(to_img(l).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
    return duotone(l, (22, 20, 20), (236, 232, 222))


def halftone(im, cell=None):
    cell = cell or max(5, round(11 * K(im)))
    l = printable(im.filter(ImageFilter.GaussianBlur(2 * K(im))), 0.6, 0.85)
    l = curve(l, 1.25, 0.5)
    W, H = im.size
    out = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(out)
    for y in range(0, H + cell, cell):
        off = (cell // 2) if (y // cell) % 2 else 0
        for x in range(-cell, W + cell, cell):
            cx, cy = x + off, y
            v = l[min(max(cy, 0), H - 1), min(max(cx, 0), W - 1)]
            r = (1 - v) ** 0.9 * cell * 0.72
            if r > 0.4:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    return duotone(np.asarray(out, np.float32) / 255, (24, 20, 22), (237, 230, 218))


def riso(im):
    l = curve(lum(im), 1.5, 0.45)
    g = grain(l.shape, 0.07)
    warm = np.clip(1 - np.clip((l - 0.35) * 1.8, 0, 1) + g, 0, 1)          # rose ink prints mids and shadows
    cold = np.clip(1 - np.clip(l * 2.4, 0, 1) + g, 0, 1)                   # dark ink prints deep shadows
    cold = np.roll(np.roll(cold, round(7 * K(im)), axis=1), round(4 * K(im)), axis=0)                    # misregistration
    paper = np.array((240, 232, 214), np.float32) / 255
    rose = np.array((214, 72, 96), np.float32) / 255
    ink = np.array((26, 34, 74), np.float32) / 255
    a = paper[None, None, :] * (1 - warm[..., None] * (1 - rose[None, None, :]))
    a = a * (1 - cold[..., None] * (1 - ink[None, None, :]))
    return to_img(a)


def engraving(im, pitch=None):
    pitch = pitch or max(3.0, 5.0 * K(im))
    l = curve(printable(im.filter(ImageFilter.GaussianBlur(1.6 * K(im))), 0.55, 0.85), 1.3, 0.5)
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    flow = yy + 10 * K(im) * np.sin(xx / (90.0 * K(im)))                                      # gently waving lines
    wave = 0.5 + 0.5 * np.sin(2 * np.pi * flow / pitch)
    cross = 0.5 + 0.5 * np.sin(2 * np.pi * (xx * 0.7 + yy * 0.7) / pitch)
    lines = (wave > l * 1.05).astype(np.float32)
    hatch = ((cross > l * 1.9) & (l < 0.33)).astype(np.float32)             # cross-hatch only in the shadows
    inked = np.clip(lines + hatch, 0, 1)
    a = np.asarray(to_img(1 - inked).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    return duotone(a, (30, 24, 20), (236, 228, 208))


def cyanotype(im):
    l = curve(lum(im), 1.25, 0.48) ** 0.9
    l = np.clip(l + grain(l.shape, 0.035), 0, 1)
    return duotone(l, (8, 28, 58), (226, 236, 240)).filter(ImageFilter.GaussianBlur(0.4))


def solarisation(im):
    l = curve(lum(im), 1.2, 0.5)
    s = np.where(l > 0.55, 1.1 - l, l)                                      # Sabattier: highlights fold back
    s = (s - s.min()) / (s.max() - s.min() + 1e-6)
    s = curve(s, 1.4, 0.45) + grain(l.shape, 0.03)
    edges = np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2 * K(im))), np.float32) / 255
    s = np.clip(s - edges * 0.9, 0, 1)                                      # the dark Mackie line on contours
    return duotone(s, (12, 12, 14), (226, 224, 220))


def pictorialism(im):
    soft = im.filter(ImageFilter.GaussianBlur(9 * K(im)))
    glow = ImageChops.screen(im, soft)
    mix = Image.blend(im, glow, 0.55).filter(ImageFilter.GaussianBlur(1.1 * K(im)))
    l = curve(lum(mix), 0.85, 0.5) * 0.92 + 0.05
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    l = np.clip(l * np.clip(vig, 0, 1) + grain(l.shape, 0.03), 0, 1)
    return duotone(l, (34, 24, 18), (232, 214, 186))


def dither(im):
    """S8: error-diffusion dither (Floyd-Steinberg), platinum dots on warm black (mood M2)."""
    px = max(1, round(2 * K(im)))
    l = printable(im, 0.45, 0.9)
    W, H = im.size
    small = to_img(l).resize((max(1, W // px), max(1, H // px)), Image.LANCZOS)
    dots = small.convert("1", dither=Image.FLOYDSTEINBERG).convert("L").resize((W, H), Image.NEAREST)
    return duotone(np.asarray(dots, np.float32) / 255, (15, 13, 12), (214, 209, 200))


def scanlines(im):
    """S9: modulated lines. Horizontal bands; the brighter the photo, the thicker the line."""
    band = max(4, round(8 * K(im)))
    l = printable(im.filter(ImageFilter.GaussianBlur(1.0 * K(im))), 0.35, 1.15)
    H, W = l.shape
    rows = np.arange(H)
    starts = (rows // band) * band
    means = np.add.reduceat(l, np.arange(0, H, band), axis=0) / np.diff(np.append(np.arange(0, H, band), H))[:, None]
    v = means[rows // band]                                                 # band average, per column
    offset = (rows - starts).astype(np.float32)[:, None] - (band - 1) / 2
    lines = (np.abs(offset) < (v * band * 0.55)).astype(np.float32)
    return duotone(lines, (15, 13, 12), (214, 209, 200))


def pixel(im):
    """S10: big pixels in a small colour palette, like early computer graphics. Keeps colour."""
    px = max(4, round(6 * K(im)))
    W, H = im.size
    small = im.convert("RGB").resize((max(1, W // px), max(1, H // px)), Image.LANCZOS)
    q = small.quantize(colors=12, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    return q.convert("RGB").resize((W, H), Image.NEAREST)


# --- S11-S20: added 2026-10-14 (Amir: "add all 10"), candidates until he keeps them on his photo ---

def _arr(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255


def _blur(a, r):
    return np.asarray(to_img_rgb(a).filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def to_img_rgb(a):
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def halation(im):
    """S11: film halation. A soft red-orange glow bleeds out of the bright edges; blacks stay deep."""
    a = _arr(im); l = lum(im)
    hi = np.clip((l - 0.62) / 0.38, 0, 1)
    glow = np.asarray(to_img(hi).filter(ImageFilter.GaussianBlur(14 * K(im))), np.float32) / 255
    wide = np.asarray(to_img(hi).filter(ImageFilter.GaussianBlur(40 * K(im))), np.float32) / 255
    tint = np.array([1.0, 0.36, 0.18], np.float32)
    halo = np.clip(glow * 0.9 + wide * 0.5 - hi, 0, 1)                       # the glow lives just outside the bright areas
    out = 1 - (1 - a) * (1 - halo[..., None] * tint[None, None, :])
    out = out * 0.96 + grain(l.shape, 0.025)[..., None]
    return to_img_rgb(out)


def window(im):
    """S12: seen through old dirty glass (Lucas Garcete's method): blotches, dust, scratches, lifted blacks."""
    a = _arr(im); H, W = a.shape[:2]
    low = rng.random((max(2, H // 90), max(2, W // 90))).astype(np.float32)
    low = np.asarray(Image.fromarray((low * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(20 * K(im))), np.float32) / 255
    smudge = np.clip((low - 0.45) * 2.2, 0, 1)
    dust = Image.new("L", (W, H), 0); d = ImageDraw.Draw(dust)
    for _ in range(int(900 * K(im) ** 2)):
        x, y = rng.integers(0, W), rng.integers(0, H); r = rng.random() * 2.4 * K(im) + 0.4
        d.ellipse((x - r, y - r, x + r, y + r), fill=int(120 + rng.random() * 135))
    for _ in range(int(14 * K(im))):
        x = rng.integers(0, W); y = rng.integers(0, H); L = rng.integers(40, 260) * K(im); ang = rng.random() * np.pi
        d.line((x, y, x + L * np.cos(ang), y + L * np.sin(ang)), fill=int(90 + rng.random() * 80), width=1)
    dust = np.asarray(dust.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    out = a * (1 - smudge[..., None] * 0.22) + smudge[..., None] * 0.10      # haze in the smudges
    out = out * 0.88 + 0.07                                                     # glass lifts the blacks
    out = out * (1 - dust[..., None] * 0.55) + (dust[..., None] * 0.35) * (low[..., None] > 0.5)
    out = _blur(out, 0.6 * K(im)) + grain(a.shape[:2], 0.035)[..., None]
    return to_img_rgb(out)


def crt(im):
    """S13: a CRT screen: the picture built from red, green and blue phosphor stripes with dark scanlines and bloom."""
    cell = max(3, round(4 * K(im)))
    W, H = im.size
    small = im.convert("RGB").resize((max(1, W // cell), max(1, H // cell)), Image.LANCZOS)
    big = np.asarray(small.resize((W, H), Image.NEAREST), np.float32) / 255
    xx = (np.arange(W) % cell)[None, :]; yy = (np.arange(H) % cell)[:, None]
    mask = np.zeros((H, W, 3), np.float32)
    third = cell / 3
    for c in range(3):
        mask[..., c] = ((xx >= c * third) & (xx < (c + 1) * third)).astype(np.float32)
    mask *= (yy < cell - max(1, cell // 3))[..., None]
    out = big * mask * 3.4
    bloom = _blur(np.clip(out, 0, 1), 3 * K(im))
    out = np.clip(out * 0.8 + bloom * 0.9, 0, 1)
    return to_img_rgb(out)


def softclub(im):
    """S14: Gen X Softclub: cold blue-cyan, soft focus, digital artefacts, archive grain; nothing dramatic."""
    l = curve(lum(im.filter(ImageFilter.GaussianBlur(1.6 * K(im)))), 0.8, 0.5) * 0.9 + 0.06
    W, H = im.size
    blocky = np.asarray(to_img(l).resize((max(1, W // 3), max(1, H // 3)), Image.BILINEAR).resize((W, H), Image.NEAREST), np.float32) / 255
    l = l * 0.7 + blocky * 0.3
    out = duotone(np.clip(l + grain(l.shape, 0.045), 0, 1), (18, 36, 58), (190, 222, 230))
    return out


def emboss(im):
    """S15: pressed relief, like a blind emboss in paper: grey on grey, light from the top left."""
    g = im.convert("L").filter(ImageFilter.GaussianBlur(1.2 * K(im)))
    e = np.asarray(g.filter(ImageFilter.EMBOSS), np.float32) / 255
    e = curve(e, 1.6, 0.5) * 0.55 + curve(lum(im), 0.9, 0.5) * 0.45         # relief plus a little of the form
    return duotone(np.clip(e + grain(e.shape, 0.02), 0, 1), (120, 114, 106), (232, 228, 220))


ASCII_RAMP = " .,:;irsXA253hMHGS#9B&@"


def ascii_art(im):
    """S16: the picture rebuilt from text characters, ink on paper."""
    cell = max(6, round(10 * K(im)))
    W, H = im.size
    cols, rows = max(1, W // cell), max(1, H // (cell * 2) * 2 // 2)
    rows = max(1, H // round(cell * 1.6))
    l = np.asarray(im.convert("L").resize((cols, rows), Image.LANCZOS), np.float32) / 255
    l = curve(l, 1.3, 0.5)
    out = Image.new("RGB", (W, H), (214, 209, 200)); d = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", round(cell * 1.15))
    except OSError:
        f = ImageFont.load_default()
    ch = H / rows
    for y in range(rows):
        for x in range(cols):
            k = int((1 - l[y, x]) * (len(ASCII_RAMP) - 1))
            if k:
                d.text((x * cell, y * ch), ASCII_RAMP[k], font=f, fill=(15, 13, 12))
    return out


def vhs(im):
    """S17: a VHS tape: soft chroma, a cold teal cast, faint vertical screen lines, tracking lines,
    tape noise. Tuned 2026-10-22 toward the R-019 tape look (less bleed, teal, screen lines); the
    render before the tuning is kept as examples/look-vhs-before-2026-10-22.jpg."""
    a = _arr(im); H, W = a.shape[:2]
    s = max(1, round(2 * K(im)))                                            # was 4: less colour bleed
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], s, axis=1); out[..., 2] = np.roll(a[..., 2], -s, axis=1)
    soft = np.asarray(to_img_rgb(out).filter(ImageFilter.BoxBlur(2 * K(im))), np.float32) / 255
    l = (out[..., 0] * .299 + out[..., 1] * .587 + out[..., 2] * .114)[..., None]
    out = l * 0.45 + soft * 0.55
    out = curve(out, 0.9, 0.5) * np.array([0.86, 1.0, 1.02])                # was 1.0 / 0.97 / 1.03: teal, not neutral
    out = out * (1 - 0.08 * ((np.arange(W) % max(2, round(3 * K(im)))) == 0))[None, :, None]   # faint vertical screen lines
    for _ in range(int(6 * K(im))):
        y = int(rng.integers(0, H)); h = int(rng.integers(2, 6) * K(im) + 1); dx = int(rng.integers(-12, 12) * K(im))
        out[y:y + h] = np.roll(out[y:y + h], dx, axis=1) * 1.1
    band = int(rng.integers(0, H)); out[band:band + int(18 * K(im))] += rng.random((min(H, band + int(18 * K(im))) - band, W, 1)) * 0.25
    out = out + grain(a.shape[:2], 0.04)[..., None]
    return to_img_rgb(out)


def anaglyph(im):
    """S18: red / cyan 3D: the left eye in red, the right eye in cyan, slightly apart."""
    l = lum(im); s = max(3, round(9 * K(im)))
    left = np.roll(l, -s, axis=1); right = np.roll(l, s, axis=1)
    out = np.stack([left, right, right], -1)
    return to_img_rgb(curve(out, 1.1, 0.5))


IRON = [(0, (0, 0, 10)), (0.2, (40, 0, 90)), (0.4, (150, 0, 140)), (0.6, (230, 70, 30)), (0.8, (250, 180, 0)), (1, (255, 255, 230))]


def thermal(im):
    """S19: a heat camera: the 'iron' palette, black and violet for cold, orange and white for hot."""
    l = curve(lum(im.filter(ImageFilter.GaussianBlur(2.5 * K(im)))), 1.2, 0.5)
    xs = np.array([p for p, _ in IRON]); cs = np.array([c for _, c in IRON], np.float32) / 255
    out = np.stack([np.interp(l, xs, cs[:, c]) for c in range(3)], -1)
    return to_img_rgb(out)


def nightvision(im):
    """S20: night vision: green phosphor, glowing highlights, noise, faint scanlines, dark edges."""
    l = curve(lum(im), 1.25, 0.42)
    glow = np.asarray(to_img(l).filter(ImageFilter.GaussianBlur(5 * K(im))), np.float32) / 255
    l = np.clip(l * 0.85 + glow * 0.35 + grain(l.shape, 0.07), 0, 1)
    H, W = l.shape
    l = l * (1 - 0.18 * ((np.arange(H) % max(2, round(3 * K(im)))) == 0))[:, None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    l = l * np.clip(1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0, 1)
    return duotone(l, (2, 12, 4), (170, 255, 140))


# --- S21-S23: added 2026-10-22 from R-019 (_kodam4_ / echo angel), Amir picked group A ---

def pixelsort(im):
    """S21: pixel-sort streaks. In every row, the bright runs are sorted by brightness, so skies
    and lights drag sideways into stripes; the dark parts of the picture stay put."""
    a = np.asarray(im.convert("RGB"))
    l = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(2 * K(im))), np.float32) / 255
    thr = np.quantile(l, 0.45)                                              # the brighter half gets sorted
    out = a.copy()
    key = a.astype(np.float32) @ np.array([.299, .587, .114], np.float32)
    for y in range(a.shape[0]):
        on = np.concatenate(([0], (l[y] > thr).astype(np.int8), [0]))
        edges = np.flatnonzero(np.diff(on))
        for x0, x1 in zip(edges[::2], edges[1::2]):
            if x1 - x0 > 2:
                order = np.argsort(-key[y, x0:x1], kind="stable")             # brightest first: the light drags left
                out[y, x0:x1] = a[y, x0:x1][order]
    return Image.fromarray(out)


def blowout(im):
    """S22: blown-out silhouette. Highlights clip to white, everything darker becomes one violet
    silhouette with horizontal line bands through it, like an overexposed phone clip."""
    l = lum(im.filter(ImageFilter.GaussianBlur(1.0 * K(im))))
    white = np.clip((l - 0.42) / 0.18, 0, 1)                                # hard clip with a short ramp
    violet = np.array((20, 17, 86), np.float32) / 255                       # measured on the R-019 EP4 reel
    lilac = np.array((120, 96, 210), np.float32) / 255
    H, W = l.shape
    band = max(3, round(6 * K(im)))
    rows = (np.arange(H) // band) % 3 == 0                                  # every third band is lifted
    lift = np.where(rows, 0.35, 0.0)[:, None] * (1 - white)
    body = violet[None, None, :] + (lilac - violet)[None, None, :] * np.clip(l / 0.42 * 0.6 + lift, 0, 1)[..., None]
    out = body * (1 - white[..., None]) + white[..., None]
    out = _blur(out, 0.5 * K(im)) + grain(l.shape, 0.02)[..., None]
    return to_img_rgb(out)


MONOTINT = (112, 115, 164)                                                  # periwinkle, measured on the echo angel reel
MONOTINT_NIGHT = (12, 138, 146)                                             # teal, measured on the R-019 "12/31" post


def monotint(im, night=False):
    """S23: monotint wash. One colour laid over the whole picture, a little of the original colour
    left in; the same tint on every image makes a set read as one world. The night setting (S23b)
    is one saturated hue on deep black, the R-019 night pictures."""
    a = _arr(im); l = lum(im)
    if night:
        tint = np.array(MONOTINT_NIGHT, np.float32) / 255
        l = curve(l, 1.25, 0.40) ** 0.95                                    # deep black floor, hue only in the light
        washed = np.clip(tint[None, None, :] * 1.7 * l[..., None] + np.clip(l - 0.75, 0, 1)[..., None] * 1.4, 0, 1)
        return to_img_rgb(washed + grain(l.shape, 0.025)[..., None])
    tint = np.array(MONOTINT, np.float32) / 255
    washed = np.clip(tint[None, None, :] * (0.35 + 1.15 * l[..., None]), 0, 1)
    out = washed * 0.8 + a * 0.2
    return to_img_rgb(out + grain(l.shape, 0.02)[..., None])


def monotint_night(im):
    return monotint(im, night=True)


# --- S24-S25: added 2026-10-22 from R-019 second pass (his picks: the face flash, the cold vintage) ---

def nightflash(im):
    """S24: night flash. A direct on-camera flash at night: the subject near the lens blows out to
    white with a soft bloom, light falls off fast, the background drops into a cold dark."""
    a = _arr(im); l = lum(im); H, W = l.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    soft = np.asarray(to_img(l).filter(ImageFilter.GaussianBlur(6 * K(im))), np.float32) / 255
    rough = np.asarray(to_img(np.abs(l - soft) * 4).filter(ImageFilter.GaussianBlur(10 * K(im))), np.float32) / 255
    sky = np.clip((soft - 0.55) / 0.2, 0, 1) * np.clip(1 - rough * 6, 0, 1)   # bright and smooth = far away, the flash never reaches it
    sky = np.asarray(to_img(sky).filter(ImageFilter.GaussianBlur(8 * K(im))), np.float32) / 255
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 0.36 * H) / H) ** 2)    # the subject sits near the centre, head in the upper third
    light = np.exp(-(d / 0.26) ** 2) * (1 - sky)                           # flash falloff around the subject
    out = a * (0.32 + 2.6 * light[..., None])                               # near: overexposed; far and sky: dark ambient
    warm = np.array([1.08, 0.98, 0.74], np.float32)                         # the flash itself is warm yellow (Amir 2026-10-22: "too fluorescent"; a yellower try was reverted)
    cold = np.array([0.92, 1.0, 1.04], np.float32)                          # the ambient stays cold, measured 13 of 19 green-teal
    out = out * (cold + (warm - cold) * light[..., None])
    hot = np.clip((out.mean(-1) - 0.85) / 0.15, 0, 1)
    bloom = np.asarray(to_img(hot).filter(ImageFilter.GaussianBlur(18 * K(im))), np.float32) / 255
    out = np.clip(out, 0, 1) + bloom[..., None] * 0.6 * np.array([1.0, 0.9, 0.62])   # yellow glow around the burn
    return to_img_rgb(out + grain(l.shape, 0.03)[..., None])


def camcorder(im):
    """S25: camcorder. The milky day picture of the R-019 vintage: green-teal mids, blacks lifted
    to grey, little colour, soft focus, a rainbow light leak, fine tape grain. Cold, never golden."""
    a = _arr(im); l = lum(im); H, W = l.shape
    g = l[..., None]
    out = g + (a - g) * 0.35                                                # saturation down to about a third
    out = out * 0.78 + 0.16                                                 # black floor near 40 of 255, measured 28 to 82
    out = out * np.array([0.93, 1.0, 0.98])                                 # green-teal mids
    out = _blur(out, 1.4 * K(im))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - 0.82 * W) / W) ** 2 + ((yy - 0.12 * H) / H) ** 2)
    leak = np.exp(-(r / 0.28) ** 2)
    hue = (np.arctan2(yy - 0.12 * H, xx - 0.82 * W) / np.pi + 1) / 2        # a rainbow fan around the leak
    rainbow = np.stack([0.5 + 0.5 * np.cos(2 * np.pi * (hue + o)) for o in (0, 1 / 3, 2 / 3)], -1)
    out = 1 - (1 - out) * (1 - leak[..., None] * (0.25 + 0.25 * rainbow))  # screen the leak in
    return to_img_rgb(out + grain(l.shape, 0.035)[..., None])


def mosaic(im, box, cell=None):
    """Pixel mosaic over one box (x, y, w, h), as R-019 hides other people's faces. Only ever on
    other people in the frame, never on Amir's own face."""
    x, y, w, h = box
    cell = cell or max(6, round(min(w, h) / 6))
    out = im.copy()
    part = out.crop((x, y, x + w, y + h))
    small = part.resize((max(1, w // cell), max(1, h // cell)), Image.BILINEAR)
    out.paste(small.resize((w, h), Image.NEAREST), (x, y))
    return out


# id -> (library code, display name, one-line note, function)
LOOKS = {
    "xerox":        ("S1", "Xerox", "photocopy degradation", xerox),
    "halftone":     ("S2", "Halftone", "blown-up newspaper dot", halftone),
    "riso":         ("S3", "Riso", "two inks, off register", riso),
    "engraving":    ("S4", "Engraving", "line and cross-hatch", engraving),
    "cyanotype":    ("S5", "Cyanotype", "Prussian blue sun print", cyanotype),
    "solarisation": ("S6", "Solarisation", "darkroom tone reversal", solarisation),
    "pictorialism": ("S7", "Pictorialism", "soft-focus platinum print", pictorialism),
    "dither":       ("S8", "Dither", "fine dots, platinum on warm black", dither),
    "scanlines":    ("S9", "Scanlines", "modulated horizontal lines", scanlines),
    "pixel":        ("S10", "Pixel", "big pixels, 12 colours", pixel),
    "halation":     ("S11", "Halation", "red glow from the bright edges", halation),
    "window":       ("S12", "Dirty window", "through old dirty glass", window),
    "crt":          ("S13", "CRT", "phosphor stripes and scanlines", crt),
    "softclub":     ("S14", "Softclub", "cold blue, soft, archive grain", softclub),
    "emboss":       ("S15", "Emboss", "pressed relief in paper", emboss),
    "ascii":        ("S16", "ASCII", "built from text characters", ascii_art),
    "vhs":          ("S17", "VHS", "tape colour bleed and tracking", vhs),
    "anaglyph":     ("S18", "Anaglyph 3D", "red and cyan offset", anaglyph),
    "thermal":      ("S19", "Thermal", "heat camera colours", thermal),
    "nightvision":  ("S20", "Night vision", "green phosphor", nightvision),
    "pixelsort":    ("S21", "Pixel sort", "bright runs dragged into stripes", pixelsort),
    "blowout":      ("S22", "Blowout", "white sky, violet silhouette", blowout),
    "monotint":     ("S23", "Monotint", "one periwinkle wash over all", monotint),
    "monotintnight": ("S23b", "Monotint night", "one teal hue on deep black", monotint_night),
    "nightflash":   ("S24", "Night flash", "face blown white, dark falloff", nightflash),
    "camcorder":    ("S25", "Camcorder", "milky, cold, light leak", camcorder),
}


def load(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def apply_look(im: Image.Image, look: str) -> Image.Image:
    """Return the photo put through one named look. Same size as the input."""
    if look not in LOOKS:
        raise ValueError(f"Unknown look '{look}'. Looks: {', '.join(LOOKS)}")
    global rng
    rng = np.random.default_rng(SEED)      # same photo in, same print out
    return LOOKS[look][3](im).convert("RGB")


def sheet(im: Image.Image, out: Path, tile_w: int = 500) -> Path:
    """All looks on one numbered sheet, to pick by eye."""
    work = im.copy()
    work.thumbnail((1000, 3000), Image.LANCZOS)
    tiles = [("0", "Original", "as it came", work)]
    for key, (code, name, note, _) in LOOKS.items():
        tiles.append((code, name, note, apply_look(work, key)))
    th = round(tile_w * work.size[1] / work.size[0])
    pad, lab, cols = 22, 58, 4
    rows = (len(tiles) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * (tile_w + pad) + pad, rows * (th + lab + pad) + pad), (15, 13, 12))
    d = ImageDraw.Draw(canvas)
    big = ImageFont.truetype(str(FONT), 34) if FONT.is_file() else ImageFont.load_default()
    small = ImageFont.truetype(str(FONT), 20) if FONT.is_file() else ImageFont.load_default()
    for i, (code, name, note, tile) in enumerate(tiles):
        x = pad + (i % cols) * (tile_w + pad)
        y = pad + (i // cols) * (th + lab + pad)
        d.text((x, y), f"{code}   {name}", font=big, fill=(214, 209, 200))
        d.text((x + 2, y + 36), note, font=small, fill=(150, 146, 140))
        canvas.paste(tile.resize((tile_w, th), Image.LANCZOS), (x, y + lab))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=90)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photo", nargs="?", type=Path)
    ap.add_argument("--look", choices=list(LOOKS))
    ap.add_argument("--sheet", action="store_true", help="all looks on one numbered sheet")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--mosaic", metavar="X,Y,W,H", action="append", default=[],
                    help="pixel mosaic over a box after the look; other people only, never Amir's face (repeatable)")
    a = ap.parse_args()

    if a.list:
        for key, (code, name, note, _) in LOOKS.items():
            print(f"  {code}  {key:<13} {name}: {note}")
        return
    if not a.photo or not a.photo.is_file():
        sys.exit("Give a photo, or use --list")
    if not (a.look or a.sheet):
        sys.exit("Choose --look NAME or --sheet")

    im = load(a.photo)
    out_dir = Path("styled")
    if a.sheet:
        out = a.out or out_dir / f"{a.photo.stem}_looks-sheet.jpg"
        print(f"sheet written: {sheet(im, out)}")
        return
    out = a.out or out_dir / f"{a.photo.stem}_{a.look}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    styled = apply_look(im, a.look)
    for spec in a.mosaic:
        try:
            box = tuple(int(v) for v in spec.split(","))
        except ValueError:
            sys.exit(f"--mosaic wants X,Y,W,H in pixels, got '{spec}'")
        if len(box) != 4 or box[2] < 1 or box[3] < 1:
            sys.exit(f"--mosaic wants X,Y,W,H in pixels, got '{spec}'")
        styled = mosaic(styled, box)
    styled.save(out, quality=95)
    code, name, _, _ = LOOKS[a.look]
    print(f"{code} {name}: {out}  ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    main()
