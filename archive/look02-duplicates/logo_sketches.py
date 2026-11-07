"""Look-02 round A: six fresh logo directions, clean and one colour, local drawing only."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

S = Path(__file__).parent
CODE = Path("/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode")
MARC = str(CODE / "docs/brand/fonts/Marcellus-Regular.ttf")
FUT = "/System/Library/Fonts/Supplemental/Futura.ttc"
INK = (214, 209, 200)          # M2 platinum
GROUND = (15, 13, 12)          # M2 warm black
K = 4                           # supersampling


def blank(n):
    return Image.new("L", (n * K, n * K), 0)


def done(m, n):
    return m.resize((n, n), Image.LANCZOS)


def disc(d, cx, cy, r, fill=255):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def eclipse(n):
    """A ring with a solid disc pushed to one side: light and its shadow in one circle."""
    m = blank(n); d = ImageDraw.Draw(m); c = n * K / 2; r = c * 0.92
    disc(d, c, c, r); disc(d, c, c, r * 0.86, 0)
    disc(d, c + r * 0.14, c + r * 0.10, r * 0.72)
    return done(m, n)


def eye(n):
    """An eye (two arcs), its pupil the eclipse."""
    m = blank(n); d = ImageDraw.Draw(m); W = n * K; c = W / 2
    R = W * 0.62; off = R * 0.62                     # two big circles, their overlap is the eye
    a = Image.new("L", m.size, 0); b = Image.new("L", m.size, 0)
    disc(ImageDraw.Draw(a), c, c - off, R); disc(ImageDraw.Draw(b), c, c + off, R)
    lens = ImageChops.multiply(a, b)
    inner = lens.filter(ImageFilter.MinFilter(int(W * 0.05) | 1))
    m = ImageChops.subtract(lens, inner)
    pupil = eclipse(int(n * 0.40)).resize((int(W * 0.40),) * 2, Image.LANCZOS)
    m.paste(255, (int(c - W * 0.20), int(c - W * 0.20)), pupil)
    return done(m, n)


def small_i(n):
    """A lowercase i: the stem, and the eclipse as its dot."""
    m = blank(n); d = ImageDraw.Draw(m); W = n * K; c = W / 2
    sw = W * 0.16
    d.rounded_rectangle((c - sw / 2, W * 0.40, c + sw / 2, W * 0.96), radius=sw * 0.12, fill=255)
    e = eclipse(int(n * 0.34)).resize((int(W * 0.34),) * 2, Image.LANCZOS)
    m.paste(255, (int(c - W * 0.17), int(W * 0.02)), e)
    return done(m, n)


def inch_mark(n):
    """The inch sign: two slanted bars, the second one only the outline of the first, its shadow."""
    m = blank(n); d = ImageDraw.Draw(m); W = n * K
    def bar(x):
        return [(x + W * 0.16, W * 0.06), (x + W * 0.34, W * 0.06), (x + W * 0.18, W * 0.94), (x, W * 0.94)]
    d.polygon(bar(W * 0.14), fill=255)
    d.polygon(bar(W * 0.46), fill=255)
    hole = Image.new("L", m.size, 0); ImageDraw.Draw(hole).polygon(bar(W * 0.46), fill=255)
    hole = hole.filter(ImageFilter.MinFilter(int(W * 0.035) | 1))
    return done(ImageChops.subtract(m, hole), n)


def split_s(n):
    """One S: the top half drawn in light (outline), the bottom half in shadow (solid)."""
    W = n * K; m = blank(n)
    f = ImageFont.truetype(FUT, int(W * 1.05), index=2)
    d = ImageDraw.Draw(m); box = d.textbbox((0, 0), "S", font=f)
    d.text(((W - (box[2] - box[0])) / 2 - box[0], (W - (box[3] - box[1])) / 2 - box[1]), "S", font=f, fill=255)
    inner = m.filter(ImageFilter.MinFilter(int(W * 0.03) | 1))
    outline = ImageChops.subtract(m, inner)
    top = Image.new("L", m.size, 0); ImageDraw.Draw(top).rectangle((0, 0, W, W * 0.5), fill=255)
    out = ImageChops.add(ImageChops.multiply(outline, top), ImageChops.multiply(m, ImageChops.invert(top)))
    return done(out, n)


def block(n):
    """INCH / OF / SHADOW locked into one square block; the O of OF is the eclipse."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m)
    f0 = ImageFont.truetype(FUT, 100, index=2)
    lines = ["INCH", "OF", "SHADOW"]; target = W * 0.92; y = W * 0.04
    heights = []
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=f0); heights.append((b[3] - b[1]) * target / (b[2] - b[0]))
    gap = (W * 0.92 - sum(heights)) / 2
    for ln, h in zip(lines, heights):
        b = d.textbbox((0, 0), ln, font=f0); size = int(100 * target / (b[2] - b[0]))
        if ln == "OF":
            f = ImageFont.truetype(FUT, size, index=2); bb = d.textbbox((0, 0), "F", font=f)
            fw = bb[2] - bb[0]; gapx = W * 0.04; dia = h
            ow = target - fw - gapx; e = eclipse(int(dia / K)).resize((int(dia),) * 2, Image.LANCZOS)
            ex = W * 0.04 + (ow - dia) / 2
            m.paste(255, (int(ex), int(y)), e)
            d.text((W * 0.04 + ow + gapx - bb[0], y - bb[1]), "F", font=f, fill=255)
        else:
            f = ImageFont.truetype(FUT, size, index=2); bb = d.textbbox((0, 0), ln, font=f)
            d.text((W * 0.04 - bb[0], y - bb[1]), ln, font=f, fill=255)
        y += h + gap
    return done(m, n)


