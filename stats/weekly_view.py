"""
stats/weekly_view.py
---------------------
Everything the Stats page's "This week" panel draws (G-06 redesign, 2026-10-21): four stat
tiles with the week's change and a 30-day trend, the tracks and videos that moved with their
cover art, and the week's tips from plans/weekly-stats.md. All numbers come from the snapshots.

Cover art: the snapshot's SoundCloud artwork_url / YouTube thumbnail (kept since 2026-10-21),
else a YouTube thumbnail by video id, else a local cover in artwork/ named after the release,
else no picture (the page draws a letter tile). Remote pictures are fetched once by the server,
shrunk to 96 px and kept in generated_images/stats_thumbs/; the browser only ever loads local files.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from stats import weekly_summary as ws

ROOT = Path(__file__).resolve().parent.parent
THUMBS = ROOT / "generated_images" / "stats_thumbs"
ARTWORK = ROOT / "artwork"
TILES = [("soundcloud", "followers", "Followers"), ("soundcloud", "total_plays", "Plays"),
         ("soundcloud", "total_likes", "Likes"), ("youtube", "total_views", "Views")]
SP_TILES = [("listeners", "Listeners"), ("streams", "Streams"), ("saves", "Saves"), ("followers", "Followers")]
PLATFORM_NAME = {"soundcloud": "SoundCloud", "youtube": "YouTube", "spotify": "Spotify"}
# the release-slug files are the live covers (The Deceiver = the Pieta since 2026-07-04, not the shared painting)
LOCAL_COVERS = {"Farewell": "farewell-single.png", "The Deceiver": "the-deceiver-single.png"}
SPARK_W, SPARK_H = 120, 34


def _series(days: int = 30, now: datetime | None = None) -> list[tuple[datetime, dict]]:
    now = now or datetime.now()
    out = []
    for t, f in ws._snapshots():
        if now - timedelta(days=days) <= t <= now:
            try:
                out.append((t, json.loads(f.read_text())))
            except (OSError, ValueError):
                continue
    return out


def _spark(vals: list[float]) -> dict:
    """Polyline points for a small trend line, plus the last point (the accent dot)."""
    if len(vals) < 2:
        return {}
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    step = SPARK_W / (len(vals) - 1)
    pts = [(round(i * step, 1), round(SPARK_H - 3 - (v - lo) / span * (SPARK_H - 6), 1)) for i, v in enumerate(vals)]
    return {"points": " ".join(f"{x},{y}" for x, y in pts), "last": pts[-1], "lo": lo, "hi": hi}


def _compact(n) -> str:
    if n is None:
        return "–"
    return f"{n / 1000:.1f}K".replace(".0K", "K") if abs(n) >= 10000 else f"{n:,}"


def _thumb_local(name: str) -> str:
    """generated_images/stats_thumbs/<name> if it is there."""
    return name if (THUMBS / name).is_file() else ""


def _fetch_thumb(url: str) -> str:
    """Download a public picture once, shrink it to 96 px, keep it local. '' on any failure."""
    if not url or not url.startswith("https://"):
        return ""
    name = hashlib.sha1(url.encode()).hexdigest()[:16] + ".jpg"
    if _thumb_local(name):
        return name
    miss = THUMBS / (name + ".miss")                          # a failed fetch waits a day before the next try
    if miss.is_file() and datetime.now().timestamp() - miss.stat().st_mtime < 86400:
        return ""
    try:
        import requests
        from PIL import Image
        r = requests.get(url.replace("-large.", "-t200x200."), timeout=8)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        im.thumbnail((96, 96))
        THUMBS.mkdir(parents=True, exist_ok=True)
        im.save(THUMBS / name, quality=88)
        return name
    except Exception:                                       # noqa: BLE001 - a missing picture is fine
        try:
            THUMBS.mkdir(parents=True, exist_ok=True)
            miss.write_text(url)
        except OSError:
            pass
        return ""


def _local_cover(title: str) -> str:
    for key, file in LOCAL_COVERS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", title) and (ARTWORK / file).is_file():
            name = "local-" + re.sub(r"[^a-z0-9]+", "-", Path(file).stem.lower()) + ".jpg"   # new file, new thumb
            if not _thumb_local(name):
                try:
                    from PIL import Image
                    with Image.open(ARTWORK / file) as im:
                        im = im.convert("RGB")
                        im.thumbnail((96, 96))
                        THUMBS.mkdir(parents=True, exist_ok=True)
                        im.save(THUMBS / name, quality=88)
                except Exception:                           # noqa: BLE001
                    return ""
            return name
    return ""


def _short(title: str) -> str:
    """'Inch of Shadow - Farewell' -> 'Farewell'; DJ sets keep their place name."""
    t = re.sub(r"^\s*Inch of Shadow\s*(&[^–-]+)?[-–]\s*", "", title).strip()
    t = re.sub(r"\s*\((Official Audio|Official Video|Visualizer)\)", "", t, flags=re.I)
    t = re.sub(r"\s*\|.*$", "", t).strip() or title
    at = re.search(r"DJ Set\s*@\s*(.+)$", t, flags=re.I)
    return f"DJ set @ {at.group(1).strip()}" if at else t


def _set_name(title: str) -> str:
    """A DJ set by its place or name: '... DJ Set @ Johnny Knüppel | Berlin 24.04.26' -> 'Johnny Knüppel'."""
    t = re.sub(r"\s*\|.*$", "", title).strip()
    if "@" in t:
        t = t.split("@", 1)[1].strip()
    else:
        t = re.sub(r"^\s*Inch of Shadow\s*[-–]\s*", "", t).strip()
    return re.sub(r",\s*Berlin$", "", t).strip() or title


GROUPS = [("sc_tracks", "SoundCloud tracks"), ("sc_sets", "SoundCloud DJ sets"), ("spotify", "Spotify"), ("youtube", "YouTube")]
GROUP_MAX = 5


def _art(m: dict, fetch: bool) -> str:
    if m.get("art_url") and fetch:
        got = _fetch_thumb(m["art_url"])
        if got:
            return got
    if m.get("video_id") and fetch:
        got = _fetch_thumb(f"https://i.ytimg.com/vi/{m['video_id']}/mqdefault.jpg")
        if got:
            return got
    return _local_cover(m["title"])


def build(now: datetime | None = None, fetch: bool = True) -> dict | None:
    now_snap, prev_snap, d1, d0 = ws.pick_pair(now)
    if now_snap is None:
        return None
    data = ws.compute(now_snap, prev_snap)
    series = _series(30, now)
    tiles = []
    for plat, key, label in TILES:
        cur = now_snap.get("platforms", {}).get(plat, {}).get(key)
        if cur is None:
            continue
        prev = (prev_snap or {}).get("platforms", {}).get(plat, {}).get(key)
        vals = [s.get("platforms", {}).get(plat, {}).get(key) for _, s in series]
        vals = [v for v in vals if isinstance(v, (int, float))]
        delta = None if prev is None else cur - prev
        from release_manager.stats_tracks import PLATFORMS as _P
        tiles.append({"label": label, "platform": PLATFORM_NAME[plat], "per": "days", "icon": _P.get(plat, {}).get("path", ""),
                      "colour": _P.get(plat, {}).get("colour", ""), "value": _compact(cur), "delta": delta,
                      "delta_text": "no change" if delta == 0 else ("–" if delta is None else f"{delta:+,}"),
                      "dir": "flat" if not delta else ("up" if delta > 0 else "down"),
                      "spark": _spark(vals), "days": len(vals)})
    # Spotify tiles from the weekly Spotify for Artists reads (one point per week)
    from release_manager.stats_tracks import PLATFORMS as _P
    from stats import spotify_s4a
    sp_cur, sp_prev = spotify_s4a.week_pair(d1)
    if sp_cur:
        weeks = [w for k, w in sorted(spotify_s4a.load().get("weeks", {}).items()) if k <= sp_cur["end"]][-12:]
        sp_tiles = []
        for key, label in SP_TILES:
            cur, prev = sp_cur.get(key), (sp_prev or {}).get(key)
            if cur is None:
                continue
            delta = None if prev is None else cur - prev
            sp_tiles.append({"label": label, "platform": "Spotify", "icon": _P["spotify"]["path"],
                             "colour": _P["spotify"]["colour"], "value": _compact(cur), "delta": delta,
                             "delta_text": "no change" if delta == 0 else ("–" if delta is None else f"{delta:+,}"),
                             "dir": "flat" if not delta else ("up" if delta > 0 else "down"),
                             "spark": _spark([w[key] for w in weeks if isinstance(w.get(key), (int, float))]),
                             "days": len(weeks), "per": "weeks" if label != "Followers" else "weeks"})
        tiles = tiles[:3] + sp_tiles + tiles[3:]
    # the movers, with what we need for their pictures
    sc_now = {t["title"]: t for t in now_snap.get("platforms", {}).get("soundcloud", {}).get("tracks", [])}
    yt_now = {v["title"]: v for v in now_snap.get("platforms", {}).get("youtube", {}).get("videos", [])}
    movers = []
    for m in data["movers"]:
        gained = m.get("plays_delta") or m.get("views_delta") or m.get("streams_week") or 0
        row = {"title": m["title"], "short": _short(m["title"]), "where": m["where"], "gained": gained,
               "unit": {"SoundCloud": "plays", "YouTube": "views", "Spotify": "streams"}[m["where"]],
               "total": m.get("plays_now") or m.get("views_now"), "likes_delta": m.get("likes_delta")}
        if m["where"] == "SoundCloud":
            row["art_url"] = sc_now.get(m["title"], {}).get("artwork_url", "")
        else:
            v = yt_now.get(m["title"], {})
            row["art_url"], row["video_id"] = v.get("thumb", ""), v.get("id", "")
        row["group"] = ("sc_sets" if m.get("kind") == "set" else "sc_tracks") if m["where"] == "SoundCloud" else \
            ("spotify" if m["where"] == "Spotify" else "youtube")
        if row["group"] == "sc_sets":
            row["short"] = _set_name(m["title"])
        movers.append(row)
    groups = []
    for key, label in GROUPS:                 # SoundCloud tracks, DJ sets, Spotify, YouTube: never mixed
        rows = sorted([m for m in movers if m["group"] == key], key=lambda m: -m["gained"])[:GROUP_MAX]
        if not rows:
            continue
        top = max(m["gained"] for m in rows) or 1
        for m in rows:
            m["pct"] = round(100 * m["gained"] / top, 1)
            m["art"] = _art(m, fetch)
            m["letter"] = (m["short"][:1] or "?").upper()
        groups.append({"key": key, "label": label, "rows": rows,
                       "note": {"sc_tracks": "plays gained", "sc_sets": "plays gained", "spotify": "streams, last 7 days",
                                "youtube": "views gained"}[key]})
    view = ws.latest_view() or {}
    tips = []
    for b in view.get("bullets", []):
        mt = re.match(r"\*\*(.+?)\*\*\s*(.*)", b)
        tips.append({"title": mt.group(1).rstrip("."), "action": mt.group(2)} if mt else {"title": "", "action": b})
    return {"week": f"{d0} to {d1}" if d0 else d1, "d1": d1, "tiles": tiles, "movers": movers, "groups": groups, "tips": tips,
            "missing": data["missing"], "rows": data["rows"], "ratio": data.get("ratio"),
            "ratio_floor": ws.RATIO_FLOOR, "ratio_target": ws.RATIO_TARGET}
