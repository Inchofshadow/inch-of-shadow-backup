"""Look-02 v3: the two marks refined in four ways each; names 20 and 21 in the faces he pointed at."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import logo_v2 as V
from logo_v2 import W, blank, done, disc, lines_same_height, clean
from logo_sketches import FUT, MARC
from logo_round_d import IMPACT, shift
from logo_round_e import noise
import logo_sketches as A, logo_round_b as B
from logo_sketches import GROUND, S

LIGHT = (236, 232, 224)


# ---------- the eclipse, four refinements ----------
def ecl_a():
    return V.eclipse()


def ecl_b():
    """The shadow rises: the disc sits high, the light is a thin smile at the bottom."""
    m = blank(); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c, c, W * 0.46); disc(d, c, c, W * 0.425, 0)
    disc(d, c, c - W * 0.05, W * 0.355)
    return done(m)


def ecl_c():
    """No ring: a full dark disc, and beside it only a hairline crescent of light, like a moon's edge."""
    m = blank(); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c + W * 0.02, c + W * 0.02, W * 0.38)
    cres = blank(); cd = ImageDraw.Draw(cres)
    disc(cd, c - W * 0.02, c - W * 0.02, W * 0.43); disc(cd, c + W * 0.005, c + W * 0.005, W * 0.43, 0)
    return done(ImageChops.lighter(m, cres))


def ecl_d():
    """The disc pushes out through the ring on one side: the shadow breaks the circle."""
    m = blank(); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c, c, W * 0.44); disc(d, c, c, W * 0.40, 0)
    disc(d, c + W * 0.075, c + W * 0.075, W * 0.36, 0)
    disc(d, c + W * 0.075, c + W * 0.075, W * 0.335)
    return done(m)


# ---------- the inch mark, four refinements ----------
def inch_a():
    return V.inch_mark()


def _pair(poly_fn, outline_px):
    m = blank(); d = ImageDraw.Draw(m)
    p1, p2 = poly_fn()
    d.polygon(p1, fill=255)
    o = blank(); ImageDraw.Draw(o).polygon(p2, fill=255)
    return ImageChops.lighter(m, ImageChops.subtract(o, o.filter(ImageFilter.MinFilter(outline_px | 1))))


def inch_b():
    """Upright, like a typographer's prime: two wedges, wide at the top, narrow at the foot."""
    def polys():
        top, bot = W * 0.12, W * 0.88
        def wedge(cx):
            return [(cx - W * 0.085, top), (cx + W * 0.085, top), (cx + W * 0.03, bot), (cx - W * 0.03, bot)]
        return wedge(W * 0.39), wedge(W * 0.61)
    return done(_pair(polys, int(W * 0.018)))


def inch_c():
    """Slanted wedges: the typographic double prime, the second one only its outline."""
    def polys():
        top, bot = W * 0.12, W * 0.88; sl = (bot - top) * math.tan(math.radians(12))
        def wedge(cx):
            return [(cx - W * 0.08 + sl / 2, top), (cx + W * 0.08 + sl / 2, top), (cx + W * 0.028 - sl / 2, bot), (cx - W * 0.028 - sl / 2, bot)]
        return wedge(W * 0.39), wedge(W * 0.61)
    return done(_pair(polys, int(W * 0.018)))


def inch_d():
    """The shadow stroke drawn with fine lines instead of an outline: one colour, but it reads as grey."""
    base = V.inch_mark()
    W2 = W
    top, h = (W2 - W2 * 0.78) / 2, W2 * 0.78; bw = W2 * 0.13; sl = h * math.tan(math.radians(14)); gap = W2 * 0.07
    x1 = (W2 - (sl + 2 * bw + gap)) / 2; x2 = x1 + bw + gap
    m = blank(); d = ImageDraw.Draw(m)
    d.polygon([(x1 + sl, top), (x1 + sl + bw, top), (x1 + bw, top + h), (x1, top + h)], fill=255)
    fill2 = blank(); ImageDraw.Draw(fill2).polygon([(x2 + sl, top), (x2 + sl + bw, top), (x2 + bw, top + h), (x2, top + h)], fill=255)
    lines = blank(); ld = ImageDraw.Draw(lines); step = int(W2 * 0.02)
    for y in range(0, W2, step):
        ld.rectangle((0, y, W2, y + step * 0.45), fill=255)
    return done(ImageChops.lighter(m, ImageChops.multiply(fill2, lines)))


# ---------- the names in the faces he pointed at ----------
def grit(mask, seed, amount=0.75, soft=0.005):
    blur = np.asarray(mask.filter(ImageFilter.GaussianBlur(W * soft))).astype(np.float64) / 255
    g = noise(W, 2, seed) * 0.6 + noise(W, 16, seed + 1) * 0.4
    return Image.fromarray((((blur + (g - 0.5) * amount) > 0.45) * 255).astype(np.uint8))


