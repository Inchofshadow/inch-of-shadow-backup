"""Clip pack (System 79, S10): schema defaults, the ranges of the spec, the never-twice rule,
load/save that keeps the rest of the release file, and the release page block + route."""
import json
from pathlib import Path

import pytest

from release_manager import clips, storage
from release_manager.models import new_release_dict, new_track_dict

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "clip-pack-release.json"


def fixture_release() -> dict:
    """A two-track release for these tests only (never a real file in releases/)."""
    rel = new_release_dict("Clip Pack Test", "Single", "2026-12-18", genre_primary="EBM")
    rel["slug"] = "clip-pack-test-single"
    rel["tracks"] = [
        new_track_dict(1, "Night Walk", bpm=118, duration="3:40"),
        new_track_dict(2, "Half Light", bpm=112, duration="4:05"),
    ]
    rel["notes"] = "keep me"
    rel["outcomes"] = {"stats": {"spotify_streams": 12}}
    return rel


def block(**over) -> dict:
    b = clips.default_track_clips(1)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(b.get(key), dict):
            b[key].update(val)
        else:
            b[key] = val
    return b


def used(**over) -> dict:
    u = {"platform": "instagram", "post": "https://www.instagram.com/reel/abc/", "date": "2026-11-20",
         "cut": "A1", "kind": "post"}
    u.update(over)
    return u


# --- fixture file -------------------------------------------------------------------------

def test_fixture_file_matches_the_schema():
    data = json.loads(FIXTURE.read_text())
    assert data["slug"] == "clip-pack-test-single"
    assert data["clips"]["version"] == clips.CLIPS_VERSION
    assert clips.validate_clips(data) == []
    assert [b["number"] for b in data["clips"]["tracks"]] == [1, 2]


# --- defaults and shape -------------------------------------------------------------------

def test_ensure_clips_adds_one_block_per_track_and_keeps_existing_values():
    rel = fixture_release()
    assert "clips" not in rel
    c = clips.ensure_clips(rel)
    assert c["version"] == clips.CLIPS_VERSION
    assert [b["number"] for b in c["tracks"]] == [1, 2]
    assert c["tracks"][0]["used_in"] == []
    rel["clips"]["tracks"][0]["tiktok"]["start"] = 72.0
    rel["tracks"].append(new_track_dict(3, "Third"))
    c = clips.ensure_clips(rel)
    assert c["tracks"][0]["tiktok"]["start"] == 72.0
    assert [b["number"] for b in c["tracks"]] == [1, 2, 3]
    assert set(c["tracks"][2]) == {"number", "tiktok", "hook_bar", "canvas", "shorts_preview", "used_in"}


def test_parse_seconds_accepts_seconds_and_minutes():
    assert clips.parse_seconds("72") == 72.0
    assert clips.parse_seconds("72.5") == 72.5
    assert clips.parse_seconds("1:12") == 72.0
    assert clips.parse_seconds("1:12.5") == 72.5
    assert clips.parse_seconds("") is None
    assert clips.parse_seconds(None) is None
    with pytest.raises(ValueError):
        clips.parse_seconds("1:72")
    with pytest.raises(ValueError):
        clips.parse_seconds("abc")
    with pytest.raises(ValueError):
        clips.parse_seconds("00:01:12")      # frames or hours are not the unit here


def test_fmt_seconds_round_trips():
    for v in (0.0, 5.0, 59.9, 72.5, 185.0):
        assert clips.parse_seconds(clips.fmt_seconds(v)) == v
    assert clips.fmt_seconds(None) == ""
    assert clips.fmt_seconds(72.5) == "1:12.5"


# --- validation: the ranges of the spec ---------------------------------------------------

def test_empty_block_is_valid():
    assert clips.validate_track_clips(clips.default_track_clips(1)) == []


def test_tiktok_start_must_be_inside_the_track():
    track = {"number": 1, "duration": "3:40"}
    assert clips.validate_track_clips(block(tiktok={"start": 72}), track) == []
    assert any("below" in e for e in clips.validate_track_clips(block(tiktok={"start": -1}), track))
    assert any("past the track end" in e for e in clips.validate_track_clips(block(tiktok={"start": 230}), track))


