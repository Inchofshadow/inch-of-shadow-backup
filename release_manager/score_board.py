"""Score board data: cards against targets, health row, ladder charts, trends.

Pure data layer. Reads the metric registry (stats/registry.py over plans/targets.json), the
stats snapshots and a few read-only automation state files; never raises because a file is
missing. Every rule takes `now` (M11, 2026-11-06): build(now=...) is the only clock.

Readings carry provenance ({value, as_of, source, run_id}); a reading older than its
cadence window is stale and shows red with its age; the verdict is OFF PACE as soon as one
card is red; `build(month="2026-11")` shows the frozen month (stats/freeze.py).
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Optional

from release_manager.stats_tracks import sparkline
from stats import ig_followback, registry, spotify_s4a, storage
from stats.targets import (
    current_rung,
    ladder_value,
    light_for_floor,
    light_for_ladder,
    load_targets,
    progress_pct,
)

ROOT = Path(__file__).resolve().parent.parent
FOLLOWBACK_FILE = ROOT / "stats_snapshots" / "ig_followback.json"
AUTONOMY_FILE = ROOT / "scene_intelligence" / "autonomy_state.json"
TARGET_LIST_FILE = ROOT / "scene_intelligence" / "ig_target_list.json"
DETECTIONS_FILE = ROOT / "scene_intelligence" / "detection_events.json"
DATA_DIR = ROOT / "data"
RELEASES_DIR = ROOT / "releases"
GATES_DIR = ROOT / "stats_snapshots" / "gates"
SPARK_DAYS = 90
PROVENANCE_KEYS = ("as_of", "source", "run_id")

# Who brings a number in, by source kind (the dashboard brief, B4): collected by itself,
# read by Claude (S4A, the IG export, the release files), typed in by Amir.
WHO = {"snapshot": ("\U0001F916", "collected by itself"), "s4a": ("\U0001F383", "Claude reads it"),
       "followback": ("\U0001F383", "Claude reads it"), "release": ("\U0001F383", "Claude reads it"),
       "manual": ("\U0001F64B", "Amir types it")}
# The freshness strip: one chip per source, in this order. A metric joins the chip of its
# first source alternative; release files have no window and get no chip.
STRIP = (("ig", "IG"), ("ig_export", "IG export"), ("sc", "SC"), ("s4a", "Spotify S4A"),
         ("youtube", "YouTube"), ("bandcamp", "Bandcamp"), ("manual", "manual"))


def _read_json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- series

def _one_source(source: str) -> list:
    """Points {date, value, as_of, source, run_id} for one source string."""
    kind, _, rest = source.partition(":")
    if kind in ("snapshot", "manual"):
        platform, _, metric = rest.partition(".")
        return storage.get_readings(platform, metric, days=400)
    if kind == "s4a":
        field = rest.partition(".")[2]
        weeks = spotify_s4a.load().get("weeks") or {}
        if not isinstance(weeks, dict):
            return []
        return [{"date": end, "value": w[field], "as_of": w.get("read_at") or end,
                 "source": w.get("source") or "s4a", "run_id": ("s4a:%s" % w["read_at"]) if w.get("read_at") else None}
                for end, w in sorted(weeks.items()) if isinstance(w, dict) and w.get(field) is not None]
    if kind == "followback":
        data = _read_json(FOLLOWBACK_FILE)
        data = data if isinstance(data, dict) else {}
        if data.get("export_date") and data.get(rest) is not None:
            return [{"date": data["export_date"], "value": data[rest], "as_of": data["export_date"],
                     "source": data.get("source") or ("export:%s" % data["export_date"]),
                     "run_id": ("followback:%s" % data["computed_at"]) if data.get("computed_at") else None}]
    if kind == "release":
        return _release_series(rest)
    return []


def _release_series(dotted: str, releases_dir: Path = None) -> list:
    """One point per release from releases/<slug>.json: the object at the dotted path
    (e.g. outcomes.stats.engagement_d28) gives {value, as_of}; backups are skipped."""
    out = []
    for f in sorted((releases_dir or RELEASES_DIR).glob("*.json")):
        if ".bak" in f.name:
            continue
        rel = _read_json(f)
        node = rel if isinstance(rel, dict) else None
        for part in dotted.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if isinstance(node, dict) and node.get("value") is not None and node.get("as_of"):
            slug = rel.get("slug") or f.stem
            out.append({"date": str(node["as_of"])[:10], "value": node["value"], "release": slug,
                        "as_of": str(node["as_of"])[:10], "source": node.get("source") or ("release:%s" % slug),
                        "run_id": None})
    return out


def _iso(day) -> Optional[date]:
    """date from an ISO string, None when malformed (bad points are skipped, never raised)."""
    try:
        return date.fromisoformat(str(day)[:10])
    except (TypeError, ValueError):
        return None


def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _clean_series(series: list) -> list:
    """Keep only points with a valid date and a numeric value (provenance keys ride along)."""
    out = []
    for p in series or []:
        if not isinstance(p, dict) or _iso(p.get("date")) is None or _num(p.get("value")) is None:
            continue
        q = {"date": str(p["date"])[:10], "value": p["value"]}
        q.update({k: p[k] for k in PROVENANCE_KEYS if p.get(k)})
        out.append(q)
    out.sort(key=lambda p: p["date"])
    return out


def _clean_metric(m: dict) -> dict:
    """The metric with malformed rungs (bad date or non-numeric value) dropped."""
    rungs = {k: v for k, v in (m.get("rungs") or {}).items() if _iso(k) is not None and _num(v) is not None}
    return dict(m, rungs=rungs)


def series_for(source: str) -> list:
    """Resolve a source string; '|' lists alternatives, first non-empty wins."""
    for part in source.split("|"):
        try:
            series = _clean_series(_one_source(part.strip()))
        except Exception:
            series = []
        if series:
            return series
    return []


def _upto(series: list, until: Optional[date]) -> list:
    """Only the points dated on or before `until` (the monthly freeze reads nothing later)."""
    if until is None:
        return series
    return [p for p in series if p["date"] <= until.isoformat()]


# ----------------------------------------------------------------- cards

def _fmt(v) -> str:
    if v is None:
        return ""
    f = _num(v)
    if f is None:
        return str(v)
    if f.is_integer():
        return "{:,}".format(int(f))
    return "{:,.1f}".format(f)


def _recent(series: list, today: date, days: int = SPARK_DAYS) -> list:
    cut = (today - timedelta(days=days)).isoformat()
    return [p for p in series if p["date"] >= cut]


def _rung_line(raw: float, plan_today: Optional[float], goal: Optional[tuple]) -> str:
    """'2 behind · 510 by Nov 30': distance to plan today, then the next rung still above the reading."""
    parts = []
    if plan_today is not None:
        d = int(round(raw - plan_today))
        parts.append("on plan" if d == 0 else ("+%d ahead" % d if d > 0 else "%d behind" % -d))
    if goal is None:
        parts.append("target reached")
    else:
        when = _iso(goal[0])
        parts.append("%s by %s" % (_fmt(goal[1]), "%s %d" % (when.strftime("%b"), when.day) if when else goal[0]))
    return " · ".join(parts)


def _next_goal(m: dict, raw: float, today: date) -> Optional[tuple]:
    """First rung from today on that the reading has not reached yet."""
    for k, v in sorted((m.get("rungs") or {}).items()):
        d, n = _iso(k), _num(v)
        if d and n is not None and d >= today and n > raw:
            return (k, n)
    return None


def is_proposed(m: dict) -> bool:
    """A rung Claude proposed that Amir has not confirmed yet (proposed_by set, confirmed false)."""
    return bool(m.get("proposed_by")) and not m.get("confirmed", False)


def _cadence(m: dict) -> str:
    return m.get("cadence") or registry.default_cadence(m.get("source", ""))


def who_for(source: str) -> tuple:
    """(emoji, words) for the first source alternative; ('', '') for an unknown kind."""
    return WHO.get(registry.source_parts(source)[0], ("", ""))


def strip_family(source: str) -> Optional[str]:
    """The freshness chip a source belongs to (STRIP keys), None for none."""
    kind, path = registry.source_parts(source)
    platform = path.partition(".")[0]
    if kind == "snapshot":
        return {"instagram": "ig", "soundcloud": "sc", "youtube": "youtube"}.get(platform)
    if kind == "followback":
        return "ig_export"
    if kind == "s4a":
        return "s4a"
    if kind == "manual":
        return "bandcamp" if platform == "bandcamp" else "manual"
    return None


def freshness_strip(members: list, now: datetime) -> list:
    """One chip per source from (source string, row) pairs, rows being built cards or trends.
    The chip shows its stalest member: a stale one first, else the oldest reading. A chip
    with no reading at all says collecting; stale is true as soon as one member is stale."""
    groups = {}
    for source, row in members:
        fam = strip_family(source)
        if fam:
            groups.setdefault(fam, []).append((source, row))
    out = []
    for fam, name in STRIP:
        rows = groups.get(fam)
        if not rows:
            continue
        have = [r for _, r in rows if r.get("as_of_full") or r.get("as_of")]
        stale = [r for r in have if r.get("stale")]

        def age_key(r):
            h = registry.age_hours(r.get("as_of_full") or r.get("as_of"), now)
            return -1 if h is None else h
        lead = (stale or sorted(have, key=age_key, reverse=True) or [None])[0]
        who, who_text = who_for(rows[0][0])
        out.append({"key": fam, "name": name, "who": who, "who_text": who_text,
                    "as_of": (lead.get("as_of_full") or lead.get("as_of")) if lead else None,
                    "age": lead.get("age", "") if lead else "", "window": lead.get("window", "") if lead else "",
                    "stale": bool(stale), "lead": lead.get("label", "") if lead else "",
                    "members": [{"label": r.get("label", ""), "as_of": r.get("as_of_full") or r.get("as_of"),
                                 "age": r.get("age", ""), "window": r.get("window", ""), "stale": bool(r.get("stale"))}
                                for _, r in rows]})
    return out


def _skipped_now(m: dict, newest: Optional[dict]) -> Optional[str]:
    """The newest snapshot's skip reason for this metric's platform (snapshot sources only)."""
    if not newest:
        return None
    for part in str(m.get("source", "")).split("|"):
        kind, path = registry.source_parts(part)
        if kind == "snapshot":
            return storage.skipped_in(newest, path.partition(".")[0])
    return None


def _card(key: str, m: dict, period: dict, now: datetime, series: Optional[list] = None,
          newest: Optional[dict] = None) -> dict:
    """One card at `now` (a date means noon of that day). `series` overrides the live read
    (the frozen month); `newest` is the newest snapshot, read for a "skipped, because" word."""
    if not isinstance(now, datetime):
        now = datetime.combine(now, time(12, 0))
    today = now.date()
    m = _clean_metric(m)
    series = series if series is not None else series_for(m.get("source", ""))
    last = series[-1] if series else None
    raw = float(last["value"]) if last else None
    reading = registry.reading(raw, (last.get("as_of") or last["date"]) if last else None,
                               (last.get("source") if last else None) or m.get("source", ""),
                               last.get("run_id") if last else None)
    fresh = registry.freshness(reading["as_of"], _cadence(m), now)
    card = {"key": key, "label": m["label"], "source": reading["source"], "unit": m.get("unit", ""),
            "value": _fmt(raw) if raw is not None else "", "raw": raw, "reading": reading,
            "run_id": reading["run_id"], "as_of_full": reading["as_of"],
            "light": "none", "light_text": "collecting", "rung_line": None, "progress": None,
            "base_line": None, "as_of": last["date"] if last else None,
            "stale": bool(fresh["stale"]), "age": fresh["age"], "window": fresh["window"], "cadence": fresh["cadence"],
            "skipped": _skipped_now(m, newest),
            "points": sparkline(_recent(series, today)), "proposed": is_proposed(m)}
    card["who"], card["who_text"] = who_for(m.get("source", ""))
    card["old"] = card["stale"]   # the card says "as of" and the age only when stale
    kind = m["kind"]
    base = (m.get("baseline") or {}).get("value")
    if kind == "ladder" and base is not None:
        plan_today = ladder_value(m, period, today)
        card["light"], card["light_text"] = light_for_ladder(raw, plan_today)
        rung = current_rung(m, today)
        if rung:
            if raw is not None:
                card["rung_line"] = _rung_line(raw, plan_today, _next_goal(m, raw, today))
        if raw is not None and _num(m.get("target")) is not None and _num(base) is not None:
            card["progress"] = progress_pct(float(base), float(m["target"]), raw)
    elif kind == "floor":
        card["light"], card["light_text"] = light_for_floor(raw, m["floor"])
        card["base_line"] = "floor %s" % _fmt(m["floor"])
        if raw is not None:
            card["rung_line"] = None
    if card["stale"] and card["light"] in ("green", "amber", "red"):
        # one freshness rule: a stale reading on a target card is red, with the age shown
        card["light"] = "red"
        card["light_text"] = "stale, %s old (window %s)" % (card["age"], card["window"])
    elif card["stale"]:
        card["light_text"] = "collecting, last reading %s old" % card["age"]
    return card


def _score(cards: list) -> dict:
    """Headline from the registry verdict: COLLECTING when no card has data, OFF PACE as
    soon as one card is red (behind, under its floor or stale), else ON PACE. Then the counts,
    e.g. 'OFF PACE, 3/9 GREEN, 1 DRIFTING, 1 RED (1 STALE), 4 COLLECTING', and `why`: the red cards."""
    n = {k: sum(1 for c in cards if c["light"] == k) for k in ("green", "amber", "red", "none")}
    with_data = n["green"] + n["amber"] + n["red"]
    head = registry.verdict([c["light"] for c in cards])
    stale = sum(1 for c in cards if c["light"] == "red" and c.get("stale"))
    red = "%d RED" % n["red"] + (" (%d STALE)" % stale if stale else "")
    parts = [head, "%d/%d GREEN" % (n["green"], len(cards)), "%d DRIFTING" % n["amber"], red, "%d COLLECTING" % n["none"]]
    why = ["%s: %s" % (c.get("label", c.get("key", "")), c.get("light_text", "")) for c in cards if c["light"] == "red"]
    return dict(n, on_pace=head == "ON PACE", with_data=with_data, line=", ".join(parts), why=why, stale=stale)


# ---------------------------------------------------------------- health

def _check(key, label, ok, detail, href=None) -> dict:
    return {"key": key, "label": label, "ok": ok, "detail": detail, "href": href}


def _newest_with(snaps: list, platform: str, *fields):
    """(snapshot, platform dict) of the newest snapshot carrying every field, else (None, None).
    A skipped block is not a reading."""
    for s in snaps:
        p = (s.get("platforms") or {}).get(platform) or {}
        if isinstance(p, dict) and not storage.is_skipped(p) and all(p.get(f) is not None for f in fields):
            return s, p
    return None, None


def _snap_day(snap: dict) -> str:
    return str(snap.get("timestamp", ""))[:10] or "unknown date"


def _snap_href(snap: Optional[dict]) -> Optional[str]:
    if snap and snap.get("_filename"):
        return "stats_snapshots/" + snap["_filename"]
    return None


def _rel(path: Path) -> str:
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


def _file_day(path: Path) -> str:
    try:
        return datetime.fromtimestamp(Path(path).stat().st_mtime).date().isoformat()
    except OSError:
        return "unknown date"


def _age_check(key: str, label: str, stamp: Optional[str], cadence: str, now: datetime,
               noun: str, verb: str, href=None) -> dict:
    """One freshness dot through the registry rule: '7 h, taken 2026-11-05 20:17, max 24 h'."""
    fr = registry.freshness(stamp, cadence, now)
    if fr["stale"] is None:
        return _check(key, label, None, "no %s, max %s" % (noun, fr["window"]), href)
    when = str(stamp)[:16].replace("T", " ")
    return _check(key, label, not fr["stale"], "%s, %s %s, max %s" % (fr["age"], verb, when, fr["window"]), href)


def _health(now: datetime) -> list:
    """Eight checks at `now`; each detail names the as-of date of the number, href the source file."""
    if not isinstance(now, datetime):
        now = datetime.combine(now, time(12, 0))
    today = now.date()
    try:
        snaps = storage.list_snapshots()
    except Exception:
        snaps = []
    out = []

    snap, ig = _newest_with(snaps, "instagram", "followers", "following")
    if ig and _num(ig["following"]) and _num(ig["followers"]) is not None:
        r = float(ig["followers"]) / float(ig["following"])
        out.append(_check("ratio", "Followers to following", r >= 1.0,
                          # counts first: 971 / 973 rounds to "1.00" and still fails the floor
                          "%s / %s = %.3f on %s, floor 1.0" % (
                              f"{int(ig['followers']):,}", f"{int(ig['following']):,}", r, _snap_day(snap)),
                          _snap_href(snap)))
    else:
        out.append(_check("ratio", "Followers to following", None, "no reading, floor 1.0"))

    auto = _read_json(AUTONOMY_FILE)
    scores = [e for e in (auto or {}).get("recent", []) if isinstance(e, dict)
              and e.get("platform") == "ig" and _num(e.get("score")) is not None]
    if scores:
        e = scores[-1]
        out.append(_check("session_score", "Last IG session score", float(e["score"]) >= 8,
                          "%s on %s, min 8" % (e["score"], e.get("date") or "unknown date"), _rel(AUTONOMY_FILE)))
    else:
        out.append(_check("session_score", "Last IG session score", None, "no session, min 8",
                          _rel(AUTONOMY_FILE) if auto is not None else None))

    tl = _read_json(TARGET_LIST_FILE)
    if isinstance(tl, dict):
        n = sum(1 for q in tl.get("queue", []) if isinstance(q, dict) and q.get("status") == "pending" and q.get("audit_date"))
        out.append(_check("vetted_pool", "Vetted target pool", n >= 30,
                          "%d on %s, min 30" % (n, _file_day(TARGET_LIST_FILE)), _rel(TARGET_LIST_FILE)))
    else:
        out.append(_check("vetted_pool", "Vetted target pool", None, "no file, min 30"))

    hk_snap, hk = _newest_with(snaps, "hikerapi", "requests")
    if hk and _num(hk.get("requests")) is not None:
        out.append(_check("hikerapi_balance", "HikerAPI requests left", float(hk["requests"]) > 10000,
                          "{:,} on {}, min 10,000".format(int(float(hk["requests"])), _snap_day(hk_snap)),
                          _snap_href(hk_snap)))
    else:
        why = storage.skipped_in(snaps[0], "hikerapi") if snaps else None
        out.append(_check("hikerapi_balance", "HikerAPI requests left", None,
                          ("skipped, because %s; min 10,000" % why) if why else "no reading, min 10,000"))

    det = _read_json(DETECTIONS_FILE)
    if isinstance(det, dict):
        cut = (today - timedelta(days=7)).isoformat()
        n = 0
        for e in det.get("events", []):
            if isinstance(e, dict) and cut <= str(e.get("date", "")) <= today.isoformat():
                n += int(_num(e.get("count")) or 1)
        out.append(_check("detections", "Detection events, 7 days", n == 0,
                          "%d in the 7 days to %s, max 0" % (n, today.isoformat()), _rel(DETECTIONS_FILE)))
    else:
        out.append(_check("detections", "Detection events, 7 days", None, "no file, max 0"))

    out.append(_age_check("snapshot_age", "Newest stats snapshot", snaps[0].get("timestamp") if snaps else None,
                          "daily", now, "snapshot", "taken", _snap_href(snaps[0]) if snaps else None))

    exp = ig_followback.newest_export_dir(DATA_DIR)
    eday = None
    if exp:
        m = ig_followback._EXPORT_RE.match(exp.name)
        eday = m.group(1) if m else None
    out.append(_age_check("export_age", "Newest IG export", eday, "monthly", now, "export", "export of",
                          _rel(exp) if exp else None))

    try:
        weeks = spotify_s4a.load().get("weeks") or {}
    except Exception:
        weeks = {}
    reads = [str(w["read_at"]) for w in (weeks.values() if isinstance(weeks, dict) else [])
             if isinstance(w, dict) and w.get("read_at")]
    newest = max(reads) if reads else None
    out.append(_age_check("spotify_read_age", "Newest Spotify read", newest, "weekly", now, "read", "read",
                          _rel(spotify_s4a.STORE) if newest else None))
    return out


# ----------------------------------------------------------- ladder chart

def ladder_svg(series: list, m: dict, today: date, period: dict, w: int = 640, h: int = 210) -> str:
    """Plan steps (solid, a dot and a number per rung) under the real line, which ends in a 'now' dot.
    Drawn near its display size so the numbers stay readable."""
    start, end = date.fromisoformat(period["start"]), date.fromisoformat(period["end"])
    span = max((end - start).days, 1)
    base = float(m["baseline"]["value"])
    rungs = sorted((_iso(k), float(v)) for k, v in _clean_metric(m)["rungs"].items())
    inside = [(_iso(p["date"]), float(p["value"])) for p in _clean_series(series)
              if start <= _iso(p["date"]) <= end]
    clean = _clean_series(series)
    newest = (_iso(clean[-1]["date"]), float(clean[-1]["value"])) if clean else None   # may sit just before the period
    vals = [v for _, v in inside] + [base] + [v for _, v in rungs] + ([newest[1]] if newest else [])
    lo, hi = min(vals), max(vals)
    pad = ((hi - lo) or 1) * 0.12
    lo, hi = lo - pad, hi + pad
    left, right, top, bottom = 16, w - 16, 34, h - 30

    def x(d):
        return left + (d - start).days / span * (right - left)

    def y(v):
        return bottom - (v - lo) / (hi - lo) * (bottom - top)

    stair = [(start, base)] + rungs
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img">' % (w, h)]
    out.append('<line class="sb-axis" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (left, bottom + 8, right, bottom + 8))
    out.append('<polyline class="sb-ladder" points="%s"/>' % " ".join("%.1f,%.1f" % (x(d), y(v)) for d, v in stair))
    for i, (d, v) in enumerate(rungs):
        cx, cy = x(d), y(v)
        last = i == len(rungs) - 1
        out.append('<circle class="sb-rung-dot%s" cx="%.1f" cy="%.1f" r="%s"/>' % (" sb-goal" if last else "", cx, cy, "6" if last else "4"))
        out.append('<text class="sb-rung-num" x="%.1f" y="%.1f" text-anchor="%s">%s%s</text>' % (
            cx, cy - 13, "end" if last else "middle", _fmt(v), " goal" if last else ""))
    if len(inside) > 1:
        out.append('<polyline class="sb-line" points="%s"/>' % " ".join("%.1f,%.1f" % (x(d), y(v)) for d, v in inside))
    if newest:
        d, v = newest
        cx, cy = x(min(max(d, start), end)), y(v)
        out.append('<circle class="sb-now" cx="%.1f" cy="%.1f" r="7"/>' % (cx, cy))
        out.append('<text class="sb-now-num" x="%.1f" y="%.1f">%s now</text>' % (cx + 4, cy + 26, _fmt(v)))
    tick = date(start.year, start.month, 1)
    while tick <= end:
        if tick >= start:
            out.append('<text class="sb-tick" x="%.1f" y="%d">%s 1</text>' % (x(tick), h - 6, tick.strftime("%b")))
        tick = date(tick.year + tick.month // 12, tick.month % 12 + 1, 1)
    out.append("</svg>")
    return "".join(out)


# ----------------------------------------------------------------- build

def _now_from(today: Optional[date], now: Optional[datetime]) -> datetime:
    """build(today=...) keeps working for the tests: noon of that day."""
    if now is not None:
        return now
    if today is not None:
        return datetime.combine(today, time(12, 0))
    return datetime.now()


def _frozen_series(frozen: dict) -> dict:
    """{key: [one point]} from a frozen month file (stats/freeze.py)."""
    out = {}
    for key, f in (frozen.get("metrics") or {}).items():
        if isinstance(f, dict) and f.get("raw") is not None and f.get("as_of"):
            out[key] = [{"date": str(f["as_of"])[:10], "value": f["raw"], "as_of": f["as_of"],
                         "source": f.get("source", ""), "run_id": f.get("run_id")}]
        else:
            out[key] = []
    return out


def load_frozen(month: str, gates_dir: Path = None) -> Optional[dict]:
    data = _read_json((gates_dir or GATES_DIR) / ("%s.json" % month))
    return data if isinstance(data, dict) and data.get("month") == month else None


def build(today: Optional[date] = None, now: Optional[datetime] = None, until: Optional[date] = None,
          month: Optional[str] = None) -> dict:
    """The board at `now` (the only clock). `until` reads no point dated after it (the freeze);
    `month` ("2026-11") shows the frozen file instead of live data and raises when there is none."""
    now = _now_from(today, now)
    frozen, frozen_series = None, {}
    if month:
        frozen = load_frozen(month)
        if frozen is None:
            raise ValueError("no frozen month %s: run python3 stats/freeze.py %s" % (month, month))
        now = registry.parse_stamp(frozen.get("cutoff")) or now
        until = now.date()
        frozen_series = _frozen_series(frozen)
    today = now.date()
    targets = load_targets()
    reg = registry.from_targets(targets, strict=True)
    period = targets["period"]
    try:
        newest = None if frozen else storage.load_latest_snapshot()
    except Exception:
        newest = None
    cards, ladders, members = [], [], []
    for key, m in registry.targets_only(reg).items():
        series = frozen_series.get(key, []) if frozen else _upto(series_for(m.get("source", "")), until)
        cards.append(_card(key, m, period, now, series=series, newest=newest))
        members.append((m.get("source", ""), cards[-1]))
        if m["kind"] == "ladder" and (m.get("baseline") or {}).get("value") is not None:
            c = cards[-1]
            goal = sorted((_clean_metric(m).get("rungs") or {}).items())[-1:] or [(period["end"], m.get("target"))]
            gd = _iso(goal[0][0])
            ladders.append({"key": key, "label": m["label"], "light": c["light"], "line": c["rung_line"],
                            "now": c["value"], "unit": c["unit"], "goal": _fmt(goal[0][1]), "proposed": c["proposed"],
                            "goal_when": "%s %d" % (gd.strftime("%b"), gd.day) if gd else goal[0][0],
                            "svg": ladder_svg(_recent(series, today, 120), m, today, period)})
    health = [] if frozen else _health(now)
    trends = []
    for key, t in registry.trends_only(reg).items():
        s = frozen_series.get(key, []) if frozen else _upto(series_for(t["source"]), until)
        last = s[-1] if s else None
        fr = registry.freshness((last.get("as_of") or last["date"]) if last else None, t["cadence"], now)
        trends.append({"key": key, "label": t["label"], "value": _fmt(last["value"]) if last else "",
                       "points": sparkline(_recent(s, today)), "as_of": last["date"] if last else None,
                       "source": (last.get("source") if last else None) or t["source"],
                       "run_id": last.get("run_id") if last else None,
                       "stale": bool(fr["stale"]), "age": fr["age"], "window": fr["window"],
                       "who": who_for(t["source"])[0], "who_text": who_for(t["source"])[1]})
        members.append((t["source"], trends[-1]))
    return {"score": _score(cards), "cards": cards, "health": health, "freshness": freshness_strip(members, now),
            "health_summary": {"pass": sum(1 for h in health if h["ok"] is True), "total": len(health)},
            "trends": trends, "ladders": ladders, "now": now.isoformat(timespec="seconds"),
            "frozen": {"month": frozen["month"], "as_of": str(frozen.get("as_of") or "")[:10],
                       "frozen_at": str(frozen.get("frozen_at") or "")[:16].replace("T", " ")} if frozen else None}
