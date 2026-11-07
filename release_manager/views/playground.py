"""
release_manager/views/playground.py
-----------------------------------
Studio area module, part 3 (RM 2.0 slice 8, plans/strategy/rm2-dry-run-2026-11-06.md): the artwork
playground (Machine-21) and the Half the Night cover stages (wall, elements, ig-grid, layout, colours,
versions). The routes moved as they were. Routes register on the shared app from core.py, so the
endpoint names are unchanged. webapp.py imports this module and re-exports the names.
Tests that patch load_release / save_release / list_releases / PROJECT_ROOT for these routes patch
this module, since the routes read its globals.
"""

from __future__ import annotations

import sys
from datetime import datetime

from flask import render_template, request, redirect, url_for, jsonify, abort, send_file

from release_manager.core import app, PROJECT_ROOT
from release_manager.storage import load_release, save_release, list_releases
from release_manager.views.studio import _fonts, _font_file_url

# ---------------------------------------------------------------------------
# Artwork playground (Machine-21): looks, colour, accent and fonts on a release's base
# artwork, with Spotify / record / Instagram previews. Composes in the browser.
# ---------------------------------------------------------------------------
from release_manager import playground as _pg


@app.route("/playground")
def playground_index():
    rels = [r for r in list_releases() if ((r.get("brand") or {}).get("playground") or {}).get("base")]
    if len(rels) == 1:
        return redirect(url_for("playground_page", slug=rels[0]["slug"]))
    return render_template("playground.html", rel=None, rels=rels, looks=[], fonts=[], moods={}, accents=[], pg={})


