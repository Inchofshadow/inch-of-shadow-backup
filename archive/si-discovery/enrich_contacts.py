"""
scene_intelligence/enrich_contacts.py
---------------------------------------
Tool 1 — Scene Intelligence Engine: Discogs Enricher

Reads scene_intelligence/raw_contacts.json, searches each label and DJ/producer
on the Discogs API, and adds structured music-industry data:

  For labels:
    discogs_url, discogs_genres, discogs_country, discogs_email,
    discogs_releases (count), discogs_last_year, discogs_website

  For DJs:
    discogs_url, discogs_genres, discogs_labels (they release on),
    discogs_releases (count), discogs_last_year, discogs_website

Also updates genre_main/genre_sub/location from Discogs data when more
accurate than keyword inference.

Output:
  scene_intelligence/enriched_contacts.json

Usage:
  python3 scene_intelligence/enrich_contacts.py
"""

from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from utils import CATEGORY_DEFAULT_SCORE, normalize_raw_contacts

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent.parent
INPUT_FILE  = BASE_DIR / "scene_intelligence" / "raw_contacts.json"
OUTPUT_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

load_dotenv(BASE_DIR / ".env")
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN", "")

DISCOGS_SEARCH = "https://api.discogs.com/database/search"
DISCOGS_ARTIST = "https://api.discogs.com/artists/{id}"
DISCOGS_LABEL  = "https://api.discogs.com/labels/{id}"

REQUEST_DELAY     = 1.0   # seconds between requests (safe at 60 req/min with token)
ENRICH_CATEGORIES = {"label", "dj"}
TIMEOUT           = 10

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _headers() -> dict:
    h = {"User-Agent": "InchOfShadowSceneIntelligence/1.0"}
    if DISCOGS_TOKEN:
        h["Authorization"] = f"Discogs token={DISCOGS_TOKEN}"
    return h


def _get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [rate limit] waiting 15s...", flush=True)
            time.sleep(15)
        return None
    except requests.RequestException:
        return None


def _extract_email(text: str) -> str:
    """Pull first email address from a block of text."""
    matches = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', text or "")
    return matches[0] if matches else ""


# ---------------------------------------------------------------------------
# Discogs lookups
# ---------------------------------------------------------------------------

def search_discogs(name: str, search_type: str) -> dict | None:
    data = _get(DISCOGS_SEARCH, params={"q": name, "type": search_type, "per_page": 3})
    time.sleep(REQUEST_DELAY)
    if not data:
        return None
    results = data.get("results", [])
    return results[0] if results else None


def get_artist_detail(artist_id: int) -> dict | None:
    data = _get(DISCOGS_ARTIST.format(id=artist_id))
    time.sleep(REQUEST_DELAY)
    return data


def get_label_detail(label_id: int) -> dict | None:
    data = _get(DISCOGS_LABEL.format(id=label_id))
    time.sleep(REQUEST_DELAY)
    return data


def get_releases(releases_url: str, per_page: int = 1) -> dict | None:
    data = _get(releases_url, params={"per_page": per_page, "sort": "year", "sort_order": "desc"})
    time.sleep(REQUEST_DELAY)
    return data


# ---------------------------------------------------------------------------
# Enrichment functions
# ---------------------------------------------------------------------------

_EMPTY = {
    "discogs_url":      "",
    "discogs_genres":   "",
    "discogs_country":  "",
    "discogs_email":    "",
    "discogs_releases": "",
    "discogs_last_year":"",
    "discogs_website":  "",
    "discogs_labels":   "",
    "discogs_found":    False,
    "discogs_match_confidence": "",
}


