"""
scene_intelligence/enrich_spotify.py
--------------------------------------
Tool 1 -- Scene Intelligence Engine: Spotify Artist Enricher

Two-phase enrichment using Spotify Web API:
  1. Direct  -- contacts with existing Spotify URLs -> artists/{id} (no search)
  2. Search  -- DJs/artists without Spotify URLs -> search (name match)

New fields added:
  spotify_id, spotify_url, spotify_genres, spotify_popularity,
  spotify_followers, spotify_match_confidence

Usage:
  python3 scene_intelligence/enrich_spotify.py              # Phase 1 + Phase 2 (DJs only)
  python3 scene_intelligence/enrich_spotify.py --all        # Phase 1 + Phase 2 (all categories)
  python3 scene_intelligence/enrich_spotify.py --force      # Re-enrich already-enriched contacts
"""

from __future__ import annotations

import base64
import difflib
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

load_dotenv(BASE_DIR / ".env")
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

SPOTIFY_TOKEN_URL  = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_ARTIST_URL = "https://api.spotify.com/v1/artists/{id}"

API_DELAY  = 1.0
TIMEOUT    = 10
SEARCH_CONFIDENCE_MIN = 80

# Categories to search in Phase 2
DEFAULT_SEARCH_CATEGORIES = {"dj"}
ALL_SEARCH_CATEGORIES = {"dj", "label", "promoter"}


# ---------------------------------------------------------------------------
# Spotify auth (Client Credentials flow)
# ---------------------------------------------------------------------------

_token_cache: dict = {"access_token": "", "expires_at": 0.0}


def _get_token() -> str:
    """Get a valid Spotify access token, refreshing if expired."""
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    credentials = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()

    try:
        r = requests.post(
            SPOTIFY_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {credentials}"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"  [AUTH ERROR] HTTP {r.status_code}: {r.text[:200]}", flush=True)
            return ""
        data = r.json()
        _token_cache["access_token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
        return _token_cache["access_token"]
    except requests.RequestException as exc:
        print(f"  [AUTH ERROR] {exc}", flush=True)
        return ""


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _spotify_get(url: str, params: dict | None = None) -> dict | None:
    """Make an authenticated Spotify API request. Returns parsed JSON or None."""
    token = _get_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

        if r.status_code == 200:
            return r.json()

        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 5))
            print(f"  [RATE LIMIT] waiting {retry_after}s...", flush=True)
            time.sleep(retry_after)
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            return None

        if r.status_code == 401:
            _token_cache["access_token"] = ""
            token = _get_token()
            if not token:
                return None
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            return None

        if r.status_code == 404:
            return None

        print(f"  [HTTP {r.status_code}]", flush=True)
        return None

    except requests.RequestException as exc:
        print(f"  [request error] {exc}", flush=True)
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_spotify_artist_id(url: str) -> str:
    """Extract artist ID from a Spotify URL."""
    m = re.search(r'spotify\.com/artist/([a-zA-Z0-9]+)', url)
    return m.group(1) if m else ""


def _collect_spotify_urls(contact: dict) -> list[str]:
    """Gather all Spotify artist URLs from a contact's various fields."""
    urls = []
    for field in ("musicbrainz_website", "discogs_official_website", "url"):
        val = contact.get(field, "") or ""
        if "spotify.com/artist/" in val.lower():
            urls.append(val)
    return urls


def _parse_artist_data(artist: dict) -> dict:
    """Extract enrichment fields from a Spotify artist object."""
    return {
        "spotify_id":         artist.get("id", ""),
        "spotify_url":        artist.get("external_urls", {}).get("spotify", ""),
        "spotify_genres":     ", ".join(artist.get("genres", [])),
        "spotify_popularity": str(artist.get("popularity", "")),
        "spotify_followers":  str(artist.get("followers", {}).get("total", "")),
    }


def _save(contacts: list[dict]) -> None:
    """Save contacts to enriched_contacts.json."""
    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Phase 1: Direct enrichment
# ---------------------------------------------------------------------------

def phase_direct(contacts: list[dict], force: bool = False) -> int:
    """Enrich contacts that already have Spotify artist URLs.

    Returns enriched_count.
    """
    targets = []
    for c in contacts:
        if not force and c.get("spotify_popularity"):
            continue
        spotify_urls = _collect_spotify_urls(c)
        if spotify_urls:
            targets.append((c, spotify_urls))

    if not targets:
        print("  No contacts with Spotify URLs to enrich.")
        return 0

    print(f"  Phase 1: {len(targets)} contacts with Spotify URLs")
    enriched = 0

    for i, (contact, spotify_urls) in enumerate(targets):
        name = contact.get("name", "")
        artist_id = ""
        for url in spotify_urls:
            artist_id = _extract_spotify_artist_id(url)
            if artist_id:
                break

        print(f"    [{i+1:>3}/{len(targets)}] {name[:40]:<40}", end="  ", flush=True)

        if not artist_id:
            print("-- could not extract artist ID")
            continue

        data = _spotify_get(SPOTIFY_ARTIST_URL.format(id=artist_id))
        time.sleep(API_DELAY)

        if not data:
            print("-- fetch failed")
            continue

        artist_data = _parse_artist_data(data)
        contact.update(artist_data)
        enriched += 1

        genres = artist_data.get("spotify_genres", "")
        pop = artist_data.get("spotify_popularity", "?")
        followers = artist_data.get("spotify_followers", "?")
        parts = []
        if pop:
            parts.append(f"pop:{pop}")
        if followers:
            parts.append(f"{followers} followers")
        if genres:
            parts.append(genres[:30])
        print(f"+{len(artist_data)} ({', '.join(parts)})")

    _save(contacts)
    return enriched


