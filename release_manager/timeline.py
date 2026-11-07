"""
release_manager/timeline.py
-----------------------------
Timeline computation — works backwards (and forwards) from a release date.

Milestones are a loose guide, not strict gates.
Multiple can be completed in any order.

days_before > 0  = pre-release (counted back from release date)
days_before == 0 = release day
days_before < 0  = post-release (counted forward from release date)
"""

from __future__ import annotations

from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Default timeline template (days_before from release date)
# ---------------------------------------------------------------------------

DEFAULT_TIMELINE: list[dict] = [
    # Pre-release (days counted back from release Friday)
    #                                label (full, timeline/checklist)                     short (calendar pill)
    {"id": "metadata_filled",       "label": "Metadata filled (credits, genre tags)",  "short": "Metadata",          "days_before": 53,  "category": "metadata"},
    {"id": "distributor_submit",    "label": "Submit to Symphonic",                    "short": "Submit",            "days_before": 39,  "category": "distribution"},
    {"id": "distributor_approved",  "label": "Distributor approved / live on DSPs",    "short": "Approved",          "days_before": 32,  "category": "distribution"},
    {"id": "spotify_pitch",         "label": "Spotify editorial pitch submitted",      "short": "Spotify pitch",     "days_before": 28,  "category": "promotion"},
    {"id": "blog_premiere_pitch",   "label": "Pitch blog premieres",                   "short": "Blog pitch",        "days_before": 25,  "category": "promotion"},
    {"id": "bandcamp_setup",        "label": "Bandcamp upload + pre-order live",       "short": "Bandcamp",          "days_before": 18,  "category": "distribution"},
    {"id": "presave_promo",         "label": "Pre-save links + promo campaign",        "short": "Pre-save",          "days_before": 11,  "category": "promotion"},
    {"id": "early_links",           "label": "Send early links to personal contacts",  "short": "Early links",       "days_before": 4,   "category": "promotion"},
    {"id": "premiere_live",         "label": "Blog premiere goes live",                "short": "Premiere",          "days_before": 1,   "category": "promotion"},
    {"id": "release_day",           "label": "Release day",                            "short": "RELEASE",           "days_before": 0,   "category": "release"},

    # Post-release
    {"id": "dj_promos_sent",        "label": "DJ promos sent (bulk)",                  "short": "DJ promos",         "days_before": -4,  "category": "post_release"},
    {"id": "spotify_check",         "label": "Spotify saves / retention check (72h)",  "short": "Spotify check",     "days_before": -3,  "category": "post_release"},
    {"id": "platform_links",        "label": "All platform links collected",           "short": "Links",             "days_before": -5,  "category": "post_release"},
    {"id": "dj_followup",           "label": "DJ promo follow-up",                     "short": "DJ follow-up",      "days_before": -11, "category": "post_release"},
    {"id": "charts_check",          "label": "Charts check (Beatport / Traxsource)",   "short": "Charts",            "days_before": -12, "category": "post_release"},
    {"id": "artist_pick_rotate",    "label": "Rotate Spotify Artist Pick",             "short": "Artist Pick",       "days_before": -14, "category": "post_release"},
    {"id": "stats_review",          "label": "Stats review + update SI contact scores","short": "Stats review",      "days_before": -25, "category": "post_release"},
]


# ---------------------------------------------------------------------------
# Bandcamp Friday dates (first Friday of each month, 2026)
# ---------------------------------------------------------------------------

BANDCAMP_FRIDAYS_2026 = [
    "2026-01-02", "2026-02-06", "2026-03-06", "2026-04-03",
    "2026-05-01", "2026-06-05", "2026-07-03", "2026-08-07",
    "2026-09-04", "2026-10-02", "2026-11-06", "2026-12-04",
]


# ---------------------------------------------------------------------------
# Compute timeline
# ---------------------------------------------------------------------------

def compute_timeline(
    release_date: str,
    template: list[dict] | None = None,
) -> list[dict]:
    """Compute concrete dates from release_date and template.

    Parameters
    ----------
    release_date : str
        YYYY-MM-DD format.
    template : list[dict], optional
        Override the default timeline milestones.

    Returns
    -------
    list[dict]
        Each entry has: id, label, days_before, date, category, done.
    """
    tmpl = template or DEFAULT_TIMELINE
    rd = datetime.strptime(release_date, "%Y-%m-%d")
    result = []
    for m in tmpl:
        days = m.get("days_before", m.get("weeks_before", 0) * 7)
        milestone_date = rd - timedelta(days=days)
        result.append({
            "id":           m["id"],
            "label":        m["label"],
            "short":        m.get("short", m["label"]),
            "days_before":  days,
            "weeks_before": days // 7 if days >= 0 else -((-days) // 7),  # backward compat
            "date":         milestone_date.strftime("%Y-%m-%d"),
            "category":     m.get("category", ""),
            "done":         False,
        })
    return result


def recompute_dates(
    timeline: list[dict],
    release_date: str,
) -> list[dict]:
    """Recompute dates after a release_date change, preserving done states."""
    rd = datetime.strptime(release_date, "%Y-%m-%d")
    for m in timeline:
        days = m.get("days_before", m.get("weeks_before", 0) * 7)
        milestone_date = rd - timedelta(days=days)
        m["date"] = milestone_date.strftime("%Y-%m-%d")
    return timeline


