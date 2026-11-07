"""Non-session-day merge gate (added after the 2026-07-18 incident).

IG sessions run Mon/Wed/Fri/Sat (SOP 2026-06-01 cadence). A session log
dated any other day (Sun/Tue/Thu) is presumed suspect and the merge refuses
(exit 2) until the artist confirms with --force.
"""
import scene_intelligence.ig_merge_session_log as m


def _stage(monkeypatch, tmp_path, day_iso, content=""):
    monkeypatch.setattr(m, "SI_DIR", tmp_path)
    (tmp_path / f"ig_session_{day_iso}.jsonl").write_text(content)


def test_sunday_session_refused(monkeypatch, tmp_path, capsys):
    _stage(monkeypatch, tmp_path, "2026-07-19")  # Sunday
    assert m.merge("2026-07-19", dry_run=True) == 2
    assert "not an IG session day" in capsys.readouterr().err


def test_tuesday_session_refused(monkeypatch, tmp_path):
    _stage(monkeypatch, tmp_path, "2026-07-21")  # Tuesday
    assert m.merge("2026-07-21", dry_run=True) == 2


def test_off_day_with_force_passes_gate(monkeypatch, tmp_path):
    # empty file -> merge returns 1 AFTER the gate (gate passed via force)
    _stage(monkeypatch, tmp_path, "2026-07-19")
    assert m.merge("2026-07-19", dry_run=True, force=True) == 1


def test_all_session_days_pass_gate(monkeypatch, tmp_path):
    # Mon, Wed, Fri, Sat (2026-07-20/22/24/25); empty file -> 1 after gate
    for d in ("2026-07-20", "2026-07-22", "2026-07-24", "2026-07-25"):
        _stage(monkeypatch, tmp_path, d)
        assert m.merge(d, dry_run=True) == 1
