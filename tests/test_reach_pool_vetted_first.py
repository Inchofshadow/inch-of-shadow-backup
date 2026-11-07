"""Reach planning must prefer VETTED candidates (entries with an audit_date).

Regression for 2026-08-12: the reach pool ranked only on seed overlap, so plans
were diluted from the 666 unaudited queue entries even though 41 freshly vetted
candidates existed. That session's plan contained 5 accounts which return HTTP
400 on every audit attempt (jasonjppeters, alphanova_music, calystarrmusic,
aztronouth, vco_atk) -- unfollowable by construction. CC burned its 50-minute
cap failing on them and never reached the 5 vetted candidates in the same plan.
Session scored 3/10 against a pool that had just been refilled.
"""
import scene_intelligence.ig_engagement as eng

cfg = eng._import_config()


def _item(name, audit_date=None, seed_count=1):
    return {
        "username": name,
        "url": f"https://www.instagram.com/{name}/",
        "status": "pending",
        "seed_count": seed_count,
        "audit_date": audit_date,
    }


def _empty_tracker():
    return {"active_follows": [], "unfollowed_history": []}


def _plan(queue, cap=10):
    elig, _ = eng.build_reach_pool(
        cfg, {"queue": queue}, set(), set(), _empty_tracker(), set(),
        {"follows_per_session": cap},
    )
    return [e.handle for e in elig]


def test_vetted_candidates_outrank_unaudited():
    # Unaudited entries sit FIRST in queue order and carry higher seed_count,
    # i.e. every signal the old ranking used favoured them.
    queue = [_item(f"junk{i}", audit_date=None, seed_count=9) for i in range(10)]
    queue += [_item(f"vetted{i}", audit_date="2026-08-12", seed_count=1) for i in range(10)]

    picked = _plan(queue, cap=10)

    assert all(h.startswith("vetted") for h in picked), picked
    assert len(picked) == 10


def test_short_vetted_supply_behaviour_follows_the_config_flag():
    # 2026-08-26 (Amir): with REACH_VETTED_ONLY on, unaudited entries no longer
    # fill the tail -- a short vetted pool means a SMALLER plan (3 here), never
    # blind candidates (that day's tail-fill served a 25-follower account and a
    # 33-day-stale one). With the flag off, legacy tail-fill still applies.
    queue = [_item(f"junk{i}", audit_date=None) for i in range(10)]
    queue += [_item(f"vetted{i}", audit_date="2026-08-12") for i in range(3)]

    picked = _plan(queue, cap=10)

    if getattr(cfg, "REACH_VETTED_ONLY", False):
        assert len(picked) == 3, picked
        assert all(h.startswith("vetted") for h in picked), picked
    else:
        assert len(picked) == 10
        assert [h for h in picked[:3] if h.startswith("vetted")] == picked[:3], picked


def test_overlap_still_orders_within_the_vetted_group():
    queue = [
        _item("low", audit_date="2026-08-12", seed_count=1),
        _item("high", audit_date="2026-08-12", seed_count=7),
    ]
    picked = _plan(queue, cap=2)
    if getattr(cfg, "OVERLAP_SORT_ENABLED", False):
        assert picked[0] == "high", picked
    else:
        assert set(picked) == {"high", "low"}
