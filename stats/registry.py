"""One registry for every metric on the score board (M11 part 1, 2026-11-06).

plans/targets.json stays the file Amir edits: period, baselines, rungs, floors, the approval
stamp. This module adds what that file does not say and validates it. For every metric:
key, label, unit, source kind + path, cadence, direction, freshness window, how pace is
computed, area. Trend-only metrics (no target) live here too, so no page keeps a list of
its own: the score board, the daily brief, the socials digest and propose_targets all read
this. tests/test_registry.py fails when a metric exists in one place and not the other.

Freshness, one rule for every reader: a reading is stale when it is older than the window
of its cadence (the Gero habit "red when older than 24 h", weekly sources get their own
stated window).
  daily    24 h       the 08:45 sync (stats_snapshots/snapshot_*.json)
  weekly   240 h      the Monday Spotify for Artists read, the Monday reach screenshot (10 days)
  monthly  960 h      the IG All-time export behind the follow-back file (40 days)
  manual   1488 h     numbers typed in by hand about once a month (62 days, twice the gap)
  none                a release read (day 28) is never stale
A date-only stamp counts in whole days from the date of `now`; a timestamp counts in hours.

Every rule function takes `now`. Nothing in this module reads the clock or the network.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

from stats.targets import TARGETS_PATH, load_targets

CADENCES = ("daily", "weekly", "monthly", "manual", "none")
WINDOW_HOURS = {"daily": 24, "weekly": 240, "monthly": 960, "manual": 1488, "none": None}
SOURCE_KINDS = ("snapshot", "manual", "s4a", "followback", "release")
DEFAULT_CADENCE = {"snapshot": "daily", "manual": "manual", "s4a": "weekly", "followback": "monthly", "release": "none"}
DIRECTIONS = ("up", "down")
PACES = ("ladder", "floor", "none", "trend")
AREAS = ("Release", "Socials", "Booking", "Income", "Studio", "System")

# What targets.json does not say, per metric key. Every key in targets.json needs a row here
# and every row here needs a key there (the parity test). `short` is the word the brief and
# the digest print; `digest` marks the rows of the 🎬 Socials goals line.
META = {
    "ig_followers": {"cadence": "daily", "direction": "up", "area": "Socials", "short": "IG", "digest": True},
    "ig_followback_pct": {"cadence": "monthly", "direction": "up", "area": "Socials", "short": "IG follow-back"},
    "ig_reach_30d": {"cadence": "weekly", "direction": "up", "area": "Socials", "short": "IG reach"},
    "sc_followers": {"cadence": "daily", "direction": "up", "area": "Socials", "short": "SC", "digest": True},
    "spotify_monthly_active": {"cadence": "weekly", "direction": "up", "area": "Release", "short": "Spotify listeners"},
    "tiktok_followers": {"cadence": "manual", "direction": "up", "area": "Socials", "short": "TikTok"},
    "spotify_followers": {"cadence": "weekly", "direction": "up", "area": "Release", "short": "Spotify followers"},
    "email_list": {"cadence": "manual", "direction": "up", "area": "Release", "short": "Email list"},
    "release_engagement_d28": {"cadence": "none", "direction": "up", "area": "Release", "short": "Release d28"},
}

# Trend-only metrics: a number and a sparkline, no target, never in the verdict.
TRENDS = {
    "yt_subscribers": {"label": "YouTube subscribers", "unit": "subscribers", "source": "snapshot:youtube.subscribers",
                       "cadence": "daily", "direction": "up", "area": "Socials", "short": "YouTube"},
    "bandcamp_followers": {"label": "Bandcamp followers", "unit": "followers", "source": "manual:bandcamp.followers",
                           "cadence": "manual", "direction": "up", "area": "Socials", "short": "Bandcamp"},
}


# ---------------------------------------------------------------- entries

def source_parts(source: str) -> tuple:
    """('snapshot', 'instagram.followers') from the first alternative of a source string."""
    first = str(source or "").split("|")[0].strip()
    kind, _, path = first.partition(":")
    return kind, path


def default_cadence(source: str) -> str:
    return DEFAULT_CADENCE.get(source_parts(source)[0], "none")


def pace_for(kind: str) -> str:
    return {"ladder": "ladder", "floor": "floor", "trend": "trend"}.get(kind, "none")


def entry(key: str, metric: dict, meta: Optional[dict] = None) -> dict:
    """One registry row: the targets.json metric plus the meta, with every field filled."""
    meta = meta or {}
    source = metric.get("source") or meta.get("source") or ""
    kind = metric.get("kind") or meta.get("kind") or "collecting"
    cadence = meta.get("cadence") or metric.get("cadence") or default_cadence(source)
    row = dict(metric)
    row.update({
        "key": key,
        "label": metric.get("label") or meta.get("label") or key,
        "unit": metric.get("unit") or meta.get("unit") or "",
        "kind": kind,
        "pace": pace_for(kind),
        "source": source,
        "source_kind": source_parts(source)[0],
        "source_path": source_parts(source)[1],
        "cadence": cadence,
        "fresh_hours": WINDOW_HOURS.get(cadence),
        "direction": meta.get("direction") or metric.get("direction") or "up",
        "area": meta.get("area") or metric.get("area") or "Socials",
        "short": meta.get("short") or metric.get("label") or key,
        "digest": bool(meta.get("digest")),
    })
    return row


def from_targets(targets: dict, strict: bool = False) -> dict:
    """{key: entry} in targets.json order, then the trend-only rows.

    strict=True raises on any parity problem (a targets key without META, a META key without
    a target, a trend key that collides with a target)."""
    problems = check(targets) if strict else []
    if problems:
        raise ValueError("metric registry out of sync: " + "; ".join(problems))
    out = {}
    for key, m in (targets.get("metrics") or {}).items():
        if isinstance(m, dict):
            out[key] = entry(key, m, META.get(key))
    for key, t in TRENDS.items():
        if key not in out:
            out[key] = entry(key, dict(t, kind="trend"), t)
    return out


def check(targets: dict) -> list:
    """Parity and field problems between targets.json and this registry (empty = fine)."""
    keys = set((targets.get("metrics") or {}).keys())
    problems = []
    for key in sorted(keys - set(META)):
        problems.append("%s is in targets.json but not in stats/registry.py META" % key)
    for key in sorted(set(META) - keys):
        problems.append("%s is in stats/registry.py META but not in targets.json" % key)
    for key in sorted(keys & set(TRENDS)):
        problems.append("%s is both a target and a trend-only row" % key)
    for key, meta in list(META.items()) + list(TRENDS.items()):
        if meta.get("cadence") not in CADENCES:
            problems.append("%s: cadence must be one of %s" % (key, ", ".join(CADENCES)))
        if meta.get("direction") not in DIRECTIONS:
            problems.append("%s: direction must be up or down" % key)
        if meta.get("area") not in AREAS:
            problems.append("%s: area must be one of %s" % (key, ", ".join(AREAS)))
    for key, m in (targets.get("metrics") or {}).items():
        kind = source_parts((m or {}).get("source", ""))[0]
        if kind not in SOURCE_KINDS:
            problems.append("%s: source kind '%s' is not one of %s" % (key, kind, ", ".join(SOURCE_KINDS)))
    for key, t in TRENDS.items():
        if source_parts(t.get("source", ""))[0] not in SOURCE_KINDS:
            problems.append("%s: trend source kind unknown" % key)
    return problems


def load_registry(path: Path = TARGETS_PATH) -> dict:
    """The registry for the real targets file, validated both ways."""
    return from_targets(load_targets(path), strict=True)


def targets_only(registry: dict) -> dict:
    """The rows that carry (or wait for) a target: everything but the trend-only rows."""
    return {k: v for k, v in registry.items() if v["pace"] != "trend"}


def trends_only(registry: dict) -> dict:
    return {k: v for k, v in registry.items() if v["pace"] == "trend"}


def digest_rows(registry: dict) -> list:
    """[(key, short, platform)] for the 🎬 Socials goals line, from the rows flagged digest."""
    out = []
    for key, e in registry.items():
        if e.get("digest") and e["source_kind"] == "snapshot":
            out.append((key, e["short"], e["source_path"].partition(".")[0]))
    return out


# ---------------------------------------------------------------- readings

def reading(value, as_of, source: str = "", run_id: Optional[str] = None) -> dict:
    """The provenance shape every reading carries: value, as_of, source, run_id."""
    return {"value": value, "as_of": as_of, "source": source or "", "run_id": run_id}


def is_skipped(block) -> bool:
    """A platform block the collector could not read: {"skipped": "<reason>"}; never a 0."""
    return isinstance(block, dict) and "skipped" in block


def skipped_reason(block) -> Optional[str]:
    return str(block.get("skipped")) if is_skipped(block) else None


# ---------------------------------------------------------------- freshness

def parse_stamp(stamp) -> Optional[datetime]:
    """datetime from an ISO stamp (date or timestamp); None when malformed. A bare date is midnight."""
    s = str(stamp or "").strip()
    if not s:
        return None
    try:
        if len(s) <= 10:
            return datetime.combine(date.fromisoformat(s), datetime.min.time())
        return datetime.fromisoformat(s[:19])
    except ValueError:
        return None


def age_hours(as_of, now: datetime) -> Optional[float]:
    """Hours between a reading and `now`; a date-only stamp counts whole days from the date of now."""
    t = parse_stamp(as_of)
    if t is None:
        return None
    if len(str(as_of).strip()) <= 10:
        return max(0, (now.date() - t.date()).days) * 24.0
    return max(0.0, (now - t).total_seconds() / 3600.0)


def hours_text(hours: Optional[float]) -> str:
    if hours is None:
        return "unknown age"
    if hours < 1:
        return "under 1 h"
    if hours < 48:
        return "%d h" % int(hours)
    return "%d days" % int(hours // 24)


def window_text(window_hours: Optional[int]) -> str:
    if window_hours is None:
        return "never stale"
    return "%d h" % window_hours if window_hours <= 48 else "%d days" % (window_hours // 24)


def freshness(as_of, cadence: str, now: datetime) -> dict:
    """{stale, age_hours, age, window, cadence}. stale is None when there is no reading or no window."""
    window = WINDOW_HOURS.get(cadence)
    hours = age_hours(as_of, now)
    stale = None if (hours is None or window is None) else hours > window
    return {"stale": stale, "age_hours": hours, "age": hours_text(hours) if hours is not None else "",
            "window": window_text(window), "cadence": cadence}


# ---------------------------------------------------------------- verdict

def verdict(lights: list) -> str:
    """COLLECTING when nothing has data; OFF PACE when any card is red; else ON PACE.

    One red card (behind its ladder, under its floor, or stale) is enough: the majority rule
    that could print ON PACE next to a red card is gone (M11, 2026-11-06)."""
    with_data = [l for l in lights if l in ("green", "amber", "red")]
    if not with_data:
        return "COLLECTING"
    return "OFF PACE" if "red" in with_data else "ON PACE"
