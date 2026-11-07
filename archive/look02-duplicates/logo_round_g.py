"""Look-02 round G, another last one: six more ways the name can be made or printed. Local only."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
import logo_round_b as B
from logo_round_d import text_mask, shift, IMPACT
from logo_round_e import noise
from logo_sketches import blank, done, K, FUT, MARC, INK, GROUND, S


def halftone(n):
    """The name made of dots; lower down the dots grow and merge into solid shadow."""
    W = n * K
    t = np.asarray(text_mask(W, ["INCH OF", "SHADOW"], FUT, 2, gap=0.04, widths=[0.64, 0.88])).astype(np.float64) / 255
    m = blank(n); d = ImageDraw.Draw(m); step = int(W * 0.018)
    ys = np.nonzero(t.max(axis=1))[0]; top, bot = ys.min(), ys.max()
    for y in range(0, W, step):
        grow = min(1.0, max(0.0, (y - top) / (bot - top)))
        r = step * (0.22 + 0.55 * grow)
        for x in range(0, W, step):
            if t[min(W - 1, y + step // 2), min(W - 1, x + step // 2)] > 0.5:
                cx, cy = x + step / 2, y + step / 2; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    return done(m, n)


def label_tape(n):
    """Embossed label tape, the kind you press letter by letter: raised letters in a black strip. DIY, a pin, a sleeve."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(FUT, int(W * 0.056), index=2); text = "INCH OF SHADOW"
    tw = d.textlength(text, font=f) + W * 0.02 * (len(text) - 1)
    x0 = (W - tw) / 2 - W * 0.05; y0 = W * 0.44; h = W * 0.12
    d.rectangle((x0, y0, x0 + tw + W * 0.10, y0 + h), fill=255)
    for i in range(0, int(tw + W * 0.10), int(W * 0.012)):     # the tape's serrated ends
        pass
    x = x0 + W * 0.05
    for ch in text:
        d.text((x, y0 + h * 0.24), ch, font=f, fill=0); x += d.textlength(ch, font=f) + W * 0.02
    m = m.rotate(-4, resample=Image.BICUBIC)
    return done(m, n)


def glitch(n):
    """The name sliced into bands, each band slipped sideways: a signal breaking, cold and digital."""
    W = n * K
    t = text_mask(W, ["INCH OF", "SHADOW"], FUT, 2, gap=0.04, widths=[0.62, 0.84])
    out = Image.new("L", (W, W), 0); rng = np.random.default_rng(12)
    y = 0
    while y < W:
        h = int(W * rng.uniform(0.012, 0.05)); dx = int(W * rng.normal(0, 0.035)) if rng.random() < 0.6 else 0
        band = t.crop((0, y, W, min(W, y + h))); out.paste(band, (dx, y)); y += h
    return done(out, n)


def weathered(n):
    """The name cut in stone and worn by weather: the edges eaten away, like an old inscription."""
    W = n * K
    t = text_mask(W, ["INCH OF", "SHADOW"], MARC, 0, gap=0.04, widths=[0.70, 0.90])
    soft = np.asarray(t.filter(ImageFilter.GaussianBlur(W * 0.006))).astype(np.float64) / 255
    wear = noise(W, 6, 41) * 0.6 + noise(W, 40, 42) * 0.4
    m = (soft + (wear - 0.5) * 0.45) > 0.55
    return done(Image.fromarray((m * 255).astype(np.uint8)), n)


def dot_matrix(n):
    """The name printed by an old dot-matrix printer: round dots on a grid, like a receipt or a ticket."""
    W = n * K; cols = 7 * 7; m = blank(n); d = ImageDraw.Draw(m)
    small = text_mask(700, ["INCH OF", "SHADOW"], FUT, 2, gap=0.08, widths=[0.64, 0.86]).resize((cols, cols), Image.BOX)
    a = np.asarray(small) > 120; step = W / cols
    for yy in range(cols):
        for xx in range(cols):
            if a[yy, xx]:
                cx, cy = (xx + 0.5) * step, (yy + 0.5) * step; r = step * 0.42
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    return done(m, n)


def torn_strip(n):
    """The name on a strip of paper torn from a page: rough torn edges, the letters cut out of it."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    rng = np.random.default_rng(3); top, bot = W * 0.36, W * 0.64
    pts = [(0, top + rng.normal(0, W * 0.006))]
    for x in np.linspace(0, W, 90)[1:]:
        pts.append((x, top + rng.normal(0, W * 0.008)))
    for x in np.linspace(W, 0, 90):
        pts.append((x, bot + rng.normal(0, W * 0.008)))
    d.polygon(pts, fill=255)
    t = text_mask(W, ["INCH OF SHADOW"], IMPACT, 0, 0.82)
    m = ImageChops.subtract(m, t).rotate(3, resample=Image.BICUBIC)
    return done(m, n)


DIRECTIONS = [
    ("38 THE HALFTONE", "the name made of dots; lower down the dots grow and merge into solid shadow", halftone),
    ("39 THE LABEL TAPE", "embossed label tape pressed letter by letter: raised letters in a black strip, DIY", label_tape),
    ("40 THE GLITCH", "the name sliced into bands that slip sideways: a signal breaking, cold and digital", glitch),
    ("41 THE WEATHERED STONE", "the name cut in stone and worn by weather, like an old inscription", weathered),
    ("42 THE DOT MATRIX", "printed by an old dot-matrix printer: round dots on a grid, a ticket, a receipt", dot_matrix),
    ("43 THE TORN STRIP", "a strip torn from a page with the name cut out of it: rough edges, paper", torn_strip),
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
        for x, cap in ((30, "the logo"), (430, "the plain wordmark (Marcellus for now)"),
                       (930, "T-shirt"), (1400, "signing a photo"), (1745, "last frame of a reel")):
            A.label(d, (x, 668 if x >= 930 else 500), cap, 22, (160, 160, 160))
        rows.append(row)
    for part, chunk in enumerate((rows[:3], rows[3:]), start=1):
        sheet = Image.new("RGB", (2330, 720 * len(chunk)), (24, 24, 24))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, 720 * i))
        sheet.save(S / f"logo_round_g_{part}.jpg", quality=90)
    ov = Image.new("RGB", (len(DIRECTIONS) * 300 + 40, 360), (236, 232, 224)); d = ImageDraw.Draw(ov)
    for i, (title, _, fn) in enumerate(DIRECTIONS):
        g = B.fit(fn(600), 260, 260); ov.paste(GROUND, (40 + i * 300 + (260 - g.width) // 2, 30 + (260 - g.height) // 2), g)
        A.label(d, (40 + i * 300, 305), title.split()[0], 30, (60, 60, 60))
    ov.save(S / "logo_round_g_overview.jpg", quality=92)
    print("ok")
