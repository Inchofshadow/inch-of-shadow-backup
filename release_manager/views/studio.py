"""
release_manager/views/studio.py
-------------------------------
Studio area module, part 1 (RM 2.0 slice 5, plans/strategy/rm2-dry-run-2026-11-06.md): the Shadow
Archive, Effects, Fonts and Video (the HyperFrames projects plus the Video Resizer section, and
/video-resizer). Routes register on the shared app from core.py, so the endpoint names are
unchanged. webapp.py imports this module and re-exports the names (the release page uses
_effects_for_release, the playground uses _fonts and _font_file_url, Imagine and Shoot use
_frame_tokens). The /resized and /resized_video file routes stay in core.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import (
    render_template, request, redirect, url_for, flash, jsonify, abort,
    send_from_directory, send_file,
)
from werkzeug.utils import secure_filename

from release_manager.core import (
    app, PROJECT_ROOT, VIDEO_DIR, RESIZED_VIDEO_DIR, VIDEO_EXTENSIONS,
    VIDEO_PRESETS, _picked_templates, _safe_existing_path,
)
from release_manager.storage import load_release, save_release, list_releases


# ---------------------------------------------------------------------------
# Shadow Archive (Machine-18): the reference library, read only. Source of truth is
# docs/brand/shadow-archive/index.json, written by Claude at intake; this page reads it.
# ---------------------------------------------------------------------------
from release_manager import archive as _archive


def _archive_index():
    """The index, or (None, error) so the page can say what is wrong instead of a 500."""
    try:
        return _archive.load_index(PROJECT_ROOT), None
    except _archive.ArchiveError as exc:
        return None, str(exc)


def _archive_file_url(rel_path: str) -> str:
    return url_for("archive_file", path=rel_path)


@app.route("/archive")
def archive_page():
    data, err = _archive_index()
    if data is None:
        return render_template("archive.html", refs=[], total=0, facets={"kind": [], "topics": [], "lane": [], "weight": [], "releases": []},
                               args=request.args, sort="added", error=err), 500
    refs = data["references"]
    sort = request.args.get("sort") or "added"
    shown = _archive.sort_refs(_archive.filter_refs(refs, request.args), sort)
    try:
        fx = _effects.load(PROJECT_ROOT)
    except Exception:
        fx = None
    strips = {}
    for r in shown:
        ex = _archive_examples(r, fx)
        strips[r["id"]] = {"n": len(ex), "srcs": [x["src"] for x in ex[:4]]}
    return render_template("archive.html", refs=shown, total=len(refs), facets=_archive.facets(data, refs),
                           args=request.args, sort=sort, error=None, strips=strips)


@app.route("/archive/<rid>")
def archive_detail(rid):
    data, err = _archive_index()
    if data is None:
        abort(500)
    r = _archive.by_id(data, rid)
    if r is None:
        abort(404)
    notes_path = _archive.safe_path(PROJECT_ROOT, r["notes"])
    notes_html = ""
    if notes_path and notes_path.is_file():
        base = url_for("archive_file", path=str(Path(r["notes"]).parent) + "/") if Path(r["notes"]).parent != Path(".") else url_for("archive_file", path="")
        notes_html = _archive.render_markdown(notes_path.read_text(encoding="utf-8"), link_base=base)
    children = [{"label": c.get("label") or c["path"], "path": c["path"], "url": _archive_file_url(c["path"])}
                for c in (r.get("children") or [])]
    return render_template("archive_detail.html", r=r, notes_html=notes_html, children=children,
                           examples=_archive_examples(r))


def _archive_examples(r: dict, fx_data: dict | None = None) -> list[dict]:
    """Pictures for one archive entry: the effects taken from it that have an example image,
    plus the Imagine images of our own ideas. Never a 500: no pictures is an empty list."""
    out = []
    for i, ex in enumerate(r.get("examples") or []):
        p = _archive.safe_path(PROJECT_ROOT, ex.get("file") or "") if isinstance(ex, dict) else None
        if p is not None and p.is_file():
            out.append({"src": url_for("archive_example", rid=r["id"], i=i), "name": "", "what": ex.get("caption") or "", "href": None})
    try:
        from release_manager import imagine as im
        for img_id in r.get("images") or []:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                if (Path(im.OUT) / (img_id + ext)).is_file():
                    out.append({"src": url_for("imagine_image", filename=img_id + ext), "name": "", "what": "", "href": None})
                    break
    except Exception:
        pass
    try:
        data = fx_data or _effects.load(PROJECT_ROOT)
        for e in data["effects"]:
            if e.get("source") == r["id"] and _effects.example_path(PROJECT_ROOT, e) is not None:
                out.append({"src": url_for("effect_example", eid=e["id"]), "name": e.get("name") or e["id"],
                            "what": e.get("what") or "", "href": url_for("effect_detail", eid=e["id"]), "mine": bool(e.get("mine"))})
    except Exception:
        pass
    return out


@app.route("/archive/example/<rid>/<int:i>")
def archive_example(rid, i):
    data, err = _archive_index()
    if data is None:
        abort(500)
    r = _archive.by_id(data, rid)
    exs = (r or {}).get("examples") or []
    if r is None or i >= len(exs) or not isinstance(exs[i], dict):
        abort(404)
    p = _archive.safe_path(PROJECT_ROOT, exs[i].get("file") or "")
    if p is None or not p.is_file():
        abort(404)
    return send_file(p, mimetype="image/jpeg", max_age=86400)


@app.route("/archive/thumb/<rid>")
def archive_thumb(rid):
    data, err = _archive_index()
    if data is None:
        abort(500)
    r = _archive.by_id(data, rid)
    if r is None or not r.get("thumb"):
        abort(404)
    p = _archive.safe_path(PROJECT_ROOT, r["thumb"])
    if p is None or not p.is_file():
        abort(404)
    return send_file(p, mimetype="image/jpeg", max_age=86400)


@app.route("/archive/file/<path:path>")
def archive_file(path):
    """A markdown file or a folder of them inside the archive, rendered. Nothing outside it."""
    data, err = _archive_index()
    rel_path = path.replace("\\", "/")
    p = _archive.safe_path(PROJECT_ROOT, rel_path.rstrip("/"))
    if p is None or not p.exists():
        abort(404)
    owner = None
    if data is not None:
        for r in data["references"]:
            paths = [r.get("notes", "")] + [c["path"] for c in (r.get("children") or [])]
            if any(rel_path.rstrip("/").startswith(x.rstrip("/")) for x in paths if x):
                owner = r
                break
    if p.is_dir():
        return render_template("archive_file.html", title=p.name, rel_path=rel_path.rstrip("/") + "/",
                               listing=_archive.list_dir(p), body_html="", owner=owner)
    if p.suffix.lower() != ".md":
        abort(404)
    text = p.read_text(encoding="utf-8")
    first = text.splitlines()[0] if text else p.stem
    title = first[2:].strip() if first.startswith("# ") else p.stem
    parent = str(Path(rel_path).parent)
    base = url_for("archive_file", path=(parent + "/") if parent not in (".", "") else "")
    return render_template("archive_file.html", title=title, rel_path=rel_path, listing=None,
                           body_html=_archive.render_markdown(text, link_base=base), owner=owner)


# ---------------------------------------------------------------------------
# Effects (Machine-20): every named effect, look and format with an example, from
# docs/brand/effects/effects.json. The only write is Amir's "mine" pick.
# ---------------------------------------------------------------------------
from release_manager import effects_page as _effects


def _effects_index():
    try:
        return _effects.load(PROJECT_ROOT), None
    except _effects.EffectsError as exc:
        return None, str(exc)


def _release_choices() -> list[dict]:
    out = []
    for r in list_releases():
        out.append({"slug": r.get("slug", ""), "title": (r.get("metadata") or {}).get("title") or r.get("slug", "")})
    return out


@app.route("/effects")
def effects_page_view():
    data, err = _effects_index()
    slug = request.args.get("release") or ""
    if data is None:
        return render_template("effects.html", rows=[], total=0, shown_n=0, counts=None, makes={}, families={},
                               args=request.args, error=err, releases=[], release=None, chosen=[], uses=_effects.USES), 500
    args = request.args.to_dict()
    if args.get("kind") not in ("still", "motion"):
        args["kind"] = "still"          # two tabs: Photo (still) is the default, Video = motion
    shown = _effects.sort_effects(data, _effects.filter_effects(data["effects"], args))
    allowed = data.get("allowed") or {}
    rel = load_release(slug) if slug and re.fullmatch(r"[a-z0-9-]+", slug) else None
    chosen, chosen_ids = [], set()
    if rel:
        for e in _effects.release_effects(rel):
            r = _effects.by_id(data, e["id"])
            if r:
                chosen.append({"r": r, "used_in": e["used_in"]})
                chosen_ids.add(r["id"])
    return render_template("effects.html", rows=_effects.rows(data, shown), total=len(data["effects"]), shown_n=len(shown),
                           tab_counts=_effects.counts_by_kind(data),
                           counts=_effects.counts(data), families=allowed.get("family", {}), makes=allowed.get("make", {}),
                           args=args, error=None, releases=_release_choices(),
                           release={"slug": slug, "title": (rel.get("metadata") or {}).get("title") or slug} if rel else None,
                           chosen=chosen, chosen_ids=chosen_ids, uses=_effects.USES)


@app.route("/effects/<eid>")
def effect_detail(eid):
    data, err = _effects_index()
    if data is None:
        abort(500)
    r = _effects.by_id(data, eid)
    if r is None:
        abort(404)
    allowed = data.get("allowed") or {}
    archive_ref = r["source"] if r["source"].startswith("R-") else None
    return render_template("effect_detail.html", r=r, family_label=allowed.get("family", {}).get(r["family"], r["family"]),
                           make_label=allowed.get("make", {}).get(r["make"], r["make"]), archive_ref=archive_ref)


@app.route("/effects/<eid>/example")
def effect_example(eid):
    data, err = _effects_index()
    if data is None:
        abort(500)
    p = _effects.example_path(PROJECT_ROOT, _effects.by_id(data, eid))
    if p is None:
        abort(404)
    return send_file(p, mimetype="image/jpeg", max_age=3600)


@app.route("/api/effects/<eid>/flag", methods=["POST"])
def effect_flag(eid):
    body = request.get_json(silent=True) or {}
    field = body.get("field") or ""
    if field not in _effects.FLAGS:
        return jsonify({"error": "unknown flag"}), 400
    try:
        ok = _effects.set_flag(PROJECT_ROOT, eid, field, bool(body.get("value")))
    except _effects.EffectsError as exc:
        return jsonify({"error": str(exc)}), 500
    if not ok:
        return jsonify({"error": "unknown effect"}), 404
    return jsonify({"id": eid, field: bool(body.get("value"))})


@app.route("/api/releases/<slug>/effects", methods=["POST"])
def release_effect_set(slug):
    """Add, update (where it is used) or remove one effect on a release: brand.effects."""
    body = request.get_json(silent=True) or {}
    eid = body.get("id") or ""
    data, err = _effects_index()
    if data is None:
        return jsonify({"error": err}), 500
    if _effects.by_id(data, eid) is None:
        return jsonify({"error": "unknown effect"}), 404
    if not re.fullmatch(r"[a-z0-9-]+", slug or ""):
        return jsonify({"error": "bad release"}), 400
    rel = load_release(slug)
    if rel is None:
        return jsonify({"error": "unknown release"}), 404
    used = body.get("used_in")
    _effects.set_release_effect(rel, eid, used_in=used if isinstance(used, list) else None, remove=bool(body.get("remove")))
    save_release(rel)
    return jsonify({"ok": True, "effects": _effects.release_effects(rel)})


def _effects_for_release(rel: dict) -> list[dict]:
    """A release's chosen effects with their records, for the release page (never a 500)."""
    try:
        data = _effects.load(PROJECT_ROOT)
        out = []
        for e in _effects.release_effects(rel):
            r = _effects.by_id(data, e["id"])
            if r:
                out.append({"r": r, "used_in": e["used_in"]})
        return out
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Fonts (Machine-19): the font collection, read only, from docs/brand/fonts/fonts.json.
# Faces are served from local files the index lists, never from a CDN.
# ---------------------------------------------------------------------------
from release_manager import fonts_page as _fonts

