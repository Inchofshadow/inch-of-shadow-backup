"""Freshness-audit hardening (T-003): consecutive-fail breaker, perma-error
retirement, and always-persist (the old write was gated on >=1 stale, so a
zero-stale run silently discarded every enrichment field)."""
import json

import scene_intelligence.ig_audit_queue_freshness as aud


def _setup(monkeypatch, tmp_path, entries, fetch=lambda s, h: None):
    qf = tmp_path / "queue.json"
    qf.write_text(json.dumps({"_meta": {}, "queue": entries}), encoding="utf-8")
    monkeypatch.setattr(aud, "QUEUE_FILE", qf)
    monkeypatch.setattr(aud, "_load_credentials", lambda: ("sid", "csrf"))
    monkeypatch.setattr(aud, "_build_session", lambda sid, csrf: object())
    monkeypatch.setattr(aud, "_fetch_profile", fetch)
    monkeypatch.setattr(aud, "_fetch_user_feed", lambda s, uid, count=3: None)
    monkeypatch.setattr(aud.time, "sleep", lambda *a: None)
    return qf


def _pending(n):
    return [{"username": f"acct{i}", "status": "pending"} for i in range(n)]


def test_breaker_aborts_after_five_consecutive_failures(monkeypatch, tmp_path, capsys):
    qf = _setup(monkeypatch, tmp_path, _pending(20))  # every fetch fails
    aud.audit(count=20, dry_run=False, max_age=30)
    out = capsys.readouterr().out
    assert "[BREAKER]" in out
    # exactly 5 attempts, not 20 — the 08-27 streak burned 16
    assert out.count("ERROR") == 5


def test_perma_fail_retirement_at_three_audits(monkeypatch, tmp_path):
    entries = [{"username": "deadacct", "status": "pending",
                "fetch_fail_count": 2}]
    qf = _setup(monkeypatch, tmp_path, entries)
    aud.audit(count=1, dry_run=False, max_age=30)
    saved = json.loads(qf.read_text(encoding="utf-8"))["queue"][0]
    assert saved["status"] == "retired_fetch_error"
    assert saved["fetch_fail_count"] == 3


def test_fail_count_clears_on_recovery(monkeypatch, tmp_path):
    entries = [{"username": "flaky", "status": "pending", "fetch_fail_count": 2}]
    body = {"data": {"user": {"id": "1", "edge_followed_by": {"count": 500},
                              "edge_follow": {"count": 300},
                              "edge_owner_to_timeline_media": {"count": 40},
                              "is_private": False, "is_verified": False,
                              "biography": "dark disco dj berlin"}}}
    qf = _setup(monkeypatch, tmp_path, entries, fetch=lambda s, h: body)
    aud.audit(count=1, dry_run=False, max_age=30)
    saved = json.loads(qf.read_text(encoding="utf-8"))["queue"][0]
    assert "fetch_fail_count" not in saved
    assert saved["status"] == "pending"


def test_zero_stale_run_still_persists_enrichment(monkeypatch, tmp_path):
    entries = [{"username": "goodacct", "status": "pending"}]
    body = {"data": {"user": {"id": "1", "edge_followed_by": {"count": 500},
                              "edge_follow": {"count": 300},
                              "edge_owner_to_timeline_media": {"count": 40},
                              "is_private": False, "is_verified": False,
                              "biography": "dark disco dj berlin"}}}
    qf = _setup(monkeypatch, tmp_path, entries, fetch=lambda s, h: body)
    aud.audit(count=1, dry_run=False, max_age=30)
    data = json.loads(qf.read_text(encoding="utf-8"))
    assert data["queue"][0].get("audit_date")          # enrichment kept
    assert data["_meta"].get("last_freshness_audit")   # stamped
