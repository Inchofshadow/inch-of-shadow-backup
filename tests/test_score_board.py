from datetime import date, datetime
from release_manager import score_board as sb


def test_build_has_nine_cards_in_targets_order_and_a_score_line():
    b = sb.build(today=date(2026, 11, 15))
    assert [c["key"] for c in b["cards"]] == ["ig_followers", "ig_followback_pct", "ig_reach_30d", "sc_followers", "spotify_monthly_active", "tiktok_followers",
                                              "spotify_followers", "email_list", "release_engagement_d28"]
    assert b["score"]["with_data"] + b["score"]["none"] == 9
    assert b["score"]["line"].startswith(("ON PACE", "OFF PACE", "COLLECTING"))
    assert "/9 GREEN" in b["score"]["line"]
    tiktok = b["cards"][5]
    assert tiktok["light"] == "none" and tiktok["light_text"] == "collecting" and tiktok["progress"] is None


def test_collecting_metric_is_excluded_from_the_score_and_has_no_ladder(monkeypatch):
    t = sb.load_targets()
    t["metrics"]["sc_followers"]["baseline"] = {"value": None, "date": None}
    monkeypatch.setattr(sb, "load_targets", lambda: t)
    b = sb.build(today=date(2026, 11, 15))
    sc = next(c for c in b["cards"] if c["key"] == "sc_followers")
    assert sc["light"] == "none" and "sc_followers" not in [l["key"] for l in b["ladders"]]


def test_missing_platform_in_newest_snapshot_keeps_last_good_reading(monkeypatch):
    series = [{"date": "2026-11-02", "value": 950}]
    monkeypatch.setattr(sb, "series_for", lambda source: series if source.startswith("snapshot:instagram") else [])
    b = sb.build(today=date(2026, 11, 15))
    ig = next(c for c in b["cards"] if c["key"] == "ig_followers")
    assert ig["value"] == "950" and ig["as_of"] == "2026-11-02"


def test_trend_cards():
    t = sb.build(today=date(2026, 11, 15))["trends"]
    assert [x["key"] for x in t] == ["yt_subscribers", "bandcamp_followers"]   # Spotify followers is a target card since D4


def test_health_row_has_eight_checks():
    b = sb.build(today=date(2026, 11, 15))
    h = b["health"]
    assert [x["key"] for x in h] == ["ratio", "session_score", "vetted_pool", "hikerapi_balance", "detections", "snapshot_age", "export_age", "spotify_read_age"]
    assert all(x["ok"] in (True, False, None) for x in h)
    assert all(isinstance(x["detail"], str) and x["detail"] for x in h)
    assert all(x["href"] is None or isinstance(x["href"], str) for x in h)
    assert b["health_summary"]["total"] == 8


def test_ratio_dot_never_prints_a_rounded_pass_that_fails(monkeypatch):
    snaps = [{"timestamp": "2026-11-06T08:45:00", "_filename": "snapshot_2026-11-06T08-45-00.json",
              "platforms": {"instagram": {"followers": 971, "following": 973}}}]
    monkeypatch.setattr(sb.storage, "list_snapshots", lambda: snaps)
    h = {x["key"]: x for x in sb._health(date(2026, 11, 6))}
    assert h["ratio"]["ok"] is False
    assert h["ratio"]["detail"].startswith("971 / 973 = 0.998")      # not "1.00 ... floor 1.0"


def test_health_details_carry_the_as_of_date_and_source(monkeypatch, tmp_path):
    snaps = [{"timestamp": "2026-11-14T08:45:00", "_filename": "snapshot_2026-11-14T08-45-00.json",
              "platforms": {"instagram": {"followers": 951, "following": 970}, "hikerapi": {"requests": 83000}}}]
    monkeypatch.setattr(sb.storage, "list_snapshots", lambda: snaps)
    h = {x["key"]: x for x in sb._health(date(2026, 11, 15))}
    assert h["ratio"]["detail"] == "951 / 970 = 0.980 on 2026-11-14, floor 1.0"
    assert h["ratio"]["href"] == "stats_snapshots/snapshot_2026-11-14T08-45-00.json"
    assert h["hikerapi_balance"]["detail"] == "83,000 on 2026-11-14, min 10,000"
    assert h["snapshot_age"]["detail"] == "27 h, taken 2026-11-14 08:45, max 24 h"   # the one freshness rule, noon of the 15th
    assert h["snapshot_age"]["ok"] is False
    assert h["session_score"]["href"] == "scene_intelligence/autonomy_state.json"
    h = {x["key"]: x for x in sb._health(datetime(2026, 11, 14, 20, 0))}
    assert h["snapshot_age"]["detail"] == "11 h, taken 2026-11-14 08:45, max 24 h" and h["snapshot_age"]["ok"] is True


