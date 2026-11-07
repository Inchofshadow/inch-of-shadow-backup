"""13:00 retry run (2026-10-25): --retry-gate says RUN only when nothing was
logged today; close_loops --rescore lets a successful retry replace the
10:00 run's zero-action score."""
import sys
from datetime import date

import scene_intelligence.close_loops as cl
import scene_intelligence.sc_engagement as sc

TODAY = date.today().isoformat()


def _gates_clear(monkeypatch):
    monkeypatch.setattr(sc, "load_json_checked", lambda *a, **k: {"pauses": {}})
    import scene_intelligence.ig_ops_guards as g
    monkeypatch.setattr(g, "active_detection_cooldown", lambda platform="sc": None)


def _run_retry_gate(monkeypatch, capsys, eng_log):
    monkeypatch.setattr(sc, "load_eng_log", lambda: eng_log)
    monkeypatch.setattr(sys, "argv", ["sc_engagement.py", "--retry-gate"])
    sc.main()
    return capsys.readouterr().out


def test_retry_gate_runs_when_nothing_logged_today(monkeypatch, capsys):
    _gates_clear(monkeypatch)
    out = _run_retry_gate(monkeypatch, capsys, {"log": {}})
    assert "VERDICT:    GO" in out
    assert "today:      follows 0  likes 0  unfollows 0  (0 logged actions)" in out
    assert "RETRY VERDICT: RUN" in out


def test_retry_gate_skips_once_the_morning_run_logged_anything(monkeypatch, capsys):
    _gates_clear(monkeypatch)
    rows = [{"date": TODAY, "platform": "soundcloud", "action": "sc_unfollow"}] * 3
    out = _run_retry_gate(monkeypatch, capsys, {"log": {"x": rows}})
    assert "RETRY VERDICT: SKIP (3 actions logged today" in out


def test_retry_gate_skips_when_gates_say_stop(monkeypatch, capsys):
    monkeypatch.setattr(sc, "load_json_checked",
                        lambda *a, **k: {"pauses": {"sc": {"reason": "test"}}})
    import scene_intelligence.ig_ops_guards as g
    monkeypatch.setattr(g, "active_detection_cooldown", lambda platform="sc": None)
    out = _run_retry_gate(monkeypatch, capsys, {"log": {}})
    assert "VERDICT:    STOP" in out and "RETRY VERDICT: SKIP (gates say STOP)" in out


def test_retry_gate_is_local_only(monkeypatch, capsys):
    class _Tripped(SystemExit):
        pass

    def trip(platform="sc"):
        raise _Tripped(6)
    monkeypatch.setattr(sc, "_sc_standard_gates", trip)
    _gates_clear(monkeypatch)
    out = _run_retry_gate(monkeypatch, capsys, {"log": {}})
    assert "RETRY VERDICT" in out


def test_forget_sc_day_replaces_the_old_score():
    state = {"processed": {"sc": ["2026-10-24", "2026-10-25"], "ig": ["2026-10-25"]},
             "recent": [{"date": "2026-10-25", "platform": "sc", "score": 3, "trend": False},
                        {"date": "2026-10-25", "platform": "ig", "score": 9},
                        {"date": "2026-10-24", "platform": "sc", "score": 10}]}
    cl.forget_sc_day(state, "2026-10-25")
    assert state["processed"]["sc"] == ["2026-10-24"]
    assert state["processed"]["ig"] == ["2026-10-25"]           # IG untouched
    assert [r for r in state["recent"] if r["platform"] == "sc"] == [
        {"date": "2026-10-24", "platform": "sc", "score": 10}]
    cl.forget_sc_day(state, "2026-10-25")                       # idempotent
    assert state["processed"]["sc"] == ["2026-10-24"]
