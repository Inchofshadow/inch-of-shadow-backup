"""sc_release_stats.py (2026-09-11): the Friday stats pull as one script."""
import json
from datetime import date, datetime

import scene_intelligence.sc_release_stats as rs


def _release(tmp_path, slug, points):
    f = tmp_path / f"{slug}.json"
    f.write_text(json.dumps({"outcomes": {"stats": {"soundcloud": {
        "timeseries": points}}}}))
    return f


def test_append_backs_up_and_dedups_by_date(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "RELEASES_DIR", tmp_path)
    prev = {"date": "2026-09-04", "plays": 327}
    f = _release(tmp_path, "x", [prev])
    now = datetime(2026, 9, 11, 18, 0, 5)
    point = rs.make_point({"plays": 340, "likes": 18, "reposts": 5,
                           "comments": 5, "downloads": 0},
                          date(2026, 7, 10), now)
    assert point["days_since_release"] == 63

    appended, got_prev = rs.append_point("x", point, now)
    assert appended and got_prev == prev
    series = json.loads(f.read_text())["outcomes"]["stats"]["soundcloud"]["timeseries"]
    assert [p["date"] for p in series] == ["2026-09-04", "2026-09-11"]
    assert len(list(tmp_path.glob("x.bak.*_sc_stats.json"))) == 1

    # a second run the same day writes nothing and makes no second backup
    appended, _ = rs.append_point("x", point, now)
    assert not appended
    assert len(json.loads(f.read_text())["outcomes"]["stats"]["soundcloud"]["timeseries"]) == 2
    assert len(list(tmp_path.glob("x.bak.*_sc_stats.json"))) == 1


def test_no_data_logs_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rs, "RELEASES_DIR", tmp_path)
    for slug, _, _ in rs.TRACKS:
        _release(tmp_path, slug, [])
    calls = []
    monkeypatch.setattr(rs.sc, "sc_client_get",
                        lambda path, params=None: calls.append(params) or None)
    monkeypatch.setattr("sys.argv", ["sc_release_stats.py"])
    rs.main()
    assert len(calls) == len(rs.TRACKS)          # exactly one read per track
    assert "NO DATA" in capsys.readouterr().out
    for slug, _, _ in rs.TRACKS:
        d = json.loads((tmp_path / f"{slug}.json").read_text())
        assert d["outcomes"]["stats"]["soundcloud"]["timeseries"] == []
