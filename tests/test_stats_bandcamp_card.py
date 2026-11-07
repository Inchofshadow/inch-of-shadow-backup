"""Stats page Bandcamp sales card (BC-01): builder summary and rendered page."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import stats.bandcamp_import as bi  # noqa: E402
from release_manager import stats_tracks  # noqa: E402

FAKE = {"total_sales": 2, "net": 8.94, "gross": 11.5, "paid_more_count": 1,
        "first_sale": "2025-09-20", "last_sale": "2026-10-06",
        "by_url": {"https://a.bandcamp.com/album/meltscape": {"count": 1, "net": 7.8},
                   "https://a.bandcamp.com/track/meltscape": {"count": 1, "net": 1.14}},
        "by_referrer": {"campaign: sc-buy": {"count": 1, "net": 7.8}, "(none)": {"count": 1, "net": 1.14}},
        "by_campaign": {"sc-buy": {"count": 1, "net": 7.8}}, "csv_file": "x_raw_data.csv", "sales": []}


def test_summary_marks_albums_and_lists_campaigns(monkeypatch):
    monkeypatch.setattr(bi, "parse_bandcamp_raw", lambda *a, **k: FAKE)
    s = stats_tracks.bandcamp_sales()
    assert ("Meltscape (album)", 1, 7.8) in s["releases"] and ("Meltscape", 1, 1.14) in s["releases"]
    assert s["campaigns"] == [("sc-buy", 1, 7.8)] and s["net"] == 8.94


def test_no_report_means_no_card(monkeypatch):
    monkeypatch.setattr(bi, "parse_bandcamp_raw", lambda *a, **k: None)
    assert stats_tracks.bandcamp_sales() is None


def test_stats_page_renders_card(monkeypatch):
    monkeypatch.setattr(bi, "parse_bandcamp_raw", lambda *a, **k: FAKE)
    from release_manager.webapp import app
    app.config["TESTING"] = True
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert "class=\"st-card st-quiet st-sales\"" in html and "Best sellers" in html and "sc-buy" in html and "&euro;8.94" in html
