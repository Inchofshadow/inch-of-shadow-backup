"""Look-02 v2: the twelve picks redrawn with more care. Same ideas, better craft. Local only."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from logo_sketches import K, FUT, MARC
from logo_round_d import IMPACT, shift
from logo_round_e import noise, COURIER

N = 700                      # output size of every mark
W = N * K                    # drawing size (4x, downsampled at the end)


def blank():
    return Image.new("L", (W, W), 0)


def done(m):
    return m.resize((N, N), Image.LANCZOS)


def disc(d, cx, cy, r, fill=255):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def lines_same_height(lines, font_path, index, cap_frac, gap_frac, track_em=0.0):
    """Stacked lines, every line at the SAME cap height (not stretched to one width), centred."""
    m = blank(); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(font_path, 1000, index=index)
    cap = d.textbbox((0, 0), "H", font=f); ch = cap[3] - cap[1]
    size = int(1000 * W * cap_frac / ch); f = ImageFont.truetype(font_path, size, index=index)
    cap = d.textbbox((0, 0), "H", font=f); ch = cap[3] - cap[1]; gap = W * gap_frac
    total = len(lines) * ch + (len(lines) - 1) * gap; y = (W - total) / 2
    for ln in lines:
        widths = [d.textlength(c, font=f) for c in ln]; tw = sum(widths) + size * track_em * (len(ln) - 1)
        x = (W - tw) / 2
        for c, cw in zip(ln, widths):
            d.text((x, y - cap[1]), c, font=f, fill=255); x += cw + size * track_em
        y += ch + gap
    return m


def clean(m, px=3):
    """Remove slivers thinner than px: an opening (erode, then dilate)."""
    return m.filter(ImageFilter.MinFilter(px)).filter(ImageFilter.MaxFilter(px))


# ---------------- family 1: the marks ----------------

def eclipse():
    """Thin ring; the dark disc sits low-right inside it, leaving a crescent of light that tapers to a hair."""
    m = blank(); d = ImageDraw.Draw(m); c = W / 2
    disc(d, c, c, W * 0.46); disc(d, c, c, W * 0.415, 0)
    o = W * 0.044
    disc(d, c + o, c + o, W * 0.34)
    return done(m)


def inch_mark():
    """Two strokes at 14 degrees, cut flat top and bottom; the second is only its own outline."""
    m = blank(); d = ImageDraw.Draw(m)
    h = W * 0.78; top = (W - h) / 2; bw = W * 0.13; sl = h * math.tan(math.radians(14))
    def stroke(x):
        return [(x + sl, top), (x + sl + bw, top), (x + bw, top + h), (x, top + h)]
    gap = W * 0.07; x1 = (W - (sl + 2 * bw + gap)) / 2; x2 = x1 + bw + gap
    d.polygon(stroke(x1), fill=255)
    o = Image.new("L", (W, W), 0); ImageDraw.Draw(o).polygon(stroke(x2), fill=255)
    m = ImageChops.lighter(m, ImageChops.subtract(o, o.filter(ImageFilter.MinFilter(int(W * 0.022) | 1))))
    return done(m)


def sword():
    """Tapered blade, a guard that thins to its tips, a short grip, a small round pommel."""
    m = blank(); d = ImageDraw.Draw(m); c = W / 2
    guard_y = W * 0.27
    d.polygon([(c - W * 0.028, guard_y), (c + W * 0.028, guard_y), (c + W * 0.018, W * 0.86), (c, W * 0.95), (c - W * 0.018, W * 0.86)], fill=255)
    d.polygon([(c - W * 0.23, guard_y - W * 0.008), (c, guard_y - W * 0.022), (c + W * 0.23, guard_y - W * 0.008),
               (c + W * 0.23, guard_y + W * 0.008), (c, guard_y + W * 0.022), (c - W * 0.23, guard_y + W * 0.008)], fill=255)
    for s in (-1, 1):
        disc(d, c + s * W * 0.232, guard_y, W * 0.013)
    d.rectangle((c - W * 0.016, W * 0.12, c + W * 0.016, guard_y - W * 0.02), fill=255)
    disc(d, c, W * 0.095, W * 0.03)
    return done(m)


# ---------------- family 2: the name as shadow ----------------

def name_in_shadow():
    """Only the shadows of the letters, cast down and right; the letters themselves are the paper."""
    t = lines_same_height(["INCH", "OF", "SHADOW"], FUT, 2, 0.12, 0.05, 0.02)
    t = shift(t, -W * 0.012, -W * 0.012)
    sh = ImageChops.subtract(shift(t, W * 0.026, W * 0.026), t)
    return done(clean(sh, 5))


def name_sinking():
    """The name in a serif; from the middle of 'Shadow' down it turns to lines that thin out to nothing."""
    t = lines_same_height(["Inch of", "Shadow"], MARC, 0, 0.13, 0.06)
    box = t.getbbox(); rows = np.nonzero(np.asarray(t).max(axis=1))[0]
    second_top = rows[rows > (box[1] + box[3]) / 2].min(); bottom = box[3]
    cut = second_top + (bottom - second_top) * 0.42
    lines = blank(); d = ImageDraw.Draw(lines); period = W * 0.016; y = cut
    while y < bottom + period:
        k = (y - cut) / (bottom - cut)
        d.rectangle((0, y, W, y + period * max(0.08, 0.72 * max(0.0, 1 - k) ** 1.3)), fill=255); y += period
    solid = blank(); ImageDraw.Draw(solid).rectangle((0, 0, W, cut - W * 0.004), fill=255)
    return done(ImageChops.lighter(ImageChops.multiply(t, solid), ImageChops.multiply(t, lines)))


def long_shadow():
    """Outlined capitals, each throwing one solid shadow at 45 degrees."""
    t = lines_same_height(["INCH", "OF", "SHADOW"], IMPACT, 0, 0.18, 0.03, 0.01)
    t = shift(t, -W * 0.05, -W * 0.05)
    sh = blank(); L = int(W * 0.085)
    for i in range(2, L, 2):
        sh = ImageChops.lighter(sh, shift(t, i, i))
    body = ImageChops.subtract(sh, t.filter(ImageFilter.MaxFilter(int(W * 0.010) | 1)))
    outline = ImageChops.subtract(t, t.filter(ImageFilter.MinFilter(int(W * 0.010) | 1)))
    return done(ImageChops.lighter(outline, clean(body, 3)))


# ---------------- family 3: pressed and printed ----------------

def stamp():
    """A rubber stamp: heavy frame with a thin inner line, tracked capitals, ink heavy at the edges and patchy inside."""
    m = blank(); d = ImageDraw.Draw(m)
    d.rectangle((W * 0.07, W * 0.25, W * 0.93, W * 0.75), outline=255, width=int(W * 0.028))
    d.rectangle((W * 0.105, W * 0.285, W * 0.895, W * 0.715), outline=255, width=int(W * 0.007))
    t = lines_same_height(["INCH OF", "SHADOW"], FUT, 2, 0.085, 0.045, 0.10)
    m = ImageChops.lighter(m, t)
    edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(int(W * 0.006) | 1)))
    ink = noise(W, 2.5, 51) * 0.55 + noise(W, 30, 52) * 0.45
    keep = Image.fromarray(((ink > 0.40) * 255).astype(np.uint8))
    m = ImageChops.lighter(ImageChops.multiply(m, keep), edge)
    return done(m.rotate(-5, resample=Image.BICUBIC))


def spray():
    """Heavy capitals sprayed through a stencil: a hard core, a soft cloud of paint, a few stray drops."""
    t = lines_same_height(["INCH", "OF", "SHADOW"], IMPACT, 0, 0.19, 0.035, 0.01)
    cloud = np.asarray(t.filter(ImageFilter.GaussianBlur(W * 0.010))).astype(np.float64) / 255
    rng = np.random.default_rng(61)
    dots = rng.random((W, W)) < cloud * 0.85
    core = np.asarray(t.filter(ImageFilter.MinFilter(3))) > 128
    m = Image.fromarray(((dots | core) * 255).astype(np.uint8)); d = ImageDraw.Draw(m)
    ys, xs = np.nonzero(np.asarray(t) > 128)
    for i in rng.choice(len(xs), 40, replace=False):
        r = W * rng.uniform(0.002, 0.006); ox = rng.normal(0, W * 0.03); oy = rng.normal(0, W * 0.03)
        disc(d, xs[i] + ox, ys[i] + oy, r)
    return done(m)


def photocopy():
    """Copied until it breaks: soft toner edges, grit, and two thin streaks where the drum was scratched."""
    t = lines_same_height(["Inch of", "Shadow"], MARC, 0, 0.14, 0.06)
    blur = np.asarray(t.filter(ImageFilter.GaussianBlur(W * 0.006))).astype(np.float64) / 255
    grit = noise(W, 2, 71) * 0.6 + noise(W, 16, 72) * 0.4
    m = (blur + (grit - 0.5) * 0.9) > 0.52
    for y in (0.46, 0.585):
        y0 = int(W * y); m[y0:y0 + int(W * 0.004), :] = False
    edge_dirt = (np.asarray(t.filter(ImageFilter.GaussianBlur(W * 0.02))) > 20) & (noise(W, 3, 73) > 0.93)
    return done(Image.fromarray(((m | edge_dirt) * 255).astype(np.uint8)))


def typewriter():
    """Typed, lower case: each key strikes a little high or low, some harder than others, the ribbon doubles a few."""
    m = blank(); d = ImageDraw.Draw(m); rng = np.random.default_rng(81)
    text = "inch of shadow."; f = ImageFont.truetype(COURIER, 100)
    size = int(100 * W * 0.86 / d.textlength(text, font=f)); f = ImageFont.truetype(COURIER, size)
    x = (W - d.textlength(text, font=f)) / 2; y = W * 0.44
    for i, ch in enumerate(text):
        g = blank(); gd = ImageDraw.Draw(g); dy = rng.normal(0, W * 0.003)
        gd.text((x, y + dy), ch, font=f, fill=255)
        if rng.random() < 0.3:
            gd.text((x + W * 0.0015, y + dy + W * 0.0012), ch, font=f, fill=255)
        density = 0.75 + 0.25 * rng.random()
        ink = noise(W, 1.8, 90 + i) > (1 - density) * 0.75
        m = ImageChops.lighter(m, ImageChops.multiply(g, Image.fromarray((ink * 255).astype(np.uint8))))
        x += d.textlength(ch, font=f)
    return done(m)


# ---------------- family 4: street and screen ----------------

def bitmap():
    """Capitals on a strict pixel grid: every line the same pixel height, square pixels, no smoothing."""
    cols = 72; small_cap = 9
    tile = Image.new("L", (cols, cols), 0); f = ImageFont.truetype(FUT, 100, index=2); dd = ImageDraw.Draw(tile)
    big = lines_same_height(["INCH", "OF", "SHADOW"], FUT, 2, small_cap / cols, 3 / cols, 0.06)
    tile = big.resize((cols, cols), Image.BOX).point(lambda v: 255 if v > 120 else 0)
    return tile.resize((N, N), Image.NEAREST)


def torn_strip():
    """A strip torn from a page: ragged fibrous edges, the name cut out of it."""
    rng = np.random.default_rng(91)
    def ragged(y, n=400, amp=0.012):
        pts = np.zeros(n); step = amp
        for s in (64, 16, 4, 1):
            pts += np.repeat(rng.normal(0, step, n // s + 1), s)[:n] if s > 1 else rng.normal(0, step * 0.4, n)
            step *= 0.55
        return [(W * (0.05 + 0.90 * i / (n - 1)), W * (y + p)) for i, p in enumerate(pts)]
    top = ragged(0.39); bot = ragged(0.61)
    m = blank(); ImageDraw.Draw(m).polygon(top + bot[::-1], fill=255)
    fibres = (noise(W, 1.5, 92) > 0.6).astype(np.uint8) * 255
    edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(int(W * 0.006) | 1)))
    m = ImageChops.subtract(m, ImageChops.multiply(edge, Image.fromarray(fibres)))
    t = lines_same_height(["INCH OF SHADOW"], IMPACT, 0, 0.085, 0, 0.02)
    return done(ImageChops.subtract(m, t).rotate(2.5, resample=Image.BICUBIC))


V2 = {
    "1": eclipse, "4": inch_mark, "14": sword,
    "20": name_in_shadow, "21": name_sinking, "25": long_shadow,
    "27": stamp, "29": photocopy, "30": typewriter, "43": torn_strip,
    "28": spray, "31": bitmap,
}
