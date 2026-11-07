"""FOLLOW_CAP_DAYS (2026-10-11, Amir "soften the dip"): dated days follow
fewer than SESSION_FOLLOWS; the logger stops there and the scorer neither
calls it a shortfall nor lets a session go past it."""
from datetime import date

import scene_intelligence.close_loops as cl
import scene_intelligence.sc_engagement as sc

TODAY = date.today().isoformat()
EMPTY = {"follows": []}


def _log(n_follow, n_like=0):
    rows = [{"date": TODAY, "platform": "soundcloud", "action": "sc_follow"}] * n_follow
    rows += [{"date": TODAY, "platform": "soundcloud", "action": "sc_like"}] * n_like
    return {"log": {"x": rows}}


def test_logger_stops_at_the_dated_cap(monkeypatch, capsys):
    from scene_intelligence import sc_engagement_config as cfg
    monkeypatch.setattr(cfg, "FOLLOW_CAP_DAYS", {TODAY: 15})
    sc.print_day_budget(_log(15, 15))
    out = capsys.readouterr().out
    assert "follows 15/15" in out and "warm-up target 15" in out
    assert "STOP: sc_follow cap reached (15/15)" in out


def test_scorer_full_marks_at_the_dated_cap(monkeypatch):
    monkeypatch.setattr(cl._scc, "FOLLOW_CAP_DAYS", {TODAY: 15})
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 40)
    score, ded, imm = cl.score_sc_day({"sc_follow": 15, "sc_like": 15}, "done",
                                      tracker=EMPTY, day=TODAY)
    assert score == 10 and imm is None, ded


def test_scorer_flags_going_past_the_dated_cap(monkeypatch):
    monkeypatch.setattr(cl._scc, "FOLLOW_CAP_DAYS", {TODAY: 15})
    monkeypatch.setattr(cl, "_sc_follow_supply", lambda day: 40)
    _, ded, imm = cl.score_sc_day({"sc_follow": 18, "sc_like": 15}, "done",
                                  tracker=EMPTY, day=TODAY)
    assert imm and "sc_follow 18 > 15" in imm


def test_other_days_keep_the_standing_cap(monkeypatch):
    monkeypatch.setattr(cl._scc, "FOLLOW_CAP_DAYS", {"2000-01-01": 15})
    assert cl._sc_follow_cap(TODAY) == cl.SC_FOLLOW_TARGET
