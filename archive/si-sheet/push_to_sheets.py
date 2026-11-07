"""
scene_intelligence/push_to_sheets.py
--------------------------------------
Tool 1 — Scene Intelligence Engine: Google Sheets Publisher

Tabs:
  A&R Targets   — premiere / press / radio channels (not labels)
  Labels        — demo submission targets
  DJs           — producers and DJs
  Venues        — clubs, festivals
  Media         — blogs, podcasts, radio
  Promoters     — party organizers, scene contacts
  Distributors  — distribution platforms
  Platforms     — DSPs and streaming
  All Contacts  — everything

Formatting per tab:
  - Coloured bold header row with white text
  - Frozen header row
  - Column widths tuned for readability
  - Category + Score dropdown menus
  - Clickable hyperlinks on URL columns
  - Filter view on all columns

Usage:
  python3 scene_intelligence/push_to_sheets.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Fix import path when running from project root
sys.path.insert(0, str(Path(__file__).parent))
from utils import CATEGORY_DEFAULT_SCORE, normalize_raw_contacts
try:
    from json_io import atomic_write_json
except ImportError:
    from scene_intelligence.json_io import atomic_write_json

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"
RAW_FILE      = BASE_DIR / "scene_intelligence" / "raw_contacts.json"
PROMO_LOG     = BASE_DIR / "scene_intelligence" / "promotion_log.json"
ENGAGE_LOG    = BASE_DIR / "scene_intelligence" / "engagement_log.json"

load_dotenv(BASE_DIR / ".env")
SHEET_ID   = os.getenv("GOOGLE_SHEETS_ID")
CREDS_FILE = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

BACKUP_DIR = BASE_DIR / "scene_intelligence" / "backups"
MAX_BACKUPS = 25  # keep last 25 backups, delete older ones

# Rate limiter: Google Sheets allows 60 req/min/user.
# We track call timestamps and only sleep when needed.
_api_calls: list[float] = []
_API_LIMIT = 55  # stay under 60
_API_WINDOW = 60.0  # seconds


def _rate_limit() -> None:
    """Sleep only if we're approaching the API rate limit."""
    now = time.time()
    # Remove calls older than the window
    while _api_calls and _api_calls[0] < now - _API_WINDOW:
        _api_calls.pop(0)
    if len(_api_calls) >= _API_LIMIT:
        wait = _api_calls[0] + _API_WINDOW - now + 0.1
        if wait > 0:
            print(f"  [rate limit] waiting {wait:.1f}s...", flush=True)
            time.sleep(wait)
    _api_calls.append(time.time())


# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

HEADERS = [
    "Name", "Delete", "Category", "Type", "Genre", "Location", "Score",
    "Verified", "Demo Email", "Last Active",
    "Notes", "Status", "Priority", "Promo",
    "Source", "URL / Username", "Discogs URL",
    "SoundCloud", "SC Followers",
    "Origin", "YT Subs", "YT Active", "Spotify",
    "Last Engaged", "Campaigns", "Promo Status",
]
STANDARD_WIDTHS = [210, 50, 90, 90, 200, 120, 50, 80, 200, 85, 200, 120, 80, 55, 130, 210, 190, 190, 80, 55, 80, 85, 190, 90, 160, 90]

LABEL_HEADERS = [
    "Name", "Delete", "Category", "Type", "Genre", "Location", "Score",
    "Verified", "Demo Email", "Label Boss", "Last Active",
    "Notes", "Status", "Priority", "Promo",
    "Source", "URL / Username", "Discogs URL",
    "SoundCloud", "SC Followers",
    "Origin", "YT Subs", "YT Active", "Spotify",
    "Last Engaged", "Campaigns", "Promo Status",
]
LABEL_WIDTHS = [210, 50, 90, 90, 200, 120, 50, 80, 200, 160, 85, 200, 120, 80, 55, 130, 210, 190, 190, 80, 55, 80, 85, 190, 90, 160, 90]

DJ_HEADERS = [
    "Name", "Delete", "Category", "Type", "Genre", "Location", "Score",
    "Verified", "Demo Email", "Label Boss", "Last Active",
    "Notes", "Status", "Priority", "Promo",
    "Source", "URL / Username", "IG / SoundCloud", "Labels (ours)",
    "SoundCloud", "SC Followers",
    "Origin", "YT Subs", "YT Active", "Spotify",
    "Last Engaged", "Campaigns", "Promo Status",
]
DJ_WIDTHS = [210, 50, 90, 90, 200, 120, 50, 80, 200, 50, 85, 200, 120, 80, 55, 130, 210, 210, 190, 190, 80, 55, 80, 85, 190, 90, 160, 90]

VENUE_HEADERS = [
    "Name", "Delete", "Category", "Type", "Genre", "Location", "Score",
    "Verified", "Booking / Email", "Last Active",
    "Notes", "Status", "Priority", "Promo",
    "Source", "URL / Username", "IG / SoundCloud", "Booking URL",
    "SoundCloud", "SC Followers",
    "Origin", "YT Subs", "YT Active", "Spotify",
    "Last Engaged", "Campaigns", "Promo Status",
]
VENUE_WIDTHS = [210, 50, 90, 90, 200, 120, 50, 80, 200, 85, 200, 120, 80, 55, 130, 210, 210, 210, 190, 80, 55, 80, 85, 190, 90, 160, 90]

MEDIA_HEADERS = [
    "Name", "Delete", "Category", "Type", "Genre", "Location", "Score",
    "Verified", "Demo Email", "Last Active",
    "Notes", "Status", "Priority", "Promo",
    "Source", "URL / Username", "Discogs URL", "Reach Out",
    "SoundCloud", "SC Followers",
    "Origin", "YT Subs", "YT Active", "Spotify",
    "Last Engaged", "Campaigns", "Promo Status",
]
MEDIA_WIDTHS = [210, 50, 90, 90, 200, 120, 50, 80, 200, 85, 200, 120, 80, 55, 130, 210, 190, 210, 190, 80, 55, 80, 85, 190, 90, 160, 90]

AR_HEADERS = [
    "Name", "Genre Main", "Genre Sub", "Location",
    "Opportunity", "Source", "URL",
    "Score", "Contact Info", "Status", "Priority", "Notes",
]
AR_WIDTHS = [210, 140, 180, 120, 170, 110, 210, 50, 210, 120, 80, 200]

