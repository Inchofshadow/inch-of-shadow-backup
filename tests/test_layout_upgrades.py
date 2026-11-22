"""Layout page upgrades for the next cover (System 92, 93, 94, 97; 2026-11-10).
97: fixed keep IDs (Half the Night's 50 keeps keep their numbers and order), a picture per keep,
the picks page with V ticks, the Export route."""
import json
import shutil
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from release_manager import playground as pg

ROOT = Path(__file__).resolve().parent.parent
HTN = ROOT / "plans" / "playground-wall" / "pinocchio-single-layouts.json"
LAYOUT = {"save": 0, "lines": 3, "x": 0.4, "y": 0.3, "size": 0.08, "lead": 0.18, "track": 0.0, "nsize": 0.04, "mdx": 0.0,
          "mdy": 0.0, "ms": 1.0, "line": 2, "ntrack": 0.06, "ntx": 0.3, "nty": 0.6, "nts": 0.4, "fxw": 0, "os": 1.0,
          "font": "futura", "align": "left", "color": "cream", "npos": "under", "nfont": "pirata", "ncolor": "cream",
          "tree": "remove", "starset": "", "ntr": "none", "cols": "", "fx": "", "fxmix": "", "name": True, "owl": True,
          "stars": True, "flip": False, "nt": False, "ntf": False}


def jpeg(px, colour=(40, 30, 60)):
    b = BytesIO()
    Image.new("RGB", (px, px), colour).save(b, "JPEG")
    return b.getvalue()


def test_ids_fill_in_list_order_and_never_come_back(tmp_path):
    for x in (0.1, 0.2, 0.3):
        pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, x=x), "now")
    f = pg.layouts_file(tmp_path, "rel")
    old = json.loads(f.read_text())
    f.write_text(json.dumps({"kept": [{k: v for k, v in x.items() if k != "id"} for x in old["kept"]]}))   # a file from before IDs
    assert [k["id"] for k in pg.layouts_kept(tmp_path, "rel")] == [1, 2, 3]
    kept = pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, x=0.2), "now")          # un-keep #2
    assert [k["id"] for k in kept] == [1, 3]
    kept = pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, x=0.9), "now")          # a new keep gets 4, not 2 or 3
    assert [k["id"] for k in kept] == [1, 3, 4]
    assert json.loads(f.read_text())["next_id"] == 5
    kept = pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, x=0.9), "now")
    kept = pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, x=0.8), "now")
    assert [k["id"] for k in kept] == [1, 3, 5]


def test_half_the_night_migration_on_a_copy_keeps_every_keep(tmp_path):
    """The proof for Amir: on a copy of the real file, 50 in = 50 out, same order, every field the same,
    only the id added, and ids = the numbers the page showed (#50 = the final cover)."""
    dst = pg.layouts_file(tmp_path, "pinocchio-single")
    dst.parent.mkdir(parents=True)
    shutil.copy(HTN, dst)
    before = json.loads(HTN.read_text())["kept"]
    rep = pg.migrate_layout_ids(tmp_path, "pinocchio-single", dry_run=True)
    assert dst.read_bytes() == HTN.read_bytes()                                      # a dry run writes nothing
    assert rep["count_before"] == rep["count_after"] == len(before)
    pg.migrate_layout_ids(tmp_path, "pinocchio-single", dry_run=False)
    after = json.loads(dst.read_text())["kept"]
    assert len(after) == len(before)
    for i, (a, b) in enumerate(zip(after, before)):
        if "id" not in b:
            assert a["id"] == i + 1
        assert {k: v for k, v in a.items() if k != "id"} == {k: v for k, v in b.items() if k != "id"}
    assert pg.migrate_layout_ids(tmp_path, "pinocchio-single", dry_run=False)["changed"] is False   # once only


def test_keep_picture_by_id_and_picks_ticks(tmp_path):
    pg.layouts_toggle(tmp_path, "rel", LAYOUT, "now")
    with pytest.raises(ValueError):
        pg.keep_snap_save(tmp_path, "rel", 2, jpeg(200))                             # no keep 2
    with pytest.raises(ValueError):
        pg.keep_snap_save(tmp_path, "rel", 1, b"not an image")
    p = pg.keep_snap_save(tmp_path, "rel", 1, jpeg(200))
    assert p.name == "id-0001.jpg" and pg.keep_snap_path(tmp_path, "rel", 1) == p
    assert pg.snaps_dir(tmp_path, "pinocchio-single").parts[-3:] == ("htn-noir", "layout-snaps", "pinocchio-single")
    assert pg.picks_toggle(tmp_path, "rel", 1) == [1]
    assert pg.picks_toggle(tmp_path, "rel", 1) == []
    with pytest.raises(ValueError):
        pg.picks_toggle(tmp_path, "rel", 7)


