"""--pass-c-targets (2026-09-11): one sanctioned PASS C list.

Two sessions on 09-11 improvised grep pipelines over the tracker to find
maintenance-like targets; the second stopped on a permission prompt for 50
minutes. The flag mirrors close_loops._sc_pass_c_available, so the pool the
scorer expects and the list the session works from are the same set.
"""
import sys
from datetime import date

import scene_intelligence.sc_engagement as sc

TODAY = date(2026, 9, 11)


def _e(name, **kw):
    d = {"user_id": name, "name": name, "url": f"https://soundcloud.com/{name}",
         "followed_back": True}
    d.update(kw)
    return d


def test_pool_matches_the_sop_rules():
    tracker = {"follows": [
        _e("fresh", last_engaged="2026-09-01"),               # inside 30d
        _e("old", last_engaged="2026-07-01"),                 # eligible
        _e("never"),                                          # eligible, first
        _e("swept", last_engaged="2026-01-01", no_longer_following=True),
        _e("dead", last_engaged="2026-01-01", no_longer_engage=True),
        _e("nofb", last_engaged="2026-01-01", followed_back=False),
        _e("si_recent", followed_back=False, source="si_contact",
           last_engaged="2026-09-08"),                        # < 7d
        _e("si_old", followed_back=False, source="si_contact",
           last_engaged="2026-08-20"),                        # eligible
        _e("bad_date", last_engaged="n/a"),                   # treated as never
    ]}
    got = [e["name"] for e in sc.pass_c_targets(tracker, TODAY)]
    assert got == ["never", "bad_date", "old", "si_old"]


def test_flag_is_local_only_and_prints(monkeypatch, capsys):
    class _Tripped(SystemExit):
        pass

    def trip(platform="sc"):
        raise _Tripped(6)
    monkeypatch.setattr(sc, "_sc_standard_gates", trip)
    monkeypatch.setattr(sc, "SC_CLIENT_ID", "x")
    monkeypatch.setattr(sc, "SC_CLIENT_SECRET", "y")
    monkeypatch.setattr(sc, "load_follow_tracker",
                        lambda: {"follows": [_e("old", last_engaged="2026-01-01"),
                                             _e("old2", last_engaged="2026-02-01")]})
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--pass-c-targets", "1"])
    sc.main()
    out = capsys.readouterr().out
    assert "PASS C TARGETS — 1 of 2" in out
    assert "old " in out and "old2" not in out
