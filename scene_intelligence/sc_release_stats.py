"""Weekly SoundCloud release-stats pull (sc-weekly-release-stats task).

Replaces the task's inline `python3 -c` block (2026-09-11): inline code cannot
be pre-approved by a safe permission rule, so the Friday run stopped for a
click. One script = one rule.

Exactly one read-only /resolve GET per track, never a write to SoundCloud.
Local writes: a backup of each release JSON, then one datapoint appended to
outcomes.stats.soundcloud.timeseries (de-duplicated by date). Engagement code
and engagement state are never touched.

Usage:
    python3 scene_intelligence/sc_release_stats.py            # pull + log
    python3 scene_intelligence/sc_release_stats.py --dry-run  # pull + print only
"""
from __future__ import annotations

import argparse
import shutil
from datetime import date, datetime

try:
    import scene_intelligence.sc_engagement as sc
    from scene_intelligence.json_io import atomic_write_json, load_json_checked
except ImportError:
    import sc_engagement as sc  # type: ignore
    from json_io import atomic_write_json, load_json_checked  # type: ignore

RELEASES_DIR = sc.BASE_DIR / "releases"

TRACKS = [
    ("the-deceiver-single",
     "https://soundcloud.com/inch-of-shadow/inch-of-shadow-the-deceiver",
     date(2026, 7, 10)),
    ("farewell-single",
     "https://soundcloud.com/inch-of-shadow/inch-of-shadow-farewell",
     date(2026, 5, 15)),
]

FIELDS = ("plays", "likes", "reposts", "comments", "downloads")


def fetch_track(url: str) -> dict | None:
    """One read-only /resolve call. None when SoundCloud returns nothing."""
    d = sc.sc_client_get("/resolve", params={"url": url})
    if not d or not isinstance(d, dict):
        return None
    return {
        "plays":     d.get("playback_count"),
        "likes":     d.get("likes_count") or d.get("favoritings_count"),
        "reposts":   d.get("reposts_count"),
        "comments":  d.get("comment_count"),
        "downloads": d.get("download_count"),
    }


def make_point(stats: dict, released: date, now: datetime) -> dict:
    return {
        "as_of": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "days_since_release": (now.date() - released).days,
        **stats,
        "source": "sc_resolve_api_live",
    }


def append_point(slug: str, point: dict, now: datetime) -> tuple[bool, dict | None]:
    """Back up the release JSON, then append `point` unless its date is logged.

    Returns (appended, previous_point)."""
    path = RELEASES_DIR / f"{slug}.json"
    rel = load_json_checked(path, None, what=f"release {slug}")
    if rel is None:
        raise SystemExit(f"release file missing: {path}")
    series = (rel.setdefault("outcomes", {}).setdefault("stats", {})
              .setdefault("soundcloud", {}).setdefault("timeseries", []))
    prev = series[-1] if series else None
    if any(p.get("date") == point["date"] for p in series):
        return False, prev
    shutil.copy2(path, RELEASES_DIR /
                 f"{slug}.bak.{now:%Y%m%d_%H%M%S}_sc_stats.json")
    series.append(point)
    atomic_write_json(path, rel)
    return True, prev


def _delta(now_v, prev_v) -> str:
    if now_v is None or prev_v is None:
        return "n/a"
    d = now_v - prev_v
    return f"{d:+d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Pull and print; write nothing.")
    args = ap.parse_args()
    now = datetime.now()

    print(f"{'track':<22}{'age':>5}  " + "  ".join(f"{f:>12}" for f in FIELDS[:3])
          + "  status")
    for slug, url, released in TRACKS:
        stats = fetch_track(url)
        if stats is None:
            print(f"{slug:<22}  NO DATA (resolve returned nothing, nothing logged)")
            continue
        point = make_point(stats, released, now)
        if args.dry_run:
            appended, prev = False, None
            status = "dry-run"
        else:
            appended, prev = append_point(slug, point, now)
            status = "logged" if appended else "already logged today"
        cells = []
        for f in FIELDS[:3]:
            d = _delta(point[f], prev.get(f) if prev else None)
            cells.append(f"{point[f]!s:>5} ({d:>4})")
        print(f"{slug:<22}{point['days_since_release']:>5}  "
              + "  ".join(f"{c:>12}" for c in cells) + f"  {status}")
        if prev:
            print(f"{'':<22}       delta vs {prev.get('date')} "
                  f"(day {prev.get('days_since_release')})")


if __name__ == "__main__":
    main()
