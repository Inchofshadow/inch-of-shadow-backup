"""Move old engagement state backups to the Trash (M4, approved 2026-11-07 by Amir in the SC chat).

Rule: `scene_intelligence/*.bak.*` older than 14 days go to the macOS Trash (never rm).
`scene_intelligence/backups/` is never touched. Nothing reads these files; only
`sc_weekly_health.py` writes them.

    python3 tools/prune_bak.py            # dry run: prints and saves the list, moves nothing
    python3 tools/prune_bak.py --apply    # moves the listed files to ~/.Trash and writes an undo script

Each run writes `docs/reports/prune-bak-<date>.md` (the list) and, with --apply,
`docs/reports/prune-bak-<date>-undo.sh` (moves every file back from the Trash).
Monthly upkeep runs it on the 1st (System handover, Monthly upkeep).
"""
import argparse
import os
import shlex
import shutil
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "scene_intelligence"
TRASH = Path.home() / ".Trash"
KEEP_DAYS = 14


def candidates(now=None, folder=FOLDER, keep_days=KEEP_DAYS):
    now = now or time.time()
    out = []
    for p in sorted(folder.glob("*.bak.*")):
        if not p.is_file():
            continue
        age_days = (now - p.stat().st_mtime) / 86400
        if age_days > keep_days:
            out.append((p, age_days, p.stat().st_size))
    return out


def trash_target(p, trash=TRASH):
    target = trash / p.name
    n = 1
    while target.exists():
        target = trash / ("%s.%d" % (p.name, n))
        n += 1
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="move the files to the Trash (default: dry run)")
    args = ap.parse_args(argv)
    rows = candidates()
    today = date.today().isoformat()
    reports = ROOT / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    listing = reports / ("prune-bak-%s.md" % today)
    total = sum(s for _, _, s in rows)
    lines = ["# prune_bak %s (%s)" % (today, "applied" if args.apply else "dry run"), "",
             "Rule: scene_intelligence/*.bak.* older than %d days go to the Trash. %d file(s), %.1f MB." % (KEEP_DAYS, len(rows), total / 1e6), "",
             "| File | Age (days) | Size |", "|---|---|---|"]
    lines += ["| %s | %.0f | %.0f KB |" % (p.relative_to(ROOT), age, size / 1024) for p, age, size in rows]
    undo = []
    if args.apply:
        for p, _, _ in rows:
            target = trash_target(p)
            shutil.move(str(p), str(target))
            undo.append("mv %s %s" % (shlex.quote(str(target)), shlex.quote(str(p))))
        undo_path = reports / ("prune-bak-%s-undo.sh" % today)
        undo_path.write_text("#!/bin/sh\n# moves the pruned backups back from the Trash\n" + "\n".join(undo) + "\n", encoding="utf-8")
        os.chmod(undo_path, 0o755)
        lines += ["", "Undo: `sh %s`" % undo_path.relative_to(ROOT)]
    listing.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("%s: %d file(s), %.1f MB%s" % (listing.relative_to(ROOT), len(rows), total / 1e6, ", moved to the Trash" if args.apply else ", dry run"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
