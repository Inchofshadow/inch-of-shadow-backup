"""The Stats page's data: every metric grouped by track, with its sparkline from the snapshots,
its 30-day change and a light. No targets yet, so a light is a trend: growing, flat, falling, or
no data (Measure-03, 2026-09-27)."""
from __future__ import annotations

from datetime import datetime, timedelta

from stats.storage import get_manual_latest, get_overview, get_time_series

def bandcamp_sales() -> dict | None:
    """BC-01: the latest raw data sales report, summed for the Stats page. No buyer data."""
    try:
        from stats.bandcamp_import import parse_bandcamp_raw
        d = parse_bandcamp_raw()
    except Exception:
        return None
    if not d:
        return None
    short = lambda url: url.rsplit("/", 1)[-1].replace("-", " ").title() + (" (album)" if "/album/" in url else "")
    return {
        "sales": d["total_sales"], "net": d["net"], "gross": d["gross"],
        "paid_more": d["paid_more_count"], "first": d["first_sale"], "last": d["last_sale"],
        "releases": [(short(u), v["count"], v["net"]) for u, v in d["by_url"].items()],
        "referrers": [(k, v["count"]) for k, v in sorted(d["by_referrer"].items(), key=lambda kv: -kv[1]["count"])][:6],
        "campaigns": [(k, v["count"], v["net"]) for k, v in d["by_campaign"].items()],
        "file": d["csv_file"],
    }


HISTORY_DAYS = 400
WINDOW_DAYS = 30

# track key, track name, metrics: (metric key, label, gate?)  gate = counts in the on-pace line
TRACKS = [
    ("instagram", "Instagram", [
        ("followers", "Followers", True),
        ("ratio", "Followers to following", True),
        ("recent_reach", "Reach, recent posts", True),
        ("recent_likes", "Likes, recent posts", False),
        ("recent_comments", "Comments, recent posts", False),
        ("media_count", "Posts", False),
    ]),
    ("soundcloud", "SoundCloud", [
        ("followers", "Followers", True),
        ("total_plays", "Plays", True),
        ("total_likes", "Likes", False),
        ("total_reposts", "Reposts", False),
        ("track_count", "Tracks", False),
    ]),
    ("youtube", "YouTube", [
        ("subscribers", "Subscribers", True),
        ("total_views", "Views", True),
        ("total_likes", "Likes", False),
        ("video_count", "Videos", False),
    ]),
    ("spotify", "Spotify", [
        ("followers", "Followers", True),
        ("catalog_size", "Releases on Spotify", False),
    ]),
]
MANUAL = [("bandcamp", "Bandcamp"), ("beatport", "Beatport")]   # Apple Music off 2026-10-21: never filled in (Amir)

