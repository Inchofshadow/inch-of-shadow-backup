"""GR-07: shape check for the three Gero-lane Gap Radar profiles (no engine needed)."""
import json
from pathlib import Path

import pytest

PROFILES = Path(__file__).resolve().parent.parent / "gap_radar" / "profiles"
NAMES = ["gero-wallet-pains", "gero-seo-topics", "gero-card-competitors"]
TOP = {"name", "question", "system_extra", "output_dir", "crowding", "sources"}
SOURCES = {"reddit", "hn_queries", "stackexchange", "youtube_queries", "github_queries",
           "appstore", "hikerapi"}


def _str_list(v):
    return isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)


@pytest.mark.parametrize("name", NAMES)
def test_profile_shape(name):
    p = json.loads((PROFILES / f"{name}.json").read_text())
    assert set(p) == TOP
    assert p["name"] == name
    assert p["question"].strip() and p["system_extra"].strip()
    assert p["crowding"] is False
    # NDA: Gero reports live in the Gero folder, never in this repo
    assert p["output_dir"] == f"/Users/amir/Desktop/Gero/gap-radar-reports/{name}/"

    s = p["sources"]
    assert set(s) == SOURCES
    assert set(s["reddit"]) == {"subs", "phrases"}
    assert _str_list(s["reddit"]["subs"]) and _str_list(s["reddit"]["phrases"])
    for k in ("hn_queries", "youtube_queries", "github_queries"):
        assert _str_list(s[k])
    assert set(s["stackexchange"]) == {"sites", "queries"}
    assert _str_list(s["stackexchange"]["sites"]) and _str_list(s["stackexchange"]["queries"])
    assert set(s["appstore"]) == {"genres", "app_ids"}
    assert _str_list(s["appstore"]["genres"])
    assert all(i.isdigit() for i in s["appstore"]["app_ids"])
    assert set(s["hikerapi"]) == {"hashtags", "accounts", "max_calls"}
    assert s["hikerapi"]["max_calls"] == 0


def test_seo_topics_uses_cardano_stackexchange():
    p = json.loads((PROFILES / "gero-seo-topics.json").read_text())
    assert "cardano" in p["sources"]["stackexchange"]["sites"]


@pytest.mark.parametrize("name", ["gero-wallet-pains", "gero-card-competitors"])
def test_competitor_profiles_have_app_ids(name):
    p = json.loads((PROFILES / f"{name}.json").read_text())
    assert len(p["sources"]["appstore"]["app_ids"]) >= 5
