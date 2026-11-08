"""Artwork playground (Machine-21): the base must sit inside artwork/, looks render and cache,
unknown looks and slugs are refused, the page answers."""
from pathlib import Path

import pytest

from release_manager import playground as pg

ROOT = Path(__file__).resolve().parent.parent


def test_base_path_stays_inside_artwork(tmp_path):
    (tmp_path / "artwork").mkdir()
    (tmp_path / "artwork" / "a.png").write_bytes(b"x")
    (tmp_path / "secret.png").write_bytes(b"x")
    ok = {"brand": {"playground": {"base": "artwork/a.png"}}}
    bad = {"brand": {"playground": {"base": "artwork/../secret.png"}}}
    assert pg.base_path(tmp_path, ok) is not None
    assert pg.base_path(tmp_path, bad) is None
    assert pg.base_path(tmp_path, {}) is None


def test_unknown_look_is_refused(tmp_path):
    from PIL import Image
    p = tmp_path / "b.png"; Image.new("RGB", (40, 40), (200, 200, 200)).save(p)
    with pytest.raises(ValueError):
        pg.look_image(p, "nope")
    assert pg.look_image(p, "dither").is_file()


@pytest.fixture
def client():
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_pages_answer(client):
    assert client.get("/playground/pinocchio-single").status_code == 200
    assert client.get("/playground/pinocchio-single/image").status_code == 200
    assert client.get("/playground/pinocchio-single/image?look=xerox").status_code == 200
    assert client.get("/playground/pinocchio-single/image?look=nope").status_code == 404
    assert client.get("/playground/no-such").status_code == 404
    assert client.get("/playground/..%2Fx").status_code == 404
    assert client.get("/playground").status_code in (200, 302)


def test_look_scale_is_clamped_and_cached_apart(tmp_path):
    from PIL import Image
    p = tmp_path / "b.png"; Image.new("RGB", (80, 80), (120, 120, 120)).save(p)
    a = pg.look_image(p, "pixel", 1); b = pg.look_image(p, "pixel", 3); c = pg.look_image(p, "pixel", 99)
    assert a != b and c.name.endswith("-4.png")
    assert Image.open(b).size == (80, 80)


def test_versions_save_overwrite_delete():
    rel = {"brand": {"playground": {"base": "artwork/x.png"}}}
    pg.save_version(rel, "first", {"a": 1}, "2026-10-14 10:00")
    pg.save_version(rel, "first", {"a": 2}, "2026-10-14 10:05")
    pg.save_version(rel, "second", {"a": 3}, "2026-10-14 10:06")
    assert [v["name"] for v in pg.versions(rel)] == ["first", "second"]
    assert pg.versions(rel)[0]["state"] == {"a": 2}
    with pytest.raises(ValueError):
        pg.save_version(rel, "  ", {}, "t")
    with pytest.raises(ValueError):
        pg.save_version(rel, "big", {"x": "y" * 70000}, "t")
    assert pg.delete_version(rel, "first") and not pg.delete_version(rel, "nope")
    assert rel["brand"]["playground"]["base"] == "artwork/x.png"


def test_accent_layer_stays_inside_artwork_and_versions_change(tmp_path):
    (tmp_path / "artwork").mkdir()
    (tmp_path / "artwork" / "l.png").write_bytes(b"x")
    (tmp_path / "secret.png").write_bytes(b"x")
    ok = {"brand": {"playground": {"base": "artwork/l.png", "accent_layer": "artwork/l.png"}}}
    bad = {"brand": {"playground": {"accent_layer": "artwork/../secret.png"}}}
    p = pg.accent_layer_path(tmp_path, ok)
    assert p is not None and pg.accent_layer_path(tmp_path, bad) is None
    assert pg.accent_layer_path(tmp_path, {"brand": {"playground": {"base": "artwork/l.png"}}}) is None
    assert pg.file_version(p).isdigit() and pg.file_version(None) == ""


def test_covers_by_name_only_inside_artwork(tmp_path):
    from PIL import Image
    d = tmp_path / "artwork" / "edits" / "x" / "playground-covers" / "my-rel"
    d.mkdir(parents=True)
    Image.new("RGB", (8, 8)).save(d / "a-cover.jpg")
    (d / "notes.txt").write_text("x")
    (tmp_path / "secret.jpg").write_bytes(b"x")
    names = [c["name"] for c in pg.covers(tmp_path, "my-rel")]
    assert names == ["a-cover.jpg"]
    assert pg.cover_path(tmp_path, "my-rel", "a-cover.jpg") is not None
    assert pg.cover_path(tmp_path, "my-rel", "../../../../secret.jpg") is None
    assert pg.cover_path(tmp_path, "my-rel", "notes.txt") is None
    assert pg.cover_path(tmp_path, "other", "a-cover.jpg") is None
    assert pg.covers(tmp_path, "../x") == []


