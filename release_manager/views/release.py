"""
release_manager/views/release.py
--------------------------------
Release area module (RM 2.0 slice 7, plans/strategy/rm2-dry-run-2026-11-06.md): Home at /
(endpoint dashboard, home.html since slice 10, section 1b of the dry run), the release pages
(/release/*, the clip pack, the Make block), the release JSON API and the artwork resizer
(/artwork-resizer, linked from the fmt_cover row of the Make block). Routes register on the shared
app from core.py, so the endpoint names are unchanged. webapp.py imports this module and re-exports
the names. Tests that patch list_releases, artwork_url_for or PROJECT_ROOT for these routes patch
this module, since the routes read its globals.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from flask import (
    render_template, request, redirect, url_for, flash, jsonify, abort,
)
from werkzeug.utils import secure_filename

from release_manager.models import (
    RELEASE_TYPES, ALL_PLATFORMS, DISTRIBUTION_STATUSES,
    make_slug, validate_date, new_release_dict, new_track_dict, validate_release,
)
from release_manager.storage import (
    load_release, save_release, list_releases, release_exists, unique_slug, delete_release,
)
from release_manager.timeline import (
    compute_timeline, recompute_dates, next_deadline, overdue_milestones,
    migrate_timeline, nearest_bandcamp_friday, calendar_grid_data, is_finished,
)
from release_manager.checklist import (
    generate_checklist, mark_done, mark_undone, migrate_checklist,
    checklist_progress, overdue_items, _CHECKLIST_TO_TIMELINE,
    CHECKLIST_TOOLTIPS,
)
from release_manager import clips as _clips
from release_manager.core import (
    app, PROJECT_ROOT, ARTWORK_DIR, RESIZED_DIR, ARTWORK_EXTENSIONS, SOCIAL_LINKS,
    save_genre, artwork_url_for, _safe_existing_path, ARTWORK_PRESETS, _picked_templates,
)
from release_manager.views.work import CONTROL_PANEL_FILE
from release_manager.views.studio import _effects_for_release
from release_manager.views.shoot import EDITS_DIR


# ---------------------------------------------------------------------------
# Home (the Dashboard until slice 10) and the release pages
# ---------------------------------------------------------------------------

def _dashboard_lines() -> dict:
    """The four lines at the top of the Dashboard (Machine-14): next release, board, backup, drive."""
    now = datetime.now()
    nxt = None
    for rel in list_releases():
        rd = rel.get("release_date") or ""
        try:
            days = (datetime.strptime(rd, "%Y-%m-%d").date() - now.date()).days
        except ValueError:
            continue
        if days >= 0 and (nxt is None or days < nxt["days"]):
            nxt = {"title": rel["metadata"].get("title", rel["slug"]), "slug": rel["slug"], "date": rd, "days": days}
    board = None
    try:
        tickets = json.loads(CONTROL_PANEL_FILE.read_text())["tickets"]
        # Done tickets leave the board (Amir, 2026-11-06) and live in the archive file next to it.
        archive = CONTROL_PANEL_FILE.with_name("tickets-done-archive.json")
        archived = json.loads(archive.read_text())["tickets"] if archive.exists() else []
        done = sum(1 for t in tickets if t.get("status") == "done") + len(archived)
        board = {"done": done, "total": len(tickets) + len(archived),
                 "in_progress": sum(1 for t in tickets if t.get("status") == "in-progress")}
    except (OSError, ValueError, KeyError):
        pass
    backup = None
    try:
        b = json.loads((PROJECT_ROOT / "plans" / "control-panel" / "backups.json").read_text())["backups"]
        if b:
            last = max(b, key=lambda x: x["date"])
            backup = {"date": last["date"], "days": (now - datetime.strptime(last["date"], "%Y-%m-%d")).days}
    except (OSError, ValueError, KeyError):
        pass
    drive = Path("/Volumes/Intenso").is_dir()
    return {"next": nxt, "board": board, "backup": backup, "drive": drive}


_BUCKET_ORDER = {"now": 0, "next": 1, "routine": 2, "parked": 3}


def _names_amir(blocked_on) -> bool:
    """blocked_on is a string in plans/tickets.json and a list of ticket ids on the Control Panel."""
    items = blocked_on if isinstance(blocked_on, list) else [blocked_on or ""]
    return any("amir" in str(b).lower() for b in items)


def _home_verdict() -> dict:
    """Block 1: the score-board verdict line (the same build the Stats page renders)."""
    from release_manager import score_board
    try:
        return {"line": score_board.build()["score"]["line"], "error": None}
    except Exception as e:                       # noqa: BLE001 - bad board data must not take down Home
        return {"line": "", "error": str(e) or type(e).__name__}


def _home_tickets() -> dict:
    """Blocks 2 and 3 from plans/tickets.json and plans/control-panel/tickets.json: the now
    tickets by area, the next count, the Control Panel open count, and the open tickets that
    wait on Amir (who amir, or blocked_on naming him) from both files."""
    from release_manager.views.work import TICKETS_FILE
    out = {"areas": [], "next": 0, "cp_open": None, "decisions": [], "tickets_error": None, "cp_error": None}
    tickets, labels = [], {}
    try:
        data = json.loads(TICKETS_FILE.read_text(encoding="utf-8"))
        tickets = [t for t in data.get("tickets", []) if t.get("status") != "done"]
        labels = data.get("areas") or {}
        now = [t for t in tickets if t.get("bucket") == "now"]
        for key, label in labels.items():
            rows = [t for t in now if (t.get("area") or t.get("section")) == key]
            if rows:
                out["areas"].append({"label": label, "tickets": rows})
        rest = [t for t in now if (t.get("area") or t.get("section")) not in labels]
        if rest:
            out["areas"].append({"label": "Other", "tickets": rest})
        out["next"] = sum(1 for t in tickets if t.get("bucket") == "next")
    except (OSError, ValueError, AttributeError) as e:
        out["tickets_error"] = str(e)
    cp = []
    try:
        cp = [t for t in json.loads(CONTROL_PANEL_FILE.read_text(encoding="utf-8")).get("tickets", [])
              if t.get("status") != "done"]
        out["cp_open"] = len(cp)
    except (OSError, ValueError, AttributeError) as e:
        out["cp_error"] = str(e)
    for source, rows in (("tickets", tickets), ("control panel", cp)):
        for t in rows:
            if t.get("who") == "amir" or _names_amir(t.get("blocked_on")):
                out["decisions"].append(dict(t, source=source))
    out["decisions"].sort(key=lambda t: _BUCKET_ORDER.get(t.get("bucket", ""), 1))
    # How a ticket is shown to Amir: "🎵 Release 2", never the stored id (CLAUDE.md, area rule).
    from release_manager.tickets import area_label
    for group in out["areas"]:
        group["tickets"] = [dict(t, shown=area_label(t, labels)) for t in group["tickets"]]
    out["decisions"] = [dict(t, shown=area_label(t, labels)) for t in out["decisions"]]
    return out


def _home_review_count() -> int | None:
    """The Review page's needs-you count, read only (no refresh, nothing written)."""
    from release_manager import review as _review
    try:
        return _review.build_view(_review.load_all())["counts"]["needs-you"]
    except Exception:                            # noqa: BLE001 - a broken review block must not take down Home
        return None


