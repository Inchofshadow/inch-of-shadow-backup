"""Small previews of HER EDITS for the Shoot page, so what shows on screen is what she made (the raw
previews are in colour even where her edit is black and white). Reads the edits from the Intenso,
writes 1024 px JPEGs to ~/.cache; never touches the originals. Local only, no AI.

    python3 docs/brand/kit/scripts/shoot_edit_previews.py          # the ones missing
    python3 docs/brand/kit/scripts/shoot_edit_previews.py --all    # redo every one
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[4]
DRIVE = Path("/Volumes/Intenso/Inch of Shadow photoshoot")
CATALOGUE = ROOT / "plans" / "control-panel" / "shoot-catalogue.json"
CACHE = Path.home() / ".cache" / "inch-of-shadow" / "shoot-edit-previews"
EDGE = 1024


def preview_path(photo_id: str) -> Path:
    return CACHE / f"{photo_id}.jpg"


def build(photo: dict, redo: bool = False) -> str:
    out = preview_path(photo["id"])
    if out.is_file() and not redo:
        return "kept"
    src = DRIVE / photo["edit"]
    if not src.is_file():
        return "no drive"
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)
        im.thumbnail((EDGE, EDGE), Image.LANCZOS)
        CACHE.mkdir(parents=True, exist_ok=True)
        im.convert("RGB").save(out, quality=88, **({"icc_profile": icc} if icc else {}))
    return "made"


def main() -> None:
    photos = json.loads(CATALOGUE.read_text())["photos"]
    counts = {}
    for p in photos:
        r = build(p, "--all" in sys.argv); counts[r] = counts.get(r, 0) + 1
    print(", ".join(f"{v} {k}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
