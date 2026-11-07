"""
scene_intelligence/fetch_youtube_subs.py
------------------------------------------
Tool 1 -- Scene Intelligence Engine: YouTube Subscription Fetcher

Replaces manual Google Takeout CSV export. Uses OAuth 2.0 to fetch your
YouTube subscriptions and writes them in the same CSV format that
extract_contacts.py expects.

One-time setup:
  1. Go to Google Cloud Console > APIs & Services > Credentials
  2. Create OAuth 2.0 Client ID (Desktop app)
  3. Download JSON, save as youtube_oauth.json in project root

Usage:
  python3 scene_intelligence/fetch_youtube_subs.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent.parent
OAUTH_FILE  = BASE_DIR / "youtube_oauth.json"
TOKEN_FILE  = BASE_DIR / "youtube_token.json"
OUTPUT_DIR  = BASE_DIR / "data" / "YouTube and YouTube Music" / "subscriptions"
OUTPUT_FILE = OUTPUT_DIR / "subscriptions.csv"

YT_SUBSCRIPTIONS = "https://www.googleapis.com/youtube/v3/subscriptions"

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
TIMEOUT = 10
API_DELAY = 1.0


# ---------------------------------------------------------------------------
# OAuth 2.0
# ---------------------------------------------------------------------------

def _get_credentials() -> Credentials | None:
    """Load saved credentials or run the OAuth flow."""
    creds = None

    # Try loading saved token
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, encoding="utf-8") as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception:
            creds = None

    # If valid, return
    if creds and creds.valid:
        return creds

    # If expired but has refresh token, refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except Exception as exc:
            print(f"  Token refresh failed: {exc}", flush=True)
            creds = None

    # No valid token -- run OAuth flow
    if not OAUTH_FILE.exists():
        print(f"ERROR: {OAUTH_FILE} not found.")
        print("  1. Go to Google Cloud Console > APIs & Services > Credentials")
        print("  2. Create OAuth 2.0 Client ID (Desktop app)")
        print("  3. Download the JSON file")
        print(f"  4. Save it as: {OAUTH_FILE}")
        return None

    print("  Opening browser for YouTube authorization...", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(OAUTH_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    print("  Authorization successful. Token saved.")
    return creds


def _save_token(creds: Credentials) -> None:
    """Save credentials to token file for reuse."""
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)


# ---------------------------------------------------------------------------
# Fetch subscriptions
# ---------------------------------------------------------------------------

def fetch_subscriptions(creds: Credentials) -> list[dict]:
    """Fetch all YouTube subscriptions. Returns list of {id, url, title}."""
    headers = {"Authorization": f"Bearer {creds.token}"}
    subscriptions = []
    page_token = None
    page = 0

    while True:
        page += 1
        params = {
            "part": "snippet",
            "mine": "true",
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            r = requests.get(YT_SUBSCRIPTIONS, params=params,
                             headers=headers, timeout=TIMEOUT)
        except requests.RequestException as exc:
            print(f"  [request error] {exc}", flush=True)
            break

        if r.status_code == 401:
            # Token expired mid-fetch -- try refresh
            from google.auth.transport.requests import Request
            try:
                creds.refresh(Request())
                _save_token(creds)
                headers = {"Authorization": f"Bearer {creds.token}"}
                continue
            except Exception:
                print("  [AUTH ERROR] Token expired and refresh failed.", flush=True)
                break

        if r.status_code != 200:
            print(f"  [HTTP {r.status_code}] {r.text[:200]}", flush=True)
            break

        data = r.json()
        items = data.get("items", [])

        for item in items:
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            channel_id = resource.get("channelId", "")
            title = snippet.get("title", "")

            if channel_id and title:
                subscriptions.append({
                    "id": channel_id,
                    "url": f"http://www.youtube.com/channel/{channel_id}",
                    "title": title,
                })

        print(f"  Page {page}: {len(items)} subscriptions (total: {len(subscriptions)})", flush=True)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        time.sleep(API_DELAY)

    return subscriptions


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def write_csv(subscriptions: list[dict]) -> None:
    """Write subscriptions in Google Takeout CSV format."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Channel Id", "Channel Url", "Channel Title"])
        for sub in sorted(subscriptions, key=lambda s: s["title"].lower()):
            writer.writerow([sub["id"], sub["url"], sub["title"]])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence -- YouTube Subscription Fetcher")
    print("=" * 52)

    # Authenticate
    creds = _get_credentials()
    if not creds:
        sys.exit(1)
    print("  Authenticated with YouTube API")

    # Fetch
    print("  Fetching subscriptions...", flush=True)
    subscriptions = fetch_subscriptions(creds)

    if not subscriptions:
        print("  No subscriptions found.")
        sys.exit(1)

    # Write CSV
    write_csv(subscriptions)

    print()
    print("=" * 52)
    print(f"  Fetched: {len(subscriptions)} subscriptions")
    print(f"  Saved to: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print()
    print("  Next step: python3 scene_intelligence/extract_contacts.py")
    print()


if __name__ == "__main__":
    main()