FONT_PREVIEW_STYLES = 12          # styles set live on a detail page; the rest are listed


def _fonts_index():
    try:
        return _fonts.load(PROJECT_ROOT), None
    except _fonts.FontsError as exc:
        return None, str(exc)


def _font_file_url(fid: str, rel: str) -> str:
    return url_for("font_file", fid=fid, rel=rel)


@app.route("/fonts")
def fonts_page_view():
    data, err = _fonts_index()
    text = (request.args.get("t") or "")[:80]
    if data is None:
        return render_template("fonts.html", shown=[], total=0, counts={"group": [], "status": [], "licence": [], "mac": 0, "canva": 0},
                               args=request.args, sort="group", text=text, error=err), 500
    fonts = data["fonts"]
    sort = request.args.get("sort") or "group"
    shown = []
    for r in _fonts.sort_fonts(_fonts.filter_fonts(fonts, request.args), sort):
        x = _fonts.shape(r)
        x["faces"] = _fonts.face_rules(r, _font_file_url)
        shown.append(x)
    return render_template("fonts.html", shown=shown, total=len(fonts), counts=_fonts.counts(data, fonts),
                           args=request.args, sort=sort, text=text, error=None)


@app.route("/fonts/<fid>")
def font_detail(fid):
    data, err = _fonts_index()
    if data is None:
        abort(500)
    r = _fonts.by_id(data, fid)
    if r is None:
        abort(404)
    faces = _fonts.face_rules(r, _font_file_url, all_files=True)
    more = max(0, len(faces) - FONT_PREVIEW_STYLES)
    return render_template("font_detail.html", r=_fonts.shape(r), faces=faces[:FONT_PREVIEW_STYLES], more_files=more,
                           group_label=(data.get("allowed") or {}).get("group", {}).get(r["group"], ""),
                           releases=_fonts.releases_using(PROJECT_ROOT, r), text=(request.args.get("t") or "")[:80])


