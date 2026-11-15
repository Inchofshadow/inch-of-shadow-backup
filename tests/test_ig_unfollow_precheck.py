"""2026-11-15: live follow-back precheck gate (Fable gate, Amir 'check each one live')."""
from datetime import date

import scene_intelligence.ig_unfollow_precheck as pc


def test_found_follower_is_kept_for_good():
    tr = {"active_follows": [{"username": "a"}, {"username": "b"}, {"username": "c"}]}
    n = pc.apply_results(tr, {"a": True, "b": False, "c": None}, "2026-11-16")
    a, b, c = tr["active_follows"]
    assert a["followed_back"] is True and a["followback_verified_at"] == "2026-11-16"
    assert b["precheck_not_follower_at"] == "2026-11-16" and "followed_back" not in b
    assert "precheck_not_follower_at" not in c
    assert n == {"follows_back": 1, "not_follower": 1, "error": 1}


def _entry(**kw):
    e = {"username": "x", "followed_at": "2026-10-01", "unfollow_after": "2026-10-08",
         "followed_back": False, "followback_verified_at": "2026-11-12"}
    e.update(kw)
    return e


def _plan(entry, today, required=True):
    import scene_intelligence.ig_engagement as E
    import scene_intelligence.ig_engagement_config as cfg
    old = getattr(cfg, "UNFOLLOW_PRECHECK_REQUIRED", False)
    cfg.UNFOLLOW_PRECHECK_REQUIRED = required
    try:
        tr = {"active_follows": [entry], "stats": {"last_checked": "2026-11-12"}}
        el, rej = E.plan_unfollow_sweep(cfg, tr, set(), set(), {"unfollows_per_session": 8}, today)
    finally:
        cfg.UNFOLLOW_PRECHECK_REQUIRED = old
    return el, rej


def test_engine_requires_todays_precheck():
    today = date(2026, 11, 16)
    el, rej = _plan(_entry(), today)
    assert el == [] and rej.get("no_live_precheck_today") == 1
    el, _ = _plan(_entry(precheck_not_follower_at="2026-11-14"), today)
    assert el == []
    el, _ = _plan(_entry(precheck_not_follower_at="2026-11-16"), today)
    assert [e.handle for e in el] == ["x"]


def test_gate_off_keeps_old_behaviour():
    el, _ = _plan(_entry(), date(2026, 11, 16), required=False)
    assert [e.handle for e in el] == ["x"]


def test_none_or_non_list_is_an_error_not_a_clear():
    assert pc.search_result(None, "x") is None
    assert pc.search_result({"users": []}, "x") is None
    assert pc.search_result([], "x") is False
    assert pc.search_result([{"username": "X"}], "x") is True


def test_control_prefers_dotted_follower():
    tr = {"active_follows": [{"username": "plain", "followed_back": True},
                             {"username": "mario.wavelet", "followed_back": True},
                             {"username": "nofb", "followed_back": False}]}
    assert pc.pick_control(tr) == "mario.wavelet"
    assert pc.pick_control({"active_follows": []}) is None
