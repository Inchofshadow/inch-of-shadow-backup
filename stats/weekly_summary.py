"""
stats/weekly_summary.py
------------------------
Weekly stats summary (G-06, 2026-10-21). Once a week (Monday, from the daily sync) it compares
the newest snapshot with the one from about 7 days earlier, builds the numbers table HERE (every
number comes from the snapshots, never from a model), and asks Claude for 2-3 short suggestions
that cite those numbers. The result goes on top of plans/weekly-stats.md, newest week first.

Covers SoundCloud and YouTube from the daily sync, and Spotify from the weekly read of Spotify for
Artists (stats/spotify_s4a.py; the public API gives only the catalogue size). Instagram is skipped
since direct reads are retired. A missing source is said, not guessed.

Usage:
    python3 stats/weekly_summary.py              # this week's summary (skips if already written)
    python3 stats/weekly_summary.py --force      # write it again
    python3 stats/weekly_summary.py --dry-run    # print, write nothing, no Claude call
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SNAPSHOTS = ROOT / "stats_snapshots"
OUT_FILE = ROOT / "plans" / "weekly-stats.md"
HEADER = ("# Weekly stats\n\nOne section per week, newest first, written on Mondays by stats/weekly_summary.py "
          "from the daily snapshots and the weekly Spotify for Artists read. Numbers come from those only. "
          "SoundCloud, Spotify and YouTube; Instagram is not collected (direct reads retired).\n")
RATIO_FLOOR, RATIO_TARGET = 1.0, (1.4, 1.6)
SC_FIELDS = [("followers", "Followers"), ("following", "Following"), ("total_plays", "Plays"),
             ("total_likes", "Likes"), ("total_reposts", "Reposts"), ("total_comments", "Comments")]
YT_FIELDS = [("subscribers", "Subscribers"), ("total_views", "Views"), ("total_likes", "Likes"),
             ("video_count", "Videos")]
SET_MIN_MS = 20 * 60 * 1000          # SoundCloud uploads of 20 minutes or more are DJ sets and mixes, not tracks
SP_FIELDS = [("listeners", "Listeners (7 days)"), ("streams", "Streams (7 days)"), ("saves", "Saves (7 days)"),
             ("playlist_adds", "Playlist adds (7 days)"), ("followers", "Followers")]

SCHEMA = {
    "type": "object",
    "properties": {"tips": {"type": "array", "items": {
        "type": "object",
        "properties": {"title": {"type": "string"}, "action": {"type": "string"}},
        "required": ["title", "action"], "additionalProperties": False}}},
    "required": ["tips"],
    "additionalProperties": False,
}

SYSTEM = """You write the weekly stats read for Inch of Shadow, a Berlin musician (songs and an electronic lane under one name).

You get a table of this week against last week for SoundCloud, Spotify (from Spotify for Artists, a 7-day window) and YouTube, and the tracks and videos that moved (SoundCloud plays gained, split into tracks and DJ sets by the "kind" field; YouTube views gained; Spotify streams in the 7 days). Treat DJ sets and released tracks as different things. Write 2 or 3 tips for a dashboard card. Each tip has:
- title: what happened, at most 7 words, with one number from the data and the track or video it belongs to (e.g. "Farewell +34 plays, most likes").
- action: one concrete thing to do about it, at most 16 words.
Use only the numbers given; never estimate or invent one. If a week shows almost no movement, say that plainly in one tip.

