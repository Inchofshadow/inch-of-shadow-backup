"""Studio: the Video page lists the HyperFrames projects and guards the starter (Machine-12)."""
from release_manager.webapp import app, VIDEOS_DIR


def test_video_page_lists_projects_and_rejects_bad_names():
    c = app.test_client()
    html = c.get("/video").get_data(as_text=True)
    assert "Start a project" in html
    if VIDEOS_DIR.is_dir():
        assert "ios-sting" in html and "_kit-test" not in html
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        assert c.post("/video/start", data={"name": "../evil", "mood": "M2", "canvas": "reel"}).status_code == 400
        assert c.post("/video/start", data={"name": "ok-name", "mood": "M2", "canvas": "poster"}).status_code == 400
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
    assert c.get("/video/render/ios-sting/../x.mp4").status_code == 404
