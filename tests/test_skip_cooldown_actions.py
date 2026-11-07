"""Skip-cooldown must recognise the action values the engine actually writes.

Regression for 2026-08-17. `recent_skip_count_for_handle` and
`last_skip_date_for_handle` matched only the legacy action value "skipped",
while the engine has written "ig_skip" since May (743 vs 40 entries in the live
log). The cooldown therefore never fired once: @dollkraut was served and skipped
as already-liked on 08-08, 08-10, 08-12, 08-14, 08-15 AND 08-17. Because the
tiny T1/T2 pools are front-loaded, those dead accounts burned the Class C
consecutive-skip breaker before the deep tier-3 pool was ever reached — the
2026-08-17 session ended after 3 scene likes.
"""
import scene_intelligence.ig_engagement as eng
from datetime import date, timedelta


def _log(handle, actions_dates):
    return {"log": {handle: [
        {"platform": "instagram", "action": a, "date": d}
        for a, d in actions_dates
    ]}}


def _recent(n_days_ago):
    return (date.today() - timedelta(days=n_days_ago)).isoformat()


def test_ig_skip_is_counted():
    log = _log("deadacct", [("ig_skip", _recent(1)), ("ig_skip", _recent(3))])
    assert eng.recent_skip_count_for_handle(log, "deadacct", 7) == 2


def test_like_skip_variants_are_counted():
    log = _log("deadacct", [
        ("ig_like_skip", _recent(1)),
        ("ig_like_skipped", _recent(2)),
        ("filter_failed_at_runtime", _recent(3)),
    ])
    assert eng.recent_skip_count_for_handle(log, "deadacct", 7) == 3


def test_legacy_skipped_value_still_counted():
    log = _log("deadacct", [("skipped", _recent(1))])
    assert eng.recent_skip_count_for_handle(log, "deadacct", 7) == 1


def test_engagement_actions_are_not_counted_as_skips():
    # Guard the fix from being too broad — real engagement must never bench.
    log = _log("goodacct", [
        ("ig_like", _recent(1)), ("ig_follow", _recent(2)),
        ("ig_unfollow", _recent(3)),
    ])
    assert eng.recent_skip_count_for_handle(log, "goodacct", 7) == 0
    assert eng.last_skip_date_for_handle(log, "goodacct") is None


def test_last_skip_date_uses_real_actions():
    log = _log("deadacct", [("ig_skip", _recent(5)), ("ig_skip", _recent(1))])
    assert eng.last_skip_date_for_handle(log, "deadacct") == date.today() - timedelta(days=1)


def test_outside_window_not_counted():
    log = _log("deadacct", [("ig_skip", _recent(30))])
    assert eng.recent_skip_count_for_handle(log, "deadacct", 7) == 0