def enrich_label(name: str) -> dict:
    result = search_discogs(name, "label")
    if not result:
        return dict(_EMPTY)

    label_id = result.get("id")
    detail   = get_label_detail(label_id) if label_id else None
    if not detail:
        return dict(_EMPTY)

    # Compute match confidence
    matched_name = result.get("title", "")
    name_normalized = re.sub(r'[^a-z0-9]', '', name.lower())
    matched_normalized = re.sub(r'[^a-z0-9]', '', matched_name.lower())
    confidence = round(difflib.SequenceMatcher(None, name_normalized, matched_normalized).ratio() * 100)

    genres       = ", ".join(result.get("genre", []) or [])
    country      = detail.get("country", "")
    url          = detail.get("uri", "") or f"https://www.discogs.com/label/{label_id}"
    contact_info = detail.get("contact_info", "")
    profile      = detail.get("profile", "")
    email        = _extract_email(contact_info) or _extract_email(profile)
    urls         = detail.get("urls", [])
    website      = urls[0] if urls else ""

    # Releases: total count + most recent year
    releases_url   = detail.get("releases_url", "")
    release_count  = ""
    last_year      = ""
    if releases_url:
        rel_data = get_releases(releases_url, per_page=1)
        if rel_data:
            release_count = str(rel_data.get("pagination", {}).get("items", ""))
            releases = rel_data.get("releases", [])
            if releases:
                last_year = str(releases[0].get("year", ""))

    return {
        "discogs_url":       url,
        "discogs_genres":    genres,
        "discogs_country":   country,
        "discogs_email":     email,
        "discogs_releases":  release_count,
        "discogs_last_year": last_year,
        "discogs_website":   website,
        "discogs_labels":    name,
        "discogs_found":     True,
        "discogs_match_confidence": confidence,
    }