DIRECTIONS = [
    ("1  THE ECLIPSE", "the name's idea + a sacred sign: a light and its shadow in one circle; it is also the O of 'of'", eclipse, True),
    ("2  THE EYE", "a sacred sign everyone reads in a second; its pupil is the eclipse", eye, False),
    ("3  THE SMALL i", "a letter as a shape: the i of inch, its dot is the eclipse", small_i, False),
    ("4  THE INCH MARK", "the name's own sign, the inch symbol; the second stroke is only the shadow of the first", inch_mark, False),
    ("5  THE SPLIT S", "a letter as a shape: one S, the top in light, the bottom in shadow", split_s, False),
    ("6  THE BLOCK", "the name as one square: INCH / OF / SHADOW locked together, the O is the eclipse", block, False),
]


def colorize(mask, ink, ground):
    im = Image.new("RGB", mask.size, ground); im.paste(ink, (0, 0), mask); return im


def wordmark(width, sym, eclipse_in_text):
    """'Inch of Shadow' in the brand face (Marcellus here, the tools' fallback)."""
    h = int(width * 0.22); m = Image.new("L", (width * 2, h * 2), 0); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(MARC, int(h * 1.05)); x = 0; base = int(h * 0.25)
    if eclipse_in_text:
        parts = ["Inch ", "o", "f Shadow"]
    else:
        parts = ["Inch of Shadow"]
    for p in parts:
        if p == "o":
            xh = d.textbbox((0, 0), "x", font=f); size = int((xh[3] - xh[1]) * 1.12)
            e = eclipse(size // 1).resize((size, size), Image.LANCZOS)
            top = base + xh[1] - int(size * 0.06)
            m.paste(255, (int(x + size * 0.04), top), e); x += size * 1.12
        else:
            d.text((x, base), p, font=f, fill=255); x += d.textlength(p, font=f)
    bb = m.getbbox(); m = m.crop(bb)
    m = m.resize((width, int(m.height * width / m.width)), Image.LANCZOS)
    return m


def tshirt(sym):
    W, H = 520, 560; im = Image.new("RGB", (W, H), (38, 38, 40)); d = ImageDraw.Draw(im)
    shirt = [(150, 60), (215, 40), (260, 70), (305, 40), (370, 60), (470, 150), (420, 215), (385, 185),
             (385, 530), (135, 530), (135, 185), (100, 215), (50, 150)]
    d.polygon(shirt, fill=(22, 21, 20)); d.arc((215, 18, 305, 98), 20, 160, fill=(10, 10, 10), width=6)
    s = sym.resize((150, 150), Image.LANCZOS); im.paste(INK, (185, 170), s)
    return im


def photo_corner(sym):
    ph = Image.open(S / "pull/out-022_reel.jpg").convert("RGB").resize((315, 560), Image.LANCZOS)
    s = sym.resize((42, 42), Image.LANCZOS); ph.paste((245, 243, 238), (315 - 42 - 20, 560 - 42 - 24), s)
    return ph


def reel_end(sym, eclipse_in_text):
    im = Image.new("RGB", (315, 560), GROUND)
    s = sym.resize((110, 110), Image.LANCZOS); im.paste(INK, ((315 - 110) // 2, 190), s)
    w = wordmark(230, sym, eclipse_in_text); im.paste(INK, ((315 - w.width) // 2, 330), w)
    return im


def label(d, xy, text, px, fill):
    d.text(xy, text, font=ImageFont.truetype(MARC, px), fill=fill)


def main():
    rows = []
    for title, why, fn, in_text in DIRECTIONS:
        sym = fn(600)
        big = colorize(sym.resize((380, 380), Image.LANCZOS), GROUND, (236, 232, 224))
        big = big.resize((380, 380))
        wm = wordmark(430, sym, in_text or fn is eclipse)
        wm_img = Image.new("RGB", (470, 380), (236, 232, 224)); wm_img.paste(GROUND, (20, (380 - wm.height) // 2), wm)
        row = Image.new("RGB", (2330, 720), (24, 24, 24)); d = ImageDraw.Draw(row)
        label(d, (30, 18), title, 40, (240, 200, 140)); label(d, (400, 30), why, 26, (190, 190, 190))
        row.paste(big, (30, 110)); row.paste(wm_img, (430, 110))
        ts = tshirt(sym).resize((440, 474)); row.paste(ts, (930, 90))
        row.paste(photo_corner(sym), (1400, 90)); row.paste(reel_end(sym, in_text), (1745, 90))
        for x, cap in ((30, "the symbol"), (430, "the wordmark (Marcellus for now)"),
                       (930, "T-shirt"), (1400, "signing a photo"), (1745, "last frame of a reel")):
            label(d, (x, 668 if x >= 930 else 500), cap, 22, (160, 160, 160))
        rows.append(row)
        sym.save(S / f"logo_{title.split()[0]}.png")
    for part, chunk in enumerate((rows[:3], rows[3:]), start=1):
        sheet = Image.new("RGB", (2330, 720 * len(chunk)), (24, 24, 24))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, 720 * i))
        sheet.save(S / f"logo_round_a_{part}.jpg", quality=90)
    print("ok")


if __name__ == "__main__":
    main()
