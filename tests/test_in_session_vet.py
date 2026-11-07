"""In-session vetting (2026-09-06, T-021): the browser session vets unvetted
queue candidates; the merge recomputes the verdict from logged numbers and
writes the API audit's fields. Zero API."""
import json
from pathlib import Path

import pytest

import scene_intelligence.ig_merge_session_log as m
import scene_intelligence.ig_engagement as eng
import scene_intelligence.ig_engagement_config as cfg


# --- merge: verdict from numbers ------------------------------------------

def test_pass_from_numbers():
    v, why = m.vet_verdict({"followers": 900, "posts": 40, "private": False,
                            "last_post_days": 3, "bio": "dark disco producer, berlin"})
    assert v == "pass" and why == "ok"


def test_pass_recency_unknown_is_still_pass():
    v, why = m.vet_verdict({"followers": "1.2k", "posts": "12", "private": False,
                            "bio": "dark disco producer, berlin"})
    assert v == "pass" and why == "ok_recency_unknown"


@pytest.mark.parametrize("ev,reason", [
    ({"followers": 900, "posts": 40, "private": True, "bio": "dark disco producer, berlin"}, "private"),
    ({"followers": 50, "posts": 40, "private": False, "bio": "dark disco producer, berlin"}, "followers_too_low:50"),
    ({"followers": 9000, "posts": 40, "private": False, "bio": "dark disco producer, berlin"}, "followers_too_high:9000"),
    ({"followers": 900, "posts": 0, "private": False, "bio": "dark disco producer, berlin"}, "no_posts"),
    ({"followers": 900, "posts": 40, "private": False, "last_post_days": 90, "bio": "dark disco producer, berlin"},
     "last_post_too_old:90d"),
])
def test_fail_reasons(ev, reason):
    v, why = m.vet_verdict(ev)
    assert v == "fail" and why == reason


def test_operator_verdict_is_ignored_without_numbers():
    v, why = m.vet_verdict({"verdict": "pass", "private": False})
    assert v is None


def _queue(tmp_path, monkeypatch, entries):
    q = tmp_path / "ig_target_list.json"
    q.write_text(json.dumps({"_meta": {}, "queue": entries}))
    monkeypatch.setattr(m, "QUEUE_FILE", q)
    return q


def test_merge_writes_audit_fields_on_pass(tmp_path, monkeypatch):
    q = _queue(tmp_path, monkeypatch, [{"username": "vetme", "status": "pending"}])
    counts = m.update_queue_from_events(
        [{"ts": "2026-09-07T15:10:00+02:00", "action": "ig_vet", "handle": "@vetme",
          "followers": 700, "posts": 21, "private": False, "last_post_days": 4,
          "bio": "dark disco producer, berlin"}],
        "2026-09-07")
    e = json.loads(q.read_text())["queue"][0]
    assert counts["queue_vet_pass"] == 1
    assert e["status"] == "pending"
    assert e["audit_date"] == "2026-09-07" and e["audit_source"] == "browser"
    assert e["ig_followers"] == 700 and e["ig_last_post_age_days"] == 4


def test_merge_marks_fail_skipped_stale(tmp_path, monkeypatch):
    q = _queue(tmp_path, monkeypatch, [{"username": "dead", "status": "pending"}])
    counts = m.update_queue_from_events(
        [{"ts": "2026-09-07T15:10:00+02:00", "action": "ig_vet", "handle": "dead",
          "followers": 700, "posts": 21, "private": False, "last_post_days": 90,
          "bio": "dark disco producer, berlin"}],
        "2026-09-07")
    e = json.loads(q.read_text())["queue"][0]
    assert counts["queue_vet_fail"] == 1
    assert e["status"] == "skipped_stale"
    assert e["skipped_reason"] == "browser_vet:last_post_too_old:90d"
    assert e["audit_source"] == "browser"


def test_merge_ignores_vet_without_numbers(tmp_path, monkeypatch):
    q = _queue(tmp_path, monkeypatch, [{"username": "x", "status": "pending"}])
    counts = m.update_queue_from_events(
        [{"ts": "2026-09-07T15:10:00+02:00", "action": "ig_vet", "handle": "x",
          "verdict": "pass"}], "2026-09-07")
    e = json.loads(q.read_text())["queue"][0]
    assert counts["queue_vet_unusable"] == 1
    assert "audit_date" not in e


