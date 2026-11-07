"""bandcamp_links.py (BC-07): ?campaign=<name> links, name rules, release write-back.

Format basis: Amir's Bandcamp Tools page, Campaign Tracking, read 2026-10-21.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import bandcamp_links as bl  # noqa: E402

TRACK = "https://inchofshadow.bandcamp.com/track/the-deceiver"


def test_adds_campaign_param():
    assert bl.campaign_url(TRACK, "sc-buy") == TRACK + "?campaign=sc-buy"


def test_replaces_old_campaign_and_keeps_other_params():
    url = TRACK + "?campaign=old&x=1"
    assert bl.campaign_url(url, "yt-desc") == TRACK + "?x=1&campaign=yt-desc"


def test_drops_fragment_and_lowercases_host():
    assert bl.campaign_url("https://InchOfShadow.bandcamp.com/album/meltscape#buy", "ig-bio") == \
        "https://inchofshadow.bandcamp.com/album/meltscape?campaign=ig-bio"


@pytest.mark.parametrize("name", ["SC-buy", "sc_buy", "sc buy", "", "sc/buy"])
def test_rejects_bad_campaign_names(name):
    with pytest.raises(ValueError):
        bl.campaign_url(TRACK, name)


@pytest.mark.parametrize("url", ["https://soundcloud.com/inch-of-shadow/x",
                                 "https://inchofshadow.bandcamp.com/",
                                 "https://inchofshadow.bandcamp.com/music",
                                 "http://inchofshadow.bandcamp.com/track/x"])
def test_rejects_non_release_urls(url):
    with pytest.raises(ValueError):
        bl.campaign_url(url, "sc-buy")


def test_all_channel_names_are_valid_and_catalog_urls_build():
    for url in bl.CATALOG.values():
        links = bl.links_for(url)
        assert set(links) == set(bl.CHANNELS)


def test_write_release_links_adds_only_its_key(monkeypatch, tmp_path):
    import json
    import release_manager.storage as st
    a = {"slug": "a", "platform_links": {"bandcamp": TRACK},
         "timeline": [{"id": "x", "done": False}], "updated_at": "2026-01-01T00:00:00"}
    b = {"slug": "b", "platform_links": {"bandcamp": ""}}
    (tmp_path / "a.json").write_text(json.dumps(a), encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps(b), encoding="utf-8")
    (tmp_path / "a.bak.20260101.json").write_text(json.dumps(a), encoding="utf-8")
    monkeypatch.setattr(st, "RELEASES_DIR", tmp_path)

    assert bl.write_release_links(["sc-buy"]) == ["a"]
    new_a = json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))
    assert new_a.pop("bandcamp_campaign_links") == {"sc-buy": TRACK + "?campaign=sc-buy"}
    assert new_a == a  # timeline and updated_at untouched
    assert json.loads((tmp_path / "b.json").read_text(encoding="utf-8")) == b
    assert "bandcamp_campaign_links" not in (tmp_path / "a.bak.20260101.json").read_text(encoding="utf-8")
    assert bl.write_release_links(["sc-buy"]) == []  # second run: nothing to change
