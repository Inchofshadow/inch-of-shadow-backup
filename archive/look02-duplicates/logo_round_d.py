"""Look-02 round D: other KINDS of mark, made from his name, his music, himself. Local only.

No religious or borrowed symbols (Amir, 2026-09-21). No eclipse, no inch mark (they stay keepers).
"""
import math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
import logo_round_b as B
from logo_sketches import blank, done, disc, K, FUT, MARC, INK, GROUND, S

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
TRACK = "/Users/amir/Desktop/Inch of Shadow/youtube/assets/audio/Inch of Shadow - The Deceiver (Indigo Children Records).wav"


def shift(m, dx, dy):
    """Move a mask without wrapping round the edges (ImageChops.offset wraps)."""
    out = Image.new("L", m.size, 0); out.paste(m, (int(dx), int(dy))); return out


def text_mask(W, lines, font_path, index=0, width=0.84, gap=0.05, widths=None):
    """Stacked lines of capitals, each line set to the same width, centred in a W x W mask."""
    m = Image.new("L", (W, W), 0); d = ImageDraw.Draw(m)
    sized = []
    for i, ln in enumerate(lines):
        f0 = ImageFont.truetype(font_path, 100, index=index); b = d.textbbox((0, 0), ln, font=f0)
        size = int(100 * W * (widths[i] if widths else width) / (b[2] - b[0])); f = ImageFont.truetype(font_path, size, index=index)
        bb = d.textbbox((0, 0), ln, font=f); sized.append((ln, f, bb))
    total = sum(bb[3] - bb[1] for _, _, bb in sized) + gap * W * (len(sized) - 1)
    y = (W - total) / 2
    for ln, f, bb in sized:
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), ln, font=f, fill=255); y += bb[3] - bb[1] + gap * W
    return m


def shadow_only(n):
    """The name drawn ONLY by its shadow: the letters themselves are not there, you read them from the dark."""
    W = n * K
    m = text_mask(W, ["INCH", "OF", "SHADOW"], FUT, 2, gap=0.05, widths=[0.62, 0.30, 0.84])
    m = shift(m, -W * 0.015, -W * 0.015)
    sh = shift(m, W * 0.03, W * 0.03)
    return done(ImageChops.subtract(sh, m.filter(ImageFilter.MaxFilter(int(W * 0.004) | 1))), n)


def sinking(n):
    """The name with its lower part gone into shadow: solid above a line, only thin lines below it."""
    W = n * K
    m = text_mask(W, ["Inch of", "Shadow"], MARC, 0, 0.92, 0.02)
    box = m.getbbox(); cut = box[1] + (box[3] - box[1]) * 0.60
    lines = Image.new("L", (W, W), 0); d = ImageDraw.Draw(lines); step = W * 0.022
    y = cut
    while y < W:
        d.rectangle((0, y, W, y + step * max(0.12, 0.55 - (y - cut) / (W * 0.5))), fill=255); y += step
    top = Image.new("L", (W, W), 0); ImageDraw.Draw(top).rectangle((0, 0, W, cut - W * 0.01), fill=255)
    return done(ImageChops.lighter(ImageChops.multiply(m, top), ImageChops.multiply(m, lines)), n)


