"""
scene_intelligence/discover_curators.py
----------------------------------------
Tool 1 -- Scene Intelligence Engine: Playlist Curator Discovery

Finds playlist curators on Spotify and SoundCloud who curate playlists
matching Inch of Shadow's genre keywords, and adds them to
enriched_contacts.json as category="curator".

Usage:
  python3 scene_intelligence/discover_curators.py                   # Both phases
  python3 scene_intelligence/discover_curators.py --spotify          # Phase 1 only
  python3 scene_intelligence/discover_curators.py --soundcloud       # Phase 2 only
  python3 scene_intelligence/discover_curators.py --dry-run          # Preview, don't save
  python3 scene_intelligence/discover_curators.py --limit 50         # Cap at N owners per platform
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key
from curator_config import (  # type: ignore[import-not-found]
    GENRE_KEYWORDS,
    match_genres,
    is_editorial_owner,
    SPOTIFY_MIN_PLAYLIST_FOLLOWERS,
    SPOTIFY_MIN_OWNER_TOTAL,
    SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS,
    SOUNDCLOUD_MIN_OWNER_TOTAL,
)


# ---------------------------------------------------------------------------
# Pure-logic helpers (unit-tested)
# ---------------------------------------------------------------------------

def aggregate_playlists_by_owner(playlists: list[dict]) -> dict[str, dict]:
    """Group playlists by owner_id. Returns {owner_id: aggregate_info}.

    Each playlist dict must have: id, name, followers, owner_id, owner_name,
    matched_genres, url. Optional: owner_permalink_url, owner_followers.
    """
    owners: dict[str, dict] = {}
    for p in playlists:
        oid = p["owner_id"]
        if oid not in owners:
            owners[oid] = {
                "owner_id": oid,
                "owner_name": p["owner_name"],
                "owner_permalink_url": p.get("owner_permalink_url", ""),
                "owner_followers": p.get("owner_followers", 0),
                "playlists": [],
                "playlist_count": 0,
                "playlist_total_followers": 0,
                "top_playlist_name": "",
                "top_playlist_followers": 0,
                "top_playlist_url": "",
                "playlist_genres": set(),
                "playlist_urls": [],
                "discovered_via": set(),
            }
        o = owners[oid]
        o["playlists"].append(p)
        o["playlist_count"] += 1
        o["playlist_total_followers"] += p["followers"]
        o["playlist_urls"].append(p["url"])
        for g in p["matched_genres"]:
            o["playlist_genres"].add(g)
            o["discovered_via"].add(f"search:{g}")
        if p["followers"] > o["top_playlist_followers"]:
            o["top_playlist_followers"] = p["followers"]
            o["top_playlist_name"] = p["name"]
            o["top_playlist_url"] = p["url"]

    # Convert sets to sorted lists for deterministic output.
    for o in owners.values():
        o["playlist_genres"] = sorted(o["playlist_genres"])
        o["discovered_via"] = sorted(o["discovered_via"])
    return owners


def build_candidate_row(owner: dict, platform: str) -> dict:
    """Convert an aggregated owner dict into an enriched_contacts.json row."""
    row = {
        "name": owner["owner_name"],
        "category": "curator",
        "sub_type": platform,
        "source": "curator_discovery",
        "url": "",
        "genre_main": "Electronic",
        "genre_sub": " / ".join(owner["playlist_genres"]),
        "location": "",
        "match_score": "3",
        "playlist_count": owner["playlist_count"],
        "playlist_total_followers": owner["playlist_total_followers"],
        "top_playlist_name": owner["top_playlist_name"],
        "top_playlist_followers": owner["top_playlist_followers"],
        "top_playlist_url": owner["top_playlist_url"],
        "playlist_genres": ", ".join(owner["playlist_genres"]),
        "playlist_urls": " | ".join(owner["playlist_urls"]),
        "discovered_via": ",".join(owner["discovered_via"]),
    }
    if platform == "spotify":
        row["spotify_id"] = owner["owner_id"]
        row["spotify_url"] = f"https://open.spotify.com/user/{owner['owner_id']}"
        row["url"] = row["spotify_url"]
    elif platform == "soundcloud":
        row["soundcloud_user_id"] = owner["owner_id"]
        row["soundcloud_url"] = owner.get("owner_permalink_url", "")
        row["soundcloud_followers"] = str(owner.get("owner_followers", 0))
        row["url"] = row["soundcloud_url"]
    return row


def filter_existing(candidates: list[dict], existing: dict) -> list[dict]:
    """Drop candidates that already exist in the contacts file.

    existing is expected to have:
      names:                 set of dedup_key(name)
      spotify_ids:           set of spotify user ids
      soundcloud_user_ids:   set of soundcloud user ids (as strings)
    """
    fresh = []
    for c in candidates:
        if dedup_key(c["name"]) in existing["names"]:
            continue
        sid = c.get("spotify_id", "")
        if sid and sid in existing["spotify_ids"]:
            continue
        scid = str(c.get("soundcloud_user_id", "") or "")
        if scid and scid in existing["soundcloud_user_ids"]:
            continue
        fresh.append(c)
    return fresh


# ---------------------------------------------------------------------------
# Spotify API layer (reuses client-credentials pattern from enrich_spotify.py)
# ---------------------------------------------------------------------------

import base64
import json
import os
import time

import requests
from dotenv import load_dotenv

BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

load_dotenv(BASE_DIR / ".env")
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SC_CLIENT_ID          = os.getenv("SOUNDCLOUD_CLIENT_ID", "")
SC_CLIENT_SECRET      = os.getenv("SOUNDCLOUD_CLIENT_SECRET", "")

SPOTIFY_TOKEN_URL  = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_PLAYLIST_URL = "https://api.spotify.com/v1/playlists/{id}"

SC_TOKEN_URL   = "https://secure.soundcloud.com/oauth/token"
SC_PLAYLISTS_URL = "https://api.soundcloud.com/playlists"

API_DELAY  = 1.0
TIMEOUT    = 10

_spotify_token: dict = {"access_token": "", "expires_at": 0.0}
_sc_token: dict      = {"access_token": "", "expires_at": 0.0}


def _spotify_auth() -> str:
    if _spotify_token["access_token"] and time.time() < _spotify_token["expires_at"]:
        return _spotify_token["access_token"]
    creds = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    try:
        r = requests.post(
            SPOTIFY_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {creds}"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"  [SPOTIFY AUTH] HTTP {r.status_code}: {r.text[:200]}", flush=True)
            return ""
        data = r.json()
        _spotify_token["access_token"] = data["access_token"]
        _spotify_token["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
        return _spotify_token["access_token"]
    except requests.RequestException as exc:
        print(f"  [SPOTIFY AUTH ERROR] {exc}", flush=True)
        return ""


def _spotify_get(url: str, params: dict | None = None) -> dict | None:
    token = _spotify_auth()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 5))
            print(f"  [RATE LIMIT] waiting {retry}s...")
            time.sleep(retry)
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            return r.json() if r.status_code == 200 else None
        if r.status_code == 401:
            _spotify_token["access_token"] = ""
            token = _spotify_auth()
            if not token:
                return None
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            return r.json() if r.status_code == 200 else None
        if r.status_code == 404:
            return None
        print(f"  [HTTP {r.status_code}] {url}")
        return None
    except requests.RequestException as exc:
        print(f"  [request error] {exc}")
        return None


def search_spotify_playlists(keyword: str, limit: int = 50) -> list[dict]:
    """Search Spotify playlists for a keyword. Returns raw playlist summaries.

    Spotify /search returns up to 50 per call; we make one call per keyword.
    Note: Some API keys have a max limit of 10; we cap conservatively.
    """
    data = _spotify_get(SPOTIFY_SEARCH_URL, params={
        "q": keyword,
        "type": "playlist",
        "limit": min(limit, 10),
    })
    time.sleep(API_DELAY)
    if not data:
        return []
    items = (data.get("playlists") or {}).get("items") or []
    return [p for p in items if p]


def fetch_spotify_playlist_detail(playlist_id: str) -> dict | None:
    """Fetch playlist detail including followers.total and owner info."""
    data = _spotify_get(
        SPOTIFY_PLAYLIST_URL.format(id=playlist_id),
        params={"fields": "id,name,description,followers.total,owner(id,display_name,external_urls)"},
    )
    time.sleep(API_DELAY)
    return data


# ---------------------------------------------------------------------------
# Phase 1: Spotify curator discovery
# ---------------------------------------------------------------------------


def discover_spotify_curators(limit: int) -> list[dict]:
    """Run Spotify phase. Returns list of candidate rows (not yet deduped)."""
    print(f"  Phase 1: Spotify playlist search ({len(GENRE_KEYWORDS)} keywords)")
    all_playlists: dict[str, dict] = {}  # playlist_id -> normalized summary

    for i, keyword in enumerate(GENRE_KEYWORDS):
        print(f"    [{i+1:>2}/{len(GENRE_KEYWORDS)}] q={keyword!r:<22}", end="  ", flush=True)
        hits = search_spotify_playlists(keyword, limit=50)
        added = 0
        for p in hits:
            pid = p.get("id")
            if not pid or pid in all_playlists:
                continue
            owner = p.get("owner") or {}
            owner_id = owner.get("id", "")
            owner_name = owner.get("display_name", "") or owner_id
            if is_editorial_owner(owner_name, owner_id):
                continue
            # Genre filter against the playlist name + description
            matched = match_genres(p.get("name", ""), p.get("description", "") or "")
            if keyword not in matched:
                matched.append(keyword)
            all_playlists[pid] = {
                "id": pid,
                "name": p.get("name", ""),
                "description": p.get("description", "") or "",
                "owner_id": owner_id,
                "owner_name": owner_name,
                "matched_genres": matched,
                "url": (p.get("external_urls") or {}).get("spotify", f"https://open.spotify.com/playlist/{pid}"),
            }
            added += 1
        print(f"+{added} new playlists")

    print(f"  Playlists gathered: {len(all_playlists)}")

    # Fetch follower counts (search endpoint doesn't include them)
    print(f"  Fetching follower counts for {len(all_playlists)} playlists...")
    qualifying: list[dict] = []
    failed_detail_fetches = 0
    for i, (pid, summary) in enumerate(all_playlists.items()):
        detail = fetch_spotify_playlist_detail(pid)
        if not detail:
            failed_detail_fetches += 1
            continue
        followers = (detail.get("followers") or {}).get("total") or 0
        if followers < SPOTIFY_MIN_PLAYLIST_FOLLOWERS:
            continue
        summary["followers"] = followers
        qualifying.append(summary)
        if (i + 1) % 25 == 0:
            print(f"    fetched {i+1}/{len(all_playlists)}, qualifying so far: {len(qualifying)}")

    if failed_detail_fetches:
        print(f"  Detail fetch failures: {failed_detail_fetches}")
    print(f"  Qualifying playlists (>= {SPOTIFY_MIN_PLAYLIST_FOLLOWERS} followers): {len(qualifying)}")

    owners = aggregate_playlists_by_owner(qualifying)
    print(f"  Unique owners before filter: {len(owners)}")

    candidates: list[dict] = []
    for owner in owners.values():
        if owner["playlist_total_followers"] < SPOTIFY_MIN_OWNER_TOTAL:
            continue
        candidates.append(build_candidate_row(owner, platform="spotify"))

    candidates.sort(key=lambda c: -c["playlist_total_followers"])
    candidates = candidates[:limit]
    print(f"  Spotify candidates kept: {len(candidates)}")
    return candidates


# ---------------------------------------------------------------------------
# SoundCloud API layer (reuses client-credentials pattern from enrich_soundcloud.py)
# ---------------------------------------------------------------------------

def _sc_auth() -> str:
    if _sc_token["access_token"] and time.time() < _sc_token["expires_at"]:
        return _sc_token["access_token"]
    creds = base64.b64encode(f"{SC_CLIENT_ID}:{SC_CLIENT_SECRET}".encode()).decode()
    try:
        r = requests.post(
            SC_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {creds}"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"  [SC AUTH] HTTP {r.status_code}: {r.text[:200]}", flush=True)
            return ""
        data = r.json()
        _sc_token["access_token"] = data["access_token"]
        _sc_token["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
        return _sc_token["access_token"]
    except requests.RequestException as exc:
        print(f"  [SC AUTH ERROR] {exc}", flush=True)
        return ""


def _sc_get(url: str, params: dict | None = None) -> list | dict | None:
    token = _sc_auth()
    if not token:
        return None
    headers = {"Authorization": f"OAuth {token}"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [SC RATE LIMIT] sleeping 10s", flush=True)
            time.sleep(10)
            return None
        if r.status_code in (401, 404):
            if r.status_code == 401:
                _sc_token["access_token"] = ""
            return None
        print(f"  [SC HTTP {r.status_code}] {url}", flush=True)
        return None
    except requests.RequestException as exc:
        print(f"  [sc request error] {exc}", flush=True)
        return None


def search_soundcloud_playlists(keyword: str, limit: int = 50) -> list[dict]:
    """Search SoundCloud playlists. Returns playlists with nested user info."""
    data = _sc_get(SC_PLAYLISTS_URL, params={"q": keyword, "limit": min(limit, 200)})
    time.sleep(API_DELAY)
    if not data:
        return []
    if isinstance(data, dict):
        data = data.get("collection") or []
    return [p for p in data if p]


# ---------------------------------------------------------------------------
# Phase 2: SoundCloud curator discovery
# ---------------------------------------------------------------------------

def discover_soundcloud_curators(limit: int) -> list[dict]:
    """Run SoundCloud phase. Returns list of candidate rows (not yet deduped).

    Note: SoundCloud doesn't expose per-playlist follower counts via its public
    API. We use likes_count + reposts_count as a reach proxy — playlists that
    other users engage with.
    """
    print(f"  Phase 2: SoundCloud playlist search ({len(GENRE_KEYWORDS)} keywords)")
    all_playlists: dict[str, dict] = {}

    for i, keyword in enumerate(GENRE_KEYWORDS):
        print(f"    [{i+1:>2}/{len(GENRE_KEYWORDS)}] q={keyword!r:<22}", end="  ", flush=True)
        hits = search_soundcloud_playlists(keyword, limit=50)
        added = 0
        for p in hits:
            pid = str(p.get("id") or "")
            if not pid or pid in all_playlists:
                continue
            user = p.get("user") or {}
            followers = int(p.get("likes_count") or 0) + int(p.get("reposts_count") or 0)
            if followers < SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS:
                continue
            matched = match_genres(p.get("title", "") or "", p.get("description", "") or "")
            if keyword not in matched:
                matched.append(keyword)
            all_playlists[pid] = {
                "id": pid,
                "name": p.get("title", ""),
                "description": p.get("description", "") or "",
                "followers": followers,
                "owner_id": str(user.get("id") or ""),
                "owner_name": user.get("username") or user.get("full_name") or "",
                "owner_permalink_url": user.get("permalink_url", ""),
                "owner_followers": int(user.get("followers_count") or 0),
                "matched_genres": matched,
                "url": p.get("permalink_url", ""),
            }
            added += 1
        print(f"+{added} new playlists")

    print(f"  Playlists qualifying: {len(all_playlists)}")

    owners = aggregate_playlists_by_owner(list(all_playlists.values()))
    print(f"  Unique owners before filter: {len(owners)}")

    candidates: list[dict] = []
    for owner in owners.values():
        if owner["playlist_total_followers"] < SOUNDCLOUD_MIN_OWNER_TOTAL:
            continue
        candidates.append(build_candidate_row(owner, platform="soundcloud"))

    candidates.sort(key=lambda c: -c["playlist_total_followers"])
    candidates = candidates[:limit]
    print(f"  SoundCloud candidates kept: {len(candidates)}")
    return candidates


# ---------------------------------------------------------------------------
# Data I/O + dedup + main
# ---------------------------------------------------------------------------

import argparse
import shutil
from datetime import datetime


def _load_contacts() -> list[dict]:
    with open(ENRICHED_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_contacts(contacts: list[dict]) -> None:
    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def _backup_contacts() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "scene_intelligence" / "backups" / f"contacts_{stamp}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENRICHED_FILE, dest)
    return dest


def _build_existing_keys(contacts: list[dict]) -> dict:
    return {
        "names":               {dedup_key(c.get("name", "")) for c in contacts if c.get("name")},
        "spotify_ids":         {c["spotify_id"] for c in contacts if c.get("spotify_id")},
        "soundcloud_user_ids": {str(c["soundcloud_user_id"]) for c in contacts if c.get("soundcloud_user_id")},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spotify",    action="store_true", help="Run Spotify phase only")
    parser.add_argument("--soundcloud", action="store_true", help="Run SoundCloud phase only")
    parser.add_argument("--dry-run",    action="store_true", help="Preview, do not save")
    parser.add_argument("--limit", type=int, default=100, help="Max candidates per platform")
    args = parser.parse_args()

    both = not args.spotify and not args.soundcloud

    contacts = _load_contacts()
    existing = _build_existing_keys(contacts)
    print(f"Loaded {len(contacts)} existing contacts.\n")

    all_candidates: list[dict] = []
    if args.spotify or both:
        all_candidates.extend(discover_spotify_curators(args.limit))
        print()
    if args.soundcloud or both:
        all_candidates.extend(discover_soundcloud_curators(args.limit))
        print()

    fresh = filter_existing(all_candidates, existing)
    dropped = len(all_candidates) - len(fresh)
    print(f"Candidates: {len(all_candidates)} total, {dropped} already known, {len(fresh)} new.\n")

    if args.dry_run:
        print("DRY RUN -- top 20 fresh candidates:")
        for c in fresh[:20]:
            print(f"  [{c['sub_type']:<10}] {c['name'][:30]:<30} {c['playlist_count']:>2} pl  "
                  f"{c['playlist_total_followers']:>7} reach  "
                  f"top: {c['top_playlist_name'][:35]}")
        return 0

    if fresh:
        backup = _backup_contacts()
        print(f"Backup: {backup}")
        contacts.extend(fresh)
        _save_contacts(contacts)
        print(f"Added {len(fresh)} curators. Total contacts: {len(contacts)}.")
    else:
        print("No new curators to add.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
