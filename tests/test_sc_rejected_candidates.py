"""Rejected-candidates memory (2026-09-08, after the junk-run incident:
a session without click-time context liked 16/18 and followed 7/7 candidates
that had been rejected days earlier). Rejections are machine-readable now and
excluded everywhere, permanently."""
import json

import scene_intelligence.sc_engagement as sc


def _setup(tmp_path, monkeypatch, rejected=None):
    f = tmp_path / "sc_rejected_candidates.json"
    if rejected is not None:
        f.write_text(json.dumps({"rejected": rejected}))
    monkeypatch.setattr(sc, "REJECTED_FILE", f)
    return f


def test_mark_rejected_appends_and_dedupes(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert sc.mark_rejected("42", "https://soundcloud.com/off-scene-guy",
                            "Off Scene Guy", "deep house") is True
    assert sc.mark_rejected("42", "", "", "again") is False          # by id
    assert sc.mark_rejected("", "off-scene-guy", "", "again") is False  # by slug
    rej = sc.load_rejected()["rejected"]
    assert len(rej) == 1
    assert rej[0]["permalink"] == "off-scene-guy"
    assert rej[0]["reason"] == "deep house"


def test_rejected_keys_shapes(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch,
           [{"permalink": "bad-guy", "user_id": "7", "reason": "x"}])
    ids, slugs = sc.rejected_keys()
    assert ids == {"7"} and slugs == {"bad-guy"}


def test_missing_file_is_empty_not_error(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert sc.load_rejected()["rejected"] == []
    assert sc.rejected_keys() == (set(), set())


def test_live_backfill_contains_the_junk_run_names():
    rej = sc.load_rejected()
    slugs = {r["permalink"] for r in rej["rejected"]}
    for known in ("ferrersantis", "talocifra", "jorgecordon-1", "zc_ned",
                  "djdeepro", "ladyarclight"):
        assert known in slugs, known
