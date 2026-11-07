#!/usr/bin/env python3
"""Find photos in the shoot catalogue and SEE them, before choosing one.

The catalogue tags say what is in a photo (framing, face, light, styling, setting, motifs,
feeling) but not where the calm area for text is. Only looking tells you that.

    contact_sheet.py --where "blue hour" --where sunglasses --orientation portrait --out sheet.jpg
    contact_sheet.py --ids out-055 out-056 --out sheet.jpg
    contact_sheet.py --stars 2 --unused --no-ai-on-him --out sheet.jpg

--stars 2 = the photographer's own top picks (25 of 204; the 1-star ones are all still good).
--unused = never posted yet. --no-ai-on-him / --no-ai = leave out frames where she used
Lightroom's generative fill on him / anywhere. --flash / --no-flash from the camera data.

Every --where word must appear somewhere in the photo's tags (case-insensitive). Reads the
files on the drive, writes ONLY the sheet. Never changes anything on the drive.
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.dont_write_bytecode = True


def catalogue() -> tuple[dict, Path]:
    here = Path(__file__).resolve()
    for root in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        p = root / "Inchofshadowcode/plans/control-panel/shoot-catalogue.json"
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8")), p
    sys.exit("shoot-catalogue.json not found")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--where", action="append", default=[], help="word that must appear in the tags (repeatable)")
    ap.add_argument("--orientation", choices=["portrait", "landscape", "square"])
    ap.add_argument("--ids", nargs="*", default=[])
    ap.add_argument("--stars", type=int, choices=[1, 2], help="her Lightroom rating; 2 = her top picks")
    ap.add_argument("--unused", action="store_true", help="only photos never posted (no used_in)")
    ap.add_argument("--no-ai-on-him", action="store_true", help="leave out frames with a generative fill on him")
    ap.add_argument("--no-ai", action="store_true", help="leave out frames with any generative fill")
    fl = ap.add_mutually_exclusive_group()
    fl.add_argument("--flash", action="store_true")
    fl.add_argument("--no-flash", action="store_true")
    ap.add_argument("--max", type=int, default=24)
    ap.add_argument("--thumb", type=int, default=360, help="tile height in px")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    cat, _ = catalogue()
    root = Path(cat["root"])
    if not root.is_dir():
        sys.exit(f"The photo drive is not connected: {root}")
    picks = []
    for p in cat["photos"]:
        blob = " ".join(str(v) for v in p["tags"].values()).lower()
        if a.ids and p["id"] not in a.ids:
            continue
        if a.orientation and p.get("orientation") != a.orientation:
            continue
        if a.stars and p.get("her_rating") != a.stars:
            continue
        if a.unused and p.get("used_in"):
            continue
        ai = p.get("ai_generated") or {}
        if (a.no_ai and ai) or (a.no_ai_on_him and ai.get("on_him")):
            continue
        fired = (p.get("camera") or {}).get("flash")
        if (a.flash and not fired) or (a.no_flash and fired):
            continue
        if all(w.lower() in blob for w in a.where):
            picks.append(p)
    print(f"{len(picks)} photo(s) match; showing {min(len(picks), a.max)}")
    picks = picks[: a.max]
    if not picks:
        sys.exit(1)

    tiles = []
    for p in picks:
        f = root / p["edit"]
        if not f.is_file():
            print(f"  missing on drive: {p['edit']}")
            continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im.thumbnail((a.thumb * 2, a.thumb))
        tiles.append((p, im))
        print(f"  {p['id']}  {p['edit'].split('/')[-1]}  | {p['tags']['framing']} | {p['tags']['light']} | {p['tags']['feeling']}")

    pad, label = 12, 18
    cols = min(6, len(tiles))
    col_w = max(t.size[0] for _, t in tiles) + pad
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * col_w + pad, rows * (a.thumb + label + pad) + pad), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(tiles):
        x = pad + (i % cols) * col_w
        y = pad + (i // cols) * (a.thumb + label + pad)
        mark = ("  **" if p.get("her_rating") == 2 else "") + ("  AI" if p.get("ai_generated") else "")
        d.text((x, y), p["id"] + mark, fill=(230, 200, 120) if p.get("her_rating") == 2 else (210, 210, 210))
        sheet.paste(im, (x, y + label))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=88)
    print(f"sheet written: {a.out}  -> look for a calm area big enough for the text, away from his head")


if __name__ == "__main__":
    main()