@app.route("/playground/<slug>")
def playground_page(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    if rel is None or _pg.base_path(PROJECT_ROOT, rel) is None:
        abort(404)
    try:
        fonts = _pg.font_choices(_fonts.load(PROJECT_ROOT), _font_file_url)
    except Exception:
        fonts = []
    try:
        import subprocess, json as _json
        out = subprocess.run([sys.executable, str(PROJECT_ROOT.parent / ".claude/skills/brand/scripts/frame_tokens.py")],
                             capture_output=True, text=True, timeout=20).stdout
        moods = _json.loads(out).get("moods", {})
    except Exception:
        moods = {}
    rels = [r for r in list_releases() if ((r.get("brand") or {}).get("playground") or {}).get("base")]
    acl = _pg.accent_layer_path(PROJECT_ROOT, rel)
    return render_template("playground.html", rel=rel, rels=rels, looks=_pg.looks(), fonts=fonts, moods=moods,
                           accents=_pg.ACCENTS, pg=(rel.get("brand") or {}).get("playground") or {},
                           bver=_pg.file_version(_pg.base_path(PROJECT_ROOT, rel)), aver=_pg.file_version(acl),
                           has_accent_layer=acl is not None, covers=_pg.covers(PROJECT_ROOT, slug),
                           ramp=_pg.RAMPS.get(slug))


@app.route("/playground/<slug>/image")
def playground_image(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    cover = request.args.get("cover") or ""
    if cover:
        base = _pg.cover_path(PROJECT_ROOT, slug, cover) if rel else None
    else:
        base = _pg.base_path(PROJECT_ROOT, rel) if rel else None
    if base is None:
        abort(404)
    look = request.args.get("look") or ""
    wpx = request.args.get("w") or ""
    try:
        if look:
            scale = int(request.args.get("scale") or 1) if (request.args.get("scale") or "1").isdigit() else 1
            out = _pg.look_image(base, look, scale)
        else:
            out = base
        if wpx.isdigit():
            return send_file(_pg.sized(out, int(wpx)), mimetype="image/jpeg", max_age=3600)
        if not look:
            return send_file(base, max_age=60)
        return send_file(out, mimetype="image/png", max_age=3600)
    except ValueError:
        abort(404)


@app.route("/playground/<slug>/overlay")
def playground_overlay(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    p = _pg.overlay_path(PROJECT_ROOT, slug, request.args.get("cover") or "")
    if p is None:
        abort(404)
    return send_file(p, mimetype="image/png", max_age=60)


@app.route("/playground/<slug>/wall")
def playground_wall(slug):
    """Effects wall: every look at once on one cover, one wet knob for all (Amir, 2026-11-04)."""
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    if rel is None or _pg.base_path(PROJECT_ROOT, rel) is None:
        abort(404)
    covers = _pg.covers(PROJECT_ROOT, slug)
    for c in covers:
        c["has_title"] = _pg.overlay_path(PROJECT_ROOT, slug, c["name"]) is not None
        c["v"] = _pg.file_version(_pg.cover_path(PROJECT_ROOT, slug, c["name"]))
    return render_template("playground_wall.html", rel=rel, looks=_pg.looks(), covers=covers,
                           ramp=_pg.RAMPS.get(slug), picks=_pg.WALL_PICKS.get(slug, []),
                           bver=_pg.file_version(_pg.base_path(PROJECT_ROOT, rel)),
                           igfeed=_pg.iggrid_feed(PROJECT_ROOT, slug))


@app.route("/api/playground/<slug>/wall-kept", methods=["GET", "POST"])
def playground_wall_kept(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            kept = _pg.wall_toggle(PROJECT_ROOT, slug, request.get_json(silent=True) or {}, datetime.now().strftime("%Y-%m-%d %H:%M"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"kept": kept})
    return jsonify({"kept": _pg.wall_kept(PROJECT_ROOT, slug)})


@app.route("/playground/<slug>/elements")
def playground_elements(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    if rel is None or _pg.element_path(PROJECT_ROOT, slug, "el-cream-none-none-keep-0.jpg") is None:
        abort(404)
    t = _pg.element_path(PROJECT_ROOT, slug, "el.title.png")
    return render_template("playground_elements.html", rel=rel, ver=_pg.file_version(t))


@app.route("/playground/<slug>/elements/img")
def playground_element_img(slug):
    p = _pg.element_path(PROJECT_ROOT, slug, request.args.get("n") or "")
    if p is None:
        abort(404)
    wpx = request.args.get("w") or ""
    if wpx.isdigit() and p.suffix == ".jpg":
        return send_file(_pg.sized(p, int(wpx)), mimetype="image/jpeg", max_age=3600)
    return send_file(p, max_age=60)


@app.route("/playground/<slug>/ig-grid")
def playground_iggrid(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    names = _pg.iggrid_files(PROJECT_ROOT, slug)
    if rel is None or not names:
        abort(404)
    vers = {n: _pg.file_version(_pg.iggrid_path(PROJECT_ROOT, slug, n)) for n in names}
    return render_template("playground_iggrid.html", rel=rel, names=names, vers=vers)


@app.route("/playground/<slug>/ig-grid/img")
def playground_iggrid_img(slug):
    p = _pg.iggrid_path(PROJECT_ROOT, slug, request.args.get("n") or "")
    if p is None:
        abort(404)
    return send_file(p, mimetype="image/jpeg", max_age=60)


@app.route("/playground/<slug>/layout")
def playground_layout(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    saves = _pg.colours_kept(PROJECT_ROOT, slug) if rel else []
    if not saves:
        abort(404)
    picks = _pg.colour_picks(PROJECT_ROOT, slug)
    return render_template("playground_layout.html", rel=rel, saves=saves, looks=_pg.looks(), hidden=_pg.wall_hidden(PROJECT_ROOT, slug),
                           pver={p: _pg.file_version(_pg.colour_path(PROJECT_ROOT, slug, p, "meta.json")) for p in picks},
                           igfeed=_pg.iggrid_feed(PROJECT_ROOT, slug))


@app.route("/playground/<slug>/layout/font")
def playground_layout_font(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    p = _pg.layout_font_path(PROJECT_ROOT, request.args.get("f") or "")
    if p is None:
        abort(404)
    return send_file(p, mimetype="font/ttf", max_age=86400)


@app.route("/playground/<slug>/layout/fx", methods=["POST"])
def playground_layout_fx(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        abort(404)
    try:
        out = _pg.look_on_bytes(request.get_data(cache=False) or b"", request.args.get("look") or "")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return send_file(_pg.sized(out, 1080), mimetype="image/jpeg", max_age=0)


@app.route("/playground/<slug>/layout/snap", methods=["POST"])
def playground_layout_snap(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        abort(404)
    try:
        _pg.layout_snap_save(PROJECT_ROOT, slug, int(request.args.get("n") or 0), request.get_data(cache=False) or b"")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True})


@app.route("/playground/<slug>/layout/extra")
def playground_layout_extra(slug):
    p = _pg.extra_path(PROJECT_ROOT, slug, request.args.get("n") or "")
    if p is None:
        abort(404)
    return send_file(p, mimetype="image/png", max_age=3600)


@app.route("/api/playground/<slug>/layouts-kept", methods=["GET", "POST"])
def playground_layouts_kept(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            kept = _pg.layouts_toggle(PROJECT_ROOT, slug, request.get_json(silent=True) or {}, datetime.now().strftime("%Y-%m-%d %H:%M"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"kept": kept})
    return jsonify({"kept": _pg.layouts_kept(PROJECT_ROOT, slug)})


@app.route("/api/playground/<slug>/elements-kept", methods=["GET", "POST"])
def playground_elements_kept(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            kept = _pg.elements_toggle(PROJECT_ROOT, slug, str((request.get_json(silent=True) or {}).get("name") or ""),
                                       datetime.now().strftime("%Y-%m-%d %H:%M"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"kept": kept})
    return jsonify({"kept": _pg.elements_kept(PROJECT_ROOT, slug)})


@app.route("/playground/<slug>/colours")
def playground_colours(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    picks = _pg.colour_picks(PROJECT_ROOT, slug) if rel else []
    if not picks:
        abort(404)
    t = _pg.element_path(PROJECT_ROOT, slug, "el.title.png")
    return render_template("playground_colours.html", rel=rel, picks=picks, ver=_pg.file_version(t),
                           pver={p: _pg.file_version(_pg.colour_path(PROJECT_ROOT, slug, p, "meta.json")) for p in picks})


@app.route("/playground/<slug>/colours/file")
def playground_colour_file(slug):
    p = _pg.colour_path(PROJECT_ROOT, slug, request.args.get("p") or "", request.args.get("f") or "")
    if p is None:
        abort(404)
    return send_file(p, max_age=60)


@app.route("/api/playground/<slug>/colours-kept", methods=["GET", "POST"])
def playground_colours_kept(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            kept = _pg.colours_toggle(PROJECT_ROOT, slug, request.get_json(silent=True) or {}, datetime.now().strftime("%Y-%m-%d %H:%M"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"kept": kept})
    return jsonify({"kept": _pg.colours_kept(PROJECT_ROOT, slug)})


@app.route("/api/playground/<slug>/wall-hidden", methods=["GET", "POST"])
def playground_wall_hidden(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            h = _pg.wall_hide_toggle(PROJECT_ROOT, slug, str((request.get_json(silent=True) or {}).get("look") or ""))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"hidden": h})
    return jsonify({"hidden": _pg.wall_hidden(PROJECT_ROOT, slug)})


@app.route("/api/playground/<slug>/fonts-hidden", methods=["GET", "POST"])
def playground_fonts_hidden(slug):
    if not _pg.SLUG.fullmatch(slug or "") or load_release(slug) is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        try:
            h = _pg.fonts_hide_toggle(PROJECT_ROOT, slug, str((request.get_json(silent=True) or {}).get("font") or ""))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"hidden": h})
    return jsonify({"hidden": _pg.fonts_hidden(PROJECT_ROOT, slug)})


@app.route("/playground/<slug>/accent")
def playground_accent(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    p = _pg.accent_layer_path(PROJECT_ROOT, rel) if rel else None
    if p is None:
        abort(404)
    return send_file(p, mimetype="image/png", max_age=60)


@app.route("/api/playground/<slug>/versions", methods=["GET", "POST"])
def playground_versions(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    if rel is None:
        return jsonify({"error": "unknown release"}), 404
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        try:
            _pg.save_version(rel, body.get("name", ""), body.get("state"), datetime.now().strftime("%Y-%m-%d %H:%M"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        save_release(rel)
    return jsonify({"versions": [{"name": v["name"], "saved": v.get("saved", ""), "state": v.get("state", {})} for v in _pg.versions(rel)]})


@app.route("/api/playground/<slug>/versions/delete", methods=["POST"])
def playground_version_delete(slug):
    if not _pg.SLUG.fullmatch(slug or ""):
        abort(404)
    rel = load_release(slug)
    if rel is None:
        return jsonify({"error": "unknown release"}), 404
    if not _pg.delete_version(rel, (request.get_json(silent=True) or {}).get("name", "")):
        return jsonify({"error": "no such version"}), 404
    save_release(rel)
    return jsonify({"ok": True})
