"""Monthly freeze of the score board (M11, 2026-11-06): every registry metric "as of" the
last day of the month, written once so the month's numbers never move again.

    python3 stats/freeze.py 2026-11            # writes stats_snapshots/gates/2026-11.json
    python3 stats/freeze.py 2026-11 --print    # prints only
    python3 stats/freeze.py 2026-11 --force    # rewrite an existing month (the numbers must not change)

Runs by hand on the 1st of the month (monthly upkeep, not scheduled). It reads nothing dated
after the cutoff, so freezing again later reproduces the same numbers. The score board shows a
frozen month with /stats?month=2026-11. Nothing here touches engagement code or state.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scene_intelligence.json_io import atomic_write_json  # noqa: E402

GATES_DIR = ROOT / "stats_snapshots" / "gates"
KEEP = ("value", "raw", "as_of", "source", "run_id", "light", "light_text", "rung_line", "progress",
        "unit", "label", "stale", "age", "window", "cadence", "proposed")


def cutoff_of(month: str) -> datetime:
    """23:59:59 on the last day of 'YYYY-MM' (ValueError when malformed)."""
    y, m = str(month).split("-")
    y, m = int(y), int(m)
    if not 1 <= m <= 12:
        raise ValueError("month must be YYYY-MM")
    return datetime.combine(date(y, m, calendar.monthrange(y, m)[1]), time(23, 59, 59))


def build_frozen(month: str, now: datetime) -> dict:
    """The frozen document: the board at the cutoff, reading no point dated after it.

    Raises ValueError when the month is not over at `now`."""
    from release_manager import score_board
    cutoff = cutoff_of(month)
    if cutoff > now:
        raise ValueError("%s is not over on %s; freeze it on the 1st" % (month, now.date().isoformat()))
    board = score_board.build(now=cutoff, until=cutoff.date())
    metrics = {}
    for c in board["cards"]:
        metrics[c["key"]] = {k: c.get(k) for k in KEEP}
        metrics[c["key"]]["as_of"] = c.get("as_of_full") or c.get("as_of")   # the full stamp, not just the day
    for t in board["trends"]:
        metrics[t["key"]] = {"value": t["value"], "raw": None, "as_of": t["as_of"], "source": t.get("source"),
                             "run_id": t.get("run_id"), "light": "trend", "light_text": "trend only",
                             "label": t["label"], "stale": t.get("stale"), "age": t.get("age"), "window": t.get("window")}
        try:
            metrics[t["key"]]["raw"] = float(str(t["value"]).replace(",", "")) if t["value"] else None
        except ValueError:
            metrics[t["key"]]["raw"] = None
    return {"month": month, "cutoff": cutoff.isoformat(timespec="seconds"), "as_of": cutoff.date().isoformat(),
            "frozen_at": now.isoformat(timespec="seconds"), "run_id": "freeze:%s:%s" % (month, now.strftime("%Y-%m-%dT%H-%M-%S")),
            "score": board["score"], "metrics": metrics}


def numbers_of(doc: dict) -> dict:
    """{key: (raw, as_of)}: what must not change between two freezes of the same month."""
    return {k: (m.get("raw"), m.get("as_of")) for k, m in (doc.get("metrics") or {}).items()}


def freeze(month: str, now: datetime, gates_dir: Path = GATES_DIR, write: bool = True, force: bool = False) -> dict:
    """Write stats_snapshots/gates/<month>.json. An existing month is kept unless `force`;
    a forced rewrite with different numbers raises (the frozen month is the record)."""
    doc = build_frozen(month, now)
    path = Path(gates_dir) / ("%s.json" % month)
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            old = None
        if isinstance(old, dict) and not force:
            return old
        if isinstance(old, dict) and numbers_of(old) != numbers_of(doc):
            raise ValueError("%s is already frozen with other numbers; not rewritten" % month)
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(path, doc)
    return doc


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    month = args[0]
    try:
        doc = freeze(month, datetime.now(), write="--print" not in argv, force="--force" in argv)
    except ValueError as e:
        print("Not frozen: %s" % e)
        return 1
    print("%s frozen as of %s (%s)" % (month, doc["as_of"], doc["score"]["line"]))
    for key, m in doc["metrics"].items():
        print("  %-26s %-10s %-8s as of %s  %s" % (key, m.get("value") or "(none)", m.get("light"), m.get("as_of") or "-", m.get("source") or ""))
    if "--print" not in argv:
        print("  written: %s" % (GATES_DIR / ("%s.json" % month)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
