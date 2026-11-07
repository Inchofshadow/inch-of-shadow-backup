"""
scene_intelligence/sc_build_browser_session.py
------------------------------------------------
Builds a Playwright browser session from the existing OAuth token
in .sc_user_token.json — no browser login needed.

SoundCloud uses the 'oauth_token' cookie to authenticate the web app.
We inject the same token we already have from the API into Playwright's
session file, so browser automation runs as Inch of Shadow immediately.

Usage:
    python3 scene_intelligence/sc_build_browser_session.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

BASE_DIR      = Path(__file__).parent.parent
TOKEN_FILE    = BASE_DIR / ".sc_user_token.json"
SESSION_FILE  = BASE_DIR / ".sc_browser_state.json"

def build_session() -> bool:
    print("Building browser session from OAuth token...")

    if not TOKEN_FILE.exists():
        print(f"ERROR: {TOKEN_FILE.name} not found. Run sc_auth_callback.py first.")
        return False

    with open(TOKEN_FILE, encoding="utf-8") as f:
        token_data = json.load(f)

    access_token = token_data.get("access_token", "")
    if not access_token:
        print("ERROR: No access_token in token file.")
        return False

    # Check token freshness
    obtained_at = token_data.get("obtained_at", 0)
    expires_in  = token_data.get("expires_in", 3600)
    if obtained_at and time.time() > obtained_at + expires_in - 60:
        print("WARNING: Token may be expired. Run sc_auth_callback.py to refresh it first.")

    # Build Playwright storage state with the oauth_token cookie injected
    # SoundCloud's web app reads this cookie to authenticate all requests
    expiry = int(obtained_at + 60 * 60 * 24 * 365) if obtained_at else int(time.time() + 60 * 60 * 24 * 365)

    storage_state = {
        "cookies": [
            {
                "name":     "oauth_token",
                "value":    access_token,
                "domain":   "soundcloud.com",
                "path":     "/",
                "expires":  expiry,
                "httpOnly": False,
                "secure":   True,
                "sameSite": "None",
            },
        ],
        "origins": [],
    }

    SESSION_FILE.write_text(json.dumps(storage_state, indent=2))
    try:
        os.chmod(SESSION_FILE, 0o600)
    except OSError:
        pass

    print(f"Session saved to: {SESSION_FILE.name}")
    print(f"Token (first 30 chars): {access_token[:30]}...")
    print("\nTest with:")
    print("  python3 scene_intelligence/sc_browser_likes.py --test <track_url>")
    return True


if __name__ == "__main__":
    ok = build_session()
    sys.exit(0 if ok else 1)
