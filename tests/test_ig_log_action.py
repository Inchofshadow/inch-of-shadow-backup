"""IG session logging through one stable command (2026-09-18).

Mirrors sc_engagement.py --log-action so a single wildcard allow rule
covers every line; before this, each raw-shell append was a unique command
string and raised its own permission prompt (the 09-18 session froze ~7h on
four of them).

The tests pin what the merge depends on: real timestamps, an auto sequence
that never drifts, and a refusal when a line would be unusable.
"""
import json

import scene_intelligence.ig_log_action as la


def _lines(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def test_like_line_shape(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "ig_like", "--handle", "@bovaflux",
                    "--track", "reach", "--pre-warm",
                    "--post-url", "https://www.instagram.com/p/X/",
                    "--file", str(p)]) == 0
    rec = _lines(p)[0]
    assert rec["action"] == "ig_like"
    assert rec["handle"] == "bovaflux"  # @ stripped
    assert rec["track"] == "reach"
    assert rec["pre_warm"] is True
    assert rec["post_url"] == "https://www.instagram.com/p/X/"
    assert rec["sequence"] == 1
    assert rec["ts"].endswith(("+02:00", "+01:00"))  # Berlin, DST-proof


def test_sequence_auto_increments_and_survives_gaps(tmp_path):
    p = tmp_path / "s.jsonl"
    for h in ("a", "b"):
        la.main(["--action-type", "ig_like", "--handle", h, "--file", str(p)])
    # a hand-written line with a jumped sequence still sets the ceiling
    p.write_text(p.read_text() + json.dumps({"action": "x", "sequence": 9}) + "\n")
    la.main(["--action-type", "ig_follow", "--handle", "c", "--file", str(p)])
    assert [r["sequence"] for r in _lines(p)] == [1, 2, 9, 10]


def test_follow_carries_source_and_follow_back(tmp_path):
    p = tmp_path / "s.jsonl"
    la.main(["--action-type", "ig_follow", "--handle", "insideoutrec",
             "--track", "reach", "--source", "ombrainternational",
             "--follow-back", "--file", str(p)])
    rec = _lines(p)[0]
    assert rec["source"] == "ombrainternational"
    assert rec["follow_back"] is True


def test_skip_requires_reason(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "ig_skip", "--handle", "x",
                    "--file", str(p)]) == 2
    assert not p.exists()
    assert la.main(["--action-type", "ig_skip", "--handle", "x",
                    "--reason", "all_recent_sponsored", "--tier", "T2",
                    "--category", "label", "--file", str(p)]) == 0
    rec = _lines(p)[0]
    assert rec["reason"] == "all_recent_sponsored"
    assert rec["tier"] == "T2"


def test_vet_needs_the_fields_the_merge_reads(tmp_path):
    p = tmp_path / "s.jsonl"
    # missing bio -> refused (the merge would drop it forever)
    assert la.main(["--action-type", "ig_vet", "--handle", "k",
                    "--followers", "972", "--following", "1698",
                    "--posts", "53", "--public", "--file", str(p)]) == 2
    assert not p.exists()
    assert la.main(["--action-type", "ig_vet", "--handle", "korboira",
                    "--followers", "972", "--following", "1698",
                    "--posts", "53", "--public", "--last-post-days", "41",
                    "--bio", "Producer & Mastering Engineer",
                    "--file", str(p)]) == 0
    rec = _lines(p)[0]
    assert rec["private"] is False
    assert rec["last_post_days"] == 41
    assert rec["bio"] == "Producer & Mastering Engineer"


def test_vet_empty_bio_is_allowed_and_means_fail(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "ig_vet", "--handle", "x",
                    "--followers", "300", "--following", "400", "--posts", "20",
                    "--public", "--bio", "", "--file", str(p)]) == 0
    assert _lines(p)[0]["bio"] == ""


def test_private_vet_needs_no_counts(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "ig_vet", "--handle", "x", "--private",
                    "--file", str(p)]) == 0
    assert _lines(p)[0]["private"] is True


def test_session_halt_needs_reason_and_no_handle(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "session_halt", "--file", str(p)]) == 2
    assert la.main(["--action-type", "session_halt",
                    "--reason", "safety: 22:00 cutoff passed",
                    "--file", str(p)]) == 0
    rec = _lines(p)[0]
    assert rec["track"] == "session"
    assert "handle" not in rec


def test_unknown_action_refused(tmp_path):
    p = tmp_path / "s.jsonl"
    assert la.main(["--action-type", "ig_dm", "--handle", "x",
                    "--file", str(p)]) == 2
    assert not p.exists()


