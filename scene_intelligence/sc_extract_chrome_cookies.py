"""
scene_intelligence/sc_extract_chrome_cookies.py
-------------------------------------------------
Extracts SoundCloud cookies from your Inch of Shadow Chrome profile
and saves them as a Playwright browser session (.sc_browser_state.json).

This bypasses the need to log in through an automated browser window,
avoiding SoundCloud's bot detection entirely.

Usage:
    python3 scene_intelligence/sc_extract_chrome_cookies.py

Requirements:
    pip3 install browser-cookie3

What it does:
    1. Reads soundcloud.com cookies from all Chrome profiles
    2. Finds the profile where the SC oauth_token belongs to Inch of Shadow
       by making a quick API call to soundcloud.com/me (no browser needed)
    3. Converts cookies to Playwright's storage state format
    4. Saves to .sc_browser_state.json

After running this, the SC engagement engine will use these cookies
for browser-based likes and reposts.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR     = Path(__file__).parent.parent
SESSION_FILE = BASE_DIR / ".sc_browser_state.json"

CHROME_BASE  = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
TARGET_EMAIL = "inchofshadow@gmail.com"
SC_DOMAIN    = "soundcloud.com"

SC_USER_ID   = "16014870"   # Inch of Shadow SoundCloud user ID
SC_PERMALINK = "inch-of-shadow"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_cookies_from_db(cookies_db: Path) -> list[dict]:
    """Read SoundCloud cookies from a Chrome Cookies SQLite database.

    Chrome locks the database while running, so we copy it first.
    Cookie values may be encrypted — we use browser-cookie3 for decryption.
    """
    cookies = []

    # Copy the database to a temp location (Chrome locks the original)
    tmp = tempfile.mktemp(suffix=".db")
    try:
        shutil.copy2(str(cookies_db), tmp)
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT host_key, name, path, expires_utc, is_secure,
                   is_httponly, samesite, encrypted_value, value
            FROM cookies
            WHERE host_key LIKE '%soundcloud.com%'
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        # Try to decrypt using browser-cookie3
        try:
            import browser_cookie3
            bc_cookies = browser_cookie3.chrome(domain_name=SC_DOMAIN)
            # Build a lookup by name for decrypted values
            decrypted = {c.name: c.value for c in bc_cookies
                         if SC_DOMAIN in c.domain}
        except Exception as exc:
            print(f"  Warning: browser-cookie3 decryption failed: {exc}")
            decrypted = {}

        for (host_key, name, path, expires_utc, is_secure,
             is_httponly, samesite, encrypted_value, raw_value) in rows:

            # Use decrypted value if available, otherwise raw
            value = decrypted.get(name, raw_value or "")
            if not value:
                continue

            # Chrome stores expires as microseconds since Jan 1, 1601.
            # Convert to Unix timestamp (seconds since Jan 1, 1970).
            if expires_utc and expires_utc > 0:
                expires_unix = (expires_utc - 11_644_473_600_000_000) / 1_000_000
            else:
                expires_unix = -1  # session cookie

            samesite_map = {-1: "None", 0: "None", 1: "Lax", 2: "Strict"}
            samesite_str = samesite_map.get(samesite, "None")

            # Keep the leading dot so the cookie covers all subdomains
            # (soundcloud.com AND api-v2.soundcloud.com etc.)
            domain = host_key if host_key else SC_DOMAIN
            if not domain.startswith(".") and "soundcloud.com" in domain:
                domain = "." + domain

            cookies.append({
                "name":     name,
                "value":    value,
                "domain":   domain,
                "path":     path or "/",
                "expires":  expires_unix,
                "httpOnly": bool(is_httponly),
                "secure":   bool(is_secure),
                "sameSite": samesite_str,
            })

    except Exception as exc:
        print(f"  Error reading cookies database: {exc}")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass

    return cookies


def _get_oauth_token_value(cookies: list[dict]) -> str:
    """Extract the oauth_token cookie value from a list of cookies."""
    for c in cookies:
        if c["name"] == "oauth_token":
            return c["value"]
    return ""


def _verify_oauth_token_api(oauth_token: str) -> tuple[bool, str]:
    """Check if this oauth_token belongs to Inch of Shadow via SC API.

    Makes a single GET /me call — no browser needed, not blocked.
    Returns (is_inch_of_shadow, username).
    """
    if not oauth_token or not _REQUESTS_AVAILABLE:
        return False, ""

    try:
        r = _requests.get(
            "https://api-v2.soundcloud.com/me",
            headers={
                "Authorization": f"OAuth {oauth_token}",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            user_id   = str(data.get("id", ""))
            username  = data.get("username", "")
            permalink = data.get("permalink", "")
            print(f"    API says: id={user_id} username='{username}' permalink='{permalink}'")
            is_match = (
                user_id == SC_USER_ID
                or SC_PERMALINK in permalink.lower()
                or "inch" in permalink.lower()
                or "shadow" in permalink.lower()
            )
            return is_match, username
        else:
            print(f"    API returned HTTP {r.status_code}")
    except Exception as exc:
        print(f"    API check error: {exc}")

    return False, ""


def _find_inch_of_shadow_profile() -> Path | None:
    """Fallback: find the Chrome profile associated with inchofshadow@gmail.com."""
    if not CHROME_BASE.exists():
        return None

    local_state_file = CHROME_BASE / "Local State"
    if local_state_file.exists():
        try:
            with open(local_state_file, encoding="utf-8") as f:
                local_state = json.load(f)
            profiles_info = local_state.get("profile", {}).get("info_cache", {})
            for profile_dir, info in profiles_info.items():
                email = info.get("user_name", "").lower()
                name  = info.get("name", "")
                if TARGET_EMAIL.lower() in email or "inch of shadow" in name.lower():
                    profile_path = CHROME_BASE / profile_dir
                    if profile_path.exists():
                        print(f"  Email match: {profile_dir} ({name} / {email})")
                        return profile_path
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  Warning: Could not read Local State: {exc}")

    return None


def extract_and_save() -> bool:
    """Main function: scan all Chrome profiles, find Inch of Shadow SC account, save session."""
    print(f"\nSoundCloud Cookie Extractor — Inch of Shadow")
    print(f"=" * 50)

    if not CHROME_BASE.exists():
        print(f"\nERROR: Chrome not found at {CHROME_BASE}")
        return False

    if not _REQUESTS_AVAILABLE:
        print("ERROR: 'requests' not installed. Run: pip3 install requests --break-system-packages")
        return False

    # Scan all Chrome profiles, collect those with SC cookies
    candidates = []
    for entry in sorted(CHROME_BASE.iterdir()):
        if not (entry.name.startswith("Profile") or entry.name == "Default"):
            continue
        cookies_db = entry / "Cookies"
        if not cookies_db.exists():
            continue
        cookies = _read_cookies_from_db(cookies_db)
        if cookies:
            candidates.append((entry, cookies))
            oauth_val = _get_oauth_token_value(cookies)
            print(f"  {entry.name}: {len(cookies)} SC cookies, oauth_token={'yes' if oauth_val else 'no'}")

    if not candidates:
        print("\nERROR: No Chrome profiles with SoundCloud cookies found.")
        print("Open SoundCloud in your Inch of Shadow Chrome profile and log in first.")
        return False

    # --- Strategy 1: API verification using the oauth_token cookie ---
    print("\nChecking which profile is logged in as Inch of Shadow (via SC API)...")
    correct_cookies = None
    for profile_path, cookies in candidates:
        oauth_val = _get_oauth_token_value(cookies)
        if not oauth_val:
            print(f"  {profile_path.name}: no oauth_token cookie, skipping")
            continue
        print(f"  {profile_path.name}: testing oauth_token...")
        is_match, username = _verify_oauth_token_api(oauth_val)
        if is_match:
            print(f"  MATCH — using {profile_path.name} ('{username}')")
            correct_cookies = cookies
            break
        elif username:
            print(f"  Skip — '{username}' is not Inch of Shadow")
        # If no username returned (e.g., API error), try next profile

    # --- Strategy 2: Email match (profile Preferences identity) ---
    # The old Strategy 2 picked whichever profile had the MOST SoundCloud
    # cookies, with no identity check at all - on a Mac with 5 Chrome
    # profiles that can persist the wrong account's session (the exact
    # 2026-06-10 wrong-profile incident class). Removed 2026-07-05
    # (audit P1-6, finding 13): a session is only saved when its identity
    # was confirmed via the API or the Chrome profile's account email.
    if not correct_cookies:
        print("\nAPI verification inconclusive. Trying Chrome profile email match...")
        profile_path = _find_inch_of_shadow_profile()
        if profile_path:
            cookies_db = profile_path / "Cookies"
            if cookies_db.exists():
                print(f"  Using {profile_path.name} (profile email matches Inch of Shadow)")
                correct_cookies = _read_cookies_from_db(cookies_db)

    if not correct_cookies:
        print("\nABORTED: could not CONFIRM which profile is the Inch of Shadow account.")
        print("No session file was written (an unverified session must never be saved -")
        print("engagement on the wrong account is worse than no engagement).")
        print("Fix: make sure you are logged in to SoundCloud in the 'Inch of Shadow'")
        print("Chrome profile (shown as 'Amir (Inch of Shadow)' in the macOS picker),")
        print("then re-run when the SC API is reachable.")
        return False

    storage_state = {"cookies": correct_cookies, "origins": []}
    SESSION_FILE.write_text(json.dumps(storage_state, indent=2))
    try:
        os.chmod(SESSION_FILE, 0o600)
    except OSError:
        pass

    print(f"\nSession saved: {len(correct_cookies)} cookies -> {SESSION_FILE.name}")
    print("Test with:")
    print('  python3 scene_intelligence/sc_browser_likes.py --test "https://soundcloud.com/discopastors/mix-062-transgression"')
    return True


if __name__ == "__main__":
    ok = extract_and_save()
    sys.exit(0 if ok else 1)
