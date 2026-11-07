from datetime import date

from scene_intelligence import ig_reenrich_contacts as rc
from scene_intelligence import si_follow_flags as ff


PROF = {"follower_count": 5066, "following_count": 300, "media_count": 40,
        "is_private": False, "is_verified": False, "biography": "new bio"}


def test_run_batch_refreshes_and_flags_dead_only_on_second_day():
    today = date(2026, 11, 4)
    batch = [{"ig_username": "eskimo"},
             {"ig_username": "gone_once"},
             {"ig_username": "gone_before", "ig_reenrich_failed_at": "2026-10-01"},
             {"ig_username": "flaky"}]
    answers = {"eskimo": ("ok", PROF), "gone_once": ("missing", None),
               "gone_before": ("missing", None), "flaky": ("error", None)}
    ok, fail, dead = rc.run_batch(batch, lambda u: answers[u], today, "2026-11-04T10:00:00", lambda: None)
    assert (ok, fail, dead) == (1, 3, 1)
    e, g1, g2, fl = batch
    assert e["ig_followers"] == 5066 and e["ig_bio"] == "new bio" and e["ig_enriched_at"].startswith("2026-11-04")
    assert g1.get("ig_reenrich_failed_at") == "2026-11-04" and not g1.get("ig_handle_dead")
    assert g2["ig_handle_dead"] is True
    assert "ig_handle_dead" not in fl and "ig_reenrich_failed_at" not in fl   # errors never mark anything


def test_run_batch_same_day_miss_does_not_kill():
    today = date(2026, 11, 4)
    x = {"ig_username": "a", "ig_reenrich_failed_at": "2026-11-04"}
    rc.run_batch([x], lambda u: ("missing", None), today, "t", lambda: None)
    assert not x.get("ig_handle_dead")


def test_run_batch_breaker_stops_on_consecutive_errors():
    calls = []
    batch = [{"ig_username": f"u{i}"} for i in range(10)]
    rc.run_batch(batch, lambda u: calls.append(u) or ("error", None), date(2026, 11, 4), "t", lambda: None)
    assert len(calls) == rc.MAX_CONSECUTIVE_FAILURES


def _lists(fol, fwg, complete=True, pf=None, pg=None):
    return {"profile": {"follower_count": pf if pf is not None else len(fol),
                        "following_count": pg if pg is not None else len(fwg)},
            "followers": [{"username": u} for u in fol], "followers_complete": complete,
            "following": [{"username": u} for u in fwg], "following_complete": complete}


def test_usable_refuses_short_or_incomplete_lists():
    assert ff.usable(_lists(["a"], ["b"]))[0]
    assert not ff.usable(_lists(["a"], ["b"], complete=False))[0]
    assert not ff.usable(_lists(["a"] * 90, ["b"], pf=100))[0]      # 90% < 97%
    assert ff.usable(_lists(["a"] * 98, ["b"], pf=100))[0]


def test_apply_sets_flags_keeps_dates_skips_no_handle():
    cs = [{"ig_username": "@Mutual", "ig_i_followed_at": "2018-09-18"},
          {"ig_username": "left", "ig_follows_me": True, "ig_i_follow": True},
          {"name": "no handle"}]
    n = ff.apply(cs, followers={"mutual"}, following={"mutual"}, checked="2026-11-04", source="own_lists_2026-11-04")
    assert n == 2
    m, l, nh = cs
    assert m["ig_mutual"] and m["ig_i_followed_at"] == "2018-09-18" and m["ig_relationship_checked"] == "2026-11-04"
    assert not l["ig_i_follow"] and not l["ig_follows_me"] and not l["ig_mutual"]
    assert "ig_i_follow" not in nh


from scene_intelligence import ig_reciprocity_from_lists as rl


def _trk():
    return {"stats": {"last_checked": "2026-10-10"}, "active_follows": [
        {"username": "Back", "followed_back": False},
        {"username": "notback", "followed_back": False},
        {"username": "keep", "followed_back": True}]}


def test_reciprocity_trusted_list_writes_both_sides():
    d = {"profile": {"follower_count": 100}, "followers_complete": True,
         "followers": [{"username": "back"}, {"username": "keep"}] + [{"username": f"x{i}"} for i in range(98)]}
    roster, trusted = rl.roster_from(d)
    assert trusted
    t = _trk()
    res = rl.apply_roster(t, roster, trusted, "2026-11-03")
    b, n, k = t["active_follows"]
    assert b["followed_back"] and b["followback_verified_at"] == "2026-11-03"
    assert not n["followed_back"] and n["followback_verified_at"] == "2026-11-03"
    assert t["stats"]["last_checked"] == "2026-11-03" and res["verified_non_followers"] == 1


def test_reciprocity_short_list_writes_positives_only():
    d = {"profile": {"follower_count": 100}, "followers_complete": True,
         "followers": [{"username": "back"}]}
    roster, trusted = rl.roster_from(d)
    assert not trusted
    t = _trk()
    rl.apply_roster(t, roster, trusted, "2026-11-03")
    b, n, _k = t["active_follows"]
    assert b["followed_back"] and "followback_verified_at" not in n   # absence proves nothing
    assert t["stats"]["last_checked"] == "2026-10-10"