# ---------------------------------------------------------------------------
# Phase 2: Search enrichment
# ---------------------------------------------------------------------------

def phase_search(contacts: list[dict], categories: set[str],
                 force: bool = False) -> tuple[int, int]:
    """Search Spotify for contacts without Spotify URLs.

    Returns (found_count, not_found_count).
    """
    targets = []
    for c in contacts:
        if not force and c.get("spotify_id"):
            continue
        if _collect_spotify_urls(c):
            continue
        cat = c.get("category", "")
        if cat not in categories:
            continue
        targets.append(c)

    if not targets:
        print("  No contacts to search.")
        return 0, 0

    print(f"  Phase 2: {len(targets)} contacts to search")
    print(f"  Categories: {', '.join(sorted(categories))}")

    found = 0
    not_found = 0

    for i, contact in enumerate(targets):
        name = contact.get("name", "")
        search_name = re.sub(r'[_\.]+', ' ', name).strip()

        print(f"    [{i+1:>3}/{len(targets)}] {name[:40]:<40}", end="  ", flush=True)

        data = _spotify_get(SPOTIFY_SEARCH_URL, params={
            "q": search_name,
            "type": "artist",
            "limit": 3,
        })
        time.sleep(API_DELAY)

        if not data:
            not_found += 1
            print("-- API error")
            continue

        items = data.get("artists", {}).get("items", [])
        if not items:
            not_found += 1
            print("-- no results")
            continue

        # Find best match by name similarity
        name_norm = re.sub(r'[^a-z0-9]', '', name.lower())
        best_item = None
        best_confidence = 0

        for item in items:
            artist_name = item.get("name", "")
            artist_norm = re.sub(r'[^a-z0-9]', '', artist_name.lower())
            confidence = round(
                difflib.SequenceMatcher(None, name_norm, artist_norm).ratio() * 100
            )
            if confidence > best_confidence:
                best_confidence = confidence
                best_item = item

        if best_confidence < SEARCH_CONFIDENCE_MIN or not best_item:
            not_found += 1
            best_name = best_item.get("name", "?") if best_item else "?"
            print(f"-- low confidence ({best_confidence}% for '{best_name}')")
            continue

        # Got a match
        artist_data = _parse_artist_data(best_item)
        artist_data["spotify_match_confidence"] = best_confidence
        contact.update(artist_data)
        found += 1

        matched_name = best_item.get("name", "")
        pop = artist_data.get("spotify_popularity", "?")
        followers = artist_data.get("spotify_followers", "?")
        genres = artist_data.get("spotify_genres", "")
        parts = [f"{best_confidence}% ({matched_name})"]
        if pop:
            parts.append(f"pop:{pop}")
        if followers:
            parts.append(f"{followers} followers")
        if genres:
            parts.append(genres[:25])
        print(f"FOUND {', '.join(parts)}")

        # Save periodically
        if (i + 1) % 25 == 0:
            _save(contacts)

    _save(contacts)
    return found, not_found


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence -- Spotify Artist Enricher")
    print("=" * 50)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found. Run enrich_contacts.py first.")
        sys.exit(1)

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("ERROR: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    # Test authentication
    token = _get_token()
    if not token:
        print("ERROR: Failed to authenticate with Spotify API. Check credentials.")
        sys.exit(1)
    print("  Spotify auth: OK")

    with open(ENRICHED_FILE, encoding="utf-8") as f:
        contacts = json.load(f)
    print(f"  Loaded {len(contacts)} contacts from enriched_contacts.json")

    has_spotify_url = sum(1 for c in contacts if _collect_spotify_urls(c))
    has_spotify_data = sum(1 for c in contacts if c.get("spotify_popularity"))
    print(f"  Contacts with Spotify URLs: {has_spotify_url}")
    print(f"  Already enriched: {has_spotify_data}")

    args = set(sys.argv[1:])
    force = "--force" in args
    search_all = "--all" in args

    categories = ALL_SEARCH_CATEGORIES if search_all else DEFAULT_SEARCH_CATEGORIES
    skipped = has_spotify_data if not force else 0

    # Phase 1: Direct enrichment (always runs)
    print(f"\n--- Phase 1: Direct enrichment (contacts with Spotify URLs) ---")
    direct_count = phase_direct(contacts, force=force)
    print(f"  Direct: {direct_count} contacts enriched")

    # Phase 2: Search enrichment (always runs, category scope varies)
    print(f"\n--- Phase 2: Spotify search ({', '.join(sorted(categories))}) ---")
    search_found, search_missed = phase_search(contacts, categories, force=force)
    print(f"  Search: {search_found} found, {search_missed} not found")

    # Final save
    _save(contacts)

    # Summary
    total = direct_count + search_found
    print()
    print("=" * 50)
    print(f"  Enriched (direct): {direct_count}")
    print(f"  Found (search):    {search_found}")
    print(f"  Not found:         {search_missed}")
    print(f"  Skipped (done):    {skipped}")
    print(f"  Total updated:     {total}")

    # Coverage summary
    has_id = sum(1 for c in contacts if c.get("spotify_id"))
    has_genres = sum(1 for c in contacts if c.get("spotify_genres"))
    has_pop = sum(1 for c in contacts if c.get("spotify_popularity"))
    print(f"\n  Spotify coverage:")
    print(f"    Artist IDs:   {has_id}")
    print(f"    Genres:       {has_genres}")
    print(f"    Popularity:   {has_pop}")
    print(f"  Saved to: enriched_contacts.json")
    print()


if __name__ == "__main__":
    main()
