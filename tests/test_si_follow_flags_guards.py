"""Socials 39 (2026-11-08): own-lists guards in si_follow_flags.py."""
import json
import sys
import types
from datetime import date

import scene_intelligence.si_follow_flags as f


def _lists(fc, gc, followers=(), following=()):
    return {"profile": {"follower_count": fc, "following_count": gc},
            "followers": [{"username": u} for u in followers], "followers_complete": True,
            "following": [{"username": u} for u in following], "following_complete": True}


def test_missing_profile_count_is_not_usable():
    ok, why = f.usable(_lists(0, 0))
    assert not ok and "profile count missing" in why


def test_full_lists_with_counts_are_usable():
    ok, _ = f.usable(_lists(2, 1, ["a", "b"], ["c"]))
    assert ok


def _fake_provider(monkeypatch, pages_fail):
    P = types.ModuleType("ig_data_provider")

    class ProviderError(RuntimeError):
        pass

    class Provider:
        calls = 0

        def profile(self, u):
            return {"id": "1", "follower_count": 1, "following_count": 1}

        def _get(self, path, **kw):
            self.calls += 1
            if pages_fail:
                raise ProviderError("404")
            return {"users": [{"username": "x"}], "next_max_id": None}

    P.Provider, P.ProviderError = Provider, ProviderError
    P._unpack_chunk = lambda data: (data["users"], data["next_max_id"])
    P.normalise_follower = lambda u: u
    L = types.ModuleType("ig_daily_ledger")
    L.check_and_claim = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "ig_data_provider", P)
    monkeypatch.setitem(sys.modules, "ig_daily_ledger", L)


def test_failed_fetch_is_not_saved_as_todays_lists(tmp_path, monkeypatch):
    monkeypatch.setattr(f, "LISTS_DIR", tmp_path)
    _fake_provider(monkeypatch, pages_fail=True)
    out = f.fetch_lists(date(2026, 11, 8))
    assert out.name == "failed-own-lists-2026-11-08.json"
    assert not list(tmp_path.glob("own-lists-*.json"))
    assert "error" in json.loads(out.read_text())


def test_good_fetch_is_saved_as_todays_lists(tmp_path, monkeypatch):
    monkeypatch.setattr(f, "LISTS_DIR", tmp_path)
    _fake_provider(monkeypatch, pages_fail=False)
    out = f.fetch_lists(date(2026, 11, 8))
    assert out.name == "own-lists-2026-11-08.json"
