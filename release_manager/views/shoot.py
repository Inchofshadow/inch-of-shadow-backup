"""
release_manager/views/shoot.py
------------------------------
Studio area module, part 2a (RM 2.0 slice 6, plans/strategy/rm2-dry-run-2026-11-06.md): the Shoot
pages (catalogue, photo page, covers, grades, crops) and the photo editor (/edit). Routes register on
the shared app from core.py, so the endpoint names are unchanged. webapp.py imports this module and
re-exports the names (SHOOT_CATALOGUE for the tests, EDITS_DIR for the artwork resizer). Tests that
patch EDITS_DIR for the editor routes patch this module, since the routes read its globals.
Imagine (views/imagine.py) imports _shoot_photos, _shoot_tools and SHOOT_EDIT_PREVIEWS from here.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import (
    render_template, request, redirect, url_for, jsonify, abort, send_from_directory,
)
from werkzeug.utils import secure_filename

from release_manager.core import (
    app, PROJECT_ROOT, ARTWORK_DIR, ARTWORK_EXTENSIONS, _safe_existing_path,
)
from release_manager.views.studio import _frame_tokens

# ---------------------------------------------------------------------------
# Studio: Shoot (Machine-11). The 204 catalogued photos, the filters contact_sheet.py has,
# and a crop for one format made with shoot_pull's own crop_box. Reads the catalogue and
# the preview cache; writes only into generated_images/shoot/ when a crop is asked for.
# ---------------------------------------------------------------------------

SHOOT_CATALOGUE = PROJECT_ROOT / "plans" / "control-panel" / "shoot-catalogue.json"
SHOOT_OUT = PROJECT_ROOT / "generated_images" / "shoot"


def _shoot_tools():
    import importlib.util
    mods = {}
    for name in ("shoot_catalogue", "shoot_pull"):
        spec = importlib.util.spec_from_file_location(name, PROJECT_ROOT / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod                       # shoot_pull does `import shoot_catalogue`
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods["shoot_catalogue"], mods["shoot_pull"]


def _shoot_photos() -> tuple[dict, list[dict]]:
    if not SHOOT_CATALOGUE.exists():
        return {}, []
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    return cat, cat.get("photos", [])


def _shoot_filter(photos: list[dict], args) -> list[dict]:
    """The same filters as docs/brand/kit/scripts/contact_sheet.py, from the query string."""
    stars = args.get("stars", type=int)
    q = (args.get("q") or "").strip().lower()
    out = []
    for p in photos:
        tags = p.get("tags", {}); ai = p.get("ai_generated") or {}
        if stars and p.get("her_rating") != stars:
            continue
        if args.get("unused") and p.get("used_in"):
            continue
        if args.get("no_ai_on_him") and ai.get("on_him"):
            continue
        if args.get("no_ai") and ai:
            continue
        light = (tags.get("light") or "").lower()
        if args.get("flash") == "yes" and "flash" not in light:
            continue
        if args.get("flash") == "no" and "flash" in light:
            continue
        if args.get("orientation") and p.get("orientation") != args.get("orientation"):
            continue
        if q and q not in " ".join(str(v) for v in tags.values()).lower():
            continue
        out.append(p)
    return out


def _shoot_groups(cat: dict, photos: list[dict], sort: str) -> list[tuple[dict | None, list[dict]]]:
    """The photos in his batches: by outfit (the order of the evening), by capture time, or by id.
    The ids follow her export folders, not the shoot, so 'outfit' is the default."""
    if sort == "id":
        return [(None, sorted(photos, key=lambda p: p["id"]))]
    if sort == "time":
        return [(None, sorted(photos, key=lambda p: p.get("captured") or ""))]
    groups = []
    for o in cat.get("outfits", []):
        ps = sorted((p for p in photos if p.get("outfit") == o["key"]), key=lambda p: p.get("captured") or "")
        if ps:
            groups.append((o, ps))
    rest = sorted((p for p in photos if not p.get("outfit")), key=lambda p: p["id"])
    if rest:
        groups.append(({"key": "", "label": "no outfit recorded", "colour": "", "swatch": "", "count": len(rest)}, rest))
    return groups


@app.route("/shoot")
def shoot_page():
    cat, photos = _shoot_photos()
    shown = _shoot_filter(photos, request.args)
    if request.args.get("outfit"):
        shown = [p for p in shown if p.get("outfit") == request.args.get("outfit")]
    sort = request.args.get("sort") or "outfit"
    drive = Path("/Volumes/Intenso/Inch of Shadow photoshoot").is_dir()
    edited = {p["id"] for p in photos if (SHOOT_EDIT_PREVIEWS / f"{p['id']}.jpg").is_file()}
    return render_template("shoot.html", photos=shown, total=len(photos), cat=cat, drive=drive, sort=sort,
                           edits_cached=len(edited), edited=edited,
                           groups=_shoot_groups(cat, shown, sort), outfits=cat.get("outfits", []),
                           args=request.args, credit=(cat.get("credit") or {}).get("line", ""))


SHOOT_EDIT_PREVIEWS = Path.home() / ".cache" / "inch-of-shadow" / "shoot-edit-previews"


def _shoot_preview(p: dict) -> Path | None:
    """What the page shows for a photo: the 1024 px preview of HER EDIT when it has been made
    (docs/brand/kit/scripts/shoot_edit_previews.py, needs the Intenso once), else the raw preview,
    which is in colour even where her edit is black and white."""
    f = SHOOT_EDIT_PREVIEWS / f"{p['id']}.jpg"
    if f.is_file():
        return f
    sc, _ = _shoot_tools()
    f = sc.cache_path(p["raw"])
    return f if f.is_file() else None


SHOOT_GRADES = Path.home() / ".cache" / "inch-of-shadow" / "shoot-grades"
GRADE_LABELS = {"bw": "B&W", "dusk": "Dusk", "day": "Day", "flash": "Flash", "bluehour": "Blue hour"}


def _edit_recipe():
    """edit_recipe.py (Look-09), loaded by path like the shoot tools."""
    import importlib.util
    _shoot_tools()                                          # registers shoot_catalogue, which it imports
    if "edit_recipe" not in sys.modules:
        spec = importlib.util.spec_from_file_location("edit_recipe", PROJECT_ROOT / "edit_recipe.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["edit_recipe"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["edit_recipe"]


import threading
from concurrent.futures import ThreadPoolExecutor

_GRADE_LOCKS: dict = {}
_GRADE_LOCKS_GUARD = threading.Lock()
_GRADE_QUEUE = ThreadPoolExecutor(max_workers=1, thread_name_prefix="shoot-grade")


def _grade_lock(key: str) -> threading.Lock:
    with _GRADE_LOCKS_GUARD:
        return _GRADE_LOCKS.setdefault(key, threading.Lock())


def _warm_grades(p: dict, first: str) -> None:
    """Prepare a photo's five templates in the background, its own light first, so a click is instant."""
    order = [first] + [f for f in GRADE_LABELS if f != first]
    for fam in order:
        if not (SHOOT_GRADES / f"{p['id']}_{fam}.jpg").is_file():
            _GRADE_QUEUE.submit(_shoot_grade, p, fam)


