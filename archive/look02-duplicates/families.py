"""Look-02: the twelve picks, big, sorted into families."""
from PIL import Image, ImageDraw
import logo_sketches as A
import logo_round_b as B
import logo_round_c as C
import logo_round_d as D
import logo_round_e as E
import logo_round_g as G
from logo_sketches import GROUND, S

LIGHT = (236, 232, 224)
FAMILIES = [
    ("FAMILY 1  -  THE MARKS", "a sign with no letters in it. It always travels next to the name, and it is what signs a photo or a corner.",
     [("1  THE ECLIPSE", A.eclipse), ("4  THE INCH MARK", A.inch_mark), ("14  THE SWORD", C.sword)]),
    ("FAMILY 2  -  THE NAME AS SHADOW", "the name itself carries the idea: the letters are their own shadow, sink into it, or throw one. Yours alone, nobody else can use these.",
     [("20  THE NAME IN ITS SHADOW", D.shadow_only), ("21  THE NAME SINKING", D.sinking), ("25  THE LONG SHADOW", D.long_shadow)]),
    ("FAMILY 3  -  PRESSED AND PRINTED", "ink on paper: a stamp, a copier, a typewriter, a torn page. Warm, old, human, the world of a zine or a lyric sheet.",
     [("27  THE STAMP", E.stamp), ("29  THE PHOTOCOPY", E.photocopy), ("30  THE TYPEWRITER", E.typewriter), ("43  THE TORN STRIP", G.torn_strip)]),
    ("FAMILY 4  -  STREET AND SCREEN", "hard edges, sprayed on a wall or built from pixels. Loud, young, city and machine.",
     [("28  THE SPRAY", E.stencil), ("31  THE BITMAP", E.bitmap)]),
]

TILE = 620
GAP = 30


def main():
    for i, (title, why, items) in enumerate(FAMILIES, start=1):
        cols = min(3, len(items)); rows = (len(items) + cols - 1) // cols
        W = cols * TILE + (cols + 1) * GAP
        H = 150 + rows * (TILE + 80) + 20
        sheet = Image.new("RGB", (W, H), (24, 24, 24)); d = ImageDraw.Draw(sheet)
        A.label(d, (GAP, 30), title, 54, (240, 200, 140))
        A.label(d, (GAP, 96), why, 28, (185, 185, 185))
        for j, (name, fn) in enumerate(items):
            x = GAP + (j % cols) * (TILE + GAP); y = 150 + (j // cols) * (TILE + 80)
            sheet.paste(LIGHT, (x, y, x + TILE, y + TILE))
            g = B.fit(fn(900), TILE - 110, TILE - 110)
            sheet.paste(GROUND, (x + (TILE - g.width) // 2, y + (TILE - g.height) // 2), g)
            A.label(d, (x + 4, y + TILE + 16), name, 34, (235, 235, 235))
        sheet.save(S / f"picks_family_{i}.jpg", quality=92)
    print("ok")


main()
