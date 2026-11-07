"""Write follow-back verification into the IG follow tracker from the HikerAPI
follower list (ticket M-13, Amir "y" 2026-11-04).

Why: the unfollow sweep only trusts accounts whose followback_verified_at is
recent and covers their follow-back window. Until now that date came only from
the official IG data export (~30-day cadence), so unfollows stalled between
exports. si_follow_flags.py already fetches the full follower list through
HikerAPI (Instagram is never contacted as Amir). This script reads that file
and writes the same fields the export path writes. Zero API calls here.

Trust rules (same as the export / roster rules):
  - PRESENCE in the list proves a follow-back: always written.
  - ABSENCE counts only when the list is complete and within 2% of the
    profile's follower count; otherwise positives only.
  - The list must be at most MAX_LIST_AGE_DAYS old; the verification date is
    the list's fetch date, never today.
The sweep gate in ig_engagement.py is unchanged.

  python3 scene_intelligence/ig_reciprocity_from_lists.py            # dry run
  python3 scene_intelligence/ig_reciprocity_from_lists.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SI_DIR))

TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"
TOLERANCE = 0.02
MAX_LIST_AGE_DAYS = 2


def roster_from(d: dict) -> tuple[set, bool]:
    """-> (follower handles, negatives trusted)."""
    fol = {str(u.get("username") or "").strip().lower() for u in d.get("followers") or []} - {""}
    reported = int((d.get("profile") or {}).get("follower_count") or 0)
    trusted = bool(d.get("followers_complete")) and reported > 0 \
        and abs(len(fol) - reported) / reported <= TOLERANCE
    return fol, trusted


def apply_roster(tracker: dict, roster: set, trusted: bool, vdate: str) -> dict:
    pos = neg = 0
    for e in tracker.get("active_follows", []):
        u = (e.get("username") or "").strip().lower()
        if not u:
            continue
        if u in roster:
            if not e.get("followed_back"):
                e["followed_back"] = True
                e.setdefault("followed_back_at", vdate)
                e["followback_discovered_via"] = "provider_follower_list"
                pos += 1
            e["followback_verified_at"] = vdate
            e.pop("overdue_unfollow", None)
        elif trusted:
            e["followback_verified_at"] = vdate
            neg += 1
    if trusted:
        tracker.setdefault("stats", {})["last_checked"] = vdate
    return {"new_follow_backs": pos, "verified_non_followers": neg,
            "unverified": sum(1 for e in tracker.get("active_follows", [])
                              if not e.get("followback_verified_at"))}


def main() -> int:
    ap = argparse.ArgumentParser(description="Follow-back verification from the HikerAPI follower list")
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    a = ap.parse_args()
    from si_follow_flags import newest_lists
    src = newest_lists()
    if not src:
        raise SystemExit("[RECIP] no own-lists file; run si_follow_flags.py --fetch first")
    d = json.loads(src.read_text(encoding="utf-8"))
    vdate = str(d.get("fetched") or "")[:10]
    age = (date.today() - date.fromisoformat(vdate)).days
    if age > MAX_LIST_AGE_DAYS:
        print(f"[RECIP] {src.name} is {age} days old (max {MAX_LIST_AGE_DAYS}). Nothing written.")
        return 2
    roster, trusted = roster_from(d)
    tracker = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    res = apply_roster(tracker, roster, trusted, vdate)
    print(f"[RECIP] {src.name}: {len(roster)} followers, negatives "
          f"{'TRUSTED' if trusted else 'WITHHELD (positives only)'}")
    for k, v in res.items():
        print(f"  {k:24s} {v}")
    if not a.apply:
        print("[DRY-RUN] nothing written. Add --apply to write.")
        return 0
    try:
        from ig_tracker_stats import recompute_follow_backs
        recompute_follow_backs(tracker)
    except Exception:
        pass
    backup = TRACKER_FILE.with_suffix(f".json.bak.{date.today():%Y%m%d}_pre_provider_recip")
    shutil.copy2(TRACKER_FILE, backup)
    fd, tmp = tempfile.mkstemp(dir=str(SI_DIR), prefix=".trk_tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(tracker, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, TRACKER_FILE)
    print(f"[RECIP] tracker updated (backup {backup.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
