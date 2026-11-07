"""
scene_intelligence/enrich_youtube.py
--------------------------------------
Tool 1 -- Scene Intelligence Engine: YouTube Channel Enricher

Three-phase enrichment using YouTube Data API v3:
  1. Direct  -- contacts with existing YouTube URLs -> channels.list (1 unit/50 IDs)
  2. Search  -- contacts without YouTube URLs -> search.list (100 units each!)
  3. Activity -- contacts with channel IDs -> playlistItems.list (1 unit each)

New fields added:
  youtube_channel_id, youtube_url, youtube_subscribers, youtube_views,
  youtube_videos, youtube_country, youtube_description, youtube_last_upload,
  youtube_custom_url, youtube_match_confidence

Usage:
  python3 scene_intelligence/enrich_youtube.py              # Phase 1 only (direct, cheap)
  python3 scene_intelligence/enrich_youtube.py --search     # Phase 1 + Phase 2
  python3 scene_intelligence/enrich_youtube.py --activity   # Phase 1 + Phase 3
  python3 scene_intelligence/enrich_youtube.py --all        # All phases
  python3 scene_intelligence/enrich_youtube.py --force      # Re-enrich already-enriched
"""

from __future__ import annotations

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
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

YT_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"
YT_SEARCH   = "https://www.googleapis.com/youtube/v3/search"
YT_PLAYLIST = "https://www.googleapis.com/youtube/v3/playlistItems"

API_DELAY  = 1.0    # 1s between calls (conservative)
TIMEOUT    = 10
BATCH_SIZE = 50     # channels.list supports up to 50 IDs per call

SEARCH_CONFIDENCE_MIN = 80  # minimum SequenceMatcher % for search matches


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _yt_get(url: str, params: dict) -> dict | None:
    """Make a YouTube API request. Returns parsed JSON or None."""
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
                print("\n  [QUOTA EXCEEDED] Daily limit reached. Saving progress.", flush=True)
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
# YouTube URL parsing
# ---------------------------------------------------------------------------

def _parse_youtube_url(url: str) -> dict:
    """Parse a YouTube URL and return channel identification info.

    Returns dict with:
      'channel_id': str or ''     -- direct UCxxx ID if available
      'handle': str or ''         -- @handle if available
      'username': str or ''       -- legacy /user/name
      'custom_name': str or ''    -- /c/name or bare /name
    """
    result = {"channel_id": "", "handle": "", "username": "", "custom_name": ""}
    if not url:
        return result

    url = url.strip().rstrip("/")

    # Strip /videos or /featured suffix
    url = re.sub(r'/(videos|featured|about|playlists|shorts)$', '', url)

    # Format 1: /channel/UCxxxxxxxx
    m = re.search(r'/channel/(UC[\w-]+)', url)
    if m:
        result["channel_id"] = m.group(1)
        return result

    # Format 2: /@handle
    m = re.search(r'/@([\w.-]+)', url)
    if m:
        result["handle"] = m.group(1)
        return result

    # Format 3: /c/customname
    m = re.search(r'/c/([\w.-]+)', url)
    if m:
        result["custom_name"] = m.group(1)
        return result

    # Format 4: /user/username
    m = re.search(r'/user/([\w.-]+)', url)
    if m:
        result["username"] = m.group(1)
        return result

    # Format 5: bare path youtube.com/name
    m = re.search(r'youtube\.com/([\w.-]+)$', url, re.IGNORECASE)
    if m:
        name = m.group(1)
        if name.lower() not in ("watch", "playlist", "feed", "results", "shorts", "live"):
            result["custom_name"] = name
        return result

    return result


