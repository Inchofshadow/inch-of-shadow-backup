"""Look-02: everything Amir kept, side by side. Two places only: a T-shirt and a cover."""
from PIL import Image, ImageDraw
import logo_sketches as A
import logo_round_b as B
import logo_round_c as C
import logo_round_d as D
import logo_round_e as E
import logo_round_g as G
from logo_sketches import GROUND, INK, S

LIGHT = (236, 232, 224)
PICKS = [
    ("1  ECLIPSE", A.eclipse, "symbol"),
    ("4  INCH MARK", A.inch_mark, "symbol"),
    ("14 SWORD", C.sword, "symbol"),
    ("20 NAME IN ITS SHADOW", D.shadow_only, "name"),
    ("21 NAME SINKING", D.sinking, "name"),
    ("25 LONG SHADOW", D.long_shadow, "name"),
    ("27 STAMP", E.stamp, "name"),
    ("28 SPRAY", E.stencil, "name"),
    ("29 PHOTOCOPY", E.photocopy, "name"),
    ("30 TYPEWRITER", E.typewriter, "name"),
    ("31 BITMAP", E.bitmap, "name"),
    ("43 TORN STRIP", G.torn_strip, "name"),
]


def cover(sym):
    """The Deceiver's cover with the type painted out, the mark small at the foot."""
    im = Image.open(S / "cover_notype.png").convert("RGB").resize((380, 380), Image.LANCZOS)
    g = B.fit(sym, 170, 95)                       # the calm band at the top, where the type used to be
    im.paste(INK, ((380 - g.width) // 2, 60 - g.height // 2 + 30), g)
    return im


def tshirt(sym):
    im = B._T(Image.new("L", sym.size, 0)); g = B.fit(sym, 210, 190)
    im.paste(INK, (260 - g.width // 2, 250 - g.height // 2), g)
    return im.resize((420, 452))


def main():
    syms = [(t, fn(600), kind) for t, fn, kind in PICKS]

    # 1. all of them side by side, same size, nothing else
    cols, tile = 6, 300
    ov = Image.new("RGB", (cols * tile + 40, 2 * (tile + 70) + 30), (24, 24, 24)); d = ImageDraw.Draw(ov)
    for i, (title, sym, kind) in enumerate(syms):
        x = 20 + (i % cols) * tile; y = 20 + (i // cols) * (tile + 70)
        ov.paste(LIGHT, (x + 6, y, x + tile - 6, y + tile))
        g = B.fit(sym, tile - 60, tile - 60)
        ov.paste(GROUND, (x + (tile - g.width) // 2, y + (tile - g.height) // 2), g)
        A.label(d, (x + 8, y + tile + 12), title, 24, (240, 200, 140) if kind == "symbol" else (200, 220, 200))
        A.label(d, (x + 8, y + tile + 42), "a symbol, works alone" if kind == "symbol" else "the name, a treatment", 20, (140, 140, 140))
    ov.save(S / "picks_side_by_side.jpg", quality=92)

    # 2. the same twelve on a shirt and on a cover
    for part in (0, 1):
        chunk = syms[part * 6:(part + 1) * 6]
        sheet = Image.new("RGB", (3 * 460 + 60, len(chunk) * 470), (24, 24, 24)); d = ImageDraw.Draw(sheet)
        for r, (title, sym, kind) in enumerate(chunk):
            y = r * 470 + 20
            A.label(d, (20, y), title, 30, (240, 200, 140) if kind == "symbol" else (200, 220, 200))
            box = Image.new("RGB", (400, 380), LIGHT)
            g = B.fit(sym, 340, 320); box.paste(GROUND, ((400 - g.width) // 2, (380 - g.height) // 2), g)
            sheet.paste(box, (20, y + 40))
            sheet.paste(tshirt(sym), (470, y + 10))
            sheet.paste(cover(sym), (940, y + 40))
        for x, cap in ((20, "the mark"), (470, "T-shirt"), (940, "cover")):
            A.label(d, (x, len(chunk) * 470 - 26), cap, 22, (150, 150, 150))
        sheet.save(S / f"picks_in_place_{part + 1}.jpg", quality=90)
    print("ok")


main()
