"""
stats/spotify_s4a.py
---------------------
Weekly Spotify for Artists numbers (2026-10-21). Spotify's public API returns no followers,
popularity or top tracks for this app, and Spotify for Artists has no API, so once a week (Monday,
before the 08:45 sync) a scheduled Claude session opens the Audience page in Amir's own Chrome,
picks the "7 days" view (Spotify's last 7 days with data, not a calendar week; the dates come
from the page), copies the page text, and this script pulls the numbers out of it. Read only:
the one click is the period view toggle; nothing is changed in his account.

Storage: stats_snapshots/spotify_s4a.json, one entry per week, keyed by the week's last day.

Usage (the Monday read saves the two page texts into generated_images/s4a_raw/ first):
    python3 stats/spotify_s4a.py --stats audience.txt [--home home.txt]
    python3 stats/spotify_s4a.py --show
    python3 stats/spotify_s4a.py --urls             # the two pages the Monday read opens
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "stats_snapshots" / "spotify_s4a.json"
ARTIST_ID = "5k4SyH7JRPMJe1RHYMI2CT"
AUDIENCE_URL = "https://artists.spotify.com/c/artist/" + ARTIST_ID + "/audience/stats"
HOME_URL = "https://artists.spotify.com/c/artist/" + ARTIST_ID + "/home"

METRICS = [("Listeners", "listeners"), ("Monthly active listeners", "monthly_active"), ("Streams", "streams"),
           ("Streams / Listener", "streams_per_listener"), ("Saves", "saves"), ("Playlist adds", "playlist_adds"),
           ("Followers", "followers")]
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


class ParseError(ValueError):
    pass


def _num(s: str) -> float | int:
    s = s.replace(",", "").strip()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KkMm]?)", s)
    if not m:
        raise ParseError(f"not a number: {s!r}")
    v = float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()]
    if m.group(2):                               # Spotify rounds big numbers (1.1K): keep a whole number
        return int(round(v))
    return int(v) if v == int(v) and "." not in m.group(1) else round(v, 2)


def _date(s: str) -> date:
    m = re.fullmatch(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})", s.strip())
    if not m or m.group(1) not in MONTHS:
        raise ParseError(f"not a date: {s!r}")
    return date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def parse_stats(text: str, expect_days: int | None = 7) -> dict:
    """The Audience page's 'Stats this period' block -> {period, metrics, changes}. expect_days=None
    accepts any period (the month pages of the backfill)."""
    m = re.search(r"Stats this period\s+([A-Z][a-z]{2} \d{1,2}, \d{4}) - ([A-Z][a-z]{2} \d{1,2}, \d{4})", text)
    if not m:
        raise ParseError("no 'Stats this period' dates on the page")
    start, end = _date(m.group(1)), _date(m.group(2))
    block = text[m.end():]
    values, changes = {}, {}
    for label, key in METRICS:
        mm = re.search(r"(?m)^" + re.escape(label) + r"[ \t]*\n[ \t]*([\d.,]+[ \t]*[KkMm]?)[ \t]*$(?:\n[ \t]*(-?[\d.]+)%)?", block)
        if mm:
            values[key] = _num(mm.group(1))
            if re.search(r"[KkMm]", mm.group(1)):
                values.setdefault("_rounded", []).append(key)
            if mm.group(2) is not None:              # no percentage line when nothing changed
                changes[key] = float(mm.group(2))
    if "listeners" not in values or "streams" not in values:
        raise ParseError("listeners or streams missing from the page text")
    if expect_days is not None and (end - start).days != expect_days - 1:
        raise ParseError(f"the page shows {start} to {end}, not a {expect_days}-day period")
    return {"start": start.isoformat(), "end": end.isoformat(), "metrics": values, "changes_pct": changes}


def parse_home(text: str) -> dict:
    """The Home page's 'Your top songs, Streams, Last 7 days' list -> {period, songs}."""
    m = re.search(r"Your top songs\s+Streams\s+Last 7 days\s+(\d{1,2})/(\d{1,2}) – (\d{1,2})/(\d{1,2})\s+(.*?)\s+See songs", text, re.S)
    if not m:
        raise ParseError("no top songs block on the home page")
    lines = [l.strip() for l in m.group(5).splitlines() if l.strip()]
    songs = []
    for title, n in zip(lines[0::2], lines[1::2]):
        try:
            songs.append({"title": title, "streams": _num(n)})
        except ParseError:
            break
    return {"from": f"{int(m.group(1)):02d}-{int(m.group(2)):02d}", "to": f"{int(m.group(3)):02d}-{int(m.group(4)):02d}",
            "songs": songs}


