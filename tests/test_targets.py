from datetime import date

import pytest

from stats.targets import load_targets, ladder_value, light_for_ladder, light_for_floor, progress_pct, current_rung

SC = {"kind": "ladder", "baseline": {"value": 447, "date": "2026-10-31"}, "rungs": {"2026-11-30": 510, "2026-12-31": 600}, "target": 600}
PERIOD = {"start": "2026-11-01", "end": "2026-12-31"}


def test_ladder_is_linear_between_rungs_and_clamped():
    assert ladder_value(SC, PERIOD, date(2026, 11, 1)) == 447
    assert round(ladder_value(SC, PERIOD, date(2026, 11, 30))) == 510
    assert round(ladder_value(SC, PERIOD, date(2026, 11, 15))) == 477        # 447 + 63 * 14/29 rounded
    assert ladder_value(SC, PERIOD, date(2026, 10, 1)) == 447                 # before start: baseline
    assert ladder_value(SC, PERIOD, date(2027, 2, 1)) == 600                  # after end: last rung
    assert ladder_value({"kind": "ladder", "baseline": {"value": None, "date": None}, "rungs": {}, "target": None}, PERIOD, date(2026, 11, 2)) is None


def test_lights_follow_the_95_85_bands():
    assert light_for_ladder(510, 510)[0] == "green"
    assert light_for_ladder(485, 510)[0] == "green"       # 95.1%
    assert light_for_ladder(440, 510)[0] == "amber"       # 86%
    assert light_for_ladder(400, 510)[0] == "red"
    assert light_for_ladder(None, 510) == ("none", "collecting")
    assert light_for_ladder(522, 510)[1] == "+12 past rung"
    assert light_for_ladder(501, 510)[1] == "-9 to rung"


def test_floor_lights():
    assert light_for_floor(23, 20)[0] == "green"
    assert light_for_floor(17, 20)[0] == "amber"
    assert light_for_floor(12, 20)[0] == "red"
    assert light_for_floor(None, 20)[0] == "none"


def test_progress_and_current_rung():
    assert progress_pct(447, 600, 510) == 41
    assert progress_pct(447, 600, 700) == 100 and progress_pct(447, 600, 400) == 0
    assert progress_pct(96, 96, 100) is None
    assert current_rung(SC, date(2026, 11, 15)) == ("2026-11-30", 510)
    assert current_rung(SC, date(2026, 12, 15)) == ("2026-12-31", 600)
    assert current_rung(SC, date(2027, 1, 5)) is None


def test_targets_file_loads_and_validates(tmp_path):
    t = load_targets()
    assert set(t["metrics"]) == {"ig_followers", "ig_followback_pct", "ig_reach_30d", "sc_followers", "spotify_monthly_active", "tiktok_followers",
                                 "spotify_followers", "email_list", "release_engagement_d28"}
    bad = tmp_path / "t.json"
    bad.write_text('{"period": {"start": "2026-11-01", "end": "2026-12-31"}, "metrics": {"x": {"kind": "ladder"}}}')
    with pytest.raises(ValueError, match="x"):
        load_targets(bad)


def test_ladder_anchors_at_a_later_baseline_date():
    ig = {"kind": "ladder", "baseline": {"value": 951, "date": "2026-11-10"},
          "rungs": {"2026-11-30": 981, "2026-12-31": 1011}, "target": 1011}
    assert ladder_value(ig, PERIOD, date(2026, 11, 1)) == 951     # before the baseline date: baseline
    assert ladder_value(ig, PERIOD, date(2026, 11, 10)) == 951    # at the baseline date: the baseline
    assert ladder_value(ig, PERIOD, date(2026, 11, 20)) == 966    # 951 + 30 * 10/20, interpolation starts there
    early = dict(ig, baseline={"value": 951, "date": "2026-10-20"})  # before period start: start anchors
    assert round(ladder_value(early, PERIOD, date(2026, 11, 15)), 2) == round(951 + 30 * 14 / 29, 2)


def test_d4_metrics_are_flagged_proposed_until_amir_confirms(tmp_path):
    t = load_targets()
    for key in ("spotify_followers", "email_list", "release_engagement_d28"):
        m = t["metrics"][key]
        assert m["proposed_by"] == "claude"
    # Amir confirmed the two ladders at the desk on 2026-11-06; d28 has no rung yet, so it stays unconfirmed
    assert t["metrics"]["spotify_followers"]["confirmed"] is True
    assert t["metrics"]["email_list"]["confirmed"] is True
    assert t["metrics"]["release_engagement_d28"]["confirmed"] is False
    assert t["metrics"]["spotify_followers"]["rungs"] == {"2026-11-30": 80, "2026-12-31": 90}
    assert t["metrics"]["email_list"]["rungs"] == {"2026-11-30": 30, "2026-12-31": 50}
    assert t["metrics"]["release_engagement_d28"]["kind"] == "collecting" and "rungs" not in t["metrics"]["release_engagement_d28"]
    assert "outcomes.stats.engagement_d28" in t["metrics"]["release_engagement_d28"]["schema"]["where"]
    bad = tmp_path / "t.json"
    bad.write_text('{"period": {"start": "2026-11-01", "end": "2026-12-31"}, "metrics": {"x": {"kind": "collecting", "label": "x", "proposed_by": "claude"}}}')
    with pytest.raises(ValueError, match="confirmed"):
        load_targets(bad)