Never tell him to post or to post more. Never suggest re-following anyone. No em-dashes. Plain, short English. The brand is not only dark; do not steer toward any mood."""


def _snapshots() -> list[tuple[datetime, Path]]:
    out = []
    for f in SNAPSHOTS.glob("snapshot_*.json"):
        try:
            out.append((datetime.strptime(f.stem[len("snapshot_"):], "%Y-%m-%dT%H-%M-%S"), f))
        except ValueError:
            continue
    return sorted(out)


def pick_pair(now: datetime | None = None) -> tuple[dict | None, dict | None, str, str]:
    """The newest snapshot at or before `now`, and the newest one at least 6 days older."""
    now = now or datetime.now()
    snaps = [s for s in _snapshots() if s[0] <= now]
    if not snaps:
        return None, None, "", ""
    t1, f1 = snaps[-1]
    older = [s for s in snaps if s[0] <= t1 - timedelta(days=6)]
    if not older:
        return json.loads(f1.read_text()), None, t1.strftime("%Y-%m-%d"), ""
    t0, f0 = older[-1]
    return json.loads(f1.read_text()), json.loads(f0.read_text()), t1.strftime("%Y-%m-%d"), t0.strftime("%Y-%m-%d")


def _delta(a, b):
    return None if a is None or b is None else a - b


def compute(now_snap: dict | None, prev_snap: dict | None) -> dict:
    """Everything the summary states, from the two snapshots. No model involved."""
    out = {"missing": [], "rows": [], "movers": []}
    if now_snap is None:
        out["missing"].append("no snapshot at all")
        return out
    if prev_snap is None:
        out["missing"].append("no snapshot from a week earlier to compare with")
    pn, pp = now_snap.get("platforms", {}), (prev_snap or {}).get("platforms", {})
    for plat, label, fields in (("soundcloud", "SoundCloud", SC_FIELDS), ("youtube", "YouTube", YT_FIELDS)):
        if plat not in pn:
            out["missing"].append(f"{label} not in this week's snapshot")
            continue
        if isinstance(pn[plat], dict) and "skipped" in pn[plat]:    # not collected, never a 0
            out["missing"].append(f"{label} skipped this week, because {pn[plat]['skipped']}")
            continue
        for key, name in fields:
            a, b = pn[plat].get(key), pp.get(plat, {}).get(key)
            out["rows"].append({"platform": label, "metric": name, "prev": b, "now": a, "delta": _delta(a, b)})
    sc_n, sc_p = pn.get("soundcloud", {}), pp.get("soundcloud", {})
    if sc_n.get("followers") is not None and sc_n.get("following"):
        out["ratio"] = {"now": round(sc_n["followers"] / sc_n["following"], 2),
                        "prev": round(sc_p["followers"] / sc_p["following"], 2) if sc_p.get("following") else None}
    # Spotify: the weekly Spotify for Artists read that ends within 3 days before this snapshot
    from stats import spotify_s4a
    sp_cur, sp_prev = spotify_s4a.week_pair((now_snap.get("timestamp") or "")[:10])
    if sp_cur is None:
        out["missing"].append("no Spotify for Artists read for this week")
    else:
        out["spotify_week"] = f"{sp_cur['start']} to {sp_cur['end']}"
        for key, name in SP_FIELDS:
            a, b = sp_cur.get(key), (sp_prev or {}).get(key)
            out["rows"].append({"platform": "Spotify", "metric": name, "prev": b, "now": a, "delta": _delta(a, b)})
        for song in sp_cur.get("top_songs", []):
            out["movers"].append({"where": "Spotify", "title": song["title"], "streams_week": song["streams"]})
    prev_tracks = {t["title"]: t for t in sc_p.get("tracks", [])}
    for t in sc_n.get("tracks", []):
        d = _delta(t.get("plays"), prev_tracks.get(t["title"], {}).get("plays"))
        if d:
            out["movers"].append({"where": "SoundCloud", "title": t["title"], "plays_now": t.get("plays"), "plays_delta": d,
                                  "likes_delta": _delta(t.get("likes"), prev_tracks.get(t["title"], {}).get("likes")),
                                  "kind": "set" if (t.get("duration_ms") or 0) >= SET_MIN_MS else "track"})
    prev_vids = {v["id"]: v for v in pp.get("youtube", {}).get("videos", [])}
    for v in pn.get("youtube", {}).get("videos", []):
        d = _delta(v.get("views"), prev_vids.get(v["id"], {}).get("views"))
        if d:
            out["movers"].append({"where": "YouTube", "title": v["title"], "views_now": v.get("views"), "views_delta": d})
    out["movers"].sort(key=lambda m: -(m.get("plays_delta") or m.get("views_delta") or m.get("streams_week") or 0))
    return out


def _fmt(v) -> str:
    return "–" if v is None else (f"{v:+d}" if isinstance(v, int) else str(v))


def table(data: dict) -> str:
    lines = ["| Platform | Metric | Last week | This week | Change |", "|---|---|---|---|---|"]
    for r in data["rows"]:
        lines.append(f"| {r['platform']} | {r['metric']} | {'–' if r['prev'] is None else r['prev']} | "
                     f"{'–' if r['now'] is None else r['now']} | {_fmt(r['delta'])} |")
    if data.get("ratio"):
        q = data["ratio"]
        lines += ["", "| SoundCloud ratio | Last week | This week | Floor | Target |", "|---|---|---|---|---|",
                  f"| followers : following | {q['prev'] if q['prev'] is not None else '–'}:1 | {q['now']}:1 | "
                  f"{RATIO_FLOOR:.0f}:1 | {RATIO_TARGET[0]}-{RATIO_TARGET[1]}:1 |"]
    return "\n".join(lines)


def _clean(text: str) -> str:
    """One line, no em- or en-dashes: a dash between digits is a range, any other dash a comma pause."""
    text = " ".join(text.split())
    text = re.sub(r"(?<=\d)\s*[\u2013\u2014]\s*(?=\d)", "-", text)
    text = re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)
    return re.sub(r"\s+,", ",", text).strip()


def ask_claude(data: dict, d1: str, d0: str, client=None) -> tuple[list[str], dict]:
    from release_manager import claude_api
    client = client or claude_api.client()
    message = claude_api.ask(
        client, max_tokens=8000, system=SYSTEM, effort="medium", schema=SCHEMA, what="weekly stats",
        messages=[{"role": "user", "content": f"Week {d0} to {d1}.\n\nNUMBERS (from the snapshots):\n"
                                              f"{json.dumps(data, ensure_ascii=False, indent=1)}"}])
    tips = json.loads(claude_api.text_of(message)).get("tips") or []
    bullets = [f"**{_clean(t['title']).rstrip('.')}.** {_clean(t['action'])}" for t in tips
               if (t.get("title") or "").strip() and (t.get("action") or "").strip()][:3]
    return bullets, claude_api.usage_of(message)


def section(now: datetime | None = None, client=None, dry_run: bool = False) -> tuple[str, str]:
    """(week key, markdown section)."""
    now_snap, prev_snap, d1, d0 = pick_pair(now)
    data = compute(now_snap, prev_snap)
    key = d1 or (now or datetime.now()).strftime("%Y-%m-%d")
    head = f"## Week to {key}" + (f" (vs {d0})" if d0 else "")
    parts = [head, ""]
    if data["missing"]:
        parts += ["Missing: " + "; ".join(data["missing"]) + ".", ""]
    if data["rows"]:
        parts += [table(data), ""]
    if data["rows"] and prev_snap is not None:
        if dry_run:
            parts.append("- (dry run: no Claude call)")
        else:
            bullets, usage = ask_claude(data, d1, d0, client=client)
            parts += [f"- {b}" for b in bullets] or ["- No suggestions came back."]
    return key, "\n".join(parts).rstrip() + "\n"


def write(now: datetime | None = None, force: bool = False, client=None) -> str:
    """Put this week's section on top of plans/weekly-stats.md. Returns what happened."""
    text = OUT_FILE.read_text(encoding="utf-8") if OUT_FILE.is_file() else HEADER
    now_snap, _, d1, _ = pick_pair(now)
    if d1 and f"## Week to {d1}" in text and not force:
        return f"week to {d1} already written"
    key, sec = section(now, client=client)
    if force:                                       # replace this week's old section, keep the rest
        import re
        text = re.sub(r"## Week to " + re.escape(key) + r".*?(?=\n## Week to |\Z)", "", text, flags=re.S).rstrip() + "\n"
    head, _, rest = text.partition("\n## ")
    body = (head.rstrip() + "\n\n" + sec + ("\n## " + rest if rest else "")).rstrip() + "\n"
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(body, encoding="utf-8")
    return f"wrote week to {key}"