def test_cover_image_route(client):
    cs = pg.covers(ROOT, "pinocchio-single")
    if not cs:
        pytest.skip("no covers on this machine")
    name = cs[0]["name"]
    assert client.get("/playground/pinocchio-single/image?cover=" + name).status_code == 200
    assert client.get("/playground/pinocchio-single/image?cover=" + name + "&look=xerox").status_code == 200
    assert client.get("/playground/pinocchio-single/image?cover=..%2Fx.jpg").status_code == 404
    page = client.get("/playground/pinocchio-single").get_data(as_text=True)
    assert 'id="pg-cover"' in page and 'id="pg-look2"' in page and 'id="pg-ramp-mode"' in page


def test_wall_page_and_kept(client, tmp_path, monkeypatch):
    assert client.get("/playground/pinocchio-single/wall").status_code == 200
    assert client.get("/playground/no-such/wall").status_code == 404
    monkeypatch.setattr(pg, "wall_file", lambda root, slug: tmp_path / f"{slug}.json")
    r = client.post("/api/playground/pinocchio-single/wall-kept", json={"cover": "", "look": "xerox", "wet": 40, "palette": "shares"})
    assert r.status_code == 200 and r.get_json()["kept"][0]["wet"] == 40
    r = client.post("/api/playground/pinocchio-single/wall-kept", json={"cover": "", "look": "xerox", "wet": 40})
    assert r.get_json()["kept"] == []
    assert client.post("/api/playground/pinocchio-single/wall-kept", json={"cover": "../x", "look": "xerox"}).status_code == 400
    assert client.post("/api/playground/pinocchio-single/wall-kept", json={"look": "x;y"}).status_code == 400


def test_small_tiles_and_overlay(client):
    assert client.get("/playground/pinocchio-single/image?w=200").mimetype == "image/jpeg"
    assert client.get("/playground/pinocchio-single/image?look=xerox&w=200").status_code == 200
    names = [c["name"] for c in pg.covers(ROOT, "pinocchio-single")]
    assert not any(".title." in n for n in names)
    if names:
        assert client.get("/playground/pinocchio-single/overlay?cover=" + names[0]).status_code in (200, 404)
    assert client.get("/playground/pinocchio-single/overlay?cover=..%2Fx").status_code == 404


def test_element_builder_names_and_kept(tmp_path):
    d = tmp_path / "artwork" / "x" / "playground-elements" / "my-rel"
    d.mkdir(parents=True)
    (d / "el-red-on-few-keep-2.jpg").write_bytes(b"x")
    assert pg.element_path(tmp_path, "my-rel", "el-red-on-few-keep-2.jpg") is not None
    assert pg.element_path(tmp_path, "my-rel", "el-owl-few-keep-2.jpg") is None
    assert pg.element_path(tmp_path, "my-rel", "../el-red-on-few-keep-2.jpg") is None
    assert pg.elements_toggle(tmp_path, "my-rel", "el-red-on-few-keep-2.jpg", "now")[0]["name"] == "el-red-on-few-keep-2.jpg"
    assert pg.elements_toggle(tmp_path, "my-rel", "el-red-on-few-keep-2.jpg", "now") == []
    import pytest
    with pytest.raises(ValueError):
        pg.elements_toggle(tmp_path, "my-rel", "el.title.png", "now")


def test_element_pages(client):
    assert client.get("/playground/pinocchio-single/elements").status_code == 200
    assert client.get("/playground/pinocchio-single/elements/img?n=el-cream-none-none-keep-0.jpg&w=480").status_code == 200
    assert client.get("/playground/pinocchio-single/elements/img?n=..%2Fx.jpg").status_code == 404


