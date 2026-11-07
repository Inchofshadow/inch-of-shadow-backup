"""SoundCloud reads are capped at 100 per hour (seen 2026-10-25). The client
records the x-ratelimit headers, discovery stops cleanly near the limit
instead of firing failing calls, and same-day refresh runs merge into one
candidate file."""
import json
from pathlib import Path

import scene_intelligence.sc_engagement as sc
import scene_intelligence.sc_weekly_health as wh


class _R:
    def __init__(self, status, remaining, body=None):
        self.status_code = status
        self.headers = {"x-ratelimit-limit": "100", "x-ratelimit-remaining": str(remaining),
                        "x-ratelimit-reset": "1792927350"}
        self._body = body if body is not None else []
    def json(self):
        return self._body


def _fresh(monkeypatch):
    monkeypatch.setattr(sc, "SC_RATE", {"limit": None, "remaining": None, "reset": None})
    monkeypatch.setattr(sc, "SC_API_FAILURES", {})
    monkeypatch.setattr(sc, "_get_client_token", lambda: "tok")


def test_headers_are_recorded_and_429_means_exhausted(monkeypatch):
    _fresh(monkeypatch)
    monkeypatch.setattr(sc.requests, "get", lambda *a, **k: _R(200, 57, {"ok": 1}))
    sc.sc_client_get("/users/1")
    assert sc.SC_RATE["remaining"] == 57 and sc.SC_RATE["limit"] == 100
    assert not sc.rate_budget_exhausted()
    monkeypatch.setattr(sc.requests, "get", lambda *a, **k: _R(429, 0))
    sc.sc_client_get("/users/2")
    assert sc.rate_budget_exhausted()


def test_unknown_budget_is_not_exhausted(monkeypatch):
    _fresh(monkeypatch)
    assert not sc.rate_budget_exhausted()


def test_discovery_stops_cleanly_at_the_reserve(monkeypatch, tmp_path, capsys):
    _fresh(monkeypatch)
    monkeypatch.setattr(sc, "SEED_ROTATION_FILE", tmp_path / "rot.json")
    monkeypatch.setattr(sc, "DISCOVERY_SEEDS", [])
    monkeypatch.setattr(sc, "ENRICHED_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_load_never_engage_keys", lambda: set())
    monkeypatch.setattr(sc, "rejected_keys", lambda: (set(), set()))
    monkeypatch.setattr(sc.time, "sleep", lambda s: None)
    calls = []
    # every call answers with remaining=2 (at the reserve); one following with no id
    monkeypatch.setattr(sc.requests, "get", lambda url, **k: calls.append(url) or _R(200, 2, [{"id": ""}]))
    t = {"follows": [{"user_id": str(i), "followed_back": True, "followers": 200} for i in range(5)]}
    sc.discover_related_artists([], t, {})
    out = capsys.readouterr().out
    assert len(calls) == 1                       # second seed never requested
    assert "Rate budget reached (remaining 2 of 100" in out and "stopped cleanly" in out
    assert "(1 of 5 seeds crawled)" in out
    assert len(json.loads((tmp_path / "rot.json").read_text())["last_crawled"]) == 1


def test_same_day_runs_merge(monkeypatch, tmp_path):
    monkeypatch.setattr(wh, "BASE", tmp_path)
    (tmp_path / "scene_intelligence").mkdir()
    p1 = wh.save_candidates([{"user_id": "1", "priority": 5}, {"user_id": "2", "priority": 9}])
    d1 = json.loads(Path(p1).read_text())
    assert d1["runs"] == 1 and d1["count"] == 2
    p2 = wh.save_candidates([{"user_id": "2", "priority": 9}, {"user_id": "3", "priority": 7}])
    d2 = json.loads(Path(p2).read_text())
    assert p1 == p2 and d2["runs"] == 2
    assert [c["user_id"] for c in d2["candidates"]] == ["2", "3", "1"]
    assert d2["count"] == 3
