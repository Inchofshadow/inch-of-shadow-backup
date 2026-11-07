"""The resizer pages after the 2026-09-27 redesign: sets, cover mode, readable labels, kept ticks."""
from release_manager.webapp import app, ARTWORK_PRESETS, VIDEO_PRESETS


def test_both_pages_render_with_sets_and_the_preview_stage():
    c = app.test_client()
    art = c.get("/artwork-resizer").get_data(as_text=True)
    vid = c.get("/video-resizer").get_data(as_text=True)
    for html, presets in ((art, ARTWORK_PRESETS), (vid, VIDEO_PRESETS)):
        assert 'id="rz-stage"' in html and "resizer.js" in html
        for p in presets:
            assert p["label"] in html
    assert 'name="cover_mode"' in art
    assert "Video 1440p" in vid and "video_youtube_1440<" not in vid


def test_presets_only_name_real_sizes():
    from artwork_resizer import EXPORTS
    from video_resizer import VIDEO_EXPORTS
    art_ids = {e[0] for e in EXPORTS}
    vid_ids = {e[0] for e in VIDEO_EXPORTS}
    for p in ARTWORK_PRESETS:
        assert set(p["templates"]) <= art_ids | {"*"}, p["key"]
    for p in VIDEO_PRESETS:
        assert set(p["templates"]) <= vid_ids | {"*"}, p["key"]


def test_a_post_without_a_source_keeps_the_ticked_sizes():
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        html = app.test_client().post("/artwork-resizer", data={"templates": ["social_instagram_post"], "cover_mode": "1"}).get_data(as_text=True)
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
    assert 'value="social_instagram_post" data-group="Instagram" checked' in html
    assert 'id="rz-cover" checked' in html


def test_source_video_route_refuses_paths_outside_the_folder():
    assert app.test_client().get("/video-resizer/source/..%2Fartist_profile.json").status_code == 404


def test_video_page_has_frame_by_hand_and_the_route_checks_frames():
    from release_manager.webapp import _video_frames
    html = app.test_client().get("/video-resizer").get_data(as_text=True)
    assert 'id="rz-frames"' in html and 'data-shape="9:16"' in html and 'name="frames"' in html
    assert _video_frames('{"9:16": {"cx": 0.2, "cy": 0.5, "z": 0.7}, "7:3": {"cx": 0.5}}') == {"9:16": {"cx": 0.2, "cy": 0.5, "z": 0.7}}
    assert _video_frames("not json") == {} and _video_frames("[1]") == {} and _video_frames("") == {}