def test_colour_stage(tmp_path, client):
    import pytest
    assert pg.colours_toggle(tmp_path, "my-rel", {"pick": "el-red-on-few-remove-3", "cols": {"hill": "purple"}}, "now")[0]["cols"] == {"hill": "purple"}
    assert pg.colours_toggle(tmp_path, "my-rel", {"pick": "el-red-on-few-remove-3", "cols": {"hill": "purple"}}, "now") == []
    for bad in ({"pick": "../x", "cols": {}}, {"pick": "el-red-on-few-remove-3", "cols": {"sky": "red"}}, {"pick": "el-red-on-few-remove-3", "cols": {"hill": "<b>"}}):
        with pytest.raises(ValueError):
            pg.colours_toggle(tmp_path, "my-rel", bad, "now")
    assert pg.colour_path(tmp_path, "my-rel", "el-red-on-few-remove-3", "../../x") is None
    if pg.colour_picks(pg.Path(__file__).resolve().parents[1], "pinocchio-single"):
        assert client.get("/playground/pinocchio-single/colours").status_code == 200
        p = pg.colour_picks(pg.Path(__file__).resolve().parents[1], "pinocchio-single")[0]
        assert client.get("/playground/pinocchio-single/colours/file?p=" + p + "&f=hill.png").status_code == 200
        assert client.get("/playground/pinocchio-single/colours/file?p=" + p + "&f=secret.txt").status_code == 404


def test_wall_hidden(tmp_path):
    import pytest
    assert pg.wall_hide_toggle(tmp_path, "my-rel", "xerox") == ["xerox"]
    assert pg.wall_hide_toggle(tmp_path, "my-rel", "xerox") == []
    with pytest.raises(ValueError):
        pg.wall_hide_toggle(tmp_path, "my-rel", "<x>")


def test_layouts_toggle_keeps_and_unkeeps(tmp_path):
    from release_manager import playground as pg
    item = {"save": 1, "lines": 3, "x": 0.465, "y": 0.245, "size": 0.105, "lead": 0.18, "track": 0, "nsize": 0.034,
            "mdx": 0, "mdy": 0, "ms": 1, "font": "futura", "align": "left", "color": "cream", "npos": "under",
            "name": True, "owl": True, "stars": False,
            "line": 2, "ntrack": 0.12, "nfont": "marcellus", "ncolor": "cream", "tree": "remove", "starset": "0,0,1;0.02,-0.1,0", "flip": False,
            "nt": True, "ntf": False, "ntx": 0.6, "nty": 0.62, "nts": 0.42, "ntr": "left", "cols": "hill=purple;moon=cream", "fx": "thermal", "fxw": 40, "os": 1.2, "fxmix": "thermal:40;xerox:20:trees"}
    kept = pg.layouts_toggle(tmp_path, "pinocchio-single", item, "2026-11-05 19:00")
    assert len(kept) == 1 and kept[0]["font"] == "futura" and kept[0]["saved"] == "2026-11-05 19:00"
    assert pg.layouts_toggle(tmp_path, "pinocchio-single", item, "x") == []
    import pytest
    for bad in ({**item, "font": "../x"}, {**item, "size": 9}, {**item, "align": "middle"}, {**item, "save": "1"}, {**item, "starset": "<script>"}, {**item, "tree": "x"}):
        with pytest.raises(ValueError):
            pg.layouts_toggle(tmp_path, "pinocchio-single", bad, "x")
    assert pg.layout_font_path(tmp_path, "../../etc/passwd") is None


def test_extra_path_only_named_trees(tmp_path):
    from release_manager import playground as pg
    d = tmp_path / "artwork" / "x" / "playground-extras" / "pinocchio-single"
    d.mkdir(parents=True)
    (d / "tree1.png").write_bytes(b"x")
    (d / "secret.txt").write_bytes(b"x")
    assert pg.extra_path(tmp_path, "pinocchio-single", "tree1.png") is not None
    assert pg.extra_path(tmp_path, "pinocchio-single", "secret.txt") is None
    assert pg.extra_path(tmp_path, "pinocchio-single", "../tree1.png") is None


def test_fonts_hide_toggle(tmp_path):
    from release_manager import playground as pg
    assert pg.fonts_hide_toggle(tmp_path, "pinocchio-single", "nmarcellus") == ["nmarcellus"]
    assert pg.fonts_hide_toggle(tmp_path, "pinocchio-single", "tfutura") == ["nmarcellus", "tfutura"]
    assert pg.fonts_hide_toggle(tmp_path, "pinocchio-single", "nmarcellus") == ["tfutura"]
    import pytest
    for bad in ("../x", "xfutura", "", "n" + "a" * 40):
        with pytest.raises(ValueError):
            pg.fonts_hide_toggle(tmp_path, "pinocchio-single", bad)


def test_look_on_bytes_rejects_junk():
    from release_manager import playground as pg
    import pytest
    for bad in (b"", b"not an image", b"x" * 7_000_000):
        with pytest.raises(ValueError):
            pg.look_on_bytes(bad, "thermal")


