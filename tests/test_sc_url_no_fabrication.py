"""Tests for profile-URL resolution on sc_follow logging (added 2026-08-08).

The sc_follow handler used to fall back to building a URL out of the display
name when CC omitted --sc-url:

    sc_url = args.sc_url or f"https://soundcloud.com/{_contact_key({'name': args.name})}"

On 2026-08-06 CC omitted the flag for all 12 follows, so the tracker recorded 12
fabricated URLs, every one of them wrong and 404-ing:

    dj_stockhaus        -> stored st_ckh_us
    jk1962              -> stored caroline_true_records
    panayiotis-fitsoros -> stored pink_dot_

The user_ids were correct, so dedup and follow-back detection still worked, but
the stored URLs were invented data. Same failure class as the 2026-07-10
contact-key bug: the handler silently manufactured a value when a flag was
missing.

_resolve_profile_url now prefers the explicit flag, then a LOCAL lookup of the
user_id in the discovery candidate files (no API call, --log-action must stay
API-free so it is safe inside a cooldown), and otherwise returns empty. It never
fabricates.
"""
import json

import scene_intelligence.sc_engagement as sc


def _write_candidates(tmp_path, monkeypatch, candidates):
    d = tmp_path / "scene_intelligence"
    d.mkdir()
    (d / "discovery_candidates_20260804.json").write_text(
        json.dumps({"candidates": candidates}), encoding="utf-8"
    )
    monkeypatch.setattr(sc, "SI_DIR", d, raising=False)
    return d


def test_explicit_url_always_wins(tmp_path, monkeypatch):
    _write_candidates(tmp_path, monkeypatch,
                      [{"user_id": "123", "sc_url": "https://soundcloud.com/from-file"}])
    got = sc._resolve_profile_url("https://soundcloud.com/explicit", "123", "Some Name")
    assert got == "https://soundcloud.com/explicit"


def test_falls_back_to_local_discovery_lookup_by_user_id(tmp_path, monkeypatch):
    _write_candidates(tmp_path, monkeypatch, [
        {"user_id": "1367911695", "permalink": "dj_stockhaus",
         "sc_url": "https://soundcloud.com/dj_stockhaus"},
    ])
    got = sc._resolve_profile_url("", "1367911695", "Støckhåus")
    assert got == "https://soundcloud.com/dj_stockhaus"


def test_returns_empty_rather_than_fabricating_from_name(tmp_path, monkeypatch):
    _write_candidates(tmp_path, monkeypatch, [])
    got = sc._resolve_profile_url("", "999", "Caroline True Records")
    assert got == ""
    assert "caroline" not in got


def test_never_produces_the_2026_08_06_wrong_urls(tmp_path, monkeypatch):
    """The exact regression: name-derived slugs must never be emitted."""
    _write_candidates(tmp_path, monkeypatch, [])
    for uid, name, wrong in [
        ("1367911695", "Støckhåus", "st_ckh_us"),
        ("225038", "Caroline True Records", "caroline_true_records"),
        ("18239757", "PinK DoT.", "pink_dot_"),
    ]:
        got = sc._resolve_profile_url("", uid, name)
        assert wrong not in got, f"fabricated {wrong} for {name}"
        assert got == ""


def test_strips_utm_query_params(tmp_path, monkeypatch):
    _write_candidates(tmp_path, monkeypatch, [])
    got = sc._resolve_profile_url(
        "https://soundcloud.com/realslug?utm_source=clipboard&utm_medium=text", "1", "N")
    assert got == "https://soundcloud.com/realslug"


def test_handles_missing_discovery_dir_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "SI_DIR", tmp_path / "does_not_exist", raising=False)
    assert sc._resolve_profile_url("", "123", "Name") == ""


def test_builds_url_from_permalink_when_file_lacks_sc_url(tmp_path, monkeypatch):
    _write_candidates(tmp_path, monkeypatch,
                      [{"user_id": "42", "permalink": "realhandle"}])
    assert sc._resolve_profile_url("", "42", "Display Name") == "https://soundcloud.com/realhandle"
