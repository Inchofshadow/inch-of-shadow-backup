"""Look-02 round F, the last one: the NAME itself as the logo, six ways. Local only."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
import logo_round_b as B
from logo_round_d import text_mask, shift, IMPACT
from logo_sketches import blank, done, K, FUT, MARC, INK, GROUND, S


def neon(n):
    """The name as a neon sign: one hollow tube per letter, light in the dark."""
    W = n * K
    t = text_mask(W, ["Inch of", "Shadow"], MARC, 0, 0.88, 0.04)
    tube = ImageChops.subtract(t.filter(ImageFilter.MaxFilter(int(W * 0.010) | 1)), t.filter(ImageFilter.MinFilter(int(W * 0.006) | 1)))
    return done(tube, n)


def knockout(n):
    """A solid black block with the name cut out of it: the light comes through the letters."""
    W = n * K; m = blank(n); ImageDraw.Draw(m).rectangle((W * 0.04, W * 0.22, W * 0.96, W * 0.78), fill=255)
    t = text_mask(W, ["INCH OF", "SHADOW"], FUT, 2, gap=0.035, widths=[0.58, 0.76])
    return done(ImageChops.subtract(m, t), n)


def column(n):
    """The name standing up, one letter under the other, like the spine of a record."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    letters = list("INCHOFSHADOW"); f = ImageFont.truetype(FUT, int(W * 0.074), index=2)
    y = W * 0.03; step = W * 0.078
    for i, ch in enumerate(letters):
        if i in (4, 6):
            y += step * 0.35                                   # a small breath between the words
        b = d.textbbox((0, 0), ch, font=f); d.text((W / 2 - (b[2] - b[0]) / 2 - b[0], y - b[1]), ch, font=f, fill=255); y += step
    return done(m, n)


def reflection(n):
    """The name and its reflection below it, fading as if in dark water: like the Pieta on The Deceiver."""
    W = n * K
    t = text_mask(W, ["Inch of Shadow"], MARC, 0, 0.90)
    t = shift(t, 0, -W * 0.12)
    box = t.getbbox(); h = box[3] - box[1]
    mirror = t.crop(box).transpose(Image.FLIP_TOP_BOTTOM)
    fade = Image.linear_gradient("L").resize(mirror.size).point(lambda v: int(v * 0.0)).transpose(Image.FLIP_TOP_BOTTOM)
    lines = Image.new("L", mirror.size, 0); d = ImageDraw.Draw(lines)
    for y in range(0, mirror.height, max(2, int(W * 0.010))):
        frac = y / mirror.height
        d.rectangle((0, y, mirror.width, y + max(1, int(W * 0.008 * (1 - frac) ** 1.5))), fill=255)
    refl = ImageChops.multiply(mirror, lines)
    t.paste(255, (box[0], box[3] + int(W * 0.02)), refl)
    return done(t, n)


def light_and_shadow(n):
    """The words themselves split: INCH OF solid in the light, SHADOW only an outline."""
    W = n * K
    top = text_mask(W, ["INCH OF", "      "], FUT, 2, gap=0.04, widths=[0.62, 0.01])
    bottom = text_mask(W, ["       ", "SHADOW"], FUT, 2, gap=0.04, widths=[0.01, 0.86])
    top = text_mask(W, ["INCH OF", "SHADOW"], FUT, 2, gap=0.04, widths=[0.62, 0.86])
    box = top.getbbox(); mid = (box[1] + box[3]) / 2
    upper = Image.new("L", (W, W), 0); ImageDraw.Draw(upper).rectangle((0, 0, W, mid), fill=255)
    solid = ImageChops.multiply(top, upper)
    lower = ImageChops.invert(upper)
    ring = ImageChops.subtract(top, top.filter(ImageFilter.MinFilter(int(W * 0.010) | 1)))
    return done(ImageChops.lighter(solid, ImageChops.multiply(ring, lower)), n)


def diagonal(n):
    """Heavy condensed italic capitals rising on a diagonal: the energy of your reference 38 (The Cure, 1985)."""
    W = n * K
    f = ImageFont.truetype(FUT, 100, index=4); tmp = Image.new("L", (10, 10)); d = ImageDraw.Draw(tmp)
    text = "INCHOFSHADOW"; b = d.textbbox((0, 0), text, font=f)
    size = int(100 * W * 1.05 / (b[2] - b[0])); f = ImageFont.truetype(FUT, size, index=4)
    strip = Image.new("L", (int(W * 1.3), int(size * 1.6)), 0); ds = ImageDraw.Draw(strip)
    x = W * 0.05
    for ch in text:
        ds.text((x, size * 0.2), ch, font=f, fill=255); x += ds.textlength(ch, font=f) * 0.94     # letters close up
    strip = strip.crop(strip.getbbox())
    strip = strip.transform((strip.width + strip.height, strip.height), Image.AFFINE, (1, 0.32, -strip.height * 0.32, 0, 1, 0), Image.BICUBIC)
    strip = strip.rotate(28, expand=True, resample=Image.BICUBIC)
    m = blank(n); g = strip.crop(strip.getbbox()); k = min(W * 0.96 / g.width, W * 0.96 / g.height)
    g = g.resize((int(g.width * k), int(g.height * k)), Image.LANCZOS)
    m.paste(255, ((W - g.width) // 2, (W - g.height) // 2), g)
    return done(m, n)


DIRECTIONS = [
    ("32 THE NEON", "the name as a neon sign: hollow tubes of light in the dark", neon),
    ("33 THE CUT-OUT", "a solid block with the name cut out of it: the light comes through the letters", knockout),
    ("34 THE COLUMN", "the name standing up, letter under letter, like the spine of a record", column),
    ("35 THE REFLECTION", "the name and its reflection fading below it, as in dark water: like the statue on The Deceiver", reflection),
    ("36 LIGHT AND SHADOW", "the words split: INCH OF solid in the light, SHADOW only an outline", light_and_shadow),
    ("37 THE DIAGONAL", "heavy condensed italic rising on a diagonal: the energy of your Cure reference (38)", diagonal),
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
        sheet.save(S / f"logo_round_f_{part}.jpg", quality=90)
    ov = Image.new("RGB", (len(DIRECTIONS) * 300 + 40, 360), (236, 232, 224)); d = ImageDraw.Draw(ov)
    for i, (title, _, fn) in enumerate(DIRECTIONS):
        g = B.fit(fn(600), 260, 260); ov.paste(GROUND, (40 + i * 300 + (260 - g.width) // 2, 30 + (260 - g.height) // 2), g)
        A.label(d, (40 + i * 300, 305), title.split()[0], 30, (60, 60, 60))
    ov.save(S / "logo_round_f_overview.jpg", quality=92)
    print("ok")
