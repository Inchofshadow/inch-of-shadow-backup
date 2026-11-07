"""SC-05 (2026-09-01): weekly health instrumentation.

1. Reciprocator-churn alarm — a drifted entry with followed_back=true is
   surfaced by name (the la-ramazotti case sat unnamed in a 32-name drift
   list for 7 weeks).
2. By-band conversion table — the 600-1000 experiment's decision rule
   required this each health pass; no report ever computed it (audit F7).
3. Pre-mutation backup — the "_health" bak must be a restore point, not a
   copy of the run's own changes (audit F4).
"""
import json
from datetime import date, timedelta

import scene_intelligence.sc_weekly_health as h


def _user(uid, permalink="x"):
    return {"id": int(uid), "permalink": permalink}


def test_reciprocator_churn_is_named(tmp_path, monkeypatch):
    monkeypatch.setattr(h, "TRACKER_FILE", tmp_path / "t.json")
    tracker = {"follows": [
        {"user_id": "1", "name": "still-followed", "followed_back": True},
        {"user_id": "2", "name": "churned-reciprocator", "followed_back": True},
        {"user_id": "3", "name": "normal-drift", "followed_back": False},
    ]}
    # live followings contain only user 1; followers irrelevant here
    summary = h.update_tracker(tracker, [_user(1)], [], dry_run=True)
    assert summary["reciprocator_churn"] == ["churned-reciprocator"]
    assert set(summary["drift_detected"]) == {"churned-reciprocator", "normal-drift"}


def test_band_conversion_lines_compute_both_views():
    today = date.today()
    old = (today - timedelta(days=30)).isoformat()   # in cohort, mature
    fresh = (today - timedelta(days=2)).isoformat()  # too young for cohort
    follows = [
        {"followers": 150, "followed_back": True,  "followed_at": old},
        {"followers": 200, "followed_back": False, "followed_at": old},
        {"followers": "700", "followed_back": True, "followed_at": old},  # str coerced
        {"followers": 800, "followed_back": False, "followed_at": fresh},
        {"followers": 50,  "followed_back": False, "followed_at": "2026-05-01"},  # pre-cohort
    ]
    lines = "\n".join(h.band_conversion_lines(follows))
    assert "all time" in lines
    assert "100-300: 1/2 (50%)" in lines
    assert "600-1000: 1/2 (50%)" in lines          # all-time view includes fresh
    # cohort view: fresh + pre-cohort excluded -> 600-1000 is 1/1
    assert "600-1000: 1/1 (100%)" in lines


def test_health_backup_is_pre_mutation(tmp_path, monkeypatch):
    monkeypatch.setattr(h, "TRACKER_FILE", tmp_path / "sc_follow_tracker.json")
    tracker = {"follows": [
        {"user_id": "9", "name": "will-drift", "followed_back": False},
    ]}
    h.update_tracker(tracker, [], [{"id": 9}], dry_run=False)
    # mutation happened in memory...
    assert tracker["follows"][0]["followed_back"] is True
    # ...but the bak holds the PRE-run state
    baks = list(tmp_path.glob("sc_follow_tracker.bak.*_health.json"))
    assert len(baks) == 1
    saved = json.loads(baks[0].read_text())
    assert saved["follows"][0].get("followed_back") is False
