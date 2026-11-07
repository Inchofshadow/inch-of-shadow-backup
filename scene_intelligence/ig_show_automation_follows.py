"""
ig_show_automation_follows.py
------------------------------
Print all IG automation follows from ig_follow_tracker.json in a clean,
scannable format. Read-only, no API calls.

Use this when you want to check "is this handle in my IG following list
because of automation, or did I follow them manually?" Anything NOT in
this output = a manual follow you did yourself (or pre-dates the
automation program).

Usage:
  python3 scene_intelligence/ig_show_automation_follows.py
  python3 scene_intelligence/ig_show_automation_follows.py --search someuser
  python3 scene_intelligence/ig_show_automation_follows.py --overdue-only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TRACKER = BASE_DIR / "scene_intelligence" / "ig_follow_tracker.json"


def parse_date(s):
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def categorize(entries):
    """Bucket active follows into reciprocators, pending in-window, overdue, keep-following."""
    today = date.today()
    reciprocators = []
    keep_following = []
    pending_in_window = []
    pending_overdue = []
    for e in entries:
        if e.get("followed_back"):
            reciprocators.append(e)
        elif e.get("keep_following"):
            keep_following.append(e)
        else:
            d = parse_date(e.get("unfollow_after", ""))
            if d and d <= today:
                pending_overdue.append(e)
            else:
                pending_in_window.append(e)
    return reciprocators, keep_following, pending_in_window, pending_overdue


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--search", help="Filter to handles containing this substring")
    p.add_argument("--overdue-only", action="store_true",
                   help="Only show overdue (next-to-unfollow) entries")
    args = p.parse_args()

    if not TRACKER.exists():
        print(f"Tracker not found: {TRACKER}", file=sys.stderr)
        return 1

    tr = json.loads(TRACKER.read_text(encoding="utf-8"))
    af = tr.get("active_follows", [])
    uh = tr.get("unfollowed_history", [])

    if args.search:
        q = args.search.lower().lstrip("@")
        af = [e for e in af if q in (e.get("username") or "").lower()]
        uh_filtered = [u for u in uh if isinstance(u, dict) and q in (u.get("username") or "").lower()]
    else:
        uh_filtered = uh

    rec, keep, pending_in, pending_over = categorize(af)

    print(f"=== IG Automation Follows Tracker ({date.today()}) ===")
    print(f"Total active follows: {len(af)}")
    if args.search:
        print(f"Filtered by handle containing: '{args.search}'")
    print(f"Total unfollowed (history): {len(uh)}")
    print()

    if not args.overdue_only:
        print(f"FOLLOWED BACK ({len(rec)}) -- permanent keep:")
        for e in sorted(rec, key=lambda x: x.get("followed_back_at") or x.get("followed_at", "")):
            print(f"  @{e['username']:<40s} fb: {e.get('followed_back_at','?')}")
        print()

        if keep:
            print(f"KEEP-FOLLOWING (flagged manual keep) ({len(keep)}):")
            for e in keep:
                print(f"  @{e['username']}")
            print()

        print(f"PENDING IN-WINDOW ({len(pending_in)}) -- haven't expired their 7-day window yet:")
        for e in sorted(pending_in, key=lambda x: x.get("followed_at", "")):
            print(f"  @{e['username']:<40s} followed: {e.get('followed_at','?')}  window-ends: {e.get('unfollow_after','?')}")
        print()

    print(f"OVERDUE -- next-to-unfollow ({len(pending_over)}):")
    for e in sorted(pending_over, key=lambda x: x.get("followed_at", "")):
        ua = parse_date(e.get("unfollow_after", ""))
        overdue_days = (date.today() - ua).days if ua else "?"
        print(f"  @{e['username']:<40s} followed: {e.get('followed_at','?')}  overdue: {overdue_days}d")
    print()

    if uh_filtered and not args.overdue_only:
        print(f"PREVIOUSLY UNFOLLOWED ({len(uh_filtered)}):")
        for u in uh_filtered[-20:]:
            if isinstance(u, dict):
                print(f"  @{u.get('username','?'):<40s} unfollowed: {u.get('unfollowed_at') or u.get('date','?')}")
            else:
                print(f"  @{u}")
        if len(uh_filtered) > 20:
            print(f"  ... and {len(uh_filtered) - 20} more (showing latest 20)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
