"""stats/freeze.py: a month frozen as of its last day; re-freezing reproduces the numbers;
the score board reads it with build(month=...)."""
import json
from datetime import date, datetime

import pytest

from release_manager import score_board as sb
from stats import freeze

CUTOFF = datetime(2026, 11, 30, 23, 59, 59)
JAN_2 = datetime(2026, 12, 1, 9, 0)

SERIES = {   # one source, with a reading after the cutoff that must never leak into November
    "snapshot:soundcloud.followers": [
        {"date": "2026-11-20", "value": 500, "as_of": "2026-11-20T08:45:10", "source": "soundcloud_api", "run_id": "sync:2026-11-20T08-45-10"},
        {"date": "2026-11-30", "value": 512, "as_of": "2026-11-30T08:45:10", "source": "soundcloud_api", "run_id": "sync:2026-11-30T08-45-10"},
        {"date": "2026-12-01", "value": 530, "as_of": "2026-12-01T08:45:10", "source": "soundcloud_api", "run_id": "sync:2026-12-01T08-45-10"}],
    "snapshot:instagram.followers": [
        {"date": "2026-11-02", "value": 966, "as_of": "2026-11-02T08:45:10", "source": "hikerapi", "run_id": "sync:2026-11-02T08-45-10"}],
}


@pytest.fixture
def board(monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "series_for", lambda source: list(SERIES.get(source, [])))
    monkeypatch.setattr(sb, "_health", lambda now: [])
    monkeypatch.setattr(sb.storage, "load_latest_snapshot", lambda: None)
    monkeypatch.setattr(sb, "GATES_DIR", tmp_path / "gates")
    monkeypatch.setattr(freeze, "GATES_DIR", tmp_path / "gates")
    return tmp_path / "gates"


def test_cutoff_is_the_last_second_of_the_month():
    assert freeze.cutoff_of("2026-11") == CUTOFF and freeze.cutoff_of("2026-02") == datetime(2026, 2, 28, 23, 59, 59)
    with pytest.raises(ValueError):
        freeze.cutoff_of("2026-13")


def test_freeze_reads_nothing_after_the_cutoff_and_writes_every_metric(board):
    doc = freeze.freeze("2026-11", JAN_2, gates_dir=board)
    assert doc["month"] == "2026-11" and doc["as_of"] == "2026-11-30" and doc["cutoff"] == "2026-11-30T23:59:59"
    assert doc["frozen_at"] == "2026-12-01T09:00:00" and doc["run_id"] == "freeze:2026-11:2026-12-01T09-00-00"
    sc = doc["metrics"]["sc_followers"]
    assert sc["raw"] == 512 and sc["as_of"] == "2026-11-30T08:45:10" and sc["run_id"] == "sync:2026-11-30T08-45-10"
    assert sc["light"] == "green" and sc["rung_line"] == "+2 ahead · 600 by Dec 31"
    ig = doc["metrics"]["ig_followers"]
    assert ig["raw"] == 966 and ig["stale"] is True and ig["light"] == "red" and "stale" in ig["light_text"]
    assert doc["score"]["line"].startswith("OFF PACE") and doc["score"]["why"] == ["IG followers: stale, 28 days old (window 24 h)"]
    assert set(doc["metrics"]) >= {"ig_followers", "sc_followers", "tiktok_followers", "yt_subscribers", "bandcamp_followers"}
    assert doc["metrics"]["tiktok_followers"]["raw"] is None and doc["metrics"]["yt_subscribers"]["light"] == "trend"
    assert json.loads((board / "2026-11.json").read_text())["metrics"]["sc_followers"]["raw"] == 512


def test_refreezing_reproduces_the_same_numbers_and_keeps_the_first_file(board):
    first = freeze.freeze("2026-11", JAN_2, gates_dir=board)
    SERIES["snapshot:soundcloud.followers"].append(
        {"date": "2026-12-15", "value": 560, "as_of": "2026-12-15T08:45:10", "source": "soundcloud_api", "run_id": "x"})
    try:
        again = freeze.freeze("2026-11", datetime(2026, 12, 20, 10, 0), gates_dir=board)
        assert again == first                                                     # the file is the record
        forced = freeze.freeze("2026-11", datetime(2026, 12, 20, 10, 0), gates_dir=board, force=True)
        assert freeze.numbers_of(forced) == freeze.numbers_of(first) and forced["frozen_at"] == "2026-12-20T10:00:00"
    finally:
        SERIES["snapshot:soundcloud.followers"].pop()


def test_a_month_that_is_not_over_is_refused(board):
    with pytest.raises(ValueError, match="not over"):
        freeze.freeze("2026-11", datetime(2026, 11, 6, 3, 0), gates_dir=board)
    assert not (board / "2026-11.json").exists()


def test_score_board_reads_the_frozen_month(board):
    with pytest.raises(ValueError, match="no frozen month 2026-11"):
        sb.build(month="2026-11")
    freeze.freeze("2026-11", JAN_2, gates_dir=board)
    b = sb.build(month="2026-11", now=datetime(2027, 3, 1, 12, 0))                # the clock does not matter: frozen
    assert b["frozen"] == {"month": "2026-11", "as_of": "2026-11-30", "frozen_at": "2026-12-01 09:00"}
    cards = {c["key"]: c for c in b["cards"]}
    assert cards["sc_followers"]["value"] == "512" and cards["sc_followers"]["as_of"] == "2026-11-30" and cards["sc_followers"]["light"] == "green"
    assert cards["sc_followers"]["run_id"] == "sync:2026-11-30T08-45-10" and cards["sc_followers"]["stale"] is False
    assert cards["ig_followers"]["light"] == "red" and cards["ig_followers"]["stale"] is True
    assert b["score"]["line"].startswith("OFF PACE") and b["health"] == [] and b["health_summary"]["total"] == 0
    assert b["now"] == "2026-11-30T23:59:59"


def test_cli_prints_and_refuses(board, capsys):
    assert freeze.main([]) == 2
    assert freeze.main(["2026-11", "--print"]) in (0, 1)   # today decides whether November is over
    out = capsys.readouterr().out
    assert "2026-11" in out
