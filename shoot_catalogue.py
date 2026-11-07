#!/usr/bin/env python3
"""Shoot catalogue: link the photographer's edits to the raws they came from (Look-08).

    shoot_catalogue.py index INDOOR            index a shoot's raws (time, rotation, preview)
    shoot_catalogue.py index Outdoor
    shoot_catalogue.py link "INDOOR/Indoor Shoot 3/Edited"     match edits to raws
    shoot_catalogue.py link "INDOOR/All Photos" "INDOOR/All Photos 2" --by-image
                                               edits WITHOUT a capture time: image only
    shoot_catalogue.py recheck INDOOR          second look at 2x for what --by-image left unverified
    shoot_catalogue.py verify                  re-derive the known outdoor links, as a test
    shoot_catalogue.py apply                   re-match every catalogued edit, write the links
    shoot_catalogue.py tags [--write]          Blue tag = "this raw was edited"; plan first
    shoot_catalogue.py used <folder> [--write] which edits were already posted (an IG export's media)
    shoot_catalogue.py missed INDOOR           contact sheets of the raws she did NOT edit, per folder
    shoot_catalogue.py status

The archive lives on the Intenso drive. No file on it is ever written, moved or renamed.
The one thing `tags --write` changes is the Finder colour tag on raws, and only after it has
printed its plan; every other command is read only. Previews are cached on the Mac, the index is a small JSON in
plans/control-panel/.

Why it exists: on 2026-09-14 the outdoor edits were matched to their raws by code that ran
once inside a session and was never saved. The edits do not carry the raw's file name, so
the link has to be found: capture time narrows it to the raws within 3 seconds, and image
matching picks the frame, because a burst puts several frames in one second.

How a raw is read: a Nikon NEF is a TIFF. The capture time, the rotation flag and a
full-size JPEG preview sit in the first few MB, so each 50 MB raw costs a 3 MB read and no
raw decoding at all. The rotation flag matters: the first matching attempt on 09-14 failed
because the previews were compared unrotated.
"""
from __future__ import annotations

import io
import json
import struct
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageOps

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
DRIVE = Path("/Volumes/Intenso/Inch of Shadow photoshoot")
INDEX = ROOT / "plans" / "control-panel" / "shoot-raw-index.json"
CATALOGUE = ROOT / "plans" / "control-panel" / "shoot-catalogue.json"
CACHE = Path.home() / ".cache" / "inch-of-shadow" / "shoot-previews"
PREVIEW_EDGE = 1024
WINDOW_S = 3.0                  # an edit's raw was shot within this many seconds of it
CONFIDENT, LIKELY = 25, 12      # homography inliers
ROTATE = {3: 180, 6: 270, 8: 90}
# --by-image (Look-13): the indoor edits came without EXIF, so there is no clock to narrow the
# search. Every raw of the shoot is scored by ORB inliers; frames close to the best are then
# laid onto the edit through their homography and compared by edge correlation (GNCC), which
# tells burst frames apart. Thresholds set on the 204 known outdoor links, 2026-10-14.
NEAR_BEST = 0.4                 # a frame within 40% of the best inlier count is a contender
GNCC_MIN = 0.45                 # lowest correct pick on the 204 outdoor links: 0.50
GNCC_MARGIN = 0.05              # lowest correct lead 0.072; both wrong picks led by 0.011 and 0.022


# ---------------------------------------------------------------- reading a NEF

