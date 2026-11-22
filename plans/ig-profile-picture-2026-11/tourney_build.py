"""Tournament entrants (Amir 11-19 "show me the final, let's make the tournament, clean similar options").
Composites use the page's own blend: original -> look A at wa% -> look B at wb% (normal). Local only."""
import json, pathlib
from PIL import Image
HERE = pathlib.Path(__file__).parent
# 6 distinct effect versions of out-037 (near-twins left out: riso100+nightflash20 = riso80+nightflash20;
# riso80+cyanotype17 and riso80+halftone15 look the same at 40 px; riso25+mono73 = riso68+mono70;
# monotint+halation13 and +blowout13 = monotint+cyanotype21) + the 5 finalist photos plain.
# Round 2 (Amir 11-19 "we will choose 37", "the tournament with 37 effects"): only out-037, plain + 6 effects.
ENTRANTS = [
 ("037-plain", "out-037", None, 0, None, 0, "No effect"),
 ("037-riso-soft", "out-037", "riso", 68, None, 0, "Riso 68%"),
 ("037-riso-flash", "out-037", "riso", 80, "nightflash", 20, "Riso 80% + Night flash 20%"),
 ("037-riso-blowout", "out-037", "riso", 100, "blowout", 8, "Riso 100% + Blowout 8%"),
 ("037-lilac", "out-037", "riso", 68, "monotint", 70, "Riso 68% + Monotint 70% (lilac)"),
 ("037-mono-night", "out-037", "monotint", 100, "monotintnight", 11, "Monotint 100% + Monotint night 11%"),
 ("037-mono-cyan", "out-037", "monotint", 100, "cyanotype", 21, "Monotint 100% + Cyanotype 21%"),
]
def comp(ph, a, wa, b, wb, size):
    src = lambda n: Image.open(HERE / "looks" / ph / f"{n}.jpg").convert("RGB")
    o = src("original")
    if a and wa: o = Image.blend(o, src(a), wa / 100)
    if b and wb: o = Image.blend(o, src(b), wb / 100)
    return o.resize((size, size), Image.LANCZOS)
out = HERE / "tourney"; out.mkdir(exist_ok=True)
meta = []
for key, ph, a, wa, b, wb, label in ENTRANTS:
    comp(ph, a, wa, b, wb, 640).save(out / f"{key}.jpg", quality=86)
    meta.append({"key": key, "ph": ph, "a": a, "wa": wa, "b": b, "wb": wb, "label": label})
json.dump(meta, open(out / "entrants.json", "w"), indent=1)
print(len(meta))