def _shoot_grade(p: dict, fam: str) -> Path | None:
    """The raw preview graded with one of the five templates. Local colour and tone only, no AI.
    One grade per file at a time: the page asks for the same picture five times at once."""
    out = SHOOT_GRADES / f"{p['id']}_{fam}.jpg"
    if out.is_file():
        return out
    with _grade_lock(out.name):
        if out.is_file():                       # made while this request waited
            return out
        return _make_grade(p, fam, out)


def _make_grade(p: dict, fam: str, out: Path) -> Path | None:
    sc, _ = _shoot_tools()
    er = _edit_recipe()
    from PIL import Image
    small = sc.cache_path(p["raw"])
    raw = sc.DRIVE / p["raw"]
    if raw.is_file():
        # graded at the size the finish was measured at (2400 px), from the camera's own preview in
        # the NEF, then shrunk: at 1024 px the sharpening worked on half-pixel detail and looked crunchy
        im = er.load_image(raw)
        im.thumbnail((int(er.MEASURED_AT), int(er.MEASURED_AT)), Image.LANCZOS)
    elif small.is_file():
        im = Image.open(small).convert("RGB")
    else:
        return None
    g = er.grade(im, fam)
    g.thumbnail((1024, 1024), Image.LANCZOS)
    SHOOT_GRADES.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part.jpg")
    g.save(tmp, quality=92)
    tmp.replace(out)                            # never serve a half-written file
    return out