def test_hook_bar_sits_inside_the_tiktok_window():
    ok = block(tiktok={"start": 72}, hook_bar={"start": 72, "length": 3.5})
    assert clips.validate_track_clips(ok) == []
    before = block(tiktok={"start": 72}, hook_bar={"start": 70, "length": 3.5})
    assert any("inside the TikTok window" in e for e in clips.validate_track_clips(before))
    after = block(tiktok={"start": 72}, hook_bar={"start": 130, "length": 3.5})
    assert any("inside the TikTok window" in e for e in clips.validate_track_clips(after))
    half = block(hook_bar={"start": 72, "length": None})
    assert any("hook bar length: missing" in e for e in clips.validate_track_clips(half))
    too_long = block(hook_bar={"start": 0, "length": 61})
    assert any("hook bar length" in e and "above" in e for e in clips.validate_track_clips(too_long))


def test_hook_bar_without_a_tiktok_start_is_allowed():
    assert clips.validate_track_clips(block(hook_bar={"start": 10, "length": 4})) == []


def test_canvas_is_3_to_8_seconds_and_720_to_1080_px():
    assert clips.validate_track_clips(block(canvas={"length": 3})) == []
    assert clips.validate_track_clips(block(canvas={"length": 8, "height_px": 1080})) == []
    assert any("Canvas length" in e for e in clips.validate_track_clips(block(canvas={"length": 2.9})))
    assert any("Canvas length" in e for e in clips.validate_track_clips(block(canvas={"length": 8.1})))
    assert any("Canvas height" in e for e in clips.validate_track_clips(block(canvas={"length": 5, "height_px": 719})))
    assert any("Canvas height" in e for e in clips.validate_track_clips(block(canvas={"length": 5, "height_px": 1081})))


def test_shorts_preview_is_30_to_60_seconds_and_starts_before_release():
    good = block(shorts_preview={"start": 60, "duration": 45, "start_date": "2026-12-04"})
    assert clips.validate_track_clips(good, release_date="2026-12-18") == []
    short = block(shorts_preview={"start": 60, "duration": 20})
    assert any("Shorts Preview duration" in e for e in clips.validate_track_clips(short))
    late = block(shorts_preview={"start": 60, "duration": 45, "start_date": "2026-12-18"})
    assert any("before the release date" in e for e in clips.validate_track_clips(late, release_date="2026-12-18"))
    bad_date = block(shorts_preview={"start": 60, "duration": 45, "start_date": "18.12.2026"})
    assert any("YYYY-MM-DD" in e for e in clips.validate_track_clips(bad_date))


def test_validate_clips_prefixes_the_track_number():
    rel = fixture_release()
    clips.ensure_clips(rel)
    rel["clips"]["tracks"][1]["canvas"]["length"] = 12
    errs = clips.validate_clips(rel)
    assert errs and all(e.startswith("track 2:") for e in errs)


# --- used_in: never the same cut twice on one platform -----------------------------------

def test_add_used_in_refuses_the_same_cut_on_the_same_platform():
    rel = fixture_release()
    assert clips.add_used_in(rel, 1, used()) == []
    errs = clips.add_used_in(rel, 1, used(post="https://www.instagram.com/reel/xyz/", date="2026-11-22"))
    assert errs and "already uploaded to instagram" in errs[0]
    assert len(clips.track_clips(rel, 1)["used_in"]) == 1


def test_a_different_cut_or_platform_is_fine():
    rel = fixture_release()
    assert clips.add_used_in(rel, 1, used()) == []
    assert clips.add_used_in(rel, 1, used(cut="A2", post="https://www.instagram.com/reel/xyz/")) == []
    assert clips.add_used_in(rel, 1, used(platform="tiktok", post="7421")) == []
    assert clips.add_used_in(rel, 2, used()) == []          # another track, its own log
    assert len(clips.track_clips(rel, 1)["used_in"]) == 3


