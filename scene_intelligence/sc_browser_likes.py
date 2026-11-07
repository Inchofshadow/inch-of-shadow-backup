"""
scene_intelligence/sc_browser_likes.py
----------------------------------------
SoundCloud auth token management and session verification.

SoundCloud blocks all third-party write operations (likes, reposts) via HTTP
requests using DataDome anti-bot protection.  This module handles the token
that is manually copied from Chrome DevTools, verifies it against /me, and
provides stub functions so sc_engagement.py imports don't break.

Likes and reposts are handled by Claude clicking buttons in the user's Chrome
browser via the Claude-in-Chrome extension.  Follows still use the SC OAuth API.

Token setup (one-time):
  1. Open soundcloud.com in Chrome, log in as Inch of Shadow.
  2. Open DevTools (Cmd+Opt+I) → Network tab → filter "api-v2".
  3. Refresh the page, click any api-v2 request, copy the Authorization header
     value (starts with "OAuth ").
  4. Add to .env:
       SC_BROWSER_TOKEN=<paste value here, without the "OAuth " prefix>

Token refresh:
  Repeat the steps above whenever the token expires (SC tokens are long-lived —
  typically weeks to months).  Run --verify to check if the current token works.

Usage:
  python3 scene_intelligence/sc_browser_likes.py --verify
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

BASE_DIR     = Path(__file__).parent.parent
SESSION_FILE = BASE_DIR / ".sc_browser_state.json"   # kept for legacy compat

_SC_V2_BASE  = "https://api-v2.soundcloud.com"
_SC_CLIENT_ID = "yNSW5UvBmb1A5j7qPUtIMuB9Itx3jsOC"  # SC web app client_id

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_REQ_HEADERS = {
    "User-Agent":      _BROWSER_UA,
    "Accept":          "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin":          "https://soundcloud.com",
    "Referer":         "https://soundcloud.com/",
    "Sec-Fetch-Dest":  "empty",
    "Sec-Fetch-Mode":  "cors",
    "Sec-Fetch-Site":  "same-site",
}

# Playwright is not used — stubs below keep sc_engagement.py imports intact
PLAYWRIGHT_AVAILABLE = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(msg, flush=True)

# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------

_req_session:     "_requests.Session | None" = None  # type: ignore[name-defined]
_req_oauth_token: str = ""


def _load_requests_session() -> bool:
    """Load the SC auth token from .env into a requests.Session.

    Priority:
      1. SC_BROWSER_TOKEN in .env  (copied from Chrome DevTools — most reliable)
      2. oauth_token cookie from .sc_browser_state.json

    Returns True if a session with a token was successfully loaded.
    """
    global _req_session, _req_oauth_token

    if not _REQUESTS_AVAILABLE:
        _log("[REQUESTS] 'requests' library not installed.")
        return False

    session = _requests.Session()
    session.headers.update(_REQ_HEADERS)

    oauth_token = ""

    # --- Priority 1: SC_BROWSER_TOKEN from .env ---
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("SC_BROWSER_TOKEN="):
                oauth_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                if oauth_token.lower().startswith("oauth "):
                    oauth_token = oauth_token[6:].strip()
                if oauth_token:
                    _log("[REQUESTS] Using SC_BROWSER_TOKEN from .env.")
                break

    # --- Priority 2: oauth_token cookie from browser state file ---
    if not oauth_token and SESSION_FILE.exists():
        try:
            state = json.loads(SESSION_FILE.read_text())
            for c in state.get("cookies", []):
                name   = c.get("name",   "")
                value  = c.get("value",  "")
                domain = c.get("domain", "").lstrip(".")
                path   = c.get("path",   "/")
                if not name or not value:
                    continue
                session.cookies.set(name, value, domain=domain, path=path)
                if name == "oauth_token" and not oauth_token:
                    oauth_token = value
            if oauth_token:
                _log("[REQUESTS] Using oauth_token from browser session file.")
        except Exception as exc:
            _log(f"[REQUESTS] Failed to read session file: {exc}")

    if not oauth_token:
        _log(
            "[REQUESTS] No auth token found.\n"
            "  Get token from Chrome DevTools → Network → any api-v2 request → Authorization header.\n"
            "  Add to .env:  SC_BROWSER_TOKEN=<token>"
        )
        return False

    session.headers["Authorization"] = f"OAuth {oauth_token}"
    _req_session      = session
    _req_oauth_token  = oauth_token
    _log(f"[REQUESTS] Session ready (token length={len(oauth_token)}).")
    return True


# ---------------------------------------------------------------------------
# Session verification
# ---------------------------------------------------------------------------

def requests_verify_session() -> bool:
    """Verify the auth token works by calling GET /me.

    Returns True if the response is HTTP 200 as Inch Of Shadow.
    """
    global _req_session
    if _req_session is None:
        if not _load_requests_session():
            return False
    try:
        r = _req_session.get(f"{_SC_V2_BASE}/me", timeout=10)
        if r.status_code == 200:
            data = r.json()
            _log(f"[REQUESTS] Verified: '{data.get('username')}' (id={data.get('id')}).")
            return True
        _log(f"[REQUESTS] /me returned HTTP {r.status_code} — token may be expired.")
        if r.status_code == 401:
            _log(
                "  Refresh: Chrome DevTools → Network → any api-v2 request → Authorization header.\n"
                "  Update SC_BROWSER_TOKEN in .env."
            )
        return False
    except Exception as exc:
        _log(f"[REQUESTS] Verify error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Stub functions — kept so sc_engagement.py imports don't break.
# Likes/reposts now happen via Claude clicking in the user's Chrome browser.
# ---------------------------------------------------------------------------

def session_exists() -> bool:
    """Return True if a session file or SC_BROWSER_TOKEN exists."""
    if SESSION_FILE.exists():
        return True
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        return "SC_BROWSER_TOKEN=" in env_file.read_text()
    return False


def ensure_session(verbose: bool = True) -> bool:
    """Check that a valid token exists. (Browser login no longer used.)"""
    return requests_verify_session()


def like_track(url: str, dry_run: bool = False, **kwargs) -> bool:
    """Stub — likes now done via Chrome browser clicks, not this function."""
    _log("[STUB] like_track called — use Chrome MCP browser clicks for likes.")
    return False


def repost_track(url: str, dry_run: bool = False, **kwargs) -> bool:
    """Stub — reposts now done via Chrome browser clicks, not this function."""
    _log("[STUB] repost_track called — use Chrome MCP browser clicks for reposts.")
    return False


def prime_browser_auth(context=None) -> str:
    """Stub — Playwright not used."""
    return ""


def release_shared_eval_page() -> None:
    """Stub — Playwright not used."""


def fast_like(track_id: str) -> bool:
    """Stub — DataDome blocks API likes. Use Chrome browser clicks."""
    return False


def fast_repost(track_id: str) -> bool:
    """Stub — DataDome blocks API reposts. Use Chrome browser clicks."""
    return False


def requests_like(track_id: str, kind: str = "track") -> bool:
    """Stub — DataDome blocks API likes from requests library."""
    _log(f"[REQUESTS] Likes blocked by DataDome. Use Chrome browser for track {track_id}.")
    return False


def requests_repost(track_id: str) -> bool:
    """Stub — DataDome blocks API reposts from requests library."""
    _log(f"[REQUESTS] Reposts blocked by DataDome. Use Chrome browser for track {track_id}.")
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SoundCloud token management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Verify the current SC_BROWSER_TOKEN against the SC API"
    )
    args = parser.parse_args()

    if args.verify:
        ok = requests_verify_session()
        sys.exit(0 if ok else 1)
    else:
        parser.print_help()