def test_export_sizes_and_no_overwrite(tmp_path):
    with pytest.raises(ValueError):
        pg.export_save(tmp_path, "rel", 2000, jpeg(2000), "20261110-120000")
    with pytest.raises(ValueError):
        pg.export_save(tmp_path, "rel", 3000, jpeg(1000), "20261110-120000")       # wrong size
    out = pg.export_save(tmp_path, "rel", 3000, jpeg(3000), "20261110-120000", 4)
    assert out.name == "cover-20261110-120000-k4-3000px.jpg" and Image.open(out).size == (3000, 3000)
    with pytest.raises(ValueError):
        pg.export_save(tmp_path, "rel", 3000, jpeg(3000), "20261110-120000", 4)
    with pytest.raises(ValueError):
        pg.run_cover_resizer(tmp_path, tmp_path / "elsewhere.jpg")


@pytest.fixture
def client():
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_picks_page_and_api(client, tmp_path, monkeypatch):
    """Routes read the globals of views/playground.py: PROJECT_ROOT and load_release patched there, tmp dir only."""
    import release_manager.views.playground as vp
    monkeypatch.setattr(vp, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(vp, "load_release", lambda slug: {"slug": slug} if slug == "my-rel" else None)
    pg.layouts_toggle(tmp_path, "my-rel", LAYOUT, "now")
    assert client.get("/playground/my-rel/picks").status_code == 200
    d = client.get("/api/playground/my-rel/picks").get_json()
    assert d["kept"][0]["id"] == 1 and d["kept"][0]["v"] == "" and d["ticks"] == []
    assert client.post("/playground/my-rel/layout/keep-snap?id=1", data=jpeg(300)).status_code == 200
    assert (tmp_path / "artwork" / "edits" / "layout-snaps" / "my-rel" / "id-0001.jpg").is_file()
    assert client.get("/api/playground/my-rel/picks").get_json()["kept"][0]["v"] != ""
    assert client.get("/playground/my-rel/layout/keep-img?id=1").status_code == 200
    assert client.get("/playground/my-rel/layout/keep-img?id=..").status_code == 404
    assert client.post("/api/playground/my-rel/picks", json={"id": 1}).get_json()["ticks"] == [1]
    assert client.post("/api/playground/my-rel/picks", json={"id": "1"}).status_code == 400
    r = client.post("/playground/my-rel/layout/export?px=3000", data=jpeg(3000)).get_json()
    assert r["ok"] and r["resized"] is None and r["file"].startswith("artwork/edits/layout-snaps/my-rel/exports/cover-")
    assert client.post("/playground/my-rel/layout/export?px=3000", data=jpeg(100)).status_code == 400
    assert client.get("/playground/no-such/picks").status_code == 404


# --- System 92: the Layout page for any release, on its own base picture ---------------------------------
def test_cover_title_from_the_release():
    assert pg.cover_title({"brand": {"playground": {"title": "HALF THE NIGHT"}}}) == "HALF THE NIGHT"
    assert pg.cover_title({"metadata": {"title": "First  Song"}}) == "FIRST SONG"
    assert pg.cover_title({"slug": "x"}) == "X"


def test_layout_page_opens_a_release_on_its_own_base(client, tmp_path, monkeypatch):
    import release_manager.views.playground as vp
    (tmp_path / "artwork" / "t").mkdir(parents=True)
    Image.new("RGB", (64, 48), (90, 60, 40)).save(tmp_path / "artwork" / "t" / "base.png")
    rels = {"with-base": {"slug": "with-base", "brand": {"playground": {"base": "artwork/t/base.png", "title": "MY SONG"}}},
            "no-base": {"slug": "no-base"}}
    monkeypatch.setattr(vp, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(vp, "load_release", lambda slug: rels.get(slug))
    r = client.get("/playground/with-base/layout")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "var PLAIN = true" in html and '"MY SONG"' in html and "lay-page plain" in html
    assert client.get("/playground/no-base/layout").status_code == 404
    assert client.get("/playground/nope/layout").status_code == 404


def test_half_the_night_layout_page_still_layered(client):
    html = client.get("/playground/pinocchio-single/layout").get_data(as_text=True)
    assert "var PLAIN = false" in html and '"HALF THE NIGHT"' in html and "lay-page plain" not in html
    assert "el-" in html   # its colour saves (element picks) are still what the page draws


# --- System 93: finish stages (grain, corners, rim light) -----------------------------------------------
def test_finish_fields_are_kept_and_checked(tmp_path):
    kept = pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, fgrain=0.15, fcorner=0.2, rim=0.6, rimx=0.7, rimy=0.4, rimcol="red"), "now")
    k = kept[0]
    assert (k["fgrain"], k["fcorner"], k["rim"], k["rimx"], k["rimy"], k["rimcol"]) == (0.15, 0.2, 0.6, 0.7, 0.4, "red")
    for bad in ({"fgrain": 2}, {"rim": -0.1}, {"rimx": 9}, {"rimcol": "pink"}):
        with pytest.raises(ValueError):
            pg.layouts_toggle(tmp_path, "rel", dict(LAYOUT, **bad), "now")


