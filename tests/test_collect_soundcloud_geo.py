"""SoundCloud collector: the follower-geography sample is opt-in (System 68, 2026-11-05).

It was one /me/followers read every day and nothing in the repo read follower_countries
or follower_cities. Default off = one SoundCloud read a day fewer. No network here.
"""
import stats.collectors as c


class R:  # minimal requests.Response stand-in
    def __init__(self, code, data):
        self.status_code, self._d = code, data

    def json(self):
        return self._d


def _fake(calls):
    def sc_get(url, headers, params=None):
        calls.append(url)
        if url.endswith("/me"):
            return R(200, {"followers_count": 450, "followings_count": 300,
                           "track_count": 12, "playlist_count": 1}), headers
        if url.endswith("/me/tracks"):
            return R(200, [{"title": "Farewell", "playback_count": 10, "likes_count": 2, "reposts_count": 1,
                            "comment_count": 0, "download_count": 0, "created_at": "2026-05-15T00:00:00Z",
                            "duration": 322000, "genre": "Dark Disco", "artwork_url": None}]), headers
        if url.endswith("/me/followers"):
            return R(200, {"collection": [{"country_code": "DE", "city": "Berlin"},
                                          {"country_code": "DE", "city": ""}]}), headers
        raise AssertionError(f"unexpected SoundCloud call {url}")
    return sc_get


def test_default_skips_the_follower_geography_read(monkeypatch):
    monkeypatch.setattr(c, "_sc_token", lambda: "tok")
    calls = []
    monkeypatch.setattr(c, "_sc_get", _fake(calls))
    out = c.collect_soundcloud()
    assert [u.rsplit("/", 1)[-1] for u in calls] == ["me", "tracks"]
    assert "follower_countries" not in out and "follower_cities" not in out
    assert out["followers"] == 450 and out["total_plays"] == 10 and out["tracks"][0]["title"] == "Farewell"


def test_geo_true_keeps_the_sample(monkeypatch):
    monkeypatch.setattr(c, "_sc_token", lambda: "tok")
    calls = []
    monkeypatch.setattr(c, "_sc_get", _fake(calls))
    out = c.collect_soundcloud(geo=True)
    assert calls[-1].endswith("/me/followers") and len(calls) == 3
    assert out["follower_countries"] == {"DE": 2} and out["follower_cities"] == {"Berlin": 1}


def test_collect_all_runs_soundcloud_without_geo(monkeypatch):
    monkeypatch.setattr(c, "_sc_token", lambda: "tok")
    calls = []
    monkeypatch.setattr(c, "_sc_get", _fake(calls))
    for name in ("spotify", "youtube", "instagram_daily", "hikerapi_balance"):
        monkeypatch.setattr(c, f"collect_{name}", lambda: {"ok": 1})
    out = c.collect_all()
    assert "follower_countries" not in out["platforms"]["soundcloud"] and len(calls) == 2