# Dropdown values (synced with utils.CATEGORY_DEFAULT_SCORE keys)
_CATEGORIES = sorted(CATEGORY_DEFAULT_SCORE.keys())
_SUB_TYPES = [
    "booking", "channel", "event", "management", "party",
    "personal", "premiere", "press", "production", "radio", "shop",
]
_SCORES = ["1", "2", "3", "4", "5"]
_PROMO = ["yes"]

# ---------------------------------------------------------------------------
# Visual styles per tab — header colour (dark), RGB 0.0–1.0
# ---------------------------------------------------------------------------

def _rgb(r: float, g: float, b: float) -> dict:
    return {"red": r, "green": g, "blue": b}

_WHITE = _rgb(1.0, 1.0, 1.0)
_LINK_BLUE = _rgb(0.06, 0.33, 0.80)

# Label size row colours (light tints)
_LABEL_BIG   = _rgb(0.85, 0.95, 0.85)   # light green
_LABEL_MID   = _rgb(1.0,  0.97, 0.80)   # light yellow
_LABEL_SMALL = _rgb(1.0,  0.88, 0.88)   # light red
_DJ_BOSS_GOLD = _rgb(1.0,  0.94, 0.70)  # gold for label boss DJs

TAB_STYLES: dict[str, dict] = {
    "A&R Targets":  _rgb(0.10, 0.10, 0.10),
    "Labels":       _rgb(0.13, 0.27, 0.53),
    "DJs":          _rgb(0.35, 0.10, 0.52),
    "Venues":       _rgb(0.10, 0.39, 0.25),
    "Media":        _rgb(0.58, 0.29, 0.04),
    "Promoters":    _rgb(0.50, 0.15, 0.30),
    "Distributors": _rgb(0.22, 0.22, 0.22),
    "Platforms":    _rgb(0.22, 0.22, 0.22),
    "All Contacts": _rgb(0.25, 0.25, 0.25),
}

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_client() -> gspread.Client:
    if not CREDS_FILE.exists():
        print(f"ERROR: credentials file not found — {CREDS_FILE}")
        sys.exit(1)
    if not SHEET_ID:
        print("ERROR: GOOGLE_SHEETS_ID not set in .env")
        sys.exit(1)
    creds = Credentials.from_service_account_file(str(CREDS_FILE), scopes=SCOPES)
    return gspread.authorize(creds)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_contacts() -> tuple[list[dict], bool]:
    if ENRICHED_FILE.exists():
        with open(ENRICHED_FILE, encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Using enriched data: {ENRICHED_FILE.name}")
        return data, True

    if RAW_FILE.exists():
        with open(RAW_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        print(f"  Enriched file not found — falling back to {RAW_FILE.name}")
        return normalize_raw_contacts(raw, extra_fields={"discogs_url": ""}), False

    print("ERROR: Neither enriched_contacts.json nor raw_contacts.json found.")
    print("Run extract_contacts.py first.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Promo & engagement data injection
# ---------------------------------------------------------------------------

_STATUS_RANK = {"charted": 5, "played": 4, "replied": 3, "sent": 2, "rejected": 1, "not_sent": 0}


def inject_promo_engagement(contacts: list[dict]) -> None:
    """Load promotion_log + engagement_log and inject summary fields per contact."""
    # -- Promotion data --
    promo_by_name: dict[str, dict] = {}
    if PROMO_LOG.exists():
        with open(PROMO_LOG, encoding="utf-8") as f:
            promo_data = json.load(f)
        for slug, campaign in promo_data.get("campaigns", {}).items():
            for t in campaign.get("targets", []):
                name = t.get("name", "")
                if not name:
                    continue
                if name not in promo_by_name:
                    promo_by_name[name] = {"campaigns": [], "best_status": "not_sent", "last_sent": ""}
                entry = promo_by_name[name]
                if slug not in entry["campaigns"]:
                    entry["campaigns"].append(slug)
                status = t.get("status", "not_sent")
                if _STATUS_RANK.get(status, 0) > _STATUS_RANK.get(entry["best_status"], 0):
                    entry["best_status"] = status
                sent = t.get("sent_at", "")
                if sent and sent > entry["last_sent"]:
                    entry["last_sent"] = sent

    # -- Engagement data --
    engaged_by_name: dict[str, str] = {}
    if ENGAGE_LOG.exists():
        with open(ENGAGE_LOG, encoding="utf-8") as f:
            engage_data = json.load(f)
        for name, entries in engage_data.get("log", {}).items():
            if name.startswith("@"):
                continue  # skip follow handle keys
            latest = ""
            for e in entries:
                d = e.get("date") or ""
                if d > latest:
                    latest = d
            if latest:
                engaged_by_name[name] = latest

    # -- Inject into contacts --
    injected = 0
    for c in contacts:
        name = c.get("name", "")
        promo = promo_by_name.get(name)
        if promo:
            c["promo_campaigns"] = " / ".join(promo["campaigns"])
            c["promo_latest_status"] = promo["best_status"]
            c["promo_last_sent"] = promo["last_sent"]
            injected += 1
        else:
            c["promo_campaigns"] = ""
            c["promo_latest_status"] = ""
            c["promo_last_sent"] = ""

        # 2026-11-07 Amir "Keep existing dates" (M4 log rotation): the live
        # log holds ~90 days only, so never blank or lower a stored date.
        prev = str(c.get("last_engaged") or "")
        new = engaged_by_name.get(name, "")
        c["last_engaged"] = max(prev, new)

    if injected:
        print(f"  {injected} contacts have promo campaign data")
    eng_count = sum(1 for c in contacts if c.get("last_engaged"))
    if eng_count:
        print(f"  {eng_count} contacts have engagement history")


# ---------------------------------------------------------------------------
# Row serializers
# ---------------------------------------------------------------------------

def _clean_url(url: str) -> str:
    return url.strip() if url else ""


def _build_genre(row: dict) -> str:
    """Build genre string, skipping redundant 'Electronic' prefix."""
    sub = row.get("genre_sub", "")
    if sub:
        return sub
    main = row.get("genre_main", "")
    return main if main and main != "Electronic" else ""


def _profile_link(row: dict) -> str:
    """Best profile link: Instagram > SoundCloud > Bandcamp (enriched data only)."""
    # 1. Enriched Instagram
    ig = (row.get("discogs_instagram") or row.get("musicbrainz_instagram")
          or row.get("wikidata_instagram") or "")
    if ig:
        return ig
    # 2. Instagram source URL
    url = row.get("url", "")
    source = row.get("source", "")
    if "instagram" in source and "instagram.com" in url:
        return url.replace("/_u/", "/")
    # 3. Enriched SoundCloud
    sc = row.get("discogs_soundcloud") or row.get("musicbrainz_soundcloud") or ""
    if sc:
        return sc
    # 4. Discogs website if it's a social link
    website = row.get("discogs_website", "")
    if website:
        wl = website.lower()
        if "instagram.com" in wl or "soundcloud.com" in wl:
            return website
    # 5. Enriched Bandcamp
    return row.get("discogs_bandcamp") or row.get("musicbrainz_bandcamp") or ""


def _origin(source: str) -> str:
    """Return 'You' for user-sourced contacts, 'API' for scraped/discovered, 'Searched' for research."""
    if "research" in source:
        return "Searched"
    api_sources = ("resident_advisor", "spotify_related", "youtube_featured", "youtube_subscriptions", "discogs_label")
    if any(s in source for s in api_sources):
        return "API"
    return "You"


def _extra_cols(row: dict) -> list[str]:
    """SC URL, SC Followers, Origin, YT Subs, YT Active, Spotify URL, Last Engaged, Campaigns, Promo Status."""
    return [
        _clean_url(row.get("soundcloud_url", "")),
        row.get("soundcloud_followers", ""),
        _origin(row.get("source", "")),
        row.get("youtube_subscribers", ""),
        row.get("youtube_last_upload", ""),
        _clean_url(row.get("spotify_url", "")),
        row.get("last_engaged", ""),
        row.get("promo_campaigns", ""),
        row.get("promo_latest_status", ""),
    ]


def to_sheet_row(row: dict) -> list[str]:
    return [
        row.get("name", ""),
        "",  # Delete
        row.get("category", ""),
        row.get("sub_type", ""),
        _build_genre(row),
        row.get("location", ""),
        row.get("match_score", ""),
        row.get("verification_status", "?"),
        row.get("email") or row.get("demo_email") or row.get("discogs_email", ""),
        row.get("discogs_last_year", ""),
        "",  # Notes
        "",  # Status
        "",  # Priority
        row.get("promo_list", ""),
        row.get("source", ""),
        _clean_url(row.get("url", "")),
        _clean_url(row.get("discogs_url", "")),
    ] + _extra_cols(row)


def to_label_row(row: dict) -> list[str]:
    return [
        row.get("name", ""),
        "",  # Delete
        row.get("category", ""),
        row.get("sub_type", ""),
        _build_genre(row),
        row.get("location", ""),
        row.get("match_score", ""),
        row.get("verification_status", "?"),
        row.get("demo_email", "") or row.get("discogs_email", ""),
        row.get("label_boss", ""),
        row.get("discogs_last_year", ""),
        "",  # Notes
        "",  # Status
        "",  # Priority
        row.get("promo_list", ""),
        row.get("source", ""),
        _clean_url(row.get("url", "")),
        _clean_url(row.get("discogs_url", "")),
    ] + _extra_cols(row)


def to_dj_row(row: dict) -> list[str]:
    return [
        row.get("name", ""),
        "",
        row.get("category", ""),
        row.get("sub_type", ""),
        _build_genre(row),
        row.get("location", ""),
        row.get("match_score", ""),
        row.get("verification_status", "?"),
        row.get("discogs_email", ""),
        "X" if row.get("is_label_boss") else "",
        row.get("discogs_last_year", ""),
        "", "", "",
        row.get("promo_list", ""),
        row.get("source", ""),
        _clean_url(row.get("url", "")),
        _clean_url(_profile_link(row)),
        row.get("label_connections", ""),
    ] + _extra_cols(row)


def to_venue_row(row: dict) -> list[str]:
    profile = _profile_link(row)
    booking = (row.get("discogs_official_website") or row.get("musicbrainz_website")
               or row.get("wikidata_website") or "")
    if not booking:
        website = row.get("discogs_website", "")
        if website and not any(s in website.lower() for s in (
            "instagram.com", "facebook.com", "twitter.com",
            "soundcloud.com", "bandcamp.com",
        )):
            booking = website
    return [
        row.get("name", ""),
        "",
        row.get("category", ""),
        row.get("sub_type", ""),
        _build_genre(row),
        row.get("location", ""),
        row.get("match_score", ""),
        row.get("verification_status", "?"),
        row.get("email") or row.get("demo_email") or row.get("discogs_email", ""),
        row.get("discogs_last_year", ""),
        row.get("notes", ""), "", "",
        row.get("promo_list", ""),
        row.get("source", ""),
        _clean_url(row.get("url", "")),
        _clean_url(profile),
        _clean_url(booking) if booking else "",
    ] + _extra_cols(row)


def to_media_row(row: dict) -> list[str]:
    base = to_sheet_row(row)  # 20 items: 16 standard + 4 extra
    url = row.get("url", "")
    source = row.get("source", "")
    ig = (row.get("discogs_instagram") or row.get("musicbrainz_instagram")
          or row.get("wikidata_instagram") or "")
    if ig:
        reach_out = ig
    elif "instagram" in source and "instagram.com" in url:
        reach_out = url.replace("/_u/", "/")
    else:
        reach_out = (row.get("discogs_official_website")
                     or row.get("musicbrainz_website")
                     or row.get("wikidata_website")
                     or row.get("discogs_website")
                     or url)
    # Insert Reach Out after Discogs URL (index 17), before the 4 extra columns
    base.insert(17, _clean_url(reach_out) if reach_out else "")
    return base


_SUB_TYPE_OPPORTUNITY: dict[str, str] = {
    "radio": "Radio / Premiere",
    "premiere": "Premiere",
    "press": "Press",
}


def to_ar_row(row: dict) -> list[str]:
    n = row.get("name", "")
    opp = OPPORTUNITY_MAP.get(n.lower(), "")
    if not opp:
        opp = _SUB_TYPE_OPPORTUNITY.get(row.get("sub_type", ""), "")
    return [
        n,
        row.get("genre_main", ""),
        row.get("genre_sub", ""),
        row.get("location", ""),
        opp,
        row.get("source", ""),
        _clean_url(row.get("url", "")),
        row.get("match_score", ""),
        "", "", "", "",
    ]

# ---------------------------------------------------------------------------
# A&R opportunity map
# ---------------------------------------------------------------------------

OPPORTUNITY_MAP: dict[str, str] = {
    "mintel":                   "Premiere",
    "sinachi":                  "Premiere",
    "positivesource":           "Premiere",
    "disco pastors":            "Premiere / Blog",
    "whitelight/whiteheat":     "Premiere / Blog",
    "themes for great cities":  "Premiere / Blog",
    "stereo society":           "Premiere / Radio",
    "thf radio":                "Radio / Premiere",
    "nts_radio":                "Radio / Premiere",
    "intergalacticfm":          "Radio / Premiere",
    "redlightradio":            "Radio / Premiere",
    "mutantradiotbilisi":       "Radio / Premiere",
    "operator.radio":           "Radio / Premiere",
    "teder.fm":                 "Radio / Premiere",
    "inn7.fm":                  "Radio / Premiere",
    "hopestradio":              "Radio / Premiere",
    "backsideradio_official":   "Radio / Premiere",
    "resident advisor":         "Press / Premiere",
    "resident_advisor":         "Press / Premiere",
    "ra exchange":              "Press / Premiere",
    "inverted audio":           "Press / Premiere",
    "pitchfork":                "Press",
    "brooklynvegan":            "Press",
    "glue.berlin":              "Press / Interview",
    "postpunkonline":           "Press / Blog",
    "synth_history":            "Press / Blog",
    "underscopefeed":           "Press / Blog",
    "whypeopledance":           "Blog / Video",
    "180 fact":                 "Press / Interview",
    "phonica records":          "Record Shop / Consignment",
    "dekmantel":                "Release / Premiere",
    "boiler room":              "Premiere / Live",
}

_AR_SKIP = {
    "samplesfrommars", "productionmusiclive", "sonic academy",
    "point blank music school", "production expert", "pro audio files",
    "pensado's place", "gearspace forum", "waves audio", "sage audio",
    "music theory", "reverb", "stream_informer", "production music live",
}

# ---------------------------------------------------------------------------
# Sheet helpers
# ---------------------------------------------------------------------------

def _get_or_create_ws(
    spreadsheet: gspread.Spreadsheet, title: str, col_count: int
) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        _rate_limit()
        return spreadsheet.add_worksheet(title=title, rows=2000, cols=col_count)


def _build_format_requests(
    spreadsheet: gspread.Spreadsheet,
    sheet_id: int,
    header_bg: dict,
    col_widths: list[int],
    col_count: int,
    row_count: int,
    matrix: list[list[str]],
    link_cols: list[int],
) -> list[dict]:
    """Build ALL formatting requests for a single batch_update call."""
    requests: list[dict] = []

    # 1. Fetch metadata once — clean up old bandings + filter views
    try:
        _rate_limit()
        meta = spreadsheet.fetch_sheet_metadata()
        for sheet in meta.get("sheets", []):
            if sheet["properties"]["sheetId"] == sheet_id:
                for br in sheet.get("bandedRanges", []):
                    requests.append({"deleteBanding": {"bandedRangeId": br["bandedRangeId"]}})
                for fv in sheet.get("filterViews", []):
                    requests.append({"deleteFilterView": {"filterId": fv["filterViewId"]}})
    except Exception:
        pass

    # 2. Column widths
    for i, width in enumerate(col_widths[:col_count]):
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                          "startIndex": i, "endIndex": i + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # 3. Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    })

    # 4. Header formatting — coloured background, bold white text
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": col_count},
            "cell": {"userEnteredFormat": {
                "backgroundColor": header_bg,
                "textFormat": {"bold": True, "fontSize": 13, "foregroundColor": _WHITE},
            }},
            "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat",
        }
    })

    # 5. Data rows — font size 13
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": row_count,
                      "startColumnIndex": 0, "endColumnIndex": col_count},
            "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 13}}},
            "fields": "userEnteredFormat.textFormat.fontSize",
        }
    })

    # 6. Name column bold
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": row_count,
                      "startColumnIndex": 0, "endColumnIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 13}}},
            "fields": "userEnteredFormat.textFormat",
        }
    })

    # 7. Dropdown validation — Category (C=2), Type (D=3), Score (G=6), Promo (N=13)
    for col_idx, values in [(2, _CATEGORIES), (3, _SUB_TYPES), (6, _SCORES), (13, _PROMO)]:
        if col_idx >= col_count:
            continue
        requests.append({
            "setDataValidation": {
                "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": 2000,
                          "startColumnIndex": col_idx, "endColumnIndex": col_idx + 1},
                "rule": {
                    "condition": {"type": "ONE_OF_LIST",
                                  "values": [{"userEnteredValue": v} for v in values]},
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        })

    # 8. Filter view
    requests.append({
        "addFilterView": {
            "filter": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": row_count,
                          "startColumnIndex": 0, "endColumnIndex": col_count},
            }
        }
    })

    # 9. Clickable hyperlinks on URL columns
    for col_idx in link_cols:
        rows_data = []
        for row_idx in range(1, len(matrix)):
            val = matrix[row_idx][col_idx] if col_idx < len(matrix[row_idx]) else ""
            if val and val.startswith(("http://", "https://")):
                rows_data.append({
                    "values": [{"userEnteredFormat": {"textFormat": {
                        "link": {"uri": val},
                        "foregroundColor": _LINK_BLUE,
                        "underline": True,
                    }}}]
                })
            else:
                rows_data.append({"values": [{}]})
        if rows_data:
            requests.append({
                "updateCells": {
                    "rows": rows_data,
                    "range": {"sheetId": sheet_id, "startRowIndex": 1,
                              "endRowIndex": len(matrix),
                              "startColumnIndex": col_idx, "endColumnIndex": col_idx + 1},
                    "fields": "userEnteredFormat.textFormat.link,"
                              "userEnteredFormat.textFormat.foregroundColor,"
                              "userEnteredFormat.textFormat.underline",
                }
            })

    return requests