def _resolve_channel_id(parsed: dict) -> str | None:
    """Resolve a parsed YouTube URL to a channel ID using the API.

    For direct channel IDs, returns immediately (no API call).
    For handles/usernames/custom names, uses channels.list (1 unit).
    """
    if parsed["channel_id"]:
        return parsed["channel_id"]

    # Handle (@name) -- use forHandle parameter
    if parsed["handle"]:
        data = _yt_get(YT_CHANNELS, {"part": "id", "forHandle": parsed["handle"]})
        time.sleep(API_DELAY)
        if data and not data.get("_quota_exceeded") and data.get("items"):
            return data["items"][0]["id"]
        return None

    # Legacy username -- use forUsername parameter
    if parsed["username"]:
        data = _yt_get(YT_CHANNELS, {"part": "id", "forUsername": parsed["username"]})
        time.sleep(API_DELAY)
        if data and not data.get("_quota_exceeded") and data.get("items"):
            return data["items"][0]["id"]
        return None

    # Custom name or bare path -- try as handle first, then username
    if parsed["custom_name"]:
        data = _yt_get(YT_CHANNELS, {"part": "id", "forHandle": parsed["custom_name"]})
        time.sleep(API_DELAY)
        if data and not data.get("_quota_exceeded") and data.get("items"):
            return data["items"][0]["id"]

        data = _yt_get(YT_CHANNELS, {"part": "id", "forUsername": parsed["custom_name"]})
        time.sleep(API_DELAY)
        if data and not data.get("_quota_exceeded") and data.get("items"):
            return data["items"][0]["id"]
        return None

    return None


# ---------------------------------------------------------------------------
# Batch channel stats
# ---------------------------------------------------------------------------

def _fetch_channel_stats(channel_ids: list[str]) -> dict[str, dict] | None:
    """Fetch stats for up to 50 channels in one API call (1 unit).

    Returns dict mapping channel_id -> stats dict, or None on quota exceeded.
    """
    if not channel_ids:
        return {}

    data = _yt_get(YT_CHANNELS, {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(channel_ids[:BATCH_SIZE]),
    })
    time.sleep(API_DELAY)

    if not data:
        return {}
    if data.get("_quota_exceeded"):
        return None  # sentinel: caller must save and exit

    result = {}
    for item in data.get("items", []):
        cid = item["id"]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})

        result[cid] = {
            "youtube_channel_id": cid,
            "youtube_url": f"https://www.youtube.com/channel/{cid}",
            "youtube_subscribers": stats.get("subscriberCount", ""),
            "youtube_views": stats.get("viewCount", ""),
            "youtube_videos": stats.get("videoCount", ""),
            "youtube_country": snippet.get("country", ""),
            "youtube_description": (snippet.get("description", "") or "")[:200],
            "youtube_custom_url": snippet.get("customUrl", ""),
            "_uploads_playlist": content.get("relatedPlaylists", {}).get("uploads", ""),
        }

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_youtube_urls(contact: dict) -> list[str]:
    """Gather all YouTube URLs from a contact's various fields."""
    urls = []
    for field in ("url", "discogs_youtube"):
        val = contact.get(field, "") or ""
        if "youtube.com" in val.lower():
            urls.append(val)
    return urls


def _save(contacts: list[dict]) -> None:
    """Save contacts to enriched_contacts.json, stripping transient fields."""
    for c in contacts:
        c.pop("_uploads_playlist", None)

    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Phase 1: Direct enrichment
# ---------------------------------------------------------------------------

