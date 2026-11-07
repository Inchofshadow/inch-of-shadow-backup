"""stats.follow_backs has ONE definition (audit P3-19): a snapshot count of
active_follows entries with followed_back=True, recomputed on every save.

Before 2026-07-19 the checker wrote a snapshot, the merge script incremented
a cumulative counter, and the checker's report ADDED the two — printing
roughly double the real follow-back rate.
"""
import scene_intelligence.ig_tracker_stats as ts
import scene_intelligence.ig_merge_session_log as m


def test_recompute_counts_only_reciprocators():
    tracker = {"active_follows": [
        {"username": "a", "followed_back": True},
        {"username": "b", "followed_back": False},
        {"username": "c"},
        {"username": "d", "followed_back": True},
    ], "stats": {"follow_backs": 999}}
    assert ts.recompute_follow_backs(tracker) == 2
    assert tracker["stats"]["follow_backs"] == 2


def test_recompute_handles_missing_keys():
    tracker = {}
    assert ts.recompute_follow_backs(tracker) == 0
    assert tracker["stats"]["follow_backs"] == 0


def test_merge_visual_guard_recomputes_not_increments(monkeypatch, tmp_path):
    # A drifted (inflated) stored stat must be REPLACED by the snapshot, not
    # incremented further — the old code would have made 10 into 11.
    import json
    tracker_file = tmp_path / "tracker.json"
    tracker_file.write_text(json.dumps({
        "active_follows": [
            {"username": "gallows", "followed_back": False,
             "followed_at": "2026-07-01"},
        ],
        "unfollowed_history": [],
        "stats": {"follow_backs": 10, "total_followed": 1,
                  "total_unfollowed": 0},
    }))
    monkeypatch.setattr(m, "TRACKER_FILE", tracker_file)

    events = [{"action": "ig_unfollow_aborted", "handle": "gallows",
               "ts": "2026-07-19T12:00:00"}]
    counts = m.update_tracker_from_events(events, "2026-07-19", dry_run=False)
    assert counts["reciprocators_visual_guard_caught"] == 1

    saved = json.loads(tracker_file.read_text())
    assert saved["active_follows"][0]["followed_back"] is True
    # snapshot semantics: exactly 1 reciprocator, regardless of prior drift
    assert saved["stats"]["follow_backs"] == 1
