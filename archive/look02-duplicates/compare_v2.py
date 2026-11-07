"""Old next to new, sorted by family."""
from PIL import Image, ImageDraw
import logo_sketches as A, logo_round_b as B, logo_round_c as C, logo_round_d as D, logo_round_e as E, logo_round_g as G
import logo_v2 as V
from logo_sketches import GROUND, S

LIGHT = (236, 232, 224)
OLD = {"1": A.eclipse, "4": A.inch_mark, "14": C.sword, "20": D.shadow_only, "21": D.sinking, "25": D.long_shadow,
       "27": E.stamp, "29": E.photocopy, "30": E.typewriter, "43": G.torn_strip, "28": E.stencil, "31": E.bitmap}
NAMES = {"1": "THE ECLIPSE", "4": "THE INCH MARK", "14": "THE SWORD", "20": "THE NAME IN ITS SHADOW", "21": "THE NAME SINKING",
         "25": "THE LONG SHADOW", "27": "THE STAMP", "29": "THE PHOTOCOPY", "30": "THE TYPEWRITER", "43": "THE TORN STRIP",
         "28": "THE SPRAY", "31": "THE BITMAP"}
FAMILIES = [("FAMILY 1  -  THE MARKS", ["1", "4", "14"]), ("FAMILY 2  -  THE NAME AS SHADOW", ["20", "21", "25"]),
            ("FAMILY 3  -  PRESSED AND PRINTED", ["27", "29", "30", "43"]), ("FAMILY 4  -  STREET AND SCREEN", ["28", "31"])]
T = 520; G_ = 24


def tile(mask, x, y, sheet, label, col):
    sheet.paste(LIGHT, (x, y, x + T, y + T)); g = B.fit(mask, T - 80, T - 80)
    sheet.paste(GROUND, (x + (T - g.width) // 2, y + (T - g.height) // 2), g)
    A.label(ImageDraw.Draw(sheet), (x + 6, y + T + 8), label, 24, col)


for fi, (title, ids) in enumerate(FAMILIES, start=1):
    H = 110 + len(ids) * (T + 70)
    sheet = Image.new("RGB", (2 * T + 3 * G_ + 300, H), (24, 24, 24)); d = ImageDraw.Draw(sheet)
    A.label(d, (G_, 24), title, 46, (240, 200, 140))
    A.label(d, (300 + G_, 80), "BEFORE", 22, (150, 150, 150)); A.label(d, (300 + 2 * G_ + T, 80), "NOW", 22, (150, 220, 150))
    for r, k in enumerate(ids):
        y = 110 + r * (T + 70)
        A.label(d, (G_, y + T // 2 - 40), k, 64, (240, 200, 140))
        A.label(d, (G_, y + T // 2 + 36), NAMES[k].replace("THE ", ""), 22, (200, 200, 200))
        tile(OLD[k](700), 300 + G_, y, sheet, "before", (140, 140, 140))
        tile(V.V2[k](), 300 + 2 * G_ + T, y, sheet, "now", (150, 220, 150))
    sheet.save(S / f"v2_family_{fi}.jpg", quality=92)

order = ["1", "4", "14", "20", "21", "25", "27", "29", "30", "43", "28", "31"]
ov = Image.new("RGB", (6 * 320 + 40, 2 * 390 + 30), (24, 24, 24)); d = ImageDraw.Draw(ov)
for i, k in enumerate(order):
    x = 20 + (i % 6) * 320; y = 20 + (i // 6) * 390
    ov.paste(LIGHT, (x + 6, y, x + 314, y + 308)); g = B.fit(V.V2[k](), 250, 250)
    ov.paste(GROUND, (x + 6 + (308 - g.width) // 2, y + (308 - g.height) // 2), g)
    A.label(d, (x + 10, y + 318), f"{k}  {NAMES[k].replace('THE ', '')}", 22, (235, 235, 235))
ov.save(S / "v2_all.jpg", quality=92)
print("ok")