def phase_direct(contacts: list[dict], force: bool = False) -> tuple[int, bool]:
    """Enrich contacts that already have YouTube URLs.

    Returns (enriched_count, quota_exceeded).
    """
    targets = []
    for c in contacts:
        if not force and c.get("youtube_subscribers"):
            continue
        yt_urls = _collect_youtube_urls(c)
        if yt_urls:
            targets.append((c, yt_urls))

    if not targets:
        print("  No contacts with YouTube URLs to enrich.")
        return 0, False

    print(f"  Phase 1: {len(targets)} contacts with YouTube URLs")

    # Step 1: Resolve all URLs to channel IDs
    print("  Resolving channel IDs...", flush=True)
    resolved: list[tuple[dict, str]] = []

    for contact, yt_urls in targets:
        channel_id = None
        for yt_url in yt_urls:
            parsed = _parse_youtube_url(yt_url)
            if parsed["channel_id"]:
                channel_id = parsed["channel_id"]
                break
            cid = _resolve_channel_id(parsed)
            if cid:
                channel_id = cid
                break

        name = contact.get("name", "")
        if channel_id:
            resolved.append((contact, channel_id))
        else:
            print(f"    {name[:40]:<40}  -- could not resolve channel ID", flush=True)

    print(f"  Resolved {len(resolved)} channel IDs")

    # Step 2: Batch-fetch channel stats (50 at a time)
    enriched = 0
    for batch_start in range(0, len(resolved), BATCH_SIZE):
        batch = resolved[batch_start:batch_start + BATCH_SIZE]
        batch_ids = [cid for _, cid in batch]

        stats = _fetch_channel_stats(batch_ids)
        if stats is None:
            _save(contacts)
            return enriched, True

        for idx_in_batch, (contact, cid) in enumerate(batch):
            name = contact.get("name", "")
            idx = batch_start + idx_in_batch + 1

            if cid in stats:
                channel_data = stats[cid]
                uploads_pl = channel_data.pop("_uploads_playlist", "")
                contact.update(channel_data)
                if uploads_pl:
                    contact["_uploads_playlist"] = uploads_pl

                enriched += 1
                subs = channel_data.get("youtube_subscribers", "?")
                vids = channel_data.get("youtube_videos", "?")
                country = channel_data.get("youtube_country", "")
                parts = []
                if subs:
                    parts.append(f"{subs} subs")
                if vids:
                    parts.append(f"{vids} videos")
                if country:
                    parts.append(country)
                print(f"    [{idx:>3}/{len(resolved)}] {name[:40]:<40}  +{len(channel_data)} ({', '.join(parts)})")
            else:
                print(f"    [{idx:>3}/{len(resolved)}] {name[:40]:<40}  -- not in API response")

        _save(contacts)

    return enriched, False


# ---------------------------------------------------------------------------
# Phase 2: Search enrichment
# ---------------------------------------------------------------------------

CATEGORY_SEARCH_TERMS: dict[str, str] = {
    "dj":       "DJ music producer",
    "label":    "record label music",
    "media":    "music media channel",
    "venue":    "music venue club",
    "promoter": "music promoter events",
}


