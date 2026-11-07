"""Effects page (Machine-20): the index validates, AI effects are never marked face safe,
examples resolve inside the effects folder only, filters behave, the 'mine' write is atomic
and scoped, the pages answer."""
import json
import shutil
from pathlib import Path

import pytest

from release_manager import effects_page as ep

ROOT = Path(__file__).resolve().parent.parent


def _rec(**kw):
    r = {"id": "x", "name": "X", "family": "looks", "kind": "still", "make": "local", "face_safe": True,
         "what": "", "how": "", "source": "R-006", "example": "", "mine": False}
    r.update(kw)
    return r


def test_the_real_index_is_valid_and_examples_exist():
    data = ep.load(ROOT)
    assert len(data["effects"]) >= 100
    for r in data["effects"]:
        if r["example"]:
            assert ep.example_path(ROOT, r) is not None, r["id"]


def test_ai_effects_are_never_face_safe_in_the_real_index():
    data = ep.load(ROOT)
    for r in data["effects"]:
        if r["make"] == "ai":
            assert r["face_safe"] is False, r["id"]


def test_validate_rejects_bad_records():
    allowed = {"family": {"looks": ""}, "kind": ["still"], "make": {"local": "", "ai": ""}}
    data = {"allowed": allowed, "effects": [_rec(), _rec(id="x"), _rec(id="y", make="ai", face_safe=True),
                                            _rec(id="z", example="../../.env"), _rec(id="w", family="nope")]}
    errs = " ".join(ep.validate(data))
    assert "duplicate" in errs and "face safe" in errs and "examples/" in errs and "family" in errs


def test_example_path_cannot_escape(tmp_path):
    assert ep.example_path(tmp_path, _rec(example="examples/../../x.jpg")) is None
    assert ep.example_path(tmp_path, _rec(example="")) is None


def test_filters():
    eff = [_rec(id="a", family="looks"), _rec(id="b", family="materials", make="ai", face_safe=False, what="glass body"),
           _rec(id="c", kind="motion", make="edit", mine=True)]
    ids = lambda rows: [r["id"] for r in rows]
    assert ids(ep.filter_effects(eff, {"family": "materials"})) == ["b"]
    assert ids(ep.filter_effects(eff, {"make": "safe"})) == ["a", "c"]
    assert ids(ep.filter_effects(eff, {"make": "ai"})) == ["b"]
    assert ids(ep.filter_effects(eff, {"kind": "motion"})) == ["c"]
    assert ids(ep.filter_effects(eff, {"mine": "1"})) == ["c"]
    assert ids(ep.filter_effects(eff, {"q": "GLASS"})) == ["b"]


def test_set_mine_writes_only_that_flag(tmp_path):
    (tmp_path / ep.EFFECTS_SUBDIR).mkdir(parents=True)
    shutil.copy(ROOT / ep.INDEX, tmp_path / ep.INDEX)
    before = json.loads((tmp_path / ep.INDEX).read_text())
    rid = next(r["id"] for r in before["effects"] if not r["mine"])
    assert ep.set_mine(tmp_path, rid, True)
    after = json.loads((tmp_path / ep.INDEX).read_text())
    changed = [(a["id"]) for a, b in zip(after["effects"], before["effects"]) if a != b]
    assert changed == [rid]
    assert ep.set_mine(tmp_path, "nothing-here", True) is False


@pytest.fixture
def client():
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_pages_answer(client):
    assert client.get("/effects").status_code == 200
    assert client.get("/effects?family=materials&make=safe&q=glass&mine=1").status_code == 200
    assert client.get("/effects/variation-flicker").status_code == 200
    assert client.get("/effects/move-micrographics").status_code == 200      # no example: still a page
    assert client.get("/effects/nothing-here").status_code == 404
    assert client.get("/effects/variation-flicker/example").status_code == 200
    assert client.get("/effects/move-micrographics/example").status_code == 404
    assert client.post("/api/effects/nothing-here/flag", json={"field": "mine", "value": True}).status_code == 404
    assert client.post("/api/effects/variation-flicker/flag", json={"field": "../x", "value": True}).status_code == 400
    assert client.post("/api/releases/no-such-release/effects", json={"id": "variation-flicker"}).status_code == 404
    assert client.post("/api/releases/pinocchio-single/effects", json={"id": "nothing-here"}).status_code == 404
    assert client.get("/effects?release=pinocchio-single").status_code == 200
    assert client.get("/release/pinocchio-single").status_code == 200


def test_release_effect_add_update_remove():
    rel = {"brand": {"mood": "M2"}}
    ep.set_release_effect(rel, "a", ["reel", "bogus"])
    ep.set_release_effect(rel, "b")
    ep.set_release_effect(rel, "a", ["cover", "reel"])
    assert ep.release_effects(rel) == [{"id": "a", "used_in": ["cover", "reel"]}, {"id": "b", "used_in": []}]
    ep.set_release_effect(rel, "a", remove=True)
    assert [e["id"] for e in ep.release_effects(rel)] == ["b"] and rel["brand"]["mood"] == "M2"


def test_rows_follow_family_order_and_skip_empty():
    data = {"allowed": {"family": {"looks": "L", "materials": "M", "eras": "E"}}}
    eff = [_rec(id="m", family="materials"), _rec(id="l", family="looks")]
    assert [r["family"] for r in ep.rows(data, eff)] == ["looks", "materials"]


def test_set_flag_refuses_unknown_field(tmp_path):
    assert ep.set_flag(tmp_path, "x", "face_safe", True) is False


def test_rows_carry_groups_in_order_and_skip_a_single_group():
    data = {"allowed": {"family": {"grades": "G"}, "groups": {"grades": ["Cold", "Warm"]}},
            "effects": []}
    a = _rec(id="a", family="grades", group="Warm")
    b = _rec(id="b", family="grades", group="Cold")
    rows = ep.rows(data, [a, b])
    assert [r["id"] for r in rows[0]["cards"]] == ["b", "a"]
    assert [g["name"] for g in rows[0]["groups"]] == ["Cold", "Warm"]
    assert ep.rows(data, [a])[0]["groups"] == []


def test_effects_page_has_photo_and_video_tabs():
    from release_manager.webapp import app
    c = app.test_client()
    photo = c.get("/effects").get_data(as_text=True)
    video = c.get("/effects?kind=motion").get_data(as_text=True)
    assert 'class="fx-tabs"' in photo and 'class="on">Photo' in photo
    assert 'class="on">Video' in video and 'class="fx-groups"' in photo