@app.route("/")
def dashboard():
    """Home (RM 2.0 slice 10): verdict line, now by area, decisions waiting on Amir, next release
    (finished releases under Out), social links, then the backup and drive footer."""
    releases = list_releases()
    open_releases, out_releases = [], []
    all_overdue = []
    titles = {}
    for rel in releases:
        cl = rel.get("checklist", [])
        title = (rel.get("metadata") or {}).get("title") or rel["slug"]
        titles[rel["slug"]] = title
        if is_finished(rel):                     # a release long out stays quiet
            out_releases.append({"slug": rel["slug"], "title": title, "date": rel.get("release_date", "")})
            continue
        done, total = checklist_progress(cl)
        open_releases.append({"slug": rel["slug"], "title": title, "date": rel.get("release_date", ""),
                              "done": done, "total": total})
        for m in overdue_milestones(rel.get("timeline", [])):
            all_overdue.append({"slug": rel["slug"], **m})
    out_releases.sort(key=lambda r: r["date"], reverse=True)

    briefing = _daily_briefing()
    today = datetime.now()
    have = {(e.get("slug"), e.get("due_date")) for e in briefing["overdue"]}
    for m in sorted(all_overdue, key=lambda d: d["date"]):   # overdue milestones join the checklist's overdue list,
        if (m["slug"], m["date"]) in have:                     # unless the checklist already shows that task (same release, same day)
            continue
        have.add((m["slug"], m["date"]))
        briefing["overdue"].append({"label": m["label"], "release": titles.get(m["slug"], m["slug"]), "slug": m["slug"],
                                    "due_date": m["date"],
                                    "days_late": (today - datetime.strptime(m["date"], "%Y-%m-%d")).days})
    briefing["overdue"].sort(key=lambda x: x["due_date"])
    lines = _dashboard_lines()
    nxt = (lines.get("next") or {}).get("slug")
    open_releases.sort(key=lambda r: (r["slug"] != nxt, r["date"] or "9999"))
    return render_template("home.html",
        verdict=_home_verdict(),
        work=_home_tickets(),
        review_count=_home_review_count(),
        open_releases=open_releases,
        out_releases=out_releases,
        overdue=briefing["overdue"],
        lines=lines,
        social_links=SOCIAL_LINKS,
    )


@app.route("/release/new", methods=["GET", "POST"])
def release_new():
    if request.method == "GET":
        return render_template("release_form.html", release=None)

    title = request.form.get("title", "").strip()
    rtype = request.form.get("release_type", "EP")
    date = request.form.get("release_date", "").strip()
    genre = request.form.get("genre_primary", "").strip()
    genre2 = request.form.get("genre_secondary", "").strip()
    description = request.form.get("description", "").strip()

    errors = []
    if not title:
        errors.append("Title is required.")
    if rtype not in RELEASE_TYPES:
        errors.append("Invalid release type.")
    if not date or not validate_date(date):
        errors.append("Valid release date (YYYY-MM-DD) is required.")
    if errors:
        flash(" ".join(errors), "error")
        return render_template("release_form.html", release=None), 400

    slug = unique_slug(make_slug(title, rtype))
    rel = new_release_dict(title, rtype, date, genre, genre2, description=description)
    rel["slug"] = slug
    rel["timeline"] = compute_timeline(date)
    rel["lane"] = "full"  # songs are the main line; set "light" by hand for an electronic drop
    rel["checklist"] = generate_checklist(rel["timeline"], lane=rel["lane"])
    save_release(rel)
    save_genre(genre)
    save_genre(genre2)

    flash(f"Release '{title}' created.", "success")
    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>")
