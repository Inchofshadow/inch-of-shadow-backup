"""get_time_series: newest same-day snapshot wins, manual entries fill days without a value."""
from __future__ import annotations

from datetime import datetime, timedelta

from stats import storage


def _day(offset: int) -> str:
    return (datetime.now() - timedelta(days=offset)).strftime("%Y-%m-%d")


def test_later_same_day_snapshot_with_platform_wins(monkeypatch):
    d = _day(3)
    snaps = [  # newest first, as list_snapshots returns them
        {"timestamp": d + "T14:00:00", "platforms": {"instagram": {"followers": 455}}},
        {"timestamp": d + "T08:45:00", "platforms": {"youtube": {"subscribers": 10}}},
    ]
    monkeypatch.setattr(storage, "list_snapshots", lambda: snaps)
    monkeypatch.setattr(storage, "load_manual_entries", lambda: {"entries": []})
    assert storage.get_time_series("instagram", "followers", 30) == [{"date": d, "value": 455}]


def test_newest_same_day_value_preferred(monkeypatch):
    d = _day(2)
    snaps = [
        {"timestamp": d + "T14:00:00", "platforms": {"instagram": {"followers": 460}}},
        {"timestamp": d + "T08:45:00", "platforms": {"instagram": {"followers": 455}}},
    ]
    monkeypatch.setattr(storage, "list_snapshots", lambda: snaps)
    monkeypatch.setattr(storage, "load_manual_entries", lambda: {"entries": []})
    assert storage.get_time_series("instagram", "followers", 30) == [{"date": d, "value": 460}]


def test_manual_entry_on_day_with_unrelated_snapshot(monkeypatch):
    d = _day(5)
    snaps = [{"timestamp": d + "T08:45:00", "platforms": {"youtube": {"subscribers": 10}}}]
    monkeypatch.setattr(storage, "list_snapshots", lambda: snaps)
    monkeypatch.setattr(storage, "load_manual_entries",
                        lambda: {"entries": [{"platform": "bandcamp", "date": d, "followers": 51}]})
    assert storage.get_time_series("bandcamp", "followers", 30) == [{"date": d, "value": 51}]


def test_snapshot_value_beats_manual_same_day(monkeypatch):
    d = _day(5)
    snaps = [{"timestamp": d + "T08:45:00", "platforms": {"bandcamp": {"followers": 52}}}]
    monkeypatch.setattr(storage, "list_snapshots", lambda: snaps)
    monkeypatch.setattr(storage, "load_manual_entries",
                        lambda: {"entries": [{"platform": "bandcamp", "date": d, "followers": 51}]})
    assert storage.get_time_series("bandcamp", "followers", 30) == [{"date": d, "value": 52}]
