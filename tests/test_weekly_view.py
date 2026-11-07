"""G-06 redesign: the This week panel data. Numbers from the snapshots; no network in tests."""

import json
from datetime import datetime

import pytest

from stats import weekly_summary as ws
from stats import weekly_view as wv


def snap(folder, stamp, followers, plays, track_plays, views):
    data = {"timestamp": stamp, "errors": [], "platforms": {
        "soundcloud": {"followers": followers, "following": 420, "total_plays": plays, "total_likes": 10,
                       "total_reposts": 1, "total_comments": 0,
                       "tracks": [{"title": "Inch of Shadow - Farewell", "plays": track_plays, "likes": 5, "artwork_url": ""},
                                  {"title": "Inch of Shadow - Electro DJ Set @ Johnny Knüppel | Berlin", "plays": 300, "likes": 2}]},
        "youtube": {"subscribers": 5, "total_views": views, "total_likes": 1, "video_count": 1,
                    "videos": [{"id": "abc", "title": "Inch of Shadow - Farewell (Official Audio)", "views": views}]}}}
    (folder / f"snapshot_{stamp}.json").write_text(json.dumps(data))


@pytest.fixture
def env(tmp_path, monkeypatch):
    from stats import spotify_s4a
    monkeypatch.setattr(spotify_s4a, "STORE", tmp_path / "spotify_s4a.json")
    monkeypatch.setattr(ws, "SNAPSHOTS", tmp_path)
    monkeypatch.setattr(ws, "OUT_FILE", tmp_path / "weekly-stats.md")
    monkeypatch.setattr(wv, "THUMBS", tmp_path / "thumbs")
    monkeypatch.setattr(wv, "ARTWORK", tmp_path / "artwork")
    return tmp_path


def test_tiles_series_movers_and_tips(env):
    for day, (f, p, t, v) in enumerate([(370, 2900, 700, 500), (380, 2950, 710, 505), (390, 3000, 734, 513)], start=6):
        snap(env, f"2026-10-{day:02d}T08-45-00", f, p, t, v)
    snap(env, "2026-10-13T08-45-00", 399, 3044, 768, 531)
    (env / "weekly-stats.md").write_text("# Weekly stats\n\n## Week to 2026-10-13 (vs 2026-10-06)\n\n"
                                         "- **Farewell +68 plays.** Pin it.\n- plain line\n")
    v = wv.build(datetime(2026, 10, 13, 9), fetch=False)
    tiles = {t["label"]: t for t in v["tiles"]}
    assert tiles["Followers"]["value"] == "399" and tiles["Followers"]["delta"] == 19 and tiles["Followers"]["dir"] == "up"
    assert tiles["Followers"]["platform"] == "SoundCloud" and tiles["Views"]["platform"] == "YouTube"
    assert tiles["Plays"]["days"] == 4 and tiles["Plays"]["spark"]["points"].count(",") == 4
    top = v["movers"][0]
    assert top["short"] == "Farewell" and top["gained"] == 58 and top["pct"] == 100.0 and top["art"] == ""
    assert top["letter"] == "F"
    assert v["tips"] == [{"title": "Farewell +68 plays", "action": "Pin it."}, {"title": "", "action": "plain line"}]


def test_short_names():
    assert wv._short("Inch of Shadow - Electro / EBM / Acid DJ Set @ Johnny Knüppel | Berlin 24.04.26") == "DJ set @ Johnny Knüppel"
    assert wv._short("Inch of Shadow & Status Zero – Mind Eaten (Meltscape EP)") == "Mind Eaten (Meltscape EP)"
    assert wv._short("Inch of Shadow - Farewell (Official Audio)") == "Farewell"


def test_local_cover_is_shrunk_into_the_thumb_folder(env):
    from PIL import Image
    (env / "artwork").mkdir()
    Image.new("RGB", (400, 400), (90, 20, 60)).save(env / "artwork" / "farewell-single.png")
    name = wv._local_cover("Inch of Shadow - Farewell")
    assert name == "local-farewell-single.jpg" and Image.open(env / "thumbs" / name).size == (96, 96)


def test_the_deceiver_uses_the_pieta_release_file():
    assert wv.LOCAL_COVERS["The Deceiver"] == "the-deceiver-single.png"


def test_a_failed_fetch_is_not_retried_for_a_day(env, monkeypatch):
    import requests
    calls = []
    monkeypatch.setattr(requests, "get", lambda *a, **k: calls.append(1) or (_ for _ in ()).throw(OSError("offline")))
    assert wv._fetch_thumb("https://example.com/a-large.jpg") == ""
    assert wv._fetch_thumb("https://example.com/a-large.jpg") == ""
    assert len(calls) == 1


def test_no_snapshots_means_no_panel(env):
    assert wv.build(datetime(2026, 10, 13), fetch=False) is None
