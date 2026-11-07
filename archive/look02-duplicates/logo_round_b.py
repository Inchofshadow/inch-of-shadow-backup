"""Look-02 round B: more directions, and the two keepers (eclipse, inch mark) combined. Local only."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import logo_sketches as A
from logo_sketches import blank, done, disc, eclipse, inch_mark, K, FUT, MARC, INK, GROUND, S


def paste_sym(m, sym_mask, box):
    x0, y0, x1, y1 = [int(v) for v in box]
    g = sym_mask.crop(sym_mask.getbbox()); k = min((x1 - x0) / g.width, (y1 - y0) / g.height)
    g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)
    m.paste(255, (x0 + ((x1 - x0) - g.width) // 2, y0 + ((y1 - y0) - g.height) // 2), g)


def seal(n):
    """The eclipse in the middle, the name running around it: a stamp, a coin, a back print."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c, c, W * 0.49); disc(d, c, c, W * 0.475, 0)          # outer hairline ring
    disc(d, c, c, W * 0.33); disc(d, c, c, W * 0.315, 0)          # inner hairline ring
    paste_sym(m, eclipse(int(n * 0.44)), (c - W * 0.22, c - W * 0.22, c + W * 0.22, c + W * 0.22))
    text = "INCH  OF  SHADOW  •  INCH  OF  SHADOW  •  "
    f = ImageFont.truetype(FUT, int(W * 0.075), index=2); r = W * 0.40
    total = sum(d.textlength(ch, font=f) for ch in text) * 1.12
    ang = -90.0
    for ch in text:
        w = d.textlength(ch, font=f) * 1.12
        a = ang + math.degrees(w / 2 / r)
        g = Image.new("L", (int(W * 0.12), int(W * 0.12)), 0)
        ImageDraw.Draw(g).text((g.width / 2, g.height / 2), ch, font=f, fill=255, anchor="mm")
        g = g.rotate(-(a + 90), resample=Image.BICUBIC)
        x = c + r * math.cos(math.radians(a)) - g.width / 2; y = c + r * math.sin(math.radians(a)) - g.height / 2
        m.paste(255, (int(x), int(y)), g)
        ang += math.degrees(w / r) * (360 / math.degrees(total / r))
    return done(m, n)


def one_line(n):
    """INCH OF SHADOW on one line, heavy capitals, the O of OF is the eclipse. The name IS the logo."""
    W = n * K; H = W; m = blank(n); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(FUT, 100, index=2)
    parts = ["INCH ", "O", "F SHADOW"]
    widths = [d.textlength(p, font=f) for p in parts]; cap = d.textbbox((0, 0), "H", font=f)
    scale = W * 0.94 / sum(widths); f = ImageFont.truetype(FUT, int(100 * scale), index=2)
    cap = d.textbbox((0, 0), "H", font=f); ch = cap[3] - cap[1]; y = H / 2 - ch / 2 - cap[1]; x = W * 0.03
    for p in parts:
        if p == "O":
            paste_sym(m, eclipse(int(ch / K) + 1), (x, y + cap[1], x + ch, y + cap[1] + ch)); x += ch * 1.06
        else:
            d.text((x, y), p, font=f, fill=255); x += d.textlength(p, font=f)
    return done(m, n)


def i_inch(n):
    """i + the inch sign reads 'inch': the i with its eclipse dot, and the inch mark beside it."""
    W = n * K; m = blank(n)
    paste_sym(m, A.small_i(n), (W * 0.02, W * 0.06, W * 0.50, W * 0.94))
    paste_sym(m, inch_mark(n), (W * 0.44, W * 0.06, W * 0.98, W * 0.60))
    return done(m, n)


def cut_eclipse(n):
    """The eclipse cut by the inch mark: two slanted gaps run through it, the sign in negative space."""
    W = n * K; m = eclipse(n).resize((W, W), Image.LANCZOS)
    cut = Image.new("L", m.size, 0); cd = ImageDraw.Draw(cut)
    for x in (W * 0.40, W * 0.53):
        cd.polygon([(x + W * 0.10, 0), (x + W * 0.145, 0), (x + W * 0.045, W), (x, W)], fill=255)
    return done(ImageChops.subtract(m, cut), n)


def keyhole(n):
    """A keyhole: the round part is the eclipse, the slot below is solid. Light through the dark."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    paste_sym(m, eclipse(n), (c - W * 0.30, W * 0.04, c + W * 0.30, W * 0.64))
    d.polygon([(c - W * 0.07, W * 0.60), (c + W * 0.07, W * 0.60), (c + W * 0.17, W * 0.96), (c - W * 0.17, W * 0.96)], fill=255)
    return done(m, n)


def rose(n):
    """A rose drawn as one exact line (a five-petal rose curve), the eclipse at its heart."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2; R = W * 0.47
    pts = []
    for i in range(0, 3601):
        t = math.radians(i / 10)
        r = R * math.cos(5 * t)
        pts.append((c + r * math.cos(t), c + r * math.sin(t)))
    d.line(pts, fill=255, width=int(W * 0.022), joint="curve")
    disc(d, c, c, W * 0.15, 0)
    paste_sym(m, eclipse(int(n * 0.26)), (c - W * 0.13, c - W * 0.13, c + W * 0.13, c + W * 0.13))
    return done(m, n)