def enrich_dj(name: str) -> dict:
    result = search_discogs(name, "artist")
    if not result:
        return dict(_EMPTY)

    artist_id = result.get("id")
    detail    = get_artist_detail(artist_id) if artist_id else None
    if not detail:
        return dict(_EMPTY)

    # Compute match confidence
    matched_name = result.get("title", "")
    name_normalized = re.sub(r'[^a-z0-9]', '', name.lower())
    matched_normalized = re.sub(r'[^a-z0-9]', '', matched_name.lower())
    confidence = round(difflib.SequenceMatcher(None, name_normalized, matched_normalized).ratio() * 100)

    genres  = ", ".join(result.get("genre", []) or result.get("style", []))
    url     = detail.get("uri", "") or f"https://www.discogs.com/artist/{artist_id}"
    urls    = detail.get("urls", [])
    website = urls[0] if urls else ""

    # Releases: labels + count + last year
    releases_url  = detail.get("releases_url", "")
    labels_found: list[str] = []
    release_count = ""
    last_year     = ""
    if releases_url:
        rel_data = get_releases(releases_url, per_page=5)
        if rel_data:
            release_count = str(rel_data.get("pagination", {}).get("items", ""))
            for rel in rel_data.get("releases", [])[:5]:
                lbl = rel.get("label", "")
                if lbl and lbl not in labels_found:
                    labels_found.append(lbl)
                if not last_year:
                    last_year = str(rel.get("year", ""))

    return {
        "discogs_url":       url,
        "discogs_genres":    genres,
        "discogs_country":   "",
        "discogs_email":     "",
        "discogs_releases":  release_count,
        "discogs_last_year": last_year,
        "discogs_website":   website,
        "discogs_labels":    ", ".join(labels_found),
        "discogs_found":     True,
        "discogs_match_confidence": confidence,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence — Discogs Enricher")
    print("=" * 42)

    if not INPUT_FILE.exists():
        print(f"ERROR: {INPUT_FILE} not found. Run extract_contacts.py first.")
        sys.exit(1)

    # LANDMINE GUARD (2026-07-05, audit P2-11): this script REBUILDS the
    # enriched DB from the raw extract, discarding every enrichment layer
    # (curator DB, IG handles, flags, scores, manual edits). Refuse when a
    # mature DB exists unless explicitly forced.
    if OUTPUT_FILE.exists() and "--force-rebuild" not in sys.argv:
        try:
            with open(OUTPUT_FILE, encoding="utf-8") as f:
                existing_count = len(json.load(f))
        except (json.JSONDecodeError, OSError):
            existing_count = -1
        print(f"REFUSED: {OUTPUT_FILE.name} already exists "
              f"({existing_count if existing_count >= 0 else 'unreadable'} contacts).")
        print("Running this script would REPLACE the mature database with a bare")
        print("re-normalization of raw_contacts.json - ALL enrichment would be lost.")
        print("If you really mean to rebuild from scratch, re-run with")
        print("--force-rebuild (a timestamped .bak copy is written first).")
        sys.exit(2)

    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    all_contacts = normalize_raw_contacts(raw)
    to_enrich    = [c for c in all_contacts if c["category"] in ENRICH_CATEGORIES]
    skip_count   = len(all_contacts) - len(to_enrich)

    if DISCOGS_TOKEN:
        print(f"  Discogs token: set  (60 req/min)")
    else:
        print(f"  Discogs token: not set  (25 req/min)")

    print(f"  Contacts to enrich: {len(to_enrich)}  (labels + DJs)")
    print(f"  Contacts skipped:   {skip_count}  (media/venue/other)")
    est_min = (len(to_enrich) * 3 * REQUEST_DELAY) / 60
    print(f"  Estimated time:     ~{est_min:.0f} minutes")
    print()

    found  = 0
    missed = 0

    for i, contact in enumerate(all_contacts):
        cat = contact["category"]

        if cat not in ENRICH_CATEGORIES:
            contact.update({k: "" for k in _EMPTY})
            contact["discogs_found"] = False
            contact["verification_status"] = "?"
            if not contact.get("match_score"):
                contact["match_score"] = CATEGORY_DEFAULT_SCORE.get(cat, "1")
            continue

        name = contact["name"]
        idx  = i + 1
        print(f"  [{idx:>4}/{len(all_contacts)}] {cat:<6}  {name[:38]:<38}", end="  ", flush=True)

        enriched = enrich_label(name) if cat == "label" else enrich_dj(name)
        contact.update(enriched)

        # Add verification status
        if enriched["discogs_found"]:
            pct = enriched.get("discogs_match_confidence", "")
            contact["verification_status"] = f"✓ {pct}%" if pct != "" else "✓"
        else:
            contact["verification_status"] = "✗"

        # Apply category-based default score if genre inference didn't produce one
        if not contact.get("match_score"):
            contact["match_score"] = CATEGORY_DEFAULT_SCORE.get(cat, "1")

        if enriched["discogs_found"]:
            found += 1
            # Use Discogs country as location if we didn't have one
            if enriched.get("discogs_country") and not contact.get("location"):
                contact["location"] = enriched["discogs_country"]

            parts = []
            if enriched.get("discogs_genres"):
                parts.append(enriched["discogs_genres"][:25])
            if enriched.get("discogs_releases"):
                parts.append(f"{enriched['discogs_releases']} releases")
            if enriched.get("discogs_last_year"):
                parts.append(f"last: {enriched['discogs_last_year']}")
            if enriched.get("discogs_email"):
                parts.append("EMAIL")
            print("✓  " + "  |  ".join(parts))
        else:
            missed += 1
            print("—  not found")

    # Save (timestamped backup first if overwriting - audit P2-11)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_FILE.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = OUTPUT_FILE.with_name(f"enriched_contacts.bak.{stamp}.json")
        shutil.copy2(OUTPUT_FILE, backup)
        print(f"  Backup written: {backup.name}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_contacts, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 42)
    print(f"  Found:     {found} contacts enriched")
    print(f"  Not found: {missed} contacts")
    print(f"  Skipped:   {skip_count} (media/venue/other)")
    emails_found = sum(1 for c in all_contacts if c.get("discogs_email"))
    print(f"  Emails:    {emails_found} demo submission emails found")
    print(f"  Saved to:  scene_intelligence/enriched_contacts.json")
    print()


if __name__ == "__main__":
    main()
