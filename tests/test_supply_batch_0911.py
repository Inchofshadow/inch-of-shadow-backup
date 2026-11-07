"""2026-09-11 batch (Amir's yes): revive stale-only candidates via browser vets,
60-day recency, auto-record 429, gentle first audit, already_following
recognised, zero-click halt does not lock the day."""
import json
from datetime import datetime
from pathlib import Path

import pytest

import scene_intelligence.ig_engagement as eng
import scene_intelligence.ig_engagement_config as cfg
import scene_intelligence.ig_merge_session_log as m
import scene_intelligence.ig_ops_guards as guards
import scene_intelligence.ig_dispatcher as disp
import scene_intelligence.close_loops as cl

BIO = "coldwave / italo producer, berlin"


def test_recency_window_is_sixty_days():
    assert cfg.REACH["max_post_recency_days"] == 60


def _q(entries):
    return {"_meta": {}, "queue": entries}


def test_vets_take_stale_only_candidates_first_least_stale_first(monkeypatch):
    stale_ok = {"username": "s1", "status": "skipped_stale", "skipped_reason": "last_post_too_old:31d",
                "ig_followers": 900, "ig_following": 800, "ig_posts": 30, "ig_bio": BIO, "seed_count": 1}
    stale_ok2 = {"username": "s2", "status": "skipped_stale", "skipped_reason": "last_post_too_old:120d",
                 "ig_followers": 900, "ig_following": 800, "ig_posts": 30, "ig_bio": BIO, "seed_count": 5}
    stale_bad = {"username": "s3", "status": "skipped_stale", "skipped_reason": "last_post_too_old:20d",
                 "ig_followers": 9000, "ig_following": 800, "ig_posts": 30, "ig_bio": BIO}
    other = {"username": "s4", "status": "skipped_stale", "skipped_reason": "followers_too_high:5000",
             "ig_followers": 5000, "ig_bio": BIO}
    unv = type("E", (), {})(); unv.handle = "u1"; unv.raw = {"seed_count": 3}
    monkeypatch.setattr(cfg, "IN_SESSION_VET", dict(cfg.IN_SESSION_VET, enabled=True))  # paused live since 2026-09-26
    got = eng.select_vet_candidates(cfg, _q([stale_ok2, stale_ok, stale_bad, other]), [unv])
    assert [g.handle for g in got] == ["s1", "s2", "u1"]


def test_vet_pass_revives_stale_entry(tmp_path, monkeypatch):
    q = tmp_path / "q.json"
    q.write_text(json.dumps(_q([{"username": "s1", "status": "skipped_stale",
                                 "skipped_reason": "last_post_too_old:31d", "skipped_date": "2026-07-08"}])))
    monkeypatch.setattr(m, "QUEUE_FILE", q)
    c = m.update_queue_from_events([{"ts": "2026-09-12T15:00:00+02:00", "action": "ig_vet", "handle": "s1",
                                     "followers": 900, "following": 800, "posts": 30, "private": False,
                                     "last_post_days": 5, "bio": BIO}], "2026-09-12")
    e = json.loads(q.read_text())["queue"][0]
    assert c["queue_vet_revived"] == 1 and e["status"] == "pending"
    assert "skipped_reason" not in e and e["revived_at"] == "2026-09-12"


def test_vet_fail_keeps_stale_entry_stale_with_new_reason(tmp_path, monkeypatch):
    q = tmp_path / "q.json"
    q.write_text(json.dumps(_q([{"username": "s1", "status": "skipped_stale",
                                 "skipped_reason": "last_post_too_old:31d"}])))
    monkeypatch.setattr(m, "QUEUE_FILE", q)
    m.update_queue_from_events([{"ts": "2026-09-12T15:00:00+02:00", "action": "ig_vet", "handle": "s1",
                                 "followers": 900, "following": 800, "posts": 30, "private": False,
                                 "last_post_days": 90, "bio": BIO}], "2026-09-12")
    e = json.loads(q.read_text())["queue"][0]
    assert e["status"] == "skipped_stale" and e["skipped_reason"].startswith("browser_vet:last_post_too_old")


def test_already_following_skip_is_recognised(tmp_path, monkeypatch):
    q = tmp_path / "q.json"
    q.write_text(json.dumps(_q([{"username": "a1", "status": "pending"}])))
    monkeypatch.setattr(m, "QUEUE_FILE", q)
    c = m.update_queue_from_events([{"ts": "2026-09-12T15:00:00+02:00", "action": "ig_skip", "handle": "a1",
                                     "track": "reach", "reason": "already_following"}], "2026-09-12")
    e = json.loads(q.read_text())["queue"][0]
    assert e["status"] == "already_following" and c["queue_skip_unrecognized"] == 0


def test_record_detection_writes_event_and_gates(tmp_path):
    p = tmp_path / "detection_events.json"
    p.write_text(json.dumps({"events": []}))
    guards.record_detection("instagram", "rate_limited_429_profile_reads",
                            "audit hit 429 on candidate 3", path=p, today="2026-09-14")
    ev = json.loads(p.read_text())["events"]
    assert ev[-1]["type"] == "rate_limited_429_profile_reads" and ev[-1]["date"] == "2026-09-14"
    assert ev[-1]["recorded_by"] == "auto"
    hit = guards.active_detection_cooldown(datetime(2026, 9, 15, 9, 30), platform="ig", path=p)
    assert hit is not None


def test_first_audit_after_quiet_week_is_gentle(monkeypatch):
    monkeypatch.setattr(disp, "api_runs_in_last_days", lambda today, days=7: 0)
    assert disp.audit_count(datetime(2026, 9, 14).date()) == disp.GENTLE_FIRST_AUDIT
    monkeypatch.setattr(disp, "api_runs_in_last_days", lambda today, days=7: 1)
    assert disp.audit_count(datetime(2026, 9, 15).date()) == disp.AUDIT_MAX_COUNT


def test_zero_click_halt_does_not_lock_the_day():
    ev = [{"ts": "2026-09-11T15:33:00+02:00", "action": "session_halt",
           "reason": "infrastructure: browser", "sequence": 0}]
    assert cl.zero_click_halt(ev) is True
    ev2 = ev + [{"ts": "2026-09-11T15:46:00+02:00", "action": "ig_like", "handle": "x"}]
    assert cl.zero_click_halt(ev2) is False


def test_audit_recency_follows_engine_config():
    import scene_intelligence.ig_audit_queue_freshness as audit
    assert audit.REACH_MAX_POST_AGE_DAYS == cfg.REACH["max_post_recency_days"] == 60
