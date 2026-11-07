"""Legibility pass over the cover ideas in shoot-catalogue.json (2026-09-27, Amir: "in some I
can't really see the text"). For every photo it measures the real pixels of her edit inside the
square cover crop, behind each text zone, and:
  - picks the ink that reads: the mood's light colour, or its dark colour on a light background
    (contrast ratio >= 3.0, the WCAG level for large text), recorded as cover_idea.ink;
  - moves a word that sits on his head, or that no ink can read, to the zone that reads best;
  - gives every cover the artist name (a missing name was flagged as wrong).
Local, reads the 1024 px edit previews only. Run from the repo root:
    python3 docs/brand/kit/scripts/cover_legibility.py [--write] [--all]
Only cover ideas not yet measured (no `ink`) are touched; --all redoes every one. Photos
without a cover idea are skipped.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shoot_pull as sp          # noqa: E402
import frame_tokens              # noqa: E402

CAT = ROOT / "plans" / "control-panel" / "shoot-catalogue.json"
PREVIEWS = Path.home() / ".cache" / "inch-of-shadow" / "shoot-edit-previews"
MIN_CONTRAST = 3.0
MOVE_BELOW = 1.8            # a word is moved only when it sits on his head or reads worse than this
RED_OK = 2.5                # the shirt red reads by hue as well as by light, so it passes lower
RED = ("#D8262E", "#0F0D0C")

# text zones as (x0, y0, x1, y1) fractions of the square, for the title by scale and for the name
TITLE = {
    "small": {"TL": (.05, .04, .55, .12), "TC": (.25, .04, .75, .12), "TR": (.45, .04, .95, .12),
              "BL": (.05, .88, .55, .96), "BC": (.25, .88, .75, .96), "BR": (.45, .88, .95, .96),
              "ML": (.05, .46, .55, .54), "MC": (.25, .46, .75, .54), "MR": (.45, .46, .95, .54),
              "VL": (.03, .22, .11, .78), "VR": (.89, .22, .97, .78)},
    "large": {"TL": (.05, .04, .70, .17), "TC": (.15, .04, .85, .17), "TR": (.30, .04, .95, .17),
              "BL": (.05, .83, .70, .96), "BC": (.15, .83, .85, .96), "BR": (.30, .83, .95, .96),
              "ML": (.05, .43, .70, .57), "MC": (.15, .43, .85, .57), "MR": (.30, .43, .95, .57),
              "VL": (.03, .15, .15, .85), "VR": (.85, .15, .97, .85)},
}
NAME = {"TL": (.05, .04, .45, .09), "TC": (.30, .04, .70, .09), "TR": (.55, .04, .95, .09),
        "BL": (.05, .91, .45, .96), "BC": (.30, .91, .70, .96), "BR": (.55, .91, .95, .96),
        "ML": (.05, .475, .45, .525), "MC": (.30, .475, .70, .525), "MR": (.55, .475, .95, .525),
        "VL": (.03, .30, .09, .70), "VR": (.91, .30, .97, .70)}
NAME_ORDER = ["BR", "BL", "TR", "TL", "BC", "TC"]
TITLE_ORDER = ["TL", "TR", "BL", "BR", "TC", "BC", "VL", "VR"]


def hex_rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def ratio(a, b):
    hi, lo = max(a, b), min(a, b); return (hi + 0.05) / (lo + 0.05)


def zone_stats(L, box):
    h, w = L.shape; x0, y0, x1, y1 = box
    z = L[int(y0 * h):max(int(y1 * h), int(y0 * h) + 1), int(x0 * w):max(int(x1 * w), int(x0 * w) + 1)]
    return float(np.percentile(z, 70)), float(np.percentile(z, 30))   # the brighter and darker typical pixels (texture gets the halo)


def best_ink(L, box, pair):
    """(ink hex, contrast) for the better of the pair: light ink judged against the zone's bright
    parts, dark ink against its dark parts (the worst case for each)."""
    bright, dark = zone_stats(L, box)
    light, darkink = pair
    cl = ratio(lum(np.array(hex_rgb(light))), bright)
    cd = ratio(lum(np.array(hex_rgb(darkink))), dark)
    ok = RED_OK if light == RED[0] else MIN_CONTRAST
    return (light, cl) if cl >= cd or cl >= ok else (darkink, cd)


def on_head(box, head, pad=.07):
    x0, y0, x1, y1 = box; hx, hy = head
    return x0 - pad <= hx <= x1 + pad and y0 - pad * 1.4 <= hy <= y1 + pad * 1.4


def on_body(box, head):
    """Below his head and within a shoulder's width of it: where his torso and legs are."""
    x0, y0, x1, y1 = box; hx, hy = head
    return y1 > hy + .12 and x0 < hx + .2 and x1 > hx - .2


