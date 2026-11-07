"""sc_client_get used to swallow every failure (2026-10-25: discovery crawled
3-4 of 55 seeds and nothing said why). Failures are now counted by status
and printed once per kind, and discovery prints the tally."""
import scene_intelligence.sc_engagement as sc


class _R:
    def __init__(self, status):
        self.status_code = status
        self.headers = {}
    def json(self):
        return {"ok": True}


def test_non_200_is_counted_and_reported_once(monkeypatch, capsys):
    monkeypatch.setattr(sc, "SC_API_FAILURES", {})
    monkeypatch.setattr(sc, "_get_client_token", lambda: "tok")
    monkeypatch.setattr(sc.requests, "get", lambda *a, **k: _R(429))
    for _ in range(5):
        assert sc.sc_client_get("/users/1/followings") is None
    assert sc.SC_API_FAILURES == {"HTTP 429": 5}
    assert capsys.readouterr().err.count("SC API HTTP 429") == 3


def test_200_leaves_the_tally_alone(monkeypatch):
    monkeypatch.setattr(sc, "SC_API_FAILURES", {})
    monkeypatch.setattr(sc, "_get_client_token", lambda: "tok")
    monkeypatch.setattr(sc.requests, "get", lambda *a, **k: _R(200))
    assert sc.sc_client_get("/users/1") == {"ok": True}
    assert sc.SC_API_FAILURES == {}


def test_discovery_prints_seed_count_and_tally(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sc, "SC_API_FAILURES", {})
    monkeypatch.setattr(sc, "SEED_ROTATION_FILE", tmp_path / "rot.json")
    monkeypatch.setattr(sc, "DISCOVERY_SEEDS", [])
    monkeypatch.setattr(sc, "ENRICHED_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_load_never_engage_keys", lambda: set())
    monkeypatch.setattr(sc, "rejected_keys", lambda: (set(), set()))
    monkeypatch.setattr(sc.time, "sleep", lambda s: None)
    monkeypatch.setattr(sc, "_get_client_token", lambda: "tok")
    monkeypatch.setattr(sc.requests, "get", lambda *a, **k: _R(429))
    t = {"follows": [{"user_id": str(i), "followed_back": True, "followers": 200} for i in range(3)]}
    sc.discover_related_artists([], t, {})
    out = capsys.readouterr().out
    assert "Discovered 0 related artists (0 of 3 seeds crawled)" in out
    # the first 429 marks the budget as spent, so the crawl stops instead of
    # firing two more failing calls
    assert "API failures this run: HTTP 429 x1" in out
    assert "Rate budget reached" in out
