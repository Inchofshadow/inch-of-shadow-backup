"""stats/registry.py (M11 part 1): one registry over plans/targets.json, parity both ways,
the one freshness rule, the any-red verdict. Every rule takes `now`; no clock, no network."""
from datetime import date, datetime

import pytest

from stats import registry
from stats.targets import load_targets

NOW = datetime(2026, 11, 15, 12, 0)


# ------------------------------------------------------------------ parity

def test_every_targets_metric_has_a_registry_row_and_vice_versa():
    targets = load_targets()
    assert registry.check(targets) == []
    reg = registry.load_registry()
    assert set(registry.targets_only(reg)) == set(targets["metrics"])
    assert set(registry.trends_only(reg)) == set(registry.TRENDS)
    assert list(reg)[:len(targets["metrics"])] == list(targets["metrics"])   # targets order first


def test_a_metric_in_one_place_and_not_the_other_fails():
    targets = load_targets()
    extra = dict(targets, metrics=dict(targets["metrics"], ghost={"label": "Ghost", "kind": "collecting", "source": "manual:x.y"}))
    assert any("ghost is in targets.json but not in" in p for p in registry.check(extra))
    with pytest.raises(ValueError, match="ghost"):
        registry.from_targets(extra, strict=True)
    fewer = dict(targets, metrics={k: v for k, v in targets["metrics"].items() if k != "sc_followers"})
    assert any("sc_followers is in stats/registry.py META but not in targets.json" in p for p in registry.check(fewer))
    bad_source = dict(targets, metrics=dict(targets["metrics"], ig_followers=dict(targets["metrics"]["ig_followers"], source="sheet:x")))
    assert any("source kind 'sheet'" in p for p in registry.check(bad_source))


def test_every_row_says_source_cadence_direction_window_and_pace():
    for key, e in registry.load_registry().items():
        assert e["key"] == key and e["label"] and e["source"]
        assert e["source_kind"] in registry.SOURCE_KINDS
        assert e["cadence"] in registry.CADENCES and e["fresh_hours"] == registry.WINDOW_HOURS[e["cadence"]]
        assert e["direction"] in registry.DIRECTIONS and e["pace"] in registry.PACES and e["area"] in registry.AREAS
    reg = registry.load_registry()
    assert reg["ig_followers"]["cadence"] == "daily" and reg["ig_followers"]["fresh_hours"] == 24
    assert reg["spotify_monthly_active"]["cadence"] == "weekly" and reg["spotify_monthly_active"]["fresh_hours"] == 240
    assert reg["ig_followback_pct"]["cadence"] == "monthly" and reg["email_list"]["cadence"] == "manual"
    assert reg["release_engagement_d28"]["fresh_hours"] is None
    assert reg["sc_followers"]["pace"] == "ladder" and reg["ig_followback_pct"]["pace"] == "floor"
    assert reg["tiktok_followers"]["pace"] == "none" and reg["yt_subscribers"]["pace"] == "trend"
    assert registry.digest_rows(reg) == [("ig_followers", "IG", "instagram"), ("sc_followers", "SC", "soundcloud")]


def test_readers_keep_no_list_of_their_own():
    from release_manager import score_board
    from stats import daily_brief, socials_digest
    assert not hasattr(score_board, "TRENDS") and not hasattr(score_board, "STALE_DAYS")
    assert not hasattr(daily_brief, "SHORT_METRIC")
    assert "ig_followers" not in open(socials_digest.__file__, encoding="utf-8").read().split("def goals_line")[1]


def test_unknown_metric_gets_defaults_from_its_source_when_not_strict():
    e = registry.from_targets({"metrics": {"x": {"kind": "ladder", "source": "s4a:weeks.saves"}}})["x"]
    assert e["label"] == "x" and e["cadence"] == "weekly" and e["pace"] == "ladder" and e["short"] == "x"


# --------------------------------------------------------------- freshness

def test_freshness_is_one_rule_with_now_as_a_parameter():
    fresh = registry.freshness("2026-11-15T08:45:00", "daily", NOW)
    assert fresh["stale"] is False and fresh["age"] == "3 h" and fresh["window"] == "24 h"
    stale = registry.freshness("2026-11-14T08:45:00", "daily", NOW)
    assert stale["stale"] is True and stale["age"] == "27 h"
    assert registry.freshness("2026-11-14T08:45:00", "daily", datetime(2026, 11, 15, 8, 0))["stale"] is False
    assert registry.freshness("2026-11-05", "weekly", NOW)["stale"] is False        # 10 days: at the window, not over it
    assert registry.freshness("2026-11-04", "weekly", NOW) == {"stale": True, "age_hours": 264.0, "age": "11 days", "window": "10 days", "cadence": "weekly"}
    assert registry.freshness("2026-10-10", "monthly", NOW)["stale"] is False       # 36 days under 40
    assert registry.freshness("2026-10-01", "monthly", NOW)["stale"] is True
    assert registry.freshness("2026-09-15", "manual", NOW)["stale"] is False        # 61 days under 62
    assert registry.freshness("2026-09-01", "manual", NOW)["stale"] is True


def test_freshness_unknown_when_no_reading_no_window_or_bad_stamp():
    assert registry.freshness(None, "daily", NOW)["stale"] is None
    assert registry.freshness("2026-11-1x", "daily", NOW)["stale"] is None
    assert registry.freshness("2026-01-01", "none", NOW) == {"stale": None, "age_hours": 7632.0, "age": "318 days", "window": "never stale", "cadence": "none"}
    assert registry.age_hours("2026-11-15", NOW) == 0 and registry.age_hours("2026-11-16", NOW) == 0   # same day or a future date: no age
    assert registry.hours_text(0.5) == "under 1 h" and registry.hours_text(47.9) == "47 h" and registry.hours_text(48) == "2 days"


# ----------------------------------------------------------------- verdict

def test_verdict_any_red_is_off_pace():
    assert registry.verdict([]) == "COLLECTING" and registry.verdict(["none", "none"]) == "COLLECTING"
    assert registry.verdict(["green", "green", "none"]) == "ON PACE"
    assert registry.verdict(["green", "amber"]) == "ON PACE"
    assert registry.verdict(["green"] * 8 + ["red"]) == "OFF PACE"
    assert registry.verdict(["red", "none"]) == "OFF PACE"


# --------------------------------------------------------------- readings

def test_reading_shape_and_skipped_blocks():
    r = registry.reading(971, "2026-11-05T20:17:25", "hikerapi", "sync:2026-11-05T20-17-25")
    assert set(r) == {"value", "as_of", "source", "run_id"}
    assert registry.is_skipped({"skipped": "HikerAPI 429"}) and registry.skipped_reason({"skipped": "HikerAPI 429"}) == "HikerAPI 429"
    assert not registry.is_skipped({"followers": 0}) and registry.skipped_reason(None) is None
    assert registry.source_parts("snapshot:instagram.followers|manual:x.y") == ("snapshot", "instagram.followers")
    assert registry.default_cadence("release:outcomes.stats.engagement_d28") == "none"
    assert isinstance(date.today(), date)