def phase_search(contacts: list[dict], force: bool = False) -> tuple[int, int, bool]:
    """Search YouTube for contacts without YouTube URLs.

    Returns (found_count, not_found_count, quota_exceeded).
    """
    targets = []
    for c in contacts:
        if not force and c.get("youtube_channel_id"):
            continue
        yt_urls = _collect_youtube_urls(c)
        if yt_urls:
            continue
        targets.append(c)

    if not targets:
        print("  No contacts to search.")
        return 0, 0, False

    # Budget: 10,000 units/day, leave 500 buffer
    max_searches = min(len(targets), 95)
    print(f"  Phase 2: {len(targets)} contacts to search (100 units each!)")
    print(f"  Will search up to {max_searches} contacts (quota budget)")

    found = 0
    not_found = 0

    for i, contact in enumerate(targets[:max_searches]):
        name = contact.get("name", "")
        cat = contact.get("category", "")

        search_name = re.sub(r'[_\.]+', ' ', name).strip()
        keyword = CATEGORY_SEARCH_TERMS.get(cat, "music")
        query = f"{search_name} {keyword}"

        print(f"    [{i+1:>3}/{max_searches}] {name[:40]:<40}", end="  ", flush=True)

        data = _yt_get(YT_SEARCH, {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": 3,
        })
        time.sleep(API_DELAY)

        if not data:
            not_found += 1
            print("-- API error")
            continue
        if data.get("_quota_exceeded"):
            _save(contacts)
            return found, not_found, True

        items = data.get("items", [])
        if not items:
            not_found += 1
            print("-- no results")
            continue

        # Find best match by name similarity
        name_norm = re.sub(r'[^a-z0-9]', '', name.lower())
        best_item = None
        best_confidence = 0

        for item in items:
            channel_title = item.get("snippet", {}).get("channelTitle", "")
            # Also check the title field (search results use 'title' in snippet)
            if not channel_title:
                channel_title = item.get("snippet", {}).get("title", "")
            title_norm = re.sub(r'[^a-z0-9]', '', channel_title.lower())
            confidence = round(
                difflib.SequenceMatcher(None, name_norm, title_norm).ratio() * 100
            )
            if confidence > best_confidence:
                best_confidence = confidence
                best_item = item

        if best_confidence < SEARCH_CONFIDENCE_MIN or not best_item:
            not_found += 1
            best_name = best_item.get("snippet", {}).get("title", "?") if best_item else "?"
            print(f"-- low confidence ({best_confidence}% for '{best_name}')")
            continue

        # Got a match -- get channel ID
        channel_id = best_item.get("id", {}).get("channelId", "")
        if not channel_id:
            channel_id = best_item.get("snippet", {}).get("channelId", "")

        if not channel_id:
            not_found += 1
            print("-- no channel ID in result")
            continue

        # Fetch full channel stats (1 unit)
        stats = _fetch_channel_stats([channel_id])
        if stats is None:
            _save(contacts)
            return found, not_found, True

        if channel_id in stats:
            channel_data = stats[channel_id]
            uploads_pl = channel_data.pop("_uploads_playlist", "")
            channel_data["youtube_match_confidence"] = best_confidence
            contact.update(channel_data)
            if uploads_pl:
                contact["_uploads_playlist"] = uploads_pl

            found += 1
            subs = channel_data.get("youtube_subscribers", "?")
            matched_name = best_item.get("snippet", {}).get("title", "")
            print(f"FOUND {best_confidence}% ({matched_name}) {subs} subs")
        else:
            not_found += 1
            print("-- stats fetch failed")

        # Save periodically
        if (i + 1) % 10 == 0:
            _save(contacts)

    _save(contacts)
    return found, not_found, False


# ---------------------------------------------------------------------------
# Phase 3: Activity check
# ---------------------------------------------------------------------------

