"""Pre-confirm flag for the scheduled IG session (2026-09-17).

The flag counts as Amir's confirm for today only: a flag from another day
is never honoured, a broken file is treated as no flag, and --check's exit
code is what the routine branches on.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import scene_intelligence.ig_session_confirm as sc
import pytest


@pytest.fixture(autouse=True)
def _no_real_standing(tmp_path, monkeypatch):
    """The live repo has the standing confirm ON since 2026-10-07; tests must
    not read it."""
    monkeypatch.setattr(sc, "STANDING_PATH", tmp_path / "no-standing.json")

BERLIN = ZoneInfo("Europe/Berlin")
FRI = datetime(2026, 9, 18, 13, 0, tzinfo=BERLIN)
SAT = datetime(2026, 9, 19, 13, 0, tzinfo=BERLIN)


def test_set_then_read_same_day(tmp_path):
    p = tmp_path / "flag.json"
    rec = sc.set_flag(p, now=FRI)
    assert rec["date"] == "2026-09-18"
    assert rec["scope"] == ["preflight", "action_1"]
    got = sc.read_flag(p, now=FRI)
    assert got is not None and got["confirmed_at"].startswith("2026-09-18T13:00:00")


def test_flag_from_another_day_is_ignored(tmp_path):
    p = tmp_path / "flag.json"
    sc.set_flag(p, now=FRI)
    assert sc.read_flag(p, now=SAT) is None


def test_missing_or_broken_flag_is_none(tmp_path):
    p = tmp_path / "flag.json"
    assert sc.read_flag(p, now=FRI) is None
    p.write_text("{not json")
    assert sc.read_flag(p, now=FRI) is None
    p.write_text(json.dumps({"date": "2026-09-18"}))  # no confirmed_at
    assert sc.read_flag(p, now=FRI) is None


def test_clear(tmp_path):
    p = tmp_path / "flag.json"
    assert sc.clear_flag(p) is False
    sc.set_flag(p, now=FRI)
    assert sc.clear_flag(p) is True
    assert not p.exists()


def test_cli_check_exit_codes(tmp_path, monkeypatch, capsys):
    p = tmp_path / "flag.json"
    monkeypatch.setattr(sc, "FLAG_PATH", p)
    monkeypatch.setattr(sc, "_now", lambda: FRI)
    assert sc.main(["--check"]) == 1
    assert capsys.readouterr().out.strip() == "none"
    assert sc.main(["--set"]) == 0
    assert "today's session" in capsys.readouterr().out
    assert sc.main(["--check"]) == 0
    assert capsys.readouterr().out.startswith("confirmed 2026-09-18")
    # next day: same file, now stale
    monkeypatch.setattr(sc, "_now", lambda: SAT)
    assert sc.main(["--check"]) == 1
    assert "stale" in capsys.readouterr().out
    assert sc.main(["--clear"]) == 0
    assert not p.exists()


# --- confirm on an off day counts for the next session (2026-09-22) ----------
TUE = datetime(2026, 9, 22, 13, 30, tzinfo=BERLIN)
WED = datetime(2026, 9, 23, 15, 0, tzinfo=BERLIN)


def test_off_day_confirm_is_for_next_action_day(tmp_path):
    p = tmp_path / "flag.json"
    rec = sc.set_flag(p, now=TUE)
    assert rec["date"] == "2026-09-23"
    assert sc.read_flag(p, now=TUE) is None      # not a Tuesday confirm
    assert sc.read_flag(p, now=WED) is not None  # counts on Wednesday


def test_action_day_after_cutoff_rolls_forward():
    late_sat = datetime(2026, 9, 19, 22, 30, tzinfo=BERLIN)
    assert sc.target_session_day(late_sat).isoformat() == "2026-09-21"  # Monday
    assert sc.target_session_day(FRI).isoformat() == "2026-09-18"        # same day


def test_clear_only_date_keeps_a_future_confirm(tmp_path):
    p = tmp_path / "flag.json"
    sc.set_flag(p, now=TUE)                       # for Wednesday
    assert sc.clear_flag(p, only_date="2026-09-22") is False
    assert p.exists()
    assert sc.clear_flag(p, only_date="2026-09-23") is True


def test_check_says_confirm_is_waiting(tmp_path, monkeypatch, capsys):
    p = tmp_path / "flag.json"
    monkeypatch.setattr(sc, "FLAG_PATH", p)
    monkeypatch.setattr(sc, "_now", lambda: TUE)
    sc.main(["--set"])
    capsys.readouterr()
    assert sc.main(["--check"]) == 1
    assert "waiting for 2026-09-23" in capsys.readouterr().out


def test_wait_returns_when_flag_appears_and_times_out(tmp_path, monkeypatch, capsys):
    """2026-10-07: the sanctioned wait. Improvised shell loops prompted and
    turned two 15-minute waits into 44 min and 2h50m."""
    p = tmp_path / "flag.json"
    monkeypatch.setattr(sc, "FLAG_PATH", p)
    monkeypatch.setattr(sc, "_now", lambda: FRI)
    import time as _t
    monkeypatch.setattr(_t, "sleep", lambda s: None)
    assert sc.main(["--wait", "0"]) == 1
    assert "timeout" in capsys.readouterr().out
    sc.set_flag(p, now=FRI)
    assert sc.main(["--wait", "0"]) == 0
    assert capsys.readouterr().out.startswith("confirmed")


def test_standing_confirm_covers_check_and_wait(tmp_path, monkeypatch, capsys):
    """2026-10-07 Amir: 'remove the confirm'. With the standing file on, --check
    and --wait are confirmed with no per-session flag; off restores the old rule."""
    f = tmp_path / "flag.json"; s = tmp_path / "standing.json"
    monkeypatch.setattr(sc, "FLAG_PATH", f); monkeypatch.setattr(sc, "STANDING_PATH", s)
    monkeypatch.setattr(sc, "_now", lambda: FRI)
    assert sc.main(["--check"]) == 1
    assert sc.main(["--standing", "on"]) == 0
    assert "ON" in capsys.readouterr().out
    assert sc.main(["--check"]) == 0
    assert "standing" in capsys.readouterr().out
    assert sc.main(["--wait", "0"]) == 0
    assert sc.main(["--standing", "off"]) == 0
    assert sc.main(["--check"]) == 1
