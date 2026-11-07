"""Fonts page (Machine-19): the index validates, nothing outside the fonts folder is served,
filters and file picking behave, the pages answer."""
from pathlib import Path

import pytest

from release_manager import fonts_page as fp

ROOT = Path(__file__).resolve().parent.parent


def _rec(**kw):
    r = {"id": "x", "name": "X", "group": "A", "status": "potential", "licence": "none", "files": [], "system": [],
         "sources": [], "canva": "unknown", "seen_on": "", "tags": ""}
    r.update(kw)
    return r


def test_the_real_index_is_valid_and_its_files_exist():
    data = fp.load(ROOT)
    assert len(data["fonts"]) >= 80
    base = ROOT / fp.FONTS_SUBDIR
    for r in data["fonts"]:
        for f in r["files"]:
            assert (base / f).is_file(), (r["id"], f)


def test_brand_faces_carry_the_right_licence():
    data = fp.load(ROOT)
    by = {r["id"]: r for r in data["fonts"]}
    assert by["albertus-nova"]["status"] == "default now" and by["albertus-nova"]["licence"] == "canva only"
    assert by["marcellus"]["status"] == "fallback" and by["marcellus"]["licence"] == "free"
    assert by["ogg"]["licence"] == "trial"
    assert by["streamster"]["licence"] == "personal use only"


def test_validate_rejects_bad_values_and_escaping_paths():
    data = {"allowed": {"group": {"A": ""}, "status": ["potential"], "licence": ["none"]},
            "fonts": [_rec(), _rec(id="x"), _rec(id="y", group="Z", files=["../../.env"])]}
    errs = fp.validate(data)
    assert any("duplicate" in e for e in errs)
    assert any("group 'Z'" in e for e in errs)
    assert any("leaves the fonts folder" in e for e in errs)


def test_file_allowed_only_for_listed_files():
    data = fp.load(ROOT)
    r = next(r for r in data["fonts"] if r["files"])
    assert fp.file_allowed(ROOT, r, r["files"][0]) is not None
    assert fp.file_allowed(ROOT, r, "../../../.env") is None
    other = next(x for x in data["fonts"] if x["files"] and x["id"] != r["id"])
    assert fp.file_allowed(ROOT, r, other["files"][0]) is None      # a file of another face


def test_primary_file_prefers_the_regular_cut():
    r = _rec(files=["f/Face-BoldItalic.otf", "f/Face-Regular.otf", "f/Face-Variable.ttf"])
    assert fp.primary_file(r) == "f/Face-Regular.otf"


def test_face_rules_use_local_for_system_fonts():
    r = _rec(system=["Didot"])
    rules = fp.face_rules(r, lambda fid, f: f"/f/{f}")
    assert rules and rules[0]["src"] == "local('Didot')"


def test_filters():
    fonts = [_rec(id="a", group="A", licence="free", files=["a.otf"]), _rec(id="b", group="B", canva="yes"),
             _rec(id="c", group="B", status="guest", seen_on="The Cure, Lovesong")]
    ids = lambda rows: [r["id"] for r in rows]
    assert ids(fp.filter_fonts(fonts, {"group": "B"})) == ["b", "c"]
    assert ids(fp.filter_fonts(fonts, {"where": "mac"})) == ["a"]
    assert ids(fp.filter_fonts(fonts, {"where": "nofile"})) == ["b", "c"]
    assert ids(fp.filter_fonts(fonts, {"where": "canva"})) == ["b"]
    assert ids(fp.filter_fonts(fonts, {"q": "cure"})) == ["c"]
    assert ids(fp.filter_fonts(fonts, {"status": "guest"})) == ["c"]


def test_for_release_matches_id_or_name():
    data = {"fonts": [_rec(id="ogg", name="Ogg (Sharp Type)")]}
    assert fp.for_release(data, "ogg")["id"] == "ogg"
    assert fp.for_release(data, "Ogg (Sharp Type)")["id"] == "ogg"
    assert fp.for_release(data, "") is None


@pytest.fixture
def client():
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_pages_answer(client):
    assert client.get("/fonts").status_code == 200
    assert client.get("/fonts?group=C&where=mac&t=Misty+Night").status_code == 200
    assert client.get("/fonts/ogg").status_code == 200
    assert client.get("/fonts/albertus-nova").status_code == 200        # no file: still a page
    assert client.get("/fonts/nothing-here").status_code == 404
    data = fp.load(ROOT)
    ogg = next(r for r in data["fonts"] if r["id"] == "ogg")
    assert client.get(f"/fonts/ogg/file/{ogg['files'][0]}").status_code == 200
    assert client.get("/fonts/ogg/file/../../../.env").status_code == 404