@app.route("/shoot/thumb/<photo_id>")
def shoot_thumb(photo_id):
    """The photo's preview: her edit when cached, else the raw's; or the raw, or a template on it."""
    _, photos = _shoot_photos()
    p = next((x for x in photos if x["id"] == photo_id), None)
    if p is None:
        abort(404)
    kind = request.args.get("kind")
    if kind == "raw":                                   # the toggle on the photo page
        sc, _ = _shoot_tools()
        f = sc.cache_path(p["raw"])
        f = f if f.is_file() else None
    elif kind == "grade":
        fam = request.args.get("family", "")
        if fam not in GRADE_LABELS:
            abort(404)
        f = _shoot_grade(p, fam)
    else:
        f = _shoot_preview(p)
    if f is None:
        abort(404)
    return send_from_directory(str(f.parent), f.name)


IG_GRID_CACHE = Path.home() / ".cache" / "inch-of-shadow" / "ig-grid"
IG_PROFILE_PIC = PROJECT_ROOT / "artwork" / "600x600 profile pic.png"


def _ig_grid_tiles(limit: int = 8) -> list[dict]:
    """His real grid, newest first, from the Instagram data exports in data/: the first image of each
    post (a carousel shows its first slide) and a frame of each reel. Video frames are pulled once
    with ffmpeg into ~/.cache. Nothing is read from Instagram."""
    tiles = {}
    for export in sorted(PROJECT_ROOT.glob("data/instagram-inch_of_shadow-*")):
        media_dir = export / "your_instagram_activity" / "media"
        for name in ("posts_1.json", "posts.json"):
            f = media_dir / name
            if not f.is_file():
                continue
            for post in json.loads(f.read_text(encoding="utf-8")):
                media = post.get("media") or []
                if not media:
                    continue
                first = media[0]
                ts = post.get("creation_timestamp") or first.get("creation_timestamp") or 0
                tiles.setdefault(Path(first["uri"]).name, {"file": export / first["uri"], "ts": ts,
                                 "kind": "carousel" if len(media) > 1 else "post", "n": len(media)})
        f = media_dir / "reels.json"
        if f.is_file():
            for reel in json.loads(f.read_text(encoding="utf-8")).get("ig_reels_media", []):
                for m in reel.get("media") or []:
                    tiles.setdefault(Path(m["uri"]).name, {"file": export / m["uri"], "ts": m.get("creation_timestamp") or 0,
                                     "kind": "reel", "n": 1})
    out = []
    for name, t in sorted(tiles.items(), key=lambda kv: kv[1]["ts"], reverse=True):
        if not t["file"].is_file():
            continue
        t["name"] = name; t["date"] = datetime.fromtimestamp(t["ts"]).strftime("%Y-%m-%d")
        if t["file"].suffix.lower() == ".mp4":
            frame = IG_GRID_CACHE / (name + ".jpg")
            if not frame.is_file():
                ffmpeg = shutil.which("ffmpeg") or str(Path.home() / ".local" / "bin" / "ffmpeg")
                IG_GRID_CACHE.mkdir(parents=True, exist_ok=True)
                try:
                    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", "1", "-i", str(t["file"]),
                                    "-frames:v", "1", "-q:v", "3", str(frame)], check=True, timeout=60)
                except Exception:
                    continue
            t["file"] = frame
        out.append(t)
        if len(out) >= limit:
            break
    return out


