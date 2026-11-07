"""Discovery must reject reposts-only accounts (added 2026-08-28).

SoundCloud's `track_count` on a user object COUNTS REPOSTS. An account that has
never uploaded anything but reposts other artists therefore sails past the
`DISCOVERY_MIN_TRACKS` gate.

`zc_ned` (user_id 143374775) reported track_count 16 and was briefed as a follow
target on BOTH 2026-08-27 and 2026-08-28. Checking the profile showed ZERO own
uploads — every item was a repost of another artist, whose href points at the
OTHER artist's account. Liking one credits a third party, and the account is a
curator, not a peer producer, so it is a poor follow target either way.

`_has_own_uploads` inspects the fetched track list and confirms at least one
track actually belongs to the candidate.
"""
import scene_intelligence.sc_engagement as sc


def _track(user_id, permalink_url=None):
    t = {"user": {"id": user_id}}
    if permalink_url:
        t["permalink_url"] = permalink_url
    return t


def test_all_reposts_is_rejected():
    """zc_ned: every track belongs to someone else."""
    tracks = [_track(999), _track(888), _track(777)]
    assert not sc._has_own_uploads(tracks, "143374775")


def test_at_least_one_own_upload_passes():
    tracks = [_track(999), _track(143374775), _track(888)]
    assert sc._has_own_uploads(tracks, "143374775")


def test_all_own_uploads_passes():
    tracks = [_track(42), _track(42)]
    assert sc._has_own_uploads(tracks, "42")


def test_handles_string_vs_int_user_ids():
    assert sc._has_own_uploads([_track("42")], 42)
    assert sc._has_own_uploads([_track(42)], "42")


def test_empty_track_list_is_rejected():
    assert not sc._has_own_uploads([], "42")
    assert not sc._has_own_uploads(None, "42")


def test_missing_user_object_does_not_crash():
    assert not sc._has_own_uploads([{"title": "no user key"}], "42")


def test_falls_back_to_permalink_url_when_user_id_absent():
    """Some track payloads omit the nested user id but carry the URL."""
    tracks = [{"permalink_url": "https://soundcloud.com/someoneelse/track-a"}]
    assert not sc._has_own_uploads(tracks, "42", permalink="myhandle")
    tracks2 = [{"permalink_url": "https://soundcloud.com/myhandle/track-b"}]
    assert sc._has_own_uploads(tracks2, "42", permalink="myhandle")
