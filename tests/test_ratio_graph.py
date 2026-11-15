"""System 98 (Amir 2026-11-11): the evening digest's followers / following graph on RM /stats,
for SoundCloud and Instagram. Spec: memory socials-digest-ratio-graph."""
import re
from datetime import date

from release_manager import ratio_graph
from release_manager.webapp import app


def _snap(stamp, sc=None, ig=None):
    p = {}
    if sc is not None:
        p["soundcloud"] = sc
    if ig is not None:
        p["instagram"] = ig
    return {"timestamp": stamp, "platforms": p}


def test_one_point_per_day_the_last_reading_wins():
    snaps = [
        _snap("2026-09-25T10:00:00", sc={"followers": 1, "following": 1}),        # before 09-26: left out
        _snap("2026-09-26T00:30:12", sc={"followers": 291, "following": 299}),
        _snap("2026-09-26T13:49:48", sc={"followers": 300, "following": 300}),    # same day, later: wins
        _snap("2026-09-27T03:06:52", sc={"skipped": "api down"}),                  # skipped is not a reading
        _snap("2026-09-28T08:45:00", sc={"followers": 310, "following": None}),    # half a reading: out
        _snap("2026-09-29T08:45:00", sc={"followers": 320, "following": 290}),
    ]
    pts = ratio_graph.daily_ratios(snaps, "soundcloud")
    assert [p["date"] for p in pts] == [date(2026, 9, 26), date(2026, 9, 29)]
    assert pts[0]["ratio"] == 1.0 and round(pts[1]["ratio"], 4) == round(320 / 290, 4)
    assert ratio_graph.daily_ratios(snaps, "instagram") == []


def test_targets_are_written_ones_only():
    sc, ig = ratio_graph.TARGETS["soundcloud"], ratio_graph.TARGETS["instagram"]
    assert sc["dec31"] == 1.2 and sc["long"] == (1.4, 1.6) and sc["long_when"] == "Aug 2027"
    assert ig["dec31"] == 1.2 and ig["long_when"] is None        # Amir 2026-11-11: 1.2 by Dec 31; long run has no date


def _pts(*pairs):
    return [{"date": d, "followers": 0, "following": 0, "ratio": r} for d, r in pairs]


def test_the_chart_has_floor_line_and_a_future_target_point():
    pts = _pts((date(2026, 9, 26), 0.97), (date(2026, 9, 27), 1.0), (date(2026, 11, 11), 1.14))
    out = ratio_graph.svg(pts, 1.2, date(2026, 12, 31))
    assert out.count('class="rg-floor"') == 1 and "1:1 floor" in out
    assert "1.14 now" in out and "1.20 Dec 31" in out
    assert out.count('class="rg-path"') == 1 and out.count('class="rg-target"') == 1
    # the target sits at Dec 31, to the right of today: a future point, never a band over the past
    now_x = float(re.search(r'class="rg-now" cx="([\d.]+)"', out).group(1))
    tgt_x = float(re.search(r'class="rg-target" cx="([\d.]+)"', out).group(1))
    assert tgt_x > now_x
    assert "rect" not in out and "<polygon" not in out
    # the line breaks over the gap: 09-26..09-27 is one piece, 11-11 alone is a dot
    assert out.count('class="rg-line"') == 1 and out.count('class="rg-dot"') == 1
    # MM-DD day labels to Dec 31
    assert ">09-26<" in out and ">12-31<" in out and ">10-10<" in out


def test_no_target_means_no_dotted_path():
    pts = _pts((date(2026, 11, 5), 1.0), (date(2026, 11, 6), 0.98))
    out = ratio_graph.svg(pts, None, date(2026, 12, 31))
    assert 'class="rg-path"' not in out and 'class="rg-target"' not in out and "0.98 now" in out


def test_phone_chart_keeps_fewer_day_labels():
    pts = _pts((date(2026, 9, 26), 1.0), (date(2026, 11, 11), 1.1))
    wide = ratio_graph.svg(pts, 1.2, date(2026, 12, 31))
    narrow = ratio_graph.svg(pts, 1.2, date(2026, 12, 31), w=330, h=250, step=28, cls="rg-narrow")
    assert narrow.count('class="rg-xtick"') < wide.count('class="rg-xtick"')
    assert 'viewBox="0 0 330 250"' in narrow


def test_stats_page_shows_both_ratio_graphs():
    html = app.test_client().get("/stats").get_data(as_text=True)
    sec = html.split('id="ratio"', 1)[1].split("</section>", 1)[0]
    assert 'id="ratio-soundcloud"' in sec and 'id="ratio-instagram"' in sec
    assert "by Dec 31" in sec and "by Aug 2027" in sec and "Long run 1.4-1.6:1, no date" in sec
    # Amir 2026-11-12: the Now card in the LADDER look (side column with the big number, graph beside)
    assert sec.count('class="sb-ladder-box rg-box') == 2 and sec.count('class="sb-ladder-now"') == 2
    # Amir 2026-11-12: the section comes right under the OFF PACE line; the score cards stay in their
    # own grid ("nahh its not good when cards under ratio graph")
    assert "sb-card" not in sec
    assert html.index('class="sb-score-head"') < html.index('id="ratio"') < html.index('class="sb-strip"')
    assert html.count('class="sb-card ') == 9                               # every card still once
    ig = sec.split('id="ratio-instagram"', 1)[1]
    assert "1.2:1" in ig and "1.20 Dec 31" in ig and 'class="rg-path"' in ig   # Amir 2026-11-11
    assert sec.count("rg-wide") == 2 and sec.count("rg-narrow") == 2
    assert "<script" not in sec and not re.search(r'(src|href)="https?:', sec)   # drawn locally, nothing loaded from outside
    css = open(app.static_folder + "/style.css", encoding="utf-8").read()
    assert ".rg-floor" in css and "stroke-dasharray" in css.split(".rg-floor", 1)[1].split("}", 1)[0]
    assert ".rg-chart .rg-narrow { display: block; }" in css


def test_stats_page_survives_a_broken_ratio_graph(monkeypatch):
    def boom(*a, **k):
        raise ValueError("bad snapshot")

    monkeypatch.setattr(ratio_graph, "build", boom)
    r = app.test_client().get("/stats")
    assert r.status_code == 200 and "Ratio graphs could not be drawn: bad snapshot" in r.get_data(as_text=True)