def _shoot_sims(p: dict, sp) -> dict:
    """How the stored head position crops this photo for each simulation, as CSS percentages: the
    preview is placed inside a box of the format's shape exactly where shoot_pull would crop it."""
    from PIL import Image
    f = _shoot_preview(p)
    if f is None:
        return {}
    with Image.open(f) as im:
        W, H = im.size
    sub = p.get("subject") or {"x": 0.5, "y": 0.42}
    sims = {}
    for fmt in ("post", "carousel", "square"):
        l, t, r, b = sp.crop_box((W, H), fmt, (sub["x"], sub["y"], "head"))
        tw, th, _ = sp.FORMATS[fmt]
        sims[fmt] = {"ratio": f"{tw} / {th}", "width": round(W / (r - l) * 100, 3),
                     "left": round(-l / (r - l) * 100, 3), "top": round(-t / (b - t) * 100, 3)}
    return sims


def _cover_idea_colour(idea: dict | None) -> str:
    """The type colour for a cover idea: the mood's light colour from frame.md, or the shirt red."""
    if not idea:
        return "#D6D1C8"
    if idea.get("colour") == "red":
        return "#D8262E"
    try:
        moods = _frame_tokens().get("moods", {})
        return moods.get(idea.get("colour"), {}).get("light") or "#D6D1C8"
    except Exception:
        return "#D6D1C8"


def _cover_font(idea: dict | None) -> dict:
    """The face the cover idea is set in: css family, where it comes from, how big."""
    from release_manager.cover_fonts import FONTS, css_family, font_path
    key = (idea or {}).get("font") or "marcellus"
    f = FONTS.get(key) or FONTS["marcellus"]
    return {"key": key, "label": f["label"], "group": f["group"], "family": css_family(key), "caps": f["caps"],
            "scale": f["scale"], "local": f.get("local"), "url": url_for("shoot_font", key=key) if font_path(key) else None}


@app.route("/shoot/covers")
def shoot_covers():
    """Every photo's cover idea side by side, by outfit, for reviewing them at once."""
    cat, photos = _shoot_photos()
    _, sp = _shoot_tools()
    groups, fonts = [], {}
    for o in cat.get("outfits", []):
        rows = []
        for p in sorted((x for x in photos if x.get("outfit") == o["key"] and x.get("cover_idea")), key=lambda x: x.get("captured") or ""):
            sims = _shoot_sims(p, sp)
            if not sims:
                continue
            font = _cover_font(p.get("cover_idea"))
            if font["url"]:
                fonts[font["key"]] = font
            rows.append({"p": p, "c": sims["square"], "idea": p.get("cover_idea") or {}, "font": font})
        if rows:
            groups.append((o, rows))
    return render_template("shoot_covers.html", groups=groups, fonts=list(fonts.values()))


@app.route("/shoot/font/<key>")
def shoot_font(key):
    """A face from the arsenal, for the cover mock only (trial files stay trial files)."""
    from release_manager.cover_fonts import font_path
    f = font_path(key)
    if f is None:
        abort(404)
    return send_from_directory(str(f.parent), f.name)


@app.route("/shoot/<photo_id>")
def shoot_photo(photo_id):
    cat, photos = _shoot_photos()
    p = next((x for x in photos if x["id"] == photo_id), None)
    if p is None:
        abort(404)
    _, sp = _shoot_tools()
    outs = sorted(SHOOT_OUT.glob(f"{photo_id}_*.jpg")) if SHOOT_OUT.is_dir() else []
    drive = Path("/Volumes/Intenso/Inch of Shadow photoshoot").is_dir()
    outfit = next((o for o in cat.get("outfits", []) if o["key"] == p.get("outfit")), None)
    her_family = _edit_recipe().family_of(p.get("tags", {}).get("light", ""))
    _warm_grades(p, her_family)
    return render_template("shoot_photo.html", p=p, formats=sp.FORMATS, outs=[o.name for o in outs],
                           drive=drive, credit=(cat.get("credit") or {}).get("line", ""),
                           message=request.args.get("m"), outfit=outfit, sims=_shoot_sims(p, sp),
                           grid=_ig_grid_tiles(8), pfp=IG_PROFILE_PIC.is_file(),
                           edit_preview=(SHOOT_EDIT_PREVIEWS / f"{photo_id}.jpg").is_file(),
                           idea=p.get("cover_idea"), idea_colour=_cover_idea_colour(p.get("cover_idea")),
                           font=_cover_font(p.get("cover_idea")),
                           grades=GRADE_LABELS, her_family=her_family, copies=_edit_copies(f"shoot:{photo_id}"))


