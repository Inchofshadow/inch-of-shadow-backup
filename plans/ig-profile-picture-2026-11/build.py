"""IG profile picture picks 2026-11-18. Local only: crop, resize, circle mask. No AI.
Reads the drive originals read-only; writes previews + 1080 square uploads into this folder."""
import json, base64, io, pathlib
from PIL import Image, ImageDraw, ImageOps
HERE = pathlib.Path(__file__).parent
CAT = json.load(open(HERE.parent / "control-panel/shoot-catalogue.json"))
P = {p["id"]: p for p in CAT["photos"]}
# Round 3 (Amir 11-18 "not sure you cropped well"): one framing rule for every pick.
# Head measured by eye on a grid: (top of hair y, chin y) as share of height, head centre x as share of width.
HEADS = {"in-003": (.08, .34, .45), "out-087": (.04, .44, .50), "in-125": (.05, .45, .50), "in-189": (.05, .30, .47),
         "in-129": (.05, .21, .38), "out-027": (.12, .43, .50), "in-056": (.05, .48, .45), "out-149": (.05, .25, .52),
         "out-190": (.18, .35, .42), "out-001": (.36, .52, .52), "out-166": (.03, .45, .45), "in-193": (.07, .33, .48),
         "in-238": (.07, .27, .47), "out-151": (.12, .30, .47), "in-023": (.08, .28, .42),
         # round 4 (Amir 11-18 "give me more options now"), leaning on his V ticks
         "in-124": (.09, .32, .45), "in-136": (.06, .30, .52), "in-138": (.06, .29, .52), "in-210": (.10, .31, .58),
         "in-225": (.02, .45, .55), "out-077": (.18, .41, .43), "out-117": (.24, .45, .50), "out-023": (.15, .38, .52),
         "out-037": (.18, .40, .45), "out-011": (.07, .36, .48), "out-050": (.12, .32, .50), "out-067": (.15, .35, .44),
         # round 5 (Amir 11-18 "give me more options now" again)
         "out-038": (.20, .43, .45), "out-024": (.14, .37, .55), "out-076": (.28, .45, .43), "out-128": (.30, .47, .55),
         "out-145": (.16, .32, .40), "out-049": (.20, .35, .50), "out-025": (.09, .26, .49), "in-211": (.11, .32, .62),
         "in-214": (.07, .30, .68), "in-232": (.07, .43, .48), "in-135": (.10, .34, .50), "in-001": (.08, .32, .38),
         # round 6 (Amir 11-18: "a few with the black tank but not only those", "my full hair to be present")
         "out-026": (.15, .33, .48), "out-035": (.18, .35, .48), "out-039": (.23, .40, .48), "out-129": (.06, .24, .52),
         "in-212": (.06, .27, .68), "in-209": (.07, .30, .62), "out-142": (.19, .34, .48), "out-079": (.16, .30, .57),
         # round 7 finals (Amir 11-19: continue with 037 039 + 142 079 077, more from these families)
         "out-036": (.23, .43, .45), "out-080": (.11, .27, .55), "out-081": (.08, .30, .44), "out-082": (.07, .34, .50),
         "out-150": (.21, .40, .48), "out-083": (.17, .33, .44), "out-152": (.08, .30, .40), "out-144": (.17, .34, .45),
         "out-078": (.14, .32, .50)}
HEAD_SHARE = 0.45   # head (hair to chin) = 45% of the circle's height: head and some shoulder
TOP_ROOM = 0.18     # space above the hair = 18% (round 6: full hair always in) of the circle
PICKS = list(HEADS)
BLACK = (15, 13, 12)
def b64(im, q=88):
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q); return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
out = {}
for k in PICKS:
    top, chin, hx = HEADS[k]
    p = P[k]; im = ImageOps.exif_transpose(Image.open(CAT["root"] + "/" + p["edit"])).convert("RGB"); w, h = im.size
    hh = (chin - top) * h; s = min(int(hh / HEAD_SHARE), w, h)
    l = max(0, min(w - s, int(hx * w - s / 2))); t = max(0, min(h - s, int(top * h - TOP_ROOM * s)))
    sq = im.crop((l, t, l + s, t + s))
    up = sq.resize((1080, 1080), Image.LANCZOS)
    up.save(HERE / f"upload_1080_{k}.jpg", quality=95)
    # zoom files for the page (tap to zoom): whole photo 1800 px long side, crop 1080
    (HERE / "zoom").mkdir(exist_ok=True)
    z = im.copy(); z.thumbnail((1800, 1800), Image.LANCZOS); z.save(HERE / "zoom" / f"full_{k}.jpg", quality=85)
    up.save(HERE / "zoom" / f"crop_{k}.jpg", quality=85)
    full = im.copy(); full.thumbnail((640, 640), Image.LANCZOS)
    canvas = Image.new("RGB", (640, 640), BLACK); canvas.paste(full, ((640 - full.width) // 2, (640 - full.height) // 2))
    out[k] = {"full": b64(canvas), "c110": b64(sq.resize((330, 330), Image.LANCZOS)), "c40": b64(sq.resize((120, 120), Image.LANCZOS)),
              "edit": p["edit"], "rating": p.get("her_rating"), "tags": p["tags"]}
json.dump(out, open(HERE / "previews.json", "w"))
print({k: len(v["full"]) + len(v["c110"]) + len(v["c40"]) for k, v in out.items()})