def fits_with(name_zone, title_zone, scale="small"):
    """The name never shares a line with the title: it sits on the other row, or stacks under
    the title in the same zone as one block. A vertical title keeps its edge to itself."""
    if name_zone == title_zone:
        return title_zone not in ("VL", "VR", "ML", "MC", "MR")
    if title_zone in ("VL", "VR"):
        return name_zone[1:] != title_zone[1:] or name_zone in ("TC", "BC")
    if title_zone in (None, "none"):
        return True
    return name_zone[0] != title_zone[0]


def main():
    cat = json.loads(CAT.read_text())
    moods = frame_tokens.load(ROOT / "docs" / "brand" / "frame.md").get("moods", {})
    changes = {"ink_dark": 0, "title_moved": 0, "name_added": 0, "name_moved": 0, "still_low": []}
    done = 0
    for p in cat["photos"]:
        i = p.get("cover_idea")
        if not i or (i.get("ink") and "--all" not in sys.argv):
            continue
        done += 1
        pair = RED if i["colour"] == "red" else (moods[i["colour"]]["light"], moods[i["colour"]]["dark"])
        im = Image.open(PREVIEWS / f"{p['id']}.jpg").convert("RGB")
        sub = p.get("subject") or {"x": .5, "y": .42}
        l, t, r, b = sp.crop_box(im.size, "square", (sub["x"], sub["y"], "head"))
        sq = np.asarray(im.crop((l, t, r, b)).resize((300, 300)), dtype=np.float64) / 255
        L = lum(sq)
        head = ((sub["x"] * im.width - l) / (r - l), (sub["y"] * im.height - t) / (b - t))
        # the title
        if i["title_at"] != "none":
            zones = TITLE[i["scale"]]
            ink, c = best_ink(L, zones[i["title_at"]], pair)
            if on_head(zones[i["title_at"]], head) or c < MOVE_BELOW:
                cands = [(best_ink(L, zones[z], pair), z) for z in TITLE_ORDER if not on_head(zones[z], head)]
                (ink2, c2), z2 = max(cands, key=lambda x: x[0][1])
                if c2 > c + .3 or on_head(zones[i["title_at"]], head):
                    i["title_moved_from"] = i["title_at"]; i["title_at"] = z2; ink, c = ink2, c2
                    changes["title_moved"] += 1
            i["ink"] = ink; i["contrast"] = round(c, 1)
        # the name: always there, never on the head, never on the title's corner
        taken = i["title_at"]
        if i["name_at"] == "none":
            i["name_at"] = None; changes["name_added"] += 1
        cands = [z for z in ([i["name_at"]] if i["name_at"] else []) + NAME_ORDER + [taken]
                 if z and fits_with(z, taken, i["scale"]) and not on_head(NAME[z], head)]
        cands = [z for z in cands if not on_body(NAME[z], head)] or cands      # off his body where possible
        scored = [(best_ink(L, NAME[z], pair), z) for z in cands]
        first = scored[0]
        (nink, nc), nz = first if first[0][1] >= MIN_CONTRAST else max(scored, key=lambda x: x[0][1])
        if i["name_at"] and nz != i["name_at"]:
            i["name_moved_from"] = i["name_at"]; changes["name_moved"] += 1
        i["name_at"] = nz; i["name_ink"] = nink; i["name_contrast"] = round(nc, 1)
        if i.get("ink") and i["ink"] == pair[1]:
            changes["ink_dark"] += 1
        if min(i.get("contrast", 9), nc) < MIN_CONTRAST:
            changes["still_low"].append((p["id"], i.get("contrast"), round(nc, 1)))
    print(f"measured {done} cover ideas")
    print(json.dumps({k: (v if not isinstance(v, list) else f"{len(v)}: {v[:12]}") for k, v in changes.items()}, indent=1))
    if "--write" in sys.argv and done:
        from datetime import date
        cat["notes_cover_idea"] += (f" {date.today().isoformat()} legibility pass (cover_legibility.py) over {done} ideas: ink / name_ink = the colour "
                                    "that reads on the pixels behind the zone, words moved off his head or to a zone that reads, the name on every cover.")
        CAT.write_text(json.dumps(cat, indent=1, ensure_ascii=False) + "\n"); print("written")


if __name__ == "__main__":
    main()
