"""--log-action prints the running day budget and a STOP line at the cap
(2026-09-24: a session counted in its head, logged 26 follows against 25 and
the loop closer paused SC for a cap violation)."""
from datetime import date

import scene_intelligence.sc_engagement as sc


def _log(n_follow, n_like=0):
    today = date.today().isoformat()
    rows = [{"date": today, "platform": "soundcloud", "action": "sc_follow"}] * n_follow
    rows += [{"date": today, "platform": "soundcloud", "action": "sc_like"}] * n_like
    return {"log": {"x": rows}}


def test_below_cap_prints_totals_without_stop(capsys):
    from scene_intelligence import sc_engagement_config as cfg
    n = cfg.SESSION_FOLLOWS - 1
    sc.print_day_budget(_log(n, n))
    out = capsys.readouterr().out
    assert f"follows {n}/" in out and "STOP" not in out


def test_at_follow_cap_prints_stop(capsys):
    from scene_intelligence import sc_engagement_config as cfg
    sc.print_day_budget(_log(cfg.SESSION_FOLLOWS))
    out = capsys.readouterr().out
    assert "STOP: sc_follow cap reached" in out


def test_action_stop_line(capsys, monkeypatch):
    from scene_intelligence import sc_engagement_config as cfg
    monkeypatch.setattr(cfg, "UNFOLLOW_CATCHUP_DAYS", {})   # no dated allowance today
    sc.print_day_budget(_log(25, cfg.SESSION_ACTION_STOP - 25))
    assert "session action stop reached" in capsys.readouterr().out
