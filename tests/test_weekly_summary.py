"""G-06: the weekly stats read. Numbers from the snapshots only; Claude writes the bullets (faked here)."""

import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from stats import weekly_summary as ws


def snap(folder, stamp, followers, following, plays, track_plays, views=100):
    data = {"timestamp": stamp, "errors": [], "platforms": {
        "soundcloud": {"followers": followers, "following": following, "total_plays": plays, "total_likes": 10,
                       "total_reposts": 1, "total_comments": 0,
                       "tracks": [{"title": "Farewell", "plays": track_plays, "likes": 5}]},
        "youtube": {"subscribers": 5, "total_views": views, "total_likes": 1, "video_count": 2,
                    "videos": [{"id": "v1", "title": "The Deceiver", "views": views}]}}}
    (folder / f"snapshot_{stamp}.json").write_text(json.dumps(data))


@pytest.fixture
def env(tmp_path, monkeypatch):
    from stats import spotify_s4a
    monkeypatch.setattr(spotify_s4a, "STORE", tmp_path / "spotify_s4a.json")   # no real Spotify reads in tests
    monkeypatch.setattr(ws, "SNAPSHOTS", tmp_path)
    monkeypatch.setattr(ws, "OUT_FILE", tmp_path / "weekly-stats.md")
    return tmp_path


class Fake:
    def __init__(self, bullets):
        self.calls, self.bullets = [], bullets
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        tips = [{"title": b.split("|")[0], "action": b.split("|")[1] if "|" in b else "Do this."} for b in self.bullets]
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps({"tips": tips}))],
                               stop_reason="end_turn", usage=SimpleNamespace(input_tokens=900, output_tokens=200))


NOW = datetime(2026, 10, 20, 9, 0)


def test_numbers_and_ratio_come_from_the_snapshots(env):
    snap(env, "2026-10-13T08-45-00", 371, 382, 2895, 700, views=513)
    snap(env, "2026-10-20T08-45-00", 399, 423, 3044, 768, views=531)
    a, b, d1, d0 = ws.pick_pair(NOW)
    data = ws.compute(a, b)
    rows = {(r["platform"], r["metric"]): r for r in data["rows"]}
    assert (d1, d0) == ("2026-10-20", "2026-10-13")
    assert rows[("SoundCloud", "Followers")]["delta"] == 28 and rows[("YouTube", "Views")]["delta"] == 18
    assert data["ratio"] == {"now": 0.94, "prev": 0.97}
    assert data["movers"][0]["title"] == "Farewell" and data["movers"][0]["plays_delta"] == 68
    t = ws.table(data)
    assert "| SoundCloud | Followers | 371 | 399 | +28 |" in t and "| followers : following | 0.97:1 | 0.94:1 | 1:1 | 1.4-1.6:1 |" in t


def test_write_puts_the_week_on_top_once_and_cleans_dashes(env):
    snap(env, "2026-10-06T08-45-00", 350, 370, 2700, 650)
    snap(env, "2026-10-13T08-45-00", 371, 382, 2895, 700)
    fake = Fake(["Farewell +68 plays \u2014 most of any track|Pin it as the Spotlight track.", "Followers +28|Keep going."])
    assert ws.write(datetime(2026, 10, 13, 9), client=fake) == "wrote week to 2026-10-13"
    snap(env, "2026-10-20T08-45-00", 399, 423, 3044, 768)
    assert ws.write(NOW, client=fake) == "wrote week to 2026-10-20"
    assert ws.write(NOW, client=fake) == "week to 2026-10-20 already written"
    text = (env / "weekly-stats.md").read_text()
    assert text.startswith("# Weekly stats") and text.index("## Week to 2026-10-20") < text.index("## Week to 2026-10-13")
    assert text.count("## Week to 2026-10-20") == 1 and "—" not in text
    assert "- **Farewell +68 plays, most of any track.** Pin it as the Spotlight track." in text
    assert len(fake.calls) == 2
    sent = fake.calls[0]["messages"][0]["content"]
    assert "NUMBERS (from the snapshots)" in sent and "Never tell him to post" in fake.calls[0]["system"]
    v = ws.latest_view()
    assert v["title"] == "Week to 2026-10-20 (vs 2026-10-13)" and len(v["bullets"]) == 2


def test_force_replaces_this_week_only(env):
    snap(env, "2026-10-13T08-45-00", 371, 382, 2895, 700)
    snap(env, "2026-10-20T08-45-00", 399, 423, 3044, 768)
    ws.write(NOW, client=Fake(["first"]))
    ws.write(NOW, force=True, client=Fake(["second"]))
    text = (env / "weekly-stats.md").read_text()
    assert text.count("## Week to 2026-10-20") == 1 and "**second.**" in text and "**first.**" not in text


def test_missing_week_is_said_and_no_model_call(env):
    snap(env, "2026-10-20T08-45-00", 399, 423, 3044, 768)
    fake = Fake(["x"])
    ws.write(NOW, client=fake)
    text = (env / "weekly-stats.md").read_text()
    assert "Missing: no snapshot from a week earlier to compare with" in text and fake.calls == []


def test_no_snapshots_at_all(env):
    key, sec = ws.section(NOW, client=Fake(["x"]))
    assert "Missing: no snapshot at all." in sec



def _no_spotify():
    pass


def test_spotify_rows_and_refresh_after_a_late_read(env):
    from stats import spotify_s4a
    from pathlib import Path
    fix = Path(__file__).parent / "fixtures"
    snap(env, "2026-10-13T08-45-00", 371, 382, 2895, 700)
    snap(env, "2026-10-20T08-45-00", 399, 423, 3044, 768)
    fake = Fake(["a|b"])
    ws.write(NOW, client=fake)
    assert "no Spotify for Artists read" in (env / "weekly-stats.md").read_text()
    spotify_s4a.save_week(spotify_s4a.parse_stats((fix / "s4a_audience_2026-10-12.txt").read_text()))
    spotify_s4a.save_week(spotify_s4a.parse_stats((fix / "s4a_audience_2026-10-19.txt").read_text()),
                          spotify_s4a.parse_home((fix / "s4a_home_2026-10-19.txt").read_text()))
    assert ws.refresh_if_spotify_missing(NOW, client=fake) == "wrote week to 2026-10-20"
    text = (env / "weekly-stats.md").read_text()
    assert "| Spotify | Streams (7 days) | 137 | 100 | -37 |" in text and "no Spotify for Artists read" not in text
    assert ws.refresh_if_spotify_missing(NOW, client=fake) == "week to 2026-10-20 already has Spotify"
    sent = json.loads(fake.calls[-1]["messages"][0]["content"].split("NUMBERS (from the snapshots):\n", 1)[1])
    assert {"where": "Spotify", "title": "Farewell", "streams_week": 28} in sent["movers"]
