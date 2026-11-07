"""Pre-confirm flag for the scheduled IG session (added 2026-09-17).

Why: the 15:00 scheduled routine waits for Amir's two confirms (pre-flight
and after action #1) inside ITS OWN run window. Confirms typed in the
normal chat never reach it -- on 2026-09-16 the run stalled four hours on
the action-#1 confirm and ended with one click.

How: Amir says "confirm" in chat (or runs this script) any time before the
session; that writes a small dated flag. The routine checks the flag at
both gates; a flag dated today counts as his explicit confirm for BOTH
gates, so it proceeds without waiting. No flag -> it waits as before, but
never longer than the bounded window the playbook sets. The loop-closer
deletes the flag after a successful merge, so a flag can never carry over
to another day (the date guard makes that impossible anyway).

The flag covers ONLY the two standing confirms. It does NOT cover popups,
warnings, CAPTCHAs, or any pause -- those still need Amir live.

Usage:
  python3 scene_intelligence/ig_session_confirm.py --set     # Amir's yes for today
  python3 scene_intelligence/ig_session_confirm.py --check   # routine: prints status, exit 0=confirmed 1=none
  python3 scene_intelligence/ig_session_confirm.py --clear   # remove the flag
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SI_DIR = Path(__file__).parent
FLAG_PATH = SI_DIR / "ig_session_confirm.json"
STANDING_PATH = SI_DIR / "ig_standing_confirm.json"
BERLIN = ZoneInfo("Europe/Berlin")
SCOPE = ["preflight", "action_1"]
ACTION_DAYS = {0, 2, 4, 5}  # Mon Wed Fri Sat


def _now() -> datetime:
    return datetime.now(BERLIN)


NIGHT_CUTOFF_HOUR = 22


def target_session_day(now: datetime) -> date:
    """Which session a "confirm" said at `now` is for (2026-09-22).

    Action day before 22:00 -> today. Otherwise (off day, or after the
    cutoff) -> the next action day. Amir kept confirming on the day before
    and the flag was ignored because it was dated wrong."""
    d = now.date()
    if d.weekday() in ACTION_DAYS and now.hour < NIGHT_CUTOFF_HOUR:
        return d
    d += timedelta(days=1)
    while d.weekday() not in ACTION_DAYS:
        d += timedelta(days=1)
    return d


def set_flag(path: Path = FLAG_PATH, now: datetime | None = None,
             by: str = "amir") -> dict:
    """Write the confirm flag for the session it applies to (see
    target_session_day). Covers exactly ONE session. Returns the record."""
    now = now or _now()
    rec = {
        "date": target_session_day(now).isoformat(),
        "confirmed_at": now.isoformat(timespec="seconds"),
        "scope": list(SCOPE),
        "by": by,
        "note": "counts as Amir's explicit confirm for pre-flight AND action #1 "
                "of today's IG session only; popups/warnings still need him live",
    }
    path.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def standing(path: Path = STANDING_PATH) -> dict | None:
    """The STANDING confirm (2026-10-07, Amir: "remove the confirm").

    When this file exists, every session counts as confirmed at both gates
    without a per-session word from Amir. He turns it off with
    `--standing off` (or by saying "stop"). It never covers popups,
    warnings, CAPTCHAs, pauses or a broken Chrome: those still halt."""
    if not path.exists():
        return None
    try:
        rec = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) and rec.get("on") else None


def set_standing(on: bool, path: Path = STANDING_PATH, now: datetime | None = None,
                 by: str = "amir") -> dict | None:
    now = now or _now()
    if not on:
        if path.exists():
            path.unlink()
        return None
    rec = {"on": True, "since": now.isoformat(timespec="seconds"), "by": by,
           "scope": list(SCOPE),
           "note": "standing confirm: every session is confirmed at pre-flight and "
                   "action #1 until Amir turns it off; popups/warnings/CAPTCHAs/"
                   "pauses still halt"}
    path.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def read_flag(path: Path = FLAG_PATH, now: datetime | None = None) -> dict | None:
    """Return the flag record if it exists AND is dated today (Berlin), else None.

    A flag from another day is ignored (never honoured), and reported as
    stale by --check so the routine can say so.
    """
    now = now or _now()
    if not path.exists():
        return None
    try:
        rec = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or rec.get("date") != now.date().isoformat():
        return None
    if not isinstance(rec.get("confirmed_at"), str):
        return None
    return rec


def clear_flag(path: Path = FLAG_PATH, only_date: str | None = None) -> bool:
    """Remove the flag. True if something was removed.

    `only_date`: remove only if the flag is for that day, so closing today's
    session never deletes a confirm Amir already gave for the next one."""
    if only_date is not None and path.exists():
        try:
            if json.loads(path.read_text()).get("date") != only_date:
                return False
        except (OSError, ValueError):
            pass
    if path.exists():
        path.unlink()
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--set", action="store_true", help="write today's confirm flag")
    g.add_argument("--check", action="store_true",
                   help="print status; exit 0 if confirmed for today, 1 otherwise")
    g.add_argument("--clear", action="store_true", help="remove the flag")
    g.add_argument("--standing", choices=("on", "off"),
                   help="Amir only: turn the standing confirm on/off (2026-10-07)")
    g.add_argument("--wait", type=int, metavar="SECONDS",
                   help="poll for today's flag up to SECONDS (2026-10-07); exit 0 the "
                        "moment it appears, 1 on timeout. The ONE sanctioned way for a "
                        "run to wait: an improvised shell loop is a new command string "
                        "every time and prompted for 44 min and 2h50m on 10-07.")
    args = p.parse_args(argv)

    if args.standing:
        rec = set_standing(args.standing == "on", STANDING_PATH)
        print(f"standing confirm ON since {rec['since']} -- every session runs without a "
              f"per-session confirm; say stop / --standing off to end it"
              if rec else "standing confirm OFF -- sessions need a per-session confirm again")
        return 0

    st = standing(STANDING_PATH)
    if args.wait is not None:
        import time
        deadline = time.monotonic() + max(0, args.wait)
        while True:
            now = _now()
            if st:
                print(f"confirmed (standing since {st['since'][:10]}; pre-flight + action #1)")
                return 0
            rec = read_flag(FLAG_PATH, now=now)
            if rec:
                print(f"confirmed {rec['confirmed_at']} (pre-flight + action #1)")
                return 0
            if time.monotonic() >= deadline:
                print(f"timeout after {args.wait}s: no confirm flag for today")
                return 1
            time.sleep(15)

    now = _now()
    if args.set:
        rec = set_flag(FLAG_PATH, now=now)
        day = date.fromisoformat(rec["date"])
        which = "today's" if day == now.date() else f"{day:%A} {day.isoformat()}'s"
        print(f"confirmed at {rec['confirmed_at']} -- covers pre-flight + "
              f"action #1 for {which} session")
        return 0
    if args.clear:
        print("cleared" if clear_flag(FLAG_PATH) else "no flag")
        return 0
    if st:
        print(f"confirmed (standing since {st['since'][:10]}; pre-flight + action #1)")
        return 0
    rec = read_flag(FLAG_PATH, now=now)
    if rec:
        print(f"confirmed {rec['confirmed_at']} (pre-flight + action #1)")
        return 0
    if FLAG_PATH.exists():
        try:
            fd = json.loads(FLAG_PATH.read_text()).get("date", "")
        except (OSError, ValueError):
            fd = ""
        if fd > now.date().isoformat():
            print(f"none for today (a confirm is waiting for {fd})")
        else:
            print("none (stale flag from another day, ignored)")
    else:
        print("none")
    return 1


if __name__ == "__main__":
    sys.exit(main())