def test_ladder_svg_contains_the_rungs_and_the_now_dot():
    b = sb.build(today=date(2026, 11, 15))
    sc = next(l for l in b["ladders"] if l["key"] == "sc_followers")
    assert sc["svg"].startswith("<svg") and "510" in sc["svg"] and "600" in sc["svg"]
    if 'class="sb-now"' in sc["svg"]:
        assert " now</text>" in sc["svg"]
    assert sc["light"] == next(c for c in b["cards"] if c["key"] == "sc_followers")["light"]


def _m(light):
    return {"light": light}


def test_score_on_pace_off_pace_and_collecting():
    on = sb._score([_m("green")] * 3 + [_m("none")] * 3)
    assert on["on_pace"] is True and on["line"] == "ON PACE, 3/6 GREEN, 0 DRIFTING, 0 RED, 3 COLLECTING"
    off = sb._score([_m("green"), _m("amber"), _m("red"), _m("red"), _m("none"), _m("none")])
    assert off["on_pace"] is False and off["line"] == "OFF PACE, 1/6 GREEN, 1 DRIFTING, 2 RED, 2 COLLECTING"
    amber_only = sb._score([_m("green"), _m("amber"), _m("none")])
    assert amber_only["on_pace"] is True and amber_only["line"].startswith("ON PACE")
    none = sb._score([_m("none")] * 6)
    assert none["on_pace"] is False and none["with_data"] == 0
    assert none["line"].startswith("COLLECTING, 0/6 GREEN") and none["line"].endswith("6 COLLECTING")


def test_one_red_card_is_off_pace_whatever_the_majority_says():
    """ON PACE can never print next to a red card (the majority rule is gone, M11)."""
    for greens in range(0, 9):
        cards = [_m("green")] * greens + [_m("red")]
        s = sb._score(cards)
        assert s["on_pace"] is False and s["line"].startswith("OFF PACE"), s["line"]
    stale = sb._score([_m("green")] * 5 + [dict(light="red", stale=True, label="IG followers", light_text="stale, 3 days old (window 24 h)")])
    assert stale["line"] == "OFF PACE, 5/6 GREEN, 0 DRIFTING, 1 RED (1 STALE), 0 COLLECTING"
    assert stale["why"] == ["IG followers: stale, 3 days old (window 24 h)"]


SC_M = {"label": "SC", "kind": "ladder", "source": "snapshot:soundcloud.followers",
        "baseline": {"value": 447, "date": "2026-10-31"}, "rungs": {"2026-11-30": 510, "2026-12-31": 600}, "target": 600}
PERIOD = {"start": "2026-11-01", "end": "2026-12-31"}


def test_rung_line_reads_delta_vs_plan_and_distance_to_rung(monkeypatch):
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-15", "value": 475}])
    c = sb._card("sc_followers", SC_M, PERIOD, date(2026, 11, 15))   # plan today 477
    assert c["rung_line"] == "2 behind \u00b7 510 by Nov 30"
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-15", "value": 522}])
    c = sb._card("sc_followers", SC_M, PERIOD, date(2026, 11, 15))
    assert c["rung_line"] == "+45 ahead \u00b7 600 by Dec 31"


def test_bad_points_and_rungs_are_skipped(monkeypatch):
    monkeypatch.setattr(sb, "_one_source", lambda source: [
        {"date": "2026-11-1x", "value": 1}, {"date": "2026-11-10", "value": "n/a"}, {"date": "2026-11-12", "value": 470}])
    assert sb.series_for("snapshot:soundcloud.followers") == [{"date": "2026-11-12", "value": 470}]
    bad = dict(SC_M, rungs={"2026-11-3O": 510, "2026-12-31": 600})
    c = sb._card("sc_followers", bad, PERIOD, date(2026, 11, 15))
    assert c["rung_line"].endswith("600 by Dec 31")
    assert sb.ladder_svg([{"date": "bad", "value": 1}], bad, date(2026, 11, 15), PERIOD).startswith("<svg")


def test_card_says_on_plan_and_dates_only_old_readings(monkeypatch):
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-15", "value": 477}])
    c = sb._card("sc_followers", SC_M, PERIOD, date(2026, 11, 15))   # plan today 477
    assert c["rung_line"] == "on plan \u00b7 510 by Nov 30" and c["old"] is False
    c = sb._card("sc_followers", SC_M, PERIOD, date(2026, 11, 19))
    assert c["old"] is True


def test_card_names_the_next_rung_above_the_reading(monkeypatch):
    sp = dict(SC_M, baseline={"value": 96, "date": "2026-10-30"}, rungs={"2026-11-30": 90, "2026-12-31": 110}, target=110)
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-02", "value": 94}])
    c = sb._card("spotify", sp, PERIOD, date(2026, 11, 2))
    assert c["rung_line"].endswith("110 by Dec 31")
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-02", "value": 700}])
    assert sb._card("sc_followers", SC_M, PERIOD, date(2026, 11, 2))["rung_line"].endswith("target reached")


