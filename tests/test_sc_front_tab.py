"""--front-tab (2026-09-11): the session brings its own Chrome tab forward.

Proven live on 09-11: Claude-in-Chrome opens every tab in the background,
SoundCloud reports such a tab as hidden and drops its clicks, and an
AppleScript `set active tab index` flips it to visible. The flag must be
local-only (exempt from the gates) and must never let anything but an int
into the script text.
"""
import subprocess
import sys

import pytest

import scene_intelligence.sc_engagement as sc


class _GateTripped(SystemExit):
    pass


def _tripping_gate(platform="sc"):
    raise _GateTripped(6)


def test_front_tab_is_local_only(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(sc, "_sc_standard_gates", _tripping_gate)
    monkeypatch.setattr(sc, "SC_CLIENT_ID", "x")
    monkeypatch.setattr(sc, "SC_CLIENT_SECRET", "y")
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: calls.append(a) or
                        subprocess.CompletedProcess(a, 0, "tab_found: true, was_active: false, was_minimized: false", ""))
    monkeypatch.setattr(sc, "_main_chrome_pid", lambda: None)   # AppleScript path
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--front-tab", "1492906596"])
    sc.main()
    assert len(calls) == 1
    assert calls[0][0][:2] == ["osascript", "-e"]
    assert '"1492906596"' in calls[0][0][2]
    assert "was_active: false" in capsys.readouterr().out


def test_front_tab_rejects_non_integer_ids(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--front-tab", "1; rm -rf /"])
    with pytest.raises(SystemExit) as e:
        sc.main()
    assert e.value.code == 2  # argparse type=int refuses it


def test_front_tab_reports_osascript_failure(monkeypatch, capsys):
    def boom(*a, **k):
        raise OSError("osascript missing")
    monkeypatch.setattr(sc.subprocess, "run", boom)
    sc.front_chrome_tab(42)
    assert "front-tab failed" in capsys.readouterr().out


def test_orphaned_test_chrome_is_closed_and_retried(monkeypatch, capsys):
    """09-30: a leftover test Chrome with no owning session (ppid 1) blocked the
    run; front-tab now closes it and retries once."""
    import signal
    killed, calls = [], []
    replies = iter(["tab_found: false", "tab_found: true, was_active: false, was_minimized: false"])
    monkeypatch.setattr(sc, "_front_tab_osascript", lambda tid: calls.append(tid) or next(replies))
    monkeypatch.setattr(sc, "_stray_automation_chromes", lambda: [("4242", "1")])
    monkeypatch.setattr(sc.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    monkeypatch.setattr(sc.time, "sleep", lambda s: None)
    sc.front_chrome_tab(7)
    out = capsys.readouterr().out
    assert killed == [(4242, signal.SIGTERM)] and len(calls) == 2
    assert "closed orphaned test Chrome" in out and "tab_found: true" in out
    assert "BLOCKED" not in out


def test_live_test_chrome_is_never_killed(monkeypatch, capsys):
    killed = []
    monkeypatch.setattr(sc, "_front_tab_osascript", lambda tid: "tab_found: false")
    monkeypatch.setattr(sc, "_stray_automation_chromes", lambda: [("5151", "900")])
    monkeypatch.setattr(sc.os, "kill", lambda pid, sig: killed.append(pid))
    sc.front_chrome_tab(7)
    out = capsys.readouterr().out
    assert killed == [] and "BLOCKED" in out and "5151" in out


def test_main_chrome_is_addressed_by_pid(monkeypatch, capsys):
    """09-30: the apartment bot's own Chrome (same bundle) captured AppleScript's
    by-name target. The main Chrome is now addressed by PID through JXA."""
    calls = []
    monkeypatch.setattr(sc, "_main_chrome_pid", lambda: 56993)
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: calls.append(a[0]) or
                        subprocess.CompletedProcess(a, 0, "tab_found: true, was_active: false, was_minimized: false", ""))
    sc.front_chrome_tab(1492906596)
    assert calls[0][:3] == ["osascript", "-l", "JavaScript"]
    assert "Application(56993)" in calls[0][4] and '"1492906596"' in calls[0][4]
    assert "tab_found: true" in capsys.readouterr().out


def test_main_chrome_pid_skips_bot_and_helpers(monkeypatch):
    ps = ("  101 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --user-data-dir=/x/.chrome_profile_gewobag --remote-debugging-port=9333\n"
          "  202 /Applications/Google Chrome.app/Contents/Frameworks/x/Google Chrome Helper --type=renderer\n"
          "  303 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n")
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, ps, ""))
    assert sc._main_chrome_pid() == 303
