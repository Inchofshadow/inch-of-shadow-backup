"""
scene_intelligence/enrich_soundcloud.py
----------------------------------------
Tool 1 -- Scene Intelligence Engine: SoundCloud User Enricher

Two-phase enrichment using SoundCloud API:
  1. Direct  -- contacts with existing SoundCloud URLs -> /resolve (no search)
  2. Search  -- DJs/artists without SoundCloud URLs -> /users?q= (name match)

New fields added:
  soundcloud_user_id, soundcloud_url, soundcloud_followers,
  soundcloud_tracks, soundcloud_city, soundcloud_country,
  soundcloud_description, soundcloud_match_confidence,
  soundcloud_last_upload (YYYY-MM-DD of most recent track),
  soundcloud_enriched_at (YYYY-MM-DD — date follower count was last fetched)

Usage:
  python3 scene_intelligence/enrich_soundcloud.py              # Phase 1 + Phase 2 (DJs only)
  python3 scene_intelligence/enrich_soundcloud.py --all        # Phase 1 + Phase 2 (all categories)
  python3 scene_intelligence/enrich_soundcloud.py --force      # Re-enrich already-enriched contacts
  python3 scene_intelligence/enrich_soundcloud.py --backfill-uploads  # Fetch last upload date for already-enriched contacts
"""

from __future__ import annotations

import base64
import datetime
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
SC_CLIENT_ID     = os.getenv("SOUNDCLOUD_CLIENT_ID", "")
SC_CLIENT_SECRET = os.getenv("SOUNDCLOUD_CLIENT_SECRET", "")

SC_TOKEN_URL   = "https://secure.soundcloud.com/oauth/token"
SC_API_BASE    = "https://api.soundcloud.com"
SC_RESOLVE_URL = f"{SC_API_BASE}/resolve"
SC_USERS_URL   = f"{SC_API_BASE}/users"

API_DELAY  = 0.5
TIMEOUT    = 10
SEARCH_CONFIDENCE_MIN = 80
SEARCH_MIN_FOLLOWERS  = 500   # Phase 2 only — reject matches with fewer followers (ghost/wrong accounts)

# Categories to search in Phase 2
DEFAULT_SEARCH_CATEGORIES = {"dj"}
ALL_SEARCH_CATEGORIES = {"dj", "label", "promoter", "media"}


# ---------------------------------------------------------------------------
# SoundCloud auth (Client Credentials flow)
# ---------------------------------------------------------------------------

_token_cache: dict = {"access_token": "", "expires_at": 0.0}


def _get_token() -> str:
    """Get a valid SoundCloud access token, refreshing if expired."""
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    credentials = base64.b64encode(
        f"{SC_CLIENT_ID}:{SC_CLIENT_SECRET}".encode()
    ).decode()

    try:
        r = requests.post(
            SC_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
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

def _sc_get(url: str, params: dict | None = None) -> dict | None:
    """Make an authenticated SoundCloud API request. Returns parsed JSON or None."""
    token = _get_token()
    if not token:
        return None

    headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}

    try:
        r = requests.get(url, params=params, headers=headers,
                         timeout=TIMEOUT, allow_redirects=True)

        if r.status_code == 200:
            return r.json()

        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 10))
            print(f"  [RATE LIMIT] waiting {retry_after}s...", flush=True)
            time.sleep(retry_after)
            r = requests.get(url, params=params, headers=headers,
                             timeout=TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                return r.json()
            return None

        if r.status_code == 401:
            _token_cache["access_token"] = ""
            token = _get_token()
            if not token:
                return None
            headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}
            r = requests.get(url, params=params, headers=headers,
                             timeout=TIMEOUT, allow_redirects=True)
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