def migrate_timeline(
    existing: list[dict],
    release_date: str,
) -> list[dict]:
    """Migrate an old timeline to the new template, preserving done states.

    Any milestone in DEFAULT_TIMELINE that is missing from `existing`
    gets added.  Done states for matching IDs are preserved.
    """
    done_map: dict[str, tuple[bool, str]] = {}
    for m in existing:
        done_map[m["id"]] = (m.get("done", False), m.get("done_date", ""))

    fresh = compute_timeline(release_date)
    for m in fresh:
        if m["id"] in done_map:
            m["done"] = done_map[m["id"]][0]
    return fresh


# ---------------------------------------------------------------------------
# Bandcamp Friday helper
# ---------------------------------------------------------------------------

def nearest_bandcamp_friday(release_date: str) -> dict | None:
    """Return info about the nearest Bandcamp Friday if within 7 days."""
    rd = datetime.strptime(release_date, "%Y-%m-%d")
    for bcf_str in BANDCAMP_FRIDAYS_2026:
        bcf = datetime.strptime(bcf_str, "%Y-%m-%d")
        delta = abs((bcf - rd).days)
        if delta <= 7 and delta > 0:
            return {
                "date": bcf_str,
                "days_away": (bcf - rd).days,  # negative = before release, positive = after
            }
    return None


# ---------------------------------------------------------------------------
# Calendar grid helper
# ---------------------------------------------------------------------------

def calendar_grid_data(
    timeline: list[dict],
    release_date: str,
) -> dict:
    """Build calendar grid data for rendering a month-based view.

    Returns a dict with:
      - months: list of {year, month, month_name, weeks: [[day_cells]]}
      - Each day_cell: {day, date_str, is_today, is_release_day, items: [...], bandcamp_friday}
      - release_date: the release date string
    """
    rd = datetime.strptime(release_date, "%Y-%m-%d")
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # Build date -> items mapping
    date_items: dict[str, list[dict]] = {}
    for m in timeline:
        date_items.setdefault(m["date"], []).append(m)

    # Determine range: from earliest milestone to latest milestone
    all_dates = [datetime.strptime(m["date"], "%Y-%m-%d") for m in timeline]
    if not all_dates:
        return {"months": [], "release_date": release_date}

    start = min(all_dates).replace(day=1)
    end = max(all_dates)
    # Go to end of that month
    if end.month == 12:
        end = end.replace(year=end.year + 1, month=1, day=1)
    else:
        end = end.replace(month=end.month + 1, day=1)

    bcf_set = set(BANDCAMP_FRIDAYS_2026)
    months = []
    current = start

    while current < end:
        year = current.year
        month = current.month
        month_name = current.strftime("%B %Y")

        # Build weeks (Mon=0 start)
        import calendar
        cal = calendar.monthcalendar(year, month)
        weeks = []
        for week_row in cal:
            week = []
            for day_num in week_row:
                if day_num == 0:
                    week.append(None)
                else:
                    d = datetime(year, month, day_num)
                    ds = d.strftime("%Y-%m-%d")
                    cell = {
                        "day": day_num,
                        "date_str": ds,
                        "is_today": ds == today_str,
                        "is_release_day": ds == release_date,
                        "bandcamp_friday": ds in bcf_set,
                        "tasks": date_items.get(ds, []),
                    }
                    week.append(cell)
            weeks.append(week)

        months.append({
            "year": year,
            "month": month,
            "month_name": month_name,
            "weeks": weeks,
        })

        # Advance to next month
        if month == 12:
            current = datetime(year + 1, 1, 1)
        else:
            current = datetime(year, month + 1, 1)

    return {"months": months, "release_date": release_date}


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def next_deadline(
    timeline: list[dict],
    today: str | None = None,
) -> dict | None:
    """Return the next undone milestone, or None if all done."""
    today_dt = datetime.strptime(today, "%Y-%m-%d") if today else datetime.now()
    undone = [m for m in timeline if not m["done"]]
    if not undone:
        return None
    # Sort by date, return the earliest undone
    undone.sort(key=lambda m: m["date"])
    return undone[0]


def overdue_milestones(
    timeline: list[dict],
    today: str | None = None,
) -> list[dict]:
    """Return milestones past their date that are not done."""
    today_str = today or datetime.now().strftime("%Y-%m-%d")
    return [m for m in timeline if not m["done"] and m["date"] < today_str]


QUIET_AFTER_DAYS = 30   # a release this long past its date stops raising overdue items (refresh step 3)


def is_finished(release: dict, today: str | None = None) -> bool:
    """A release more than QUIET_AFTER_DAYS past its release date.

    Its undone milestones are history, not work: the audit of 2026-09-26 found the Dashboard
    opening on 16 overdue items from Farewell and The Deceiver, months after they were out.
    """
    rdate = release.get("release_date") or ""
    if not rdate:
        return False
    today_dt = datetime.strptime(today, "%Y-%m-%d") if today else datetime.now()
    try:
        return (today_dt - datetime.strptime(rdate, "%Y-%m-%d")).days > QUIET_AFTER_DAYS
    except ValueError:
        return False