def test_a_keep_from_before_finish_means_no_finish(tmp_path):
    """An old keep (no finish fields, no lw) is the same layout as the page sending finish 0 and lw 1:
    pressing Keep on it un-keeps it instead of adding a twin, and nothing is added to it."""
    f = pg.layouts_file(tmp_path, "rel")
    f.parent.mkdir(parents=True)
    old = {k: v for k, v in LAYOUT.items()}
    f.write_text(json.dumps({"kept": [dict(old, saved="2026-11-06 02:04")]}))
    page = dict(LAYOUT, lw=1.0, hglow=0.0, fgrain=0.0, fcorner=0.0, rim=0.0, rimx=0.75, rimy=0.2, rimcol="", tgrain=False, tshadow=False)
    assert pg.layouts_toggle(tmp_path, "rel", page, "now") == []


# --- System 94: one fixed tag list (T1) and the studio drawer (A) ----------------------------------------
def test_tag_file_uses_only_the_list_and_covers_every_library():
    from release_manager import studio_tags as st
    d = st.load()
    ids = {t["id"] for t in d["tags"]}
    assert ids == {t for t, _ in st.tag_list(d)} and 25 <= len(ids) <= 45   # the file is the source (Fable gate 11-20)
    assert all(set(v) <= ids for v in d["assign"].values())
    libs = {k.split(":")[0] for k in d["assign"]}
    assert libs == {"archive", "effect", "font", "imagine"}
    assert "90s-noir" in d["assign"]["archive:R-022"] and "half-the-night" in d["assign"]["archive:R-022"]
    assert "half-the-night" in d["assign"]["effect:look-xerox"]


def test_new_library_item_gets_rule_tags_and_hand_edits_win():
    from release_manager import studio_tags as st
    data = {"assign": {"effect:x": ["moon", "not-a-tag"]}}
    assert st.tags_for("effect", "x", {}, data) == ["moon"]                       # the file wins, list tags only
    assert st.tags_for("effect", "new", {"name": "Neon night glow", "group": "Light"}, data) == ["night", "neon", "glow"]


def test_drawer_lists_the_four_libraries_with_actions(client):
    d = client.get("/api/playground/pinocchio-single/drawer").get_json()
    libs = {i["lib"] for i in d["items"]}
    assert libs == {"archive", "effect", "font", "imagine"}
    xerox = next(i for i in d["items"] if i["id"] == "look-xerox")
    assert xerox["look"] == "xerox"                                                # a page effect: one click puts it on
    import re
    assert all(re.fullmatch(r"l[a-z0-9]{1,19}", i["key"]) for i in d["items"] if i["lib"] == "font")   # valid keep font keys
    assert client.get("/api/playground/no-such/drawer").status_code == 404


def test_layout_page_has_the_drawer(client):
    html = client.get("/playground/pinocchio-single/layout").get_data(as_text=True)
    assert 'id="drawer"' in html and 'id="draweropen"' in html and 'id="pins"' in html


# --- System 100: phone width (375 px), no sideways scroll on Layout, release, /review, /shoot ------------
def test_phone_width_rules_are_in_place(client):
    html = client.get("/playground/pinocchio-single/layout").get_data(as_text=True)
    assert "@media (max-width: 700px)" in html and ".pill { flex-wrap: wrap;" in html and ".stagewrap { grid-template-columns: minmax(0, 1fr); }" in html
    css = (ROOT / "release_manager" / "static" / "style.css").read_text()
    phone = css[css.index("System 100"):]
    for rule in (".tracks-table { display: block; max-width: 100%; overflow-x: auto; }", ".board-page { grid-template-columns: minmax(0, 1fr); }",
                 ".board-kpis { flex-wrap: wrap;", ".shoot-outfit-head { flex-wrap: wrap; }"):
        assert rule in phone
    assert not any(t in phone for t in ("rgb(", "rgba(", "#"))   # colours only through the :root tokens: the phone block sets none
    import re as _re
    _v = _re.search(r"style\.css\?v=(\d+)", client.get("/release/pinocchio-single").get_data(as_text=True))
    assert _v and int(_v.group(1)) >= 103                # any later bump is fine (a pinned 103 broke on v104)   # phones fetch the new CSS


