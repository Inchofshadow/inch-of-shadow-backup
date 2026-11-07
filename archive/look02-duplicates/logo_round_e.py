"""Look-02 round E: wider still. Rough and hand-made KINDS of mark: printed, cut, sprayed, blotted.

Local only. Nothing borrowed, no religious signs, no eclipse, no inch mark.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
import logo_round_b as B
from logo_round_d import text_mask, shift, IMPACT
from logo_sketches import blank, done, K, FUT, MARC, INK, GROUND, S

CODE = "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/docs/brand/fonts/free/"
OCRB = CODE + "OCR-B-Regular.otf"
COURIER = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
RNG = np.random.default_rng(1027)          # fixed seed: the same sketch every time it is drawn


def noise(W, scale, seed):
    """Smooth random field 0..1, made by blowing up a small random image."""
    r = np.random.default_rng(seed).random((max(2, int(W / scale)),) * 2)
    img = Image.fromarray((r * 255).astype(np.uint8)).resize((W, W), Image.BICUBIC)
    return np.asarray(img).astype(np.float64) / 255


def inkblot(n):
    """An ink blot folded in half: a shadow shape everyone reads something different into. Unique to him."""
    W = n * K
    f = noise(W, 90, 7) * 0.6 + noise(W, 30, 8) * 0.3 + noise(W, 10, 9) * 0.1
    yy, xx = np.mgrid[0:W, 0:W] / W
    fall = np.exp(-(((xx - 0.5) / 0.30) ** 2 + ((yy - 0.52) / 0.36) ** 2))
    half = (f * fall)[:, : W // 2]
    blot = np.hstack([half, half[:, ::-1]])
    m = Image.fromarray(((blot > 0.33) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(W * 0.004)).point(lambda v: 255 if v > 128 else 0)
    return done(m, n)


def stamp(n):
    """A rubber stamp: the name in a box, the ink uneven, the way a label marks its records."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    d.rectangle((W * 0.06, W * 0.24, W * 0.94, W * 0.76), outline=255, width=int(W * 0.03))
    t = text_mask(W, ["INCH OF", "SHADOW"], FUT, 2, gap=0.03, widths=[0.56, 0.74])
    m = ImageChops.lighter(m, t)
    ink = noise(W, 3, 21) * 0.5 + noise(W, 25, 22) * 0.5
    keep = Image.fromarray(((ink > 0.38) * 255).astype(np.uint8))
    m = ImageChops.multiply(m, keep).rotate(-6, resample=Image.BICUBIC)
    return done(m, n)


def stencil(n):
    """A spray stencil: the name in heavy capitals with the bridges a stencil needs, soft overspray at the edges."""
    W = n * K
    t = text_mask(W, ["INCH", "OF", "SHADOW"], IMPACT, 0, gap=0.035, widths=[0.56, 0.26, 0.80])
    bars = Image.new("L", (W, W), 0); d = ImageDraw.Draw(bars)
    box = t.getbbox(); h = box[3] - box[1]
    t = ImageChops.subtract(t, bars)
    spray = t.filter(ImageFilter.GaussianBlur(W * 0.012))
    grain = Image.fromarray(((np.random.default_rng(5).random((W, W)) < np.asarray(spray) / 255 * 0.9) * 255).astype(np.uint8))
    return done(ImageChops.lighter(t, grain), n)


def photocopy(n):
    """The name photocopied too many times: the letters break up, grit everywhere. A post-punk flyer."""
    W = n * K
    t = text_mask(W, ["Inch of", "Shadow"], MARC, 0, 0.90, 0.03)
    blur = np.asarray(t.filter(ImageFilter.GaussianBlur(W * 0.008))).astype(np.float64) / 255
    grit = noise(W, 2, 31) * 0.55 + noise(W, 14, 32) * 0.45
    m = ((blur * 0.9 + (grit - 0.5) * 1.1) > 0.5)
    speck = (noise(W, 3, 34) > 0.985) & (np.random.default_rng(33).random((W, W)) > 0.85)
    return done(Image.fromarray(((m | speck) * 255).astype(np.uint8)), n)


def typewriter(n):
    """Typed on a typewriter, lower case, a full stop: quiet, literary, like a lyric sheet."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(COURIER, int(W * 0.105))
    x0 = W * 0.08; y0 = W * 0.42; x = x0
    for i, ch in enumerate("inch of shadow."):
        dy = RNG.normal(0, W * 0.004); dx = RNG.normal(0, W * 0.002)
        g = Image.new("L", (W, W), 0); ImageDraw.Draw(g).text((x + dx, y0 + dy), ch, font=f, fill=255)
        strength = 0.55 + 0.45 * RNG.random()
        ink = noise(W, 2, 100 + i) > (1 - strength) * 0.8
        m = ImageChops.lighter(m, ImageChops.multiply(g, Image.fromarray((ink * 255).astype(np.uint8))))
        x += d.textlength(ch, font=f)
    return done(m, n)


def bitmap(n):
    """The name at one bit and very few pixels: blocky, cold, a screen in the dark."""
    W = n * K; small = 64
    t = text_mask(small * 8, ["INCH", "OF", "SHADOW"], FUT, 2, gap=0.06, widths=[0.62, 0.30, 0.86]).resize((small, small), Image.BOX)
    t = t.point(lambda v: 255 if v > 110 else 0)
    return done(t.resize((W, W), Image.NEAREST), n)


DIRECTIONS = [
    ("26 THE INK BLOT", "ink folded in half: a shadow shape people read their own things into, and nobody else has it", inkblot),
    ("27 THE STAMP", "a rubber stamp with uneven ink: the name as a mark you press on sleeves, merch, letters", stamp),
    ("28 THE SPRAY", "the name sprayed through a stencil on a wall, soft overspray around every letter: the street, Berlin", stencil),
    ("29 THE PHOTOCOPY", "the name copied until it breaks up: grit, a post-punk flyer, a zine", photocopy),
    ("30 THE TYPEWRITER", "typed, lower case, with a full stop: quiet and literary, like a lyric sheet", typewriter),
    ("31 THE BITMAP", "the name at one bit and very few pixels: blocky and cold, a screen in the dark", bitmap),
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
        sheet.save(S / f"logo_round_e_{part}.jpg", quality=90)
    ov = Image.new("RGB", (len(DIRECTIONS) * 300 + 40, 360), (236, 232, 224)); d = ImageDraw.Draw(ov)
    for i, (title, _, fn) in enumerate(DIRECTIONS):
        g = B.fit(fn(600), 260, 260); ov.paste(GROUND, (40 + i * 300 + (260 - g.width) // 2, 30 + (260 - g.height) // 2), g)
        A.label(d, (40 + i * 300, 305), title.split()[0], 30, (60, 60, 60))
    ov.save(S / "logo_round_e_overview.jpg", quality=92)
    print("ok")
