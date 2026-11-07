"""Tests for the stale-skip prefix matching added 2026-07-05 (audit P3-14).

The old exact-match tuple caught 0 of 64 reach skips in the 2026-07-01
session; dead accounts stayed pending and were re-served every session.
"""
import scene_intelligence.ig_merge_session_log as m


def test_real_session_vocabulary_matches():
    # every variant observed in archived sessions that exact-match missed
    for reason in (
        "page_unavailable_deleted",
        "account_not_found",
        "account_dead",
        "filter_failed_private_account",
        "filter_failed_at_runtime_0posts_49followers",
        "filter_failed_followers_too_high_6028",
        "posts_older_than_90_days",
        "all_posts_over_90_days",
        "private_account",
        "stale_last_post",
    ):
        assert m._is_stale_skip_reason(reason), reason


def test_old_exact_vocabulary_still_matches():
    for reason in (
        "filter_failed_at_runtime",
        "posts_older_than_window",
        "ig_handle_dead",
        "account_unavailable",
        "in_blocked_list",
        "in_personal_network",
    ):
        assert m._is_stale_skip_reason(reason), reason


def test_non_stale_reasons_do_not_match():
    for reason in ("user_veto", "session_cap_reached", "", None,
                   "already_following"):
        assert not m._is_stale_skip_reason(reason), reason


def test_pool_depth_runs_on_real_data():
    # Read-only on the live queue/tracker/lists; must return an int >= 0
    depth = m.report_vetted_pool_depth()
    assert isinstance(depth, int)
    assert depth >= 0