# each platform's own colour, and its mark as an SVG path on a 24x24 box (Beatport has none we own:
# a letter mark stands in until a real path is added)
PLATFORMS = {
    "instagram":   {"colour": "#E4405F", "path": 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z'},
    "soundcloud":  {"colour": "#FF5500", "path": 'M11.56 8.87V17h8.76c1.85 0 3.35-1.67 3.35-3.73 0-2.06-1.5-3.73-3.35-3.73-.37 0-.73.07-1.06.2C18.87 6.78 16.48 4.5 13.56 4.5c-.95 0-1.85.27-2.63.74V17h.63V8.87zM0 13.5v3c0 .28.22.5.5.5s.5-.22.5-.5v-3c0-.28-.22-.5-.5-.5s-.5.22-.5.5zm2-2v5c0 .28.22.5.5.5s.5-.22.5-.5v-5c0-.28-.22-.5-.5-.5s-.5.22-.5.5zm2-1v6c0 .28.22.5.5.5s.5-.22.5-.5v-6c0-.28-.22-.5-.5-.5s-.5.22-.5.5zm2-1v8c0 .28.22.5.5.5s.5-.22.5-.5v-8c0-.28-.22-.5-.5-.5s-.5.22-.5.5zm2-.5v9c0 .28.22.5.5.5s.5-.22.5-.5v-9c0-.28-.22-.5-.5-.5s-.5.22-.5.5z'},
    "youtube":     {"colour": "#FF0000", "path": 'M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z'},
    "spotify":     {"colour": "#1DB954", "path": 'M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z'},
    "bandcamp":    {"colour": "#629AA9", "path": "M0 18.75l7.437-13.5H24l-7.438 13.5H0z"},
    "beatport":    {"colour": "#94D500", "path": "", "letter": "B"},
    "apple_music": {"colour": "#FA2D48", "path": "M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"},
}
MANUAL_FIELDS = [("followers", "Followers"), ("plays", "Plays or streams"), ("sales", "Sales"), ("revenue", "Revenue")]


def fmt(v) -> str:
    if v is None:
        return "no data"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return f"{v:,}"


def sparkline(series: list[dict], w: int = 120, h: int = 32) -> str:
    """SVG polyline points for the series, or '' when there is nothing to draw."""
    vals = [p["value"] for p in series if isinstance(p.get("value"), (int, float))]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    step = (w - 2) / (len(vals) - 1)
    return " ".join(f"{1 + i * step:.1f},{h - 2 - (v - lo) / span * (h - 4):.1f}" for i, v in enumerate(vals))


def change(series: list[dict], days: int = WINDOW_DAYS) -> tuple:
    """(delta over the last `days`, the number of days actually covered) or (None, 0)."""
    if len(series) < 2:
        return None, 0
    last = series[-1]
    last_d = datetime.strptime(last["date"], "%Y-%m-%d")
    cutoff = last_d - timedelta(days=days)
    before = [p for p in series if datetime.strptime(p["date"], "%Y-%m-%d") <= cutoff]
    base = before[-1] if before else series[0]     # the last reading at or before the window, else the oldest
    if base is last:
        return None, 0
    covered = (last_d - datetime.strptime(base["date"], "%Y-%m-%d")).days
    return last["value"] - base["value"], covered


def light_for(delta, covered: int, value) -> tuple[str, str]:
    if value is None:
        return "none", "no data"
    if delta is None:
        return "none", "one reading, no trend yet"
    span = f"in {covered} days" if covered != WINDOW_DAYS else "in 30 days"
    if isinstance(delta, float):
        text = f"{delta:+.2f} {span}"
    else:
        text = f"{delta:+,} {span}"
    if delta > 0:
        return "green", text
    if delta == 0:
        return "amber", f"flat {span}"
    return "red", text


def _metric(track: str, key: str, label: str, gate: bool, platforms: dict) -> dict:
    data = platforms.get(track) or {}
    if key == "ratio":
        f = get_time_series(track, "followers", HISTORY_DAYS)
        g = get_time_series(track, "following", HISTORY_DAYS)
        by_date = {p["date"]: p["value"] for p in g if p["value"]}
        series = [{"date": p["date"], "value": round(p["value"] / by_date[p["date"]], 2)} for p in f if p["date"] in by_date]
        value = series[-1]["value"] if series else None
        delta, covered = change(series)
        light, text = light_for(delta, covered, value)
        if value is not None:                     # the one metric with a floor: never under 1:1
            light = "green" if value >= 1.0 else "red"
            text = f"floor 1.0 · {text}"
    else:
        series = get_time_series(track, key, HISTORY_DAYS)
        value = data.get(key)
        if value is None and series:              # the API stopped answering: keep the last reading, say when
            last = series[-1]
            return {"key": key, "label": label, "gate": gate, "value": fmt(last["value"]), "light": "none",
                    "light_text": f"no data since {last['date']}", "points": sparkline(series), "as_of": last["date"]}
        delta, covered = change(series)
        light, text = light_for(delta, covered, value)
    if not gate and value is not None:
        light = "quiet"
    return {"key": key, "label": label, "gate": gate, "value": fmt(value), "light": light, "light_text": text,
            "points": sparkline(series), "as_of": series[-1]["date"] if series else ""}


def build() -> dict:
    overview = get_overview()
    platforms = overview.get("platforms", {})
    tracks = []
    for tkey, tname, metrics in TRACKS:
        tracks.append({"key": tkey, "name": tname, "metrics": [_metric(tkey, k, l, g, platforms) for k, l, g in metrics],
                       **PLATFORMS[tkey]})
    manual = []
    for mkey, mname in MANUAL:
        entry = get_manual_latest(mkey)
        manual.append({"key": mkey, "name": mname, "entry": entry,
                       "fields": [(f, l, (entry or {}).get(f)) for f, l in MANUAL_FIELDS],
                       "sales": bandcamp_sales() if mkey == "bandcamp" else None, **PLATFORMS[mkey]})
    gates = [m for t in tracks for m in t["metrics"] if m["gate"]]
    score = {c: sum(1 for m in gates if m["light"] == c) for c in ("green", "amber", "red", "none")}
    score["total"] = len(gates)
    synced = overview.get("last_synced") or ""
    days_ago = None
    if synced:
        try:
            days_ago = (datetime.now() - datetime.strptime(synced[:10], "%Y-%m-%d")).days
        except ValueError:
            pass
    return {"tracks": tracks, "manual": manual, "score": score, "last_synced": synced[:10], "synced_days_ago": days_ago}
