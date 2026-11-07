"""A SoundCloud like/repost may be identified by the track's web address when
the numeric id is unreadable (2026-09-08: the browser surface exposes no track
ids, so a verified like could not be logged and the session stopped at 1 action).

The address is a stable per-track key, so the re-like guard keeps working."""
import scene_intelligence.sc_engagement as sc


def test_normalise_strips_host_query_and_case():
    n = sc.normalise_track_url
    assert n("https://soundcloud.com/ferrersantis/kinesis") == "ferrersantis/kinesis"
    assert n("https://soundcloud.com/FerrerSantis/Kinesis?in=x&si=y") == "ferrersantis/kinesis"
    assert n("/ferrersantis/kinesis/") == "ferrersantis/kinesis"
    assert n("soundcloud.com/ferrersantis/kinesis") == "ferrersantis/kinesis"
    assert n("") == ""
    assert n(None) == ""


def test_normalise_rejects_non_track_paths():
    # a bare profile, or a profile tab, is not a track
    assert sc.normalise_track_url("https://soundcloud.com/ferrersantis") == ""
    assert sc.normalise_track_url("https://soundcloud.com/ferrersantis/sets") == ""
    assert sc.normalise_track_url("https://soundcloud.com/ferrersantis/popular-tracks") == ""


def _log(entry):
    return {"log": {"ferrer_santis": [entry]}}


def test_was_track_liked_matches_on_url_when_no_id():
    from datetime import date
    eng = _log({"platform": "soundcloud", "action": "sc_like",
                "track_url": "ferrersantis/kinesis", "date": date.today().isoformat()})
    assert sc.was_track_liked("", eng, track_url="https://soundcloud.com/ferrersantis/kinesis")
    assert not sc.was_track_liked("", eng, track_url="ferrersantis/other-track")


def test_was_track_liked_still_matches_on_id():
    from datetime import date
    eng = _log({"platform": "soundcloud", "action": "sc_like",
                "track_id": "2384498973", "date": date.today().isoformat()})
    assert sc.was_track_liked("2384498973", eng)
    assert not sc.was_track_liked("9999999999", eng)


def test_was_track_reposted_matches_on_url():
    from datetime import date
    eng = _log({"platform": "soundcloud", "action": "sc_repost",
                "track_url": "ferrersantis/kinesis", "date": date.today().isoformat()})
    assert sc.was_track_reposted("", eng, track_url="ferrersantis/kinesis")


def test_track_identifier_required_accepts_either():
    assert sc.track_identifier_missing(track_id="", track_url="") is True
    assert sc.track_identifier_missing(track_id="123", track_url="") is False
    assert sc.track_identifier_missing(
        track_id="", track_url="https://soundcloud.com/a/b") is False
    # a profile URL is not a track identifier
    assert sc.track_identifier_missing(
        track_id="", track_url="https://soundcloud.com/ferrersantis") is True
