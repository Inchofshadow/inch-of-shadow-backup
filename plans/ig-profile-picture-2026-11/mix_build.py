"""Effects mixer renders (Amir 11-19 "try some of our effects on them"). Local only: print_looks.py
(no AI, never redraws his face). Input = the 1080 upload crops; output = 640 px previews per look."""
import sys, json, time, pathlib
from PIL import Image
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
import print_looks as PL
PHOTOS = sys.argv[1:] or ["out-037", "out-039", "out-142", "out-079", "out-077"]
OUT = HERE / "looks"
meta = {}
for k in PHOTOS:
    src = Image.open(HERE / f"upload_1080_{k}.jpg").convert("RGB")
    d = OUT / k; d.mkdir(parents=True, exist_ok=True)
    src.resize((640, 640), Image.LANCZOS).save(d / "original.jpg", quality=84)
    for name in PL.LOOKS:
        t = time.time()
        try:
            im = PL.apply_look(src, name).convert("RGB")
            im.resize((640, 640), Image.LANCZOS).save(d / f"{name}.jpg", quality=84)
        except Exception as e:
            print("FAIL", k, name, e); continue
        print(k, name, round(time.time() - t, 1), flush=True)
json.dump({n: {"code": v[0], "name": v[1], "what": v[2]} for n, v in PL.LOOKS.items()}, open(HERE / "looks" / "looks.json", "w"), indent=1)
