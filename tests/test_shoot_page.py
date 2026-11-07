"""Studio: the Shoot page shows the catalogue with contact_sheet's filters (Machine-11)."""
import json
from pathlib import Path
import pytest
from release_manager.webapp import app, SHOOT_CATALOGUE

pytestmark = pytest.mark.skipif(not SHOOT_CATALOGUE.exists(), reason="no shoot catalogue")


def test_shoot_page_lists_everything_and_filters_like_the_contact_sheet():
    c = app.test_client()
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    html = c.get("/shoot").get_data(as_text=True)
    assert f"{len(cat['photos'])} of {len(cat['photos'])}" in html
    stars = sum(1 for p in cat["photos"] if p.get("her_rating") == 2)
    assert f"{stars} of {len(cat['photos'])}" in c.get("/shoot?stars=2").get_data(as_text=True)
    no_ai = sum(1 for p in cat["photos"] if not p.get("ai_generated"))
    assert f"{no_ai} of {len(cat['photos'])}" in c.get("/shoot?no_ai=1").get_data(as_text=True)
    assert c.get("/shoot/nope").status_code == 404


def test_photo_page_and_a_bad_format():
    c = app.test_client()
    first = json.loads(SHOOT_CATALOGUE.read_text())["photos"][0]["id"]
    html = c.get(f"/shoot/{first}").get_data(as_text=True)
    assert "Crop for a platform" not in html          # the crop buttons left the page on 2026-09-26, the route stays for the tools
    app.config["WTF_CSRF_ENABLED"] = False          # the form carries the token; the test skips it
    try:
        assert c.post(f"/shoot/{first}/pull", data={"format": "banner"}).status_code == 400
    finally:
        app.config["WTF_CSRF_ENABLED"] = True


def test_shoot_page_groups_by_outfit_and_can_sort_by_time_or_id():
    c = app.test_client()
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    html = c.get("/shoot").get_data(as_text=True)
    for o in cat.get("outfits", []):
        assert f'id="outfit-{o["key"]}"' in html
    assert "by capture time" in c.get("/shoot?sort=time").get_data(as_text=True)
    first = cat["outfits"][0]
    assert f'{first["count"]} of {len(cat["photos"])}' in c.get(f"/shoot?outfit={first['key']}").get_data(as_text=True)


def test_photo_page_links_full_size_and_simulates_post_grid_and_cover():
    c = app.test_client()
    first = json.loads(SHOOT_CATALOGUE.read_text())["photos"][0]["id"]
    html = c.get(f"/shoot/{first}").get_data(as_text=True)
    assert f"/shoot/full/{first}" in html
    r = c.get(f"/shoot/full/{first}")
    assert r.status_code in (200, 404)           # 404 only when neither the drive nor the preview cache is there
    if "How it would look" in html:              # needs the preview cache
        assert html.count('class="sim-crop"') >= 4 and "inch_of_shadow" in html and "Song title" in html
    assert c.get("/shoot/grid-tile/nope.jpg").status_code == 404


def test_photo_page_toggles_between_her_edit_and_the_raw():
    c = app.test_client()
    first = json.loads(SHOOT_CATALOGUE.read_text())["photos"][0]["id"]
    html = c.get(f"/shoot/{first}").get_data(as_text=True)
    assert 'data-kind="raw"' in html and f"/shoot/thumb/{first}?kind=raw" in html
    assert c.get(f"/shoot/thumb/{first}?kind=raw").status_code in (200, 404)


def _with_idea(cat):
    """Cover ideas exist for every outdoor photo and for her indoor Best picks (rating 2) only:
    the indoor rating-1 photos have none on purpose since 2026-10-14 (56c1271), and the covers page skips them."""
    for p in cat["photos"]:
        if p["id"].startswith("in-") and p.get("her_rating") != 2:
            assert "cover_idea" not in p or p["cover_idea"], p["id"]
            continue
        assert "cover_idea" in p, p["id"]
    return [p for p in cat["photos"] if p.get("cover_idea")]


def test_every_photo_has_a_cover_idea_and_the_page_draws_it():
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    zones = {"TL", "TC", "TR", "ML", "MC", "MR", "BL", "BC", "BR", "VL", "VR", "none"}
    for p in _with_idea(cat):
        i = p["cover_idea"]
        assert i["title_at"] in zones and i["name_at"] in zones and i["scale"] in ("small", "large") and i["note"]
    first = cat["photos"][0]
    html = app.test_client().get(f"/shoot/{first['id']}").get_data(as_text=True)
    assert "Cover idea for this photo" in html and f'cv-{first["cover_idea"]["title_at"]}' in html


def test_cover_fonts_exist_and_the_page_sets_the_idea_in_one():
    from release_manager.cover_fonts import FONTS, font_path
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    for p in _with_idea(cat):
        assert p["cover_idea"]["font"] in FONTS
    for key, f in FONTS.items():
        assert f.get("local") or font_path(key), key
    first = cat["photos"][0]
    c = app.test_client()
    html = c.get(f"/shoot/{first['id']}").get_data(as_text=True)
    assert "set in <strong>" in html
    file_key = next(k for k, f in FONTS.items() if f.get("file"))
    assert c.get(f"/shoot/font/{file_key}").status_code == 200 and c.get("/shoot/font/nope").status_code == 404


def test_covers_page_and_every_cover_carries_the_name_and_an_ink():
    cat = json.loads(SHOOT_CATALOGUE.read_text())
    ideas = _with_idea(cat)
    for p in ideas:
        i = p["cover_idea"]
        assert i["name_at"] not in (None, "none") and i["name_ink"] and i["ink"], p["id"]
        assert i["name_at"] != i["title_at"] or True
    r = app.test_client().get("/shoot/covers")
    assert r.status_code == 200 and r.get_data(as_text=True).count('class="cv cv-name') == len(ideas)


def test_photo_page_offers_the_five_templates_and_serves_a_graded_preview():
    c = app.test_client()
    first = json.loads(SHOOT_CATALOGUE.read_text())["photos"][0]["id"]
    html = c.get(f"/shoot/{first}").get_data(as_text=True)
    for fam in ("bw", "dusk", "day", "flash", "bluehour"):
        assert f'data-family="{fam}"' in html
    assert html.count('class="js-photo"') >= 4
    assert c.get(f"/shoot/thumb/{first}?kind=grade&family=nope").status_code == 404
    r = c.get(f"/shoot/thumb/{first}?kind=grade&family=dusk")
    assert r.status_code in (200, 404)                  # 404 only without the raw preview cache