def _collect_sc_urls(contact: dict) -> list[str]:
    """Gather all SoundCloud URLs from a contact's various fields.

    soundcloud_url is checked first — if we've manually set a confirmed URL,
    Phase 1 will use it directly instead of falling through to name search.
    """
    urls = []
    # Check soundcloud_url first (manually confirmed or previously enriched)
    sc_url = contact.get("soundcloud_url", "") or ""
    if sc_url and "soundcloud.com" in sc_url.lower():
        urls.append(sc_url.strip())
    # Then check source fields (Discogs, MusicBrainz, generic url)
    for field in ("discogs_soundcloud", "musicbrainz_soundcloud", "url"):
        val = contact.get(field, "") or ""
        if "soundcloud.com" in val.lower() and val.strip() not in urls:
            urls.append(val.strip())
    return urls


def _normalize_sc_url(url: str) -> str:
    """Normalize a SoundCloud URL for the resolve endpoint."""
    url = url.strip().rstrip("/")
    # Ensure https
    url = re.sub(r'^http://', 'https://', url)
    # Remove query params and fragments
    url = re.sub(r'[?#].*$', '', url)
    return url


def _parse_user_data(user: dict) -> dict:
    """Extract enrichment fields from a SoundCloud user object."""
    user_id = user.get("id", "")
    # Handle URN format (soundcloud:users:12345)
    urn = user.get("urn", "")
    if urn and not user_id:
        m = re.search(r':(\d+)$', urn)
        if m:
            user_id = m.group(1)

    return {
        "soundcloud_user_id":      str(user_id),
        "soundcloud_url":          user.get("permalink_url", ""),
        "soundcloud_followers":    str(user.get("followers_count", "")),
        "soundcloud_tracks":       str(user.get("track_count", "")),
        "soundcloud_city":         user.get("city", "") or "",
        "soundcloud_country":      user.get("country_code", "") or user.get("country", "") or "",
        "soundcloud_description":  (user.get("description", "") or "")[:200],
        "soundcloud_enriched_at":  datetime.date.today().isoformat(),
    }


def _fetch_last_upload(user_id: str) -> str:
    """Fetch the date of a user's most recent track. Returns 'YYYY-MM-DD' or ''."""
    if not user_id:
        return ""
    data = _sc_get(f"{SC_API_BASE}/users/{user_id}/tracks",
                   params={"limit": 1, "linked_partitioning": 1})
    time.sleep(API_DELAY)
    if not data:
        return ""
    items = data if isinstance(data, list) else data.get("collection", [])
    if not items:
        return ""
    created = items[0].get("created_at", "") or items[0].get("display_date", "")
    if not created:
        return ""
    # SoundCloud may return "2025/07/22 14:44:54 +0000" or "2025-07-22T14:44:54Z"
    m = re.match(r"(\d{4})[/-](\d{2})[/-](\d{2})", created)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return ""


def _save(contacts: list[dict]) -> None:
    """Save contacts to enriched_contacts.json."""
    # SC-06 (2026-09-01): atomic write — a crash mid-write no longer
    # truncates the 2.3MB contacts DB.
    tmp = str(ENRICHED_FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ENRICHED_FILE)


# ---------------------------------------------------------------------------
# Phase 1: Direct enrichment (contacts with SC URLs)
# ---------------------------------------------------------------------------

