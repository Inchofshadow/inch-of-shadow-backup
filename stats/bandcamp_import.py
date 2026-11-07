"""
stats/bandcamp_import.py
-------------------------
Parse Bandcamp payout CSV exports into structured stats.

Reads the latest CSV from data/bandcamp/ (payout files).
Drop a new export in the same folder -- the latest file is auto-detected.
"""

from __future__ import annotations

import csv
import re
import os
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BANDCAMP_DIR = BASE_DIR / "data" / "bandcamp"


def _find_latest_payout_csv() -> Path | None:
    """Find the most recent Bandcamp payout CSV file."""
    if not BANDCAMP_DIR.exists():
        return None
    csvs = [
        f for f in BANDCAMP_DIR.iterdir()
        if f.suffix == ".csv" and "payout" in f.name.lower()
    ]
    if not csvs:
        return None
    return max(csvs, key=lambda f: f.stat().st_mtime)


def parse_bandcamp_csv(filepath: Path | None = None) -> dict | None:
    """Parse a Bandcamp payout CSV and return structured stats.

    Returns dict with: total_sales, total_revenue, by_track, by_country, by_month, sales list.
    """
    if filepath is None:
        filepath = _find_latest_payout_csv()
    if filepath is None or not filepath.exists():
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception:
        return None

    sales = [r for r in rows if r.get("item type") == "digital"]
    if not sales:
        return None

    total_revenue = 0.0
    total_fees = 0.0
    by_track = defaultdict(lambda: {"count": 0, "revenue": 0.0})
    by_country = defaultdict(int)
    by_month = defaultdict(lambda: {"count": 0, "revenue": 0.0})
    sale_list = []

    for r in rows:
        paid = float(r.get("paid to you", 0) or 0)
        if r.get("item type") == "digital":
            total_revenue += paid
            name = r.get("description", "Unknown")
            by_track[name]["count"] += 1
            by_track[name]["revenue"] += paid
            country = r.get("buyer country", "")
            if country:
                by_country[country] += 1
            month = r.get("item date", "")[:7]
            if month:
                by_month[month]["count"] += 1
                by_month[month]["revenue"] += paid
            sale_list.append({
                "date": r.get("item date", "")[:10],
                "track": name,
                "revenue": round(paid, 2),
                "country": country,
            })
        elif r.get("item type") == "payout fee":
            total_fees += paid

    # Sort sales newest first
    sale_list.sort(key=lambda x: x["date"], reverse=True)

    # Sort and format
    by_track_sorted = dict(
        sorted(by_track.items(), key=lambda x: -x[1]["revenue"])
    )
    for v in by_track_sorted.values():
        v["revenue"] = round(v["revenue"], 2)

    by_country_sorted = dict(
        sorted(by_country.items(), key=lambda x: -x[1])
    )

    by_month_sorted = dict(sorted(by_month.items()))
    for v in by_month_sorted.values():
        v["revenue"] = round(v["revenue"], 2)

    return {
        "total_sales": len(sales),
        "total_revenue": round(total_revenue, 2),
        "total_fees": round(total_fees, 2),
        "net_revenue": round(total_revenue + total_fees, 2),
        "by_track": by_track_sorted,
        "by_country": by_country_sorted,
        "by_month": by_month_sorted,
        "sales": sale_list,
        "csv_file": filepath.name,
    }


# ---------------------------------------------------------------------------
# Raw data report (ticket BC-01, 2026-10-21)
# Tools page > Sales Reports > "Raw data". UTF-16, one row per sale or payout,
# with a "referrer" column: campaign links (?campaign=sc-buy etc.) show there.
# Buyer name, email, phone and ship-to fields are never read.
# ---------------------------------------------------------------------------

SALE_TYPES = ("track", "album")


def _find_latest_raw_csv() -> Path | None:
    if not BANDCAMP_DIR.exists():
        return None
    csvs = [f for f in BANDCAMP_DIR.iterdir() if f.suffix == ".csv" and "raw_data" in f.name.lower()]
    return max(csvs, key=lambda f: f.stat().st_mtime) if csvs else None


def _read_any_csv(filepath: Path) -> list[dict]:
    raw = filepath.read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig")
    first = text.splitlines()[0] if text else ""
    return list(csv.DictReader(text.splitlines(), delimiter="\t" if "\t" in first else ","))


def _sale_date(value: str) -> str:
    """'9/20/25 5:39am' -> '2025-09-20'."""
    from datetime import datetime as _dt
    try:
        return _dt.strptime(value.strip().split(" ")[0], "%m/%d/%y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _num(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def campaign_of(referrer: str) -> str:
    """Campaign name if the referrer is one of our ?campaign= links, else ''."""
    m = re.search(r"campaign[:=\s]+([a-z0-9-]+)", referrer or "", re.I)
    return m.group(1).lower() if m else ""


def parse_bandcamp_raw(filepath: Path | None = None) -> dict | None:
    """Sales from the raw data report: totals, per release URL, referrer, campaign, country, month."""
    filepath = filepath or _find_latest_raw_csv()
    if filepath is None or not filepath.exists():
        return None
    try:
        rows = _read_any_csv(filepath)
    except (OSError, UnicodeDecodeError):
        return None
    sales = []
    for r in rows:
        if r.get("item type") not in SALE_TYPES:
            continue
        referrer = (r.get("referrer") or "").strip()
        sales.append({
            "date": _sale_date(r.get("date", "")),
            "type": r["item type"],
            "item": r.get("item name", ""),
            "url": (r.get("item url") or "").split("?")[0],
            "currency": r.get("currency", ""),
            "price": round(_num(r.get("item price")), 2),
            "paid_extra": round(_num(r.get("additional fan contribution")), 2),
            "net": round(_num(r.get("net amount")), 2),
            "country": r.get("country code", ""),
            "referrer": referrer or "(none)",
            "campaign": campaign_of(referrer),
            "discount_code": r.get("discount code", ""),
        })
    if not sales:
        return None

    def group(key: str) -> dict:
        out: dict = defaultdict(lambda: {"count": 0, "net": 0.0})
        for s in sales:
            out[s[key] or "(none)"]["count"] += 1
            out[s[key] or "(none)"]["net"] += s["net"]
        return {k: {"count": v["count"], "net": round(v["net"], 2)}
                for k, v in sorted(out.items(), key=lambda kv: -kv[1]["net"])}

    for s in sales:
        s["month"] = s["date"][:7]
    sales.sort(key=lambda s: s["date"], reverse=True)
    return {
        "total_sales": len(sales),
        "gross": round(sum(s["price"] + s["paid_extra"] for s in sales), 2),
        "net": round(sum(s["net"] for s in sales), 2),
        "paid_more_count": sum(1 for s in sales if s["paid_extra"] > 0),
        "first_sale": sales[-1]["date"],
        "last_sale": sales[0]["date"],
        "by_url": group("url"),
        "by_referrer": group("referrer"),
        "by_campaign": {k: v for k, v in group("campaign").items() if k != "(none)"},
        "by_country": group("country"),
        "by_month": dict(sorted(group("month").items())),
        "sales": [{k: v for k, v in s.items() if k != "month"} for s in sales],
        "csv_file": filepath.name,
    }