def sound(n):
    """One second of The Deceiver drawn round a circle: the loudness pushes the line out. A sign found in his own track."""
    W = n * K; c = W / 2
    w = wave.open(TRACK); rate = w.getframerate(); w.setpos(int(rate * 62))
    raw = np.frombuffer(w.readframes(rate * 2), dtype=np.uint8).reshape(-1, 3)
    x = (raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16))
    x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64)
    x = x.reshape(-1, 2).mean(axis=1) / 8388608.0
    n_pts = 360
    env = np.array([np.sqrt(np.mean(x[i * len(x) // n_pts:(i + 1) * len(x) // n_pts] ** 2)) for i in range(n_pts)])
    env = np.convolve(np.r_[env[-3:], env, env[:3]], np.ones(7) / 7, mode="same")[3:-3]
    env = (env - env.min()) / (env.max() - env.min() + 1e-9)
    m = Image.new("L", (W, W), 0); d = ImageDraw.Draw(m)
    for k in range(n_pts):
        a = 2 * math.pi * k / n_pts - math.pi / 2
        r0 = W * 0.22; r1 = W * (0.26 + 0.22 * env[k])
        d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + r1 * math.cos(a), c + r1 * math.sin(a))], fill=255, width=int(W * 0.006))
    return done(m, n)


def sunglasses(n):
    """His sunglasses, his signature object: two dark lenses and a thin bridge, nothing else."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    for s in (-1, 1):
        cx = c + s * W * 0.22
        d.rounded_rectangle((cx - W * 0.19, W * 0.36, cx + W * 0.19, W * 0.64), radius=W * 0.12, fill=255)
    d.arc((c - W * 0.07, W * 0.37, c + W * 0.07, W * 0.51), 200, 340, fill=255, width=int(W * 0.022))
    return done(m, n)


def the_band(n):
    """An inch of shadow, literally: a light field and, at its foot, one narrow band of dark."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    d.rectangle((W * 0.12, W * 0.08, W * 0.88, W * 0.92), fill=255, outline=None)
    d.rectangle((W * 0.12 + W * 0.02, W * 0.08 + W * 0.02, W * 0.88 - W * 0.02, W * 0.76), fill=0)
    return done(m, n)


def long_shadow(n):
    """The name in Impact, the letters only outlined, each one throwing a long solid shadow down to the right."""
    W = n * K
    m = text_mask(W, ["INCH", "OF", "SHADOW"], IMPACT, 0, gap=0.03, widths=[0.50, 0.24, 0.66])
    m = shift(m, -W * 0.08, -W * 0.08)
    sh = Image.new("L", (W, W), 0)
    for i in range(1, int(W * 0.16), 3):
        sh = ImageChops.lighter(sh, shift(m, i, i))
    outline = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(int(W * 0.008) | 1)))
    body = ImageChops.subtract(sh, m.filter(ImageFilter.MaxFilter(int(W * 0.012) | 1)))
    return done(ImageChops.lighter(outline, body), n)


DIRECTIONS = [
    ("20 THE NAME IN ITS SHADOW", "the letters are not there, only their shadows: you read the name from the dark", shadow_only),
    ("21 THE NAME SINKING", "the name goes into shadow: solid on top, only thin lines below, fading", sinking),
    ("22 THE SOUND", "two seconds of The Deceiver drawn round a circle, the loudness pushing the line out: found in your own music", sound),
    ("23 THE SUNGLASSES", "your signature object as the sign: two dark lenses, a thin bridge", sunglasses),
    ("24 AN INCH OF SHADOW", "the name taken literally: a light field with one narrow band of dark at its foot (it also looks like a Polaroid)", the_band),
    ("25 THE LONG SHADOW", "the name in Impact, the letters only outlined, each throwing a long solid shadow", long_shadow),
]

if __name__ == "__main__":
    A.tshirt, A.photo_corner, A.reel_end = B.tshirt, B.photo_corner, B.reel_end
    rows = []
    for title, why, fn in DIRECTIONS:
        sym = fn(600)
        big = A.colorize(sym.resize((380, 380), Image.LANCZOS), GROUND, (236, 232, 224))
        wm = A.wordmark(430, sym, False)
        wm_img = Image.new("RGB", (470, 380), (236, 232, 224)); wm_img.paste(GROUND, (20, (380 - wm.height) // 2), wm)
        row = Image.new("RGB", (2330, 720), (24, 24, 24)); d = ImageDraw.Draw(row)
        A.label(d, (30, 18), title, 40, (240, 200, 140)); A.label(d, (30, 66), why, 26, (190, 190, 190))
        row.paste(big, (30, 110)); row.paste(wm_img, (430, 110))
        row.paste(A.tshirt(sym).resize((440, 474)), (930, 90))
        row.paste(A.photo_corner(sym), (1400, 90)); row.paste(A.reel_end(sym, False), (1745, 90))
        for x, cap in ((30, "the symbol"), (430, "the wordmark (Marcellus for now)"),
                       (930, "T-shirt"), (1400, "signing a photo"), (1745, "last frame of a reel")):
            A.label(d, (x, 668 if x >= 930 else 500), cap, 22, (160, 160, 160))
        rows.append(row)
    for part, chunk in enumerate((rows[:3], rows[3:]), start=1):
        sheet = Image.new("RGB", (2330, 720 * len(chunk)), (24, 24, 24))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, 720 * i))
        sheet.save(S / f"logo_round_d_{part}.jpg", quality=90)
    ov = Image.new("RGB", (len(DIRECTIONS) * 300 + 40, 360), (236, 232, 224)); d = ImageDraw.Draw(ov)
    for i, (title, _, fn) in enumerate(DIRECTIONS):
        g = B.fit(fn(600), 260, 260); ov.paste(GROUND, (40 + i * 300 + (260 - g.width) // 2, 30 + (260 - g.height) // 2), g)
        A.label(d, (40 + i * 300, 305), title.split()[0], 30, (60, 60, 60))
    ov.save(S / "logo_round_d_overview.jpg", quality=92)
    print("ok")
