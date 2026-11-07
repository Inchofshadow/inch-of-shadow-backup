"""daily_sync refreshes the follow-back file only when a newer IG export is on disk. No network."""
import json
from pathlib import Path

from stats import daily_sync, ig_followback


def _setup(monkeypatch, tmp_path, export_name, current):
    out = tmp_path / "ig_followback.json"
    if current is not None:
        out.write_text(json.dumps({"export_date": current}))
    monkeypatch.setattr(ig_followback, "OUT", out)
    monkeypatch.setattr(ig_followback, "newest_export_dir", lambda d: Path(export_name) if export_name else None)
    calls = []
    monkeypatch.setattr(ig_followback, "write", lambda *a, **k: calls.append(1) or {})
    return calls


def test_newer_export_rewrites(monkeypatch, tmp_path):
    calls = _setup(monkeypatch, tmp_path, "instagram-inch_of_shadow-2026-11-10-abc", "2026-10-10")
    assert daily_sync.refresh_followback(tmp_path) is True and calls == [1]


def test_same_export_does_not_rewrite(monkeypatch, tmp_path):
    calls = _setup(monkeypatch, tmp_path, "instagram-inch_of_shadow-2026-10-10-abc", "2026-10-10")
    assert daily_sync.refresh_followback(tmp_path) is False and calls == []


def test_missing_file_rewrites(monkeypatch, tmp_path):
    calls = _setup(monkeypatch, tmp_path, "instagram-inch_of_shadow-2026-10-10-abc", None)
    assert daily_sync.refresh_followback(tmp_path) is True and calls == [1]


def test_failure_never_raises(monkeypatch, tmp_path, capsys):
    _setup(monkeypatch, tmp_path, "instagram-inch_of_shadow-2026-11-10-abc", None)

    def boom(*a, **k):
        raise RuntimeError("tracker unreadable")

    monkeypatch.setattr(ig_followback, "write", boom)
    assert daily_sync.refresh_followback(tmp_path) is False
    assert "Follow-back refresh failed" in capsys.readouterr().out
