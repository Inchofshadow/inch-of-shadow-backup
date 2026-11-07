import os
import stat
from datetime import date

import pytest

from stats import ig_token_refresh as t


def _env(tmp_path, body):
    p = tmp_path / ".env"
    p.write_text(body)
    os.chmod(p, 0o600)
    return p


def test_write_token_replaces_only_that_line(tmp_path):
    p = _env(tmp_path, "A=1\nMETA_IG_ACCESS_TOKEN=OLD\nB=2\n")
    t.write_token("NEWTOKEN", p)
    assert p.read_text() == "A=1\nMETA_IG_ACCESS_TOKEN=NEWTOKEN\nB=2\n"
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    assert t.read_token(p) == "NEWTOKEN"


@pytest.mark.parametrize("bad", ["", "a b", "x\ny", '"q"'])
def test_write_token_rejects_bad_values(tmp_path, bad):
    p = _env(tmp_path, "META_IG_ACCESS_TOKEN=OLD\n")
    with pytest.raises(ValueError):
        t.write_token(bad, p)
    assert t.read_token(p) == "OLD"


def test_write_token_needs_exactly_one_line(tmp_path):
    p = _env(tmp_path, "META_IG_ACCESS_TOKEN=A\nMETA_IG_ACCESS_TOKEN=B\n")
    with pytest.raises(ValueError):
        t.write_token("NEW", p)


def test_plan_waits_then_refreshes():
    st = {"issued": "2026-11-03", "expires": "2027-01-02"}
    assert t.plan(st, date(2026, 11, 4)) == ("wait", 1, 59)
    assert t.plan(st, date(2026, 12, 22))[0] == "wait"      # day 49
    assert t.plan(st, date(2026, 12, 23))[0] == "refresh"   # day 50
    assert t.plan({}, date(2026, 11, 4))[0] == "unknown"


def test_mark_issued_uses_expires_in(tmp_path):
    p = tmp_path / "s.json"
    st = t.mark_issued(date(2026, 11, 3), p, expires_in=5184000)  # 60 days
    assert st == {"issued": "2026-11-03", "expires": "2027-01-02"}
    assert t.load_state(p) == st


def test_run_makes_no_call_while_young(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "STATE_PATH", tmp_path / "s.json")
    t.mark_issued(date(2026, 11, 3), t.STATE_PATH)
    monkeypatch.setattr(t, "call_refresh", lambda tok: pytest.fail("no network while young"))
    monkeypatch.setattr(t, "claim", lambda: pytest.fail("no ledger claim while young"))
    assert t.run(date(2026, 11, 10)) == 0


def test_run_retries_tomorrow_when_ledger_refuses(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "STATE_PATH", tmp_path / "s.json")
    monkeypatch.setattr(t, "ENV_PATH", _env(tmp_path, "META_IG_ACCESS_TOKEN=OLD\n"))
    t.mark_issued(date(2026, 9, 1), t.STATE_PATH)
    def refuse():
        raise SystemExit(4)
    monkeypatch.setattr(t, "claim", refuse)
    monkeypatch.setattr(t, "call_refresh", lambda tok: pytest.fail("no call when refused"))
    monkeypatch.setattr(t, "notify", lambda m: None)
    assert t.run(date(2026, 10, 22)) == 0
    assert t.load_state(t.STATE_PATH)["issued"] == "2026-09-01"


def test_run_refreshes_and_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "STATE_PATH", tmp_path / "s.json")
    env = _env(tmp_path, "META_IG_ACCESS_TOKEN=OLD\n")
    monkeypatch.setattr(t, "ENV_PATH", env)
    t.mark_issued(date(2026, 9, 1), t.STATE_PATH)
    monkeypatch.setattr(t, "claim", lambda: None)
    seen = {}
    def fake(tok):
        seen["tok"] = tok
        return {"access_token": "IGAAnew", "token_type": "bearer", "expires_in": 5184000}
    monkeypatch.setattr(t, "call_refresh", fake)
    assert t.run(date(2026, 10, 22)) == 0
    assert seen["tok"] == "OLD"
    assert t.read_token(env) == "IGAAnew"
    assert t.load_state(t.STATE_PATH) == {"issued": "2026-10-22", "expires": "2026-12-21"}


def test_force_refreshes_a_young_token(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "STATE_PATH", tmp_path / "s.json")
    env = _env(tmp_path, "META_IG_ACCESS_TOKEN=OLD\n")
    monkeypatch.setattr(t, "ENV_PATH", env)
    t.mark_issued(date(2026, 11, 3), t.STATE_PATH)
    monkeypatch.setattr(t, "claim", lambda: None)
    monkeypatch.setattr(t, "call_refresh", lambda tok: {"access_token": "IGAAfresh", "expires_in": 5184000})
    assert t.run(date(2026, 11, 4), force=True) == 0
    assert t.read_token(env) == "IGAAfresh"
    assert t.load_state(t.STATE_PATH)["issued"] == "2026-11-04"
