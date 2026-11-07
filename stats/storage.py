"""
stats/storage.py
-----------------
JSON snapshot storage for stats data. Each sync creates a timestamped snapshot.
Supports manual entry for platforms without APIs (Bandcamp, Beatport, Apple Music).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from scene_intelligence.json_io import atomic_write_json, load_json_checked

BASE_DIR = Path(__file__).parent.parent
SNAPSHOTS_DIR = BASE_DIR / "stats_snapshots"
MANUAL_FILE = Path(os.getenv("STATS_MANUAL_FILE", SNAPSHOTS_DIR / "manual_entries.json"))
MANUAL_PLATFORMS = ("bandcamp", "beatport", "apple_music", "instagram_insights", "tiktok", "email_list")


def ensure_dir():
    SNAPSHOTS_DIR.mkdir(exist_ok=True)


# Provenance (M11, 2026-11-06): every snapshot carries a run_id, every platform block an
# as_of stamp and a source word. A block the collector could not read is {"skipped": reason}.
DEFAULT_SOURCES = {"spotify": "spotify_api", "soundcloud": "soundcloud_api", "youtube": "youtube_data_api",
                   "instagram": "hikerapi", "hikerapi": "hikerapi"}


def stamp_provenance(data: dict, now: datetime, run_id: str) -> dict:
    """The snapshot body with run_id at the top and as_of + source on every platform block."""
    out = dict(data)
    out["run_id"] = run_id
    platforms = {}
    for name, block in (data.get("platforms") or {}).items():
        if isinstance(block, dict):
            block = dict(block)
            block.setdefault("as_of", now.isoformat(timespec="seconds"))
            if "skipped" not in block:
                block.setdefault("source", DEFAULT_SOURCES.get(name, name))
        platforms[name] = block
    out["platforms"] = platforms
    return out


def save_snapshot(data: dict, now: datetime | None = None, run: str = "sync") -> str:
    """Save a stats snapshot. Returns the filename."""
    ensure_dir()
    now = now or datetime.now()
    ts = now.strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"snapshot_{ts}.json"
    snapshot = {
        "timestamp": now.isoformat(timespec="seconds"),
        **stamp_provenance(data, now, f"{run}:{ts}"),
    }
    filepath = SNAPSHOTS_DIR / filename
    atomic_write_json(filepath, snapshot)
    return filename


def is_skipped(block) -> bool:
    """A platform block the collector could not read ({"skipped": reason}): not collected, never 0."""
    return isinstance(block, dict) and "skipped" in block


def skipped_in(snapshot: dict | None, platform: str) -> str | None:
    """The skip reason for a platform in a snapshot, None when it was read (or absent)."""
    block = ((snapshot or {}).get("platforms") or {}).get(platform)
    return str(block.get("skipped")) if is_skipped(block) else None


def list_snapshots() -> list[dict]:
    """List all snapshots sorted by timestamp (newest first)."""
    ensure_dir()
    snapshots = []
    for f in sorted(SNAPSHOTS_DIR.glob("snapshot_*.json"), reverse=True):
        try:
            with open(f) as fh:
                data = json.load(fh)
            data["_filename"] = f.name
            snapshots.append(data)
        except Exception:
            continue
    return snapshots


def load_latest_snapshot() -> dict | None:
    """Load the most recent snapshot."""
    snapshots = list_snapshots()
    return snapshots[0] if snapshots else None


def load_snapshot(filename: str) -> dict | None:
    """Load a specific snapshot by filename."""
    filepath = SNAPSHOTS_DIR / filename
    if not filepath.exists():
        return None
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Manual entries (Bandcamp, Beatport, Apple Music)
# ---------------------------------------------------------------------------

def load_manual_entries() -> dict:
    """Load manual platform entries. Corrupt-existing file = hard stop
    (audit P2-10): the old empty fallback + save_manual_entry clobbered
    the whole history."""
    ensure_dir()
    return load_json_checked(MANUAL_FILE, {"entries": []},
                             what="manual stats entries")


def save_manual_entry(platform: str, data: dict, date: str | None = None, source: str = "manual:amir") -> dict:
    """Add a manual entry for a platform (Bandcamp, Beatport, Apple Music).

    data can include: followers, plays, sales, revenue, chart_position, notes
    date: optional "YYYY-MM-DD" overriding today (ValueError if malformed).
    source: who or what read the number (manual:amir, cli:s4a-read, import:bandcamp-csv).
    """
    if date is not None:
        datetime.strptime(date, "%Y-%m-%d")
    else:
        date = datetime.now().strftime("%Y-%m-%d")
    entries = load_manual_entries()
    entry = {
        "platform": platform,
        "date": date,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        **data,
    }
    entries["entries"].append(entry)
    ensure_dir()
    atomic_write_json(MANUAL_FILE, entries)
    return entry


def get_manual_latest(platform: str) -> dict | None:
    """Get the most recent manual entry for a platform."""
    entries = load_manual_entries()
    platform_entries = [e for e in entries["entries"] if e["platform"] == platform]
    return platform_entries[-1] if platform_entries else None


# ---------------------------------------------------------------------------
# Time-series helpers
# ---------------------------------------------------------------------------

def get_readings(platform: str, metric: str, days: int = 30, now: datetime | None = None) -> list[dict]:
    """The time series of one platform metric with provenance on every point:
    {"date", "value", "as_of", "source", "run_id"}. A skipped block is not a reading.
    """
    from datetime import timedelta
    now = now or datetime.now()
    cutoff = now - timedelta(days=days)

    snapshots = list_snapshots()
    series = []
    seen_dates = set()

    # Snapshots are listed newest first: the first value seen for a date is
    # the newest reading of that day. A date counts as seen only when a value
    # was actually taken, so snapshots without this platform (or with a skipped
    # block) never block a later reading or a manual entry.
    for snap in snapshots:
        ts_str = snap.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except Exception:
            continue
        if ts < cutoff:
            continue

        date_str = ts.strftime("%Y-%m-%d")
        if date_str in seen_dates:
            continue
        platform_data = (snap.get("platforms") or {}).get(platform) or {}
        if is_skipped(platform_data) or not isinstance(platform_data, dict):
            continue
        value = platform_data.get(metric)
        if value is not None:
            seen_dates.add(date_str)
            series.append({"date": date_str, "value": value,
                           "as_of": platform_data.get("as_of") or ts_str,
                           "source": platform_data.get("source") or DEFAULT_SOURCES.get(platform, platform),
                           "run_id": snap.get("run_id")})

    # Also include manual entries for manual platforms (only for dates
    # without a snapshot value for this platform)
    if platform in MANUAL_PLATFORMS:
        manual = load_manual_entries()
        for entry in reversed(manual["entries"]):  # newest entry of a day wins
            if entry.get("platform") != platform:
                continue
            date_str = entry.get("date", "")
            if date_str in seen_dates:
                continue
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                continue
            if entry_date < cutoff:
                continue
            value = entry.get(metric)
            if value is not None:
                seen_dates.add(date_str)
                series.append({"date": date_str, "value": value, "as_of": date_str,
                               "source": entry.get("source") or "manual",
                               "run_id": ("manual:" + str(entry["timestamp"])) if entry.get("timestamp") else None})

    series.sort(key=lambda x: x["date"])
    return series


def get_time_series(platform: str, metric: str, days: int = 30) -> list[dict]:
    """Extract a time series for a specific platform metric across snapshots.

    Returns list of {"date": "2026-04-03", "value": 123} (get_readings without the provenance).
    """
    return [{"date": p["date"], "value": p["value"]} for p in get_readings(platform, metric, days)]


def get_growth(current: dict, previous: dict) -> dict:
    """Compare two snapshots and return per-platform growth deltas.

    Returns {"spotify": {"catalog_size": +1}, "soundcloud": {"followers": +3, ...}, ...}
    """
    growth = {}
    cur_platforms = current.get("platforms", {})
    prev_platforms = previous.get("platforms", {}) if previous else {}

    # Metrics to compare per platform
    metric_keys = {
        "spotify": ["catalog_size"],   # followers/popularity left the snapshot 2026-11-05 (S4A is the source)
        "soundcloud": ["followers", "total_plays", "total_likes", "total_reposts"],
        "youtube": ["subscribers", "total_views", "total_likes"],
        "instagram": ["followers", "media_count", "recent_reach"],
    }

    for platform, keys in metric_keys.items():
        cur = cur_platforms.get(platform, {})
        prev = prev_platforms.get(platform, {})
        deltas = {}
        for key in keys:
            cur_val = cur.get(key)
            prev_val = prev.get(key)
            if cur_val is not None and prev_val is not None:
                deltas[key] = cur_val - prev_val
        if deltas:
            growth[platform] = deltas

    return growth


def get_overview() -> dict:
    """Build an overview combining latest API snapshot + latest manual entries + growth."""
    snapshots = list_snapshots()
    latest = snapshots[0] if snapshots else None
    previous = snapshots[1] if len(snapshots) > 1 else None
    platforms = latest.get("platforms", {}) if latest else {}
    timestamp = latest.get("timestamp", "") if latest else ""

    # Add manual platform latest
    for mp in MANUAL_PLATFORMS:
        entry = get_manual_latest(mp)
        if entry:
            platforms[mp] = entry

    # Growth comparison
    growth = get_growth(latest, previous) if latest and previous else {}

    return {
        "platforms": platforms,
        "last_synced": timestamp,
        "growth": growth,
    }