# ---------------------------------------------------------------------------
# Tab writers
# ---------------------------------------------------------------------------

def _label_size(row: dict) -> str:
    """Classify a label as big/mid/small based on SC followers + Discogs releases."""
    override = row.get("size_override", "")
    if override in ("big", "mid", "small"):
        return override
    def _int(v):
        try: return int(v)
        except (TypeError, ValueError): return 0
    sc = _int(row.get("soundcloud_followers", 0))
    dr = _int(row.get("discogs_releases", 0))
    score = sc + dr * 50
    if score >= 10000:
        return "big"
    elif score >= 2000:
        return "mid"
    return "small"


def _color_label_rows(
    spreadsheet: gspread.Spreadsheet,
    ws_id: int,
    rows: list[dict],
    col_count: int,
) -> None:
    """Apply background colours to label rows based on size."""
    color_map = {"big": _LABEL_BIG, "mid": _LABEL_MID, "small": _LABEL_SMALL}
    reqs = []
    for i, row in enumerate(rows):
        size = _label_size(row)
        bg = color_map[size]
        row_idx = i + 1  # skip header
        reqs.append({
            "repeatCell": {
                "range": {"sheetId": ws_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                          "startColumnIndex": 0, "endColumnIndex": col_count},
                "cell": {"userEnteredFormat": {"backgroundColor": bg}},
                "fields": "userEnteredFormat.backgroundColor",
            }
        })
    if reqs:
        _rate_limit()
        try:
            spreadsheet.batch_update({"requests": reqs})
        except Exception as e:
            print(f"  Warning: label row colouring failed — {e}")


