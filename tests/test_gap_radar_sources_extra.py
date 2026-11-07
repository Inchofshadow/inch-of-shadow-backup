"""GR-04: extra Gap Radar sources, all HTTP mocked."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gap_radar"))
import sources_extra as sx  # noqa: E402


class FakeResp:
    def __init__(self, data, status=200):
        self._data, self.status_code = data, status

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code} for url https://x/?key=SECRET")


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(sx.time, "sleep", lambda s: None)


def route(monkeypatch, handler):
    calls = []

    def fake_get(url, headers=None, timeout=None, params=None):
        calls.append((url, params or {}))
        return handler(url, params or {})
    monkeypatch.setattr(sx.requests, "get", fake_get)
    return calls


SHAPE = {"src", "title", "text", "url", "date"}


def test_stackexchange_items(monkeypatch, no_sleep):
    calls = route(monkeypatch, lambda url, p: FakeResp({"items": [{
        "title": "Is there a tool to split stems?", "body": "<p>I would <b>pay</b> for it</p>",
        "link": "https://music.stackexchange.com/q/1", "creation_date": 1762300800, "score": 7}],
        "quota_remaining": 250}))
    out = sx.stackexchange(sites=["music"], phrases=["is there a tool", "alternative to"])
    assert len(out) == 2 and len(calls) == 2
    it = out[0]
    assert SHAPE <= set(it)
    assert it["src"] == "stackexchange music"
    assert it["text"] == "I would pay for it"
    assert it["date"] == "2025-11-05"
    assert calls[0][1]["site"] == "music" and calls[0][1]["filter"] == "withbody"
    assert "key" not in calls[0][1]


def test_stackexchange_stops_on_low_quota(monkeypatch, no_sleep):
    calls = route(monkeypatch, lambda url, p: FakeResp({"items": [], "quota_remaining": 3}))
    sx.stackexchange(sites=["superuser", "webapps"], phrases=["a", "b"])
    assert len(calls) == 1


def test_stackexchange_error_does_not_stop(monkeypatch, no_sleep):
    n = {"i": 0}

    def h(url, p):
        n["i"] += 1
        return FakeResp({}, 500) if n["i"] == 1 else FakeResp({"items": [
            {"title": "t", "body": "b", "link": "l", "creation_date": 0}]})
    route(monkeypatch, h)
    assert len(sx.stackexchange(sites=["superuser"], phrases=["a", "b"])) == 1


def yt_handler(url, p):
    if url.endswith("/search"):
        return FakeResp({"items": [{"id": {"videoId": "v1"}, "snippet": {"title": "Best DJ app"}},
                                   {"id": {"videoId": "v2"}, "snippet": {"title": "Off"}}]})
    if p["videoId"] == "v2":
        return FakeResp({}, 403)   # comments disabled
    return FakeResp({"items": [
        {"id": "c1", "snippet": {"topLevelComment": {"snippet": {
            "textDisplay": "I wish there was an app that syncs cue points across all my devices",
            "publishedAt": "2026-10-01T10:00:00Z", "likeCount": 12}}}},
        {"id": "c2", "snippet": {"topLevelComment": {"snippet": {
            "textDisplay": "great video", "publishedAt": "2026-10-01T10:00:00Z"}}}}]})


def test_youtube_items_and_key_never_printed(monkeypatch, no_sleep, capsys):
    calls = route(monkeypatch, yt_handler)
    out = sx.youtube(queries=["best DJ software"], key="SECRET")
    assert len(out) == 1                       # short comment filtered, v2 skipped
    it = out[0]
    assert SHAPE <= set(it)
    assert it["src"] == "youtube 'best DJ software'"
    assert it["url"] == "https://www.youtube.com/watch?v=v1&lc=c1"
    assert it["date"] == "2026-10-01" and it["likes"] == 12
    assert calls[0][1]["maxResults"] == sx.YT_VIDEOS
    assert "SECRET" not in capsys.readouterr().out


def test_youtube_without_key_skips(monkeypatch, no_sleep):
    calls = route(monkeypatch, yt_handler)
    assert sx.youtube(queries=["x"], key="") == []
    assert calls == []


def test_github_items(monkeypatch, no_sleep):
    calls = route(monkeypatch, lambda url, p: FakeResp({"items": [{
        "title": "Add offline mode", "body": None, "html_url": "https://github.com/a/b/issues/1",
        "repository_url": "https://api.github.com/repos/a/b", "created_at": "2026-01-02T00:00:00Z",
        "reactions": {"total_count": 120}}]}))
    out = sx.github(labels=["enhancement"])
    assert len(out) == 1
    it = out[0]
    assert SHAPE <= set(it)
    assert it["src"] == "github a/b" and it["reactions"] == 120 and it["text"] == ""
    q = calls[0][1]["q"]
    assert 'label:"enhancement"' in q and "reactions:>=" in q and "is:issue" in q
    assert calls[0][1]["sort"] == "reactions"


def mk(src, n):
    return [{"src": src, "title": "t", "text": f"{src} {i}", "url": f"u{i}", "date": ""} for i in range(n)]


def fam_counts(items):
    c = {}
    for it in items:
        c[sx.family(it)] = c.get(sx.family(it), 0) + 1
    return c


def test_balance_caps_largest_family_at_half():
    items = mk("appstore A (X)", 1500) + mk("appstore B (Y)", 900) + mk("reddit r/a", 300) + mk("hackernews", 100)
    out = sx.balance(items)
    c = fam_counts(out)
    assert c["reddit"] == 300 and c["hackernews"] == 100
    assert c["appstore"] <= 0.5 * len(out) and c["appstore"] == 400
    srcs = [it["src"] for it in out if it["src"].startswith("appstore")]
    assert srcs.count("appstore A (X)") == 200 and srcs.count("appstore B (Y)") == 200   # round-robin


def test_balance_leaves_balanced_sample_alone():
    items = mk("reddit r/a", 100) + mk("github a/b", 80) + mk("youtube 'q'", 60)
    assert sx.balance(items) == items


def test_balance_single_family_untouched():
    items = mk("appstore A (X)", 10)
    assert sx.balance(items) == items
