#!/usr/bin/env python3
"""Pull a photo out of the shoot, cropped for a platform with him kept in frame (Look-10).

    shoot_pull.py out-066 --format post                 one format
    shoot_pull.py out-066 --format all --check          every format + a sheet showing the crops
    shoot_pull.py --raw "Outdoor/Outdoor Shoot 7/Raw/DSC_6702.NEF" --family dusk --format reel
                                                        an UNEDITED raw: graded by our recipe first

Why: every edit is 3:2 (8256 px), and no platform wants 3:2. Instagram takes 4:5 or 3:4 in
the feed and 9:16 for stories and reels. A centre crop cuts heads off, so the crop is placed
on his HEAD. For the 204 catalogued edits the position is known: every one was checked by
eye on 2026-09-21 (`subject` in the catalogue). A classical face finder is only the fallback,
for a raw nobody has looked at yet. Local and free, no AI.

Why not trust the finder: measured against the verified positions it is right 65% of the time
(81% when it reports a face, 27% when it falls back to the centre). It fails on lying, tilted
and from-above poses, and sometimes circles the ground or a hand with full confidence.
So for a --raw, ALWAYS look at the --check sheet. The calm area for type stays a human call.

Reads from the drive, writes only into generated_images/shoot/ on the Mac. Find photos with
the brand kit's contact_sheet.py (--where, --stars 2, --unused, --no-ai-on-him).
"""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import shoot_catalogue as sc  # noqa: E402

OUT = ROOT / "generated_images" / "shoot"
FORMATS = {                      # name: (width, height, where the face sits, top to bottom)
    "post":     (1080, 1350, 0.36),   # 4:5 feed post
    "carousel": (1080, 1440, 0.36),   # 3:4, fills the grid tile
    "reel":     (1080, 1920, 0.33),   # 9:16 story, reel, Spotify Canvas still
    "square":   (1080, 1080, 0.40),
    "wide":     (1920, 1080, 0.42),   # 16:9 YouTube
}
COLOURS = {"post": (255, 90, 90), "carousel": (255, 190, 80), "reel": (110, 200, 255),
           "square": (170, 255, 140), "wide": (220, 140, 255)}


def _rot_point(x, y, w, h, quarter):
    """A point found in the frame rotated by `quarter` x 90 degrees (counter-clockwise), mapped back."""
    for _ in range(quarter):                                   # undo one CCW quarter turn at a time
        x, y, w, h = h - 1 - y, x, h, w                      # the turned frame's height is the upright width
    return x, y


