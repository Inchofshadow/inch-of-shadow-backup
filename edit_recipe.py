#!/usr/bin/env python3
"""Our own edit recipe: learn the photographer's grade from her own edits (Look-09).

    edit_recipe.py learn                 measure all raw-and-edit pairs, fit one recipe per light family
    edit_recipe.py test                  held-out pairs: his edit next to the recipe's output
    edit_recipe.py grade <raw or jpg> --family dusk [--brightness darker|auto|brighter|all]
                         [--warmth -2..2] [--colour 0.8..1.8]
    edit_recipe.py families              what the families are and how many pairs each has

What it learns: for every edit in the shoot catalogue we know the exact raw it came from
(Look-08). The raw's camera preview is lined up with the edit, and the colour of the same
spot before and after is recorded, a few thousand spots a photo. Per light family those
samples become a 3D colour table (a LUT, 17 steps a channel), written as a standard .cube
file that ffmpeg, HyperFrames and any grading tool can read.

It works like a Lightroom preset: THE LOOK IS LEARNED, THE BRIGHTNESS IS A CHOICE. Found the
hard way on 2026-09-21. A colour table alone failed, because she sets the brightness of every
photo by hand, from x0.35 to x38 against the camera preview. Pulling every frame to its
family's usual brightness failed too (dusk got worse): some frames she leaves dark on purpose,
it is taste, frame by frame. But GIVEN the brightness she chose, one table per family lands on
the floor, the best any colour recipe could do for that photo (dusk 5.8 against 5.0). So:
(1) LEVEL the frame: `auto` predicts the brightness from the frame itself (a dark frame stays
fairly dark, which is what she does; fixed family settings turned a moody dusk frame garish),
with `darker` and `brighter` one step either side; (2) apply the family's LOOK.
Brightness stays Amir's call: even `auto` only recovers part of it, it is taste.

(3) the FINISH. Colour alone looked flat next to her edits (Amir, 2026-09-21). Measured on the
pairs, her files have more fine detail, texture and local contrast, darker edges, and 2 to 4
times the noise of the camera preview. Those five are matched per family after the look.
CORRECTION the same day, from her own Lightroom settings, which every edit carries in its XMP
(plans/control-panel/shoot-lightroom-settings.json): the noise and the dark edges are mostly
NOT effects she added. She added grain on 7% of photos and a vignette on 2%. The rest is the
difference between two developers of the same raw: the camera's preview applies its own noise
reduction and vignette control, Lightroom's conversion with her settings applies no luminance
noise reduction (98% of photos) and no lens correction (all 204), and she sharpens at 40. So
the finish step is right about WHAT to match and was wrong about WHY. Sharpening, Clarity
(median +8, on 69%) and Texture (on 44%) are truly hers.

THE HONEST CEILING (four experiments, 2026-09-21). She grades every photo by hand. A recipe
shared by a light family keeps only 48% (flash) to 84% (day) of her colour strength, because
averaging different grades gives mud, like mixing paints. A finer table did not help (48 to
50%). Grouping photos by how she graded them instead of by light did not help either (73 to
84% with 10 groups), so she is not working from a few presets. Even GIVEN her white balance
and saturation per photo, the shared look stays short of a recipe fitted to that one photo
(colour error about 4 against 2). So no recipe reproduces a specific edit of hers. What it
gives is her average look and her finish, plus three dials set by eye: `--brightness`,
`--warmth`, `--colour`. The default `--colour` already makes up for the averaging loss.

What it does NOT learn: retouching, local dodging, crops.

The starting point on both sides is the camera's own embedded preview JPEG (full size,
8256x5504 on the D850), not a raw decode. The recipe is learned from that and applied to
that, so the two ends match. Local, free, no AI.
"""
from __future__ import annotations

import io
import json
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import shoot_catalogue as sc  # noqa: E402