def _color_dj_boss_rows(
    spreadsheet: gspread.Spreadsheet,
    ws_id: int,
    rows: list[dict],
    col_count: int,
) -> None:
    """Apply gold background to DJ rows where is_label_boss=True."""
    reqs = []
    for i, row in enumerate(rows):
        if row.get("is_label_boss"):
            row_idx = i + 1
            reqs.append({
                "repeatCell": {
                    "range": {"sheetId": ws_id, "startRowIndex": row_idx, "endRowIndex": row_idx + 1,
                              "startColumnIndex": 0, "endColumnIndex": col_count},
                    "cell": {"userEnteredFormat": {"backgroundColor": _DJ_BOSS_GOLD}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            })
    if reqs:
        _rate_limit()
        try:
            spreadsheet.batch_update({"requests": reqs})
        except Exception as e:
            print(f"  Warning: DJ boss row colouring failed — {e}")


# Tab config: (headers, widths, row_fn, link_cols)
_TAB_CONFIG = {
    "Labels":    (LABEL_HEADERS, LABEL_WIDTHS, to_label_row, [16, 17, 18, 23]),
    "DJs":       (DJ_HEADERS, DJ_WIDTHS, to_dj_row, [16, 17, 19, 24]),
    "Venues":    (VENUE_HEADERS, VENUE_WIDTHS, to_venue_row, [15, 16, 17, 18, 23]),
    "Media":     (MEDIA_HEADERS, MEDIA_WIDTHS, to_media_row, [15, 16, 17, 18, 23]),
    "Promoters": (HEADERS, STANDARD_WIDTHS, to_sheet_row, [15, 16, 17, 22]),
}


def _split_email_rows(headers: list[str], row: list[str]) -> list[list[str]]:
    """Duplicate a built row into one row per email when the email cell holds
    several comma-separated addresses. Single-email rows pass through as-is."""
    email_idx = next((i for i, h in enumerate(headers) if "email" in h.lower()), None)
    if email_idx is None or email_idx >= len(row):
        return [row]
    cell = row[email_idx] or ""
    emails = [e.strip() for e in cell.split(",") if e.strip()]
    if len(emails) <= 1:
        return [row]
    out = []
    for e in emails:
        dup = list(row)
        dup[email_idx] = e
        out.append(dup)
    return out


def write_tab(
    spreadsheet: gspread.Spreadsheet,
    title: str,
    rows: list[dict],
) -> int:
    header_bg = TAB_STYLES.get(title, TAB_STYLES["All Contacts"])
    headers, widths, row_fn, link_cols = _TAB_CONFIG.get(
        title, (HEADERS, STANDARD_WIDTHS, to_sheet_row, [15, 16, 17, 22])
    )
    col_count = len(headers)

    # 1. Get/create worksheet
    ws = _get_or_create_ws(spreadsheet, title, col_count)

    # 2. Clear old data
    _rate_limit()
    ws.clear()

    # 3. Sort — Labels: by size (big→mid→small) then relevance; others: by relevance
    if title == "Labels":
        _size_order = {"big": 0, "mid": 1, "small": 2}
        rows = sorted(rows, key=lambda r: (_size_order.get(_label_size(r), 2), -r.get("relevance_score", 0), r.get("name", "").lower()))
    else:
        rows = sorted(rows, key=lambda r: (-r.get("relevance_score", 0), r.get("name", "").lower()))

    # 4. Write new data — one row per email (a venue with several booking
    #    addresses is duplicated, one address per row)
    data_rows: list[list[str]] = []
    for r in rows:
        data_rows.extend(_split_email_rows(headers, row_fn(r)))
    matrix = [headers] + data_rows
    _rate_limit()
    # RAW, not USER_ENTERED (audit P2-13): contact-sourced strings must never
    # be interpreted as formulas (a name like "=IMPORTRANGE(...)" would
    # execute). Hyperlinks are applied via batch formatting, not =HYPERLINK.
    ws.update(matrix, "A1", value_input_option="RAW")

    # 4. One batch call for ALL formatting + hyperlinks
    reqs = _build_format_requests(
        spreadsheet, ws.id, header_bg, widths, col_count, len(matrix), matrix, link_cols,
    )
    if reqs:
        _rate_limit()
        try:
            spreadsheet.batch_update({"requests": reqs})
        except Exception as e:
            print(f"  Warning: formatting batch failed for {title} — {e}")

    return len(data_rows)


_AR_SUB_TYPES = {"radio", "premiere", "press"}


def write_ar_tab(spreadsheet: gspread.Spreadsheet, all_rows: list[dict]) -> int:
    ar_rows = []
    for r in all_rows:
        if r.get("category") != "media":
            continue
        name_lower = r.get("name", "").lower()
        if name_lower in _AR_SKIP:
            continue
        sub = r.get("sub_type", "")
        if name_lower in OPPORTUNITY_MAP or sub in _AR_SUB_TYPES or any(
            kw in name_lower
            for kw in ("radio", "blog", "zine", "xlr8r", "mixmag", "djmag")
        ):
            ar_rows.append(r)

    ar_rows.sort(key=lambda r: (-r.get("relevance_score", 0), r.get("name", "").lower()))

    header_bg = TAB_STYLES["A&R Targets"]
    col_count = len(AR_HEADERS)

    ws = _get_or_create_ws(spreadsheet, "A&R Targets", col_count)
    _rate_limit()
    ws.clear()

    matrix = [AR_HEADERS] + [to_ar_row(r) for r in ar_rows]
    _rate_limit()
    # RAW, not USER_ENTERED (audit P2-13): contact-sourced strings must never
    # be interpreted as formulas (a name like "=IMPORTRANGE(...)" would
    # execute). Hyperlinks are applied via batch formatting, not =HYPERLINK.
    ws.update(matrix, "A1", value_input_option="RAW")

    reqs = _build_format_requests(
        spreadsheet, ws.id, header_bg, AR_WIDTHS, col_count, len(matrix), matrix, [6],
    )
    if reqs:
        _rate_limit()
        try:
            spreadsheet.batch_update({"requests": reqs})
        except Exception as e:
            print(f"  Warning: formatting batch failed for A&R — {e}")

    return len(ar_rows)

# ---------------------------------------------------------------------------
# Sync from sheet
# ---------------------------------------------------------------------------

_SYNC_TABS = ["Labels", "DJs", "Venues", "Media", "Promoters", "Distributors", "Platforms", "All Contacts"]


# Last-pushed snapshot (audit P2-12). Written after every successful push;
# sync-back applies a sheet value ONLY when it differs from what we last
# pushed — i.e. a human actually edited the cell. Without this, an SI-side
# edit made between pushes was reverted by the stale sheet value on the
# next sync (the class of bug score_locked was papering over for one field).
SNAPSHOT_FILE = Path(__file__).parent / "sheet_push_snapshot.json"

# Prune safety (audit P2-13): never prune when any sync tab failed to load
# (its contacts would look "deleted"), and never prune more than this many
# contacts in one run without manual review.
MAX_PRUNE_PER_RUN = 25


def _snapshot_fields(c: dict) -> dict:
    """The synced fields, normalized exactly as sync_from_sheet compares them."""
    return {
        "category": str(c.get("category", "")).strip().lower(),
        "sub_type": str(c.get("sub_type", "")).strip().lower(),
        "genre": _build_genre(c).strip(),
        "score": str(c.get("match_score", "")).strip(),
        "promo": "yes" if str(c.get("promo_list", "")).strip().lower() == "yes" else "",
    }


def write_push_snapshot(contacts: list[dict]) -> None:
    atomic_write_json(SNAPSHOT_FILE, {
        c["name"]: _snapshot_fields(c) for c in contacts if c.get("name")
    })


def load_push_snapshot() -> dict:
    if not SNAPSHOT_FILE.exists():
        return {}
    try:
        with open(SNAPSHOT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        print("  WARN: sheet_push_snapshot.json unreadable — syncing without "
              "stale-overwrite protection this run")
        return {}


def sync_from_sheet(
    spreadsheet: gspread.Spreadsheet,
    contacts: list[dict],
    prune_missing: bool = False,
) -> tuple[int, int]:
    """Pull category/score/delete changes from ALL tabs back into data.

    If prune_missing=True, any contact whose name does not appear in ANY
    sheet tab is removed from the local JSON (handles rows physically deleted
    from the sheet).
    """
    by_name: dict[str, dict] = {c.get("name", ""): c for c in contacts}
    changes = 0
    deleted: list[str] = []
    already_synced: set[str] = set()
    # Track every name seen in the sheet (used for prune pass)
    seen_in_sheet: set[str] = set()

    # Duplicate display names collide in by_name — edits would hit the wrong
    # contact and a Delete flag would remove every namesake (audit P2-13).
    # Ambiguous names are skipped entirely; fix them SI-side.
    name_counts = Counter(c.get("name", "") for c in contacts)
    ambiguous = {n for n, k in name_counts.items() if n and k > 1}
    ambiguous_warned: set[str] = set()

    # Stale-overwrite protection (audit P2-12): what the last push wrote.
    snapshot = load_push_snapshot()

    # Tabs that could not be read this run — pruning is unsafe if any tab is
    # missing, because its contacts would all look deleted (audit P2-13).
    tabs_failed: list[str] = []

    for tab_name in _SYNC_TABS:
        try:
            ws = spreadsheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            tabs_failed.append(tab_name)
            continue

        _rate_limit()
        rows = ws.get_all_values()
        if len(rows) < 2:
            tabs_failed.append(tab_name)
            continue

        header = rows[0]
        col_map = {name: i for i, name in enumerate(header)}
        name_idx = col_map.get("Name", 0)
        cat_idx = col_map.get("Category", -1)
        type_idx = col_map.get("Type", -1)
        genre_idx = col_map.get("Genre", -1)
        score_idx = col_map.get("Score", -1)
        promo_idx = col_map.get("Promo", -1)
        delete_idx = col_map.get("Delete", -1)
        ig_idx = col_map.get("IG / SoundCloud", -1)

        for row in rows[1:]:
            if len(row) <= name_idx:
                continue
            name = row[name_idx]
            if name:
                seen_in_sheet.add(name)
            if name not in by_name:
                continue
            if name in ambiguous:
                if name not in ambiguous_warned:
                    print(f"    WARN: '{name}' matches {name_counts[name]} "
                          f"contacts — skipping all sheet edits for it "
                          f"(disambiguate in SI first)")
                    ambiguous_warned.add(name)
                continue
            if tab_name == "All Contacts" and name in already_synced:
                continue
            contact = by_name[name]
            snap = snapshot.get(name, {})

            def _stale(field: str, sheet_val: str) -> bool:
                """True when the sheet still shows what WE last pushed while
                the local value has since changed — a human did not edit the
                cell, so applying it would revert the newer local value."""
                if field not in snap:
                    return False
                if sheet_val != snap[field]:
                    return False  # human edited the cell — apply it
                print(f"    [STALE-SKIP] {name}: {field} sheet value "
                      f"'{sheet_val}' is our own last push; keeping newer "
                      f"local value ({tab_name})")
                return True

            # Delete flag
            if delete_idx >= 0 and len(row) > delete_idx:
                delete_val = row[delete_idx].strip().lower()
                if delete_val in ("x", "yes", "delete", "1"):
                    deleted.append(name)
                    continue

            # Category change
            if cat_idx >= 0 and len(row) > cat_idx:
                sheet_cat = row[cat_idx].strip().lower()
                if (sheet_cat and sheet_cat != contact.get("category", "")
                        and not _stale("category", sheet_cat)):
                    print(f"    {name}: category {contact.get('category')} -> {sheet_cat} ({tab_name})")
                    contact["category"] = sheet_cat
                    changes += 1
                    already_synced.add(name)

            # Sub-type change
            if type_idx >= 0 and len(row) > type_idx:
                sheet_type = row[type_idx].strip().lower()
                if (sheet_type and sheet_type != contact.get("sub_type", "")
                        and not _stale("sub_type", sheet_type)):
                    print(f"    {name}: sub_type {contact.get('sub_type', '')} -> {sheet_type} ({tab_name})")
                    contact["sub_type"] = sheet_type
                    changes += 1
                    already_synced.add(name)

            # Genre change (syncs to genre_sub)
            if genre_idx >= 0 and len(row) > genre_idx:
                sheet_genre = row[genre_idx].strip()
                current_genre = _build_genre(contact)
                if (sheet_genre and sheet_genre != current_genre
                        and not _stale("genre", sheet_genre)):
                    print(f"    {name}: genre '{current_genre}' -> '{sheet_genre}' ({tab_name})")
                    contact["genre_sub"] = sheet_genre
                    changes += 1
                    already_synced.add(name)

            # Score change
            # NOTE 2026-05-06: skip score sync if contact has score_locked=True.
            # User had been making manual SI score edits that kept getting
            # overwritten by stale Sheet values on every sync. The lock flag
            # makes deliberate SI-side score changes durable.
            if score_idx >= 0 and len(row) > score_idx:
                sheet_score = row[score_idx].strip()
                if contact.get("score_locked") is True:
                    # Don't overwrite locked scores. Skip sync for this field.
                    pass
                elif (sheet_score
                        and sheet_score != str(contact.get("match_score", ""))
                        and not _stale("score", sheet_score)):
                    contact["match_score"] = sheet_score
                    changes += 1
                    already_synced.add(name)

            # Promo list change
            if promo_idx >= 0 and len(row) > promo_idx:
                sheet_promo = row[promo_idx].strip().lower()
                current_promo = contact.get("promo_list", "")
                if (sheet_promo in ("yes", "y", "1") and current_promo != "yes"
                        and not _stale("promo", "yes")):
                    contact["promo_list"] = "yes"
                    changes += 1
                    already_synced.add(name)
                elif (sheet_promo in ("", "no", "n", "0") and current_promo == "yes"
                        and not _stale("promo", "")):
                    contact["promo_list"] = ""
                    changes += 1
                    already_synced.add(name)

            # IG handle sync — extract username from IG URL in "IG / SoundCloud" column
            if ig_idx >= 0 and len(row) > ig_idx:
                cell = row[ig_idx].strip()
                if "instagram.com" in cell.lower():
                    # Strip query string and fragment, take path after instagram.com
                    url_clean = cell.split("?", 1)[0].split("#", 1)[0]
                    after = url_clean.lower().split("instagram.com", 1)[1].lstrip("/").rstrip("/")
                    segments = [s for s in after.split("/") if s]
                    # Reject content paths: /p/<id>, /reel/<id>, /tv/<id>, /explore/<…>, etc.
                    NON_HANDLE_PREFIX = {"p", "reel", "reels", "tv", "explore",
                        "stories", "accounts", "about", "directory", "developer",
                        "legal", "privacy", "help"}
                    if segments and segments[0] in NON_HANDLE_PREFIX:
                        segments = []
                    # Skip /_u/ prefix (used by our own pushes)
                    if segments and segments[0] == "_u":
                        segments = segments[1:]
                    handle = segments[0].lstrip("@") if segments else ""
                    # Re-extract from original cell to preserve case (lowercase split was for matching)
                    if handle:
                        idx = cell.lower().find(handle.lower())
                        if idx >= 0:
                            handle = cell[idx:idx + len(handle)]
                    # Validate: IG handles are 2-30 chars, alphanumeric + . _ only
                    valid = (handle and 2 <= len(handle) <= 30
                             and all(ch.isalnum() or ch in "._" for ch in handle))
                    # Don't re-extract a handle that was deliberately cleared
                    was_cleared = bool(contact.get("ig_username_cleared"))
                    current = contact.get("ig_username", "")
                    if valid and handle != current and not was_cleared:
                        print(f"    {name}: ig_username '{current}' -> '{handle}' ({tab_name})")
                        contact["ig_username"] = handle
                        if "instagram.com" not in contact.get("url", ""):
                            contact["url"] = f"https://www.instagram.com/_u/{handle}"
                        changes += 1
                        already_synced.add(name)

    if deleted:
        deleted_set = set(deleted)
        contacts[:] = [c for c in contacts if c.get("name", "") not in deleted_set]
        changes += len(deleted)

    # Prune contacts that are no longer present in any sheet tab.
    # Only removes contacts whose names appeared in the sheet at some point
    # (i.e. the sheet is the source of truth for presence).
    # Contacts that never had a sheet row (e.g. pure Discogs additions with
    # no score) are left alone — identified by having a blank match_score.
    if prune_missing and tabs_failed:
        # A tab that failed to load makes every contact that lives only on
        # that tab look deleted — mass-delete guard (audit P2-13).
        print(f"\n  PRUNE SKIPPED: could not read tab(s) {tabs_failed} — "
              f"pruning with partial sheet data would mass-delete contacts.")
    elif prune_missing and seen_in_sheet:
        pruned = []
        keep = []
        for c in contacts:
            name = c.get("name", "")
            score = str(c.get("match_score", "")).strip()
            # Only prune contacts that had a real score (were reviewed in sheet)
            # and are now absent from all tabs.
            if score and name not in seen_in_sheet and name not in set(deleted):
                pruned.append(name)
            else:
                keep.append(c)
        if len(pruned) > MAX_PRUNE_PER_RUN:
            # Mass-delete guard (audit P2-13): a wrong tab read or renamed
            # column shouldn't be able to wipe a large slice of the DB.
            print(f"\n  PRUNE REFUSED: {len(pruned)} contacts would be pruned "
                  f"(cap {MAX_PRUNE_PER_RUN}/run). First 30:")
            for n in pruned[:30]:
                print(f"    - {n}")
            print("  If this is intentional, prune in batches or raise "
                  "MAX_PRUNE_PER_RUN deliberately.")
        elif pruned:
            print(f"\n  Pruned (deleted from sheet): {len(pruned)}")
            for n in pruned:
                print(f"    - {n}")
            contacts[:] = keep
            changes += len(pruned)

    if changes:
        atomic_write_json(ENRICHED_FILE, contacts)

    return changes, len(deleted)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def backup_contacts() -> str | None:
    """Save a timestamped backup of enriched_contacts.json before pushing."""
    src = ENRICHED_FILE if ENRICHED_FILE.exists() else RAW_FILE
    if not src.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"contacts_{stamp}.json"
    shutil.copy2(src, dst)
    # Prune old backups
    backups = sorted(BACKUP_DIR.glob("contacts_*.json"), key=lambda p: p.name)
    while len(backups) > MAX_BACKUPS:
        try:
            backups.pop(0).unlink()
        except OSError:
            break  # sandbox may not have delete permission; leave old backups
    return dst.name


def main() -> None:
    print("\nScene Intelligence — Google Sheets Publisher")
    print("=" * 46)

    backup_name = backup_contacts()
    if backup_name:
        print(f"  Backup saved: backups/{backup_name}")

    all_rows, is_enriched = load_contacts()
    enriched_count = sum(1 for r in all_rows if r.get("discogs_found"))
    print(f"  {len(all_rows)} total contacts loaded")
    if is_enriched:
        print(f"  {enriched_count} contacts have Discogs enrichment data")

    # Inject promo & engagement data into contacts
    inject_promo_engagement(all_rows)
    # Save enriched contacts with promo/engagement fields
    atomic_write_json(ENRICHED_FILE, all_rows)

    print("  Connecting to Google Sheets...")
    client      = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"  Connected: '{spreadsheet.title}'")

    # Sync manual edits from sheet before overwriting
    if "--no-sync" in sys.argv:
        print("  Skipping sync (--no-sync)")
    else:
        prune = "--prune-deleted" in sys.argv
        print("  Syncing changes from sheet..." + (" (prune mode)" if prune else ""))
        edits, deletes = sync_from_sheet(spreadsheet, all_rows, prune_missing=prune)
        if edits or deletes:
            print(f"  Synced: {edits - deletes} edits, {deletes} deletions")
            print(f"  {len(all_rows)} contacts after sync")
        else:
            print("  No manual changes detected")
    print()

    tabs = [
        ("A&R Targets",  None),
        ("Labels",       lambda r: r.get("category") == "label"),
        ("DJs",          lambda r: r.get("category") in ("dj", "artist", "personal")),
        ("Venues",       lambda r: r.get("category") == "venue"),
        ("Media",        lambda r: r.get("category") == "media"),
        ("Promoters",    lambda r: r.get("category") == "promoter"),
        ("Distributors", lambda r: r.get("category") == "distributor"),
        ("Platforms",    lambda r: r.get("category") == "platform"),
        ("All Contacts", lambda r: True),
    ]

    t0 = time.time()
    for tab_title, filter_fn in tabs:
        if tab_title == "A&R Targets":
            count = write_ar_tab(spreadsheet, all_rows)
            print(f"  {'A&R Targets':<16} {count:>4} rows  (premiere / press / radio)")
        else:
            filtered = [r for r in all_rows if filter_fn(r)]
            count    = write_tab(spreadsheet, tab_title, filtered)
            # Colour label rows by size: green=big, yellow=mid, red=small
            if tab_title == "Labels":
                _size_order = {"big": 0, "mid": 1, "small": 2}
                sorted_labels = sorted(filtered, key=lambda r: (_size_order.get(_label_size(r), 2), -r.get("relevance_score", 0), r.get("name", "").lower()))
                headers = _TAB_CONFIG.get(tab_title, (HEADERS, STANDARD_WIDTHS, to_sheet_row, [15, 16, 17, 22]))[0]
                ws = _get_or_create_ws(spreadsheet, tab_title, len(headers))
                _color_label_rows(spreadsheet, ws.id, sorted_labels, len(headers))
            # Colour label boss DJs in gold
            if tab_title == "DJs":
                sorted_djs = sorted(filtered, key=lambda r: (-r.get("relevance_score", 0), r.get("name", "").lower()))
                dj_headers = _TAB_CONFIG["DJs"][0]
                ws = _get_or_create_ws(spreadsheet, tab_title, len(dj_headers))
                _color_dj_boss_rows(spreadsheet, ws.id, sorted_djs, len(dj_headers))
            print(f"  {tab_title:<16} {count:>4} rows")

    # Generate label_tiers.json
    _generate_label_tiers(all_rows)

    # Record what this push wrote, so the next sync-back can tell a human
    # sheet edit from our own stale value (audit P2-12).
    write_push_snapshot(all_rows)

    elapsed = time.time() - t0
    print(f"\n{'=' * 46}")
    print(f"  Sheet updated in {elapsed:.0f}s: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print()


def _generate_label_tiers(all_rows: list[dict]) -> None:
    """Write label_tiers.json — auto-synced every push."""
    def _int(v):
        try: return int(v)
        except (TypeError, ValueError): return 0

    labels = [r for r in all_rows if r.get("category") == "label"]
    tiers: dict[str, list] = {"big": [], "mid": [], "small": []}

    for c in labels:
        tier = _label_size(c)
        tiers[tier].append({
            "name": c.get("name", ""),
            "tier": tier,
            "location": c.get("location", "") or c.get("soundcloud_city", ""),
            "genre": c.get("genre_sub") or c.get("genre_main", ""),
            "demo_email": c.get("demo_email", ""),
            "website": c.get("discogs_official_website") or c.get("discogs_website", ""),
            "bandcamp": c.get("discogs_bandcamp", ""),
            "soundcloud_url": (c.get("soundcloud_url") or "").split("?")[0],
            "soundcloud_followers": _int(c.get("soundcloud_followers", 0)),
            "discogs_releases": _int(c.get("discogs_releases", 0)),
            "discogs_url": c.get("discogs_url", ""),
            "instagram": c.get("url", "") if "instagram" in c.get("url", "") else "",
            "origin": c.get("source", ""),
        })

    for tier in tiers:
        tiers[tier].sort(
            key=lambda x: x["soundcloud_followers"] + x["discogs_releases"] * 50,
            reverse=True,
        )

    output = {
        "tier_thresholds": {
            "big": "SC followers + (Discogs releases x 50) >= 10000, or size_override=big",
            "mid": "SC followers + (Discogs releases x 50) >= 2000, or size_override=mid",
            "small": "below mid threshold",
        },
        "counts": {t: len(v) for t, v in tiers.items()},
        "tiers": tiers,
    }

    tiers_path = Path(__file__).parent / "label_tiers.json"
    atomic_write_json(tiers_path, output)

    total = sum(len(v) for v in tiers.values())
    print(f"  Label tiers     {total:>4} labels (big={len(tiers['big'])}, mid={len(tiers['mid'])}, small={len(tiers['small'])})")


if __name__ == "__main__":
    main()
