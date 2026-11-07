"""Tests for the merge-time fabrication guard (the 2026-05-31 CC-fabrication signature)."""
from datetime import datetime, timezone, timedelta

import scene_intelligence.ig_merge_session_log as m


def _epoch(iso):
    return datetime.fromisoformat(iso).timestamp()


def test_parse_ts_offset_and_naive_and_bad():
    assert m._parse_ts("2026-06-10T12:46:33+02:00").utcoffset() == timedelta(hours=2)
    assert m._parse_ts("2026-06-10T12:46:33").tzinfo == timezone.utc  # naive -> assumed UTC
    assert m._parse_ts("not-a-date") is None
    assert m._parse_ts(None) is None


def test_guard_passes_when_file_written_after_events():
    # Real session: events appended as they happen, file mtime at/after last event.
    events = [
        {"ts": "2026-06-10T12:46:33+02:00", "action": "ig_like", "handle": "a"},
        {"ts": "2026-06-10T12:53:08+02:00", "action": "ig_follow", "handle": "a"},
    ]
    mtime = _epoch("2026-06-10T12:53:10+02:00")  # 2s after last event
    ok, detail = m.check_not_fabricated(events, mtime)
    assert ok is True


def test_guard_trips_when_events_postdate_file_mtime():
    # The 2026-05-31 fabrication: file written 10:49, events claim 14:03-15:03.
    events = [
        {"ts": "2026-05-31T14:03:00+02:00", "action": "ig_follow", "handle": "x"},
        {"ts": "2026-05-31T15:03:00+02:00", "action": "ig_follow", "handle": "y"},
    ]
    mtime = _epoch("2026-05-31T10:49:00+02:00")
    ok, detail = m.check_not_fabricated(events, mtime)
    assert ok is False
    assert "FABRICATED" in detail and "AFTER file mtime" in detail


def test_guard_tolerates_small_clock_skew():
    # Last event 90s after mtime -> within the 120s tolerance, allowed.
    events = [{"ts": "2026-06-10T12:00:00+00:00", "action": "ig_follow", "handle": "a"}]
    mtime = _epoch("2026-06-10T11:58:30+00:00")  # 90s before the event
    ok, _ = m.check_not_fabricated(events, mtime)
    assert ok is True
    # But 90s with a 30s tolerance trips it.
    ok2, _ = m.check_not_fabricated(events, mtime, tolerance_s=30)
    assert ok2 is False


def test_guard_skipped_when_no_parseable_timestamps():
    events = [{"action": "ig_follow", "handle": "a"}, {"ts": "bad", "action": "ig_like"}]
    ok, detail = m.check_not_fabricated(events, _epoch("2026-06-10T12:00:00+00:00"))
    assert ok is True and "guard skipped" in detail