def release_detail(slug, _clip_errors=None, _clip_draft=None):
    rel = load_release(slug)
    if not rel:
        abort(404)

    # --- Migrate old timeline/checklist to new template if needed ---
    tl = rel.get("timeline", [])
    cl = rel.get("checklist", [])
    tl_ids = {m["id"] for m in tl}
    cl_ids = {item["id"] for item in cl}
    migrated = False

    # Check if timeline needs migration (missing new milestones)
    from release_manager.timeline import DEFAULT_TIMELINE
    expected_tl_ids = {m["id"] for m in DEFAULT_TIMELINE}
    if expected_tl_ids - tl_ids:
        tl = migrate_timeline(tl, rel["release_date"])
        rel["timeline"] = tl
        migrated = True

    from release_manager.checklist import expected_ids
    expected_cl_ids = expected_ids(rel.get("lane"))
    if expected_cl_ids - cl_ids:
        cl = migrate_checklist(cl, tl, lane=rel.get("lane"))
        rel["checklist"] = cl
        migrated = True

    if migrated:
        save_release(rel)

    done, total = checklist_progress(cl)
    warnings = validate_release(rel)

    # Category ordering for display
    cat_order = ["metadata", "distribution", "promotion", "formats", "youtube", "post_release"]
    cat_labels = {
        "metadata": "Metadata",
        "distribution": "Distribution",
        "promotion": "Promotion",
        "formats": "Formats (the fixed set)",
        "youtube": "YouTube",
        "post_release": "Post-Release",
    }
    categories = {}
    for item in cl:
        cat = item["category"]
        categories.setdefault(cat, []).append(item)

    ordered_categories = []
    for cat_key in cat_order:
        if cat_key in categories:
            ordered_categories.append((cat_labels.get(cat_key, cat_key.title()), categories[cat_key]))

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Calendar grid and Bandcamp Friday
    cal_grid = calendar_grid_data(tl, rel["release_date"])
    bcf = nearest_bandcamp_friday(rel["release_date"])

    # Split timeline for display: pre-release and post-release
    tl_pre = [m for m in tl if m["weeks_before"] >= 0]
    tl_post = [m for m in tl if m["weeks_before"] < 0]

    return render_template("release_detail.html",
        rel=rel,
        meta=rel["metadata"],
        dist=rel["distribution"],
        done=done, total=total,
        pct=(done * 100 // total) if total else 0,
        ordered_categories=ordered_categories,
        make=_make_block(rel),
        timeline=tl,
        tl_pre=tl_pre,
        tl_post=tl_post,
        next_dl=next_deadline(tl),
        overdue_tl=[m["id"] for m in overdue_milestones(tl)],
        overdue_cl=[i["id"] for i in overdue_items(cl)],
        warnings=warnings,
        today=today_str,
        tooltips=CHECKLIST_TOOLTIPS,
        artwork_url=artwork_url_for(slug),
        cal_grid=cal_grid,
        bandcamp_friday=bcf,
        archive_refs=_archive_refs_for(slug),
        title_font=_title_font_for(rel),
        release_effects=_effects_for_release(rel),
        clip_rows=_clips.page_rows(rel),
        clip_errors=_clip_errors or {},
        clip_draft=_clip_draft or {},
        clip_platforms=_clips.PLATFORMS,
        clip_kinds=_clips.KINDS,
        clip_canvas_rules=_clips.CANVAS_RULES,
    )


def _title_font_for(rel: dict) -> dict | None:
    """The fonts.json record a release's brand.title_font names, with its @font-face rule."""
    try:
        from release_manager import fonts_page as _f
        r = _f.for_release(_f.load(PROJECT_ROOT), (rel.get("brand") or {}).get("title_font", ""))
        if r is None:
            return None
        x = _f.shape(r)
        x["faces"] = _f.face_rules(r, lambda fid, f: url_for("font_file", fid=fid, rel=f))
        return x
    except Exception:
        return None


def _archive_refs_for(slug: str) -> list[dict]:
    """Shadow Archive entries Amir tagged with this release (never a 500 if the index is off)."""
    try:
        from release_manager import archive as _arch
        return _arch.for_release(_arch.load_index(PROJECT_ROOT), slug)
    except Exception:
        return []


@app.route("/api/release/<slug>/delete", methods=["POST"])
def api_release_delete(slug):
    """Permanently delete a release."""
    if not release_exists(slug):
        return jsonify({"error": f"Release '{slug}' not found"}), 404
    delete_release(slug)
    return jsonify({"ok": True})


@app.route("/release/<slug>/edit", methods=["GET", "POST"])
def release_edit(slug):
    rel = load_release(slug)
    if not rel:
        abort(404)

    if request.method == "GET":
        return render_template("release_form.html", release=rel)

    meta = rel["metadata"]
    changed = []

    title = request.form.get("title", "").strip()
    if title and title != meta["title"]:
        meta["title"] = title
        changed.append("title")

    rtype = request.form.get("release_type", "").strip()
    if rtype and rtype in RELEASE_TYPES and rtype != meta["release_type"]:
        meta["release_type"] = rtype
        changed.append("type")

    genre = request.form.get("genre_primary", "").strip()
    if genre != meta.get("genre_primary", ""):
        meta["genre_primary"] = genre
        changed.append("genre")

    genre2 = request.form.get("genre_secondary", "").strip()
    if genre2 != meta.get("genre_secondary", ""):
        meta["genre_secondary"] = genre2
        changed.append("genre2")

    desc = request.form.get("description", "").strip()
    if desc != meta.get("description", ""):
        meta["description"] = desc
        changed.append("description")

    copyright_val = request.form.get("copyright", "").strip()
    if copyright_val and copyright_val != meta.get("copyright", ""):
        meta["copyright"] = copyright_val
        changed.append("copyright")

    catalog = request.form.get("catalog_number", "").strip()
    if catalog != meta.get("catalog_number", ""):
        meta["catalog_number"] = catalog
        changed.append("catalog")

    distributor = request.form.get("distributor", "").strip()
    if distributor != rel["distribution"].get("distributor", ""):
        rel["distribution"]["distributor"] = distributor
        changed.append("distributor")

    upc = request.form.get("upc", "").strip()
    if upc != rel["distribution"].get("upc", ""):
        rel["distribution"]["upc"] = upc
        changed.append("upc")

    dist_id = request.form.get("distributor_id", "").strip()
    if dist_id != rel["distribution"].get("distributor_id", ""):
        rel["distribution"]["distributor_id"] = dist_id
        changed.append("distributor_id")

    dist_status = request.form.get("dist_status", "").strip()
    if dist_status and dist_status in DISTRIBUTION_STATUSES:
        if dist_status != rel["distribution"].get("status", "draft"):
            rel["distribution"]["status"] = dist_status
            changed.append("status")

    submitted_date = request.form.get("submitted_date", "").strip()
    if submitted_date != rel["distribution"].get("submitted_date", ""):
        rel["distribution"]["submitted_date"] = submitted_date
        changed.append("submitted_date")

    approved_date = request.form.get("approved_date", "").strip()
    if approved_date != rel["distribution"].get("approved_date", ""):
        rel["distribution"]["approved_date"] = approved_date
        changed.append("approved_date")

    live_date = request.form.get("live_date", "").strip()
    if live_date != rel["distribution"].get("live_date", ""):
        rel["distribution"]["live_date"] = live_date
        changed.append("live_date")

    dist_notes = request.form.get("dist_notes", "").strip()
    if dist_notes != rel["distribution"].get("notes", ""):
        rel["distribution"]["notes"] = dist_notes
        changed.append("dist_notes")

    notes = request.form.get("notes", "").strip()
    if notes != rel.get("notes", ""):
        rel["notes"] = notes
        changed.append("notes")

    # Date change triggers timeline recompute
    new_date = request.form.get("release_date", "").strip()
    if new_date and new_date != rel["release_date"]:
        if not validate_date(new_date):
            flash(f"Invalid date: {new_date}", "error")
            return render_template("release_form.html", release=rel), 400
        rel["release_date"] = new_date
        recompute_dates(rel["timeline"], new_date)
        tl_dates = {m["id"]: m["date"] for m in rel["timeline"]}
        for item in rel["checklist"]:
            timeline_id = _CHECKLIST_TO_TIMELINE.get(item["id"], "")
            if timeline_id:
                item["due_date"] = tl_dates.get(timeline_id, item["due_date"])
        changed.append("date + timeline")

    if changed:
        save_release(rel)
        save_genre(genre)
        save_genre(genre2)
        flash(f"Updated: {', '.join(changed)}", "success")
    else:
        flash("No changes made.", "info")

    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>/track/new", methods=["GET", "POST"])
def track_new(slug):
    rel = load_release(slug)
    if not rel:
        abort(404)

    if request.method == "GET":
        return render_template("track_form.html", rel=rel, track=None)

    title = request.form.get("title", "").strip()
    if not title:
        flash("Track title is required.", "error")
        return render_template("track_form.html", rel=rel, track=None), 400

    bpm_str = request.form.get("bpm", "").strip()
    bpm = float(bpm_str) if bpm_str else 0

    number = len(rel["tracks"]) + 1
    track = new_track_dict(
        number=number,
        title=title,
        bpm=bpm,
        key=request.form.get("key", "").strip(),
        duration=request.form.get("duration", "").strip(),
        genre_primary=request.form.get("genre_primary", "").strip() or rel["metadata"].get("genre_primary", ""),
        genre_secondary=request.form.get("genre_secondary", "").strip() or rel["metadata"].get("genre_secondary", ""),
    )
    rel["tracks"].append(track)
    save_release(rel)
    save_genre(track["genre_primary"])
    save_genre(track["genre_secondary"])

    flash(f"Track {number}: '{title}' added.", "success")
    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>/track/<int:num>/edit", methods=["GET", "POST"])
def track_edit(slug, num):
    rel = load_release(slug)
    if not rel:
        abort(404)

    track = None
    for t in rel["tracks"]:
        if t["number"] == num:
            track = t
            break
    if not track:
        abort(404)

    if request.method == "GET":
        return render_template("track_form.html", rel=rel, track=track)

    changed = []
    title = request.form.get("title", "").strip()
    if title and title != track["title"]:
        track["title"] = title
        changed.append("title")

    bpm_str = request.form.get("bpm", "").strip()
    if bpm_str:
        track["bpm"] = float(bpm_str)
        changed.append("bpm")

    key = request.form.get("key", "").strip()
    if key != track.get("key", ""):
        track["key"] = key
        changed.append("key")

    duration = request.form.get("duration", "").strip()
    if duration != track.get("duration", ""):
        track["duration"] = duration
        changed.append("duration")

    isrc = request.form.get("isrc", "").strip()
    if isrc != track.get("isrc", ""):
        track["isrc"] = isrc
        changed.append("isrc")

    g1 = request.form.get("genre_primary", "").strip()
    if g1 != track.get("genre_primary", ""):
        track["genre_primary"] = g1
        changed.append("genre")

    g2 = request.form.get("genre_secondary", "").strip()
    if g2 != track.get("genre_secondary", ""):
        track["genre_secondary"] = g2
        changed.append("genre2")

    # Credits
    for field in ("producer", "mixer", "mastering", "writer"):
        val = request.form.get(field, "").strip()
        if val and val != track["credits"].get(field, ""):
            track["credits"][field] = val
            changed.append(field)

    if changed:
        save_release(rel)
        save_genre(g1)
        save_genre(g2)
        flash(f"Track {num} updated: {', '.join(changed)}", "success")
    else:
        flash("No changes made.", "info")

    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>/track/<int:num>/delete", methods=["POST"])
def track_delete(slug, num):
    rel = load_release(slug)
    if not rel:
        abort(404)

    removed = None
    for i, t in enumerate(rel["tracks"]):
        if t["number"] == num:
            removed = rel["tracks"].pop(i)
            break
    if not removed:
        abort(404)

    # Renumber
    for i, t in enumerate(rel["tracks"]):
        t["number"] = i + 1

    save_release(rel)
    flash(f"Track '{removed['title']}' deleted.", "success")
    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>/links", methods=["POST"])
def release_links(slug):
    rel = load_release(slug)
    if not rel:
        abort(404)

    changed = []
    for platform in ALL_PLATFORMS:
        val = request.form.get(platform, "").strip()
        if val != rel["platform_links"].get(platform, ""):
            rel["platform_links"][platform] = val
            changed.append(platform)

    if changed:
        save_release(rel)
        flash(f"Links updated: {', '.join(changed)}", "success")
    else:
        flash("No changes made.", "info")

    return redirect(url_for("release_detail", slug=slug))


@app.route("/release/<slug>/clips/<int:num>", methods=["POST"])
def release_clips(slug, num):
    """Clip pack (System 79, S10): edit one track's timecodes or its used_in log.

    action=save      the per-track form (seconds, not frames)
    action=add_used  one used_in row; a second upload of the same cut on one platform is refused
    action=remove_used  drop row `index` (0-based)
    Errors render the release page again with the messages inline, nothing saved.
    """
    rel = load_release(slug)
    if not rel:
        abort(404)
    if _clips.track_clips(rel, num) is None:
        abort(404)

    action = request.form.get("action", "save")
    form = {k: request.form.get(k, "") for k in request.form}
    if action == "save":
        errors = _clips.update_track_clips(rel, num, form)
        what = "clip pack saved"
    elif action == "add_used":
        errors = _clips.add_used_in(rel, num, form)
        what = "used_in row added"
    elif action == "remove_used":
        try:
            index = int(request.form.get("index", ""))
        except ValueError:
            abort(400)
        errors = _clips.remove_used_in(rel, num, index)
        what = "used_in row removed"
    else:
        abort(400)

    if errors:
        draft = {"action": action, "form": form}
        return release_detail(slug, _clip_errors={num: errors}, _clip_draft={num: draft}), 400

    _clips.save_release_clips(rel)
    flash(f"Track {num}: {what}", "success")
    return redirect(url_for("release_detail", slug=slug) + f"#clips-{num}")


@app.route("/release/<slug>/artwork", methods=["POST"])
def release_artwork(slug):
    rel = load_release(slug)
    if not rel:
        abort(404)

    file = request.files.get("artwork")
    if not file or not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("release_detail", slug=slug))

    ext = Path(file.filename).suffix.lower()
    if ext not in ARTWORK_EXTENSIONS:
        flash(f"Unsupported format: {ext}", "error")
        return redirect(url_for("release_detail", slug=slug))

    ARTWORK_DIR.mkdir(parents=True, exist_ok=True)
    dest = ARTWORK_DIR / f"{slug}{ext}"
    file.save(str(dest))

    flash("Artwork uploaded.", "success")
    return redirect(url_for("release_detail", slug=slug))


