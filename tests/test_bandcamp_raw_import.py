"""stats/bandcamp_import.parse_bandcamp_raw (BC-01): UTF-16 raw data report, no buyer data out.

Synthetic file only. Column names as in Amir's export of 2026-10-21.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stats import bandcamp_import as bi  # noqa: E402

HEAD = ["date", "paid to", "item type", "item name", "currency", "item price", "additional fan contribution",
        "net amount", "item url", "discount code", "buyer name", "buyer email", "country code", "referrer"]


def write(path: Path, rows: list[list[str]]) -> Path:
    text = "\n".join("\t".join(r) for r in [HEAD] + rows) + "\n"
    path.write_bytes(text.encode("utf-16"))
    return path


def test_parses_sales_skips_payouts_and_buyer_data(tmp_path):
    f = write(tmp_path / "x_bandcamp_raw_data_y.csv", [
        ["9/20/25 5:39am", "Bandcamp", "track", "The Cure", "EUR", "1.50", "0.00", "1.14",
         "https://a.bandcamp.com/track/the-cure", "", "Jane Fan", "jane@example.com", "US",
         "Bandcamp Discover: hypnotic-techno"],
        ["9/22/25 12:00am", "x", "payout", "", "EUR", "", "", "", "", "", "", "", "", ""],
        ["10/6/26 4:33pm", "Bandcamp", "album", "Meltscape", "EUR", "9.00", "1.00", "7.80",
         "https://a.bandcamp.com/album/meltscape?campaign=sc-buy", "", "Bob", "bob@example.com", "DE",
         "campaign: sc-buy"],
    ])
    d = bi.parse_bandcamp_raw(f)
    assert d["total_sales"] == 2 and d["net"] == 8.94 and d["gross"] == 11.5
    assert d["paid_more_count"] == 1
    assert d["first_sale"] == "2025-09-20" and d["last_sale"] == "2026-10-06"
    assert d["by_url"]["https://a.bandcamp.com/album/meltscape"]["count"] == 1   # query string dropped
    assert d["by_campaign"] == {"sc-buy": {"count": 1, "net": 7.8}}
    out = json.dumps(d)
    assert "jane" not in out.lower() and "bob" not in out.lower()


def test_campaign_of():
    assert bi.campaign_of("campaign: yt-desc") == "yt-desc"
    assert bi.campaign_of("Google search") == ""


def test_missing_file_returns_none(tmp_path):
    assert bi.parse_bandcamp_raw(tmp_path / "nope.csv") is None
