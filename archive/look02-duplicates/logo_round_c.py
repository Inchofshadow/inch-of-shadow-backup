"""Look-02 round C: eight NEW directions. No eclipse, no inch mark. Local drawing only."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
import logo_round_b as B
from logo_sketches import blank, done, disc, K, FUT, MARC, INK, GROUND, S


def outline_of(mask, px):
    return ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(px | 1)))


def star(n):
    """A four-point star, and beside it its own shadow drawn as a thin outline."""
    W = n * K
    def shape(cx, cy, R):
        m = Image.new("L", (W, W), 0)
        pts = [(cx + R * math.cos(t) ** 3, cy + R * math.sin(t) ** 3) for t in [i * math.pi / 360 for i in range(720)]]
        ImageDraw.Draw(m).polygon(pts, fill=255); return m
    big = shape(W * 0.44, W * 0.52, W * 0.40)
    small = shape(W * 0.84, W * 0.16, W * 0.11)
    return done(ImageChops.lighter(big, small), n)


def sword(n):
    """A long blade that is also a cross: clean, vertical, sacred and sharp."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    d.polygon([(c - W * 0.035, W * 0.30), (c + W * 0.035, W * 0.30), (c + W * 0.035, W * 0.84), (c, W * 0.98), (c - W * 0.035, W * 0.84)], fill=255)
    d.rounded_rectangle((c - W * 0.25, W * 0.25, c + W * 0.25, W * 0.30), radius=W * 0.02, fill=255)
    d.rectangle((c - W * 0.022, W * 0.10, c + W * 0.022, W * 0.25), fill=255)
    disc(d, c, W * 0.075, W * 0.045)
    return done(m, n)


def heart(n):
    """A sacred heart: the heart, a small flame rising from it, a thin cross above."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    pts = []
    for i in range(720):
        t = i * math.pi / 360
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((c + x * W * 0.021, W * 0.60 - y * W * 0.021))
    d.polygon(pts, fill=255)
    fl = []
    for i in range(721):
        t = math.radians(i / 2)
        fl.append((c + math.sin(t) * math.sin(t / 2) ** 2.2 * W * 0.08, W * 0.27 - math.cos(t) * W * 0.09))
    d.polygon(fl, fill=255)
    d.rectangle((c - W * 0.012, W * 0.02, c + W * 0.012, W * 0.20), fill=255)
    d.rectangle((c - W * 0.06, W * 0.07, c + W * 0.06, W * 0.095), fill=255)
    return done(m, n)


def key(n):
    """An old key: a ring for the bow, a long shaft, two teeth. Mystery, a door you open."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c, W * 0.20, W * 0.17); disc(d, c, W * 0.20, W * 0.105, 0)
    disc(d, c, W * 0.20, W * 0.04)
    d.rectangle((c - W * 0.03, W * 0.35, c + W * 0.03, W * 0.96), fill=255)
    d.rectangle((c + W * 0.03, W * 0.74, c + W * 0.16, W * 0.79), fill=255)
    d.rectangle((c + W * 0.03, W * 0.86, c + W * 0.13, W * 0.91), fill=255)
    return done(m, n)


def moth(n):
    """A moth, the creature drawn to the light: swept, pointed wings, exact and symmetric."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    for s in (-1, 1):
        d.polygon([(c + s * W * 0.04, c - W * 0.14), (c + s * W * 0.47, c - W * 0.24), (c + s * W * 0.40, c + W * 0.02), (c + s * W * 0.04, c + W * 0.06)], fill=255)
        d.polygon([(c + s * W * 0.04, c + W * 0.08), (c + s * W * 0.30, c + W * 0.10), (c + s * W * 0.14, c + W * 0.34), (c + s * W * 0.04, c + W * 0.24)], fill=255)
        d.line([(c, c - W * 0.19), (c + s * W * 0.06, c - W * 0.31), (c + s * W * 0.14, c - W * 0.35)], fill=255, width=int(W * 0.012))
    d.ellipse((c - W * 0.03, c - W * 0.20, c + W * 0.03, c + W * 0.30), fill=255)
    return done(m, n)


def arch(n):
    """A church door standing open: the pointed arch is light, and the light falls out onto the floor."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    half = W * 0.15; spring = W * 0.34; bottom = W * 0.62; r = 2 * half
    left = [(c + half + r * math.cos(math.radians(a)), spring - r * math.sin(math.radians(a))) for a in range(180, 119, -1)]
    right = [(c - half + r * math.cos(math.radians(a)), spring - r * math.sin(math.radians(a))) for a in range(60, -1, -1)]
    d.polygon(left + right + [(c + half, bottom), (c - half, bottom)], fill=255)
    d.polygon([(c - half, W * 0.66), (c + half, W * 0.66), (c + W * 0.44, W * 0.96), (c - W * 0.44, W * 0.96)], fill=255)
    return done(m, n)


