"""Machine-27: Write with both. Claude and GPT write the same copy side by side; nothing is saved
until a field or bio is picked, and the pick records who wrote it. Fake writers, nothing sent."""

import pytest

from release_manager import bio_manager, seo_copy_generator, webapp
from release_manager.views import words   # RM 2.0 slice 3: the routes read words' globals


@pytest.fixture
def app(monkeypatch):
    webapp.app.config["WTF_CSRF_ENABLED"] = False
    store = {"rel": {"slug": "test-song", "metadata": {"title": "Test Song"}, "seo_copy": {}}, "saved": 0}

    def load(slug):
        return store["rel"] if slug == "test-song" else None

    def save(rel):
        store["saved"] += 1
        store["rel"] = rel

    monkeypatch.setattr(words, "load_release", load)
    monkeypatch.setattr(words, "save_release", save)
    monkeypatch.setattr(words, "list_releases", lambda: [store["rel"]])
    return webapp.app.test_client(), store


def fake_copy(release, platforms, tone, provider="claude"):
    return {"spotify_pitch": f"{provider} pitch", "youtube_titles": [f"{provider} a", f"{provider} b"]}


def test_seo_both_returns_two_versions_and_saves_nothing(app, monkeypatch):
    c, store = app
    monkeypatch.setattr(seo_copy_generator, "generate_copy", fake_copy)
    j = c.post("/api/seo-copy/generate-both", json={"slug": "test-song", "platforms": ["spotify", "youtube"]}).get_json()
    assert j["ok"] and j["copies"]["claude"]["spotify_pitch"] == "claude pitch"
    assert j["copies"]["openai"]["spotify_pitch"] == "openai pitch" and j["errors"] == {}
    assert store["saved"] == 0


def test_seo_pick_saves_one_field_with_who_wrote_it(app):
    c, store = app
    j = c.post("/api/seo-copy/pick", json={"slug": "test-song", "key": "spotify_pitch", "value": "openai pitch",
                                           "written_by": "openai"}).get_json()
    assert j["ok"] and store["saved"] == 1
    sc = store["rel"]["seo_copy"]
    assert sc["spotify"]["pitch"] == "openai pitch" and sc["written_by"]["spotify_pitch"] == "openai"
    j = c.post("/api/seo-copy/pick", json={"slug": "test-song", "key": "youtube_titles", "value": ["a", "b"],
                                           "written_by": "claude"}).get_json()
    assert j["ok"] and store["rel"]["seo_copy"]["youtube"]["titles"] == ["a", "b"]


@pytest.mark.parametrize("body", [{"key": "nope", "value": "x"}, {"key": "spotify_pitch", "value": {"a": 1}},
                                  {"key": "spotify_pitch", "value": "x", "slug": "missing"}])
def test_seo_pick_refuses_bad_input(app, body):
    c, store = app
    r = c.post("/api/seo-copy/pick", json={"slug": "test-song", **body})
    assert r.status_code in (400, 404) and store["saved"] == 0


def test_one_writer_failing_still_returns_the_other(app, monkeypatch):
    c, _ = app

    def half(release, platforms, tone, provider="claude"):
        if provider == "openai":
            raise ValueError("GPT returned no text")
        return {"spotify_pitch": "claude pitch"}

    monkeypatch.setattr(seo_copy_generator, "generate_copy", half)
    j = c.post("/api/seo-copy/generate-both", json={"slug": "test-song", "platforms": ["spotify"]}).get_json()
    assert j["ok"] and list(j["copies"]) == ["claude"] and j["errors"] == {"openai": "GPT returned no text"}


def test_both_failing_is_an_error(app, monkeypatch):
    c, _ = app
    monkeypatch.setattr(seo_copy_generator, "generate_copy", lambda *a, **k: (_ for _ in ()).throw(ValueError("down")))
    r = c.post("/api/seo-copy/generate-both", json={"slug": "test-song", "platforms": ["spotify"]})
    assert r.status_code == 502 and "down" in r.get_json()["error"]


def test_bios_both_and_written_by_on_save(app, monkeypatch):
    c, _ = app
    profile = {"artist": "Inch of Shadow", "bios": {"bandcamp": {"current": "old"}}}
    saved = {}
    monkeypatch.setattr(bio_manager, "load_profile", lambda: profile)
    monkeypatch.setattr(bio_manager, "save_profile", lambda p: saved.update(p))
    monkeypatch.setattr(bio_manager, "generate_bios",
                        lambda prof, latest=None, provider="claude": {"bandcamp": f"{provider} bio"})
    j = c.post("/api/bios/generate-both", json={}).get_json()
    assert j["ok"] and j["bios"]["claude"]["bandcamp"] == "claude bio" and j["bios"]["openai"]["bandcamp"] == "openai bio"
    assert saved == {}
    j = c.put("/api/bios/save", json={"platform": "bandcamp", "bio": "openai bio", "source": "generate",
                                      "written_by": "openai"}).get_json()
    assert j["ok"] and saved["bios"]["bandcamp"]["current"] == "openai bio"
    assert saved["bios"]["bandcamp"]["written_by"] == "openai" and saved["bios"]["bandcamp"]["previous"] == "old"
