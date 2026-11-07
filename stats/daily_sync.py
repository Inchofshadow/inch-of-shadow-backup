"""
stats/daily_sync.py
--------------------
Daily stats sync script. Collects data from all platform APIs
and saves a snapshot. Designed to run via cron/launchd.

Usage:
    python3 stats/daily_sync.py                      # every platform (the 08:45 launchd default since 2026-11-05;
                                                     #  Instagram = 1 HikerAPI profile read, claimed in the IG daily ledger)
    python3 stats/daily_sync.py --skip instagram     # was the scheduled default 2026-09-30 to 2026-11-05
    (on Mondays it also writes the weekly summary, stats/weekly_summary.py; --weekly forces it)
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on path
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from stats.collectors import collect_all
from stats.storage import save_snapshot


def refresh_followback(data_dir: Path = Path(_project_root) / "data") -> bool:
    """Rewrite stats_snapshots/ig_followback.json when a newer IG export sits under data/.

    Missing file = refresh. Local files only. A failure prints a line and never breaks the sync.
    Returns True when the file was rewritten.
    """
    try:
        import json
        from stats import ig_followback
        export = ig_followback.newest_export_dir(data_dir)
        if export is None:
            return False
        m = ig_followback._EXPORT_RE.match(export.name)
        newest = m.group(1) if m else None
        try:
            current = json.loads(ig_followback.OUT.read_text(encoding="utf-8")).get("export_date")
        except (OSError, ValueError, AttributeError):
            current = None
        if newest and (current is None or newest > str(current)):
            ig_followback.write()
            print(f"  Follow-back refreshed from the {newest} export")
            return True
        return False
    except Exception as e:                           # noqa: BLE001 - the sync itself must finish
        print(f"  Follow-back refresh failed: {e}")
        return False


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] Stats daily sync starting...")

    skip = tuple(sys.argv[sys.argv.index("--skip") + 1].split(",")) if "--skip" in sys.argv else ()
    result = collect_all(skip=skip)
    skipped = result.get("skipped") or {}
    platforms = [p for p in result["platforms"] if p not in skipped]

    filename = save_snapshot(result)
    print(f"  Saved: {filename}")
    print(f"  Platforms: {', '.join(platforms)}")

    for name, why in skipped.items():            # never a 0 for a failed read: the reason is in the snapshot
        print(f"  {name}: skipped, because {why}")

    refresh_followback()

    # G-06: on Mondays, the weekly summary (plans/weekly-stats.md). A failure never breaks the sync.
    if datetime.now().weekday() == 0 or "--weekly" in sys.argv:
        try:
            from stats.weekly_summary import write as write_weekly
            print(f"  Weekly summary: {write_weekly()}")
        except Exception as e:                       # noqa: BLE001 - the sync itself must finish
            print(f"  Weekly summary failed: {e}")

    print(f"  Done.")


if __name__ == "__main__":
    main()