def phase_direct(contacts: list[dict], force: bool = False) -> int:
    """Enrich contacts that already have SoundCloud URLs via /resolve.

    Returns enriched_count.
    """
    targets = []
    for c in contacts:
        if not force and c.get("soundcloud_user_id"):
            continue
        sc_urls = _collect_sc_urls(c)
        if sc_urls:
            targets.append((c, sc_urls))

    if not targets:
        print("  No contacts with SoundCloud URLs to enrich.")
        return 0

    print(f"  Phase 1: {len(targets)} contacts with SoundCloud URLs")
    enriched = 0

    for i, (contact, sc_urls) in enumerate(targets):
        name = contact.get("name", "")
        print(f"    [{i+1:>3}/{len(targets)}] {name[:40]:<40}", end="  ", flush=True)

        resolved = False
        for url in sc_urls:
            clean_url = _normalize_sc_url(url)
            data = _sc_get(SC_RESOLVE_URL, params={"url": clean_url})
            time.sleep(API_DELAY)

            if not data:
                continue

            # resolve can return tracks, playlists, or users
            kind = data.get("kind", "")
            if kind != "user":
                print(f"-- resolved to {kind}, not user", end="  ")
                continue

            user_data = _parse_user_data(data)
            user_data["soundcloud_match_confidence"] = 100
            # Fetch last upload date
            last_upload = _fetch_last_upload(user_data.get("soundcloud_user_id", ""))
            user_data["soundcloud_last_upload"] = last_upload
            contact.update(user_data)
            enriched += 1
            resolved = True

            followers = user_data.get("soundcloud_followers", "?")
            tracks = user_data.get("soundcloud_tracks", "?")
            city = user_data.get("soundcloud_city", "")
            parts = [f"{followers} followers", f"{tracks} tracks"]
            if last_upload:
                parts.append(f"last upload {last_upload}")
            if city:
                parts.append(city)
            print(f"OK ({', '.join(parts)})")
            break

        if not resolved:
            print("-- resolve failed")

        # Save periodically
        if (i + 1) % 25 == 0:
            _save(contacts)

    _save(contacts)
    return enriched


# ---------------------------------------------------------------------------
# Phase 2: Search enrichment (contacts without SC URLs)
# ---------------------------------------------------------------------------

