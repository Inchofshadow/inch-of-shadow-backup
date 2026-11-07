import stats.collectors as c


class R:  # minimal requests.Response stand-in
    def __init__(self, code, data):
        self.status_code, self._d = code, data

    def json(self):
        return self._d


def test_graph_variant_reads_profile_and_reach(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph")
    monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    monkeypatch.setattr(c, "_claim", lambda **kw: None)
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if url.endswith("/me"):
            return R(200, {"followers_count": 951, "follows_count": 970, "media_count": 85})
        return R(200, {"data": [{"name": "reach", "total_value": {"value": 2310}}]})

    monkeypatch.setattr(c.requests, "get", fake_get)
    assert c.collect_instagram_daily() == {
        "followers": 951, "following": 970, "media_count": 85, "reach_30d": 2310, "source": "graph"}
    assert len(calls) == 2


def test_ledger_refusal_returns_none_and_sync_keeps_other_platforms(monkeypatch):
    from scene_intelligence.ig_daily_ledger import LedgerRefused

    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph")
    monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    claimed = []

    def refuse(**kw):
        claimed.append(kw)
        raise LedgerRefused(4)

    monkeypatch.setattr(c, "_claim", refuse)
    monkeypatch.setattr(c, "_provider", lambda: (_ for _ in ()).throw(AssertionError("no read after refusal")))
    assert c.collect_instagram_daily() == {"skipped": "ledger refused the Instagram read: 4"}   # a reason, never None or 0
    assert [k["kind"] for k in claimed] == ["api", "provider"]
    monkeypatch.setattr(c, "collect_spotify", lambda: {"ok": 1})
    monkeypatch.setattr(c, "collect_soundcloud", lambda: None)
    monkeypatch.setattr(c, "collect_youtube", lambda: None)
    monkeypatch.setattr(c, "collect_hikerapi_balance", lambda: {"requests": 83000})
    out = c.collect_all()
    assert out["platforms"]["spotify"] == {"ok": 1}
    assert "instagram" in out["errors"]
    assert out["platforms"]["instagram"]["skipped"].startswith("ledger refused")
    assert out["skipped"]["soundcloud"] == "collector returned nothing"
    assert out["platforms"]["hikerapi"]["requests"] == 83000


def test_graph_claim_gate_falls_back_to_hikerapi(monkeypatch):
    """OpsGate / LedgerRefused on the api claim (a SystemExit) -> HikerAPI reading."""
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph")
    monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    claims = []

    def fake_claim(**kw):
        claims.append(kw["kind"])
        if kw["kind"] == "api":
            raise SystemExit("outside 09:00-21:00")
        return None

    monkeypatch.setattr(c, "_claim", fake_claim)
    monkeypatch.setattr(c.requests, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no Graph call")))

    class P:
        def profile(self, u):
            return {"follower_count": 952, "following_count": 971, "media_count": 85}

    monkeypatch.setattr(c, "_provider", lambda: P())
    out = c.collect_instagram_daily()
    assert out == {"followers": 952, "following": 971, "media_count": 85, "reach_30d": None, "source": "hikerapi"}
    assert claims == ["api", "provider"]


def test_hikerapi_variant(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "hikerapi")
    claims = []
    monkeypatch.setattr(c, "_claim", lambda **kw: claims.append(kw))

    class P:
        def profile(self, u):
            return {"username": u, "follower_count": 952, "following_count": 971, "media_count": 85}

    monkeypatch.setattr(c, "_provider", lambda: P())
    out = c.collect_instagram_daily()
    assert out == {"followers": 952, "following": 971, "media_count": 85, "reach_30d": None, "source": "hikerapi"}
    assert claims == [dict(script="stats_daily_sync", kind="provider", est_calls=1, endpoint="user_by_username")]


def test_graph_profile_failure_falls_back_to_hikerapi(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph")
    monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    claims = []
    monkeypatch.setattr(c, "_claim", lambda **kw: claims.append(kw))
    monkeypatch.setattr(c.requests, "get", lambda url, params=None, timeout=None: R(400, {}))

    class P:
        def profile(self, u):
            return {"follower_count": 9, "following_count": 8, "media_count": 7}

    monkeypatch.setattr(c, "_provider", lambda: P())
    out = c.collect_instagram_daily()
    assert out["source"] == "hikerapi" and out["followers"] == 9
    assert [k["kind"] for k in claims] == ["api", "provider"]


def test_graph_reach_failure_keeps_profile(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph")
    monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    monkeypatch.setattr(c, "_claim", lambda **kw: None)

    def fake_get(url, params=None, timeout=None):
        if url.endswith("/me"):
            return R(200, {"followers_count": 1, "follows_count": 2, "media_count": 3})
        return R(500, {})

    monkeypatch.setattr(c.requests, "get", fake_get)
    assert c.collect_instagram_daily()["reach_30d"] is None


def test_hikerapi_balance(monkeypatch):
    class P:
        def balance(self):
            return {"requests": 83000, "amount": 1.2}

    monkeypatch.setattr(c, "_provider", lambda: P())
    assert c.collect_hikerapi_balance() == {"requests": 83000, "balance": {"requests": 83000, "amount": 1.2}}

    def boom():
        raise RuntimeError("x")

    monkeypatch.setattr(c, "_provider", boom)
    assert c.collect_hikerapi_balance() == {"skipped": "RuntimeError: x"}

    class Q:
        def balance(self):
            return None  # Provider.balance() returns None on ProviderError

    monkeypatch.setattr(c, "_provider", lambda: Q())
    assert c.collect_hikerapi_balance() == {"skipped": "HikerAPI balance call returned nothing"}


# --- 2026-11-05 (System 68): HikerAPI is the default daily source -----------

def test_default_daily_source_is_hikerapi():
    """The scheduled sync reads the profile through HikerAPI (direct reads off since 09-14)."""
    assert c.IG_DAILY_SOURCE == "hikerapi"


def test_default_sync_claims_exactly_one_provider_call_and_stores_instagram(monkeypatch):
    claims = []
    monkeypatch.setattr(c, "_claim", lambda **kw: claims.append(kw))
    monkeypatch.setattr(c.requests, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no Graph call")))

    class P:
        def profile(self, u):
            assert u == "inch_of_shadow"
            return {"follower_count": 969, "following_count": 950, "media_count": 85}

        def balance(self):
            return {"requests": 83400}

    monkeypatch.setattr(c, "_provider", lambda: P())
    for name in ("spotify", "soundcloud", "youtube"):
        monkeypatch.setattr(c, f"collect_{name}", lambda: {"ok": 1})
    out = c.collect_all()
    assert out["platforms"]["instagram"] == {
        "followers": 969, "following": 950, "media_count": 85, "reach_30d": None, "source": "hikerapi"}
    assert out["errors"] == []
    assert claims == [dict(script="stats_daily_sync", kind="provider", est_calls=1, endpoint="user_by_username")]
