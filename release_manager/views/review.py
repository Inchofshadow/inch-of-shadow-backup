"""
release_manager/views/review.py
-------------------------------
Review module (RM 2.0 slice 9, plans/strategy/rm2-dry-run-2026-11-06.md section 1c; System 82,
card M10, schema in plans/review-flow-schema.md): the /review page, the item thumbnail and the
tick API over the review block of releases/<slug>.json. The routes moved from webapp.py as they
were. Routes register on the shared app from core.py, so the endpoint names (review_page,
review_thumb, review_tick) are unchanged. webapp.py imports this module and re-exports the names.
Nothing on this page moves, renames, deletes, posts or marks used. A held item cannot be approved.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from flask import render_template, request, jsonify, abort, send_file

from release_manager.core import app
from release_manager.storage import load_release


_REVIEW_DEMO = {}   # one in-memory demo release per process (?demo=1), never saved


def _review_demo_release():
    from release_manager import review as _review
    if "rel" not in _REVIEW_DEMO:
        import tempfile
        media = Path(tempfile.mkdtemp(prefix="review-demo-")) / "media"
        _REVIEW_DEMO["rel"] = _review.demo_release(media)
    return _REVIEW_DEMO["rel"]


@app.route("/review")
def review_page():
    """Items grouped by release, newest first; needs-you first with held on top.
    Filters ?release= and ?area=. A GET only writes when an approved file changed
    on disk (the item falls back to needs-you with the note)."""
    from release_manager import review as _review
    if request.args.get("demo") == "1":
        releases = [_review_demo_release()]
        demo = True
    else:
        releases = _review.load_all()
        for rel in releases:
            if _review.refresh(rel):
                _review.save_release_review(rel)
        demo = False
    view = _review.build_view(
        releases,
        release=request.args.get("release", "")[:80],
        area=request.args.get("area", "")[:20],
    )
    return render_template("review.html", view=view, demo=demo)


@app.route("/review/thumb/<slug>/<item_id>")
def review_thumb(slug, item_id):
    """A small JPEG of one recorded item (its path comes from the release JSON, never from the request)."""
    from release_manager import review as _review
    if request.args.get("demo") == "1":
        rel = _review_demo_release()
    else:
        rel = load_release(slug)
    if rel is None:
        abort(404)
    try:
        item = _review.get_item(rel, item_id)
    except _review.ReviewError:
        abort(404)
    data = _review.thumbnail_jpeg(item)
    if not data:
        abort(404)
    return send_file(BytesIO(data), mimetype="image/jpeg", max_age=300)


@app.route("/api/review/<slug>/<item_id>", methods=["POST"])
def review_tick(slug, item_id):
    """Amir's tick from the desktop page: {action: approve | change | drop, note, sha256}.
    approve needs the sha256 he saw; it is refused with "file changed after approval"
    when the file on disk differs, "hash mismatch" when the tick names another hash,
    and "held" when a chip fails. used, delete and anything else are not actions here."""
    from release_manager import review as _review
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action", ""))[:20]
    note = str(payload.get("note", "") or "")[:2000]
    sha256 = str(payload.get("sha256", "") or "")[:64]
    if action not in _review.TICK_ACTIONS:
        return jsonify({"ok": False, "error": "action must be approve, change or drop"}), 400
    rel = load_release(slug)
    if rel is None:
        return jsonify({"ok": False, "error": "unknown release"}), 404
    try:
        _review.get_item(rel, item_id)
    except _review.ReviewError:
        return jsonify({"ok": False, "error": "unknown item"}), 404
    try:
        item = _review.tick(rel, item_id, action, by="amir", via="rm", note=note, sha256=sha256)
    except _review.ReviewError as e:
        # a refused approve may have flagged the item (file changed): keep that record
        _review.save_release_review(rel)
        return jsonify({"ok": False, "error": str(e)}), 409
    _review.save_release_review(rel)
    return jsonify({"ok": True, "item": _review.item_view(rel, item)})