def find_subject(im: Image.Image) -> tuple:
    """(x, y, how) in 0..1 of the frame. Faces first, then a standing figure, then the centre.

    Half this shoot is tilted, lying or shot from above, and a classical face finder only
    knows upright faces. So the frame is tried at all four quarter turns, frontal and both
    profiles, and the biggest face wins. Upright finds are trusted a little more."""
    import cv2
    small = im.copy()
    small.thumbnail((1400, 1400))
    g0 = cv2.equalizeHist(cv2.cvtColor(np.array(small), cv2.COLOR_RGB2GRAY))
    H0, W0 = g0.shape
    base = cv2.data.haarcascades
    cascades = [(cv2.CascadeClassifier(base + "haarcascade_frontalface_alt2.xml"), False),
                (cv2.CascadeClassifier(base + "haarcascade_profileface.xml"), False),
                (cv2.CascadeClassifier(base + "haarcascade_profileface.xml"), True)]
    best = None
    for quarter in range(4):
        g = np.ascontiguousarray(np.rot90(g0, quarter))
        h, w = g.shape
        for casc, flip in cascades:
            img = cv2.flip(g, 1) if flip else g
            found = casc.detectMultiScale(img, 1.08, 7 if quarter else 6, minSize=(max(w, h) // 26,) * 2)
            for (x, y, fw, fh) in found:
                if flip:
                    x = w - x - fw
                cx, cy = _rot_point(x + fw / 2, y + fh / 2, w, h, quarter)
                score = fw * fh * (1.25 if quarter == 0 else 1.0)
                if best is None or score > best[2]:
                    turned = "" if quarter == 0 else f", head turned {quarter * 90} deg in frame"
                    best = (cx / W0, cy / H0, score, "face" + turned)
    if best:
        return best[0], best[1], best[3]
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    s = 640 / max(H0, W0)
    people, weights = hog.detectMultiScale(cv2.resize(g0, None, fx=s, fy=s), winStride=(8, 8), padding=(8, 8), scale=1.05)
    if len(people):
        x, y, pw, ph = people[int(np.argmax(weights))]
        return (x + pw / 2) / s / W0, (y + ph * 0.18) / s / H0, "figure"   # the head is near the top of a figure
    return 0.5, 0.42, "centre (nothing found, CHECK THIS ONE)"


def crop_box(size: tuple, fmt: str, subject: tuple) -> tuple:
    W, H = size
    tw, th, face_at = FORMATS[fmt]
    ratio = tw / th
    cw, ch = (W, round(W / ratio)) if W / H < ratio else (round(H * ratio), H)
    sx, sy = subject[0] * W, subject[1] * H
    left = min(max(round(sx - cw / 2), 0), W - cw)
    top = min(max(round(sy - ch * face_at), 0), H - ch)
    return left, top, left + cw, top + ch


def load(photo_id: str | None, raw: str | None, family: str | None, brightness: str):
    if raw:
        import edit_recipe as er
        if not family:
            sys.exit("--raw needs --family (" + ", ".join(er.FAMILIES) + "): which light was it shot in?")
        path = sc.DRIVE / raw
        print(f"grading {path.name} with OUR recipe, family '{family}', brightness '{brightness}' (local, no AI)")
        return er.grade(er.load_image(path), family, brightness), path.stem + f"_{family}", None
    cat = json.loads(sc.CATALOGUE.read_text())
    p = next((x for x in cat["photos"] if x["id"] == photo_id), None)
    if p is None:
        sys.exit(f"No photo '{photo_id}' in the catalogue.")
    src = Image.open(sc.DRIVE / p["edit"])
    icc = src.info.get("icc_profile")
    ai = p.get("ai_generated")
    if ai:
        print(f"note: {photo_id} has {ai['areas']} AI-filled area(s) from her edit ({ai['what']}), {ai['on_him']} on him")
    if cat.get("credit"):
        print(f"credit, on every Instagram post from this shoot (Instagram only): {cat['credit']['line']}")
    global _KNOWN
    sub = p.get("subject")
    _KNOWN = (sub["x"], sub["y"], f"head, {sub['source']}") if sub else None
    return ImageOps.exif_transpose(src).convert("RGB"), photo_id, icc


_KNOWN = None


def main() -> None:
    ap = ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("id", nargs="?", help="a catalogue id, e.g. out-066")
    ap.add_argument("--raw", help="an unedited raw, path relative to the shoot root on the drive")
    ap.add_argument("--family", help="light family for --raw (edit_recipe.py families)")
    ap.add_argument("--brightness", default="auto", choices=["darker", "auto", "brighter"])
    ap.add_argument("--format", default="post", choices=[*FORMATS, "all"])
    ap.add_argument("--check", action="store_true", help="also write a sheet showing the subject and every crop")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    if not a.id and not a.raw:
        sys.exit("Give a catalogue id or --raw.")
    if not sc.DRIVE.is_dir():
        sys.exit(f"The photo drive is not connected: {sc.DRIVE}")

    im, stem, icc = load(a.id, a.raw, a.family, a.brightness)
    subject = _KNOWN or find_subject(im)
    print(f"subject: {subject[2]} at {subject[0]:.2f}, {subject[1]:.2f} of the frame")
    a.out.mkdir(parents=True, exist_ok=True)
    fmts = list(FORMATS) if a.format == "all" else [a.format]
    for f in fmts:
        box = crop_box(im.size, f, subject)
        tw, th, _ = FORMATS[f]
        keep = (box[2] - box[0]) * (box[3] - box[1]) / (im.width * im.height)
        out = a.out / f"{stem}_{f}.jpg"
        im.crop(box).resize((tw, th), Image.LANCZOS).save(out, quality=95, **({"icc_profile": icc} if icc else {}))
        print(f"  {f:<9}{tw}x{th}  keeps {keep * 100:>3.0f}% of the frame  -> {out}")

    if a.check:
        sheet = im.copy()
        sheet.thumbnail((1600, 1600))
        k = sheet.width / im.width
        d = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(str(ROOT / "docs/brand/fonts/Marcellus-Regular.ttf"), 26)
        for n, f in enumerate(fmts):
            b = [v * k for v in crop_box(im.size, f, subject)]
            inset = 4 * n                                     # nested boxes stay readable
            d.rectangle([b[0] + inset, b[1] + inset, b[2] - inset, b[3] - inset], outline=COLOURS[f], width=5)
            d.text((b[0] + 12 + inset, b[1] + 8 + inset + 30 * n), f, font=font, fill=COLOURS[f])
        cx, cy = subject[0] * sheet.width, subject[1] * sheet.height
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=(255, 255, 255), width=5)
        d.text((cx + 24, cy - 14), subject[2], font=font, fill=(255, 255, 255))
        out = a.out / f"{stem}_CHECK.jpg"
        sheet.save(out, quality=90)
        print(f"  check sheet -> {out}   LOOK at it: is his head inside every box?")


if __name__ == "__main__":
    main()
