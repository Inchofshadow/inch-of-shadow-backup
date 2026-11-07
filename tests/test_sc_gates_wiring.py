"""SC-01 (2026-09-01): pause/cooldown gates wired into SC entrypoints.

Audit F1: ig_ops_guards shipped an "sc" alias no SC script called. Now:
- sc_engagement API paths call standard_gates("sc") first
- local-only bookkeeping (--log-action / --mark-keep / --plan-unfollows)
  stays exempt, so reality can be recorded during a pause
- sc_weekly_health gates its whole run (all API)
"""
import json
import sys

import pytest

import scene_intelligence.sc_engagement as sc
import scene_intelligence.sc_weekly_health as h
from scene_intelligence.ig_ops_guards import OpsGate, require_not_paused


class _GateTripped(SystemExit):
    pass


def _tripping_gate(platform="sc"):
    raise _GateTripped(6)


def test_engine_api_path_is_gated(monkeypatch):
    monkeypatch.setattr(sc, "_sc_standard_gates", _tripping_gate)
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--dry-run"])
    monkeypatch.setattr(sc, "SC_CLIENT_ID", "x")
    monkeypatch.setattr(sc, "SC_CLIENT_SECRET", "y")
    with pytest.raises(_GateTripped):
        sc.main()


def test_local_bookkeeping_is_exempt(monkeypatch, capsys):
    monkeypatch.setattr(sc, "_sc_standard_gates", _tripping_gate)
    monkeypatch.setattr(sys, "argv",
                        ["sc_engagement.py", "--mark-keep", "--user-id", "0"])
    monkeypatch.setattr(sc, "SC_CLIENT_ID", "x")
    monkeypatch.setattr(sc, "SC_CLIENT_SECRET", "y")
    # gate must NOT trip; the command fails later on the unknown user_id
    with pytest.raises(SystemExit) as e:
        sc.main()
    assert not isinstance(e.value, _GateTripped)
    assert "not found in tracker" in capsys.readouterr().out


def test_health_run_is_gated(monkeypatch):
    monkeypatch.setattr(h, "_standard_gates", _tripping_gate)
    monkeypatch.setattr(sys, "argv", ["sc_weekly_health.py", "--dry-run"])
    with pytest.raises(_GateTripped):
        h.main()


def test_sc_pause_actually_blocks(tmp_path):
    """End-to-end on the gate itself: a pauses.sc entry raises OpsGate."""
    f = tmp_path / "autonomy_state.json"
    f.write_text(json.dumps({"pauses": {"ig": None,
                                        "sc": {"reason": "test", "at": "now"}}}))
    with pytest.raises(OpsGate):
        require_not_paused("sc", f)
    # and an IG-only pause does NOT block SC
    f.write_text(json.dumps({"pauses": {"ig": {"reason": "x"}, "sc": None}}))
    require_not_paused("sc", f)


def test_check_gates_is_local_only_and_prints_a_verdict(monkeypatch, capsys):
    """One command replaces the inline `python3 -c` gate check (2026-09-11):
    inline python cannot be covered by a safe permission rule, so every
    scheduled run stopped for an approval click. It must also be exempt from
    the gates it reports, or a blocked session gets an exception, not an answer."""
    monkeypatch.setattr(sc, "_sc_standard_gates", _tripping_gate)
    monkeypatch.setattr(sc, "SC_CLIENT_ID", "x")
    monkeypatch.setattr(sc, "SC_CLIENT_SECRET", "y")
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--check-gates"])
    sc.main()
    out = capsys.readouterr().out
    for field in ("date:", "cooldown:", "pauses.sc:", "VERDICT:"):
        assert field in out, field
