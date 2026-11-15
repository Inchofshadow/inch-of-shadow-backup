"""
release_manager/ratio_graph.py
------------------------------
System 98 (Amir 2026-11-11, about the graph under the evening Socials digest: "thos the kinds
of grpahs i wanna see also on RM"): the followers ÷ following ratio per day on RM /stats, for
SoundCloud and Instagram. Spec: memory socials-digest-ratio-graph.

- one point per day: the last snapshot of that day (stats_snapshots/snapshot_*.json) whose platform
  block has both followers and following; skipped blocks are not readings
- a solid line for the real ratio (broken where readings are more than 3 days apart), a dashed 1:1
  floor, a dotted path from today's ratio to the Dec 31 target point, x-axis in days (MM-DD) to Dec 31
- targets are FUTURE points, never a band over the past (Amir 11-06)
- drawn here as inline SVG (RM loads nothing from outside), twice: wide (sized to the LADDER box's
  graph column, Amir 2026-11-12) for desktop and narrow for
  phones, so the labels keep their real size; colours come from CSS classes on the --sb tokens
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Optional

START = date(2026, 9, 26)     # the digest graph's first day (memory socials-digest-ratio-graph)
GAP_DAYS = 3                  # readings further apart than this are not joined

# Written targets only, each with where it is written. Nothing here is a guess: a target that is not
# written anywhere stays None and the page says "not set".
TARGETS = {
    "soundcloud": {
        "name": "SoundCloud",
        "dec31": 1.2,
        "long": (1.4, 1.6),
        "long_when": "Aug 2027",
        "source": "memory socials-digest-ratio-graph; plans/handovers/socials/sc-agent.md "
                  "(Dec 31 600 at 1.2:1, Aug 2027 1000 at 1.4-1.6:1)",
    },
    "instagram": {
        "name": "Instagram",
        "dec31": 1.2,        # Amir 2026-11-11 (System 98 side chat): "1.2:1", same as SoundCloud
        "long": (1.4, 1.6),
        "long_when": None,   # memory ig-kpis: floor 1:1, drift to ~1.4-1.6:1, no date
        "source": "Dec 31: Amir 2026-11-11 (System 98 side chat); long-run: memory ig-kpis "
                  "(floor 1:1, drift to ~1.4-1.6:1, no date)",
    },
}


def daily_ratios(snapshots: list, platform: str, start: date = START) -> list:
    """[{date, followers, following, ratio}] oldest first, one per day from `start` on."""
    by_day = {}
    for s in snapshots:
        block = (s.get("platforms") or {}).get(platform)
        if not isinstance(block, dict) or "skipped" in block:
            continue
        fol, fing = block.get("followers"), block.get("following")
        if not isinstance(fol, int) or not isinstance(fing, int) or fol <= 0 or fing <= 0:
            continue
        stamp = str(s.get("timestamp") or "")
        try:
            day = date.fromisoformat(stamp[:10])
        except ValueError:
            continue
        if day < start:
            continue
        if day not in by_day or stamp >= by_day[day][0]:
            by_day[day] = (stamp, fol, fing)
    return [{"date": d, "followers": f, "following": g, "ratio": f / g}
            for d, (_, f, g) in sorted(by_day.items())]


def _r(v: float) -> str:
    return "%.2f" % v


def _ticks(start: date, end: date, step: int) -> list:
    out, d = [], start
    while d < end:
        if (end - d).days >= step * 0.6:      # keep clear of the end label
            out.append(d)
        d += timedelta(days=step)
    return out + [end]


def svg(points: list, target: Optional[float], end: date, start: date = START,
        w: int = 680, h: int = 280, step: int = 14, cls: str = "") -> str:
    """One ratio chart. `step` is the day gap between MM-DD labels (wide 14, phone 28)."""
    span = max((end - start).days, 1)
    vals = [p["ratio"] for p in points] + [1.0] + ([target] if target else [])
    lo = int(min(vals) * 20 - 1) / 20.0            # 0.05 below the lowest, on a 0.05 step
    hi = int(max(vals) * 20 + 2) / 20.0            # 0.05 above the highest
    left, right, top, bottom = 40, w - 14, 22, h - 32

    def x(d):
        return left + (d - start).days / span * (right - left)

    def y(v):
        return bottom - (v - lo) / (hi - lo) * (bottom - top)

    out = ['<svg class="rg-svg %s" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
           'aria-label="Followers per following, by day, to Dec 31">' % (cls, w, h)]
    g = math.ceil(lo * 10 - 1e-9) / 10.0           # first 0.1 line at or above lo
    while g <= hi + 1e-9:
        if abs(g - 1.0) > 1e-9:
            out.append('<line class="rg-grid" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (left, y(g), right, y(g)))
        out.append('<text class="rg-ytick" x="%d" y="%.1f" text-anchor="end">%.1f</text>' % (left - 6, y(g) + 4, g))
        g = round(g + 0.1, 1)
    out.append('<line class="rg-floor" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (left, y(1.0), right, y(1.0)))
    out.append('<text class="rg-floor-label" x="%d" y="%.1f" text-anchor="end">1:1 floor</text>' % (right, y(1.0) + 16))
    out.append('<line class="rg-axis" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (left, bottom, right, bottom))
    for t in _ticks(start, end, step):
        out.append('<text class="rg-xtick" x="%.1f" y="%d" text-anchor="%s">%s</text>' % (
            x(t), h - 10, "end" if t == end else ("start" if t == start else "middle"), t.strftime("%m-%d")))
    # the real line, broken over gaps; a lone reading gets a dot
    seg = []
    segs = []
    for p in points:
        if seg and (p["date"] - seg[-1]["date"]).days > GAP_DAYS:
            segs.append(seg)
            seg = []
        seg.append(p)
    if seg:
        segs.append(seg)
    for s in segs:
        if len(s) == 1:
            out.append('<circle class="rg-dot" cx="%.1f" cy="%.1f" r="3"/>' % (x(s[0]["date"]), y(s[0]["ratio"])))
        else:
            out.append('<polyline class="rg-line" points="%s"/>' % " ".join(
                "%.1f,%.1f" % (x(p["date"]), y(p["ratio"])) for p in s))
    if points:
        now = points[-1]
        nx, ny = x(now["date"]), y(now["ratio"])
        if target:
            tx, ty = x(end), y(target)
            out.append('<line class="rg-path" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (nx, ny, tx, ty))
            out.append('<circle class="rg-target" cx="%.1f" cy="%.1f" r="6"/>' % (tx, ty))
            out.append('<text class="rg-target-num" x="%.1f" y="%.1f" text-anchor="end">%s Dec 31</text>' % (
                tx - 2, ty - 12, _r(target)))
        out.append('<circle class="rg-now" cx="%.1f" cy="%.1f" r="6"/>' % (nx, ny))
        # below-right of the dot: the real line comes in from the left, the dotted path leaves upward
        out.append('<text class="rg-now-num" x="%.1f" y="%.1f" text-anchor="start">%s now</text>' % (
            nx + 8, ny + 22, _r(now["ratio"])))
    out.append("</svg>")
    return "".join(out)


def build(snapshots: Optional[list] = None, today: Optional[date] = None) -> list:
    """The two charts for the template: [{key, name, now, cards, wide, narrow}]."""
    if snapshots is None:
        from stats.storage import list_snapshots
        snapshots = list_snapshots()
    today = today or date.today()
    end = date(today.year, 12, 31)
    out = []
    for key in ("soundcloud", "instagram"):
        t = TARGETS[key]
        pts = daily_ratios(snapshots, key)
        now = pts[-1] if pts else None
        lo_hi = "%.1f-%.1f:1" % t["long"]
        out.append({
            "key": key,
            "name": t["name"],
            "now": now,
            "now_text": (_r(now["ratio"]) + ":1") if now else None,
            "under_floor": bool(now and now["ratio"] < 1.0),
            "dec31": (_r(t["dec31"]).rstrip("0").rstrip(".") + ":1") if t["dec31"] else None,
            "long": lo_hi,
            "long_when": t["long_when"],
            "source": t["source"],
            "days": len(pts),
            "wide": svg(pts, t["dec31"], end, cls="rg-wide") if pts else "",
            "narrow": svg(pts, t["dec31"], end, w=330, h=250, step=28, cls="rg-narrow") if pts else "",
        })
    return out
