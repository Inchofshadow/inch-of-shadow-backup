"""Reciprocator guard: live followed_by re-check at unfollow time.

Root cause (2026-06-26/27 churn of @gallowmaker, @pao_laportoghese, etc.):
plan_unfollow_sweep trusts the cached `followed_back` field, which goes stale
between follow-back checker runs (last run 2026-06-10). _execute_unfollow had
NO live reciprocity check, so a real reciprocator whose cache still said
followed_back=False got unfollowed.

The fix: re-check the live API `followed_by` signal at unfollow time. If they
follow back, abort the unfollow and heal the tracker cache. Defense-in-depth —
a reciprocator is never churned even when the cache is stale.
"""
from datetime import date

import scene_intelligence.ig_engagement as eng

cfg = eng._import_config()

# Never actually sleep during the test.
eng.jittered_sleep_seconds = lambda *a, **k: 0.0


class _ReciprocatorStub(eng.StubBrowserDriver):
    """Live state says: this profile DOES follow @inch_of_shadow back."""
    def follows_back(self):
        return True


class _NonReciprocatorStub(eng.StubBrowserDriver):
    """Live state says: this profile does NOT follow back."""
    def follows_back(self):
        return False


def _stale_tracker(handle="gallowmaker"):
    # Cache says followed_back=False, but the live API will say they DO follow back.
    return {
        "active_follows": [{
            "username": handle,
            "followed_at": "2026-06-10",
            "unfollow_after": "2026-06-17",
            "followed_back": False,
        }],
        "unfollowed_history": [],
        "stats": {},
    }


def _entry(handle="gallowmaker"):
    return eng.UnfollowEntry(
        handle=handle, followed_at="2026-06-10",
        unfollow_after="2026-06-17", reason="7day_rule_no_follow_back",
    )


def test_reciprocator_is_not_unfollowed_and_cache_is_healed():
    drv = _ReciprocatorStub(verbose=False)
    tracker = _stale_tracker()
    result = eng.SessionResult(started_at="2026-06-27T00:00:00")

    eng._execute_unfollow(cfg, drv, _entry(), tracker, {}, result)

    # The unfollow must have been aborted.
    assert result.unfollows_done == 0
    assert not any(a["kind"] == "unfollow" for a in drv.actions)
    # Stays followed, and the stale cache is healed to followed_back=True.
    assert len(tracker["active_follows"]) == 1
    assert tracker["active_follows"][0]["followed_back"] is True
    assert tracker["unfollowed_history"] == []


def test_non_reciprocator_is_unfollowed_normally():
    drv = _NonReciprocatorStub(verbose=False)
    tracker = _stale_tracker()
    result = eng.SessionResult(started_at="2026-06-27T00:00:00")

    eng._execute_unfollow(cfg, drv, _entry(), tracker, {}, result)

    # Genuine non-reciprocator: normal unfollow proceeds.
    assert result.unfollows_done == 1
    assert any(a["kind"] == "unfollow" for a in drv.actions)
    assert tracker["active_follows"] == []
    assert len(tracker["unfollowed_history"]) == 1


# --- Freshness gate: the structural fix (plan_unfollow_sweep) ---

def _sweep_tracker(last_checked, due_handle="somedue", verified_at="2026-06-28",
                   followed_at="2026-06-10"):
    # verified_at defaults to "measured yesterday". Pass None to model an entry
    # whose reciprocity was never successfully measured (2026-08-28: 26 of 28
    # entries were in that state and the sweep treated them as eligible).
    entry = {
        "username": due_handle,
        "followed_at": followed_at,
        "unfollow_after": "2026-06-17",  # due as of 2026-06-29
        "followed_back": False,
    }
    if verified_at is not None:
        entry["followback_verified_at"] = verified_at
    return {
        "active_follows": [entry],
        "unfollowed_history": [],
        "stats": {"last_checked": last_checked},
    }


_PHASE = {"unfollows_per_session": 8}


def test_sweep_blocked_when_followback_data_is_stale():
    # Export-era (2026-08-31): global freshness = the ~30-day export cadence.
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-05-25")  # 35 days stale > 30
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    assert eligible == []
    assert "followback_data_stale_sweep_blocked" in rejects


def test_sweep_blocked_when_last_checked_missing():
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-06-10")
    tracker["stats"] = {}  # no last_checked at all
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    assert eligible == []
    assert "followback_data_stale_sweep_blocked" in rejects


def test_sweep_runs_when_export_verification_covers_window():
    # Export law (2026-08-31): eligible = verification is recent (<=30d) AND
    # dated >= followed_at + 21d, so the export covers the whole follow-back
    # window. Followed May 15, verified Jun 28 (44d later), today Jun 29.
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-06-28", followed_at="2026-05-15",
                             verified_at="2026-06-28")
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    assert len(eligible) == 1
    assert eligible[0].handle == "somedue"


def test_recent_follow_blocked_until_export_covers_window():
    # Followed Jun 10, verified Jun 28 — only 18 days after the follow: the
    # export cannot prove they didn't follow back later. Protected until the
    # NEXT export (>= followed_at + 21d). This replaces the old same-day
    # checker rule and is what keeps the @infoluences/@_.miser._ class dead.
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-06-28", followed_at="2026-06-10",
                             verified_at="2026-06-28")
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    assert eligible == []
    assert "followback_verification_stale_or_window" in rejects


def test_unverified_entry_is_never_swept():
    """FAIL-CLOSED (2026-08-28, after @_.miser._): an entry whose reciprocity was
    never successfully measured must be protected, not eligible. Global
    stats.last_checked is fresh here -- only the per-entry stamp is missing,
    which is exactly the 2026-08-28 shape (26 of 28 unresolvable user_ids,
    last_checked stamped anyway)."""
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-06-29", verified_at=None)
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    if getattr(cfg, "FOLLOWBACK_REQUIRE_VERIFIED", False):
        assert eligible == [], eligible
        assert "followback_unverified_protected" in rejects, rejects
    else:
        assert len(eligible) == 1


def test_entry_with_stale_verification_is_not_swept():
    today = date(2026, 6, 29)
    tracker = _sweep_tracker("2026-06-29", followed_at="2026-04-01",
                             verified_at="2026-05-20")  # 40 days old > 30
    eligible, rejects = eng.plan_unfollow_sweep(cfg, tracker, set(), set(), _PHASE, today)
    if getattr(cfg, "FOLLOWBACK_REQUIRE_VERIFIED", False):
        assert eligible == [], eligible
        assert "followback_verification_stale_or_window" in rejects, rejects