def phase_search(contacts: list[dict], categories: set[str],
                 force: bool = False) -> tuple[int, int]:
    """Search SoundCloud for contacts without SoundCloud URLs.

    Returns (found_count, not_found_count).
    """
    targets = []
    for c in contacts:
        if not force and c.get("soundcloud_user_id"):
            continue
        if _collect_sc_urls(c):
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

        data = _sc_get(SC_USERS_URL, params={
            "q": search_name,
            "limit": 5,
        })
        time.sleep(API_DELAY)

        if not data:
            not_found += 1
            print("-- API error")
            continue

        # API may return a list directly or a dict with "collection"
        if isinstance(data, list):
            items = data
        else:
            items = data.get("collection", [])
        if not items:
            not_found += 1
            print("-- no results")
            continue

        # Find best match by name similarity
        name_norm = re.sub(r'[^a-z0-9]', '', name.lower())
        best_item = None
        best_confidence = 0

        for item in items:
            # Check both username and full_name
            for field in ("username", "full_name"):
                candidate = item.get(field, "") or ""
                if not candidate:
                    continue
                candidate_norm = re.sub(r'[^a-z0-9]', '', candidate.lower())
                confidence = round(
                    difflib.SequenceMatcher(None, name_norm, candidate_norm).ratio() * 100
                )
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_item = item

        if best_confidence < SEARCH_CONFIDENCE_MIN or not best_item:
            not_found += 1
            best_name = best_item.get("username", "?") if best_item else "?"
            print(f"-- low confidence ({best_confidence}% for '{best_name}')")
            continue

        # Reject ghost/wrong accounts — must have meaningful SC presence
        best_followers = best_item.get("followers_count", 0) or 0
        if best_followers < SEARCH_MIN_FOLLOWERS:
            not_found += 1
            best_name = best_item.get("username", "?")
            print(f"-- too few followers ({best_followers} for '{best_name}', min {SEARCH_MIN_FOLLOWERS})")
            continue

        # Got a match
        user_data = _parse_user_data(best_item)
        user_data["soundcloud_match_confidence"] = best_confidence
        # Fetch last upload date
        last_upload = _fetch_last_upload(user_data.get("soundcloud_user_id", ""))
        user_data["soundcloud_last_upload"] = last_upload
        contact.update(user_data)
        found += 1

        matched_name = best_item.get("username", "")
        followers = user_data.get("soundcloud_followers", "?")
        tracks = user_data.get("soundcloud_tracks", "?")
        parts = [f"{best_confidence}% ({matched_name})", f"{followers} followers"]
        if tracks and tracks != "0":
            parts.append(f"{tracks} tracks")
        if last_upload:
            parts.append(f"last upload {last_upload}")
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
    print("\nScene Intelligence -- SoundCloud User Enricher")
    print("=" * 50)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found. Run enrich_contacts.py first.")
        sys.exit(1)

    if not SC_CLIENT_ID or not SC_CLIENT_SECRET:
        print("ERROR: SOUNDCLOUD_CLIENT_ID and SOUNDCLOUD_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    # Test authentication
    token = _get_token()
    if not token:
        print("ERROR: Failed to authenticate with SoundCloud API. Check credentials.")
        sys.exit(1)
    print("  SoundCloud auth: OK")

    with open(ENRICHED_FILE, encoding="utf-8") as f:
        contacts = json.load(f)
    print(f"  Loaded {len(contacts)} contacts from enriched_contacts.json")

    has_sc_url = sum(1 for c in contacts if _collect_sc_urls(c))
    has_sc_data = sum(1 for c in contacts if c.get("soundcloud_user_id"))
    print(f"  Contacts with SoundCloud URLs: {has_sc_url}")
    print(f"  Already enriched: {has_sc_data}")

    args = set(sys.argv[1:])
    force = "--force" in args
    search_all = "--all" in args
    backfill_uploads = "--backfill-uploads" in args

    if backfill_uploads:
        # Standalone mode: only fetch last upload dates for already-enriched contacts
        print(f"\n--- Backfill: Fetching last upload dates ---")
        targets = [c for c in contacts
                   if c.get("soundcloud_user_id") and not c.get("soundcloud_last_upload")]
        print(f"  {len(targets)} contacts need last upload date")
        updated = 0
        for i, c in enumerate(targets):
            name = c.get("name", "")
            uid = c["soundcloud_user_id"]
            print(f"    [{i+1:>3}/{len(targets)}] {name[:40]:<40}", end="  ", flush=True)
            last_upload = _fetch_last_upload(uid)
            c["soundcloud_last_upload"] = last_upload
            if last_upload:
                updated += 1
                print(f"last upload {last_upload}")
            else:
                print("-- no tracks")
            if (i + 1) % 25 == 0:
                _save(contacts)
        _save(contacts)
        has_upload = sum(1 for c in contacts if c.get("soundcloud_last_upload"))
        print(f"\n  Updated: {updated}")
        print(f"  Total with last upload date: {has_upload}/{has_sc_data}")
        print(f"  Saved to: enriched_contacts.json")
        print()
        return

    categories = ALL_SEARCH_CATEGORIES if search_all else DEFAULT_SEARCH_CATEGORIES
    skipped = has_sc_data if not force else 0

    # Phase 1: Direct enrichment (always runs)
    print(f"\n--- Phase 1: Direct enrichment (contacts with SoundCloud URLs) ---")
    direct_count = phase_direct(contacts, force=force)
    print(f"  Direct: {direct_count} contacts enriched")

    # Phase 2: Search enrichment
    print(f"\n--- Phase 2: SoundCloud search ({', '.join(sorted(categories))}) ---")
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
    has_id = sum(1 for c in contacts if c.get("soundcloud_user_id"))
    has_followers = sum(1 for c in contacts if c.get("soundcloud_followers"))
    has_url = sum(1 for c in contacts if c.get("soundcloud_url"))
    has_upload = sum(1 for c in contacts if c.get("soundcloud_last_upload"))
    print(f"\n  SoundCloud coverage:")
    print(f"    User IDs:      {has_id}")
    print(f"    URLs:          {has_url}")
    print(f"    Followers:     {has_followers}")
    print(f"    Last upload:   {has_upload}")
    print(f"  Saved to: enriched_contacts.json")
    print()


if __name__ == "__main__":
    main()
