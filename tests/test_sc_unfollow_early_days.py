"""UNFOLLOW_EARLY_DAYS (2026-09-26): a dated pull-forward of the 14-day window."""
from datetime import date, timedelta

import scene_intelligence.sc_engagement as sc


def _t(days_until_due):
    d = (date.today() + timedelta(days=days_until_due)).isoformat()
    return {"follows": [{"user_id": "1", "name": "x", "url": "u",
                         "followers": 1, "unfollow_after": d}]}


def test_no_pull_keeps_window(monkeypatch):
    monkeypatch.setattr(sc, "UNFOLLOW_EARLY_DAYS", {})
    plan = sc.plan_unfollow_batch(_t(2), 10)
    assert plan["batch"] == [] and plan["excluded"].get("window_open") == 1


def test_pull_today_makes_near_due_eligible(monkeypatch):
    monkeypatch.setattr(sc, "UNFOLLOW_EARLY_DAYS", {date.today().isoformat(): 4})
    assert len(sc.plan_unfollow_batch(_t(2), 10)["batch"]) == 1
    assert sc.plan_unfollow_batch(_t(5), 10)["batch"] == []   # beyond the pull
