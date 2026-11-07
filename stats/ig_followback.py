"""Follow-back rate of the automation's monthly follow cohorts.

Matches the follow tracker (read only) against the follower list in the
newest All-time Instagram data export under data/.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scene_intelligence.json_io import atomic_write_json  # noqa: E402

TRACKER = ROOT / "scene_intelligence" / "ig_follow_tracker.json"
DATA_DIR = ROOT / "data"
OUT = ROOT / "stats_snapshots" / "ig_followback.json"
FOLLOWERS_FILE = Path("connections") / "followers_and_following" / "followers_1.json"
_EXPORT_RE = re.compile(r"^instagram-inch_of_shadow-(\d{4}-\d{2}-\d{2})-")


def _norm(handle: str) -> str:
    return handle.strip().lstrip("@").lower()


def cohorts(tracker: dict, followers: set[str], export_date: str) -> dict[str, dict]:
    """Per follow-month counts: followed, back, pct (None for the export month and after)."""
    followers = {_norm(f) for f in followers}
    counts: dict[str, list[int]] = {}
    entries = [(e, "followed_at") for e in tracker.get("active_follows", [])]
    entries += [(e, "followed_date") for e in tracker.get("unfollowed_history", [])]
    for entry, field in entries:
        day = entry.get(field)
        if not day:
            continue
        month = str(day)[:7]
        row = counts.setdefault(month, [0, 0])
        row[0] += 1
        if _norm(entry.get("username", "")) in followers:
            row[1] += 1
    export_month = export_date[:7]
    out: dict[str, dict] = {}
    for month in sorted(counts):
        followed, back = counts[month]
        # No pct after the export, and none for the export month itself: it is
        # still running, so its counts are kept but its rate would mislead.
        pct = None if month >= export_month else round(100.0 * back / followed, 1)
        out[month] = {"followed": followed, "back": back, "pct": pct}
        if month == export_month:
            out[month]["partial"] = True
    return out


def since_may_pct(cohort_map: dict, start: str = "2026-05") -> float | None:
    """Pooled follow-back percent for completed cohorts from start.

    The 2026-10-10 analysis counted May to September (319 follows, 72 back, 23%)
    and left the still-running export month out (flagged "partial" by cohorts).
    Cohorts after the export (pct None) are excluded too.
    """
    rows = [v for k, v in cohort_map.items()
            if k >= start and v["pct"] is not None and not v.get("partial")]
    followed = sum(v["followed"] for v in rows)
    if not followed:
        return None
    return round(100.0 * sum(v["back"] for v in rows) / followed, 1)


def newest_export_dir(data_dir: Path) -> Path | None:
    best = None
    for d in Path(data_dir).glob("instagram-inch_of_shadow-*"):
        m = _EXPORT_RE.match(d.name)
        if d.is_dir() and m and (best is None or m.group(1) > best[0]):
            best = (m.group(1), d)
    return best[1] if best else None


def followers_from_export(export_dir: Path) -> set[str]:
    data = json.loads((Path(export_dir) / FOLLOWERS_FILE).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("relationships_followers", [])
    handles = set()
    for item in data:
        for sd in item.get("string_list_data", []):
            if sd.get("value"):
                handles.add(_norm(sd["value"]))
    return handles


def write(out: Path = OUT) -> dict:
    export = newest_export_dir(DATA_DIR)
    if export is None:
        raise FileNotFoundError("no instagram-inch_of_shadow-* export under data/")
    export_date = _EXPORT_RE.match(export.name).group(1)
    tracker = json.loads(TRACKER.read_text(encoding="utf-8"))
    c = cohorts(tracker, followers_from_export(export), export_date)
    result = {
        "export_date": export_date,
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "source": "export:%s + ig_follow_tracker" % export_date,   # provenance stamp (M11)
        "cohorts": c,
        "since_may_pct": since_may_pct(c),
    }
    atomic_write_json(out, result)
    return result


def main() -> None:
    r = write()
    print("export:", r["export_date"])
    for month, v in r["cohorts"].items():
        pct = "n/a" if v["pct"] is None else "%s%%" % v["pct"]
        print("%s  followed %4d  back %4d  %s" % (month, v["followed"], v["back"], pct))
    print("since May: %d%%" % round(r["since_may_pct"] or 0))


if __name__ == "__main__":
    main()