def test_ladder_now_dot_shows_a_reading_from_just_before_the_period():
    sp = dict(SC_M, baseline={"value": 96, "date": "2026-10-30"}, rungs={"2026-11-30": 90, "2026-12-31": 110}, target=110)
    svg = sb.ladder_svg([{"date": "2026-10-31", "value": 94}], sp, date(2026, 11, 2), PERIOD)
    assert 'class="sb-now"' in svg and "94 now" in svg


# ------------------------------------------------------------ M11 part 1 (2026-11-06)

def test_stale_reading_is_red_with_the_age_and_now_is_a_parameter(monkeypatch):
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-11", "value": 480, "as_of": "2026-11-11T08:45:10",
                                                           "source": "soundcloud_api", "run_id": "sync:2026-11-11T08-45-10"}])
    c = sb._card("sc_followers", SC_M, PERIOD, datetime(2026, 11, 12, 8, 0))      # 23 h: fresh, ahead of plan
    assert c["light"] == "green" and c["stale"] is False and c["old"] is False and c["age"] == "23 h"
    c = sb._card("sc_followers", SC_M, PERIOD, datetime(2026, 11, 15, 12, 0))     # 4 days: stale, red, the age shown
    assert c["light"] == "red" and c["light_text"] == "stale, 4 days old (window 24 h)" and c["old"] is True
    assert c["reading"] == {"value": 480.0, "as_of": "2026-11-11T08:45:10", "source": "soundcloud_api", "run_id": "sync:2026-11-11T08-45-10"}
    assert c["source"] == "soundcloud_api" and c["run_id"] == "sync:2026-11-11T08-45-10" and c["as_of"] == "2026-11-11"
    weekly = dict(SC_M, source="s4a:weeks.followers", cadence="weekly")
    assert sb._card("spotify_followers", weekly, PERIOD, datetime(2026, 11, 15, 12, 0))["stale"] is False   # 4 days inside 10


def test_collecting_card_with_a_stale_reading_stays_grey(monkeypatch):
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-01", "value": 2310}])
    m = {"label": "IG reach, 30d", "kind": "collecting", "source": "manual:instagram_insights.reach_30d", "cadence": "weekly"}
    c = sb._card("ig_reach_30d", m, PERIOD, datetime(2026, 11, 15, 12, 0))
    assert c["light"] == "none" and c["light_text"] == "collecting, last reading 14 days old" and c["stale"] is True
    assert sb._score([c])["line"].startswith("COLLECTING")


def test_card_says_skipped_because_when_the_newest_sync_skipped_its_platform(monkeypatch):
    monkeypatch.setattr(sb, "series_for", lambda source: [{"date": "2026-11-14", "value": 971, "as_of": "2026-11-14T08:45:10"}])
    newest = {"timestamp": "2026-11-15T08:45:10", "platforms": {"instagram": {"skipped": "HikerAPI 429"}, "soundcloud": {"followers": 480}}}
    ig = dict(SC_M, source="snapshot:instagram.followers", baseline={"value": 966, "date": "2026-11-02"}, rungs={"2026-11-30": 996}, target=996)
    c = sb._card("ig_followers", ig, PERIOD, datetime(2026, 11, 15, 10, 0), newest=newest)
    assert c["skipped"] == "HikerAPI 429" and c["value"] == "971" and c["light"] == "red"    # 25 h old: stale, never a 0
    assert sb._card("sc_followers", SC_M, PERIOD, datetime(2026, 11, 15, 10, 0), newest=newest)["skipped"] is None


def test_build_takes_now_and_reads_nothing_after_until(monkeypatch):
    pts = [{"date": "2026-11-10", "value": 470, "as_of": "2026-11-10T08:45:10"}, {"date": "2026-11-20", "value": 500, "as_of": "2026-11-20T08:45:10"}]
    monkeypatch.setattr(sb, "series_for", lambda source: list(pts) if source == "snapshot:soundcloud.followers" else [])
    monkeypatch.setattr(sb, "_health", lambda now: [])
    b = sb.build(now=datetime(2026, 11, 20, 12, 0))
    sc = next(c for c in b["cards"] if c["key"] == "sc_followers")
    assert sc["value"] == "500" and b["now"] == "2026-11-20T12:00:00"
    b = sb.build(now=datetime(2026, 11, 11, 8, 0), until=date(2026, 11, 11))    # 23 h after the 11-10 sync
    sc = next(c for c in b["cards"] if c["key"] == "sc_followers")
    assert sc["value"] == "470" and sc["stale"] is False and sc["age"] == "23 h"
    b = sb.build(now=datetime(2026, 11, 11, 12, 0), until=date(2026, 11, 11))   # 27 h: the same reading is stale
    assert next(c for c in b["cards"] if c["key"] == "sc_followers")["stale"] is True


