#!/usr/bin/env python3
"""Write the daily brief and the Socials digest without a model (System 104, 2026-11-15).

Why: on Sat 2026-11-14 both 20:00 chat tasks failed with "weekly limit reached", so no brief
and no digest existed for that day. This runs from launchd (com.inchofshadow.evening-reports,
19:55) and needs no model: it calls the two report scripts and saves their files.
The 20:00 chat tasks then only post the saved file.

  .venv/bin/python stats/evening_reports.py                # today
  .venv/bin/python stats/evening_reports.py 2026-11-14     # another day
  .venv/bin/python stats/evening_reports.py --dry-run      # say what it would write, write nothing

A report whose file already exists is left alone (the brief's --write also saves state and
handover proposals, so it must run once per day). One failing report never stops the other.
Exit 0 when both files exist at the end, else 1.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORTS = ROOT / "docs" / "reports"


def brief_path(d: date, reports: Path = REPORTS) -> Path:
    return reports / f"daily-brief-{d.isoformat()}.md"


def digest_path(d: date, reports: Path = REPORTS) -> Path:
    return reports / f"socials-digest-{d.isoformat()}.md"


def _write_brief(d: date) -> None:
    from stats import daily_brief
    daily_brief.build(d, write=True)


def _write_digest(d: date) -> None:
    from stats import socials_digest
    text = socials_digest.build(d)
    REPORTS.mkdir(parents=True, exist_ok=True)
    digest_path(d).write_text(text + "\n", encoding="utf-8")


def run(d: date, *, dry_run: bool = False, jobs=None, reports: Path = REPORTS) -> int:
    jobs = jobs or (("daily brief", brief_path, _write_brief), ("Socials digest", digest_path, _write_digest))
    failed = 0
    for name, path_of, write in jobs:
        path = path_of(d, reports)
        if path.exists():
            print(f"{name}: already written ({path.name})")
            continue
        if dry_run:
            print(f"{name}: would write {path.name}")
            continue
        try:
            write(d)
        except BaseException as exc:  # noqa: BLE001  (a SystemExit in one report must not stop the other)
            print(f"{name}: FAILED {type(exc).__name__}: {str(exc)[:200]}")
        if path.exists():
            print(f"{name}: written ({path.name})")
        else:
            failed += 1
            print(f"{name}: no file")
    return 1 if failed else 0


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    d = date.fromisoformat(args[0]) if args else date.today()
    return run(d, dry_run="--dry-run" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