def latest() -> str:
    """The newest section, for the Stats page (read-only)."""
    if not OUT_FILE.is_file():
        return ""
    text = OUT_FILE.read_text(encoding="utf-8")
    i = text.find("## Week to ")
    if i < 0:
        return ""
    j = text.find("\n## Week to ", i + 1)
    return text[i: j if j > 0 else None].strip()


def latest_view() -> dict | None:
    """The newest week as plain parts for the Stats page: title, missing line, suggestions (no table:
    the page shows every number already)."""
    sec = latest()
    if not sec:
        return None
    lines = sec.splitlines()
    return {"title": lines[0].lstrip("# ").strip(),
            "missing": next((l[len("Missing: "):] for l in lines if l.startswith("Missing: ")), ""),
            "bullets": [l[2:] for l in lines if l.startswith("- ")]}


def refresh_if_spotify_missing(now: datetime | None = None, client=None) -> str:
    """After a late Spotify read: rewrite this week's section only if it was written without Spotify."""
    if not OUT_FILE.is_file():
        return "no summary yet"
    _, _, d1, _ = pick_pair(now)
    text = OUT_FILE.read_text(encoding="utf-8")
    i = text.find(f"## Week to {d1}")
    if i < 0:
        return f"week to {d1} not written yet (the Monday sync writes it)"
    j = text.find("\n## Week to ", i + 1)
    if "no Spotify for Artists read" not in text[i: j if j > 0 else None]:
        return f"week to {d1} already has Spotify"
    return write(now, force=True, client=client)


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print(section(dry_run=True)[1])
    elif "--refresh-spotify" in sys.argv:
        print(refresh_if_spotify_missing())
    else:
        print(write(force="--force" in sys.argv))