def read_nef(path: Path) -> dict:
    """Capture time, rotation and the largest embedded JPEG, from the head of the file."""
    with open(path, "rb") as f:
        head = f.read(8)
        bo = "<" if head[:2] == b"II" else ">"

        def u32(b):
            return struct.unpack(bo + "I", b)[0]

        def ifd(off):
            f.seek(off)
            (n,) = struct.unpack(bo + "H", f.read(2))
            out = {}
            for _ in range(n):
                tag, typ, cnt, val = struct.unpack(bo + "HHI4s", f.read(12))
                out[tag] = (cnt, val)
            return out

        def text(entry):
            cnt, val = entry
            if cnt <= 4:
                return val[:cnt].rstrip(b"\0").decode("ascii", "replace")
            f.seek(u32(val))
            return f.read(cnt).rstrip(b"\0").decode("ascii", "replace")

        e0 = ifd(u32(head[4:8]))
        orientation = struct.unpack(bo + "H", e0[0x0112][1][:2])[0] if 0x0112 in e0 else 1

        subs = []
        if 0x014A in e0:                                   # SubIFDs hold the previews
            cnt, val = e0[0x014A]
            if cnt == 1:
                subs = [u32(val)]
            else:
                f.seek(u32(val))
                subs = list(struct.unpack(bo + f"{cnt}I", f.read(4 * cnt)))
        best = None
        for s in subs:
            e = ifd(s)
            if 0x0201 in e and 0x0202 in e:
                off, length = u32(e[0x0201][1]), u32(e[0x0202][1])
                if best is None or length > best[1]:
                    best = (off, length)

        captured = None
        if 0x8769 in e0:                                   # the EXIF block
            ex = ifd(u32(e0[0x8769][1]))
            if 0x9003 in ex:
                stamp = text(ex[0x9003])
                sub = text(ex[0x9291]) if 0x9291 in ex else "0"
                captured = datetime.strptime(stamp, "%Y:%m:%d %H:%M:%S")
                captured += timedelta(seconds=float("0." + (sub.strip() or "0")))

        jpeg = b""
        if best:
            f.seek(best[0])
            jpeg = f.read(best[1])
    return {"captured": captured, "orientation": orientation, "jpeg": jpeg}


def upright(im: Image.Image, orientation: int) -> Image.Image:
    return im.rotate(ROTATE[orientation], expand=True) if orientation in ROTATE else im


def cache_path(rel: str) -> Path:
    return CACHE / (rel.replace("/", "__") + ".jpg")


# ---------------------------------------------------------------- index

def load_index() -> dict:
    return json.loads(INDEX.read_text()) if INDEX.exists() else {"raws": {}}


def cmd_index(shoot: str) -> None:
    base = DRIVE / shoot
    if not base.is_dir():
        sys.exit(f"Not found: {base}. Is the Intenso drive plugged in?")
    CACHE.mkdir(parents=True, exist_ok=True)
    idx = load_index()
    raws = sorted(p for p in base.rglob("*.NEF") if not p.name.startswith("._"))
    new = failed = 0
    for n, p in enumerate(raws, 1):
        rel = str(p.relative_to(DRIVE))
        if rel in idx["raws"] and cache_path(rel).exists():
            continue
        try:
            info = read_nef(p)
            im = upright(Image.open(io.BytesIO(info["jpeg"])).convert("RGB"), info["orientation"])
            im.thumbnail((PREVIEW_EDGE, PREVIEW_EDGE), Image.LANCZOS)
            im.save(cache_path(rel), quality=88)
            idx["raws"][rel] = {
                "captured": info["captured"].isoformat(timespec="milliseconds") if info["captured"] else None,
                "orientation": info["orientation"],
                "bytes": p.stat().st_size,
            }
            new += 1
        except Exception as ex:                             # a truncated raw must not stop the run
            failed += 1
            print(f"  FAILED {rel}: {ex}")
        if n % 100 == 0:
            print(f"  {n}/{len(raws)}")
    idx["updated"] = datetime.now().isoformat(timespec="seconds")
    INDEX.write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n")
    print(f"{shoot}: {len(raws)} raws on the drive, {new} newly indexed, {failed} failed. "
          f"Index: {INDEX.name}, previews cached in {CACHE}")


# ---------------------------------------------------------------- matching

def edit_time(path: Path) -> datetime | None:
    ex = Image.open(path).getexif()
    sub = ex.get_ifd(0x8769)
    stamp = sub.get(0x9003) or ex.get(0x0132)
    if not stamp:
        return None
    t = datetime.strptime(str(stamp)[:19], "%Y:%m:%d %H:%M:%S")
    frac = str(sub.get(0x9291) or "0").strip() or "0"
    return t + timedelta(seconds=float("0." + frac))


