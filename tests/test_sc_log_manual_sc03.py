"""SC-03 (2026-09-01): sc_log_manual.py made safe.

Audit F3/F6: the script could silently wipe both shared state files (corrupt
-> empty default -> plain overwrite), hardcoded a 7-day window vs the config's
14, and dropped unresolved manual follows on the floor (logged but untracked).
"""
import json

import pytest

import scene_intelligence.sc_log_manual as m
from scene_intelligence.json_io import CorruptStateFile
from scene_intelligence.sc_engagement_config import UNFOLLOW_AFTER_DAYS


def test_corrupt_tracker_hard_stops(tmp_path, monkeypatch):
    f = tmp_path / "t.json"
    f.write_text("{broken")
    monkeypatch.setattr(m, "TRACKER_FILE", f)
    with pytest.raises(CorruptStateFile):
        m._load_tracker()


def test_corrupt_eng_log_hard_stops(tmp_path, monkeypatch):
    f = tmp_path / "e.json"
    f.write_text("{broken")
    monkeypatch.setattr(m, "ENG_LOG_FILE", f)
    with pytest.raises(CorruptStateFile):
        m._load_eng_log()


def test_missing_files_still_bootstrap(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "TRACKER_FILE", tmp_path / "none.json")
    monkeypatch.setattr(m, "ENG_LOG_FILE", tmp_path / "none2.json")
    assert m._load_tracker()["follows"] == []
    assert m._load_eng_log()["log"] == {}


def test_manual_follow_window_matches_config():
    src = open(m.__file__).read()
    assert "timedelta(days=UNFOLLOW_AFTER_DAYS)" in src
    assert "timedelta(days=7)" not in src
    assert UNFOLLOW_AFTER_DAYS == 10   # 14 -> 10 on 2026-09-29 (Amir)


def test_unresolved_manual_follow_reaches_tracker(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "TRACKER_FILE", tmp_path / "t.json")
    monkeypatch.setattr(m, "ENG_LOG_FILE", tmp_path / "e.json")
    monkeypatch.setattr(m, "ENRICHED_FILE", tmp_path / "none.json")
    monkeypatch.setattr(m, "resolve_url", lambda url: None)  # API resolve fails
    m.log_manual_follow("https://soundcloud.com/some-artist")
    tracker = json.loads((tmp_path / "t.json").read_text())
    assert len(tracker["follows"]) == 1
    e = tracker["follows"][0]
    assert e["user_id"] == ""                 # unresolved, honest
    assert e["log_slug"] == "some-artist"     # weekly health can resolve it
    assert e["source"] == "manual"


def test_manual_unfollow_of_protected_is_not_cemented(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(m, "TRACKER_FILE", tmp_path / "t.json")
    monkeypatch.setattr(m, "ENG_LOG_FILE", tmp_path / "e.json")
    monkeypatch.setattr(m, "ENRICHED_FILE", tmp_path / "none.json")
    (tmp_path / "t.json").write_text(json.dumps({
        "follows": [{"user_id": "42", "name": "friend", "followed_back": True}],
        "permanently_unfollowed": [], "manually_unfollowed_slugs_pending": [],
        "stats": {}}))
    monkeypatch.setattr(m, "resolve_url",
                        lambda url: {"id": 42, "username": "friend", "followers_count": 5})
    m.log_manual_unfollow("https://soundcloud.com/friend")
    out = capsys.readouterr().out
    assert "CHURN ALERT" in out
    tracker = json.loads((tmp_path / "t.json").read_text())
    assert tracker["permanently_unfollowed"] == []   # mistake not cemented
    assert tracker["follows"] == []                  # but reality recorded
