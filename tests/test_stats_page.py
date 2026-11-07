"""Stats (Measure-03): the on-pace line and the metrics by track, with trend lights."""
from release_manager.stats_tracks import change, light_for, sparkline
from release_manager.webapp import app


from release_manager import score_board


def test_change_uses_the_last_reading_before_the_window():
    s = [{"date": "2026-04-01", "value": 100}, {"date": "2026-08-01", "value": 150}, {"date": "2026-09-27", "value": 160}]
    assert change(s) == (10, 57)                      # from 2026-08-01, the last reading at or before 30 days back
    assert change(s[:1]) == (None, 0)


def test_lights_are_trends():
    assert light_for(5, 30, 100)[0] == "green"
    assert light_for(0, 30, 100)[0] == "amber"
    assert light_for(-2, 30, 100)[0] == "red"
    assert light_for(None, 0, None)[0] == "none"
    assert sparkline([{"date": "a", "value": 1}]) == "" and sparkline([{"date": "a", "value": 1}, {"date": "b", "value": 2}])


def test_stats_page_renders_the_score_line_and_every_track():
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert "GREEN" in html and "no data" in html
    for track in ("Instagram", "SoundCloud", "YouTube", "Spotify", "Bandcamp"):
        assert track in html
    assert "stats.js" not in html and "chart.js" not in html


def test_stats_page_renders_the_score_board():
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert 'class="sb-score"' in html and "IG followers" in html and "TikTok followers" in html
    assert "HEALTH" in html and "LADDER" in html and "TREND ONLY" in html
    assert "Growth against the written targets" not in html and "snapshot:instagram.followers</span>" not in html
    assert "collecting" in html
    for track in ("Instagram", "SoundCloud", "YouTube", "Spotify", "Bandcamp"):   # the old grid is still there
        assert track in html
    assert "style.css?v=88" in html
    assert html.count('class="sb-card ') == 9 and "/8" in html
    for row in ("Spotify followers", "Email list", "Release engagement, day 28"):   # D4 rows, 2026-11-05
        assert row in html
    # 2026-11-06: Spotify followers and email list rungs confirmed by Amir; only d28 still carries the badge
    assert html.count('class="sb-badge"') == 1 and ">proposed</span>" in html
    b = score_board.build()
    failing = sum(1 for h in b["health"] if h["ok"] is not True)
    assert html.count('class="sb-dot ') == failing                       # only checks that are not passing get a dot
    assert ("all good" in html) == (failing == 0)


def test_stats_page_survives_a_broken_score_board(monkeypatch):
    from release_manager import score_board

    def boom(*a, **k):
        raise ValueError("metric x: bad rung date")

    monkeypatch.setattr(score_board, "build", boom)
    r = app.test_client().get("/stats")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Score board unavailable: metric x: bad rung date" in html and 'class="sb-error"' in html
    assert 'class="sb-score"' not in html and "TREND ONLY" not in html
    for track in ("Instagram", "SoundCloud", "YouTube", "Spotify", "Bandcamp"):   # the per-track grid
        assert 'class="st-track"' in html and track in html


def test_trends_come_after_this_week_and_before_the_track_grid():
    html = app.test_client().get("/stats").get_data(as_text=True)
    i_ladder, i_trend, i_track = html.index("LADDER"), html.index("TREND ONLY"), html.index('class="st-track"')
    assert i_ladder < i_trend < i_track
    if 'aria-label="This week"' in html:
        assert html.index('aria-label="This week"') < i_trend


def test_details_sit_in_a_closed_all_numbers_fold():
    html = app.test_client().get("/stats").get_data(as_text=True)
    i_fold = html.index('<details class="st-more">')
    assert html.index("LADDER") < i_fold < html.index("TREND ONLY") < html.index('class="st-track"')
    if 'aria-label="This week"' in html:
        assert html.index('aria-label="This week"') < i_fold
    if "Try this week" in html:
        assert html.index("Try this week") > i_fold


def test_top_zone_order_verdict_strip_cards_then_health():
    html = app.test_client().get("/stats").get_data(as_text=True)
    i = [html.index(x) for x in ('class="sb-score"', 'class="sb-strip"', 'class="sb-grid"', "HEALTH", "LADDER")]
    assert i == sorted(i)
    assert 'class="sb-score-head"' in html and "/9 GREEN" in html


def test_freshness_strip_one_chip_per_source_and_red_when_stale():
    from datetime import datetime
    now = datetime(2026, 11, 6, 12, 0)
    fresh = {"label": "IG followers", "as_of_full": "2026-11-06T08:45:10", "age": "3 h", "window": "24 h", "stale": False}
    old = {"label": "IG follow-back", "as_of": "2026-09-01", "age": "66 days", "window": "40 days", "stale": True}
    none = {"label": "TikTok followers", "as_of": None, "age": "", "window": "62 days", "stale": False}
    chips = score_board.freshness_strip([("snapshot:instagram.followers", fresh), ("followback:since_may_pct", old),
                                         ("manual:tiktok.followers", none), ("release:outcomes.x", none)], now)
    assert [c["name"] for c in chips] == ["IG", "IG export", "manual"]          # release files get no chip
    ig, exp, man = chips
    assert ig["stale"] is False and ig["age"] == "3 h" and ig["who"] == "\U0001F916"
    assert exp["stale"] is True and exp["window"] == "40 days" and exp["who"] == "\U0001F383"
    assert man["as_of"] is None and man["who"] == "\U0001F64B"                   # no reading: the chip says collecting
    html = app.test_client().get("/stats").get_data(as_text=True)
    b = score_board.build()
    assert html.count('<li class="sb-chip') == len(b["freshness"])
    assert html.count('class="sb-chip is-stale"') == sum(1 for f in b["freshness"] if f["stale"])


def test_collecting_cards_never_show_a_bare_zero():
    html = app.test_client().get("/stats").get_data(as_text=True)
    b = score_board.build()
    empty = [c for c in b["cards"] if not c["value"]]
    assert html.count("is-collecting") == len(empty)
    assert html.count('class="sb-value sb-value-none">collecting</span>') >= len(empty)
    assert '<span class="sb-value">0<' not in html


def test_skipped_card_says_because(monkeypatch):
    real = score_board.build()

    def fake(*a, **k):
        b = dict(real)
        b["cards"] = [dict(real["cards"][0], skipped="HikerAPI 429")] + real["cards"][1:]
        return b

    monkeypatch.setattr(score_board, "build", fake)
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert '<div class="sb-skip">skipped today, because HikerAPI 429</div>' in html and "is-skipped" in html


def test_jost_comes_from_the_local_font_route():
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent / "release_manager" / "static" / "style.css").read_text(encoding="utf-8")
    assert "url('/fonts/jost-light/file/free/Jost-Variable.ttf')" in css
    import re
    assert not [u for u in re.findall(r"url\('([^']+)'\)", css) if "://" in u]          # no remote font or CDN
    r = app.test_client().get("/fonts/jost-light/file/free/Jost-Variable.ttf")
    assert r.status_code == 200 and r.mimetype == "font/ttf"