@app.route("/shoot/full/<photo_id>")
def shoot_full(photo_id):
    """The photo at full size: her edit from the Intenso when it is connected, else the 1024 px raw preview."""
    _, photos = _shoot_photos()
    p = next((x for x in photos if x["id"] == photo_id), None)
    if p is None:
        abort(404)
    sc, _ = _shoot_tools()
    edit = sc.DRIVE / p["edit"]
    if request.args.get("kind") == "grade":            # a template: the 1024 px graded preview
        fam = request.args.get("family", "")
        g = _shoot_grade(p, fam) if fam in GRADE_LABELS else None
        if g is None:
            abort(404)
        return send_from_directory(str(g.parent), g.name)
    if edit.is_file() and request.args.get("kind") != "raw":
        return send_from_directory(str(edit.parent), edit.name)
    f = sc.cache_path(p["raw"])
    if not f.is_file():
        abort(404)
    return send_from_directory(str(f.parent), f.name)


@app.route("/shoot/grid-tile/<name>")
def shoot_grid_tile(name):
    t = next((x for x in _ig_grid_tiles(8) if x["name"] == name), None)
    if t is None:
        abort(404)
    return send_from_directory(str(t["file"].parent), t["file"].name)


@app.route("/shoot/pfp")
def shoot_pfp():
    if not IG_PROFILE_PIC.is_file():
        abort(404)
    return send_from_directory(str(IG_PROFILE_PIC.parent), IG_PROFILE_PIC.name)


@app.route("/shoot/<photo_id>/pull", methods=["POST"])
def shoot_pull_route(photo_id):
    """Crop the edit for one format, his head kept in frame, the way shoot_pull.py does it."""
    from PIL import Image, ImageOps
    _, photos = _shoot_photos()
    p = next((x for x in photos if x["id"] == photo_id), None)
    sc, sp = _shoot_tools()
    fmt = request.form.get("format", "")
    if p is None or fmt not in sp.FORMATS:
        abort(400)
    src = sc.DRIVE / p["edit"]
    if not src.is_file():
        return redirect(url_for("shoot_photo", photo_id=photo_id, m="The photo drive is not connected, so the full-size edit cannot be read."))
    im = Image.open(src); icc = im.info.get("icc_profile")
    im = ImageOps.exif_transpose(im).convert("RGB")
    sub = p.get("subject") or {"x": 0.5, "y": 0.42}
    box = sp.crop_box(im.size, fmt, (sub["x"], sub["y"], "head"))
    tw, th, _ = sp.FORMATS[fmt]
    SHOOT_OUT.mkdir(parents=True, exist_ok=True)
    out = SHOOT_OUT / f"{photo_id}_{fmt}.jpg"
    im.crop(box).resize((tw, th), Image.LANCZOS).save(out, quality=95, **({"icc_profile": icc} if icc else {}))
    return redirect(url_for("shoot_photo", photo_id=photo_id, m=f"{fmt} written: {out.name}"))


@app.route("/shoot/out/<filename>")
def shoot_out(filename):
    if not SHOOT_OUT.is_dir():
        abort(404)
    return send_from_directory(str(SHOOT_OUT), filename)


# ---------------------------------------------------------------------------
# Photo editor (2026-09-27): crop, turn, straighten and adjust live, iPhone style; saving writes a
# NEW file in artwork/edits/ with a JSON record. The original is never written. Local, no AI.
# ---------------------------------------------------------------------------

