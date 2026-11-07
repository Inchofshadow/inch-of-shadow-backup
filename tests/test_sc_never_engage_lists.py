"""Tests for the blocked/personal-network exclusion added 2026-07-05 (audit P1-9).

SOP 4.3 rules 13-14 required cross-checking ig_blocked_accounts.json and
ig_personal_network.json before any SC follow/like; the engine read
neither file (2026-06-12 review fix that never landed).
"""
import scene_intelligence.sc_engagement as sc


def test_normalize_collapses_variants():
    assert sc._never_engage_normalize("mm.discos") == "mmdiscos"
    assert sc._never_engage_normalize("MM Discos") == "mmdiscos"
    assert sc._never_engage_normalize("__p.r.z__") == "prz"
    assert sc._never_engage_normalize(None) == ""


def test_is_never_engage_matches_any_value():
    keys = {"mmdiscos", "carlosthings"}
    assert sc._is_never_engage(keys, "MM Discos", "")
    assert sc._is_never_engage(keys, "Some Name", "carlosthings")
    assert not sc._is_never_engage(keys, "Other Artist", "other-slug")
    assert not sc._is_never_engage(keys, "", None)


def test_load_never_engage_keys_reads_both_real_files():
    keys = sc._load_never_engage_keys()
    # from ig_blocked_accounts.json (own labels added in P0-2)
    assert "mmdiscos" in keys
    assert "stereosociety" in keys
    # from ig_personal_network.json (personal friend, added 2026-05-29)
    assert "mollylollen" in keys


def test_build_si_queue_skips_never_engage(monkeypatch):
    def _contact(name, url=""):
        return {"name": name, "category": "dj", "soundcloud_user_id": "1",
                "match_score": "5", "soundcloud_tracks": 20,
                "soundcloud_followers": 500, "soundcloud_url": url}
    contacts = [
        _contact("Carlos Things", "https://soundcloud.com/carlosthings"),
        _contact("Normal DJ", "https://soundcloud.com/normal-dj"),
    ]
    monkeypatch.setattr(sc, "_load_si_contacts", lambda: contacts)
    monkeypatch.setattr(sc, "_load_never_engage_keys", lambda: {"carlosthings"})
    queue = sc.build_si_queue({"log": {}, "hidden": []})
    names = [item["contact"]["name"] for item in queue]
    assert "Carlos Things" not in names
    assert "Normal DJ" in names
