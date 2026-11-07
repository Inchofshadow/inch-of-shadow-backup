"""G-03 (2026-10-21): the health check notices a reciprocator who no longer
follows us back. History is kept (followed_back stays True), the entry gets
followback_lost_at, seeds skip it, and the U2 planner keeps protecting it
unless FOLLOWBACK_LOST_UNFOLLOW is on."""
import sys
from datetime import date

import scene_intelligence.sc_engagement as sc
import scene_intelligence.sc_weekly_health as wh

TODAY = date.today().isoformat()


def _e(uid, fb=True, **kw):
    d = {"user_id": uid, "name": f"n{uid}", "followed_back": fb, "followers": 200,
         "followed_at": "2026-09-01"}
    d.update(kw)
    return d


def _users(*ids):
    return [{"id": int(i), "permalink": f"p{i}"} for i in ids]


def test_lost_reciprocator_is_stamped_and_kept():
    t = {"follows": [_e(str(i)) for i in range(1, 11)]}
    s = wh.update_tracker(t, _users(*range(1, 11)), _users(*range(2, 11)), dry_run=True)
    e1 = t["follows"][0]
    assert e1["followback_lost_at"] == TODAY and e1["followed_back"] is True
    assert s["followback_lost"] == ["n1"] and not s["followback_lost_suspect"]


def test_mass_loss_is_treated_as_partial_fetch():
    t = {"follows": [_e(str(i)) for i in range(1, 41)]}
    s = wh.update_tracker(t, _users(*range(1, 41)), _users(*range(1, 11)), dry_run=True)
    assert s["followback_lost_suspect"] == 30 and s["followback_lost"] == []
    assert not any(e.get("followback_lost_at") for e in t["follows"])


def test_empty_follower_list_stamps_nothing():
    t = {"follows": [_e("1")]}
    wh.update_tracker(t, _users(1), [], dry_run=True)
    assert "followback_lost_at" not in t["follows"][0]


def test_regained_follower_is_cleared():
    t = {"follows": [_e("1", followback_lost_at="2026-10-01")]}
    s = wh.update_tracker(t, _users(1), _users(1), dry_run=True)
    assert "followback_lost_at" not in t["follows"][0]
    assert t["follows"][0]["followback_regained_at"] == TODAY
    assert s["followback_regained"] == ["n1"]


def test_seeds_skip_lost_reciprocators():
    t = {"follows": [_e("1"), _e("2", followback_lost_at="2026-10-01")]}
    assert {s["user_id"] for s in sc._reciprocator_seeds(t, 10)} == {"1"}


def test_planner_protects_lost_by_default_and_unfollows_when_switched_on(monkeypatch, capsys):
    from scene_intelligence import sc_engagement_config as cfg
    entry = _e("77", followback_lost_at="2026-10-01", followed_at="2026-09-01",
               unfollow_after="2026-09-11")
    t = {"follows": [entry]}
    monkeypatch.setattr(cfg, "FOLLOWBACK_LOST_UNFOLLOW", False)
    assert [e["user_id"] for e in sc.plan_unfollow_batch(t, 20)["batch"]] == []
    monkeypatch.setattr(cfg, "FOLLOWBACK_LOST_UNFOLLOW", True)
    assert [e["user_id"] for e in sc.plan_unfollow_batch(t, 20)["batch"]] == ["77"]


def test_keep_following_always_protects(monkeypatch):
    from scene_intelligence import sc_engagement_config as cfg
    monkeypatch.setattr(cfg, "FOLLOWBACK_LOST_UNFOLLOW", True)
    t = {"follows": [_e("78", followback_lost_at="2026-10-01", keep_following="Amir")]}
    assert sc.plan_unfollow_batch(t, 20)["batch"] == []


# ---- 2026-10-25: the first option-A session stopped its U2 lane after one
# click because the logger still called a lost reciprocator "churn", and the
# PASS C list still offered them a maintenance like.

def test_pass_c_skips_lost_reciprocators():
    t = {"follows": [_e("1", last_engaged="2026-01-01"),
                     _e("2", last_engaged="2026-01-01", followback_lost_at="2026-10-23")]}
    assert [e["user_id"] for e in sc.pass_c_targets(t, date(2026, 10, 25))] == ["1"]


def test_scorer_pass_c_pool_skips_lost_reciprocators():
    import scene_intelligence.close_loops as cl
    t = {"follows": [_e("1", last_engaged="2026-01-01"),
                     _e("2", last_engaged="2026-01-01", followback_lost_at="2026-10-23")]}
    assert cl._sc_pass_c_available(t, "2026-10-25") == 1


def test_unfollowing_a_lost_reciprocator_is_not_churn(monkeypatch, capsys):
    saved = {}
    t = {"follows": [_e("33925", followback_lost_at="2026-10-23")],
         "permanently_unfollowed": [], "stats": {"total_unfollowed": 0}}
    eng = {"log": {}}
    monkeypatch.setattr(sc, "load_follow_tracker", lambda: t)
    monkeypatch.setattr(sc, "_save_follow_tracker", lambda tr: saved.setdefault("t", tr))
    monkeypatch.setattr(sc, "load_eng_log", lambda: eng)
    monkeypatch.setattr(sc, "save_eng_log", lambda e: saved.setdefault("e", e))
    monkeypatch.setattr(sc, "_sc_standard_gates", lambda platform="sc": None)
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--log-action", "--action-type",
                                      "sc_unfollow", "--user-id", "33925", "--name", "n33925"])
    sc.main()
    out = capsys.readouterr().out
    assert "CHURN ALERT" not in out and "Logged sc_unfollow" in out
    logged = [a for rows in eng["log"].values() for a in rows if a.get("action") == "sc_unfollow"]
    assert logged and not logged[0].get("churn_alert")


def test_unfollowing_a_real_reciprocator_still_alerts(monkeypatch, capsys):
    t = {"follows": [_e("44")], "permanently_unfollowed": [], "stats": {"total_unfollowed": 0}}
    monkeypatch.setattr(sc, "load_follow_tracker", lambda: t)
    monkeypatch.setattr(sc, "_save_follow_tracker", lambda tr: None)
    monkeypatch.setattr(sc, "load_eng_log", lambda: {"log": {}})
    monkeypatch.setattr(sc, "save_eng_log", lambda e: None)
    monkeypatch.setattr(sc, "_sc_standard_gates", lambda platform="sc": None)
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--log-action", "--action-type",
                                      "sc_unfollow", "--user-id", "44", "--name", "n44"])
    sc.main()
    assert "CHURN ALERT" in capsys.readouterr().out


def test_health_churn_alarm_ignores_lost_reciprocators():
    t = {"follows": [_e("1", followback_lost_at="2026-10-23"), _e("2")]}
    s = wh.update_tracker(t, _users(), _users(), dry_run=True)   # both left our followings
    assert s["reciprocator_churn"] == ["n2"]
