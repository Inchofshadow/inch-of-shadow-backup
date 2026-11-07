import scene_intelligence.curator_check_adds as ca


def test_track_id_from_url():
    assert ca.track_id_from_url("https://open.spotify.com/track/6lOM9849xsWTUGiBJBjpuE?si=x") == "6lOM9849xsWTUGiBJBjpuE"
    assert ca.track_id_from_url("") == ""


def test_track_in_playlist():
    assert ca.track_in_playlist("ABC", ["X", "ABC", "Y"]) is True
    assert ca.track_in_playlist("ABC", ["X", "Y"]) is False
    assert ca.track_in_playlist("", ["X"]) is False
