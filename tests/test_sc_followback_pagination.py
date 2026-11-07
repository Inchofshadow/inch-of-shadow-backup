"""Follow-back detection must see ALL followers, not the first 200 (audit P3-17).

The old single GET /me/followers?limit=200 truncated silently; a reciprocator
on page 2 read as "no follow-back" and was fed to the unfollow sweep — the
engine-side twin of the 2026-07-15 manual churn incident. Pagination must
also fail CLOSED: a partial follower set re-creates the truncation bug, so
any page failure aborts the whole check.
"""
import scene_intelligence.sc_engagement as sc


def _fake_sc_get(pages):
    """Return a sc_get stub serving canned pages keyed by path/URL."""
    calls = []

    def fake(path, params=None):
        calls.append(path)
        return pages.get(path)

    return fake, calls


def test_single_page_no_next_href(monkeypatch):
    pages = {"/me/followers": {"collection": [{"id": 1}, {"id": 2}]}}
    fake, _ = _fake_sc_get(pages)
    monkeypatch.setattr(sc, "sc_get", fake)
    assert sc.fetch_all_follower_ids() == {"1", "2"}


def test_follows_next_href_across_pages(monkeypatch):
    nxt = "https://api.soundcloud.com/me/followers?cursor=abc&limit=200"
    pages = {
        "/me/followers": {"collection": [{"id": 1}], "next_href": nxt},
        nxt: {"collection": [{"id": 2}, {"id": 3}]},
    }
    fake, calls = _fake_sc_get(pages)
    monkeypatch.setattr(sc, "sc_get", fake)
    assert sc.fetch_all_follower_ids() == {"1", "2", "3"}
    assert calls == ["/me/followers", nxt]


def test_mid_pagination_failure_returns_none(monkeypatch):
    # partial data must NOT be returned — that is the truncation bug again
    nxt = "https://api.soundcloud.com/me/followers?cursor=abc"
    pages = {"/me/followers": {"collection": [{"id": 1}], "next_href": nxt}}
    fake, _ = _fake_sc_get(pages)  # nxt missing -> sc_get returns None
    monkeypatch.setattr(sc, "sc_get", fake)
    assert sc.fetch_all_follower_ids() is None


def test_first_page_failure_returns_none(monkeypatch):
    monkeypatch.setattr(sc, "sc_get", lambda path, params=None: None)
    assert sc.fetch_all_follower_ids() is None


def test_runaway_pagination_fails_closed(monkeypatch):
    # every page points to another page; must abort at max_pages with None
    def endless(path, params=None):
        return {"collection": [{"id": 9}],
                "next_href": "https://api.soundcloud.com/loop"}

    monkeypatch.setattr(sc, "sc_get", endless)
    assert sc.fetch_all_follower_ids(max_pages=3) is None


def test_reciprocator_on_page_two_detected(monkeypatch):
    # the actual regression: entry 777 reciprocated but sat past entry 200
    nxt = "https://api.soundcloud.com/me/followers?cursor=p2"
    pages = {
        "/me/followers": {"collection": [{"id": i} for i in range(200)],
                          "next_href": nxt},
        nxt: {"collection": [{"id": 777}]},
    }
    fake, _ = _fake_sc_get(pages)
    monkeypatch.setattr(sc, "sc_get", fake)

    tracker = {"follows": [{"user_id": "777", "name": "pagetwo"}],
               "stats": {}}
    assert sc.update_follow_back_status(tracker) == 1
    assert tracker["follows"][0]["followed_back"] is True


def test_fetch_failure_updates_nothing(monkeypatch):
    # SC-02 (2026-09-01): a failed fetch now returns None (fail closed), not 0
    # — 0 used to be indistinguishable from "checked, no news" and let the
    # sweep run on stale reciprocity flags.
    monkeypatch.setattr(sc, "sc_get", lambda path, params=None: None)
    tracker = {"follows": [{"user_id": "1", "name": "x"}], "stats": {}}
    assert sc.update_follow_back_status(tracker) is None
    assert "followed_back" not in tracker["follows"][0]
