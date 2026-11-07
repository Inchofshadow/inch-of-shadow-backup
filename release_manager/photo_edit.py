"""The photo editor's maths (2026-09-27): the same operations the browser shows live on a small
preview, applied here to the full-size original when a copy is saved. The original file is never
written; every save is a new file with a JSON record of what was done. Local, no AI.

Order, identical in static/photo_editor.js:
  geometry  1. quarter turns clockwise  2. mirror  3. straighten (a rotation, zoomed so the frame
            stays covered)  4. crop (a rectangle as fractions of that frame)
  tone      on 0..1 values: exposure (stops), warmth, shadows, highlights, contrast, saturation
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageOps

TONE_KEYS = ("exposure", "contrast", "shadows", "highlights", "saturation", "warmth")
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def clean_params(p: dict | None) -> dict:
    """Clamp everything the browser sends to the ranges the editor offers."""
    p = p or {}
    out = {"rot": int(p.get("rot", 0)) % 4, "flip": bool(p.get("flip", False)),
           "angle": max(-45.0, min(45.0, float(p.get("angle", 0.0))))}
    c = p.get("crop") or {}
    x = min(max(float(c.get("x", 0.0)), 0.0), 1.0)
    y = min(max(float(c.get("y", 0.0)), 0.0), 1.0)
    w = min(max(float(c.get("w", 1.0)), 0.01), 1.0 - x)
    h = min(max(float(c.get("h", 1.0)), 0.01), 1.0 - y)
    out["crop"] = {"x": x, "y": y, "w": w, "h": h}
    for k in TONE_KEYS:
        out[k] = max(-1.0, min(1.0, float(p.get(k, 0.0))))
    return out


def cover_scale(w: float, h: float, angle_deg: float) -> float:
    """How much a w x h picture turned by angle must grow to still cover the w x h frame."""
    a = math.radians(abs(angle_deg))
    c, s = math.cos(a), math.sin(a)
    return max((w * c + h * s) / w, (w * s + h * c) / h)


def tone(x: np.ndarray, p: dict) -> np.ndarray:
    """x: float32 H x W x 3 in 0..1, changed in place and returned."""
    if p["exposure"]:
        x *= 2.0 ** p["exposure"]
    if p["warmth"]:
        x[..., 0] *= 1 + 0.12 * p["warmth"]
        x[..., 2] *= 1 - 0.12 * p["warmth"]
    np.clip(x, 0.0, 1.0, out=x)
    if p["shadows"]:
        x += p["shadows"] * 0.9 * x * (1 - x) ** 3
    if p["highlights"]:
        x += p["highlights"] * 0.9 * x ** 3 * (1 - x)
    if p["contrast"]:
        x -= 0.5
        x *= 1 + p["contrast"]
        x += 0.5
    if p["saturation"]:
        lum = (x @ LUMA)[..., None]
        x -= lum
        x *= 1 + p["saturation"]
        x += lum
    return np.clip(x, 0.0, 1.0, out=x)


def geometry(im: Image.Image, p: dict) -> Image.Image:
    """Quarter turns, mirror, straighten and crop, in one resampling for the straighten+crop."""
    if p["rot"]:
        im = im.transpose({1: Image.ROTATE_270, 2: Image.ROTATE_180, 3: Image.ROTATE_90}[p["rot"]])
    if p["flip"]:
        im = ImageOps.mirror(im)
    W, H = im.size
    c = p["crop"]
    X0, Y0 = c["x"] * W, c["y"] * H
    ow, oh = max(1, round(c["w"] * W)), max(1, round(c["h"] * H))
    if not p["angle"]:
        return im.crop((round(X0), round(Y0), round(X0) + ow, round(Y0) + oh))
    s = cover_scale(W, H, p["angle"])
    a = math.radians(p["angle"])
    cs, sn = math.cos(a), math.sin(a)
    cx, cy = W / 2, H / 2
    # output pixel (u, v) sits at frame (u + X0, v + Y0); the frame is the picture turned by +angle
    # (clockwise on screen, as the canvas does) and grown by s about the centre. Inverse mapping:
    A, B = cs / s, sn / s
    D, E = -sn / s, cs / s
    Cc = cx + A * (X0 - cx) + B * (Y0 - cy)
    F = cy + D * (X0 - cx) + E * (Y0 - cy)
    return im.transform((ow, oh), Image.AFFINE, (A, B, Cc, D, E, F), resample=Image.BICUBIC)


def apply(im: Image.Image, params: dict, strip: int = 1024) -> Image.Image:
    """The whole edit on a picture of any size; tone in strips to keep memory low."""
    p = clean_params(params)
    im = geometry(ImageOps.exif_transpose(im).convert("RGB"), p)
    if not any(p[k] for k in TONE_KEYS):
        return im
    a = np.asarray(im)
    out = np.empty_like(a)
    for y in range(0, a.shape[0], strip):
        part = a[y:y + strip].astype(np.float32) / 255.0
        out[y:y + strip] = (tone(part, p) * 255.0 + 0.5).astype(np.uint8)
    return Image.fromarray(out)
