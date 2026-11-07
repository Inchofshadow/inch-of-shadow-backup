"""Spotify collector (System 68, 2026-11-05): catalogue only, no artist-profile request.

The /v1/artists/{id} call carried followers and popularity, null on every snapshot since
2026-10-01; the Monday Spotify for Artists read is the followers source. No network here.
"""
import stats.collectors as c
from stats.storage import get_growth


class R:  # minimal requests.Response stand-in
    def __init__(self, code, data):
        self.status_code, self._d = code, data

    def json(self):
        return self._d


def _fake(calls, albums_code=200):
    def get(url, headers=None, params=None, timeout=None):
        calls.append(url)
        if url.endswith("/top-tracks"):
            return R(403, {})
        if url.endswith("/albums"):
            return R(albums_code, {"items": [{
                "id": "a1", "name": "Farewell", "album_type": "single", "album_group": "single",
                "release_date": "2026-05-15", "total_tracks": 1, "available_markets": []}]})
        if url.endswith("/albums/a1/tracks"):
            return R(200, {"items": [{"track_number": 1, "name": "Farewell", "duration_ms": 322000,
                                      "id": "t1", "artists": [{"name": "Inch of Shadow"}]}]})
        raise AssertionError(f"unexpected Spotify call {url}")
    return get


def test_no_artist_profile_request_and_s4a_is_the_followers_source(monkeypatch):
    monkeypatch.setattr(c, "_spotify_token", lambda: "tok")
    calls = []
    monkeypatch.setattr(c.requests, "get", _fake(calls))
    out = c.collect_spotify()
    assert not any(u.endswith(f"/artists/{c.SPOTIFY_ARTIST_ID}") for u in calls)
    assert len(calls) == 3                                   # top tracks, albums, one album's tracks
    assert "followers" not in out and "popularity" not in out and "genres" not in out
    assert out["followers_source"] == "spotify_for_artists" and "spotify_s4a" in out["note"]
    assert out["catalog_size"] == 1 and out["albums"][0]["tracks"][0]["duration"] == "5:22"
    assert out["top_tracks"] == []


def test_catalogue_failure_is_skipped_with_the_reason(monkeypatch):
    monkeypatch.setattr(c, "_spotify_token", lambda: "tok")
    monkeypatch.setattr(c.requests, "get", _fake([], albums_code=401))
    assert c.collect_spotify() == {"skipped": "Spotify albums call answered HTTP 401"}


def test_no_token_is_skipped_with_the_reason(monkeypatch):
    monkeypatch.setattr(c, "_spotify_token", lambda: "")
    monkeypatch.setattr(c.requests, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call")))
    assert c.collect_spotify()["skipped"].startswith("no Spotify token")


def test_growth_compares_catalog_size_only():
    cur = {"platforms": {"spotify": {"catalog_size": 7, "followers_source": "spotify_for_artists"}}}
    prev = {"platforms": {"spotify": {"catalog_size": 6, "followers": None, "popularity": None}}}
    assert get_growth(cur, prev) == {"spotify": {"catalog_size": 1}}
