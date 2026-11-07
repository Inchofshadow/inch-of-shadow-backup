"""The photo editor page: opens for shoot photos and artwork, saves only NEW files, never the original."""
import json

import release_manager.views.shoot as shoot_view   # the /edit routes read EDITS_DIR from here (RM 2.0 slice 6)
import release_manager.webapp as w
from release_manager.webapp import app


def test_editor_opens_for_artwork_and_refuses_unknown_sources():
    c = app.test_client()
    art = next(p.name for p in sorted(w.ARTWORK_DIR.iterdir()) if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    assert c.get("/edit", query_string={"src": f"artwork:{art}"}).status_code == 200
    assert c.get("/edit", query_string={"src": "artwork:../artist_profile.json"}).status_code == 404
    assert c.get("/edit", query_string={"src": "nope:x"}).status_code == 404
    assert c.get("/edit/preview", query_string={"src": f"artwork:{art}"}).status_code == 200


def test_save_writes_a_new_copy_and_leaves_the_original(tmp_path, monkeypatch):
    art = next(p for p in sorted(w.ARTWORK_DIR.iterdir()) if p.suffix.lower() in (".jpg", ".jpeg"))
    before = art.stat().st_mtime, art.stat().st_size
    monkeypatch.setattr(shoot_view, "EDITS_DIR", tmp_path)
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        r = app.test_client().post("/edit/save", json={"src": f"artwork:{art.name}",
                                                        "params": {"crop": {"x": .1, "y": .1, "w": .5, "h": .5}, "exposure": .3}})
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
    j = r.get_json()
    assert j["ok"] and (tmp_path / j["file"]).is_file() and (tmp_path / (j["file"][:-4] + ".json")).is_file()
    assert json.loads((tmp_path / (j["file"][:-4] + ".json")).read_text())["params"]["exposure"] == .3
    assert (art.stat().st_mtime, art.stat().st_size) == before


def test_shoot_photo_page_links_the_editor():
    cat = json.loads(w.SHOOT_CATALOGUE.read_text())
    html = app.test_client().get(f"/shoot/{cat['photos'][0]['id']}").get_data(as_text=True)
    assert "/edit?src=shoot" in html and "Edit a copy" in html


def test_a_platform_tag_names_the_file_and_the_copy_is_listed(tmp_path, monkeypatch):
    art = next(p for p in sorted(w.ARTWORK_DIR.iterdir()) if p.suffix.lower() in (".jpg", ".jpeg"))
    monkeypatch.setattr(shoot_view, "EDITS_DIR", tmp_path)
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        c = app.test_client()
        j = c.post("/edit/save", json={"src": f"artwork:{art.name}", "params": {}, "tag": "ig-reel"}).get_json()
        html = c.get("/edit", query_string={"src": f"artwork:{art.name}"}).get_data(as_text=True)
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
    assert "_ig-reel_edit_" in j["file"]
    assert j["file"] in html and "IG Reel / Story" in html and "Copies of this picture" in html


def test_delete_moves_a_copy_and_its_record_to_the_trash_only_inside_edits(tmp_path, monkeypatch):
    edits, home = tmp_path / "edits", tmp_path / "home"
    edits.mkdir(); (home / ".Trash").mkdir(parents=True)
    (edits / "x_edit_1.jpg").write_bytes(b"jpg"); (edits / "x_edit_1.json").write_text("{}")
    monkeypatch.setattr(shoot_view, "EDITS_DIR", edits)
    monkeypatch.setenv("HOME", str(home))
    app.config["WTF_CSRF_ENABLED"] = False
    try:
        c = app.test_client()
        assert c.post("/edit/delete", json={"file": "../x_edit_1.jpg"}).get_json()["ok"] is True   # name only: stays inside edits
        assert not (edits / "x_edit_1.jpg").exists() and (home / ".Trash" / "x_edit_1.jpg").exists()
        assert (home / ".Trash" / "x_edit_1.json").exists()
        assert c.post("/edit/delete", json={"file": "nope.jpg"}).status_code == 404
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
