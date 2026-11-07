"""Tests for derived tracker stats (added 2026-07-10).

CC's 2026-07-10 session report published "Net active follows 367" and
"Follow-back rate ~13.6%", computed as 422 - 55 and 50/367.

That subtraction is invalid. The tracker has TWO unfollow representations:

  * remove_follow_record() DELETES the entry from `follows` and increments
    stats.total_unfollowed. Those 55 accounts are already absent from the list.
  * the unfollow sweep SOFT-FLAGS no_longer_following=true and KEEPS the entry.
    There are 298 of those.

So `total_followed - total_unfollowed` subtracts hard-deleted accounts from a
list that never contained them. The number anyone actually wants, active follows,
was not exposed by stats at all. recompute_tracker_stats() now derives it.

stats.total_unfollowed is left alone: it is a legitimate cumulative counter of
hard deletes, not a stale field.
"""
import scene_intelligence.sc_engagement as sc


def _tracker(follows, **stats):
    base = {"total_followed": 0, "total_unfollowed": 0, "follow_backs": 0}
    base.update(stats)
    return {"follows": follows, "stats": base}


def test_derives_active_follows_excluding_soft_flagged():
    t = _tracker([
        {"user_id": "1", "followed_back": True},
        {"user_id": "2", "followed_back": False},
        {"user_id": "3", "followed_back": True, "no_longer_following": True},
        {"user_id": "4", "followed_back": False, "no_longer_following": True},
    ])
    sc.recompute_tracker_stats(t)
    s = t["stats"]
    assert s["total_followed"] == 4
    assert s["no_longer_following"] == 2
    assert s["active_follows"] == 2


def test_derives_follow_backs_from_entries():
    t = _tracker([
        {"user_id": "1", "followed_back": True},
        {"user_id": "2", "followed_back": True},
        {"user_id": "3", "followed_back": False},
    ], follow_backs=99)
    sc.recompute_tracker_stats(t)
    assert t["stats"]["follow_backs"] == 2


def test_does_not_touch_total_unfollowed_hard_delete_counter():
    t = _tracker([{"user_id": "1", "followed_back": False}], total_unfollowed=55)
    sc.recompute_tracker_stats(t)
    assert t["stats"]["total_unfollowed"] == 55


def test_active_follows_never_computed_as_total_minus_unfollowed():
    """The exact 2026-07-10 miscalculation must not be reproducible."""
    follows = [{"user_id": str(i), "followed_back": False} for i in range(422)]
    for e in follows[:298]:
        e["no_longer_following"] = True
    t = _tracker(follows, total_unfollowed=55)
    sc.recompute_tracker_stats(t)
    s = t["stats"]
    assert s["active_follows"] == 124
    assert s["active_follows"] != s["total_followed"] - s["total_unfollowed"]  # != 367


def test_empty_tracker_is_all_zeroes():
    t = _tracker([])
    sc.recompute_tracker_stats(t)
    s = t["stats"]
    assert s["total_followed"] == 0
    assert s["active_follows"] == 0
    assert s["no_longer_following"] == 0
    assert s["follow_backs"] == 0


def test_missing_stats_block_is_created():
    t = {"follows": [{"user_id": "1", "followed_back": True}]}
    sc.recompute_tracker_stats(t)
    assert t["stats"]["active_follows"] == 1


def test_save_follow_tracker_recomputes_before_writing(tmp_path, monkeypatch):
    import json
    target = tmp_path / "tracker.json"
    monkeypatch.setattr(sc, "FOLLOW_TRACKER", target)
    t = _tracker([
        {"user_id": "1", "followed_back": True},
        {"user_id": "2", "followed_back": False, "no_longer_following": True},
    ], follow_backs=0)
    sc._save_follow_tracker(t)
    written = json.loads(target.read_text())
    assert written["stats"]["active_follows"] == 1
    assert written["stats"]["follow_backs"] == 1