OUT = ROOT / "docs" / "brand" / "recipes"
SAMPLES = Path.home() / ".cache" / "inch-of-shadow" / "recipe-samples.npz"
N = 17                                   # LUT steps per channel
PER_PAIR = 3000                          # colour samples taken from each pair
FAMILIES = ("bw", "flash", "bluehour", "dusk", "day")
LABEL = {"bw": "black and white", "flash": "direct flash, colour", "bluehour": "blue hour",
         "dusk": "soft dusk and late light", "day": "daylight, overcast, golden hour"}


def family_of(light: str) -> str:
    t = light.lower()
    if "black and white" in t or "sepia" in t:
        return "bw"
    if "flash" in t:
        return "flash"
    if "blue hour" in t:
        return "bluehour"
    if "dusk" in t or "late" in t:
        return "dusk"
    return "day"


# ---------------------------------------------------------------- pairs to samples

def aligned_pair(edit_path: Path, raw_rel: str):
    """The raw preview warped onto the edit, both small and slightly blurred so a pixel or
    two of misalignment and the retouching do not matter. Returns (raw, edit, mask)."""
    import cv2
    e = ImageOps.exif_transpose(Image.open(edit_path)).convert("RGB")
    e.thumbnail((sc.PREVIEW_EDGE, sc.PREVIEW_EDGE), Image.LANCZOS)
    r = Image.open(sc.cache_path(raw_rel)).convert("RGB")
    ea, ra = np.array(e), np.array(r)
    orb = cv2.ORB_create(4000)
    ke, de = orb.detectAndCompute(cv2.equalizeHist(cv2.cvtColor(ea, cv2.COLOR_RGB2GRAY)), None)
    kr, dr = orb.detectAndCompute(cv2.equalizeHist(cv2.cvtColor(ra, cv2.COLOR_RGB2GRAY)), None)
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(dr, de, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 12:
        return None
    src = np.float32([kr[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([ke[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
    if H is None or mask.sum() < 12:
        return None
    h, w = ea.shape[:2]
    warped = cv2.warpPerspective(ra, H, (w, h))
    valid = cv2.warpPerspective(np.full(ra.shape[:2], 255, np.uint8), H, (w, h)) > 250
    k = (9, 9)
    return cv2.GaussianBlur(warped, k, 0), cv2.GaussianBlur(ea, k, 0), valid


def cmd_learn() -> None:
    cat = json.loads(sc.CATALOGUE.read_text())
    rng = np.random.default_rng(9)
    data = {f: ([], [], []) for f in FAMILIES}            # raw rgb, edit rgb, photo index
    skipped = 0
    for i, p in enumerate(cat["photos"]):
        fam = family_of(p["tags"].get("light", ""))
        pair = aligned_pair(sc.DRIVE / p["edit"], p["raw"])
        if pair is None:
            skipped += 1
            continue
        raw, edit, valid = pair
        ys, xs = np.nonzero(valid)
        pick = rng.choice(len(ys), size=min(PER_PAIR, len(ys)), replace=False)
        data[fam][0].append(raw[ys[pick], xs[pick]])
        data[fam][1].append(edit[ys[pick], xs[pick]])
        data[fam][2].append(np.full(len(pick), i, np.int32))
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(cat['photos'])}")
    SAMPLES.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(SAMPLES, **{f"{f}_{k}": np.concatenate(v[j]) if v[j] else np.zeros((0,))
                                    for f, v in data.items() for j, k in enumerate(("raw", "edit", "idx"))})
    print(f"sampled {len(cat['photos']) - skipped} pairs, {skipped} skipped")
    fit_all()


# ---------------------------------------------------------------- step 1: level the frame

PCTS = (1, 5, 25, 50, 75, 95, 99)
LUMA = np.array([0.2126, 0.7152, 0.0722])
MAX_GAIN = 16.0            # an 8-bit preview lifted further than this is only noise


def luma(rgb: np.ndarray) -> np.ndarray:
    return rgb.astype(np.float64) @ LUMA


def level_curve(src_lum: np.ndarray, target: np.ndarray) -> tuple:
    """A monotone brightness curve that moves this frame's percentiles onto the family's."""
    s = np.percentile(src_lum, PCTS).astype(np.float64)
    s = np.maximum.accumulate(s + np.arange(len(s)) * 1e-3)      # strictly rising, even on a black frame
    xs = np.concatenate([[0.0], s, [255.0 + 1e-3 * len(s)]])
    ys = np.concatenate([[0.0], target, [255.0]])
    return xs, np.maximum.accumulate(ys)


def level(rgb: np.ndarray, curve: tuple) -> np.ndarray:
    """Brightness follows the curve, colour is kept: each pixel is scaled by new/old luma."""
    xs, ys = curve
    lum = luma(rgb)
    new = np.interp(lum, xs, ys)
    gain = np.clip(new / np.maximum(lum, 1.0), 0.0, MAX_GAIN)
    # lifting a dark 8-bit frame multiplies its colour noise too; ease the colour off as the lift grows
    keep = 1.0 / (1.0 + 0.18 * np.maximum(gain - 1.0, 0.0))
    grey = lum[..., None]
    out = (grey + (rgb.astype(np.float64) - grey) * keep[..., None]) * gain[..., None]
    dark = lum < 1.0                                             # no colour to scale there
    out[dark] = new[dark][..., None]
    return np.clip(out, 0, 255)


BRIGHTNESS = {"darker": 1.3, "auto": 1.0, "brighter": 0.77}      # a gamma on the predicted spread
RIDGE = 50.0                                                     # few photos, 7 correlated inputs


def fit_brightness(raw: np.ndarray, edit: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """How bright he makes a frame, predicted from how bright it was shot. Linear, per family,
    from the frame's 7 brightness percentiles to the edit's 7."""
    photos = np.unique(idx)
    X = np.array([np.percentile(luma(raw[idx == ph]), PCTS) for ph in photos])
    Y = np.array([np.percentile(luma(edit[idx == ph]), PCTS) for ph in photos])
    A = np.column_stack([np.ones(len(X)), X])
    return np.linalg.solve(A.T @ A + RIDGE * np.eye(A.shape[1]), A.T @ Y)


def predict_target(src_lum: np.ndarray, W: np.ndarray, step: str = "auto") -> np.ndarray:
    x = np.concatenate([[1.0], np.percentile(src_lum, PCTS)])
    t = np.maximum.accumulate(np.clip(x @ W, 0, 255))
    return 255.0 * (t / 255.0) ** BRIGHTNESS[step]


def level_samples(raw: np.ndarray, idx: np.ndarray, target) -> np.ndarray:
    """target: one spread for every photo, or None = each photo gets the brightness HE gave it
    (needs the edit, so only for learning and for measuring the floor of the look)."""
    out = np.zeros(raw.shape, np.float64)
    for ph in np.unique(idx):
        m = idx == ph
        t = target if target is not None else np.percentile(luma(_EDIT_FOR_ORACLE[m]), PCTS)
        out[m] = level(raw[m], level_curve(luma(raw[m]), t))
    return out


_EDIT_FOR_ORACLE = None


# ---------------------------------------------------------------- step 2: the look, samples to a LUT

def fit_lut(raw: np.ndarray, edit: np.ndarray) -> np.ndarray:
    """Each sample votes for the 8 table nodes around its raw colour, weighted by how close
    it is. Nodes no sample came near fall back to a smooth global fit, so colours the shoot
    never contained still grade sensibly instead of jumping."""
    x = raw.astype(np.float64) / 255 * (N - 1)
    y = edit.astype(np.float64) / 255
    i0 = np.clip(np.floor(x).astype(int), 0, N - 2)
    f = x - i0
    acc = np.zeros((N, N, N, 3))
    wsum = np.zeros((N, N, N))
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                w = (np.where(dr, f[:, 0], 1 - f[:, 0]) * np.where(dg, f[:, 1], 1 - f[:, 1])
                     * np.where(db, f[:, 2], 1 - f[:, 2]))
                idx = (i0[:, 0] + dr, i0[:, 1] + dg, i0[:, 2] + db)
                np.add.at(wsum, idx, w)
                np.add.at(acc, idx, w[:, None] * y)

    # the smooth fallback: a per-channel cubic in all three raw channels
    rn = raw.astype(np.float64) / 255
    A = np.column_stack([np.ones(len(rn)), rn, rn ** 2, rn ** 3, rn[:, [0]] * rn[:, [1]],
                         rn[:, [1]] * rn[:, [2]], rn[:, [0]] * rn[:, [2]]])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    g = np.linspace(0, 1, N)
    R, G, B = np.meshgrid(g, g, g, indexing="ij")
    P = np.column_stack([v.ravel() for v in (R, G, B)])
    Ag = np.column_stack([np.ones(len(P)), P, P ** 2, P ** 3, P[:, [0]] * P[:, [1]],
                          P[:, [1]] * P[:, [2]], P[:, [0]] * P[:, [2]]])
    smooth = np.clip(Ag @ coef, 0, 1).reshape(N, N, N, 3)

    trust = np.clip(wsum / 40.0, 0, 1)[..., None]       # 40 votes = fully trusted
    lut = np.where(wsum[..., None] > 0, acc / np.maximum(wsum, 1e-9)[..., None], smooth)
    lut = trust * lut + (1 - trust) * smooth
    from scipy.ndimage import gaussian_filter            # soften node-to-node jitter
    for c in range(3):
        lut[..., c] = gaussian_filter(lut[..., c], 0.6)
    return np.clip(lut, 0, 1)


def apply_lut(img: np.ndarray, lut: np.ndarray) -> np.ndarray:
    if img.ndim == 3 and img.shape[0] > 1024:                 # a full frame: work in strips
        return np.concatenate([apply_lut(img[y:y + 512], lut) for y in range(0, img.shape[0], 512)])
    x = np.asarray(img, np.float32) / 255 * (N - 1)
    i0 = np.clip(np.floor(x).astype(int), 0, N - 2)
    f = x - i0
    out = np.zeros(x.shape, np.float32)
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                w = (np.where(dr, f[..., 0], 1 - f[..., 0]) * np.where(dg, f[..., 1], 1 - f[..., 1])
                     * np.where(db, f[..., 2], 1 - f[..., 2]))
                out += w[..., None] * lut[i0[..., 0] + dr, i0[..., 1] + dg, i0[..., 2] + db]
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)


def write_cube(lut: np.ndarray, path: Path, title: str) -> None:
    lines = [f'TITLE "{title}"', f"LUT_3D_SIZE {N}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    for b in range(N):                                   # .cube: red changes fastest
        for g in range(N):
            for r in range(N):
                lines.append("%.6f %.6f %.6f" % tuple(lut[r, g, b]))
    path.write_text("\n".join(lines) + "\n")


def split(idx: np.ndarray):
    """Hold out every fifth PHOTO (not every fifth pixel), so the test is on unseen pictures."""
    photos = np.unique(idx)
    held = set(photos[::5].tolist())
    test = np.isin(idx, list(held))
    return ~test, test, sorted(held)


def fit_all() -> None:
    global _EDIT_FOR_ORACLE
    z = np.load(SAMPLES)
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    print(f"\n{'family':<10}{'pairs':>6}{'untouched':>11}{'auto':>7}{'best of 3':>11}{'his own':>9}{'floor':>7}"
          "   mean colour error on held-out photos (0-255)")
    for fam in FAMILIES:
        raw, edit, idx = z[f"{fam}_raw"], z[f"{fam}_edit"], z[f"{fam}_idx"]
        if len(raw) == 0:
            continue
        _EDIT_FOR_ORACLE = edit
        train, test, held = split(idx)
        lut = fit_lut(level_samples(raw, idx, None)[train], edit[train])     # the look, brightness as he set it
        W = fit_brightness(raw[train], edit[train], idx[train])

        auto, best3, own, floor = [], [], [], []
        for ph in held:
            m = idx == ph
            lum = luma(raw[m])

            def err(target):
                lev = level(raw[m], level_curve(lum, target))
                return np.abs(apply_lut(lev[None], lut)[0].astype(float) - edit[m]).mean()

            steps = {k: err(predict_target(lum, W, k)) for k in BRIGHTNESS}
            auto.append(steps["auto"])
            best3.append(min(steps.values()))                                # he would pick the closest
            own.append(err(np.percentile(luma(edit[m]), PCTS)))
            h = np.arange(m.sum()) % 2 == 0
            o = fit_lut(raw[m][h], edit[m][h])
            floor.append(np.abs(apply_lut(raw[m][~h][None], o)[0].astype(float) - edit[m][~h]).mean())
        before = np.abs(raw[test].astype(float) - edit[test]).mean()

        full = fit_lut(level_samples(raw, idx, None), edit)                  # shipped: every pair
        write_cube(full, OUT / f"ios-{fam}.cube", f"Inch of Shadow, {LABEL[fam]} (set brightness first)")
        np.save(OUT / f"ios-{fam}.npy", full.astype(np.float32))
        report[fam] = {"label": LABEL[fam], "pairs": int(len(np.unique(idx))), "held_out_photos": held,
                       "brightness_model": fit_brightness(raw, edit, idx).round(5).tolist(),
                       "error": {"untouched": round(float(before), 1), "auto": round(float(np.mean(auto)), 1),
                                 "best_of_3": round(float(np.mean(best3)), 1),
                                 "his_own_brightness": round(float(np.mean(own)), 1),
                                 "floor": round(float(np.mean(floor)), 1)}}
        print(f"{fam:<10}{len(np.unique(idx)):>6}{before:>11.1f}{np.mean(auto):>7.1f}{np.mean(best3):>11.1f}"
              f"{np.mean(own):>9.1f}{np.mean(floor):>7.1f}")
    (OUT / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"\nrecipes in {OUT.relative_to(ROOT)}/ : brightness model in report.json, look as .cube and .npy")


# ---------------------------------------------------------------- the dials

# How much of her colour strength the shared look keeps, measured on held-out photos. The
# default colour dial divides it back out (capped: flash at 48% would need x2, which is a guess).
COLOUR_KEPT = {"bw": 1.0, "flash": 0.48, "bluehour": 0.79, "dusk": 0.83, "day": 0.84}
WARMTH_STEP = 0.07           # one step of --warmth, a gentle red-up blue-down


def default_colour(fam: str) -> float:
    return round(min(1.0 / COLOUR_KEPT[fam], 1.5), 2)


def dial(rgb: np.ndarray, warmth: float, colour: float) -> np.ndarray:
    x = rgb.astype(np.float32)
    if warmth:
        t = float(np.exp(WARMTH_STEP * warmth))
        x = x * np.array([t, 1.0, 1.0 / t], np.float32)
    if colour != 1.0:
        lum = (x @ LUMA.astype(np.float32))[..., None]
        x = lum + (x - lum) * colour
    return np.clip(x, 0, 255)


# ---------------------------------------------------------------- step 3: her finish

# Measured 2026-09-21 on 7 pairs a family at 2400 px, the raw tone-matched to her edit first so
# only the finish remained. detail/texture/local = how much stronger than the raw, vignette =
# edge brightness against the centre, grain = noise in the flattest tenth of the frame.
EFFECTS = {
    "bw":       {"detail": 1.34, "texture": 1.20, "local": 1.10, "vignette": 0.85, "grain": 0.91, "grain_raw": 0.45},
    "flash":    {"detail": 1.12, "texture": 1.16, "local": 1.10, "vignette": 0.97, "grain": 0.87, "grain_raw": 0.20},
    "bluehour": {"detail": 1.18, "texture": 1.18, "local": 1.13, "vignette": 0.92, "grain": 1.24, "grain_raw": 0.66},
    "dusk":     {"detail": 1.14, "texture": 1.09, "local": 1.06, "vignette": 0.96, "grain": 1.48, "grain_raw": 0.61},
    "day":      {"detail": 1.15, "texture": 1.15, "local": 1.10, "vignette": 0.96, "grain": 1.14, "grain_raw": 0.26},
}
MEASURED_AT = 2400.0       # the long edge the numbers above were measured at


def finish(rgb: np.ndarray, fam: str, seed: int = 0) -> np.ndarray:
    """Sharpening, texture, local contrast, vignette, grain, in that order, on brightness only
    so the look's colours are not pushed around."""
    import cv2
    fx = EFFECTS[fam]
    img = rgb.astype(np.float32)
    k = max(img.shape[:2]) / MEASURED_AT                      # the same effect at any output size
    lum = img @ LUMA.astype(np.float32)
    g1 = cv2.GaussianBlur(lum, (0, 0), 1.2 * k)
    g4 = cv2.GaussianBlur(lum, (0, 0), 4 * k)
    g16 = cv2.GaussianBlur(lum, (0, 0), 16 * k)
    # part of her "fine detail" is the grain itself, so the sharpening takes 70% of the measured gain
    add = (0.7 * (fx["detail"] - 1)) * (lum - g1) + (fx["texture"] - 1) * (g1 - g4) + (fx["local"] - 1) * (g4 - g16)
    img += add[..., None]

    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rad = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
    img *= (1 - (1 - fx["vignette"]) * 1.43 * rad ** 2.2)[..., None]

    need = np.sqrt(max(fx["grain"] ** 2 - fx["grain_raw"] ** 2, 0.0)) * k      # per-pixel, at this size
    noise = np.random.default_rng(seed).normal(0, 1, (h, w)).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0, 0), 0.7)
    img += (noise / noise.std() * min(need, 5.0))[..., None]
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- using it

def load_image(path: Path) -> Image.Image:
    if path.suffix.lower() == ".nef":
        info = sc.read_nef(path)
        return sc.upright(Image.open(io.BytesIO(info["jpeg"])).convert("RGB"), info["orientation"])
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def grade(im: Image.Image, fam: str, brightness: str = "auto", effects: bool = True,
          warmth: float = 0.0, colour: float | None = None) -> Image.Image:
    rep = json.loads((OUT / "report.json").read_text())[fam]
    lut = np.load(OUT / f"ios-{fam}.npy").astype(np.float64)
    a = np.array(im)
    small = luma(np.array(im.resize((max(1, im.width // 8), max(1, im.height // 8))))).ravel()
    target = predict_target(small, np.array(rep["brightness_model"]), brightness)
    curve = level_curve(small, target)
    if a.shape[0] > 1024:                                     # a full frame: level in strips
        lev = np.concatenate([level(a[y:y + 512], curve) for y in range(0, a.shape[0], 512)])
    else:
        lev = level(a, curve)
    out = apply_lut(lev, lut)
    if fam != "bw":
        out = dial(out, warmth, default_colour(fam) if colour is None else colour)
    return Image.fromarray(finish(out, fam) if effects else np.clip(out + 0.5, 0, 255).astype(np.uint8))


def cmd_grade(path: Path, fam: str, brightness: str, out: Path | None, warmth: float, colour) -> None:
    src = load_image(path)
    for b in (BRIGHTNESS if brightness == "all" else [brightness]):
        dest = out or ROOT / "generated_images" / "graded" / f"{path.stem}_{fam}_{b}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        grade(src, fam, b, warmth=warmth, colour=colour).save(dest, quality=94)
        print(f"{path.name}: '{LABEL[fam]}', {b} -> {dest}")


def cmd_test(out: Path) -> None:
    """One held-out photo per family: untouched preview, the recipe, his real edit."""
    cat = json.loads(sc.CATALOGUE.read_text())
    rep = json.loads((OUT / "report.json").read_text())
    rows = []
    for fam in FAMILIES:
        if fam not in rep:
            continue
        p = cat["photos"][rep[fam]["held_out_photos"][len(rep[fam]["held_out_photos"]) // 2]]
        pair = aligned_pair(sc.DRIVE / p["edit"], p["raw"])
        if pair is None:
            continue
        e = ImageOps.exif_transpose(Image.open(sc.DRIVE / p["edit"])).convert("RGB")
        e.thumbnail((sc.PREVIEW_EDGE, sc.PREVIEW_EDGE), Image.LANCZOS)
        import cv2
        r = np.array(Image.open(sc.cache_path(p["raw"])).convert("RGB"))
        # warp the UNBLURRED preview onto the edit's crop so the three tiles show the same frame
        ea = np.array(e)
        orb = cv2.ORB_create(4000)
        ke, de = orb.detectAndCompute(cv2.cvtColor(ea, cv2.COLOR_RGB2GRAY), None)
        kr, dr = orb.detectAndCompute(cv2.cvtColor(r, cv2.COLOR_RGB2GRAY), None)
        pr = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(dr, de, k=2)
        good = [m for m, n in (q for q in pr if len(q) == 2) if m.distance < 0.75 * n.distance]
        H, _ = cv2.findHomography(np.float32([kr[m.queryIdx].pt for m in good]).reshape(-1, 1, 2),
                                  np.float32([ke[m.trainIdx].pt for m in good]).reshape(-1, 1, 2), cv2.RANSAC, 4.0)
        w = cv2.warpPerspective(r, H, (ea.shape[1], ea.shape[0]))
        wi = Image.fromarray(w)
        rows.append((fam, p["id"], wi, grade(wi, fam, "darker"), grade(wi, fam, "auto"), grade(wi, fam, "brighter"), e))
    th = 360
    tiles = [[im.resize((round(im.width * th / im.height), th), Image.LANCZOS) for im in row[2:]] for row in rows]
    W = max(sum(t.width for t in ts) + 4 * 16 for ts in tiles)
    sheet = Image.new("RGB", (W, len(rows) * (th + 46) + 40), (18, 18, 18))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ROOT / "docs/brand/fonts/Marcellus-Regular.ttf"), 20)
    y = 12
    for (fam, pid, *_), ts in zip(rows, tiles):
        d.text((16, y), f"{LABEL[fam]}  ({pid}, a photo the recipe never saw)    camera preview  |  "
                        f"OUR RECIPE darker, auto, brighter  |  HER EDIT", font=font, fill=(200, 196, 188))
        x = 16
        for t in ts:
            sheet.paste(t, (x, y + 30))
            x += t.width + 16
        y += th + 46
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=92)
    print(f"sheet: {out}")


def main() -> None:
    ap = ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("learn")
    sub.add_parser("families")
    t = sub.add_parser("test")
    t.add_argument("--out", type=Path, default=ROOT / "references" / "look09" / "recipe_vs_his_edit.jpg")
    g = sub.add_parser("grade")
    g.add_argument("image", type=Path)
    g.add_argument("--family", choices=FAMILIES, required=True)
    g.add_argument("--brightness", choices=[*BRIGHTNESS, "all"], default="all")
    g.add_argument("--warmth", type=float, default=0.0, help="-2 cooler .. +2 warmer")
    g.add_argument("--colour", type=float, help="colour strength; default makes up for the averaging loss")
    g.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.cmd == "learn":
        cmd_learn()
    elif a.cmd == "test":
        cmd_test(a.out)
    elif a.cmd == "grade":
        cmd_grade(a.image, a.family, a.brightness, a.out, a.warmth, a.colour)
    else:
        cat = json.loads(sc.CATALOGUE.read_text())
        import collections
        c = collections.Counter(family_of(p["tags"].get("light", "")) for p in cat["photos"])
        for f in FAMILIES:
            print(f"{f:<10}{c[f]:>4}  {LABEL[f]}")


if __name__ == "__main__":
    main()