@app.route("/fonts/<fid>/file/<path:rel>")
def font_file(fid, rel):
    data, err = _fonts_index()
    if data is None:
        abort(500)
    r = _fonts.by_id(data, fid)
    p = _fonts.file_allowed(PROJECT_ROOT, r, rel) if r else None
    if p is None:
        abort(404)
    mime = "font/otf" if p.suffix.lower() == ".otf" else "font/ttf"
    return send_file(p, mimetype=mime, max_age=86400)


# ---------------------------------------------------------------------------
# Studio: Brand (Machine-10). Read-only, straight from docs/brand/frame.md, so the
# page can never disagree with the tools that read the same file.
# ---------------------------------------------------------------------------

def _frame_tokens():
    import importlib.util
    path = PROJECT_ROOT / "docs" / "brand" / "kit" / "scripts" / "frame_tokens.py"
    spec = importlib.util.spec_from_file_location("frame_tokens", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.load(PROJECT_ROOT / "docs" / "brand" / "frame.md")


# ---------------------------------------------------------------------------
# Studio: Video (Machine-12). The HyperFrames projects in ../videos: what exists, its
# renders, and a way to start a new one on brand with the kit's start_video_project.py.
# ---------------------------------------------------------------------------

VIDEOS_DIR = PROJECT_ROOT.parent / "videos"
_PROJECT_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")


def _video_projects() -> list[dict]:
    out = []
    if not VIDEOS_DIR.is_dir():
        return out
    for d in sorted(VIDEOS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith((".", "_")) or not (d / "hyperframes.json").is_file():
            continue
        meta = {}
        try:
            meta = json.loads((d / "meta.json").read_text())
        except (OSError, ValueError):
            pass
        mood = canvas = ""
        css = d / "brand.css"
        if css.is_file():
            m = re.search(r"mood (\w+)", css.read_text()[:200]); mood = m.group(1) if m else ""
        idx = d / "index.html"
        if idx.is_file():
            m = re.search(r'data-width="(\d+)"\s+data-height="(\d+)"', idx.read_text()); canvas = f"{m.group(1)}x{m.group(2)}" if m else ""
        renders = []
        rd = d / "renders"
        if rd.is_dir():
            for f in sorted(rd.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
                st = f.stat()
                renders.append({"name": f.name, "mb": round(st.st_size / 1e6, 1),
                                "when": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
        out.append({"name": d.name, "created": (meta.get("createdAt") or "")[:10], "mood": mood,
                    "canvas": canvas, "renders": renders, "path": str(d)})
    out.sort(key=lambda p: p["created"], reverse=True)
    return out


@app.route("/video")
def video_page():
    """Video: projects on top, the resizer section below; the resizer's GET builds the whole page."""
    return video_resizer_page()


@app.route("/video/start", methods=["POST"])
def video_start():
    """Start a project with the kit's starter (npx hyperframes init + brand.css + an on-brand first page)."""
    name = (request.form.get("name") or "").strip().lower()
    mood = request.form.get("mood") or "M2"
    canvas = request.form.get("canvas") or "reel"
    if not _PROJECT_NAME.match(name) or canvas not in ("reel", "wide", "square") or not re.match(r"^[A-Z0-9]{1,3}$", mood):
        abort(400)
    if (VIDEOS_DIR / name).exists():
        return redirect(url_for("video_page", m=f"{name} exists already; the starter never overwrites."))
    starter = PROJECT_ROOT / "docs" / "brand" / "kit" / "scripts" / "start_video_project.py"
    try:
        r = subprocess.run([sys.executable, str(starter), name, "--mood", mood, "--canvas", canvas],
                           cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        return redirect(url_for("video_page", m="The starter took longer than four minutes (npx hyperframes init); check the terminal."))
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    return redirect(url_for("video_page", m=("started " + name if r.returncode == 0 else "failed: ") + " " + tail[0][:200]))


@app.route("/video/render/<project>/<filename>")
def video_render(project, filename):
    if not _PROJECT_NAME.match(project) or "/" in filename or not filename.endswith(".mp4"):
        abort(404)
    d = VIDEOS_DIR / project / "renders"
    if not (d / filename).is_file():
        abort(404)
    return send_from_directory(str(d), filename)


# ---------------------------------------------------------------------------
# Video Resizer page
# ---------------------------------------------------------------------------

VIDEO_FOCAL_POINTS = [
    "top-left", "top", "top-right",
    "left", "center", "right",
    "bottom-left", "bottom", "bottom-right",
]


def _build_video_export_groups():
    """Build grouped export specs for the template."""
    from video_resizer import VIDEO_EXPORTS
    groups = []
    seen = {}
    labels = {
        "reel_instagram": "Reel",
        "story_instagram": "Story",
        "post_square_instagram": "Post (Square)",
        "post_portrait_instagram": "Post (Portrait)",
        "video_youtube": "Video",
        "shorts_youtube": "Shorts",
        "canvas_square_spotify": "Canvas (Square)",
        "canvas_vertical_spotify": "Canvas (Vertical)",
        "video_youtube_1440": "Video 1440p",
        "video_youtube_4k": "Video 4K",
        "video_tiktok": "Video",
    }
    for template, w, h, category, platform, dur_max, dur_min, audio, fps, notes in VIDEO_EXPORTS:
        if category not in seen:
            seen[category] = len(groups)
            groups.append({"name": category, "exports": []})
        dur_str = f"{dur_max}s" if dur_max else None
        if dur_min:
            dur_str = f"{dur_min}-{dur_max}s"
        groups[seen[category]]["exports"].append({
            "template": template,
            "label": labels.get(template, template),
            "width": w,
            "height": h,
            "duration": dur_str,
            "notes": notes,
        })
    return groups


VIDEO_SHAPES = ("9:16", "4:5", "1:1", "16:9")


def _video_frames(raw: str) -> dict:
    """The frames Amir dragged on the page, one per shape, as JSON from a hidden field; checked."""
    from video_resizer import picked_frame
    try:
        data = json.loads(raw) if raw else {}
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for shape in VIDEO_SHAPES:
        f = picked_frame(data.get(shape))
        if f:
            out[shape] = f
    return out


def _render_video(**resizer):
    """Video (RM 2.0 slice 1b): the HyperFrames projects on top, the Video Resizer section below.
    /video and /video-resizer render the same page; /video-resizer opens on the resizer."""
    return render_template("video.html", projects=_video_projects(),
                           moods=list(_frame_tokens().get("moods", {}).keys()),
                           canvases=["reel", "wide", "square"], message=request.args.get("m"),
                           videos_dir=VIDEOS_DIR, open_resizer=request.endpoint == "video_resizer_page",
                           **resizer)


@app.route("/video-resizer", methods=["GET", "POST"])
def video_resizer_page():
    # Find available videos in videos/ folder
    existing_videos = []
    if VIDEO_DIR.exists():
        for p in sorted(VIDEO_DIR.iterdir()):
            if p.suffix.lower() in VIDEO_EXTENSIONS:
                existing_videos.append(p.name)

    export_groups = _build_video_export_groups()
    results = None
    all_warnings = []
    selected_focal = "center"
    frames = {}

    # Load releases for metadata dropdown
    release_options = [
        {"slug": r["slug"], "title": r["metadata"]["title"], "type": r["metadata"]["release_type"]}
        for r in list_releases()
    ]
    preselected_release = request.args.get("release", "")

    if request.method == "POST":
        focal = request.form.get("focal", "center")
        selected_focal = focal
        selected_templates = request.form.getlist("templates")
        frames = _video_frames(request.form.get("frames", ""))
        trim_start_str = request.form.get("trim_start", "").strip()
        trim_end_str = request.form.get("trim_end", "").strip()

        trim_start = float(trim_start_str) if trim_start_str else None
        trim_end = float(trim_end_str) if trim_end_str else None

        # Determine source video
        source_file = request.files.get("upload")
        source_path = None

        if source_file and source_file.filename:
            ext = Path(source_file.filename).suffix.lower()
            mime = (source_file.content_type or "").lower()
            is_video_ext = ext in VIDEO_EXTENSIONS
            is_video_mime = mime.startswith("video/")
            if not is_video_ext and not is_video_mime:
                flash(f"Not a video file ({source_file.filename}). Drop a video from Photos or Finder.", "error")
                return _render_video(presets=VIDEO_PRESETS, picked=_picked_templates(),
                    existing_videos=existing_videos,
                    focal_points=VIDEO_FOCAL_POINTS,
                    export_groups=export_groups,
                    results=None, warnings=None,
                    selected_focal=selected_focal)
            VIDEO_DIR.mkdir(parents=True, exist_ok=True)
            # Ensure saved file has a proper video extension
            if not is_video_ext and is_video_mime:
                # Photos app may give generic name -- use .mov for QuickTime, .mp4 otherwise
                new_ext = ".mov" if "quicktime" in mime else ".mp4"
                stem = secure_filename(Path(source_file.filename).stem) or "upload"
                safe_name = stem + new_ext
            else:
                safe_name = secure_filename(source_file.filename) or "upload"
            dest = VIDEO_DIR / safe_name
            source_file.save(str(dest))
            source_path = dest
        else:
            existing = request.form.get("existing_video", "")
            if existing:
                source_path = _safe_existing_path(VIDEO_DIR, existing)

        if not source_path or not source_path.exists():
            flash("No video selected.", "error")
            return _render_video(presets=VIDEO_PRESETS, picked=_picked_templates(),
                existing_videos=existing_videos,
                focal_points=VIDEO_FOCAL_POINTS,
                export_groups=export_groups,
                results=None, warnings=None,
                selected_focal=selected_focal)

        # Build metadata dict (opt-in)
        metadata = None
        metadata_mode = request.form.get("metadata_mode", "none")
        if metadata_mode == "release":
            release_slug = request.form.get("metadata_release", "").strip()
            if release_slug:
                from metadata_utils import metadata_from_release
                metadata = metadata_from_release(release_slug)
        elif metadata_mode == "manual":
            from metadata_utils import metadata_from_flags
            meta_title = request.form.get("meta_title", "").strip()
            meta_artist = request.form.get("meta_artist", "").strip()
            meta_copyright = request.form.get("meta_copyright", "").strip()
            meta_description = request.form.get("meta_description", "").strip()
            meta_genre = request.form.get("meta_genre", "").strip()
            if any([meta_title, meta_artist, meta_copyright, meta_description, meta_genre]):
                metadata = metadata_from_flags(
                    title=meta_title, artist=meta_artist,
                    copyright_text=meta_copyright,
                    description=meta_description, genre=meta_genre,
                )

        # Run the video resizer
        try:
            from video_resizer import process_video, VIDEO_EXPORTS
            RESIZED_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
            if selected_templates:
                active_exports = [e for e in VIDEO_EXPORTS if e[0] in selected_templates]
            else:
                active_exports = VIDEO_EXPORTS
            raw_results = process_video(
                source_path, RESIZED_VIDEO_DIR,
                active_exports, focal,
                trim_start, trim_end,
                metadata=metadata, frames=frames,
            )
            results = []
            for r in raw_results:
                fname, w, h, size_kb, dur, cat, warns = r
                results.append({
                    "filename": fname,
                    "width": w,
                    "height": h,
                    "size_kb": size_kb,
                    "duration": dur,
                    "category": cat,
                })
                all_warnings.extend(warns)
            meta_note = " Metadata embedded." if metadata else ""
            flash(f"Exported {len(results)} video(s).{meta_note}", "success")
            subprocess.Popen(["open", str(RESIZED_VIDEO_DIR)])
        except Exception as e:
            flash(f"Video resize failed: {e}", "error")

    return _render_video(presets=VIDEO_PRESETS, picked=_picked_templates(),
        existing_videos=existing_videos,
        focal_points=VIDEO_FOCAL_POINTS,
        export_groups=export_groups,
        results=results,
        warnings=all_warnings if all_warnings else None,
        selected_focal=selected_focal,
        frames=frames, frames_json=json.dumps(frames) if frames else "",
        posted_video=request.form.get("existing_video", "") if request.method == "POST" else "",
        trim=(request.form.get("trim_start", ""), request.form.get("trim_end", "")) if request.method == "POST" else ("", ""),
        release_options=release_options,
        preselected_release=preselected_release,
    )


@app.route("/video-resizer/source/<path:name>")
def video_resizer_source(name):
    """A source video from videos/, for the preview on the Video Resizer page."""
    p = _safe_existing_path(VIDEO_DIR, name)
    if p is None or not p.is_file():
        abort(404)
    return send_from_directory(str(p.parent), p.name)