def test_vet_alias_normalised():
    ev = m._normalize_event({"action": "vet", "handle": "a"})
    assert ev["action"] == "ig_vet"


# --- engine: vet slice ------------------------------------------------------

class _E:
    def __init__(self, handle, seeds):
        self.handle = handle
        self.raw = {"seed_count": seeds}


def test_select_vets_only_when_pool_low(monkeypatch):
    pool = [_E("a", 4), _E("b", 3), _E("c", 3), _E("d", 2), _E("e", 2),
            _E("f", 1), _E("g", 1)]
    low = {"queue": [{"status": "pending", "audit_date": "2026-09-01"}] * 10}
    full = {"queue": [{"status": "pending", "audit_date": "2026-09-01"}] * 40}
    monkeypatch.setattr(cfg, "IN_SESSION_VET", dict(cfg.IN_SESSION_VET, enabled=True, per_session=6))  # pin 6: live value is a temporary 15 (M-10)
    got = eng.select_vet_candidates(cfg, low, pool)
    assert [e.handle for e in got] == ["a", "b", "c", "d", "e", "f"]
    assert eng.select_vet_candidates(cfg, full, pool) == []


def test_vet_checklist_mirrors_reach():
    ck = eng.vet_checklist(cfg)
    assert ck["min_followers"] == cfg.REACH["min_followers"]
    assert ck["max_followers"] == cfg.REACH["max_followers"]
    assert ck["max_post_age_days"] == cfg.REACH["max_post_recency_days"]


# --- 2026-09-08: a browser vet must apply the SAME filters the engine will ---
# Defect found the day after shipping: the vet recorded followers/posts only, so
# every passed candidate was later rejected by the engine's bio check
# (has_ig_data -> require_bio_text). A vet now captures bio and following too.

def test_vet_without_bio_is_unusable():
    v, why = m.vet_verdict({"followers": 900, "posts": 40, "private": False,
                            "last_post_days": 3})
    assert v is None and "bio" in why


def test_empty_bio_fails_like_the_engine_would():
    v, why = m.vet_verdict({"followers": 900, "posts": 40, "private": False,
                            "last_post_days": 3, "bio": "   "})
    assert (v, why) == ("fail", "bio_too_short")


def test_pass_requires_bio_text():
    v, why = m.vet_verdict({"followers": 900, "posts": 40, "private": False,
                            "last_post_days": 3, "bio": "dark disco / ebm, berlin"})
    assert v == "pass"


def test_following_ratio_checked_when_given():
    base = {"followers": 300, "posts": 40, "private": False, "bio": "techno dj",
            "last_post_days": 2}
    assert m.vet_verdict({**base, "following": 600})[0] == "pass"
    v, why = m.vet_verdict({**base, "following": 5000})
    assert v == "fail" and why.startswith("following_")


def test_merge_stores_bio_and_following(tmp_path, monkeypatch):
    q = _queue(tmp_path, monkeypatch, [{"username": "good", "status": "pending"}])
    m.update_queue_from_events(
        [{"ts": "2026-09-09T15:10:00+02:00", "action": "ig_vet", "handle": "good",
          "followers": 700, "following": 800, "posts": 21, "private": False,
          "last_post_days": 4, "bio": "italo / coldwave producer"}],
        "2026-09-09")
    e = json.loads(q.read_text())["queue"][0]
    assert e["ig_bio"] == "italo / coldwave producer"
    assert e["ig_following"] == 800
    assert e["audit_source"] == "browser" and e["status"] == "pending"


def test_plan_file_carries_follow_ceiling(tmp_path, monkeypatch):
    """2026-09-08: with a dry queue the plan's reach_follows is empty; the
    session's follow ceiling must still be the phase target."""
    from datetime import datetime
    monkeypatch.setattr(eng, "SI_DIR", tmp_path)
    plan = eng.SessionPlan(phase_label="p", phase_limits={"follows_per_session": 12,
                           "likes_per_session": 6, "unfollows_per_session": 8},
                           unfollows=[], likes=[], follows=[], scene_rejects={},
                           reach_rejects={}, unfollow_rejects={}, tier_budgets=[])
    path = eng.write_session_plan_file(cfg, plan, datetime(2026, 9, 9, 15, 0))
    meta = json.loads(Path(path).read_text())["_meta"]
    assert meta["follows_target"] == 12
