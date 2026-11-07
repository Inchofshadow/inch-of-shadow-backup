"""Tests for canonical engagement-log key resolution (added 2026-07-10).

The 2026-06-02 Armela incident fixed tracker `last_engaged` matching by giving it
the priority user_id > name > contact_key. The engagement LOG key never got the
same treatment: log_sc_action() used whatever --contact-key CC typed.

On 2026-07-10 that split four accounts into eight log identities. CC liked using
the discovery-file name and followed using the live display name:

    liked as cha_ptlt               followed as lun_          (both = LUNÅ)
    liked as cristina_aranda        followed as freya_dj      (both = Freya Dj)
    liked as irish_rep              followed as flip_the_lid  (both = Flip The Lid)
    liked as twentyfourhoursrecords followed as 24_h          (both = 24/H)

In every case CC passed the CORRECT name in --artist. The data to derive the
right key was in the same command, unused.

Note PASS A likes fire BEFORE PASS B follows, so at like time there is usually no
tracker entry to resolve user_id against. The artist fallback is the load-bearing
path, not the user_id one.
"""
import scene_intelligence.sc_engagement as sc


def _tracker(*entries):
    return {"follows": list(entries)}


def test_user_id_wins_over_artist_and_contact_key():
    tracker = _tracker({"user_id": "63760131", "name": "LUNÅ"})
    key = sc._resolve_log_key(
        contact_key="cha_ptlt", artist="Stale Name", user_id="63760131", tracker=tracker
    )
    assert key == "lun_"


def test_falls_back_to_artist_when_tracker_has_no_entry_yet():
    # PASS A: the like fires before the follow creates the tracker entry.
    key = sc._resolve_log_key(
        contact_key="cha_ptlt", artist="LUNÅ", user_id="63760131", tracker=_tracker()
    )
    assert key == "lun_"


def test_falls_back_to_contact_key_when_no_artist():
    key = sc._resolve_log_key(
        contact_key="some_slug", artist="", user_id="", tracker=_tracker()
    )
    assert key == "some_slug"


def test_artist_fallback_ignores_blank_and_whitespace_artist():
    key = sc._resolve_log_key(
        contact_key="some_slug", artist="   ", user_id="", tracker=_tracker()
    )
    assert key == "some_slug"


def test_user_id_miss_does_not_crash_and_falls_through():
    tracker = _tracker({"user_id": "999", "name": "Someone Else"})
    key = sc._resolve_log_key(
        contact_key="fallback_key", artist="Real Artist", user_id="63760131", tracker=tracker
    )
    assert key == "real_artist"


def test_tracker_entry_without_name_does_not_win():
    tracker = _tracker({"user_id": "63760131", "name": ""})
    key = sc._resolve_log_key(
        contact_key="cha_ptlt", artist="LUNÅ", user_id="63760131", tracker=tracker
    )
    assert key == "lun_"


def test_regression_the_four_2026_07_10_collisions():
    """Each of these produced a duplicate log identity on 2026-07-10."""
    cases = [
        ("cha_ptlt", "LUNÅ", "lun_"),
        ("cristina_aranda", "Freya Dj", "freya_dj"),
        ("irish_rep", "Flip The Lid", "flip_the_lid"),
        ("twentyfourhoursrecords", "24/H", "24_h"),
    ]
    for contact_key, artist, expected in cases:
        got = sc._resolve_log_key(
            contact_key=contact_key, artist=artist, user_id="", tracker=_tracker()
        )
        assert got == expected, f"{contact_key} + {artist!r} -> {got!r}, want {expected!r}"


def test_resolved_key_matches_what_sc_follow_would_write():
    """The whole point: like and follow must land on the same key."""
    artist = "24/H"
    like_key = sc._resolve_log_key(
        contact_key="twentyfourhoursrecords", artist=artist, user_id="", tracker=_tracker()
    )
    follow_key = sc._contact_key({"name": artist})
    assert like_key == follow_key
