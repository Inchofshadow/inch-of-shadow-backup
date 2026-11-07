"""Look-02: the moon, engraved, and set as the O of 'of' or of 'Shadow'. Local only, one colour."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from logo_sketches import MARC, GROUND, S
from logo_round_d import IMPACT
import logo_sketches as A, logo_round_b as B

LIGHT = (236, 232, 224)
SS = 4                                   # supersampling


def _grid(px):
    n = px * SS; v = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(v, v)
    return x, y, np.sqrt(x * x + y * y)


def _out(ink, px):
    return Image.fromarray((ink * 255).astype(np.uint8)).resize((px, px), Image.LANCZOS)


def engraved_sphere(px, lines=34, tilt=-24, light=(-0.70, -0.45, 0.55)):
    """E1: a moon as a lit sphere, engraved with curved lines of latitude; each line thickens where it turns into shadow."""
    x, y, r = _grid(px); inside = r <= 0.94
    xs, ys = x / 0.94, y / 0.94
    z = np.sqrt(np.clip(1 - xs * xs - ys * ys, 0, 1))
    L = np.array(light); L = L / np.linalg.norm(L)
    shade = np.clip(xs * L[0] + ys * L[1] + z * L[2], 0, 1)
    dark = np.clip(1 - shade ** 0.7, 0, 1)
    a = math.radians(tilt)
    lat = np.arcsin(np.clip(ys * math.cos(a) - z * math.sin(a), -1, 1))
    p = math.pi / lines
    dist = np.abs(((lat / p) % 1) - 0.5) * 2
    ink = inside & (dark > 0.10) & (dist > 1 - np.clip(dark * 0.95, 0.10, 0.92))
    ring = (r <= 0.955) & (r >= 0.935)
    return _out(ink | ring, px)


def engraved_eclipse(px, lines=16):
    """E2: the eclipse, engraved: a fine ring, and the shadow disc drawn in rings of line that thicken toward its dark edge."""
    x, y, r = _grid(px)
    ring = (r <= 0.96) & (r >= 0.90)
    cx, cy, R = 0.07, 0.07, 0.72
    dx, dy = x - cx, y - cy; rd = np.sqrt(dx * dx + dy * dy); inside = rd <= R
    toward = np.clip((dx * 0.7 + dy * 0.7) / R, -1, 1)          # 1 at the lower right edge of the disc
    dark = np.clip(0.55 + 0.45 * toward, 0.12, 1)
    p = R / lines
    dist = np.abs(((rd / p) % 1) - 0.5) * 2
    ink = inside & (dist > 1 - dark)
    edge = inside & (rd >= R - 0.02)
    return _out(ring | ink | edge, px)


def engraved_crescent(px, lines=30):
    """E3: a crescent of bare paper, the rest of the moon cross-hatched, the hatching denser deeper into the shadow."""
    x, y, r = _grid(px); moon = r <= 0.94
    lit_c = (0.20, 0.16); lit = np.sqrt((x - lit_c[0]) ** 2 + (y - lit_c[1]) ** 2) > 0.80   # outside the covering disc = lit
    cover = moon & ~lit
    depth = np.clip((np.sqrt((x - lit_c[0]) ** 2 + (y - lit_c[1]) ** 2)) / 0.8, 0, 1)
    depth = 1 - depth                                            # deeper inside the shadow disc = darker
    d1 = np.abs((((x + y) / (2 / lines)) % 1) - 0.5) * 2
    d2 = np.abs((((x - y) / (2 / lines)) % 1) - 0.5) * 2
    h1 = d1 > 1 - np.clip(0.35 + 0.45 * depth, 0, 1)
    h2 = (d2 > 1 - np.clip(0.25 + 0.45 * depth, 0, 1)) & (depth > 0.05)
    ring = (r <= 0.955) & (r >= 0.935)
    return _out((cover & (h1 | h2)) | ring, px)


def wordmark(text_parts, font_path, cap_ref, moon_fn, width_px, caps=False):
    """Set the name with the moon standing in for one o. text_parts: list of strings and None (None = the moon)."""
    size = 400; f = ImageFont.truetype(font_path, size)
    tmp = Image.new("L", (10, 10)); d = ImageDraw.Draw(tmp)
    ref = d.textbbox((0, 0), cap_ref, font=f); h_o = ref[3] - ref[1]          # height of the letter the moon replaces
    mo = int(h_o * 1.06)                                                     # a round letter overshoots a little
    widths = [d.textlength(p, font=f) if p is not None else mo + size * 0.04 for p in text_parts]
    W_ = int(sum(widths) + size * 0.2); H_ = int(size * 1.4)
    m = Image.new("L", (W_, H_), 0); dm = ImageDraw.Draw(m)
    base_top = int(size * 0.2); x = size * 0.1
    moon = moon_fn(mo)
    for p, w in zip(text_parts, widths):
        if p is None:
            m.paste(255, (int(x + size * 0.02), base_top + ref[1] - int(mo * 0.03)), moon)
        else:
            dm.text((x, base_top), p, font=f, fill=255)
        x += w
    m = m.crop(m.getbbox())
    return m.resize((width_px, int(m.height * width_px / m.width)), Image.LANCZOS)


def main():
    # sheet 1: the moon itself, engraved three ways, next to the flat one
    T = 520; G = 26
    moons = [("FLAT (the eclipse so far)", lambda px: B.fit(A.eclipse(px), px, px)),
             ("E1  ENGRAVED SPHERE", engraved_sphere), ("E2  ENGRAVED ECLIPSE", engraved_eclipse), ("E3  CROSS-HATCHED", engraved_crescent)]
    sh = Image.new("RGB", (4 * T + 5 * G, T + 170), (24, 24, 24)); d = ImageDraw.Draw(sh)
    A.label(d, (G, 22), "THE MOON, ENGRAVED", 44, (240, 200, 140))
    for i, (lab, fn) in enumerate(moons):
        x = G + i * (T + G); y = 90
        sh.paste(LIGHT, (x, y, x + T, y + T)); g = fn(T - 90)
        sh.paste(GROUND, (x + 45, y + 45), g)
        A.label(d, (x + 6, y + T + 12), lab, 24, (230, 230, 230))
    sh.save(S / "moon_engraved.jpg", quality=92)

    # sheet 2: the moon as the o, in 'of' and in 'Shadow', two faces, two engravings
    rows = [
        ("Marcellus, the moon as the o of 'of'", ["Inch ", None, "f Shadow"], MARC, "o", False),
        ("Marcellus, the moon as the o of 'Shadow'", ["Inch of Shad", None, "w"], MARC, "o", False),
        ("Impact, the moon as the O of 'OF'", ["INCH ", None, "F SHADOW"], IMPACT, "O", True),
        ("Impact, the moon as the O of 'SHADOW'", ["INCH OF SHAD", None, "W"], IMPACT, "O", True),
    ]
    cols = [("E1 sphere", engraved_sphere), ("E2 eclipse", engraved_eclipse)]
    TW, TH = 900, 300
    sh = Image.new("RGB", (2 * TW + 3 * G, 100 + len(rows) * (TH + 70)), (24, 24, 24)); d = ImageDraw.Draw(sh)
    A.label(d, (G, 22), "THE MOON INSIDE THE NAME", 44, (240, 200, 140))
    for c, (clab, fn) in enumerate(cols):
        A.label(d, (G + c * (TW + G), 76), clab, 22, (150, 220, 150))
    for r_, (lab, parts, font, ref, caps) in enumerate(rows):
        y = 110 + r_ * (TH + 70)
        for c, (clab, fn) in enumerate(cols):
            x = G + c * (TW + G)
            sh.paste(LIGHT, (x, y, x + TW, y + TH))
            wm = wordmark(parts, font, ref, fn, TW - 120)
            sh.paste(GROUND, (x + 60, y + (TH - wm.height) // 2), wm)
            small = wordmark(parts, font, ref, fn, 220)            # how it reads small, in a corner
            sh.paste(GROUND, (x + TW - 240, y + TH - small.height - 14), small)
        A.label(d, (G, y + TH + 10), lab + "   (bottom right: the same at small size)", 22, (220, 220, 220))
    sh.save(S / "moon_in_name.jpg", quality=92)
    print("ok")


if __name__ == "__main__":
    main()
