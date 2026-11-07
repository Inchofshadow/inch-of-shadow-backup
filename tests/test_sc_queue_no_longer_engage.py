"""Tests for the no_longer_engage queue guard added 2026-07-05 (audit P0).

The 2026-07-04 audit found the SC engine never read the flag: released-on
labels mm.discos and Stereo Society were live like/repost targets, and the
engagement log shows mm.discos was actually liked twice (2026-05-09 and
2026-05-23).
"""
import scene_intelligence.sc_engagement as sc


def _contact(name, **kw):
    c = {
        "name": name,
        "category": "label",
        "soundcloud_user_id": kw.pop("uid", "12345"),
        "match_score": "5",
        "soundcloud_tracks": 50,
        "soundcloud_followers": 3000,
    }
    c.update(kw)
    return c


def test_build_si_queue_skips_no_longer_engage(monkeypatch):
    contacts = [
        _contact("mm.discos", uid="2159984", no_longer_engage=True),
        _contact("Normal Label", uid="999"),
    ]
    monkeypatch.setattr(sc, "_load_si_contacts", lambda: contacts)
    queue = sc.build_si_queue({"log": {}, "hidden": []})
    names = [item["contact"]["name"] for item in queue]
    assert "mm.discos" not in names
    assert "Normal Label" in names
