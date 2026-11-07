import json
from datetime import date

import pytest

from stats.propose_targets import six_month_rate, round5, set_ig_baseline


def test_six_month_rate_matches_the_spec_number():
    s = [{"date": "2026-04-03", "value": 777}, {"date": "2026-07-19", "value": 890}, {"date": "2026-09-26", "value": 948}, {"date": "2026-10-10", "value": 955}]
    assert round(six_month_rate(s, date(2026, 9, 26)), 1) == 29.5
    assert round5(29.5) == 30 and round5(91.75) == 90 and round5(109) == 110


def test_six_month_rate_exclude_and_too_few():
    s = [{"date": "2026-04-03", "value": 777}, {"date": "2026-09-26", "value": 948}]
    assert six_month_rate(s[:1], date(2026, 9, 26)) is None
    assert six_month_rate(s, date(2026, 9, 26), exclude=("2026-09-01", "2026-09-30")) is None


def _targets(tmp_path, end="2026-12-31"):
    p = tmp_path / "targets.json"
    p.write_text(json.dumps({"period": {"start": "2026-11-01", "end": end},
                             "metrics": {"ig_followers": {"label": "x", "kind": "ladder", "baseline": {"value": None, "date": None},
                                                          "rate_per_month": 30, "rungs": {}, "target": None}}}))
    return p


def test_set_ig_baseline_writes_once(tmp_path):
    p = _targets(tmp_path)
    m = set_ig_baseline(950, date(2026, 11, 2), path=p)["metrics"]["ig_followers"]
    assert m["baseline"] == {"value": 950, "date": "2026-11-02"} and m["rungs"] == {"2026-11-30": 980, "2026-12-31": 1010} and m["target"] == 1010
    assert json.loads(p.read_text())["metrics"]["ig_followers"]["target"] == 1010
    with pytest.raises(RuntimeError):
        set_ig_baseline(951, date(2026, 11, 3), path=p)


def test_set_ig_baseline_single_rung_when_month_end_is_period_end(tmp_path):
    p = _targets(tmp_path, end="2026-11-30")
    m = set_ig_baseline(950, date(2026, 11, 2), path=p)["metrics"]["ig_followers"]
    assert m["rungs"] == {"2026-11-30": 980} and m["target"] == 980


def test_set_ig_baseline_guards(tmp_path):
    p = _targets(tmp_path)
    with pytest.raises(ValueError, match="after the period end"):
        set_ig_baseline(950, date(2027, 1, 2), path=p)
    data = json.loads(p.read_text())
    del data["metrics"]["ig_followers"]["rate_per_month"]
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="rate_per_month"):
        set_ig_baseline(950, date(2026, 11, 2), path=p)


def test_earliest_ig_reading_on_or_after_period_start():
    from stats.propose_targets import earliest_ig_reading
    snaps = [  # newest first, as storage.list_snapshots returns them
        {"timestamp": "2026-11-04T08:45:00", "platforms": {"instagram": {"followers": 958}}},
        {"timestamp": "2026-11-03T08:45:00", "platforms": {"youtube": {"subscribers": 3}}},
        {"timestamp": "2026-11-02T14:00:00", "platforms": {"instagram": {"followers": 952}}},
        {"timestamp": "2026-11-02T08:45:00", "platforms": {"instagram": {"followers": 951}}},
        {"timestamp": "2026-10-20T08:45:00", "platforms": {"instagram": {"followers": 940}}},
    ]
    assert earliest_ig_reading(snaps, date(2026, 11, 1)) == (951, date(2026, 11, 2))
    assert earliest_ig_reading(snaps[:2], date(2026, 11, 5)) is None


def test_cli_uses_earliest_reading_and_overrides(tmp_path, monkeypatch):
    import stats.propose_targets as pt
    from stats import storage
    p = _targets(tmp_path)
    calls = []
    monkeypatch.setattr(pt, "load_targets", lambda path=p: json.loads(p.read_text()))
    monkeypatch.setattr(pt, "set_ig_baseline", lambda v, on, path=None: calls.append((v, on)) or
                        {"metrics": {"ig_followers": {"baseline": {"value": v, "date": on.isoformat()}}}})
    monkeypatch.setattr(storage, "list_snapshots", lambda: [
        {"timestamp": "2026-11-05T08:45:00", "platforms": {"instagram": {"followers": 960}}},
        {"timestamp": "2026-11-02T08:45:00", "platforms": {"instagram": {"followers": 951}}}])
    assert pt.main(["--set-ig-baseline"]) == 0
    assert pt.main(["--set-ig-baseline", "--value", "955", "--date", "2026-11-03"]) == 0
    assert calls == [(951, date(2026, 11, 2)), (955, date(2026, 11, 3))]