# ---------------------------------------------------------------------------
# Artwork Resizer page
# ---------------------------------------------------------------------------

FOCAL_POINTS = [
    "top-left", "top", "top-right",
    "left", "center", "right",
    "bottom-left", "bottom", "bottom-right",
]


def _build_artwork_export_groups():
    """Build grouped artwork export specs, merging identical-size duplicates."""
    from artwork_resizer import EXPORTS
    labels = {
        "release_spotify": "Spotify",
        "release_applemusic": "Apple Music",
        "release_bandcamp": "Bandcamp",
        "release_beatport": "Beatport",
        "profile_beatport": "Profile",
        "release_soundcloud": "SoundCloud",
        "release_web_thumb": "Web Thumbnail",
        "profile_spotify_avatar": "Avatar",
        "profile_spotify_banner": "Banner",
        "profile_applemusic": "Profile",
        "profile_youtube_banner": "Banner",
        "profile_youtube_avatar": "Avatar",
        "thumb_youtube": "Thumbnail",
        "thumb_youtube_4k": "Thumbnail 4K",
        "thumb_youtube_shorts": "Shorts Thumbnail",
        "profile_bandcamp_avatar": "Avatar",
        "profile_bandcamp_header": "Header",
        "profile_soundcloud_banner": "Banner",
        "profile_soundcloud_avatar": "Avatar",
        "social_instagram_post": "Post",
        "social_instagram_story": "Story",
        "social_instagram_portrait": "Post 4:5",
        "social_instagram_grid": "Post 3:4 (grid)",
        "social_instagram_reel_cover": "Reel Cover",
    }
    groups = []
    seen_cat: dict[str, int] = {}
    for template, w, h, category, platform in EXPORTS:
        if category not in seen_cat:
            seen_cat[category] = len(groups)
            groups.append({"name": category, "_map": {}, "_order": []})
        group = groups[seen_cat[category]]
        key = (w, h)
        if key not in group["_map"]:
            group["_map"][key] = {
                "templates": [template],
                "labels": [labels.get(template, template)],
                "width": w, "height": h,
            }
            group["_order"].append(key)
        else:
            group["_map"][key]["templates"].append(template)
            lbl = labels.get(template, template)
            if lbl not in group["_map"][key]["labels"]:
                group["_map"][key]["labels"].append(lbl)
    # Flatten to template-friendly list
    result = []
    for group in groups:
        exports = []
        for key in group["_order"]:
            entry = group["_map"][key]
            exports.append({
                "templates": entry["templates"],
                "label": ", ".join(entry["labels"]),
                "width": entry["width"],
                "height": entry["height"],
            })
        result.append({"name": group["name"], "exports": exports})
    return result


