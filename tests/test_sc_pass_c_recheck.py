"""PASS C re-check pause (2026-11-03): a target skipped for no recent track is
stamped passc_checked_at and stays off --pass-c-targets for
PASS_C_RECHECK_DAYS, so silent accounts stop taking the top slots."""
import json
from datetime import date

import pytest

import scene_intelligence.sc_engagement as sc

TODAY = date(2026, 11, 3)


def _e(name, **kw):
    d = {"user_id": f"id-{name}", "name": name,
         "url": f"https://soundcloud.com/{name}", "followed_back": True,
         "last_engaged": "2026-07-01"}
    d.update(kw)
    return d


def test_recently_checked_targets_leave_the_list():
    tracker = {"follows": [
        _e("silent", passc_checked_at="2026-11-01"),     # 2 days ago -> out
        _e("old_check", passc_checked_at="2026-10-10"),  # 24 days -> back in
        _e("edge", passc_checked_at="2026-10-20"),       # exactly 14 -> back in
        _e("bad", passc_checked_at="n/a"),               # unparseable -> in
        _e("plain"),
    ]}
    got = [e["name"] for e in sc.pass_c_targets(tracker, TODAY)]
    assert "silent" not in got
    assert set(got) == {"old_check", "edge", "bad", "plain"}


def test_recheck_days_come_from_config(monkeypatch):
    monkeypatch.setattr(sc._cfg_mod(), "PASS_C_RECHECK_DAYS", 30, raising=False)
    tracker = {"follows": [_e("old_check", passc_checked_at="2026-10-10")]}
    assert sc.pass_c_targets(tracker, TODAY) == []


@pytest.fixture
def tmp_tracker(tmp_path, monkeypatch):
    path = tmp_path / "sc_follow_tracker.json"
    data = {"follows": [_e("abbyknives", user_id="899389738"),
                        _e("baba_roga", user_id="9721558")],
            "permanently_unfollowed": [], "stats": {}}
    path.write_text(json.dumps(data))
    monkeypatch.setattr(sc, "FOLLOW_TRACKER", path)
    return path


def test_mark_by_slug_id_and_url(tmp_tracker):
    marked, unknown = sc.mark_passc_checked(
        ["abbyknives", "9721558", "https://soundcloud.com/nobody"], today=TODAY)
    assert marked == ["abbyknives", "baba_roga"]
    assert unknown == ["https://soundcloud.com/nobody"]
    saved = json.loads(tmp_tracker.read_text())
    assert all(e["passc_checked_at"] == "2026-11-03" for e in saved["follows"])


def test_mark_by_profile_url(tmp_tracker):
    marked, _ = sc.mark_passc_checked(["https://soundcloud.com/AbbyKnives"],
                                      today=TODAY)
    assert marked == ["abbyknives"]


def test_unknown_only_does_not_write(tmp_tracker):
    before = tmp_tracker.read_text()
    marked, unknown = sc.mark_passc_checked(["ghost"], today=TODAY)
    assert marked == [] and unknown == ["ghost"]
    assert tmp_tracker.read_text() == before