def test_append_never_overwrites(tmp_path):
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps({"action": "ig_like", "sequence": 1}) + "\n")
    la.main(["--action-type", "ig_follow", "--handle", "x", "--file", str(p)])
    assert len(_lines(p)) == 2


# --- ig_session_state.py --gates (2026-09-21) --------------------------------
from datetime import datetime as _dt
from zoneinfo import ZoneInfo as _ZI

import scene_intelligence.ig_session_state as ss

_B = _ZI("Europe/Berlin")


def _gate_env(monkeypatch, tmp_path, pause=None):
    (tmp_path / "autonomy_state.json").write_text(
        json.dumps({"pauses": {"ig": pause, "sc": None}}))
    monkeypatch.setattr(ss, "SI_DIR", tmp_path)
    import scene_intelligence.ig_ops_guards as g
    import scene_intelligence.ig_daily_ledger as dl
    import scene_intelligence.ig_session_confirm as sc
    monkeypatch.setattr(g, "active_detection_cooldown", lambda **k: None)
    monkeypatch.setattr(dl, "runs_on", lambda day: [])
    monkeypatch.setattr(sc, "read_flag", lambda: None)


def test_gates_clear_on_action_day(monkeypatch, tmp_path):
    _gate_env(monkeypatch, tmp_path)
    assert ss.gates(now=_dt(2026, 9, 21, 15, 4, tzinfo=_B)) == 0  # Monday


def test_gates_stop_on_pause(monkeypatch, tmp_path, capsys):
    _gate_env(monkeypatch, tmp_path, pause={"reason": "x"})
    assert ss.gates(now=_dt(2026, 9, 21, 15, 4, tzinfo=_B)) == 3
    assert "pauses.ig is set" in capsys.readouterr().out


def test_gates_stop_on_off_day_and_night(monkeypatch, tmp_path):
    _gate_env(monkeypatch, tmp_path)
    assert ss.gates(now=_dt(2026, 9, 22, 15, 4, tzinfo=_B)) == 3  # Tuesday
    assert ss.gates(now=_dt(2026, 9, 21, 22, 5, tzinfo=_B)) == 3  # after 22:00


def test_gates_stop_when_session_already_ran(monkeypatch, tmp_path):
    # 2026-09-26: "ran" = the day is marked processed (a bare claim is not enough)
    _gate_env(monkeypatch, tmp_path)
    (tmp_path / "autonomy_state.json").write_text(json.dumps(
        {"pauses": {"ig": None, "sc": None}, "processed": {"ig": ["2026-09-21"], "sc": []}}))
    import scene_intelligence.ig_daily_ledger as dl
    monkeypatch.setattr(dl, "runs_on", lambda day: [{"script": "ig_session"}])
    assert ss.gates(now=_dt(2026, 9, 21, 15, 4, tzinfo=_B)) == 3


def test_gate3_zero_click_claim_does_not_block(monkeypatch, tmp_path):
    """2026-09-26: a ledger claim with no clicks (halted run) must not read as
    'ran today'; a processed day or a click in the live log must."""
    _gate_env(monkeypatch, tmp_path)
    import scene_intelligence.ig_daily_ledger as dl
    monkeypatch.setattr(dl, "runs_on", lambda day: [{"script": "ig_session", "kind": "browser"}])
    now = _dt(2026, 9, 26, 15, 45, tzinfo=_B)  # Saturday
    assert ss.gates(now=now) == 0
    (tmp_path / "ig_session_2026-09-26.jsonl").write_text(
        json.dumps({"action": "session_halt"}) + "\n")
    assert ss.gates(now=now) == 0
    (tmp_path / "ig_session_2026-09-26.jsonl").write_text(
        json.dumps({"action": "ig_like", "handle": "x"}) + "\n")
    assert ss.gates(now=now) == 3


def test_ledger_release_claim_browser_only(tmp_path):
    import json as _j
    import scene_intelligence.ig_daily_ledger as dl
    p = tmp_path / "ledger.json"
    p.write_text(_j.dumps({"runs": [
        {"date": "2026-09-26", "script": "ig_session", "kind": "browser"},
        {"date": "2026-09-26", "script": "ig_probe", "kind": "api"},
        {"date": "2026-09-25", "script": "ig_session", "kind": "browser"},
    ]}))
    assert dl.release_claim("ig_session", "2026-09-26", path=p) == 1
    left = _j.loads(p.read_text())["runs"]
    assert [(r["date"], r["script"]) for r in left] == [
        ("2026-09-26", "ig_probe"), ("2026-09-25", "ig_session")]
    assert dl.release_claim("ig_session", "2026-09-26", path=p) == 0
