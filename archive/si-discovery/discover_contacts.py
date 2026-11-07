"""
scene_intelligence/discover_contacts.py
-----------------------------------------
Tool 1 -- Scene Intelligence Engine: Contact Discovery

Discovers new contacts by crawling the network graph of existing seeds:
  Phase 1: Spotify Related Artists (seeds with spotify_id -> up to 20 related each)
  Phase 2: YouTube Subscriptions (seeds with youtube_channel_id -> public subscriptions)

Frequency-based ranking: only contacts that appear from multiple seeds are kept.
  Spotify minimum: 3 seeds   (algorithmic, needs higher bar)
  YouTube minimum: 2 seeds   (subscriptions are curated, lower bar)

Usage:
  python3 scene_intelligence/discover_contacts.py               # Both phases
  python3 scene_intelligence/discover_contacts.py --spotify      # Phase 1 only
  python3 scene_intelligence/discover_contacts.py --youtube      # Phase 2 only
  python3 scene_intelligence/discover_contacts.py --dry-run      # Preview, don't save
  python3 scene_intelligence/discover_contacts.py --limit 75     # Cap at N (default 100)
"""

from __future__ import annotations

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
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
DISCOGS_TOKEN         = os.getenv("DISCOGS_TOKEN", "")

# Spotify
SPOTIFY_TOKEN_URL   = "https://accounts.spotify.com/api/token"
SPOTIFY_RELATED_URL = "https://api.spotify.com/v1/artists/{id}/related-artists"

# YouTube
YT_CHANNELS      = "https://www.googleapis.com/youtube/v3/channels"
YT_SUBSCRIPTIONS = "https://www.googleapis.com/youtube/v3/subscriptions"

# Discogs
DISCOGS_SEARCH         = "https://api.discogs.com/database/search"
DISCOGS_LABEL_RELEASES = "https://api.discogs.com/labels/{id}/releases"

# Thresholds
SPOTIFY_MIN_FREQ = 3   # must appear in 3+ seeds' related lists
YOUTUBE_MIN_FREQ = 2   # must appear in 2+ seeds' featured channels
DISCOGS_MIN_FREQ = 2   # must appear on 2+ scene labels
DEFAULT_LIMIT    = 100
BATCH_SIZE       = 50   # YouTube channels.list max per call
API_DELAY        = 1.0
TIMEOUT          = 10

# ---------------------------------------------------------------------------
# Shared utilities (imported from sibling modules)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key, CATEGORY_DEFAULT_SCORE


# ---------------------------------------------------------------------------
# Spotify auth (Client Credentials -- same pattern as enrich_spotify.py)
# ---------------------------------------------------------------------------
import base64

_token_cache: dict = {"access_token": "", "expires_at": 0.0}


