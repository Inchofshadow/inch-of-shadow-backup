"""build_full_queue must treat any discovery* source as discovery (audit P3-15).

The engine emits discovery candidates with source "discovery_v2", but the
upload-age bypass checked == "discovery". Discovery items carry an empty
contact dict (no soundcloud_last_upload), so every discovery_v2 peer failed
the upload-age gate and engine-driven discovery follows NEVER queued.
"""
import scene_intelligence.sc_engagement as sc


def _discovery_item(uid, source):
    return {
        "user_id": uid,
        "contact_key": f"disc_{uid}",
        "name": f"artist {uid}",
        "contact": {},          # discovery items never carry last_upload
        "tier": "peer",
        "source": source,
        "match_score": 0,
        "followers": 500,
    }


def _build(monkeypatch, items):
    monkeypatch.setattr(sc, "build_promo_queue", lambda eng_log: ([], []))
    monkeypatch.setattr(sc, "build_si_queue", lambda eng_log: [])
    monkeypatch.setattr(sc, "discover_related_artists",
                        lambda si, tracker, log: items)
    tracker = {"follows": [], "stats": {}}
    return sc.build_full_queue({}, tracker, include_discovery=True)


def test_discovery_v2_items_reach_follows_queue(monkeypatch):
    q = _build(monkeypatch, [_discovery_item("101", "discovery_v2")])
    assert [i["user_id"] for i in q["follows"]] == ["101"]


def test_legacy_discovery_source_still_bypasses(monkeypatch):
    q = _build(monkeypatch, [_discovery_item("102", "discovery")])
    assert [i["user_id"] for i in q["follows"]] == ["102"]


def test_non_discovery_empty_contact_still_gated(monkeypatch):
    # an SI-style item with no last_upload must NOT follow (inactive account)
    item = _discovery_item("103", "si_contact")
    q = _build(monkeypatch, [item])
    assert q["follows"] == []