@app.route("/artwork-resizer", methods=["GET", "POST"])
def artwork_resizer_page():
    # Find available images in artwork/ folder
    existing_images = []
    if ARTWORK_DIR.exists():
        for p in sorted(ARTWORK_DIR.iterdir()):
            if p.suffix.lower() in ARTWORK_EXTENSIONS:
                existing_images.append(p.name)
    if EDITS_DIR.exists():                                   # copies made in the photo editor
        for p in sorted(EDITS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.suffix.lower() in ARTWORK_EXTENSIONS:
                existing_images.append(f"edits/{p.name}")

    export_groups = _build_artwork_export_groups()
    results = None
    preview_file = None
    selected_focal = "center"
    selected_fmt = "jpg"

    # Load releases for metadata dropdown
    release_options = [
        {"slug": r["slug"], "title": r["metadata"]["title"], "type": r["metadata"]["release_type"]}
        for r in list_releases()
    ]
    # Check for ?release= query param (linked from release detail page)
    preselected_release = request.args.get("release", "")

    # Preserve form values across POST
    posted_meta = {}

    if request.method == "POST":
        focal = request.form.get("focal", "center")
        fmt = request.form.get("format", "jpg")
        selected_focal = focal
        selected_fmt = fmt
        # Capture metadata fields so they survive re-render
        posted_meta = {
            "mode": request.form.get("metadata_mode", "none"),
            "release": request.form.get("metadata_release", ""),
            "existing_image": request.form.get("existing_image", ""),
            "title": request.form.get("meta_title", ""),
            "artist": request.form.get("meta_artist", ""),
            "copyright": request.form.get("meta_copyright", ""),
            "genre": request.form.get("meta_genre", ""),
            "description": request.form.get("meta_description", ""),
        }
        raw_templates = request.form.getlist("templates")
        # Flatten comma-separated values (merged groups send multiple IDs)
        selected_templates = []
        for t in raw_templates:
            selected_templates.extend(t.split(","))

        # Determine source image
        source_file = request.files.get("upload")
        source_path = None

        if source_file and source_file.filename:
            # Uploaded file — save to artwork/
            ext = Path(source_file.filename).suffix.lower()
            mime = (source_file.content_type or "").lower()
            is_image_ext = ext in ARTWORK_EXTENSIONS
            is_image_mime = mime.startswith("image/")
            if not is_image_ext and not is_image_mime:
                flash(f"Not an image file ({source_file.filename}). Drop an image from Photos or Finder.", "error")
                return render_template("artwork_resizer.html", presets=ARTWORK_PRESETS,
                    cover_mode=request.form.get("cover_mode") == "1", picked=_picked_templates(),
                    existing_images=existing_images,
                    focal_points=FOCAL_POINTS,
                    export_groups=export_groups,
                    results=None, preview_file=None,
                    selected_focal=selected_focal, selected_fmt=selected_fmt,
                    release_options=release_options,
                    preselected_release=preselected_release,
                    posted_meta=posted_meta)
            ARTWORK_DIR.mkdir(parents=True, exist_ok=True)
            # Photos app may give generic name without proper extension
            if not is_image_ext and is_image_mime:
                new_ext = ".heic" if "heic" in mime else ".jpg"
                stem = secure_filename(Path(source_file.filename).stem) or "upload"
                safe_name = stem + new_ext
            else:
                safe_name = secure_filename(source_file.filename) or "upload"
            dest = ARTWORK_DIR / safe_name
            source_file.save(str(dest))
            source_path = dest
        else:
            # Pick from existing
            existing = request.form.get("existing_image", "")
            if existing.startswith("edits/"):
                source_path = _safe_existing_path(EDITS_DIR, existing[len("edits/"):])
            elif existing:
                source_path = _safe_existing_path(ARTWORK_DIR, existing)

        if not source_path or not source_path.exists():
            flash("No image selected.", "error")
            return render_template("artwork_resizer.html", presets=ARTWORK_PRESETS,
                cover_mode=request.form.get("cover_mode") == "1", picked=_picked_templates(),
                existing_images=existing_images,
                focal_points=FOCAL_POINTS,
                export_groups=export_groups,
                results=None, preview_file=None,
                selected_focal=selected_focal, selected_fmt=selected_fmt,
                release_options=release_options,
                preselected_release=preselected_release,
                posted_meta=posted_meta)

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

        # Run the resizer
        try:
            from artwork_resizer import process_image, EXPORTS, clean_stem
            RESIZED_DIR.mkdir(parents=True, exist_ok=True)
            if selected_templates:
                active_exports = [e for e in EXPORTS if e[0] in selected_templates]
            else:
                active_exports = EXPORTS
            import artwork_resizer as _ar
            _ar.COVER_MODE = request.form.get("cover_mode") == "1"
            try:
                results = process_image(
                    source_path, RESIZED_DIR,
                    active_exports,
                    focal, None, None, fmt, False,
                    metadata=metadata,
                )
            finally:
                _ar.COVER_MODE = False
            # Find preview grid (uses cleaned stem)
            cleaned = clean_stem(source_path.stem)
            for p in RESIZED_DIR.iterdir():
                if p.name.startswith("_preview_") and cleaned in p.name:
                    preview_file = p.name
                    break
            # Count non-square crops where focal point matters
            cropped_count = sum(1 for r in results if r[1] != r[2])
            focal_note = ""
            if focal != "center":
                focal_note = f" Focal '{focal}' applied to {cropped_count} non-square crop(s)."
            elif cropped_count:
                focal_note = f" {cropped_count} non-square crop(s) used center focal."
            meta_note = " Metadata embedded." if metadata else ""
            flash(f"Resized {len(results)} images.{focal_note}{meta_note}", "success")
            subprocess.Popen(["open", str(RESIZED_DIR)])
        except Exception as e:
            flash(f"Resize failed: {e}", "error")

    return render_template("artwork_resizer.html", presets=ARTWORK_PRESETS,
        cover_mode=request.form.get("cover_mode") == "1", picked=_picked_templates(),
        existing_images=existing_images,
        focal_points=FOCAL_POINTS,
        export_groups=export_groups,
        results=results,
        preview_file=preview_file,
        selected_focal=selected_focal,
        selected_fmt=selected_fmt,
        release_options=release_options,
        preselected_release=preselected_release,
        posted_meta=posted_meta,
    )


# ---------------------------------------------------------------------------
# API routes (JSON, called by JavaScript)
# ---------------------------------------------------------------------------

@app.route("/api/release/<slug>/check/<task_id>", methods=["POST"])
def api_check(slug, task_id):
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": "not found"}), 404

    if mark_done(rel["checklist"], task_id):
        for m in rel["timeline"]:
            if m["id"] == task_id:
                m["done"] = True
        save_release(rel)
        done, total = checklist_progress(rel["checklist"])
        return jsonify({"ok": True, "done": done, "total": total})

    return jsonify({"error": "task not found"}), 404


@app.route("/api/release/<slug>/uncheck/<task_id>", methods=["POST"])
def api_uncheck(slug, task_id):
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": "not found"}), 404

    if mark_undone(rel["checklist"], task_id):
        for m in rel["timeline"]:
            if m["id"] == task_id:
                m["done"] = False
        save_release(rel)
        done, total = checklist_progress(rel["checklist"])
        return jsonify({"ok": True, "done": done, "total": total})

    return jsonify({"error": "task not found"}), 404


@app.route("/api/release/<slug>/validate")
def api_validate(slug):
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": "not found"}), 404

    warnings = validate_release(rel)
    return jsonify({"warnings": warnings, "count": len(warnings)})


@app.route("/api/release/<slug>/metadata")
def api_release_metadata(slug):
    """Return title/artist/copyright/description/genre for a release (used by resizer pages)."""
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": "not found"}), 404
    meta = rel.get("metadata", {})
    genre_parts = [meta.get("genre_primary", ""), meta.get("genre_secondary", "")]
    return jsonify({
        "title":       meta.get("title", ""),
        "artist":      meta.get("artist", ""),
        "copyright":   meta.get("copyright", ""),
        "description": meta.get("description", ""),
        "genre":       " / ".join(p for p in genre_parts if p),
    })


# ---------------------------------------------------------------------------
# The overdue list on Home: checklist items of unfinished releases past their due date
# (the promotion log read and the campaign follow-ups went in RM 2.0 slice 10).
# ---------------------------------------------------------------------------

def _daily_briefing() -> dict:
    """Overdue checklist items across releases. A release past its date plus 30 days
    (`is_finished`) stays quiet here. Home adds the overdue timeline milestones."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    overdue = []
    for rel in list_releases():
        if is_finished(rel):
            continue
        title = (rel.get("metadata") or {}).get("title") or rel["slug"]
        for item in rel.get("checklist", []):
            due = item.get("due_date", "")
            if item.get("done") or not due or due >= today_str:
                continue
            try:
                late = (now - datetime.strptime(due, "%Y-%m-%d")).days
            except ValueError:
                continue
            overdue.append({"release": title, "slug": rel["slug"], "label": item["label"],
                            "due_date": due, "category": item.get("category", ""), "days_late": late})
    overdue.sort(key=lambda x: x["due_date"])
    return {"overdue": overdue}


# ---------------------------------------------------------------------------
# The Make block on a release page (Machine-13): for each object of the fixed set, is
# there a file on disk yet, which one, and the command that makes it (docs/brand/machine.md).
# ---------------------------------------------------------------------------

_MAKE = {   # checklist id: (folders to look in, filename hint, the command)
    "fmt_cover":              (["artwork", "resized"], "", "design, then: python3 artwork_resizer.py <cover> --cover"),
    "fmt_canvas":             (["resized_video"], "canvas_vertical_spotify", "HyperFrames loop, then: python3 video_resizer.py <render> --only spotify"),
    "fmt_process_reel":       (["resized_video", "../videos"], "reel_instagram", "footage + HyperFrames, then: python3 video_resizer.py <render> --reel"),
    "fmt_release_reel_hooks": (["resized_video", "../videos"], "reel_instagram", "one HyperFrames project, the hook as a variable, render --batch, then --reel"),
    "fmt_shorts":             (["resized_video"], "shorts_youtube", "python3 video_resizer.py <render> --reel (the Shorts file is one of the three)"),
    "fmt_story_set":          (["generated_images"], "story", "three 1080x1920 frames from the shoot or the cover (A or B, his call per release)"),
    "fmt_reveal_carousel":    (["generated_images", "resized"], "carousel", "python3 shoot_pull.py <id> --format carousel, then artwork_resizer.py"),
    "fmt_face_reel":          (["resized_video", "../videos"], "reel_instagram", "footage + HyperFrames, then --reel"),
    "fmt_lyric_reel":         (["resized_video", "../videos"], "reel_instagram", "HyperFrames music-to-video, then --reel"),
    "fmt_youtube_visualizer": (["../youtube/renders"], "", "HyperFrames landscape-4k -q delivery; cover thumbnail from artwork_resizer.py --cover"),
    "fmt_presave_asset":      (["generated_images", "resized"], "presave", "image tool or Canva, 1080x1920 + 1080x1440"),
}


def _make_block(rel: dict) -> list[dict]:
    from release_manager.checklist import FORMAT_CHECKLIST, LANES
    lane = rel.get("lane")
    if lane not in LANES:
        return []
    wanted = ("light",) if lane == "light" else LANES
    slug = rel["slug"].lower()
    title = (rel.get("metadata", {}).get("title") or "").lower()
    keys = {k for k in (slug, slug.replace("-", "_"), slug.replace("-", ""), slug.replace("-single", ""),
                        title, title.replace(" ", "_"), title.replace(" ", "-"), title.replace(" ", "")) if len(k) > 2}
    out = []
    for f in FORMAT_CHECKLIST:
        if f["lane"] not in wanted:
            continue
        folders, hint, how = _MAKE.get(f["id"], ([], "", ""))
        found = []
        for folder in folders:
            d = (PROJECT_ROOT / folder).resolve()
            if not d.is_dir():
                continue
            for p in d.iterdir():
                n = p.name.lower()
                if n.startswith(".") or (hint and hint not in n) or not any(k in n for k in keys):
                    continue
                found.append(str(p.relative_to(PROJECT_ROOT.parent)))
        out.append({"id": f["id"], "label": f["label"], "lane": f["lane"], "made": bool(found),
                    "files": sorted(found)[:6], "how": how})
    return out