def flame(n):
    """A candle flame: the left half drawn in light (outline), the right half in shadow (solid)."""
    W = n * K; m = blank(n); d = ImageDraw.Draw(m); c = W / 2
    pts = []
    for i in range(0, 721):
        t = math.radians(i / 2)
        x = math.sin(t) * math.sin(t / 2) ** 2.2
        y = -math.cos(t)
        lean = 0.10 * ((1 - y) / 2) ** 3          # only the tip leans to the side
        pts.append((c + (x * 0.36 + lean) * W, W * 0.52 + y * W * 0.46))
    d.polygon(pts, fill=255)
    inner = m.filter(ImageFilter.MinFilter(int(W * 0.03) | 1))
    outline = ImageChops.subtract(m, inner)
    right = Image.new("L", m.size, 0); ImageDraw.Draw(right).rectangle((c, 0, W, W), fill=255)
    out = ImageChops.add(ImageChops.multiply(outline, ImageChops.invert(right)), ImageChops.multiply(m, right))
    return done(out, n)


DIRECTIONS = [
    ("7  THE SEAL", "the eclipse in the middle, the name running around it: a stamp, a coin, a back print", seal, False),
    ("8  THE NAME, ONE LINE", "heavy capitals, the O of OF is the eclipse: the name itself is the logo", one_line, False),
    ("9  i + THE INCH MARK", "the small i with its eclipse dot, plus the inch sign: together they read 'inch'", i_inch, False),
    ("10 THE CUT MOON", "the eclipse crossed by the inch mark: your two keepers in one sign", cut_eclipse, False),
    ("11 THE KEYHOLE", "the eclipse as the round of a keyhole: light seen through the dark, mystery", keyhole, False),
    ("12 THE FLAME", "a candle flame, half in light, half in shadow", flame, False),
]

_T, _P, _R = A.tshirt, A.photo_corner, A.reel_end   # the round-A mock-ups, kept before overriding


def fit(sym, w, h):
    g = sym.crop(sym.getbbox()); k = min(w / g.width, h / g.height)
    return g.resize((int(g.width * k), int(g.height * k)), Image.LANCZOS)


def tshirt(sym):
    im = _T(Image.new("L", sym.size, 0)); g = fit(sym, 190, 170)
    im.paste(INK, (260 - g.width // 2, 245 - g.height // 2), g); return im


def photo_corner(sym):
    ph = _P(Image.new("L", sym.size, 0)); g = fit(sym, 70, 46)
    ph.paste((245, 243, 238), (315 - 20 - g.width, 560 - 24 - g.height), g); return ph


def reel_end(sym, in_text):
    im = _R(Image.new("L", sym.size, 0), in_text); g = fit(sym, 200, 120)
    im.paste(INK, ((315 - g.width) // 2, 250 - g.height), g); return im


if __name__ == "__main__":
    A.DIRECTIONS = DIRECTIONS
    A.tshirt, A.photo_corner, A.reel_end = tshirt, photo_corner, reel_end
    rows = []
    for title, why, fn, in_text in DIRECTIONS:
        sym = fn(600)
        big = A.colorize(sym.resize((380, 380), Image.LANCZOS), GROUND, (236, 232, 224))
        wm = A.wordmark(430, sym, True)
        wm_img = Image.new("RGB", (470, 380), (236, 232, 224)); wm_img.paste(GROUND, (20, (380 - wm.height) // 2), wm)
        row = Image.new("RGB", (2330, 720), (24, 24, 24)); d = ImageDraw.Draw(row)
        A.label(d, (30, 18), title, 40, (240, 200, 140)); A.label(d, (520, 30), why, 26, (190, 190, 190))
        row.paste(big, (30, 110)); row.paste(wm_img, (430, 110))
        row.paste(A.tshirt(sym).resize((440, 474)), (930, 90))
        row.paste(A.photo_corner(sym), (1400, 90)); row.paste(A.reel_end(sym, True), (1745, 90))
        for x, cap in ((30, "the symbol"), (430, "the wordmark, eclipse as the o (Marcellus for now)"),
                       (930, "T-shirt"), (1400, "signing a photo"), (1745, "last frame of a reel")):
            A.label(d, (x, 668 if x >= 930 else 500), cap, 22, (160, 160, 160))
        rows.append(row)
    for part, chunk in enumerate((rows[:3], rows[3:]), start=1):
        sheet = Image.new("RGB", (2330, 720 * len(chunk)), (24, 24, 24))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, 720 * i))
        sheet.save(S / f"logo_round_b_{part}.jpg", quality=90)
    print("ok")