def test_skipped_block_is_not_a_reading_for_the_health_row():
    snaps = [{"timestamp": "2026-11-15T08:45:10", "_filename": "snapshot_2026-11-15T08-45-10.json",
              "platforms": {"instagram": {"skipped": "HikerAPI 429"}, "hikerapi": {"skipped": "HikerAPI balance call returned nothing"}}},
             {"timestamp": "2026-11-14T08:45:00", "_filename": "snapshot_2026-11-14T08-45-00.json",
              "platforms": {"instagram": {"followers": 951, "following": 970}}}]
    assert sb._newest_with(snaps, "instagram", "followers", "following")[1]["followers"] == 951
    assert sb._newest_with(snaps, "hikerapi", "requests") == (None, None)


# ------------------------------------------------------------ D4 rows (2026-11-05)

def test_d4_rows_read_their_sources_and_carry_the_proposed_flag():
    # Rungs for spotify_followers and email_list were confirmed by Amir on 2026-11-06; d28 still collects.
    b = sb.build(today=date(2026, 11, 5))
    cards = {c["key"]: c for c in b["cards"]}
    sp = cards["spotify_followers"]
    assert sp["value"] == "68" and sp["as_of"] == "2026-10-31" and sp["proposed"] is False    # S4A Monday read
    assert sp["rung_line"] == "2 behind \u00b7 80 by Nov 30" and sp["light"] == "green"
    em = cards["email_list"]
    assert em["value"] == "16" and em["as_of"] == "2026-11-05" and em["proposed"] is False    # manual entry
    assert em["rung_line"] == "on plan \u00b7 30 by Nov 30"
    re_ = cards["release_engagement_d28"]
    assert re_["light"] == "none" and re_["light_text"] == "collecting" and re_["proposed"] is True
    assert re_["value"] == "" and re_["rung_line"] is None                                     # no day-28 read yet
    assert all(c["proposed"] is False for k, c in cards.items() if k != "release_engagement_d28")
    ladders = {l["key"]: l for l in b["ladders"]}
    assert ladders["spotify_followers"]["proposed"] is False and ladders["email_list"]["goal"] == "50"
    assert ladders["sc_followers"]["proposed"] is False and "release_engagement_d28" not in ladders


def test_is_proposed_needs_proposed_by_and_an_unconfirmed_flag():
    assert sb.is_proposed({"proposed_by": "claude", "confirmed": False}) is True
    assert sb.is_proposed({"proposed_by": "claude", "confirmed": True}) is False
    assert sb.is_proposed({"confirmed": False}) is False and sb.is_proposed({}) is False


def test_release_series_reads_one_point_per_release_and_skips_backups(tmp_path):
    (tmp_path / "a-single.json").write_text('{"slug": "a-single", "outcomes": {"stats": {"engagement_d28": {"value": 41, "as_of": "2026-12-20", "parts": {"spotify_saves": 30}}}}}')
    (tmp_path / "b-single.json").write_text('{"slug": "b-single", "outcomes": {"stats": {}}}')                      # no read yet
    (tmp_path / "c-single.json").write_text('{"slug": "c-single", "outcomes": {"stats": {"engagement_d28": {"value": 12, "as_of": "2026-11-28"}}}}')
    (tmp_path / "c-single.bak.20261101.json").write_text('{"slug": "c", "outcomes": {"stats": {"engagement_d28": {"value": 999, "as_of": "2026-11-01"}}}}')
    (tmp_path / "broken.json").write_text("{not json")
    pts = sb._release_series("outcomes.stats.engagement_d28", tmp_path)
    assert [(p["date"], p["value"], p["release"]) for p in pts] == [("2026-12-20", 41, "a-single"), ("2026-11-28", 12, "c-single")]
    last = sb._clean_series(pts)[-1]
    assert (last["date"], last["value"]) == ("2026-12-20", 41)
    assert last["source"] == "release:a-single" and last["as_of"] == "2026-12-20"   # provenance rides along
    assert sb._release_series("outcomes.stats.engagement_d28", tmp_path / "missing") == []


def test_release_source_resolves_through_series_for(monkeypatch):
    monkeypatch.setattr(sb, "RELEASES_DIR", sb.ROOT / "releases")
    assert sb.series_for("release:outcomes.stats.engagement_d28") == []       # no release has a day-28 read tonight
    monkeypatch.setattr(sb, "_release_series", lambda dotted, releases_dir=None: [{"date": "2026-12-20", "value": 41, "release": "x"}])
    assert sb.series_for("release:outcomes.stats.engagement_d28") == [{"date": "2026-12-20", "value": 41}]
