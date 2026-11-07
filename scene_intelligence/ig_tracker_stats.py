"""One definition of the IG follow-back stat (audit P3-19).

Before 2026-07-19, `stats.follow_backs` in ig_follow_tracker.json had two
competing semantics: ig_followback_checker overwrote it with a snapshot
(count of active_follows entries with followed_back=True) while
ig_merge_session_log treated it as a cumulative counter and incremented it.
The checker's report then ADDED the two, printing roughly double the real
follow-back rate.

The definition, everywhere, is the SNAPSHOT:

    stats.follow_backs == count of active_follows entries with
                          followed_back == True

Reciprocators are permanent keeps (they are never unfollowed, SOP §4.8), so
they stay in active_follows forever and the snapshot is also the all-time
reciprocator count. Every tracker writer calls recompute_follow_backs()
before saving; nothing increments the stat by hand.
"""


def recompute_follow_backs(tracker: dict) -> int:
    """Set stats.follow_backs from active_follows; return the count."""
    stats = tracker.setdefault("stats", {})
    n = sum(1 for e in tracker.get("active_follows", [])
            if e.get("followed_back"))
    stats["follow_backs"] = n
    return n