def hand(n):
    """An open hand raised, and its shadow on the wall behind it, drawn as an outline."""
    W = n * K; c = W / 2
    def one(ox, oy):
        g = Image.new("L", (W, W), 0); d = ImageDraw.Draw(g)
        d.rounded_rectangle((ox + W * 0.30, oy + W * 0.46, ox + W * 0.66, W * 0.86 + oy), radius=W * 0.08, fill=255)
        for i, (h, x) in enumerate(((0.26, 0.30), (0.33, 0.39), (0.31, 0.48), (0.24, 0.57))):
            d.rounded_rectangle((ox + W * x, oy + W * (0.50 - h), ox + W * (x + 0.08), oy + W * 0.56), radius=W * 0.04, fill=255)
        t = Image.new("L", (W, W), 0)
        ImageDraw.Draw(t).rounded_rectangle((c - W * 0.04, c - W * 0.16, c + W * 0.04, c + W * 0.06), radius=W * 0.04, fill=255)
        t = t.rotate(40, resample=Image.BICUBIC, center=(c, c))
        return ImageChops.lighter(g, ImageChops.offset(t, int(ox - W * 0.24), int(oy + W * 0.17)))
    front = one(-W * 0.04, 0)
    back = outline_of(one(W * 0.06, -W * 0.05), int(W * 0.016))
    back = ImageChops.subtract(back, front.filter(ImageFilter.MaxFilter(int(W * 0.03) | 1)))
    return done(ImageChops.lighter(front, back), n)


def of_ligature(n):
    """The small word in the middle of the name, 'of', drawn as one locked sign: the o inside the f."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(MARC, int(W * 1.05))
    bf = d.textbbox((0, 0), "f", font=f)
    fx = W * 0.56 - (bf[2] - bf[0]) / 2 - bf[0]; fy = W * 0.02 - bf[1]
    d.text((fx, fy), "f", font=f, fill=255)
    fo = ImageFont.truetype(MARC, int(W * 0.80)); bo = d.textbbox((0, 0), "o", font=fo)
    ox = W * 0.34 - (bo[2] - bo[0]) / 2 - bo[0]; oy = W * 0.98 - bo[3]
    o = Image.new("L", (W, W), 0); ImageDraw.Draw(o).text((ox, oy), "o", font=fo, fill=255)
    gap = o.filter(ImageFilter.MaxFilter(int(W * 0.03) | 1))
    m = ImageChops.lighter(ImageChops.subtract(m, gap), o)
    return done(m, n)


DIRECTIONS = [
    ("13 THE STAR", "a four-point star with a small one beside it: luxury, a guiding light in the dark", star, False),
    ("14 THE SWORD", "a blade that is also a cross: sacred and sharp, long and elegant on a shirt", sword, False),
    ("15 THE SACRED HEART", "love and faith: a heart with a flame rising from it and a small cross above", heart, False),
    ("16 THE KEY", "an old key: mystery, a door only some people open", key, False),
    ("17 THE MOTH", "the creature drawn to the light, drawn exact and symmetric", moth, False),
    ("18 THE OPEN DOOR", "a church door standing open, its light falling out onto the floor (the floor light still reads a bit like a base)", arch, False),
    ("19 THE 'of'", "a letter sign: the small 'of' of the name, locked into one shape; it also reads like a music note", of_ligature, False),
]

if __name__ == "__main__":
    A.tshirt, A.photo_corner, A.reel_end = B.tshirt, B.photo_corner, B.reel_end
    rows = []
    for title, why, fn, _ in DIRECTIONS:
        sym = fn(600)
        big = A.colorize(sym.resize((380, 380), Image.LANCZOS), GROUND, (236, 232, 224))
        wm = A.wordmark(430, sym, False)
        wm_img = Image.new("RGB", (470, 380), (236, 232, 224)); wm_img.paste(GROUND, (20, (380 - wm.height) // 2), wm)
        row = Image.new("RGB", (2330, 720), (24, 24, 24)); d = ImageDraw.Draw(row)
        A.label(d, (30, 18), title, 40, (240, 200, 140)); A.label(d, (560, 30), why, 26, (190, 190, 190))
        row.paste(big, (30, 110)); row.paste(wm_img, (430, 110))
        row.paste(A.tshirt(sym).resize((440, 474)), (930, 90))
        row.paste(A.photo_corner(sym), (1400, 90)); row.paste(A.reel_end(sym, False), (1745, 90))
        for x, cap in ((30, "the symbol"), (430, "the wordmark (Marcellus for now)"),
                       (930, "T-shirt"), (1400, "signing a photo"), (1745, "last frame of a reel")):
            A.label(d, (x, 668 if x >= 930 else 500), cap, 22, (160, 160, 160))
        rows.append(row)
    for part, chunk in enumerate((rows[:4], rows[4:]), start=1):
        sheet = Image.new("RGB", (2330, 720 * len(chunk)), (24, 24, 24))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, 720 * i))
        sheet.save(S / f"logo_round_c_{part}.jpg", quality=90)
    # one quick overview of the eight symbols alone, to look at before the detail sheets
    ov = Image.new("RGB", (len(DIRECTIONS) * 260 + 40, 330), (236, 232, 224)); d = ImageDraw.Draw(ov)
    for i, (title, _, fn, _) in enumerate(DIRECTIONS):
        g = B.fit(fn(600), 220, 220); ov.paste(GROUND, (40 + i * 260 + (220 - g.width) // 2, 30 + (220 - g.height) // 2), g)
        A.label(d, (40 + i * 260, 275), title.split()[0], 30, (60, 60, 60))
    ov.save(S / "logo_round_c_overview.jpg", quality=92)
    print("ok")