def test_finish_starts_at_zero_when_the_release_has_keeps(client, tmp_path, monkeypatch):
    """Amir 11-12: a release with keeps (Half the Night) opens with no grain or corners on a fresh browser;
    only a new cover with no keeps starts them low (15% / 20%)."""
    assert "var HASKEEPS = true" in client.get("/playground/pinocchio-single/layout").get_data(as_text=True)
    import release_manager.views.playground as vp
    (tmp_path / "artwork" / "t").mkdir(parents=True)
    Image.new("RGB", (64, 64), (90, 60, 40)).save(tmp_path / "artwork" / "t" / "base.png")
    monkeypatch.setattr(vp, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(vp, "load_release", lambda slug: {"slug": slug, "brand": {"playground": {"base": "artwork/t/base.png"}}})
    html = client.get("/playground/new-song/layout").get_data(as_text=True)
    assert "var HASKEEPS = false" in html and "fgrain: 0.15, fcorner: 0.2" in html
    pg.layouts_toggle(tmp_path, "new-song", LAYOUT, "now")
    assert "var HASKEEPS = true" in client.get("/playground/new-song/layout").get_data(as_text=True)


def test_drawer_shows_items_without_a_tag_under_an_untagged_chip(client):
    # Fable gate 2026-11-15: 65 items had no tag and hid from every chip.
    d = client.get("/api/playground/pinocchio-single/drawer").get_json()
    assert all(it["tags"] for it in d["items"])
    lone = [it for it in d["items"] if it["tags"] == ["untagged"]]
    if lone:
        assert any(t["id"] == "untagged" for t in d["tags"])
    from release_manager import studio_tags as st
    assert "untagged" not in st.TAG_IDS                      # a drawer chip only, never a stored tag
    assert dict(st.TAGS)["rose"] == "Roses (one of our motifs)"


# Opus gate 2026-11-15: the tag list itself comes from docs/brand/tags.json, not from the code.
def test_tag_list_is_read_from_the_file():
    from release_manager import studio_tags as st
    data = {"tags": [{"id": "moon", "means": "The moon"}, {"id": "snow", "means": "Snow and frost"}], "assign": {}}
    assert st.tag_list(data) == [("moon", "The moon"), ("snow", "Snow and frost")]
    data["assign"]["effect:x"] = ["snow", "night"]                  # night is not in this file's list
    assert st.tags_for("effect", "x", {}, data) == ["snow"]


def test_tag_list_skips_bad_entries_and_falls_back_when_empty():
    from release_manager import studio_tags as st
    bad = {"tags": [{"id": "Bad Id"}, {"id": "untagged", "means": "x"}, "moon", {"id": "owl", "means": 5},
                    {"id": "owl", "means": "again"}, {"id": "<b>x</b>", "means": "y"}]}
    assert st.tag_list(bad) == [("owl", "")]
    assert st.tag_list({"tags": []}) == list(st.TAGS)
    assert st.tag_list({}) == list(st.TAGS)
    assert st.tag_list({"tags": "moon"}) == list(st.TAGS)


def test_drawer_tag_list_matches_the_file(client):
    from release_manager import studio_tags as st
    d = client.get("/api/playground/pinocchio-single/drawer").get_json()
    shown = [(t["id"], t["means"]) for t in d["tags"] if t["id"] != "untagged"]
    assert shown == st.tag_list(st.load())


def test_tag_reader_survives_broken_values():
    # Fable gate 2026-11-20: a broken tags.json falls back instead of crashing the drawer
    from release_manager import studio_tags as st
    for bad in ({"tags": 5}, {"tags": True}, {"tags": "moon"}, {"tags": {"id": "moon"}}, []):
        assert st.tag_list(bad) == list(st.TAGS)
    data = {"tags": [{"id": "moon", "means": "The moon"}, {"id": "dark", "means": "Dark"}],
            "assign": {"effect:a": [["moon"], "moon", 5], "effect:b": "moon", "effect:c": None}}
    assert st.tags_for("effect", "a", {}, data) == ["moon"]
    assert st.tags_for("effect", "b", {"group": "Dark and horror"}, data) == ["dark"]   # a string value = not listed: rule tags
    assert st.tags_for("effect", "c", {}, data) == []
    assert st.tags_for("effect", "d", {}, {"tags": data["tags"], "assign": 7}) == []


def test_new_file_tag_reaches_unlisted_items_through_the_rules():
    from release_manager import studio_tags as st
    data = {"tags": [{"id": "zebra", "means": "Stripes"}], "assign": {}}
    assert st.tags_for("archive", "R-999", {"tags": ["zebra", "moon"]}, data) == ["zebra"]
    assert st.rule_tags("archive", {"tags": ["zebra"]}) == []   # the first fill still uses the built-in list


def test_drawer_drops_saved_tags_that_left_the_list():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / "release_manager/templates/playground_layout.html").read_text()
    assert "a tag renamed or removed in tags.json leaves the filter" in html
