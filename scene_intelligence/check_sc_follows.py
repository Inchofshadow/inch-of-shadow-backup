#!/usr/bin/env python3
"""
check_sc_follows.py
-------------------
Fetches the full list of accounts Inch of Shadow follows on SoundCloud
via the OAuth API, then cross-references with enriched_contacts.json.

Reports:
  A) Accounts you follow that have NO match in SI at all
  B) Accounts you follow that ARE in SI but missing SC data
  C) SC follow tracker entries that are no longer in your following list
     (follow-backs who unfollowed, or manual cleans)

Usage:
    python scene_intelligence/check_sc_follows.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
BASE = Path(__file__).parent.parent
load_dotenv(BASE / ".env")

TOKEN_FILE = BASE / ".sc_user_token.json"
CONTACTS_FILE = BASE / "scene_intelligence" / "enriched_contacts.json"
TRACKER_FILE = BASE / "scene_intelligence" / "sc_follow_tracker.json"

SC_API = "https://api.soundcloud.com"
SC_API_V2 = "https://api-v2.soundcloud.com"

# ---------------------------------------------------------------------------


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        sys.exit(f"[ERROR] Token file not found: {TOKEN_FILE}")
    return json.loads(TOKEN_FILE.read_text())


def get_access_token(token_data: dict) -> str:
    return token_data.get("access_token", "")


def fetch_my_followings(access_token: str) -> list[dict]:
    """Fetch all accounts this user follows, paginating automatically."""
    followings = []
    url = f"{SC_API}/me/followings"
    headers = {"Authorization": f"OAuth {access_token}", "Accept": "application/json"}
    params = {"limit": 200}
    page = 0

    while url:
        page += 1
        print(f"  Fetching page {page}...", end=" ", flush=True)
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 401:
            sys.exit(f"\n[ERROR] 401 Unauthorized — OAuth token may be expired. Re-auth via sc_auth_callback.py\nResponse: {resp.text[:300]}")
        if resp.status_code != 200:
            sys.exit(f"\n[ERROR] API returned {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        # API v1 returns a list directly or a dict with 'collection'
        if isinstance(data, list):
            batch = data
            url = None
        elif isinstance(data, dict):
            batch = data.get("collection", [])
            next_href = data.get("next_href")
            url = next_href if next_href else None
            params = {"limit": 200}
        else:
            break

        print(f"{len(batch)} accounts")
        followings.extend(batch)

        if not batch or url is None:
            break
        time.sleep(1)

    return followings


def build_si_lookup(contacts: list[dict]) -> dict:
    """Build lookup dicts from SI contacts."""
    by_sc_id: dict[str, dict] = {}
    by_sc_slug: dict[str, dict] = {}
    by_name: dict[str, dict] = {}

    for c in contacts:
        # SC-06 (2026-09-01): the real SI field is soundcloud_user_id —
        # "soundcloud_id" exists on 0 of 1,206 contacts, so ID matching
        # never fired and everything fell through to slug/name.
        sc_id = str(c.get("soundcloud_user_id", "") or c.get("soundcloud_id", "")).strip()
        sc_url = c.get("soundcloud_url", "").strip().lower()
        name = c.get("name", "").strip().lower()

        if sc_id and sc_id != "0":
            by_sc_id[sc_id] = c
        if sc_url:
            slug = sc_url.rstrip("/").split("/")[-1].lower()
            by_sc_slug[slug] = c
        if name:
            by_name[name] = c

    return by_sc_id, by_sc_slug, by_name


def has_sc_data(contact: dict) -> bool:
    """Check if a SI contact has meaningful SC data."""
    followers = contact.get("soundcloud_followers", 0) or 0
    sc_url = contact.get("soundcloud_url", "")
    return bool(sc_url) and int(followers) > 0


def main():
    print("=== SC Following Cross-Reference ===\n")

    # Load token
    token_data = load_token()
    access_token = get_access_token(token_data)
    print(f"Token loaded (expires: {token_data.get('expires_at', 'unknown')})\n")

    # Load SI contacts
    contacts = json.loads(CONTACTS_FILE.read_text())
    print(f"SI contacts loaded: {len(contacts)}\n")

    # Load follow tracker
    tracker = json.loads(TRACKER_FILE.read_text()) if TRACKER_FILE.exists() else {}
    follows_list = tracker.get("follows", [])
    if isinstance(follows_list, list):
        tracked_ids = {str(v.get("user_id", "")) for v in follows_list if v.get("user_id")}
    else:
        tracked_ids = {str(v.get("soundcloud_id", "")) for v in follows_list.values() if v.get("soundcloud_id")}

    # Fetch followings
    print("Fetching your SC followings...")
    followings = fetch_my_followings(access_token)
    print(f"\nTotal accounts you follow: {len(followings)}\n")

    # Build SI lookups
    by_sc_id, by_sc_slug, by_name = build_si_lookup(contacts)

    # Cross-reference
    not_in_si: list[dict] = []         # A: no match in SI at all
    in_si_no_data: list[dict] = []     # B: in SI but missing SC data
    matched: list[dict] = []           # found and have data

    following_ids = set()

    for acc in followings:
        sc_id = str(acc.get("id", ""))
        permalink = (acc.get("permalink", "") or "").lower()
        username = (acc.get("username", "") or "").lower()
        followers_count = acc.get("followers_count", 0) or 0
        tracks_count = acc.get("track_count", 0) or 0
        sc_url = f"https://soundcloud.com/{permalink}"

        following_ids.add(sc_id)

        # Try matching to SI
        si_match = (
            by_sc_id.get(sc_id)
            or by_sc_slug.get(permalink)
            or by_name.get(username)
        )

        entry = {
            "sc_id": sc_id,
            "username": acc.get("username", ""),
            "permalink": permalink,
            "url": sc_url,
            "followers": followers_count,
            "tracks": tracks_count,
        }

        if si_match is None:
            not_in_si.append(entry)
        elif not has_sc_data(si_match):
            entry["si_name"] = si_match.get("name", "")
            in_si_no_data.append(entry)
        else:
            entry["si_name"] = si_match.get("name", "")
            matched.append(entry)

    # Sort by followers desc for readability
    not_in_si.sort(key=lambda x: x["followers"], reverse=True)
    in_si_no_data.sort(key=lambda x: x["followers"], reverse=True)

    # Print results
    print("=" * 60)
    print(f"A) FOLLOWING but NOT IN SI ({len(not_in_si)} accounts)")
    print("=" * 60)
    for a in not_in_si:
        print(f"  {a['username']:<35} {a['followers']:>6} followers  {a['tracks']:>3} tracks  {a['url']}")

    print()
    print("=" * 60)
    print(f"B) IN SI but MISSING SC DATA ({len(in_si_no_data)} accounts)")
    print("=" * 60)
    for b in in_si_no_data:
        print(f"  SI: {b['si_name']:<30} SC: {b['username']:<25} {b['followers']:>6} followers  {b['url']}")

    print()
    print("=" * 60)
    print(f"C) MATCHED with SC data ({len(matched)} accounts)")
    print("=" * 60)
    for m in matched:
        print(f"  {m['si_name']:<35} -> {m['username']}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  You follow:              {len(followings)} accounts")
    print(f"  Not in SI at all:        {len(not_in_si)}")
    print(f"  In SI, missing SC data:  {len(in_si_no_data)}")
    print(f"  Matched and have data:   {len(matched)}")

    # C) Tracker entries no longer in the live following list (SC-06: the
    # docstring promised this report since day one; tracked_ids was computed
    # and never used).
    ghosts = []
    if isinstance(follows_list, list):
        ghosts = [f for f in follows_list
                  if str(f.get("user_id", "")) and
                  str(f.get("user_id")) not in following_ids and
                  not f.get("no_longer_following")]
    print()
    print("=" * 60)
    print(f"C) IN TRACKER but NOT FOLLOWING LIVE ({len(ghosts)} entries)")
    print("=" * 60)
    for g in ghosts:
        flag = " [RECIPROCATOR!]" if g.get("followed_back") else ""
        print(f"  {g.get('name',''):<35} id={g.get('user_id')}{flag}")

    # Save JSON output for further processing. SC-06: own file —
    # sc_following_audit.json belongs to sc_weekly_health (two writers with
    # two schemas were silently overwriting each other).
    output = {
        "fetched_at": __import__("datetime").date.today().isoformat(),
        "not_in_si": not_in_si,
        "in_si_no_data": in_si_no_data,
        "tracker_ghosts": [{"name": g.get("name"), "user_id": g.get("user_id"),
                            "followed_back": bool(g.get("followed_back"))}
                           for g in ghosts],
        "matched_count": len(matched),
        "total_following": len(followings),
    }
    out_path = BASE / "scene_intelligence" / "sc_following_crossref.json"
    tmp = str(out_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp, out_path)
    print(f"\nFull results saved to: scene_intelligence/sc_following_crossref.json")


if __name__ == "__main__":
    main()
