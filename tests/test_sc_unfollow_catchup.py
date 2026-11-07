"""UNFOLLOW_CATCHUP_DAYS (2026-09-15): a one-off, Amir-approved allowance
above the 15/day unfollow cap, honored by the planner AND the scorer, so a
planned catch-up is neither truncated nor scored as a cap violation."""
from datetime import date

import scene_intelligence.close_loops as cl
import scene_intelligence.sc_engagement as sc


def test_allowance_only_on_listed_days(monkeypatch):
    monkeypatch.setattr(sc, "UNFOLLOW_CATCHUP_DAYS", {"2026-09-16": 6})
    assert sc.unfollow_catchup_allowance(date(2026, 9, 16)) == 6
    assert sc.unfollow_catchup_allowance(date(2026, 9, 18)) == 0


def test_scorer_raises_the_cap_only_on_listed_days(monkeypatch):
    monkeypatch.setattr(cl._scc, "UNFOLLOW_CATCHUP_DAYS", {"2026-09-16": 6})
    ok, _, imm = cl.score_sc_day({"sc_unfollow": 21}, "complete", tracker={"follows": []},
                                 day="2026-09-16")
    assert imm is None
    _, ded, imm2 = cl.score_sc_day({"sc_unfollow": 21}, "complete", tracker={"follows": []},
                                   day="2026-09-18")
    assert imm2 is not None and any("cap violation" in d for d in ded)


def test_catchup_only_day_is_not_scored_for_likes_and_follows(monkeypatch):
    """09-16 regression: 21 approved unfollows scored 4/10 for 0 likes/0 follows
    and, with the supply-bound 09-15, tripped the trend pause."""
    monkeypatch.setattr(cl._scc, "UNFOLLOW_CATCHUP_DAYS", {"2026-09-16": 6})
    score, ded, imm = cl.score_sc_day({"sc_unfollow": 21}, "catch-up", tracker={"follows": []},
                                      day="2026-09-16")
    assert score == 10 and imm is None, ded
    # a normal day with only unfollows is still a shortfall
    score2, _, _ = cl.score_sc_day({"sc_unfollow": 12}, "x", tracker={"follows": []},
                                   day="2026-09-18")
    assert score2 < 10
