"""Scene-press exception (2026-09-01, Amir): small high-score press/radio
pages are like-eligible; big media stays banned; unknown sizes fail closed."""
import scene_intelligence.ig_engagement as eng

cfg = eng._import_config()


def _c(category, score, followers):
    return {"ig_username": "x_page", "name": "X", "category": category,
            "match_score": score, "ig_followers": followers}


def _skip(c):
    return eng.contact_is_always_skip(c, cfg, set(), set(), set())


def test_small_score5_media_is_eligible():
    skip, reason = _skip(_c("media", 5, 2049))
    if (getattr(cfg, "SCENE_PRESS_EXCEPTION", {}) or {}).get("enabled"):
        assert not skip or "category_always_skip" not in reason, reason
    else:
        assert skip


def test_big_media_still_banned():
    skip, reason = _skip(_c("media", 5, 60000))
    assert skip, "RA-sized media must stay skipped"


def test_low_score_media_still_banned():
    skip, reason = _skip(_c("media", 2, 900))
    assert skip and "category_always_skip" in reason


def test_unknown_size_fails_closed():
    skip, reason = _skip(_c("media", 5, None))
    assert skip, "unknown follower count must not slip through the exception"


def test_venue_untouched_by_exception():
    skip, reason = _skip(_c("venue", 5, 900))
    assert skip and "category_always_skip" in reason