def candidates(when: datetime, raws: dict, window: float = WINDOW_S) -> list:
    out = []
    for rel, r in raws.items():
        if not r.get("captured"):
            continue
        dt = abs((datetime.fromisoformat(r["captured"]) - when).total_seconds())
        if dt <= window + 1.0:                    # edits keep whole seconds, raws keep hundredths
            out.append((dt, rel))
    return [rel for _, rel in sorted(out)]


def classify(best: int, second: int) -> str:
    if best >= CONFIDENT and best >= 2 * max(second, 1):
        return "verified"
    if best >= CONFIDENT:
        return "ambiguous"                        # a burst: two frames nearly identical
    if best >= LIKELY:
        return "likely"
    return "unmatched"


def inliers(a, b) -> int:
    """ORB features, ratio test, homography. Survives the crop, the grade and the retouch."""
    import cv2
    import numpy as np
    orb = cv2.ORB_create(3000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return 0
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 8:
        return 0
    src = np.float32([ka[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kb[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    return int(mask.sum()) if mask is not None else 0


def gray(path: Path):
    import cv2
    import numpy as np
    im = ImageOps.exif_transpose(Image.open(path)).convert("L")
    im.thumbnail((PREVIEW_EDGE, PREVIEW_EDGE), Image.LANCZOS)
    return cv2.equalizeHist(np.array(im))


def match_edit(edit: Path, raws: dict) -> dict:
    when = edit_time(edit)
    if when is None:
        return {"status": "unmatched", "why": "the edit carries no capture time"}
    cands = [c for c in candidates(when, raws) if cache_path(c).exists()]
    if not cands:
        return {"status": "unmatched", "why": "no indexed raw within 3 s", "captured": when.isoformat()}
    e = gray(edit)
    scores = {c: inliers(e, gray(cache_path(c))) for c in cands}
    scored = sorted(((n, c) for c, n in scores.items()), reverse=True)
    best, second = scored[0], (scored[1] if len(scored) > 1 else (0, None))
    out = {"captured": when.isoformat(), "raw": best[1], "inliers": best[0],
           "second": second[1], "second_inliers": second[0],
           "candidates": len(cands), "status": classify(best[0], second[0]), "by": "image"}

    # A burst puts near-identical frames in one second and the image cannot tell them apart
    # (out-204: 634 against 646 inliers). The edit keeps the raw's time to the hundredth of a
    # second, so when exactly one candidate shares it, and the image agrees it is the same
    # scene, the clock decides.
    if when.microsecond:
        exact = [c for c in cands
                 if abs((datetime.fromisoformat(raws[c]["captured"]) - when).total_seconds()) < 0.011]
        if len(exact) == 1 and scores[exact[0]] >= LIKELY:
            out.update(raw=exact[0], inliers=scores[exact[0]], status="verified",
                       by="capture time to 1/100 s, image agrees")
    return out


# ---------------------------------------------------------------- matching without a clock

_POOL: dict = {}


def _pool_init(prefix: str) -> None:
    """One worker's copy of every raw preview of the shoot, with its ORB features."""
    import cv2
    cv2.setNumThreads(1)                          # 10 workers x OpenCV's own threads froze the Mac
    orb = cv2.ORB_create(3000)
    _POOL.clear()
    for rel in load_index()["raws"]:
        if rel.startswith(prefix) and cache_path(rel).exists():
            g = gray(cache_path(rel))
            k, d = orb.detectAndCompute(g, None)
            _POOL[rel] = (g, k, d)


def _homography(ke, de, kr, dr):
    """Inliers and the raw-to-edit homography."""
    import cv2
    import numpy as np
    if de is None or dr is None or len(ke) < 8 or len(kr) < 8:
        return 0, None
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(de, dr, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 8:
        return 0, None
    src = np.float32([ke[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kr[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(dst, src, cv2.RANSAC, 5.0)
    return (int(mask.sum()) if mask is not None else 0), H


def _edges(g):
    import cv2
    g = cv2.GaussianBlur(g, (0, 0), 1.5).astype("float32")
    return cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))


def edge_correlation(edit_gray, raw_gray, H) -> float:
    """Lay the raw onto the edit and correlate their edges. The grade changes brightness,
    not where the edges are, so the true frame scores near 1 and its burst neighbour,
    with a hand or the head moved, falls far below (0.96 against 0.24 on the 10-14 test)."""
    import cv2
    import numpy as np
    h, w = edit_gray.shape
    warped = cv2.warpPerspective(raw_gray, H, (w, h))
    mask = cv2.warpPerspective(np.ones_like(raw_gray), H, (w, h))
    mask = cv2.erode(mask, np.ones((9, 9), np.uint8)) > 0
    if mask.mean() < 0.3:                         # the raw covers too little of the edit
        return -1.0
    a, b = _edges(edit_gray)[mask], _edges(warped)[mask]
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))


def classify_by_image(contenders: list) -> tuple:
    """contenders: [(raw, inliers, gncc)], best inliers first. Returns (status, pick, why).
    The edge correlation picks among the contenders; inliers alone only say 'same scene'."""
    if not contenders or contenders[0][1] < LIKELY:
        return "unmatched", None, "no raw shares enough features"
    ranked = sorted(contenders, key=lambda c: -c[2])
    pick = ranked[0]
    runner = ranked[1][2] if len(ranked) > 1 else None
    clear = runner is None or pick[2] - runner >= GNCC_MARGIN
    if pick[2] >= GNCC_MIN and clear and pick[1] >= CONFIDENT:
        return "verified", pick, "image only: features + edge correlation"
    if pick[2] >= GNCC_MIN and clear:
        return "likely", pick, "image only: few features (dark frame?), edges agree"
    if pick[1] >= CONFIDENT and not clear:
        return "ambiguous", pick, "burst: two frames line up equally well"
    return "likely" if pick[1] >= LIKELY else "unmatched", pick, "image only: weak, look at it"


def match_by_image(edit_rel: str) -> tuple:
    """Worker: score one edit against every raw in the pool."""
    import cv2
    orb = cv2.ORB_create(3000)
    e = gray(DRIVE / edit_rel)
    ke, de = orb.detectAndCompute(e, None)
    scored = sorted(((*_homography(ke, de, k, d), rel) for rel, (_, k, d) in _POOL.items()),
                    key=lambda t: -t[0])
    best = scored[0][0] if scored else 0
    contenders = [(rel, n, round(edge_correlation(e, _POOL[rel][0], H), 3))
                  for n, H, rel in scored[:6] if H is not None and n >= max(LIKELY, NEAR_BEST * best)]
    status, pick, why = classify_by_image(contenders)
    out = {"status": status, "by": why, "raw": pick[0] if pick else None,
           "inliers": pick[1] if pick else best, "edge_corr": pick[2] if pick else None,
           "contenders": [{"raw": r, "inliers": n, "edge_corr": g} for r, n, g in contenders]}
    return edit_rel, out



def _frame_no(rel: str) -> int:
    digits = "".join(ch for ch in Path(rel).stem if ch.isdigit())
    return int(digits) if digits else -1


def _big_gray(im: Image.Image, edge: int = 2048):
    """Double resolution, local contrast lifted: dark frames give ORB something to hold."""
    import cv2
    import numpy as np
    im = im.convert("L")
    im.thumbnail((edge, edge), Image.LANCZOS)
    return cv2.createCLAHE(3.0, (8, 8)).apply(np.array(im))


def recheck_by_image(edit_rel: str, first: dict, raws: dict, spread: int = 5, seeds: list | None = None) -> dict:
    """Second look for an edit the first pass did not verify: its contenders plus the frames
    shot just before and after them, at double resolution from the raw's full embedded JPEG.
    On 2026-10-14 this settled all five indoor bursts and found -105 (DSC_4152), which the
    first pass had missed in the dark."""
    import cv2
    orb = cv2.ORB_create(10000, fastThreshold=5)
    shoot = Path(edit_rel).parts[0]
    seeds = [c["raw"] for c in first.get("contenders", [])] or list(seeds or [])
    by_no = {_frame_no(r): r for r in raws if r.startswith(shoot + "/")}
    near = {by_no[n] for s_ in seeds for n in range(_frame_no(s_) - spread, _frame_no(s_) + spread + 1) if n in by_no}
    if not seeds:                                 # nothing to start from: the whole shoot at low cost is pass one
        return first
    e = Image.open(DRIVE / edit_rel)
    e.draft("RGB", (2500, 2500))
    eg = _big_gray(ImageOps.exif_transpose(e))
    ke, de = orb.detectAndCompute(eg, None)
    scored = []
    for rel in sorted(near | set(seeds)):
        try:
            info = read_nef(DRIVE / rel)
        except Exception:
            continue
        rg = _big_gray(upright(Image.open(io.BytesIO(info["jpeg"])), info["orientation"]))
        kr, dr = orb.detectAndCompute(rg, None)
        n, H = _homography(ke, de, kr, dr)
        if H is not None and n >= LIKELY:
            scored.append((rel, n, round(edge_correlation(eg, rg, H), 3)))
    scored.sort(key=lambda c: -c[1])
    best = scored[0][1] if scored else 0
    contenders = [c for c in scored if c[1] >= NEAR_BEST * best][:6]
    status, pick, why = classify_by_image(contenders)
    out = {"status": status, "by": "recheck at 2x: " + why, "raw": pick[0] if pick else None,
           "inliers": pick[1] if pick else best, "edge_corr": pick[2] if pick else None,
           "contenders": [{"raw": r, "inliers": n, "edge_corr": g} for r, n, g in contenders],
           "first_pass": {k: first.get(k) for k in ("status", "raw", "inliers", "edge_corr")}}
    return out


def cmd_link(edits_dirs: list, out: Path | None, by_image: bool = False, workers: int = 6) -> None:
    raws = load_index()["raws"]
    if not raws:
        sys.exit("The raw index is empty. Run: shoot_catalogue.py index <shoot>")
    edits = []
    for d in edits_dirs:
        base = DRIVE / d
        if not base.is_dir():
            sys.exit(f"Not found: {base}")
        edits += sorted(p for p in base.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg") and not p.name.startswith("._"))
    shoot = Path(edits_dirs[0]).parts[0]
    report, tally = {}, {}

    def note(rel, r, n):
        report[rel] = r
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        if n % 25 == 0:
            print(f"  {n}/{len(edits)}", flush=True)

    if by_image:
        from concurrent.futures import ProcessPoolExecutor
        rels = [str(p.relative_to(DRIVE)) for p in edits]
        with ProcessPoolExecutor(workers, initializer=_pool_init, initargs=(shoot + "/",)) as ex:
            for n, (rel, r) in enumerate(ex.map(match_by_image, rels, chunksize=2), 1):
                note(rel, r, n)
    else:
        for n, p in enumerate(edits, 1):
            note(str(p.relative_to(DRIVE)), match_edit(p, raws), n)
    out = out or ROOT / "plans" / "control-panel" / f"shoot-links-{shoot.lower()}.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(edits)} edits: " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())) + f". Report: {out.name}")


def cmd_recheck(report_path: Path | None, shoot: str) -> None:
    """Second pass over a --by-image report: every edit that is not verified gets recheck_by_image."""
    path = report_path or ROOT / "plans" / "control-panel" / f"shoot-links-{shoot.lower()}.json"
    rep = json.loads(path.read_text())
    raws = load_index()["raws"]
    for rel, r in rep.items():
        if r["status"] == "verified":
            continue
        # an edit with no contender at all: her export numbers follow the shoot, so the raws
        # of the edits numbered next to it say where to look (-105 sits between -104 and -106)
        no = _frame_no(rel)
        neighbours = [v["raw"] for k, v in rep.items() if v.get("raw") and v["status"] == "verified"
                      and Path(k).parent.parent == Path(rel).parent.parent and 0 < abs(_frame_no(k) - no) <= 2]
        new = recheck_by_image(rel, r, raws, seeds=neighbours)
        print(f"  {Path(rel).name}: {r['status']} {Path(r['raw'] or '-').name} -> {new['status']} {Path(new['raw'] or '-').name}")
        rep[rel] = new
    path.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n")
    tally = {}
    for r in rep.values():
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print(f"{len(rep)} edits: " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())) + f". Report: {path.name}")


def cmd_verify(limit: int | None) -> None:
    """Re-derive the outdoor links that were checked by hand and by ORB on 2026-09-14."""
    cat = json.loads(CATALOGUE.read_text())
    raws = load_index()["raws"]
    known = [p for p in cat["photos"] if p.get("raw_match") == "verified" and p.get("raw")]
    if limit:
        known = known[:: max(1, len(known) // limit)][:limit]
    same = differ = skipped = 0
    for p in known:
        edit = DRIVE / p["edit"]
        if not edit.exists() or p["raw"] not in raws:
            skipped += 1
            continue
        r = match_edit(edit, raws)
        if r.get("raw") == p["raw"]:
            same += 1
        else:
            differ += 1
            print(f"  DIFFERS {p['id']}: catalogue {p['raw']}  tool {r.get('raw')} ({r.get('inliers')} inliers, {r['status']})")
    print(f"verify: {same} of {same + differ} known links reproduced, {differ} differ, {skipped} skipped")

# ---------------------------------------------------------------- write the links back

def cmd_apply() -> None:
    """Re-match every catalogued edit and write the result into the catalogue. Git keeps
    the previous state of the file."""
    cat = json.loads(CATALOGUE.read_text())
    raws = load_index()["raws"]
    moved, tally = [], {}
    for n, p in enumerate(cat["photos"], 1):
        edit = DRIVE / p["edit"]
        if not edit.exists():
            continue
        r = match_edit(edit, raws)
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        if r["status"] in ("verified", "likely") and r.get("raw"):
            old = p.get("raw")
            if old != r["raw"]:
                moved.append((p["id"], old, r["raw"]))
            p["raw"] = r["raw"]
            p["raw_match"] = r["status"]
            p["raw_check"] = {"method": "capture time within 3 s + ORB homography inliers; bursts "
                                        "settled by capture time to 1/100 s",
                              "decided_by": r["by"], "inliers": r["inliers"],
                              "second": r["second"], "second_inliers": r["second_inliers"],
                              "checked": datetime.now().date().isoformat()}
            p["raw_tagged_blue"] = True
        if n % 50 == 0:
            print(f"  {n}/{len(cat['photos'])}")
    cat["updated"] = datetime.now().date().isoformat()
    CATALOGUE.write_text(json.dumps(cat, indent=1, ensure_ascii=False) + "\n")
    print("links: " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())) + f"; {len(moved)} now point to a different raw")
    for m in moved:
        print(f"  {m[0]}: {m[1]}  ->  {m[2]}")


# ---------------------------------------------------------------- already posted?

def features(path: Path):
    import cv2
    orb = cv2.ORB_create(3000)
    return orb.detectAndCompute(gray(path), None)


def inliers_kd(ka, da, kb, db) -> int:
    import cv2
    import numpy as np
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return 0
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 8:
        return 0
    src = np.float32([ka[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kb[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    return int(mask.sum()) if mask is not None else 0


def find_used(posted: list, cat: dict) -> list:
    """For every posted image, the catalogued edit it was made from, if any. A post is a crop,
    a resize and a recompression of the edit, sometimes with type on it; ORB survives that."""
    edits = [(p, features(DRIVE / p["edit"])) for p in cat["photos"] if (DRIVE / p["edit"]).exists()]
    hits = []
    for img in posted:
        kp, de = features(img)
        scored = sorted(((inliers_kd(kp, de, k, d), p["id"]) for p, (k, d) in edits), reverse=True)
        best, second = scored[0], scored[1]
        if best[0] >= CONFIDENT and best[0] >= 2 * max(second[0], 1):
            hits.append({"posted": str(img), "edit": best[1], "inliers": best[0], "second": second[0]})
    return hits


def cmd_used(folder: Path, write: bool) -> None:
    if not folder.is_dir():
        sys.exit(f"Not found: {folder}")
    posted = sorted(p for p in folder.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    cat = json.loads(CATALOGUE.read_text())
    hits = find_used(posted, cat)
    print(f"{len(posted)} posted images checked against {len(cat['photos'])} edits: {len(hits)} came from the shoot")
    for h in hits:
        print(f"  {h['edit']}  <-  {Path(h['posted']).name}  ({h['inliers']} inliers, next best {h['second']})")
    if write and hits:
        by = {p["id"]: p for p in cat["photos"]}
        for h in hits:
            used = by[h["edit"]].setdefault("used_in", [])
            if Path(h["posted"]).name not in used:
                used.append(Path(h["posted"]).name)
        CATALOGUE.write_text(json.dumps(cat, indent=1, ensure_ascii=False) + "\n")
        print("written into the catalogue as used_in")
    elif hits:
        print("plan only. Run again with --write to record them.")


# ---------------------------------------------------------------- Finder tags

TAG_ATTR = "com.apple.metadata:_kMDItemUserTags"
BLUE = "Blue\n4"


def read_tags(path: Path) -> list:
    import plistlib
    import subprocess
    r = subprocess.run(["xattr", "-px", TAG_ATTR, str(path)], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return []
    return list(plistlib.loads(bytes.fromhex("".join(r.stdout.split()))))


def write_tags(path: Path, tags: list) -> None:
    import plistlib
    import subprocess
    if not tags:
        subprocess.run(["xattr", "-d", TAG_ATTR, str(path)], capture_output=True)
        return
    data = plistlib.dumps(tags, fmt=plistlib.FMT_BINARY).hex()
    subprocess.run(["xattr", "-wx", TAG_ATTR, data, str(path)], check=True)


def cmd_tags(write: bool) -> None:
    """Blue on a raw means an edit was made from it. Only the Blue entry is ever added or
    removed; any other colour Amir has put on a file stays."""
    cat = json.loads(CATALOGUE.read_text())
    raws = load_index()["raws"]
    want = set()
    for p in cat["photos"]:
        r = p.get("raw")
        want.update(r if isinstance(r, list) else [r] if r else [])
    shoots = {p["edit"].split("/")[0] for p in cat["photos"]}          # never touch a shoot with no edits
    add, remove = [], []
    for rel in sorted(raws):
        if rel.split("/")[0] not in shoots:
            continue
        has = any(t.split("\n")[0] == "Blue" for t in read_tags(DRIVE / rel))
        if rel in want and not has:
            add.append(rel)
        elif rel not in want and has:
            remove.append(rel)
    print(f"edited raws per the catalogue: {len(want)}.  Blue to ADD: {len(add)}, Blue to REMOVE: {len(remove)}")
    for rel in add:
        print("  + " + rel)
    for rel in remove:
        print("  - " + rel)
    if not write:
        print("plan only. Run again with --write to change the tags.")
        return
    for rel in add:
        write_tags(DRIVE / rel, read_tags(DRIVE / rel) + [BLUE])
    for rel in remove:
        write_tags(DRIVE / rel, [t for t in read_tags(DRIVE / rel) if t.split("\n")[0] != "Blue"])
    bad = [rel for rel in add if not any(t.startswith("Blue") for t in read_tags(DRIVE / rel))]
    bad += [rel for rel in remove if any(t.startswith("Blue") for t in read_tags(DRIVE / rel))]
    print(f"written and read back: {len(add) + len(remove) - len(bad)} ok, {len(bad)} failed")



# ---------------------------------------------------------------- the raws she did not edit

MISSED = ROOT / "generated_images" / "shoot" / "missed-picks"


def cmd_missed(shoot: str, cols: int = 6, edge: int = 300) -> None:
    """One contact sheet per folder of the raws no catalogued edit came from, so Amir can look
    for frames she skipped. Reads the cached 1024 px raw previews; writes only the sheets."""
    from PIL import ImageDraw, ImageFont
    cat = json.loads(CATALOGUE.read_text())
    used = set()
    for p in cat["photos"]:
        r = p.get("raw")
        used.update(r if isinstance(r, list) else [r] if r else [])
    raws = load_index()["raws"]
    rest = sorted((rel for rel in raws if rel.startswith(shoot + "/") and rel not in used),
                  key=lambda rel: (rel.split("/")[1], raws[rel].get("captured") or rel))
    if not rest:
        sys.exit(f"every indexed {shoot} raw is linked to an edit")
    out = MISSED / shoot.lower()
    out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    by_folder = {}
    for rel in rest:
        by_folder.setdefault(rel.split("/")[1], []).append(rel)
    total = 0
    for folder, rels in by_folder.items():
        tiles = []
        for rel in rels:
            f = cache_path(rel)
            if not f.is_file():
                continue
            im = Image.open(f).convert("RGB")
            im.thumbnail((edge, edge))
            t = Image.new("RGB", (edge, edge + 26), (24, 24, 24))
            t.paste(im, ((edge - im.width) // 2, 0))
            cap = (raws[rel].get("captured") or "")[11:19]
            ImageDraw.Draw(t).text((4, edge + 4), f"{Path(rel).stem}  {cap}", fill=(220, 220, 220), font=font)
            tiles.append(t)
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (edge + 8) + 8, rows * (edge + 34) + 44), (24, 24, 24))
        ImageDraw.Draw(sheet).text((8, 10), f"{shoot} / {folder}: {len(tiles)} raws without an edit", fill=(240, 240, 240), font=font)
        for i, t in enumerate(tiles):
            sheet.paste(t, (8 + (i % cols) * (edge + 8), 44 + (i // cols) * (edge + 34)))
        name = folder.replace(" ", "_") + ".jpg"
        sheet.save(out / name, quality=86)
        total += len(tiles)
        print(f"  {name}: {len(tiles)}")
    print(f"{shoot}: {total} raws without an edit on {len(by_folder)} sheets in {out}")


def cmd_status() -> None:
    raws = load_index()["raws"]
    by = {}
    for rel in raws:
        by[rel.split("/")[0]] = by.get(rel.split("/")[0], 0) + 1
    print("raws indexed: " + (", ".join(f"{k} {v}" for k, v in sorted(by.items())) or "none"))
    if CATALOGUE.exists():
        cat = json.loads(CATALOGUE.read_text())
        print(f"edits catalogued: {len(cat['photos'])} (scope: {cat.get('scope', '')[:70]})")
    print(f"drive mounted: {DRIVE.is_dir()}")


def main() -> None:
    ap = ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index").add_argument("shoot", help="a top folder on the drive: INDOOR or Outdoor")
    lk = sub.add_parser("link")
    lk.add_argument("edits_dir", nargs="+", help="folder(s) of edited JPGs, relative to the drive's shoot root")
    lk.add_argument("--out", type=Path)
    lk.add_argument("--by-image", action="store_true", help="edits without a capture time: compare with every raw")
    lk.add_argument("--workers", type=int, default=6)
    rc = sub.add_parser("recheck", help="second look at 2x for the edits a --by-image link did not verify")
    rc.add_argument("shoot", help="INDOOR or Outdoor: reads shoot-links-<shoot>.json")
    rc.add_argument("--report", type=Path)
    sub.add_parser("verify").add_argument("--limit", type=int, help="check an even sample of N")
    sub.add_parser("apply")
    sub.add_parser("tags").add_argument("--write", action="store_true", help="change the tags; default is plan only")
    us = sub.add_parser("used")
    us.add_argument("folder", type=Path, help="a folder of posted images, e.g. an IG export's media/posts")
    us.add_argument("--write", action="store_true")
    ms = sub.add_parser("missed", help="contact sheets of the raws she did not edit")
    ms.add_argument("shoot", help="INDOOR or Outdoor")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "index":
        cmd_index(a.shoot)
    elif a.cmd == "link":
        cmd_link(a.edits_dir, a.out, a.by_image, a.workers)
    elif a.cmd == "recheck":
        cmd_recheck(a.report, a.shoot)
    elif a.cmd == "verify":
        cmd_verify(a.limit)
    elif a.cmd == "apply":
        cmd_apply()
    elif a.cmd == "tags":
        cmd_tags(a.write)
    elif a.cmd == "used":
        cmd_used(a.folder, a.write)
    elif a.cmd == "missed":
        cmd_missed(a.shoot)
    else:
        cmd_status()


if __name__ == "__main__":
    main()