def test_repost_and_replace_audio_reuse_a_cut_without_tripping_the_rule():
    rel = fixture_release()
    assert clips.add_used_in(rel, 1, used()) == []
    assert clips.add_used_in(rel, 1, used(kind="repost", date="2026-12-01")) == []
    assert clips.add_used_in(rel, 1, used(kind="replace_audio", date="2026-12-02")) == []
    assert clips.add_used_in(rel, 1, used(kind="trial", date="2026-12-03")) != []


def test_used_in_rows_need_platform_cut_date_and_post():
    errs = clips.validate_used_in([], {"platform": "vimeo", "post": "", "date": "soon", "cut": "", "kind": "x"})
    joined = " | ".join(errs)
    for word in ("platform must be", "kind must be", "cut label", "YYYY-MM-DD", "post id or URL"):
        assert word in joined


def test_remove_used_in_by_index():
    rel = fixture_release()
    clips.add_used_in(rel, 1, used())
    clips.add_used_in(rel, 1, used(cut="A2"))
    assert clips.remove_used_in(rel, 1, 0) == []
    assert [u["cut"] for u in clips.track_clips(rel, 1)["used_in"]] == ["A2"]
    assert clips.remove_used_in(rel, 1, 5) != []
    assert clips.remove_used_in(rel, 9, 0) != []


# --- the edit form ------------------------------------------------------------------------

def test_update_from_form_in_seconds_and_minutes():
    rel = fixture_release()
    form = {"tiktok_start": "1:12", "hook_start": "72.5", "hook_length": "3.5", "canvas_length": "5",
            "canvas_source": "night-walk-loop.mp4", "canvas_height": "1080", "canvas_confirmed": "on",
            "preview_start": "", "preview_duration": "", "preview_start_date": ""}
    assert clips.update_track_clips(rel, 1, form) == []
    b = clips.track_clips(rel, 1)
    assert b["tiktok"]["start"] == 72.0
    assert b["hook_bar"] == {"start": 72.5, "length": 3.5}
    assert b["canvas"] == {"length": 5.0, "source": "night-walk-loop.mp4", "height_px": 1080, "confirmed": True}
    assert b["shorts_preview"] == {"start": None, "duration": None, "start_date": ""}
    assert clips.block_to_form(b)["tiktok_start"] == "1:12.0"


def test_update_from_form_rejects_and_leaves_the_block_untouched():
    rel = fixture_release()
    clips.update_track_clips(rel, 1, {"tiktok_start": "72", "hook_start": "72", "hook_length": "3"})
    errs = clips.update_track_clips(rel, 1, {"tiktok_start": "72", "hook_start": "10", "hook_length": "3"})
    assert errs and "inside the TikTok window" in errs[0]
    assert clips.track_clips(rel, 1)["hook_bar"]["start"] == 72.0
    errs = clips.update_track_clips(rel, 1, {"tiktok_start": "abc"})
    assert errs and "not a time" in errs[0]
    assert clips.update_track_clips(rel, 7, {}) == ["track 7: no such track"]


def test_summary_lines():
    b = block(tiktok={"start": 72}, hook_bar={"start": 72, "length": 3.5}, canvas={"length": 5})
    s = clips.summary(b, {"title": "Night Walk"})
    assert s["tiktok"] == "1:12.0 to 2:12.0 (Symphonic Clip Start Time 00:01:12)"
    assert s["hook_bar"] == "1:12.0 for 3.5 s (to 1:15.5)"
    assert s["canvas"] == "5 s loop, rules not confirmed yet"
    assert s["shorts_preview"].startswith("not set")


# --- load / save keep every other key -----------------------------------------------------

@pytest.fixture
def releases_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RELEASES_DIR", tmp_path)
    rel = fixture_release()
    (tmp_path / "clip-pack-test-single.json").write_text(json.dumps(rel, indent=2))
    return tmp_path


