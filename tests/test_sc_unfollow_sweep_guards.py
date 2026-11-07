"""Tests for the unfollow-sweep guards added 2026-07-05 (audit P0).

The 2026-07-04 audit found the sweep unbounded: no session cap, no
circuit-breaker check, no delay after failed calls, and no respect for
the no_longer_engage / no_longer_following tracker flags (271 expired
candidates were queued, including released-on label mm.discos).
"""
import scene_intelligence.sc_engagement as sc


def _entry(name, **kw):
    e = {
        "user_id": kw.pop("user_id", str(abs(hash(name)) % 10**8)),
        "name": name,
        "followed_back": False,
        "unfollow_after": "2020-01-01",  # long expired
    }
    e.update(kw)
    return e


def _reasons(kept):
    return {k["name"]: k["reason"] for k in kept}


def test_flagged_entries_never_swept():
    tracker = {"follows": [
        _entry("mm.discos", no_longer_engage=True),
        _entry("drifted", no_longer_following=True),
        _entry("reciprocator", followed_back=True),
        _entry("normal-expired"),
    ]}
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=True)
    reasons = _reasons(res["kept"])
    assert reasons["mm.discos"] == "no_longer_engage"
    assert reasons["drifted"] == "no_longer_following"
    assert reasons["reciprocator"] == "followed_back"
    assert [u["name"] for u in res["unfollowed"]] == ["normal-expired"]


def test_session_cap():
    tracker = {"follows": [_entry(f"user{i}", user_id=str(i)) for i in range(40)]}
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=True)
    assert len(res["unfollowed"]) == sc.UNFOLLOWS_PER_SESSION
    capped = [k for k in res["kept"] if k["reason"] == "session_cap_reached"]
    assert len(capped) == 40 - sc.UNFOLLOWS_PER_SESSION


def test_session_halt_stops_sweep(monkeypatch):
    monkeypatch.setattr(sc, "_cb_session_halted", True)
    tracker = {"follows": [_entry("a", user_id="1"), _entry("b", user_id="2")]}
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=True)
    assert res["unfollowed"] == []
    assert all(k["reason"] == "session_halted" for k in res["kept"])


def test_consecutive_failures_halt_and_delay(monkeypatch):
    delays = []
    monkeypatch.setattr(sc, "_action_delay", lambda: delays.append(1))
    monkeypatch.setattr(sc, "sc_delete", lambda path: False)
    tracker = {"follows": [_entry(f"user{i}", user_id=str(i)) for i in range(10)]}
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=False)
    assert len(res["unfollowed"]) == sc.MAX_CONSECUTIVE_UNFOLLOW_FAILURES
    assert all(u["success"] is False for u in res["unfollowed"])
    # failures must delay too (rapid-fire failed writes were the bug)
    assert len(delays) == sc.MAX_CONSECUTIVE_UNFOLLOW_FAILURES
    # tracker is never mutated on failed unfollows
    assert len(tracker["follows"]) == 10
