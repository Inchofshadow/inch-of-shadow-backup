"""Supply-aware SC scoring + pacing warning (2026-09-24).

After the 18 -> 25 raise, a thin-supply day (10 follows because the discovery
file ran dry) scored 4/10 and two of those auto-pause SC: a pause caused by a
supply gap, not a fault. Targets are now capped at what was on offer, and a
day over SESSION_ACTION_STOP gets a pacing WARNING, never a pause.
"""
from datetime import date

import pytest

import scene_intelligence.close_loops as cl

TODAY = date.today().isoformat()
EMPTY = {"follows": []}


@pytest.fixture(autouse=True)
def _no_dated_follow_cap(monkeypatch):
    """These tests assume the standing SESSION_FOLLOWS cap. A dated cap in
    FOLLOW_CAP_DAYS (e.g. 10/day 2026-11-07..16) would make them depend on
    today's date, so pin it off (same idea as UNFOLLOW_CATCHUP_DAYS)."""
    from scene_intelligence import sc_engagement_config as cfg
    monkeypatch.setattr(cfg, "FOLLOW_CAP_DAYS", {})


def test_thin_supply_day_is_not_scored_as_a_shortfall(monkeypatch):
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 0)
    score, ded, imm = cl.score_sc_day({"sc_follow": 10, "sc_like": 10}, "done",
                                      tracker=EMPTY, day=TODAY)
    assert score == 10 and imm is None, ded
    assert any("capped at 10 by supply" in d for d in ded)


def test_lazy_session_with_supply_left_is_still_a_shortfall(monkeypatch):
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 40)
    n = cl.SC_FOLLOW_TARGET // 4          # well under half the target, supply left
    score, ded, _ = cl.score_sc_day({"sc_follow": n, "sc_like": n}, "done",
                                    tracker=EMPTY, day=TODAY)
    assert score <= 4, ded
    assert any("severe shortfall: sc_follow" in d for d in ded)


def test_unknown_supply_keeps_the_full_target(monkeypatch):
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: None)
    _, ded, _ = cl.score_sc_day({"sc_follow": 10, "sc_like": 10}, "done",
                                tracker=EMPTY, day=TODAY)
    assert any("sc_follow 10/" in d for d in ded)


def test_supply_lookup_only_for_today():
    assert cl._sc_follow_supply("2026-01-01") is None
    assert cl._sc_follow_supply("") is None


def test_full_session_with_small_pass_c_pool_scores_10(monkeypatch):
    """The phantom-target regression: 25/25 + 3 PASS C likes lost a point
    against a 37-like target built from a pool that had nothing to like."""
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 30)
    recips = {"follows": [{"user_id": str(i), "followed_back": True,
                           "last_engaged": "2026-01-01"} for i in range(20)]}
    score, ded, _ = cl.score_sc_day(
        {"sc_follow": cl.SC_FOLLOW_TARGET, "sc_like": cl.SC_PASS_A_LIKES + 3},
        "done", tracker=recips, day=TODAY)
    assert score == 10, ded


def test_over_the_action_stop_is_a_warning_not_a_pause(monkeypatch):
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 30)
    # Sweep-allowance days (UNFOLLOW_CATCHUP_DAYS) raise the stop; pin it to 0
    # so the test does not depend on today's date.
    monkeypatch.setattr(cl, "_sc_unfollow_catchup", lambda day: 0)
    f, l = cl.SC_FOLLOW_TARGET, cl.SC_PASS_A_LIKES + 5
    u = cl.SC_ACTION_STOP + 5 - f - l                     # 5 over the stop, all within caps
    counts = {"sc_follow": f, "sc_like": l, "sc_unfollow": u}
    assert u <= cl.SC_CAPS["sc_unfollow"] and l <= cl.SC_CAPS["sc_like"]
    score, ded, imm = cl.score_sc_day(counts, "done", tracker=EMPTY, day=TODAY)
    assert imm is None and score == 10, ded
    assert any(f"PACING WARNING {cl.SC_ACTION_STOP + 5} actions" in d for d in ded)


def test_like_skips_do_not_count_as_clicks(monkeypatch):
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 30)
    counts = {"sc_follow": 25, "sc_like": 25, "sc_like_skip": 20}   # 50 clicks
    _, ded, _ = cl.score_sc_day(counts, "done", tracker=EMPTY, day=TODAY)
    assert not any("PACING WARNING" in d for d in ded)