def test_layout_snap_route_writes_only_into_its_root(client, tmp_path, monkeypatch):
    """POST /playground/<slug>/layout/snap (cover chat, 11-06): the picks page snap. The route reads the
    globals of views/playground.py, so PROJECT_ROOT and load_release are patched there: tmp dir only."""
    from io import BytesIO
    from PIL import Image
    import release_manager.views.playground as vp
    monkeypatch.setattr(vp, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(vp, "load_release", lambda slug: {"slug": slug} if slug == "my-rel" else None)
    buf = BytesIO(); Image.new("RGB", (40, 40), (10, 20, 30)).save(buf, "PNG")
    r = client.post("/playground/my-rel/layout/snap?n=3", data=buf.getvalue())
    assert r.status_code == 200 and r.get_json() == {"ok": True}
    d = tmp_path / "artwork" / "edits" / "htn-noir" / "layout-snaps" / "my-rel"
    assert (d / "keep-03.jpg").is_file()
    assert client.post("/playground/my-rel/layout/snap?n=0", data=buf.getvalue()).status_code == 200
    assert (d / "current.jpg").is_file()
    assert client.post("/playground/my-rel/layout/snap?n=3", data=b"not an image").status_code == 400
    assert client.post("/playground/my-rel/layout/snap?n=5000", data=buf.getvalue()).status_code == 400
    assert client.post("/playground/no-such/layout/snap?n=3", data=buf.getvalue()).status_code == 404
    assert sorted(p.name for p in d.iterdir()) == ["current.jpg", "keep-03.jpg"]


def test_barlowc_layout_font_is_served(client, tmp_path, monkeypatch):
    """The barlowc key (cover chat, 11-06): whitelisted in LAYOUT_FONT_FILES, offered by the layout
    page, served by /playground/<slug>/layout/font?f=barlowc. Fake font file in a tmp root."""
    import release_manager.views.playground as vp
    assert pg.LAYOUT_FONT_FILES["barlowc"] == "docs/brand/fonts/free/BarlowCondensed-ExtraBold.ttf"
    assert "LF('barlowc')" in (ROOT / "release_manager" / "templates" / "playground_layout.html").read_text()
    f = tmp_path / "docs" / "brand" / "fonts" / "free" / "BarlowCondensed-ExtraBold.ttf"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"fake-ttf")
    assert pg.layout_font_path(tmp_path, "barlowc") == f.resolve()
    monkeypatch.setattr(vp, "PROJECT_ROOT", tmp_path)
    r = client.get("/playground/pinocchio-single/layout/font?f=barlowc")
    assert r.status_code == 200 and r.mimetype == "font/ttf" and r.get_data() == b"fake-ttf"
    assert client.get("/playground/pinocchio-single/layout/font?f=barlow").status_code == 404


def test_layouts_toggle_refuses_when_full_and_keeps_old(tmp_path, monkeypatch):
    import pytest
    from release_manager import playground as pg
    item = {"save": 1, "lines": 3, "x": 0.465, "y": 0.245, "size": 0.105, "lead": 0.18, "track": 0, "nsize": 0.034,
            "mdx": 0, "mdy": 0, "ms": 1, "font": "futura", "align": "left", "color": "cream", "npos": "under",
            "name": True, "owl": True, "stars": False,
            "line": 2, "ntrack": 0.12, "nfont": "marcellus", "ncolor": "cream", "tree": "remove", "starset": "", "flip": False,
            "nt": True, "ntf": False, "ntx": 0.6, "nty": 0.62, "nts": 0.42, "ntr": "left", "cols": "", "fx": "", "fxw": 40, "os": 1.2, "fxmix": ""}
    monkeypatch.setattr(pg, "LAYOUTS_MAX", 2)
    pg.layouts_toggle(tmp_path, "pinocchio-single", {**item, "x": 0.1}, "a")
    pg.layouts_toggle(tmp_path, "pinocchio-single", {**item, "x": 0.2}, "b")
    with pytest.raises(ValueError):
        pg.layouts_toggle(tmp_path, "pinocchio-single", {**item, "x": 0.3}, "c")
    kept = pg.layouts_kept(tmp_path, "pinocchio-single")
    assert [k["x"] for k in kept] == [0.1, 0.2]
    # un-keeping still works when full
    assert [k["x"] for k in pg.layouts_toggle(tmp_path, "pinocchio-single", {**item, "x": 0.1}, "d")] == [0.2]
