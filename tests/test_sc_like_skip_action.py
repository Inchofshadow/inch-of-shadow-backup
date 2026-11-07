"""`sc_like_skip` must be a loggable action (added 2026-08-12).

close_loops now credits already-liked skips toward the like target, mirroring
IG's `ig_unfollow_skip`. That only works if CC can actually log one. The CLI
accepted only sc_like / sc_repost / sc_follow / sc_unfollow, so the documented
command would have died on an argparse error.

A skip has no track_id (the point is that no track was liked), so it must not
inherit the sc_like requirement for --track-id.
"""
import scene_intelligence.sc_engagement as sc


def test_sc_like_skip_is_an_accepted_action_type():
    assert "sc_like_skip" in sc.LOG_ACTION_TYPES


def test_skip_does_not_require_a_track_id():
    assert "sc_like_skip" not in sc.TRACK_REQUIRED_ACTIONS
    assert "sc_like" in sc.TRACK_REQUIRED_ACTIONS


def test_skip_is_not_capped_as_a_real_like():
    """A skip is not an engagement action, so it must not count toward SC caps."""
    import scene_intelligence.close_loops as cl
    assert "sc_like_skip" not in cl.SC_CAPS


def test_log_sc_action_records_a_skip(tmp_path):
    eng = {"log": {}}
    sc.log_sc_action("someartist", "sc_like_skip",
                     {"reason": "all visible tracks already liked"}, eng)
    entries = eng["log"]["someartist"]
    assert len(entries) == 1
    assert entries[0]["action"] == "sc_like_skip"
    assert entries[0]["platform"] == "soundcloud"
    assert entries[0]["reason"] == "all visible tracks already liked"