EDITS_DIR = ARTWORK_DIR / "edits"
EDIT_TAGS = [   # key, label, aspect, colour: the shapes each platform wants, in its own colour
    ("ig-post", "IG Post", "4:5", "#E4405F"),
    ("ig-grid", "IG Grid", "3:4", "#E4405F"),
    ("ig-reel", "IG Reel / Story", "9:16", "#E4405F"),
    ("spotify-cover", "Spotify Cover", "1:1", "#1DB954"),
    ("spotify-canvas", "Spotify Canvas", "9:16", "#1DB954"),
    ("apple-cover", "Apple Music Cover", "1:1", "#FA2D48"),
    ("youtube-thumb", "YouTube Thumbnail", "16:9", "#FF0000"),
    ("youtube-banner", "YouTube Banner", "16:9", "#FF0000"),
    ("tiktok", "TikTok", "9:16", "#25F4EE"),
    ("soundcloud-banner", "SoundCloud Banner", "124:26", "#FF5500"),
    ("bandcamp-header", "Bandcamp Header", "975:180", "#629AA9"),
]


def _edit_copies(src: str) -> list[dict]:
    """The copies saved from one picture, newest first, from their JSON records."""
    out = []
    if not EDITS_DIR.is_dir():
        return out
    for rec in EDITS_DIR.glob("*.json"):
        try:
            d = json.loads(rec.read_text())
        except (OSError, ValueError):
            continue
        img = rec.with_suffix(".jpg")
        if d.get("source") == src and img.is_file():
            tag = next((t for t in EDIT_TAGS if t[0] == d.get("tag")), None)
            out.append({"file": img.name, "saved": d.get("saved", ""), "size": d.get("size"),
                        "tag": tag[1] if tag else "", "colour": tag[3] if tag else "",
                        "url": url_for("serve_artwork", filename=f"edits/{img.name}"),
                        "resizer": url_for("artwork_resizer_page", pick=f"edits/{img.name}")})
    return sorted(out, key=lambda x: x["saved"], reverse=True)
EDIT_PREVIEWS = Path.home() / ".cache" / "inch-of-shadow" / "edit-previews"
EDIT_PREVIEW_EDGE = 1600


def _edit_source(src: str) -> dict | None:
    """What a `src` names: 'shoot:out-083' (her edit on the drive), 'artwork:<file>', 'edit:<file>'."""
    kind, _, name = (src or "").partition(":")
    if kind == "shoot":
        _, photos = _shoot_photos()
        p = next((x for x in photos if x["id"] == name), None)
        if p is None:
            return None
        sc, _ = _shoot_tools()
        full = sc.DRIVE / p["edit"]
        return {"src": src, "label": p["id"], "stem": p["id"], "full": full if full.is_file() else None,
                "fallback": SHOOT_EDIT_PREVIEWS / f"{p['id']}.jpg", "back": url_for("shoot_photo", photo_id=p["id"])}
    if kind == "imagine":
        from release_manager import imagine as im
        f = _safe_existing_path(im.OUT, name)
        if f is None:
            return None
        return {"src": src, "label": f.name, "stem": f.stem, "full": f, "fallback": None,
                "back": url_for("imagine_page", release=f.name.split("_")[0])}
    base = {"artwork": ARTWORK_DIR, "edit": EDITS_DIR}.get(kind)
    if base is None:
        return None
    f = _safe_existing_path(base, name)
    if f is None or f.suffix.lower() not in ARTWORK_EXTENSIONS:
        return None
    pick = f.name if kind == "artwork" else f"edits/{f.name}"
    return {"src": src, "label": f.name, "stem": Path(f.name).stem, "full": f, "fallback": None,
            "back": url_for("artwork_resizer_page", pick=pick)}


@app.route("/edit")
def photo_editor():
    info = _edit_source(request.args.get("src", ""))
    if info is None:
        abort(404)
    size = None
    if info["full"]:
        from PIL import Image
        with Image.open(info["full"]) as im:
            size = im.size
    return render_template("photo_editor.html", info=info, size=size, tags=EDIT_TAGS, copies=_edit_copies(info["src"]))


