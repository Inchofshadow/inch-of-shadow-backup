"""Release checklist: the fixed format set per single (board ticket Formats-01, 2026-09-20).

LIGHT lane = electronic drops, FULL lane = songs (light + five more). Releases made
before the lane existed carry no lane and must stay exactly as they were.
"""
from release_manager.checklist import (
    BANDCAMP_CHECKLIST, DEFAULT_CHECKLIST, FORMAT_CHECKLIST, YOUTUBE_CHECKLIST, CHECKLIST_TOOLTIPS,
    expected_ids, generate_checklist, migrate_checklist,
)

TL = [{"id": "release_day", "date": "2026-11-06"}]
LIGHT = {"fmt_cover", "fmt_canvas", "fmt_process_reel", "fmt_release_reel_hooks",
         "fmt_shorts", "fmt_story_set"}
YT = {"yt_render", "yt_uploaded", "yt_metadata", "yt_thumbnail", "yt_premiere",
      "yt_end_screen", "yt_channel_day", "yt_shorts_link"}   # Machine-03: every lane release gets these
FULL_ONLY = {"fmt_reveal_carousel", "fmt_face_reel", "fmt_lyric_reel",
             "fmt_youtube_visualizer", "fmt_presave_asset"}
BC = {"bandcamp_campaign_links"}   # BC-04: every lane release links Bandcamp with campaign links


def ids(items):
    return {i["id"] for i in items}


def test_format_set_matches_the_decision():
    assert {i["id"] for i in FORMAT_CHECKLIST if i["lane"] == "light"} == LIGHT
    assert {i["id"] for i in FORMAT_CHECKLIST if i["lane"] == "full"} == FULL_ONLY
    for i in FORMAT_CHECKLIST:
        assert i["category"] == "formats"
        assert i["id"] in CHECKLIST_TOOLTIPS


def test_no_lane_means_no_format_items():
    base = ids(DEFAULT_CHECKLIST)
    assert ids(generate_checklist(TL)) == base
    assert expected_ids(None) == base


def test_light_lane_gets_six_full_lane_gets_eleven():
    base = ids(DEFAULT_CHECKLIST)
    assert ids(generate_checklist(TL, lane="light")) == base | LIGHT | YT | BC
    assert ids(generate_checklist(TL, lane="full")) == base | LIGHT | YT | FULL_ONLY | BC
    assert expected_ids("light") == base | LIGHT | YT | BC


def test_migrate_adds_format_items_and_keeps_done_state():
    old = generate_checklist(TL)
    old[0]["done"] = True
    old[0]["done_date"] = "2026-09-14"
    new = migrate_checklist(old, TL, lane="light")
    assert ids(new) == ids(DEFAULT_CHECKLIST) | LIGHT | YT | BC
    assert new[0]["done"] is True and new[0]["done_date"] == "2026-09-14"
    assert all(i["done"] is False for i in new if i["id"] in LIGHT)


def test_migrate_without_lane_leaves_old_releases_alone():
    old = generate_checklist(TL)
    assert ids(migrate_checklist(old, TL)) == ids(DEFAULT_CHECKLIST)


def test_youtube_steps_match_the_hook_tool():
    """The Release Manager and youtube/tools/yt_release.py must list the same steps, same order."""
    import importlib.util, pathlib
    path = pathlib.Path(__file__).resolve().parents[2] / "youtube" / "tools" / "yt_release.py"
    if not path.is_file():
        import pytest; pytest.skip("youtube folder not present")
    spec = importlib.util.spec_from_file_location("yt_release", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert [s[0] for s in mod.STEPS] == [i["id"] for i in YOUTUBE_CHECKLIST]
    assert {i["id"] for i in YOUTUBE_CHECKLIST} == YT
    assert all(i["id"] in CHECKLIST_TOOLTIPS for i in YOUTUBE_CHECKLIST)


def test_youtube_draft_follows_the_copy_rules():
    import importlib.util, json, pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    path = root.parent / "youtube" / "tools" / "yt_release.py"
    if not path.is_file():
        import pytest; pytest.skip("youtube folder not present")
    spec = importlib.util.spec_from_file_location("yt_release", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    rel = {"slug": "x-single", "release_date": "2026-11-06", "lane": "light", "platform_links": {},
           "metadata": {"artist": "Inch of Shadow", "title": "X", "release_type": "Single",
                        "genre_primary": "Acid", "genre_secondary": "Italo Disco",
                        "copyright": "2026 Indigo Children Records"},
           "tracks": [{"title": "X", "artist": "Inch of Shadow", "bpm": 126.0,
                       "genre_primary": "Acid", "genre_secondary": "House"}]}
    text = mod.draft_text(rel, json.loads((root / "artist_profile.json").read_text()), rel["tracks"][0])
    assert "PUBLISH: 2026-11-06 Fri 18:00" in text and "PREMIERE: yes" in text
    assert "Inch of Shadow - X (Official Audio)" in text
    assert "Mixed and mastered by Inch of Shadow at Ambertone Studios." in text
    assert "Released on Indigo Children Records." in text
    assert "[TODO" in text                         # a draft can never be applied as it is
    assert "\u2014" not in text and " -- " not in text
    assert text.split("===== TAGS (copy) =====")[1].strip().startswith("inch of shadow")


def test_bandcamp_item_has_tooltip_and_skips_finished_releases():
    assert {i["id"] for i in BANDCAMP_CHECKLIST} == BC
    assert all(i["id"] in CHECKLIST_TOOLTIPS for i in BANDCAMP_CHECKLIST)
    assert not BC & expected_ids(None)   # Farewell / The Deceiver carry no lane


def test_migrate_keeps_done_or_noted_items_that_left_the_template():
    old = generate_checklist(TL)
    old.append({"id": "gone_done", "category": "promotion", "label": "Old step", "done": True,
                "done_date": "2026-08-01", "due_date": "", "notes": ""})
    old.append({"id": "gone_noted", "category": "promotion", "label": "Old step 2", "done": False,
                "done_date": "", "due_date": "", "notes": "asked label"})
    old.append({"id": "gone_empty", "category": "promotion", "label": "Old step 3", "done": False,
                "done_date": "", "due_date": "", "notes": ""})
    new = migrate_checklist(old, TL, lane="light")
    got = {i["id"]: i for i in new}
    assert got["gone_done"]["done"] is True and got["gone_done"]["done_date"] == "2026-08-01"
    assert got["gone_noted"]["notes"] == "asked label"
    assert "gone_empty" not in got