def phase_activity(contacts: list[dict]) -> tuple[int, bool]:
    """Fetch last upload date for contacts with channel IDs.

    Returns (updated_count, quota_exceeded).
    """
    targets = []
    for c in contacts:
        if not c.get("youtube_channel_id"):
            continue
        if c.get("youtube_last_upload"):
            continue
        targets.append(c)

    if not targets:
        print("  No contacts need activity check.")
        return 0, False

    print(f"  Phase 3: {len(targets)} contacts to check for recent activity")

    # Ensure we have uploads playlist IDs (batch-fetch if missing)
    need_playlist = [c for c in targets if not c.get("_uploads_playlist")]
    if need_playlist:
        print(f"  Fetching uploads playlists for {len(need_playlist)} contacts...", flush=True)
        for batch_start in range(0, len(need_playlist), BATCH_SIZE):
            batch = need_playlist[batch_start:batch_start + BATCH_SIZE]
            ids = [c["youtube_channel_id"] for c in batch]

            data = _yt_get(YT_CHANNELS, {
                "part": "contentDetails",
                "id": ",".join(ids),
            })
            time.sleep(API_DELAY)

            if not data:
                continue
            if data.get("_quota_exceeded"):
                _save(contacts)
                return 0, True

            id_to_playlist = {}
            for item in data.get("items", []):
                cid = item["id"]
                pl = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads", "")
                if pl:
                    id_to_playlist[cid] = pl

            for c in batch:
                cid = c["youtube_channel_id"]
                if cid in id_to_playlist:
                    c["_uploads_playlist"] = id_to_playlist[cid]

    # Fetch most recent upload from each playlist
    updated = 0
    for i, contact in enumerate(targets):
        playlist_id = contact.get("_uploads_playlist", "")
        if not playlist_id:
            continue

        name = contact.get("name", "")
        print(f"    [{i+1:>3}/{len(targets)}] {name[:40]:<40}", end="  ", flush=True)

        data = _yt_get(YT_PLAYLIST, {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 1,
        })
        time.sleep(API_DELAY)

        if not data:
            print("-- fetch failed")
            continue
        if data.get("_quota_exceeded"):
            _save(contacts)
            return updated, True

        items = data.get("items", [])
        if items:
            published = items[0].get("snippet", {}).get("publishedAt", "")
            if published:
                contact["youtube_last_upload"] = published[:10]
                updated += 1
                print(f"last upload: {published[:10]}")
            else:
                print("-- no date")
        else:
            contact["youtube_last_upload"] = "no uploads"
            print("-- no uploads")

        if (i + 1) % 25 == 0:
            _save(contacts)

    _save(contacts)
    return updated, False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence -- YouTube Channel Enricher")
    print("=" * 50)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found. Run enrich_contacts.py first.")
        sys.exit(1)

    if not YOUTUBE_API_KEY:
        print("ERROR: YOUTUBE_API_KEY not set in .env")
        sys.exit(1)

    with open(ENRICHED_FILE, encoding="utf-8") as f:
        contacts = json.load(f)
    print(f"  Loaded {len(contacts)} contacts from enriched_contacts.json")

    has_yt_url = sum(1 for c in contacts if _collect_youtube_urls(c))
    has_yt_data = sum(1 for c in contacts if c.get("youtube_subscribers"))
    print(f"  Contacts with YouTube URLs: {has_yt_url}")
    print(f"  Already enriched: {has_yt_data}")

    args = set(sys.argv[1:])
    force = "--force" in args
    run_search = "--search" in args or "--all" in args
    run_activity = "--activity" in args or "--all" in args

    quota_exceeded = False
    direct_count = 0
    search_found = 0
    search_missed = 0
    activity_count = 0
    skipped = has_yt_data if not force else 0

    # Phase 1: Direct enrichment (always runs)
    print(f"\n--- Phase 1: Direct enrichment (contacts with YouTube URLs) ---")
    direct_count, quota_exceeded = phase_direct(contacts, force=force)
    print(f"  Direct: {direct_count} contacts enriched")

    # Phase 2: Search (opt-in)
    if run_search and not quota_exceeded:
        print(f"\n--- Phase 2: YouTube search (100 units per search!) ---")
        search_found, search_missed, quota_exceeded = phase_search(contacts, force=force)
        print(f"  Search: {search_found} found, {search_missed} not found")
    elif run_search and quota_exceeded:
        print(f"\n--- Phase 2: SKIPPED (quota exceeded) ---")

    # Phase 3: Activity check (opt-in)
    if run_activity and not quota_exceeded:
        print(f"\n--- Phase 3: Recent activity check ---")
        activity_count, quota_exceeded = phase_activity(contacts)
        print(f"  Activity: {activity_count} contacts updated with last upload date")
    elif run_activity and quota_exceeded:
        print(f"\n--- Phase 3: SKIPPED (quota exceeded) ---")

    # Final save
    _save(contacts)

    # Summary
    total = direct_count + search_found + activity_count
    print()
    print("=" * 50)
    print(f"  Enriched (direct): {direct_count}")
    if run_search:
        print(f"  Found (search):    {search_found}")
        print(f"  Not found:         {search_missed}")
    if run_activity:
        print(f"  Activity updated:  {activity_count}")
    print(f"  Skipped (done):    {skipped}")
    print(f"  Total updated:     {total}")
    if quota_exceeded:
        print(f"  WARNING: Quota exceeded -- progress saved, re-run tomorrow")

    # Coverage summary
    has_yt = sum(1 for c in contacts if c.get("youtube_channel_id"))
    has_subs = sum(1 for c in contacts if c.get("youtube_subscribers"))
    has_upload = sum(1 for c in contacts if c.get("youtube_last_upload"))
    print(f"\n  YouTube coverage:")
    print(f"    Channel IDs:  {has_yt}")
    print(f"    Subscribers:  {has_subs}")
    print(f"    Last upload:  {has_upload}")
    print(f"  Saved to: enriched_contacts.json")
    print()


if __name__ == "__main__":
    main()