def shadow_name(font, index, lines, cap, gap, track):
    t = lines_same_height(lines, font, index, cap, gap, track)
    t = shift(t, -W * 0.012, -W * 0.012)
    return clean(ImageChops.subtract(shift(t, W * 0.024, W * 0.024), t), 5)


def sinking_name(font, index, lines, cap, gap, track):
    t = lines_same_height(lines, font, index, cap, gap, track)
    box = t.getbbox(); rows = np.nonzero(np.asarray(t).max(axis=1))[0]
    second_top = rows[rows > (box[1] + box[3]) / 2].min(); bottom = box[3]
    cut = second_top + (bottom - second_top) * 0.42
    lines_m = blank(); d = ImageDraw.Draw(lines_m); period = W * 0.016; y = cut
    while y < bottom + period:
        k = (y - cut) / (bottom - cut)
        d.rectangle((0, y, W, y + period * max(0.08, 0.72 * max(0.0, 1 - k) ** 1.3)), fill=255); y += period
    solid = blank(); ImageDraw.Draw(solid).rectangle((0, 0, W, cut - W * 0.004), fill=255)
    return ImageChops.lighter(ImageChops.multiply(t, solid), ImageChops.multiply(t, lines_m))


FACES = [
    ("IMPACT", lambda fn: fn(IMPACT, 0, ["INCH", "OF", "SHADOW"], 0.17, 0.035, 0.01)),
    ("IMPACT + PRINT GRIT", lambda fn: grit(fn(IMPACT, 0, ["INCH", "OF", "SHADOW"], 0.17, 0.035, 0.01), 201)),
    ("MARCELLUS + PRINT GRIT (29)", lambda fn: grit(fn(MARC, 0, ["Inch of", "Shadow"], 0.13, 0.06, 0.0), 211)),
]


def tile(sheet, mask, x, y, T, label):
    sheet.paste(LIGHT, (x, y, x + T, y + T)); g = B.fit(mask, T - 70, T - 70)
    sheet.paste(GROUND, (x + (T - g.width) // 2, y + (T - g.height) // 2), g)
    A.label(ImageDraw.Draw(sheet), (x + 6, y + T + 8), label, 22, (220, 220, 220))


def main():
    T = 440; G = 24
    # sheet 1: the marks
    rows = [("THE ECLIPSE", [("A  as v2", ecl_a), ("B  the shadow rises", ecl_b), ("C  no ring, a moon's edge", ecl_c), ("D  the shadow breaks the circle", ecl_d)]),
            ("THE INCH MARK", [("A  as v2", inch_a), ("B  upright wedges", inch_b), ("C  slanted wedges", inch_c), ("D  shadow in fine lines", inch_d)])]
    sh = Image.new("RGB", (4 * T + 5 * G, 90 + 2 * (T + 110)), (24, 24, 24)); d = ImageDraw.Draw(sh)
    A.label(d, (G, 24), "THE MARKS, REFINED", 44, (240, 200, 140))
    for r, (name, items) in enumerate(rows):
        y = 90 + r * (T + 110)
        A.label(d, (G, y), name, 28, (200, 220, 200))
        for i, (lab, fn) in enumerate(items):
            tile(sh, fn(), G + i * (T + G), y + 40, T, lab)
    sh.save(S / "v3_marks.jpg", quality=92)
    # sheet 2: the names in the faces
    rows = [("20  THE NAME IN ITS SHADOW", shadow_name), ("21  THE NAME SINKING", sinking_name)]
    sh = Image.new("RGB", (3 * T + 4 * G, 90 + 2 * (T + 110)), (24, 24, 24)); d = ImageDraw.Draw(sh)
    A.label(d, (G, 24), "YOUR TWO NAMES, IN THE FACES YOU POINTED AT", 40, (240, 200, 140))
    for r, (name, fn) in enumerate(rows):
        y = 90 + r * (T + 110)
        A.label(d, (G, y), name, 28, (200, 220, 200))
        for i, (lab, build) in enumerate(FACES):
            if fn is sinking_name and "GRIT" in lab:
                font = IMPACT if lab.startswith("IMPACT") else MARC
                lines = ["INCH", "OF", "SHADOW"] if font == IMPACT else ["Inch of", "Shadow"]
                cap, gap = (0.17, 0.035) if font == IMPACT else (0.13, 0.06)
                raw = fn(font, 0, lines, cap, gap, 0.01 if font == IMPACT else 0.0)
                mask = grit(raw, 221 + i, amount=0.35, soft=0.0015)
            else:
                mask = build(fn)
            tile(sh, done(mask), G + i * (T + G), y + 40, T, lab)
    sh.save(S / "v3_names.jpg", quality=92)
    print("ok")


if __name__ == "__main__":
    main()
