"""HikerAPI provider client (2026-09-14) -- mocked transport, zero network."""
import json
import pytest
import scene_intelligence.ig_data_provider as dp
import scene_intelligence.ig_daily_ledger as dl
from datetime import datetime


class _Resp:
    def __init__(self, code, body):
        self.status_code = code; self._b = body; self.text = json.dumps(body)
    def json(self):
        return self._b


class _Sess:
    def __init__(self, routes):
        self.routes = routes; self.calls = []
    def get(self, url, params=None, timeout=None, headers=None):
        self.calls.append((url, params, headers))
        for k, v in self.routes.items():
            if url.endswith(k):
                return _Resp(*v)
        return _Resp(404, {})


def _prov(routes):
    return dp.Provider(key="k", session=_Sess(routes))


def test_profile_normalised_and_header_sent():
    p = _prov({"/v1/user/by/username": (200, {"pk": 3619491348, "username": "samo_records",
               "follower_count": 2483, "following_count": 1040, "media_count": 330,
               "is_private": False, "is_verified": False, "biography": "VA Oval - Out Now",
               "category_name": "Record label"})})
    u = p.profile("samo_records")
    assert u["id"] == "3619491348" and u["follower_count"] == 2483 and u["biography"].startswith("VA")
    assert p.s.calls[0][2]["x-access-key"] == "k" and p.calls == 1


def test_profile_missing_returns_none():
    assert _prov({}).profile("nobody") is None


def test_newest_post_uses_max_not_first():
    p = _prov({"/v1/user/medias": (200, [
        {"taken_at": "2026-05-04T12:05:40Z"},          # pinned, old
        {"taken_at": "2026-09-10T10:00:00Z"},
        {"taken_at": 1757000000}])})
    ep = p.newest_post_epoch(1)
    assert ep == int(datetime.fromisoformat("2026-09-10T10:00:00+00:00").timestamp())


def test_followers_page_unpacks_list_shape():
    p = _prov({"/v1/user/followers/chunk": (200, [[{"pk": "1", "username": "a", "is_private": False},
                                                   {"pk": "2", "username": "b", "is_private": True}], "CURSOR2"])})
    users, nxt = p.followers_page(9)
    assert [u["username"] for u in users] == ["a", "b"] and users[1]["is_private"] is True
    assert nxt == "CURSOR2"


def test_non_200_is_provider_error_not_ig_event():
    p = _prov({"/v1/user/by/username": (402, {"detail": "balance"})})
    with pytest.raises(dp.ProviderError):
        p.profile("x")


def test_legacy_body_walks_like_web_profile_info():
    body = dp.legacy_user_body(dp.normalise_profile({"pk": 5, "username": "z", "follower_count": 700,
                                                     "following_count": 300, "media_count": 40,
                                                     "biography": "italo"}))
    u = body["data"]["user"]
    assert u["edge_followed_by"]["count"] == 700 and u["edge_owner_to_timeline_media"]["count"] == 40


# --- ledger: provider kind ---------------------------------------------------

DAY = "2026-09-15"; NIGHT = datetime(2026, 9, 15, 2, 0)


def test_provider_claim_ignores_ig_timing_law(tmp_path):
    p = tmp_path / "l.json"
    dl.check_and_claim("ig_audit_queue_freshness", path=p, today=DAY, kind="provider",
                       est_calls=200, now=NIGHT)              # night + >150: fine
    dl.check_and_claim("ig_queue_builder", path=p, today=DAY, kind="provider",
                       est_calls=40, now=NIGHT)               # second job same day: fine
    runs = json.loads(p.read_text())["runs"]
    assert [r["kind"] for r in runs] == ["provider", "provider"]
    assert dl.provider_calls_today(DAY, p) == 240


def test_provider_cap_and_same_script_rule(tmp_path, monkeypatch):
    p = tmp_path / "l.json"
    monkeypatch.setattr(dl, "provider_cap", lambda: 300)
    dl.check_and_claim("ig_audit_queue_freshness", path=p, today=DAY, kind="provider", est_calls=250)
    with pytest.raises(SystemExit):
        dl.check_and_claim("ig_audit_queue_freshness", path=p, today=DAY, kind="provider", est_calls=1)
    with pytest.raises(SystemExit):
        dl.check_and_claim("ig_queue_builder", path=p, today=DAY, kind="provider", est_calls=60)
    assert len(json.loads(p.read_text())["runs"]) == 1


def test_provider_claims_do_not_consume_the_ig_api_slot(tmp_path):
    p = tmp_path / "l.json"
    dl.check_and_claim("ig_queue_builder", path=p, today=DAY, kind="provider", est_calls=40)
    dl.check_and_claim("ig_fetch_insights", path=p, today=DAY, kind="api", est_calls=5,
                       endpoint="graph_insights", now=datetime(2026, 9, 15, 12, 0))