def test_save_clips_keeps_the_rest_of_the_file_and_backs_it_up(releases_dir):
    before = json.loads((releases_dir / "clip-pack-test-single.json").read_text())
    c = clips.load_clips("clip-pack-test-single")
    assert [b["number"] for b in c["tracks"]] == [1, 2]
    c["tracks"][0]["tiktok"]["start"] = 72.0
    c["tracks"][0]["used_in"].append(used())
    assert clips.save_clips("clip-pack-test-single", c) is not None
    after = json.loads((releases_dir / "clip-pack-test-single.json").read_text())
    assert after["clips"]["tracks"][0]["tiktok"]["start"] == 72.0
    assert after["clips"]["tracks"][0]["used_in"] == [used()]
    for key in before:
        if key not in ("clips", "updated_at"):
            assert after[key] == before[key], key
    backups = list(releases_dir.glob("clip-pack-test-single.bak.*_clips.json"))
    assert len(backups) == 1 and "clips" not in json.loads(backups[0].read_text())
    assert clips.save_clips("no-such-release", c) is None
    assert clips.load_clips("no-such-release") is None
    assert [p.name for p in storage.iter_release_paths()] == ["clip-pack-test-single.json"]


# --- the release page block and its route -------------------------------------------------

@pytest.fixture
def client(releases_dir):
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def _stored(releases_dir):
    return json.loads((releases_dir / "clip-pack-test-single.json").read_text())


def test_release_page_shows_the_clip_pack_block(client):
    html = client.get("/release/clip-pack-test-single").get_data(as_text=True)
    assert 'id="section-clips"' in html
    assert 'id="clips-1"' in html and 'id="clips-2"' in html
    assert "Night Walk" in html and "Half Light" in html
    assert 'name="tiktok_start"' in html and 'name="canvas_length"' in html
    assert "Symphonic" in html


def test_route_saves_seconds_and_redirects(client, releases_dir):
    r = client.post("/release/clip-pack-test-single/clips/1", data={
        "action": "save", "tiktok_start": "1:12", "hook_start": "1:12", "hook_length": "3.5",
        "canvas_length": "5", "canvas_confirmed": "on"})
    assert r.status_code == 302 and r.headers["Location"].endswith("/release/clip-pack-test-single#clips-1")
    t1 = _stored(releases_dir)["clips"]["tracks"][0]
    assert t1["tiktok"]["start"] == 72.0 and t1["hook_bar"]["length"] == 3.5 and t1["canvas"]["confirmed"] is True


def test_route_shows_errors_inline_and_saves_nothing(client, releases_dir):
    r = client.post("/release/clip-pack-test-single/clips/1", data={
        "action": "save", "tiktok_start": "1:12", "hook_start": "0:10", "hook_length": "3.5"})
    assert r.status_code == 400
    html = r.get_data(as_text=True)
    assert "inside the TikTok window" in html
    assert 'value="0:10"' in html             # the typed value stays in the form
    assert "clips" not in _stored(releases_dir)


def test_route_used_in_add_refuses_the_second_upload(client, releases_dir):
    row = {"action": "add_used", "platform": "tiktok", "post": "7421", "date": "2026-11-20", "cut": "A1", "kind": "post"}
    assert client.post("/release/clip-pack-test-single/clips/2", data=row).status_code == 302
    assert _stored(releases_dir)["clips"]["tracks"][1]["used_in"][0]["cut"] == "A1"
    r = client.post("/release/clip-pack-test-single/clips/2", data=dict(row, post="7422", date="2026-11-21"))
    assert r.status_code == 400 and "already uploaded to tiktok" in r.get_data(as_text=True)
    assert len(_stored(releases_dir)["clips"]["tracks"][1]["used_in"]) == 1
    r = client.post("/release/clip-pack-test-single/clips/2", data={"action": "remove_used", "index": "0"})
    assert r.status_code == 302 and _stored(releases_dir)["clips"]["tracks"][1]["used_in"] == []


def test_route_404_and_400(client):
    assert client.post("/release/no-such/clips/1", data={"action": "save"}).status_code == 404
    assert client.post("/release/clip-pack-test-single/clips/9", data={"action": "save"}).status_code == 404
    assert client.post("/release/clip-pack-test-single/clips/1", data={"action": "nope"}).status_code == 400
    assert client.post("/release/clip-pack-test-single/clips/1", data={"action": "remove_used", "index": "x"}).status_code == 400
