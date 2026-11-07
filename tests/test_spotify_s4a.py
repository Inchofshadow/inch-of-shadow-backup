"""Weekly Spotify for Artists read: page text in, numbers out. Fixtures are real page texts (2026-10-21)."""

import json
from pathlib import Path

import pytest

from stats import spotify_s4a as s4a

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(s4a, "STORE", tmp_path / "spotify_s4a.json")
    return tmp_path


def test_parse_audience_7_days():
    st = s4a.parse_stats((FIX / "s4a_audience_2026-10-19.txt").read_text())
    assert (st["start"], st["end"]) == ("2026-10-13", "2026-10-19")
    assert st["metrics"] == {"listeners": 65, "monthly_active": 115, "streams": 100, "streams_per_listener": 1.5,
                             "saves": 0, "playlist_adds": 22, "followers": 67}
    assert st["changes_pct"]["streams"] == -27.0 and st["changes_pct"]["followers"] == 3.1


def test_parse_home_top_songs():
    h = s4a.parse_home((FIX / "s4a_home_2026-10-19.txt").read_text())
    assert h["to"] == "10-19" and h["songs"] == [{"title": "Farewell", "streams": 28}, {"title": "Taka Juno", "streams": 18},
                                                 {"title": "The Deceiver", "streams": 17}]


def test_28_day_view_or_a_login_page_is_refused():
    t28 = (FIX / "s4a_audience_2026-10-19.txt").read_text().replace("Oct 13, 2026 - Oct 19, 2026", "Sep 22, 2026 - Oct 19, 2026")
    with pytest.raises(s4a.ParseError, match="not a 7-day period"):
        s4a.parse_stats(t28)
    with pytest.raises(s4a.ParseError):
        s4a.parse_stats("Log in to Spotify for Artists")


def test_save_and_week_pair(store):
    s4a.save_week(s4a.parse_stats((FIX / "s4a_audience_2026-10-12.txt").read_text()))
    s4a.save_week(s4a.parse_stats((FIX / "s4a_audience_2026-10-19.txt").read_text()),
                  s4a.parse_home((FIX / "s4a_home_2026-10-19.txt").read_text()))
    cur, prev = s4a.week_pair("2026-10-20")
    assert cur["end"] == "2026-10-19" and prev["end"] == "2026-10-12" and prev["streams"] == 137
    assert cur["top_songs"][0]["title"] == "Farewell"
    assert s4a.week_pair("2026-10-30") == (None, None)            # no read for that week
    data = json.loads((store / "spotify_s4a.json").read_text())
    assert set(data["weeks"]) == {"2026-10-12", "2026-10-19"}


def test_top_songs_from_another_week_are_not_attached(store):
    home = s4a.parse_home((FIX / "s4a_home_2026-10-19.txt").read_text())
    e = s4a.save_week(s4a.parse_stats((FIX / "s4a_audience_2026-10-12.txt").read_text()), home)
    assert "top_songs" not in e



def test_a_metric_without_a_change_line_is_still_read():
    text = (FIX / "s4a_audience_2026-10-12.txt").read_text().replace("Followers\n65\n1.6%\n", "Followers\n64\n")
    st = s4a.parse_stats(text)
    assert st["metrics"]["followers"] == 64 and "followers" not in st["changes_pct"] and st["metrics"]["streams"] == 137


def test_backfill_weeks_and_months_with_rounded_values(store):
    week = (FIX / "s4a_audience_2026-10-12.txt").read_text()
    month = ("Stats this period\n\nSep 1, 2025 - Sep 30, 2025 · Worldwide\nListeners\n1006\nMonthly active listeners\n225\n"
             "Streams\n2.1K\nStreams / Listener\n2.1\nSaves\n197\nPlaylist adds\n175\nFollowers\n31\n")
    s4a.save_week(s4a.parse_stats(week))
    counts = s4a.save_backfill([week, month])
    assert counts == {"weeks": 0, "months": 1, "skipped": 1}          # a week already stored keeps its own entry
    d = json.loads((store / "spotify_s4a.json").read_text())
    m = d["months"]["2025-09"]
    assert m["streams"] == 2100 and isinstance(m["streams"], int) and m["rounded"] == ["streams"] and m["listeners"] == 1006
    with pytest.raises(s4a.ParseError, match="neither a week nor a month"):
        s4a.save_backfill([month.replace("Sep 1, 2025 - Sep 30, 2025", "Sep 3, 2025 - Sep 20, 2025")])