def _get_spotify_token() -> str:
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
            print(f"  [SPOTIFY AUTH ERROR] HTTP {r.status_code}: {r.text[:200]}", flush=True)
            return ""
        data = r.json()
        _token_cache["access_token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
        return _token_cache["access_token"]
    except requests.RequestException as exc:
        print(f"  [SPOTIFY AUTH ERROR] {exc}", flush=True)
        return ""


def _spotify_get(url: str, params: dict | None = None) -> dict | None:
    token = _get_spotify_token()
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
            return r.json() if r.status_code == 200 else None
        if r.status_code == 401:
            _token_cache["access_token"] = ""
            token = _get_spotify_token()
            if not token:
                return None
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            return r.json() if r.status_code == 200 else None
        if r.status_code == 404:
            return None
        print(f"  [HTTP {r.status_code}]", flush=True)
        return None
    except requests.RequestException as exc:
        print(f"  [request error] {exc}", flush=True)
        return None


# ---------------------------------------------------------------------------
# YouTube HTTP helper (same pattern as enrich_youtube.py)
# ---------------------------------------------------------------------------

def _yt_get(url: str, params: dict) -> dict | None:
    params["key"] = YOUTUBE_API_KEY
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 403:
            error = r.json().get("error", {})
            reason = ""
            for e in error.get("errors", []):
                reason = e.get("reason", "")
            if reason == "quotaExceeded":
                print("\n  [QUOTA EXCEEDED] Daily limit reached.", flush=True)
                return {"_quota_exceeded": True}
            print(f"  [403] {error.get('message', 'Forbidden')}", flush=True)
            return None
        if r.status_code == 404:
            return None
        print(f"  [HTTP {r.status_code}]", flush=True)
        return None
    except requests.RequestException as exc:
        print(f"  [request error] {exc}", flush=True)
        return None


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_contacts() -> list[dict]:
    with open(ENRICHED_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(contacts: list[dict]) -> None:
    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def _build_existing_keys(contacts: list[dict]) -> dict:
    """Build dedup sets from existing contacts."""
    return {
        "names": {dedup_key(c.get("name", "")) for c in contacts if c.get("name")},
        "spotify_ids": {c["spotify_id"] for c in contacts if c.get("spotify_id")},
        "yt_ids": {c["youtube_channel_id"] for c in contacts if c.get("youtube_channel_id")},
    }


# ---------------------------------------------------------------------------
# Phase 1: Spotify Related Artists
# ---------------------------------------------------------------------------

def _fetch_related_artists(spotify_id: str) -> list[dict] | None:
    """Fetch related artists for a Spotify artist ID."""
    data = _spotify_get(SPOTIFY_RELATED_URL.format(id=spotify_id))
    if not data:
        return None
    return data.get("artists", [])


def discover_spotify(contacts: list[dict], existing: dict) -> list[dict]:
    """Discover new artists via Spotify Related Artists.

    Returns list of candidate dicts with _frequency and _discovered_via.
    """
    seeds = [c for c in contacts if c.get("spotify_id")]
    if not seeds:
        print("  No Spotify seeds found.")
        return []

    print(f"  Phase 1: {len(seeds)} Spotify seeds")

    # Track candidates by spotify_id
    candidates: dict[str, dict] = {}  # spotify_id -> candidate
    name_to_id: dict[str, str] = {}   # dedup_key(name) -> spotify_id

    for i, seed in enumerate(seeds):
        seed_name = seed.get("name", "")
        sid = seed["spotify_id"]

        print(f"    [{i+1:>3}/{len(seeds)}] {seed_name[:40]:<40}", end="  ", flush=True)

        related = _fetch_related_artists(sid)
        time.sleep(API_DELAY)

        if related is None:
            print("-- API error")
            continue

        new_count = 0
        dupe_count = 0

        for artist in related:
            artist_id = artist.get("id", "")
            artist_name = artist.get("name", "")
            if not artist_id or not artist_name:
                continue

            key = dedup_key(artist_name)

            # Skip if already in existing contacts
            if key in existing["names"] or artist_id in existing["spotify_ids"]:
                dupe_count += 1
                continue

            # Track candidate
            if artist_id in candidates:
                candidates[artist_id]["_frequency"] += 1
                candidates[artist_id]["_discovered_via"].append(seed_name)
            elif key in name_to_id:
                # Same name, different spotify_id (unlikely but handle it)
                existing_id = name_to_id[key]
                if existing_id in candidates:
                    candidates[existing_id]["_frequency"] += 1
                    candidates[existing_id]["_discovered_via"].append(seed_name)
            else:
                spotify_url = artist.get("external_urls", {}).get("spotify", "")
                candidates[artist_id] = {
                    "name": artist_name,
                    "spotify_id": artist_id,
                    "spotify_url": spotify_url,
                    "spotify_genres": ", ".join(artist.get("genres", [])),
                    "_frequency": 1,
                    "_discovered_via": [seed_name],
                    "_source": "spotify_related",
                }
                name_to_id[key] = artist_id
                new_count += 1

        print(f"+{new_count} new, {dupe_count} existing")

    # Filter by minimum frequency
    result = [c for c in candidates.values() if c["_frequency"] >= SPOTIFY_MIN_FREQ]
    result.sort(key=lambda c: (-c["_frequency"], c["name"].lower()))

    below = len(candidates) - len(result)
    print(f"  Spotify raw: {len(candidates)} unique candidates")
    print(f"  Spotify after freq >= {SPOTIFY_MIN_FREQ}: {len(result)} kept, {below} below threshold")

    return result


# ---------------------------------------------------------------------------
# Phase 2: YouTube Subscriptions
# ---------------------------------------------------------------------------

def _fetch_subscriptions(channel_id: str, max_pages: int = 2) -> list[str] | None:
    """Fetch public subscriptions for a channel. Returns list of subscribed channel IDs.
    Returns None on quota exceeded. Returns [] if subs are private or empty.
    Max 50 per page; max_pages caps total fetched (default: 100 subs per seed).
    """
    subscribed_ids = []
    page_token = None

    for _ in range(max_pages):
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token

        data = _yt_get(YT_SUBSCRIPTIONS, params)
        time.sleep(API_DELAY)

        if not data:
            return []  # Private subs or error — not fatal
        if data.get("_quota_exceeded"):
            return None

        for item in data.get("items", []):
            res_id = item.get("snippet", {}).get("resourceId", {})
            sub_cid = res_id.get("channelId", "")
            if sub_cid:
                subscribed_ids.append(sub_cid)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return subscribed_ids


def _enrich_channels(channel_ids: list[str]) -> dict[str, dict] | None:
    """Batch fetch snippet+statistics for discovered channels. Returns {id: info} or None on quota."""
    data = _yt_get(YT_CHANNELS, {
        "part": "snippet,statistics",
        "id": ",".join(channel_ids[:BATCH_SIZE]),
    })
    time.sleep(API_DELAY)

    if not data:
        return {}
    if data.get("_quota_exceeded"):
        return None

    result = {}
    for item in data.get("items", []):
        cid = item["id"]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        result[cid] = {
            "name": snippet.get("title", ""),
            "youtube_channel_id": cid,
            "youtube_url": f"https://www.youtube.com/channel/{cid}",
            "youtube_subscribers": stats.get("subscriberCount", ""),
            "youtube_views": stats.get("viewCount", ""),
            "youtube_videos": stats.get("videoCount", ""),
            "youtube_country": snippet.get("country", ""),
            "youtube_description": (snippet.get("description", "") or "")[:200],
            "youtube_custom_url": snippet.get("customUrl", ""),
        }

    return result


def discover_youtube(
    contacts: list[dict],
    existing: dict,
    already_discovered_names: set[str],
) -> list[dict]:
    """Discover new channels via YouTube public subscriptions.

    For each seed with a youtube_channel_id, fetches their public subscriptions.
    Channels subscribed to by multiple seeds are scene-relevant.
    Returns list of candidate dicts with _frequency and _discovered_via.
    """
    seeds = [c for c in contacts if c.get("youtube_channel_id")]
    if not seeds:
        print("  No YouTube seeds found.")
        return []

    print(f"  Phase 2: {len(seeds)} YouTube seeds")

    # Fetch subscriptions for each seed
    candidate_freq: dict[str, dict] = {}  # channel_id -> {_frequency, _discovered_via}
    seeds_with_subs = 0
    quota_hit = False

    for i, seed in enumerate(seeds):
        seed_name = seed.get("name", "")
        cid = seed["youtube_channel_id"]

        print(f"    [{i+1:>3}/{len(seeds)}] {seed_name[:40]:<40}", end="  ", flush=True)

        sub_ids = _fetch_subscriptions(cid)

        if sub_ids is None:
            print("-- QUOTA EXCEEDED")
            quota_hit = True
            break

        if not sub_ids:
            print("-- private or empty")
            continue

        seeds_with_subs += 1
        new_count = 0

        for sub_id in sub_ids:
            # Skip if already in existing contacts
            if sub_id in existing["yt_ids"]:
                continue
            if sub_id in candidate_freq:
                # Only count once per seed
                if seed_name not in candidate_freq[sub_id]["_discovered_via"]:
                    candidate_freq[sub_id]["_frequency"] += 1
                    candidate_freq[sub_id]["_discovered_via"].append(seed_name)
            else:
                candidate_freq[sub_id] = {
                    "_frequency": 1,
                    "_discovered_via": [seed_name],
                }
                new_count += 1

        print(f"+{len(sub_ids)} subs, {new_count} new")

    print(f"  Seeds with public subs: {seeds_with_subs}/{len(seeds)}")

    if not candidate_freq:
        print("  No subscriptions found.")
        return []

    # Filter by minimum frequency
    qualified_ids = [
        cid for cid, info in candidate_freq.items()
        if info["_frequency"] >= YOUTUBE_MIN_FREQ
    ]

    below = len(candidate_freq) - len(qualified_ids)
    print(f"  YouTube raw: {len(candidate_freq)} unique subscribed channels")
    print(f"  YouTube after freq >= {YOUTUBE_MIN_FREQ}: {len(qualified_ids)} kept, {below} below threshold")

    if not qualified_ids:
        return []

    # Enrich qualified channels to get their names and stats
    print(f"  Enriching {len(qualified_ids)} discovered channels...")
    candidates = []

    for batch_start in range(0, len(qualified_ids), BATCH_SIZE):
        batch = qualified_ids[batch_start:batch_start + BATCH_SIZE]
        result = _enrich_channels(batch)
        if result is None:
            print("  [QUOTA EXCEEDED] Partial enrichment.", flush=True)
            break

        for cid, info in result.items():
            name = info.get("name", "")
            if not name:
                continue

            key = dedup_key(name)
            # Skip if name matches existing contact or other discoveries
            if key in existing["names"] or key in already_discovered_names:
                continue

            freq_info = candidate_freq[cid]
            candidate = {
                **info,
                "_frequency": freq_info["_frequency"],
                "_discovered_via": freq_info["_discovered_via"],
                "_source": "youtube_subscriptions",
            }
            candidates.append(candidate)

    candidates.sort(key=lambda c: (-c["_frequency"], c["name"].lower()))
    print(f"  YouTube final (after name dedup): {len(candidates)} candidates")

    return candidates


# ---------------------------------------------------------------------------
# Phase 3: Discogs Label Rosters
# ---------------------------------------------------------------------------

_LABEL_SKIP = {
    "not on label", "not on label (self-released)", "white label",
    # Major labels that introduce too much mainstream noise
    "emi", "decca", "sony / atv music publishing", "deutsche grammophon",
    "warner classics", "bella musica edition gmbh",
}

_ARTIST_SKIP = {
    "unknown artist", "unknown", "various", "various artists", "va",
    "no artist", "anonymous", "n/a",
}


def _discogs_headers() -> dict:
    h = {"User-Agent": "InchOfShadowSceneIntelligence/1.0"}
    if DISCOGS_TOKEN:
        h["Authorization"] = f"Discogs token={DISCOGS_TOKEN}"
    return h


def _discogs_get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, params=params, headers=_discogs_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [rate limit] waiting 15s...", flush=True)
            time.sleep(15)
            r = requests.get(url, params=params, headers=_discogs_headers(), timeout=TIMEOUT)
            return r.json() if r.status_code == 200 else None
        return None
    except requests.RequestException:
        return None


def _collect_scene_labels(contacts: list[dict]) -> list[str]:
    """Collect unique label names from contacts' discogs_labels field."""
    labels = set()
    for c in contacts:
        raw = c.get("discogs_labels", "")
        if not raw:
            continue
        for label in raw.split(", "):
            label = label.strip()
            if label and label.lower() not in _LABEL_SKIP:
                labels.add(label)
    return sorted(labels)


def _search_label_id(label_name: str) -> int | None:
    """Search Discogs for a label and return its ID."""
    data = _discogs_get(DISCOGS_SEARCH, params={
        "q": label_name, "type": "label", "per_page": 3,
    })
    time.sleep(API_DELAY)
    if not data or not data.get("results"):
        return None

    # Take first result -- Discogs search is usually accurate for labels
    return data["results"][0].get("id")


def _fetch_label_artists(label_id: int) -> list[dict]:
    """Fetch artists from a label's release catalog (first 100 releases)."""
    data = _discogs_get(DISCOGS_LABEL_RELEASES.format(id=label_id), params={
        "per_page": 100, "page": 1,
    })
    time.sleep(API_DELAY)
    if not data:
        return []

    artists = []
    for release in data.get("releases", []):
        artist_name = release.get("artist", "")
        if not artist_name:
            continue
        # Clean up Discogs formatting
        artist_name = re.sub(r'\s*\(\d+\)\s*$', '', artist_name)  # remove (2), (3) etc.
        artist_name = artist_name.rstrip('*').strip()  # remove trailing asterisks
        # Skip generic / compilation names
        if artist_name.lower() in _ARTIST_SKIP or len(artist_name) < 2:
            continue
        artists.append({"name": artist_name})

    return artists


def discover_discogs(
    contacts: list[dict],
    existing: dict,
    already_discovered_names: set[str],
) -> list[dict]:
    """Discover new artists via Discogs label rosters.

    Finds labels from enriched contacts, fetches their rosters,
    tracks how many scene labels each artist appears on.
    """
    labels = _collect_scene_labels(contacts)
    if not labels:
        print("  No labels found in contacts.")
        return []

    print(f"  Phase 3: {len(labels)} scene labels to scan")

    # Track candidates by dedup_key(name) -> candidate info
    candidates: dict[str, dict] = {}

    for i, label_name in enumerate(labels):
        print(f"    [{i+1:>3}/{len(labels)}] {label_name[:40]:<40}", end="  ", flush=True)

        label_id = _search_label_id(label_name)
        if not label_id:
            print("-- not found on Discogs")
            continue

        artists = _fetch_label_artists(label_id)
        if not artists:
            print("-- no releases")
            continue

        new_count = 0
        for artist in artists:
            name = artist["name"]
            key = dedup_key(name)

            if not key:
                continue

            # Skip if already in existing contacts or already discovered
            if key in existing["names"] or key in already_discovered_names:
                continue

            if key in candidates:
                # Only count once per label
                if label_name not in candidates[key]["_discovered_via"]:
                    candidates[key]["_frequency"] += 1
                    candidates[key]["_discovered_via"].append(label_name)
            else:
                candidates[key] = {
                    "name": name,
                    "_frequency": 1,
                    "_discovered_via": [label_name],
                    "_source": "discogs_label",
                }
                new_count += 1

        print(f"+{new_count} new artists, {len(artists)} total on label")

    # Filter by minimum frequency
    result = [c for c in candidates.values() if c["_frequency"] >= DISCOGS_MIN_FREQ]
    result.sort(key=lambda c: (-c["_frequency"], c["name"].lower()))

    below = len(candidates) - len(result)
    print(f"  Discogs raw: {len(candidates)} unique candidates")
    print(f"  Discogs after freq >= {DISCOGS_MIN_FREQ}: {len(result)} kept, {below} below threshold")

    return result


# ---------------------------------------------------------------------------
# Merge, rank, and build contacts
# ---------------------------------------------------------------------------

def merge_and_rank(
    all_candidate_lists: list[list[dict]],
    limit: int,
) -> list[dict]:
    """Merge all discovery sources, cross-deduplicate, rank by frequency."""
    merged: dict[str, dict] = {}

    for cand_list in all_candidate_lists:
        for c in cand_list:
            key = dedup_key(c["name"])
            if key in merged:
                existing = merged[key]
                existing["_frequency"] += c["_frequency"]
                existing["_discovered_via"].extend(c["_discovered_via"])
                # Combine source labels
                sources = set(existing["_source"].split("+"))
                sources.add(c["_source"])
                existing["_source"] = "+".join(sorted(sources))
                # Merge any extra fields (YouTube, Spotify)
                for field in ("spotify_id", "spotify_url", "spotify_genres",
                              "youtube_channel_id", "youtube_url", "youtube_subscribers",
                              "youtube_views", "youtube_videos", "youtube_country",
                              "youtube_description", "youtube_custom_url"):
                    if c.get(field) and not existing.get(field):
                        existing[field] = c[field]
            else:
                merged[key] = c

    result = sorted(merged.values(), key=lambda c: (-c["_frequency"], c["name"].lower()))

    if len(result) > limit:
        result = result[:limit]

    return result


def _build_contact(candidate: dict) -> dict:
    """Convert discovery candidate into a full contact record."""
    source = candidate.get("_source", "")
    # Discogs label artists are most likely DJs/producers
    category = "dj" if ("spotify" in source or "discogs" in source or "youtube" in source) else "other"

    contact = {
        "name": candidate.get("name", ""),
        "category": category,
        "source": source,
        "url": candidate.get("spotify_url") or candidate.get("youtube_url", ""),
        "genre_main": "",
        "genre_sub": "",
        "location": "",
        "match_score": CATEGORY_DEFAULT_SCORE.get(category, "1"),
        "discogs_url": "",
        "discogs_genres": "",
        "discogs_country": "",
        "discogs_email": "",
        "discogs_releases": "",
        "discogs_last_year": "",
        "discogs_website": "",
        "discogs_labels": "",
        "discogs_found": False,
        "discogs_match_confidence": "",
        "verification_status": "?",
        "spotify_id": candidate.get("spotify_id", ""),
        "spotify_url": candidate.get("spotify_url", ""),
        "spotify_genres": candidate.get("spotify_genres", ""),
        "spotify_popularity": "",
        "spotify_followers": "",
        "youtube_channel_id": candidate.get("youtube_channel_id", ""),
        "youtube_url": candidate.get("youtube_url", ""),
        "youtube_subscribers": candidate.get("youtube_subscribers", ""),
        "youtube_views": candidate.get("youtube_views", ""),
        "youtube_videos": candidate.get("youtube_videos", ""),
        "youtube_country": candidate.get("youtube_country", ""),
        "youtube_description": candidate.get("youtube_description", ""),
        "youtube_custom_url": candidate.get("youtube_custom_url", ""),
        "discovery_frequency": candidate.get("_frequency", 0),
        "discovered_via": ", ".join(candidate.get("_discovered_via", [])[:10]),
    }

    return contact


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence -- Contact Discovery")
    print("=" * 42)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found.")
        sys.exit(1)

    args = set(sys.argv[1:])
    dry_run = "--dry-run" in args
    spotify_only = "--spotify" in args
    youtube_only = "--youtube" in args
    discogs_only = "--discogs" in args
    # If a specific phase is requested, only run that one
    specific = spotify_only or youtube_only or discogs_only
    run_spotify = spotify_only or not specific
    run_youtube = youtube_only or not specific
    run_discogs = discogs_only or not specific

    # Parse --limit N
    limit = DEFAULT_LIMIT
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--limit" and i < len(sys.argv) - 1:
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass

    contacts = _load_contacts()
    existing = _build_existing_keys(contacts)
    print(f"  Loaded {len(contacts)} existing contacts")
    print(f"  Dedup keys: {len(existing['names'])} names, {len(existing['spotify_ids'])} Spotify IDs, {len(existing['yt_ids'])} YouTube IDs")
    print(f"  Target: up to {limit} new contacts")
    if dry_run:
        print("  MODE: dry-run (no changes saved)")
    print()

    # Check API credentials
    if run_spotify and (not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET):
        print("WARNING: SPOTIFY_CLIENT_ID/SECRET not set. Skipping Spotify phase.")
        run_spotify = False
    if run_youtube and not YOUTUBE_API_KEY:
        print("WARNING: YOUTUBE_API_KEY not set. Skipping YouTube phase.")
        run_youtube = False
    if run_discogs and not DISCOGS_TOKEN:
        print("WARNING: DISCOGS_TOKEN not set. Skipping Discogs phase.")
        run_discogs = False

    all_cands: list[list[dict]] = []
    all_discovered_names: set[str] = set()

    # Phase 1: Spotify
    spotify_cands = []
    if run_spotify:
        print("--- Phase 1: Spotify Related Artists ---")
        token = _get_spotify_token()
        if not token:
            print("  ERROR: Spotify auth failed. Skipping.")
        else:
            print("  Spotify auth: OK")
            spotify_cands = discover_spotify(contacts, existing)
        all_cands.append(spotify_cands)
        all_discovered_names.update(dedup_key(c["name"]) for c in spotify_cands)
        print()

    # Phase 2: YouTube
    youtube_cands = []
    if run_youtube:
        print("--- Phase 2: YouTube Subscriptions ---")
        youtube_cands = discover_youtube(contacts, existing, all_discovered_names)
        all_cands.append(youtube_cands)
        all_discovered_names.update(dedup_key(c["name"]) for c in youtube_cands)
        print()

    # Phase 3: Discogs Label Rosters
    discogs_cands = []
    if run_discogs:
        print("--- Phase 3: Discogs Label Rosters ---")
        discogs_cands = discover_discogs(contacts, existing, all_discovered_names)
        all_cands.append(discogs_cands)
        print()

    # Merge and rank
    print("--- Merge & Rank ---")
    final = merge_and_rank(all_cands, limit)
    print(f"  Final: {len(final)} new contacts to add")

    if not final:
        print("  No new contacts discovered.")
        return

    # Preview top results
    print(f"\n  Top discoveries (by frequency):")
    for i, c in enumerate(final[:20]):
        freq = c["_frequency"]
        name = c["name"]
        source = c["_source"]
        via = ", ".join(c["_discovered_via"][:3])
        if len(c["_discovered_via"]) > 3:
            via += f" +{len(c['_discovered_via']) - 3} more"
        print(f"    {i+1:>3}. [{freq}x] {name:<35} ({source}) via: {via}")

    if len(final) > 20:
        print(f"    ... and {len(final) - 20} more")

    # Save
    if dry_run:
        print(f"\n  DRY RUN -- would add {len(final)} contacts. No changes saved.")
        return

    new_contacts = [_build_contact(c) for c in final]
    contacts.extend(new_contacts)
    _save(contacts)

    # Summary
    by_source = {}
    for c in new_contacts:
        s = c["source"]
        by_source[s] = by_source.get(s, 0) + 1

    print()
    print("=" * 42)
    print(f"  Added: {len(new_contacts)} new contacts")
    for src, count in sorted(by_source.items()):
        print(f"    {src}: {count}")
    print(f"  Total contacts: {len(contacts)}")
    print(f"  Saved to: enriched_contacts.json")
    print()
    print("  Next: python3 scene_intelligence/push_to_sheets.py")
    print()


if __name__ == "__main__":
    main()