@app.route("/edit/preview")
def photo_editor_preview():
    """The picture the editor works on live: at most 1600 px, cached; the save uses the full size."""
    info = _edit_source(request.args.get("src", ""))
    if info is None:
        abort(404)
    src_file = info["full"] or (info["fallback"] if info["fallback"] and info["fallback"].is_file() else None)
    if src_file is None:
        abort(404)
    import hashlib
    from PIL import Image, ImageOps
    key = hashlib.sha1(f"{src_file}:{src_file.stat().st_mtime}".encode()).hexdigest()[:16]
    out = EDIT_PREVIEWS / f"{key}.jpg"
    if not out.is_file():
        EDIT_PREVIEWS.mkdir(parents=True, exist_ok=True)
        with Image.open(src_file) as im:
            im.draft("RGB", (EDIT_PREVIEW_EDGE, EDIT_PREVIEW_EDGE))
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((EDIT_PREVIEW_EDGE, EDIT_PREVIEW_EDGE), Image.LANCZOS)
            im.save(out, quality=90)
    return send_from_directory(str(out.parent), out.name)


@app.route("/edit/save", methods=["POST"])
def photo_editor_save():
    """Apply the edit to the full-size original and write it as a new file; never the original."""
    from PIL import Image
    from release_manager.photo_edit import apply, clean_params
    data = request.get_json(silent=True) or {}
    info = _edit_source(data.get("src", ""))
    if info is None:
        return jsonify({"ok": False, "error": "Unknown picture."}), 404
    if info["full"] is None:
        return jsonify({"ok": False, "error": "The full-size photo is on the Intenso: connect the drive to save."}), 409
    params = clean_params(data.get("params"))
    tag = next((t for t in EDIT_TAGS if t[0] == data.get("tag")), None)
    with Image.open(info["full"]) as im:
        icc = im.info.get("icc_profile")
        out_im = apply(im, params)
    EDITS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{secure_filename(info['stem']) or 'photo'}{'_' + tag[0] if tag else ''}_edit_{stamp}.jpg"
    dest = EDITS_DIR / name
    out_im.save(dest, quality=95, subsampling=0, **({"icc_profile": icc} if icc else {}))
    (EDITS_DIR / (dest.stem + ".json")).write_text(json.dumps({
        "source": info["src"], "source_file": str(info["full"]), "saved": datetime.now().isoformat(timespec="seconds"),
        "size": list(out_im.size), "params": params, "tag": tag[0] if tag else None,
        "made_by": "Release Manager photo editor (local, no AI)"}, indent=2))
    return jsonify({"ok": True, "file": name, "size": list(out_im.size), "folder": "artwork/edits/",
                    "reveal": url_for("photo_editor_reveal"),
                    "url": url_for("serve_artwork", filename=f"edits/{name}"),
                    "resizer": url_for("artwork_resizer_page", pick=f"edits/{name}"),
                    "again": url_for("photo_editor", src=f"edit:{name}")})


@app.route("/edit/reveal", methods=["POST"])
def photo_editor_reveal():
    """Show a saved copy selected in Finder (only files inside artwork/edits/)."""
    data = request.get_json(silent=True) or request.form
    f = _safe_existing_path(EDITS_DIR, (data.get("file") or ""))
    if f is None:
        return jsonify({"ok": False}), 404
    subprocess.Popen(["open", "-R", str(f)])
    return jsonify({"ok": True})


@app.route("/edit/delete", methods=["POST"])
def photo_editor_delete():
    """Move a saved copy (and its JSON record) to the macOS Trash, on Amir's click. Only files in
    artwork/edits/; the Trash keeps them until it is emptied, so a wrong click can be undone."""
    import shutil
    data = request.get_json(silent=True) or request.form
    f = _safe_existing_path(EDITS_DIR, (data.get("file") or ""))
    if f is None:
        return jsonify({"ok": False}), 404
    trash = Path.home() / ".Trash"
    for part in (f, f.with_suffix(".json")):
        if part.is_file():
            dest = trash / part.name
            if dest.exists():
                dest = trash / f"{part.stem} {datetime.now().strftime('%H.%M.%S')}{part.suffix}"
            shutil.move(str(part), str(dest))
    return jsonify({"ok": True})
