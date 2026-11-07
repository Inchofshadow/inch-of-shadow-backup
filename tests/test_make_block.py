"""The Make block: per object of the fixed set, made or not from the files on disk (Machine-13)."""
import release_manager.views.release as release_view   # _make_block lives here since RM 2.0 slice 7
from release_manager.webapp import _make_block


def test_no_lane_no_block():
    assert _make_block({"slug": "x", "metadata": {"title": "X"}}) == []


def test_light_lane_lists_six_and_finds_files(tmp_path, monkeypatch):
    monkeypatch.setattr(release_view, "PROJECT_ROOT", tmp_path / "code")
    (tmp_path / "code" / "resized_video").mkdir(parents=True)
    (tmp_path / "code" / "resized_video" / "canvas_vertical_spotify_the-deceiver_canvas.mp4").write_bytes(b"x")
    rows = _make_block({"slug": "the-deceiver-single", "lane": "light", "metadata": {"title": "The Deceiver"}})
    assert [r["id"] for r in rows] == ["fmt_cover", "fmt_canvas", "fmt_process_reel", "fmt_release_reel_hooks", "fmt_shorts", "fmt_story_set"]
    by = {r["id"]: r for r in rows}
    assert by["fmt_canvas"]["made"] and by["fmt_canvas"]["files"] == ["code/resized_video/canvas_vertical_spotify_the-deceiver_canvas.mp4"]
    assert not by["fmt_cover"]["made"] and "artwork_resizer.py" in by["fmt_cover"]["how"]
    assert len(_make_block({"slug": "s", "lane": "full", "metadata": {"title": "Song"}})) == 11


def test_release_page_renders_with_the_block():
    from release_manager.webapp import app, list_releases
    slugs = [r["slug"] for r in list_releases()]
    if not slugs:
        return
    for slug in slugs:
        assert app.test_client().get(f"/release/{slug}").status_code == 200