def load() -> dict:
    try:
        return json.loads(STORE.read_text())
    except (OSError, ValueError):
        return {"weeks": {}}


def save_week(stats: dict, home: dict | None = None) -> dict:
    data = load()
    metrics = dict(stats["metrics"])
    rounded = metrics.pop("_rounded", [])
    entry = {"start": stats["start"], "end": stats["end"], **metrics, "changes_pct": stats["changes_pct"],
             "read_at": datetime.now().isoformat(timespec="seconds"), "source": "Spotify for Artists, Audience, 7 days"}
    if rounded:
        entry["rounded"] = rounded
    if home and home.get("to") == stats["end"][5:]:           # only when the top songs are the same week
        entry["top_songs"] = home["songs"]
    data.setdefault("weeks", {})[stats["end"]] = {**data.get("weeks", {}).get(stats["end"], {}), **entry}
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(STORE)
    return data["weeks"][stats["end"]]


def save_backfill(texts: list[str]) -> dict:
    """The one-time backfill (2026-10-21): Audience pages opened one by one for past periods, read like
    the Monday read. A 7-day page becomes a week (a week already stored keeps its own entry); a page that
    spans a whole calendar month (or the start of the current one) becomes a month."""
    data = load()
    counts = {"weeks": 0, "months": 0, "skipped": 0}
    for text in texts:
        st = parse_stats(text, expect_days=None)
        start, end = date.fromisoformat(st["start"]), date.fromisoformat(st["end"])
        metrics = dict(st["metrics"])
        rounded = metrics.pop("_rounded", [])
        entry = {"start": st["start"], "end": st["end"], **metrics, "changes_pct": st["changes_pct"],
                 "read_at": datetime.now().isoformat(timespec="seconds"), "source": "Spotify for Artists, backfill 2026-10-21"}
        if rounded:
            entry["rounded"] = rounded                # shown by Spotify as e.g. 1.1K
        if (end - start).days == 6:
            if st["end"] in data.setdefault("weeks", {}):
                counts["skipped"] += 1
                continue
            data["weeks"][st["end"]] = entry
            counts["weeks"] += 1
        elif start.day == 1 and (end + timedelta(days=1)).day == 1 or (start.day == 1 and end.month == start.month):
            data.setdefault("months", {})[st["start"][:7]] = entry
            counts["months"] += 1
        else:
            raise ParseError(f"{start} to {end} is neither a week nor a month")
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(STORE)
    return counts


def week_pair(d1: str) -> tuple[dict | None, dict | None]:
    """The stored week that ends within 3 days before the snapshot date d1, and the one 7 days before it."""
    weeks = load().get("weeks", {})
    try:
        ref = date.fromisoformat(d1)
    except ValueError:
        return None, None
    cur = next((weeks[k] for k in sorted(weeks, reverse=True) if 0 <= (ref - date.fromisoformat(k)).days <= 3), None)
    if not cur:
        return None, None
    prev = weeks.get((date.fromisoformat(cur["end"]) - timedelta(days=7)).isoformat())
    return cur, prev


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--urls" in args:
        print(AUDIENCE_URL + "   (then the '7 days' period option)")
        print(HOME_URL)
    elif "--backfill" in args:                 # files, one Audience page text each, split by a line '=====PAGE'
        texts = [t for f in args[args.index("--backfill") + 1:] for t in Path(f).read_text().split("=====PAGE") if t.strip()]
        print(save_backfill(texts))
    elif "--show" in args:
        print(json.dumps(load(), indent=2, ensure_ascii=False))
    elif "--stats" in args:
        stats = parse_stats(Path(args[args.index("--stats") + 1]).read_text())
        home = parse_home(Path(args[args.index("--home") + 1]).read_text()) if "--home" in args else None
        print(json.dumps(save_week(stats, home), indent=2, ensure_ascii=False))
    else:
        print(__doc__)
