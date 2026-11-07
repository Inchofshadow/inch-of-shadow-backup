"""Propose score board targets from the data (prints only) and set the Instagram baseline once.

    python3 stats/propose_targets.py                   print the proposal, never writes
    python3 stats/propose_targets.py --set-ig-baseline one-shot write of the ig_followers baseline
        (the earliest snapshot reading of instagram.followers on or after period.start, and its date;
         --date YYYY-MM-DD and --value N override)
"""
from __future__ import annotations

import calendar
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scene_intelligence.json_io import atomic_write_json
from stats.targets import TARGETS_PATH, load_targets


def six_month_rate(series: list, end: date, exclude: Optional[Tuple[str, str]] = None) -> Optional[float]:
    """Per-30.4-day rate from the first to the last reading in the 183 days ending at `end`."""
    start = end - timedelta(days=183)
    rows = []
    for r in series:
        d = date.fromisoformat(r["date"])
        if not (start <= d <= end):
            continue
        if exclude and exclude[0] <= r["date"] <= exclude[1]:
            continue
        rows.append((d, r["value"]))
    rows.sort()
    if len(rows) < 2:
        return None
    days = (rows[-1][0] - rows[0][0]).days
    if days <= 0:
        return None
    return (rows[-1][1] - rows[0][1]) / (days / 30.4)


def round5(x: float) -> int:
    return int(5 * round(x / 5))


def _month_end(d: date) -> date:
    return date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])


def _spotify_numbers(today: date) -> Optional[Tuple[float, float]]:
    from stats import spotify_s4a
    weeks = spotify_s4a.load().get("weeks", {})
    cut = (today - timedelta(days=183)).isoformat()
    vals = [weeks[k]["monthly_active"] for k in sorted(weeks) if k >= cut and weeks[k].get("monthly_active") is not None]
    if len(vals) < 4:
        return None
    last12 = vals[-12:]
    mean12 = sum(last12) / len(last12)
    best4 = max(sum(vals[i:i + 4]) / 4 for i in range(len(vals) - 3))
    return mean12, best4


def propose(today: date) -> dict:
    from stats import registry, storage
    metrics = registry.targets_only(registry.load_registry())   # the one registry over targets.json (M11)
    out = {}
    for key, m in metrics.items():
        rule = m.get("rule", "")
        head = "%s [%s, %s, %s] rule: %s" % (key, m["kind"], m["cadence"], m["source"], rule)
        if key == "ig_followers":
            series = storage.get_time_series("instagram", "followers", 400)
            rate = six_month_rate(series, today)
            latest = series[-1]["value"] if series else None
            if rate is None or latest is None:
                text = "no Instagram readings yet"
            else:
                r = round5(rate)
                text = "latest %s, rate %.1f/month -> %d; rungs %s, %s" % (latest, rate, r, latest + r, latest + 2 * r)
                out[key] = {"latest": latest, "rate": r}
        elif key == "spotify_monthly_active":
            nums = _spotify_numbers(today)
            if nums is None:
                text = "not enough S4A weeks"
            else:
                text = "12-week mean %.2f -> %d; best 4-week mean %.2f -> %d" % (nums[0], round5(nums[0]), nums[1], round5(nums[1]))
                out[key] = {"nov": round5(nums[0]), "dec": round5(nums[1])}
        elif key == "sc_followers":
            text = "SC-07 ladder, unchanged"
        elif m["kind"] == "floor":
            text = "floor %s" % m.get("floor")
        else:
            text = "collecting"
        print("%s\n    proposed: %s" % (head, text))
    return out


def set_ig_baseline(value: int, on: date, path: Path = TARGETS_PATH) -> dict:
    data = load_targets(path)
    m = data["metrics"]["ig_followers"]
    if (m.get("baseline") or {}).get("value") is not None:
        raise RuntimeError("baseline already set")
    rate = m.get("rate_per_month")
    if rate is None:
        raise ValueError("ig_followers needs 'rate_per_month' in the targets file")
    end = date.fromisoformat(data["period"]["end"])
    if on > end:
        raise ValueError("baseline date %s is after the period end %s" % (on.isoformat(), end.isoformat()))
    first = _month_end(on)
    rungs = {first.isoformat(): value + rate}
    if first != end:
        rungs[end.isoformat()] = value + 2 * rate
    m["baseline"] = {"value": value, "date": on.isoformat()}
    m["rungs"] = rungs
    m["target"] = list(rungs.values())[-1]
    atomic_write_json(path, data)
    return data


def earliest_ig_reading(snaps: list, start: date) -> Optional[Tuple[int, date]]:
    """(followers, date) of the earliest snapshot with platforms.instagram.followers on or after start."""
    best = None
    for snap in snaps:
        value = ((snap.get("platforms") or {}).get("instagram") or {}).get("followers")
        try:
            day = date.fromisoformat(str(snap.get("timestamp", ""))[:10])
        except ValueError:
            continue
        if value is None or day < start:
            continue
        stamp = str(snap.get("timestamp", ""))
        if best is None or stamp < best[0]:
            best = (stamp, int(value), day)
    return (best[1], best[2]) if best else None


def _arg(argv: list, flag: str) -> Optional[str]:
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
        raise SystemExit("%s needs a value" % flag)
    return None


def main(argv: list) -> int:
    if "--set-ig-baseline" in argv:
        from stats import storage
        start = date.fromisoformat(load_targets()["period"]["start"])
        reading = earliest_ig_reading(storage.list_snapshots(), start)
        value_arg, date_arg = _arg(argv, "--value"), _arg(argv, "--date")
        value = int(value_arg) if value_arg is not None else (reading[0] if reading else None)
        on = date.fromisoformat(date_arg) if date_arg is not None else (reading[1] if reading else None)
        if value is None or on is None:
            print("No Instagram follower reading on or after %s; run the daily sync first or pass --value and --date." % start)
            return 1
        data = set_ig_baseline(value, on)
        print(data["metrics"]["ig_followers"])
        return 0
    propose(date.today())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
