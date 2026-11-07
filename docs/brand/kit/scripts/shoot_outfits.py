"""Group the outdoor shoot by outfit: the styling tag first, the capture time where the tag is vague
(black and white frames tagged 'light shirt' or just 'shirt'). Writes `outfit` per photo and an
`outfits` list into the catalogue. Local only, no image is changed."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode")
import shoot_catalogue as sc

CAT = Path("plans/control-panel/shoot-catalogue.json")
OUTFITS = [   # key, label, colour word, swatch, capture window (fallback when the tag is vague)
    ("polka",   "cream polka-dot shirt",  "cream",        "#E8DCC0", "19:50", "19:55"),
    ("polka_jacket", "black jacket over the polka-dot shirt", "black on cream", "#3A3630", "19:55", "20:00"),
    ("green",   "green satin shirt",      "green",        "#2F5A3A", "20:04", "20:14"),
    ("red",     "red shirt",              "red",          "#9B1E2A", "20:23", "20:30"),
    ("red_jacket", "black jacket over the red shirt", "black on red", "#3A1C1E", "20:30", "20:33"),
    ("tank",    "black tank top",         "black",        "#151515", "20:36", "20:47"),
    ("striped", "striped shirt",          "stripes",      "#7A7A7A", "20:43", "20:46"),
    ("leather", "black leather jacket",   "black leather","#0B0B0B", "20:47", "20:50"),
    ("white_tank", "white tank top",      "white",        "#F2F2F2", "20:50", "20:55"),
    ("sheer",   "sheer black shirt",      "sheer black",  "#262626", "20:55", "21:04"),
    ("white_satin", "white satin shirt",  "white satin",  "#EDE9E0", "21:06", "21:17"),
    ("yellow",  "pale yellow shirt",      "pale yellow",  "#E9DFA0", "21:26", "21:30"),
]
KEYS = [("polka", "polka"), ("green satin", "green"), ("red", "red"), ("black tank", "tank"), ("white tank", "white_tank"),
        ("tank top", "tank"), ("striped", "striped"), ("leather", "leather"), ("sheer", "sheer"), ("black shirt", "sheer"),
        ("white satin", "white_satin"), ("white shirt", "white_satin"), ("yellow", "yellow")]

def assign(p):
    s = (p["tags"].get("styling") or "").lower(); t = p["captured"][11:16]
    if "jacket" in s and "leather" not in s:
        return ("polka_jacket" if t < "20:00" else "red_jacket"), "styling tag"
    for word, key in KEYS:
        if word in s:
            return key, "styling tag"
    for key, *_, a, b in OUTFITS:
        if a <= t <= b:
            return key, "capture time"
    return None, None

cat = json.loads(CAT.read_text()); by = {}
for p in cat["photos"]:
    key, how = assign(p); p["outfit"] = key; by.setdefault(key, []).append(p)
    if how == "capture time": print("by time:", p["id"], p["captured"][11:16], "|", p["tags"].get("styling"))
order = [o[0] for o in OUTFITS]
cat["outfits"] = []
for key, label, colour, swatch, *_ in OUTFITS:
    ps = sorted(by.get(key, []), key=lambda p: p["captured"])
    cat["outfits"].append({"key": key, "label": label, "colour": colour, "swatch": swatch, "count": len(ps),
                           "from": ps[0]["captured"][11:16], "to": ps[-1]["captured"][11:16],
                           "settings": sorted({(p["tags"].get("setting") or "").split(",")[0] for p in ps})})
    print(f"{key:12s} {len(ps):3d}  {ps[0]['captured'][11:16]}-{ps[-1]['captured'][11:16]}")
print("unassigned:", [p["id"] for p in by.get(None, [])])
cat["notes_outfits"] = ("outfit = which shirt he wore, assigned 2026-09-26 from the styling tag, or from the capture time for "
                        "black-and-white frames whose tag only says 'light shirt' or 'shirt'. Order of the day: " + ", ".join(order) + ".")
if "--write" in sys.argv:
    CAT.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n"); print("written")
# contact sheets, one per outfit, for checking by eye
for key, label, *_ in OUTFITS:
    ps = sorted(by.get(key, []), key=lambda p: p["captured"]); cols = 8; tw = 150
    rows = (len(ps) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (tw + 18) + 30), (30, 30, 30)); d = ImageDraw.Draw(sheet)
    d.text((6, 6), f"{key}: {label} ({len(ps)})", fill=(240, 220, 160))
    for i, p in enumerate(ps):
        f = sc.cache_path(p["raw"])
        if f.is_file():
            im = Image.open(f); im.thumbnail((tw - 4, tw - 4)); x, y = (i % cols) * tw, 30 + (i // cols) * (tw + 18)
            sheet.paste(im, (x + 2, y + 2)); d.text((x + 4, y + tw + 2), f"{p['id']} {p['captured'][11:16]}", fill=(200, 200, 200))
    sheet.save(f"/private/tmp/claude-501/-Users-amir-Desktop-Inch-of-Shadow/b22299d3-ce74-437a-a1cb-0b6b5a9c3dbf/scratchpad/outfit_{key}.jpg", quality=85)
