"""
release_manager/views/stats.py
------------------------------
Stats area module (RM 2.0 slice 2, plans/strategy/rm2-dry-run-2026-11-06.md): the /stats page and
its forms, thumbnails and JSON API. Routes register on the shared app from core.py, so the
endpoint names (stats_page, api_stats_overview, ...) are unchanged. webapp.py imports this module.
"""

from __future__ import annotations

import re

from flask import (
    render_template, request, redirect,
    url_for, jsonify, abort, send_from_directory,
)

from release_manager.core import app, _safe_existing_path
from stats.collectors import collect_all
from stats.storage import (
    save_snapshot, list_snapshots,
    get_overview, get_time_series, save_manual_entry,
)
from stats.bandcamp_import import parse_bandcamp_csv



# ---------------------------------------------------------------------------
# Stats Dashboard (Tool 5)
# ---------------------------------------------------------------------------

@app.route("/stats")
def stats_page():
    """Stats: one on-pace line, then every metric by track with its sparkline and light (Measure-03)."""
    from release_manager.stats_tracks import build
    from stats.weekly_view import build as weekly_build    # G-06: the "This week" panel, read-only
    from release_manager import score_board
    board, board_error = None, None
    month = request.args.get("month", "")            # ?month=2026-11 shows the frozen month (stats/freeze.py, M11)
    month = month if re.fullmatch(r"\d{4}-\d{2}", month) else None
    try:
        board = score_board.build(month=month)
    except Exception as e:                       # noqa: BLE001 - bad board data must not take down the page
        board_error = str(e) or type(e).__name__
    return render_template("stats.html", s=build(), message=request.args.get("m"), weekly=weekly_build(),
                           board=board, board_error=board_error)


@app.route("/stats/thumb/<path:filename>")
def stats_thumb(filename):
    """Cover thumbnails for the This week panel, kept locally in generated_images/stats_thumbs/."""
    from stats.weekly_view import THUMBS
    f = _safe_existing_path(THUMBS, filename)
    if f is None:
        abort(404)
    return send_from_directory(str(f.parent), f.name)


@app.route("/stats/sync", methods=["POST"])
def stats_sync_form():
    """The Sync now button: collect from every platform API, save a snapshot, come back."""
    result = collect_all()
    filename = save_snapshot(result)
    errs = result.get("errors") or []
    msg = f"Synced: {filename}" + (f" · {len(errs)} platform(s) failed: " + "; ".join(str(e)[:80] for e in errs) if errs else "")
    return redirect(url_for("stats_page", m=msg))


@app.route("/stats/manual", methods=["POST"])
def stats_manual_form():
    """The typed-in numbers for the platforms without an API."""
    platform = (request.form.get("platform") or "").strip().lower()
    if platform not in ("bandcamp", "beatport", "apple_music"):
        abort(400)
    entry = {}
    for f in ("followers", "plays", "sales"):
        v = (request.form.get(f) or "").strip()
        if v:
            try:
                entry[f] = int(v)
            except ValueError:
                abort(400)
    v = (request.form.get("revenue") or "").strip()
    if v:
        try:
            entry["revenue"] = float(v)
        except ValueError:
            abort(400)
    if not entry:
        return redirect(url_for("stats_page", m="Nothing entered."))
    save_manual_entry(platform, entry)
    return redirect(url_for("stats_page", m=f"{platform} saved."))


@app.route("/api/stats/sync", methods=["POST"])
def api_stats_sync():
    """Trigger a fresh stats collection from all platform APIs."""
    result = collect_all()
    filename = save_snapshot(result)
    overview = get_overview()
    return jsonify({
        "ok": True,
        "filename": filename,
        "platforms": list(result["platforms"].keys()),
        "errors": result["errors"],
        "overview": overview,
    })


@app.route("/api/stats/overview")
def api_stats_overview():
    """Get the current overview (latest snapshot + manual entries)."""
    return jsonify(get_overview())


@app.route("/api/stats/time-series")
def api_stats_time_series():
    """Get time series data for a platform metric.

    Query params: platform, metric, days (default 30)
    """
    platform = request.args.get("platform", "")
    metric = request.args.get("metric", "")
    days = request.args.get("days", "30")
    try:
        days = int(days)
    except ValueError:
        days = 30
    if not platform or not metric:
        return jsonify({"error": "platform and metric required"}), 400
    series = get_time_series(platform, metric, days)
    return jsonify({"platform": platform, "metric": metric, "days": days, "data": series})


@app.route("/api/stats/manual-entry", methods=["POST"])
def api_stats_manual_entry():
    """Save a manual stats entry for Bandcamp, Beatport, or Apple Music."""
    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip().lower()
    if platform not in ("bandcamp", "beatport", "apple_music"):
        return jsonify({"error": "Platform must be bandcamp, beatport, or apple_music"}), 400

    allowed_fields = {"followers", "plays", "sales", "revenue", "chart_position", "notes",
                      "streams", "listeners", "shazams"}
    entry_data = {k: v for k, v in data.items() if k in allowed_fields and v != "" and v is not None}
    if not entry_data:
        return jsonify({"error": "No valid data fields provided"}), 400

    # Convert numeric fields
    for field in ("followers", "plays", "sales", "streams", "listeners", "shazams", "chart_position"):
        if field in entry_data:
            try:
                entry_data[field] = int(entry_data[field])
            except (ValueError, TypeError):
                return jsonify({"error": f"Invalid number for {field}"}), 400
    if "revenue" in entry_data:
        try:
            entry_data["revenue"] = float(entry_data["revenue"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid number for revenue"}), 400

    entry = save_manual_entry(platform, entry_data)
    return jsonify({"ok": True, "entry": entry})


@app.route("/api/stats/snapshots")
def api_stats_snapshots():
    """List all snapshots (metadata only, not full data)."""
    snapshots = list_snapshots()
    return jsonify([{
        "filename": s.get("_filename", ""),
        "timestamp": s.get("timestamp", ""),
        "platforms": list(s.get("platforms", {}).keys()),
    } for s in snapshots[:50]])


@app.route("/api/stats/bandcamp")
def api_stats_bandcamp():
    """Get parsed Bandcamp sales data from CSV export."""
    data = parse_bandcamp_csv()
    if data is None:
        return jsonify({"error": "No Bandcamp CSV found in data/bandcamp/"}), 404
    return jsonify(data)
