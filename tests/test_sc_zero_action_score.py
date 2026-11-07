"""Zero-action sessions (2026-09-11): honest score, no freeze.

The 09-11 session stopped on two dead unfollow clicks, logged nothing, and
scored 8/10 because the SESSION_INCOMPLETE marker waived the volume targets.
Now a zero-action day is capped at 3/10. It stays OUT of the two-low-scores
trend pause: a freeze without Amir's approval breaks his 2026-09-09 law.
"""
import scene_intelligence.close_loops as cl

REPORT = "SESSION_INCOMPLETE: first two unfollow clicks did not register."


def _state():
    return {"recent": [], "pauses": {"ig": None, "sc": None},
            "processed": {"ig": [], "sc": []}}


def test_zero_action_incomplete_session_is_capped():
    score, ded, imm = cl.score_sc_day({}, REPORT, tracker={"follows": []},
                                      day="2026-09-11")
    assert score <= cl.ZERO_ACTION_SCORE_CAP
    assert any("zero logged actions" in d for d in ded)
    assert imm is None


def test_incomplete_session_with_actions_is_not_capped():
    score, _, _ = cl.score_sc_day({"sc_like": 6, "sc_follow": 5}, REPORT,
                                  tracker={"follows": []}, day="2026-08-28")
    assert score == 10


def test_zero_action_scores_do_not_trigger_the_trend_pause():
    st = _state()
    for day in ("2026-09-11", "2026-09-14"):
        assert cl.record_score(st, "sc", day, 3, None,
                               counts_for_trend=False) is None
    assert st["pauses"]["sc"] is None
    assert [r["score"] for r in st["recent"]] == [3, 3]   # still recorded


def test_real_low_scores_still_trigger_the_trend_pause():
    st = _state()
    cl.record_score(st, "sc", "2026-09-11", 4, None)
    assert cl.record_score(st, "sc", "2026-09-14", 5, None) is not None


def test_close_sc_keeps_a_zero_action_incomplete_day_out_of_the_trend(
        tmp_path, monkeypatch):
    (tmp_path / "engagement_log.json").write_text('{"log": {}}')
    (tmp_path / "sc_session_report_20260911.md").write_text(REPORT)
    monkeypatch.setattr(cl, "ENG_LOG_FILE", tmp_path / "engagement_log.json")
    monkeypatch.setattr(cl, "SI_DIR", tmp_path)
    st = _state()
    st["recent"].append({"date": "2026-09-10", "platform": "sc", "score": 4})
    code, _ = cl.close_sc("2026-09-11", st)
    assert code == 0
    assert st["pauses"]["sc"] is None
    assert st["recent"][-1] == {"date": "2026-09-11", "platform": "sc",
                                "score": cl.ZERO_ACTION_SCORE_CAP,
                                "trend": False}
