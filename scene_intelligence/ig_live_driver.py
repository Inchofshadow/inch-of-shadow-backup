"""
scene_intelligence/ig_live_driver.py
--------------------------------------
RequestsBrowserDriver — live BrowserDriver implementation for ig_engagement.py.

Uses Instagram's internal JSON API with session cookies stored in .env.
No browser required. Plugs directly into the existing BrowserDriver interface
so the full ig_engagement.py engine runs unmodified.

Setup (one-time):
    1. Log in to Instagram in Chrome.
    2. Run:  python3 scene_intelligence/ig_live_driver.py --extract-cookies
       (opens the Chrome tab you have open, pulls sessionid + csrftoken, writes to .env)
    3. Add IG_USER_ID to .env (your own Instagram numeric user ID).
       Find it by running: python3 scene_intelligence/ig_live_driver.py --whoami

Usage in ig_engagement.py (automatic — build_driver() imports this):
    python3 scene_intelligence/ig_engagement.py --live

Rate limits (conservative):
    - web_profile_info: ~40/hr before soft block — used once per profile check
    - friendships/create: follows, 25/day safe ceiling (set in config)
    - friendships/destroy: unfollows, 25/day safe ceiling
    - likes/{id}: 60-80/hr safe — used sparingly (like-before-follow)

Circuit breakers:
    - HTTP 400 + feedback_required → Action Blocked (same as UI block)
    - HTTP 429 → rate limited
    - HTTP 401 → session expired → hard stop
    - Response body matching ig_engagement_config.CIRCUIT_BREAKER_SIGNALS
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import random
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv, set_key

# Resolve paths
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
SI_DIR = BASE_DIR / "scene_intelligence"

# Instagram API constants
IG_APP_ID = "936619743392459"
IG_API_BASE = "https://www.instagram.com/api/v1"
IG_WEB = "https://www.instagram.com"

# Headers that mimic a real browser session
_BASE_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "X-IG-App-ID": IG_APP_ID,
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Origin": "https://www.instagram.com",
}


# ---------------------------------------------------------------------------
# Import engine types (safe — only needed at runtime with installed package)
# ---------------------------------------------------------------------------

def _import_engine():
    try:
        from scene_intelligence.ig_engagement import (  # type: ignore
            BrowserDriver,
            PostMetadata,
            CircuitBreakerTripped,
        )
        return BrowserDriver, PostMetadata, CircuitBreakerTripped
    except ImportError:
        try:
            sys.path.insert(0, str(BASE_DIR))
            from scene_intelligence.ig_engagement import (
                BrowserDriver,
                PostMetadata,
                CircuitBreakerTripped,
            )
            return BrowserDriver, PostMetadata, CircuitBreakerTripped
        except ImportError as e:
            raise ImportError(f"Cannot import ig_engagement: {e}") from e


# ---------------------------------------------------------------------------
# RequestsBrowserDriver
# ---------------------------------------------------------------------------

class RequestsBrowserDriver:
    """
    Live BrowserDriver that talks to Instagram's internal JSON API.

    Implements every method the ig_engagement.py engine calls.
    Requires IG_SESSION_ID, IG_CSRF_TOKEN, and IG_USER_ID in .env.
    """

    LIVE = True

    def __init__(self, session_id: str, csrf_token: str, own_user_id: str):
        self._sid = session_id
        self._csrf = csrf_token
        self._own_id = own_user_id

        self._session = requests.Session()
        self._session.headers.update({**_BASE_HEADERS, "X-CSRFToken": csrf_token})
        self._session.cookies.set("sessionid", session_id, domain=".instagram.com")
        self._session.cookies.set("csrftoken", csrf_token, domain=".instagram.com")
        self._session.cookies.set("ds_user_id", own_user_id, domain=".instagram.com")

        # Per-profile state (reset on each navigate_to_profile call)
        self._current_handle: Optional[str] = None
        self._current_user_id: Optional[str] = None
        self._profile_cache: dict = {}

        # Track last response for circuit breaker inspection
        self._last_response: Optional[requests.Response] = None

        # Import circuit breaker config lazily
        self._cb_signals: list[str] = []
        try:
            from scene_intelligence import ig_engagement_config as cfg  # type: ignore
            self._cb_signals = list(getattr(cfg, "CIRCUIT_BREAKER_SIGNALS", []))
        except ImportError:
            pass

    # ------------------------------------------------------------------
    # BrowserDriver interface
    # ------------------------------------------------------------------

    def navigate_to_profile(self, handle: str) -> None:
        """Set the current handle. API calls happen in get_profile_state()."""
        self._current_handle = handle.lower().strip().strip("/")
        self._current_user_id = None
        self._profile_cache = {}

    def scroll(self, duration_seconds: float) -> None:
        """API has no scroll — just sleep to preserve human-like timing."""
        time.sleep(max(0.5, duration_seconds))

    def get_profile_state(self) -> dict:
        """
        Fetch profile info for the current handle.

        Returns:
            {
                is_private: bool,
                not_found: bool,
                is_following: bool,
                recent_posts: [PostMetadata, ...]
            }
        """
        _, PostMetadata, CircuitBreakerTripped = _import_engine()
        empty = {"is_private": False, "not_found": False, "is_following": False, "recent_posts": []}

        if not self._current_handle:
            return empty

        r = self._get(
            f"{IG_API_BASE}/users/web_profile_info/",
            params={"username": self._current_handle},
            referer=f"{IG_WEB}/{self._current_handle}/",
        )
        if r is None:
            return empty

        if r.status_code == 404:
            return {**empty, "not_found": True}

        if r.status_code != 200:
            return empty

        try:
            data = r.json()
        except ValueError:
            return empty

        user = data.get("data", {}).get("user")
        if not user:
            return {**empty, "not_found": True}

        uid = str(user.get("id", ""))
        self._current_user_id = uid
        self._profile_cache = user

        is_private = bool(user.get("is_private"))
        friendship = user.get("friendship_status") or {}
        is_following = bool(friendship.get("following"))
        # Best-effort reciprocity from web_profile_info. Not always populated
        # here, so the unfollow guard uses the authoritative follows_back()
        # (friendships/show) instead -- this is only surfaced for visibility.
        followed_by = bool(friendship.get("followed_by"))

        recent_posts: list = []
        if not is_private:
            # First: extract posts from the web_profile_info response itself.
            # This works for all public accounts regardless of follow status.
            recent_posts = self._extract_posts_from_profile(user, PostMetadata, count=5)

            # Fallback: feed/user endpoint (works when already following)
            if not recent_posts and uid:
                recent_posts = self._fetch_recent_posts(uid, PostMetadata, count=5)

        # Extract live follower metrics from the API response.
        # These are used by _execute_follow to write real counts into the tracker
        # instead of the zero-filled placeholders from the static target list.
        follower_count = int(
            (user.get("edge_followed_by") or {}).get("count") or
            user.get("follower_count") or 0
        )
        following_count = int(
            (user.get("edge_follow") or {}).get("count") or
            user.get("following_count") or 0
        )
        post_count = int(
            (user.get("edge_owner_to_timeline_media") or {}).get("count") or
            user.get("media_count") or 0
        )
        bio = str(user.get("biography") or "").strip()
        is_verified = bool(user.get("is_verified"))

        return {
            "is_private": is_private,
            "is_verified": is_verified,
            "not_found": False,
            "is_following": is_following,
            "followed_by": followed_by,
            "recent_posts": recent_posts,
            # Live profile metrics — populated by RequestsBrowserDriver only
            "follower_count": follower_count,
            "following_count": following_count,
            "post_count": post_count,
            "bio": bio,
        }

    def like_post(self, post_id: str) -> bool:
        """Like a post by its numeric media ID.

        The likes endpoint requires media_id in the POST body — without it
        Instagram accepts the request silently but does not register the like.
        post_id may arrive as 'media_id' or 'media_id_owner_id'; we use only
        the numeric media_id part for both the URL and the body.

        Returns True if Instagram confirmed the like (status=ok), False otherwise.
        The caller must only log/count a like when this returns True.
        """
        if not post_id or "stub" in post_id:
            return False

        # Strip owner_id suffix if present (e.g. "3882278118812500655_14576029052")
        media_id = post_id.split("_")[0]

        # Small pre-like pause — natural behaviour
        time.sleep(random.uniform(1.5, 3.5))

        # Web session uses /web/likes/{media_id}/like/ — not the mobile /api/v1/likes/ path.
        # media_id MUST be included in the POST body; without it Instagram accepts
        # the request silently (200 OK) but does not register the like.
        r = self._post(
            f"{IG_WEB}/web/likes/{media_id}/like/",
            data={"media_id": media_id},
            referer=f"{IG_WEB}/p/{media_id}/",
        )
        if r is None:
            return False
        self._check_response_for_circuit_breaker(r)
        try:
            return r.status_code == 200 and r.json().get("status") == "ok"
        except (ValueError, AttributeError):
            return r.status_code == 200

    @staticmethod
    def _friendship_confirmed(r, *, want_following: bool) -> bool:
        """True only when IG's response confirms the follow/unfollow took.

        friendships/create and friendships/destroy both answer with
        {"status": "ok", "friendship_status": {...}}. Requires status ok, then
        checks friendship_status when present: for a follow, `following` (or
        `outgoing_request` — private account, request sent) must be true; for
        an unfollow, `following` must be false. A missing friendship_status
        with status ok still counts (mirrors like_post's lenient parse).
        Audit P1-5 (findings 4/5): the caller must only record the action in
        tracker/queue/log when this is True.
        """
        if r is None or r.status_code != 200:
            return False
        try:
            data = r.json()
        except (ValueError, AttributeError):
            return r.status_code == 200
        if data.get("status") != "ok":
            return False
        fs = data.get("friendship_status")
        if not isinstance(fs, dict):
            return True
        if want_following:
            return bool(fs.get("following") or fs.get("outgoing_request"))
        return not fs.get("following")

    def follow_current_profile(self) -> bool:
        """Follow the current profile via friendships/create.

        Returns True only when Instagram confirmed the follow.
        """
        uid = self._resolve_user_id()
        if not uid:
            return False

        time.sleep(random.uniform(1.5, 3.0))

        r = self._post(
            f"{IG_API_BASE}/friendships/create/{uid}/",
            referer=f"{IG_WEB}/{self._current_handle}/",
        )
        if r is not None:
            self._check_response_for_circuit_breaker(r)
        return self._friendship_confirmed(r, want_following=True)

    def follows_back(self) -> bool | None:
        """Authoritative reciprocity check via friendships/show.

        True if the current profile follows @inch_of_shadow back, False if not,
        None if undeterminable (caller then proceeds with the planned decision).
        Uses the same endpoint as ig_followback_checker -- the reliable signal,
        unlike DOM 'Follows you' badge scraping which IG keeps breaking.
        """
        uid = self._resolve_user_id()
        if not uid:
            return None
        r = self._get(
            f"{IG_API_BASE}/friendships/show/{uid}/",
            referer=f"{IG_WEB}/{self._current_handle}/",
        )
        if r is None or r.status_code != 200:
            return None
        try:
            data = r.json()
        except ValueError:
            return None
        if "followed_by" not in data:
            return None
        return bool(data.get("followed_by"))

    def unfollow_current_profile(self) -> bool:
        """Unfollow the current profile via friendships/destroy.

        Returns True only when Instagram confirmed the unfollow.
        """
        uid = self._resolve_user_id()
        if not uid:
            return False

        time.sleep(random.uniform(2.0, 4.0))

        r = self._post(
            f"{IG_API_BASE}/friendships/destroy/{uid}/",
            referer=f"{IG_WEB}/{self._current_handle}/",
        )
        if r is not None:
            self._check_response_for_circuit_breaker(r)
        return self._friendship_confirmed(r, want_following=False)

    def check_for_circuit_breaker(self) -> None:
        """
        Check the last API response for circuit breaker signals.
        Also checks for session expiry (HTTP 401).
        Raises CircuitBreakerTripped if a stop signal is found.
        """
        _, _, CircuitBreakerTripped = _import_engine()

        if self._last_response is None:
            return

        r = self._last_response

        # Session expired
        if r.status_code == 401:
            raise CircuitBreakerTripped("Session expired — re-extract cookies")

        # Hard rate limit / challenge
        if r.status_code == 429:
            raise CircuitBreakerTripped("Try Again Later")

        # Try to match response body against known signals
        try:
            body = r.text.lower()
        except Exception:
            return

        for signal in self._cb_signals:
            if signal.lower() in body:
                raise CircuitBreakerTripped(signal)

    def close(self) -> None:
        """Clean up the requests session."""
        try:
            self._session.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_user_id(self) -> Optional[str]:
        """Return cached user ID, or fetch it if not yet known."""
        if self._current_user_id:
            return self._current_user_id
        if not self._current_handle:
            return None
        # Trigger profile fetch to populate user ID
        self.get_profile_state()
        return self._current_user_id

    def _extract_posts_from_profile(self, user: dict, PostMetadata, count: int = 3) -> list:
        """
        Extract recent posts from the web_profile_info user dict.
        The response includes edge_owner_to_timeline_media.edges which works
        for all public accounts regardless of follow status — no extra API call.
        """
        edges = (
            user.get("edge_owner_to_timeline_media") or {}
        ).get("edges", [])

        out = []
        for edge in edges[:count]:
            node = edge.get("node", {})
            post_id = str(node.get("id", ""))
            if not post_id:
                continue
            caption_edges = (node.get("edge_media_to_caption") or {}).get("edges", [])
            caption_text = ""
            if caption_edges:
                caption_text = caption_edges[0].get("node", {}).get("text", "") or ""
            out.append(PostMetadata(
                post_id=post_id,
                is_sponsored=bool(node.get("is_ad") or node.get("is_paid_partnership")),
                caption=str(caption_text),
                already_liked=bool(node.get("viewer_has_liked")),
                likes=int((node.get("edge_media_preview_like") or {}).get("count", 0)),
                posted_at=str(node.get("taken_at_timestamp", "")),
            ))
        return out

    def _fetch_recent_posts(self, user_id: str, PostMetadata, count: int = 3) -> list:
        """Fetch the N most recent posts for a user and return PostMetadata list."""
        r = self._get(
            f"{IG_API_BASE}/feed/user/{user_id}/",
            params={"count": count},
            referer=f"{IG_WEB}/",
        )
        if r is None or r.status_code != 200:
            return []
        try:
            items = r.json().get("items", [])
        except ValueError:
            return []

        out = []
        for item in items[:count]:
            post_id = str(item.get("id", ""))
            if not post_id:
                continue
            caption_obj = item.get("caption") or {}
            caption_text = caption_obj.get("text", "") if isinstance(caption_obj, dict) else ""
            out.append(PostMetadata(
                post_id=post_id,
                is_sponsored=bool(item.get("is_ad") or item.get("is_paid_partnership")),
                caption=str(caption_text or ""),
                already_liked=bool(item.get("has_liked")),
                likes=int(item.get("like_count", 0)),
                posted_at=str(item.get("taken_at", "")),
            ))
        return out

    def _get(
        self,
        url: str,
        params: dict | None = None,
        referer: str = IG_WEB,
    ) -> Optional[requests.Response]:
        """GET with error handling. Returns None on network error."""
        try:
            r = self._session.get(
                url,
                params=params,
                headers={"Referer": referer},
                timeout=20,
            )
            self._last_response = r
            return r
        except requests.RequestException as exc:
            print(f"  [DRIVER] GET {url} failed: {exc}")
            return None

    def _post(
        self,
        url: str,
        data: dict | None = None,
        referer: str = IG_WEB,
    ) -> Optional[requests.Response]:
        """POST with error handling. Returns None on network error."""
        try:
            r = self._session.post(
                url,
                data=data or {},
                headers={
                    "Referer": referer,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=20,
            )
            self._last_response = r
            return r
        except requests.RequestException as exc:
            print(f"  [DRIVER] POST {url} failed: {exc}")
            return None

    def _check_response_for_circuit_breaker(self, r: requests.Response) -> None:
        """Inspect a specific response for circuit breaker signals."""
        _, _, CircuitBreakerTripped = _import_engine()

        if r.status_code == 401:
            raise CircuitBreakerTripped("Session expired — re-extract cookies")
        if r.status_code == 429:
            raise CircuitBreakerTripped("Try Again Later")

        # feedback_required = Action Blocked
        try:
            body = r.json()
            msg = str(body.get("message", "")).lower()
            if "feedback_required" in msg or "challenge_required" in msg:
                raise CircuitBreakerTripped("Action Blocked")
            spam = str(body.get("spam", "")).lower()
            if spam == "true":
                raise CircuitBreakerTripped("We've limited some features")
        except (ValueError, AttributeError):
            pass


# ---------------------------------------------------------------------------
# Factory — called by ig_engagement.py's build_driver()
# ---------------------------------------------------------------------------

# The only account this driver is ever allowed to act as. 4 of 5 Chrome
# profiles on this Mac start with "Amir" and cookies have been extracted
# from the wrong one before (2026-06-10 incident).
EXPECTED_IG_USERNAME = "inch_of_shadow"


def build_live_driver() -> RequestsBrowserDriver:
    """
    Read credentials from .env and return a configured RequestsBrowserDriver.

    Raises SystemExit with a helpful message if any required var is missing,
    or if the session does not verifiably belong to EXPECTED_IG_USERNAME
    (2026-07-05, audit P1-6: identity is verified BEFORE any action fires;
    an unverifiable identity fails closed).
    """
    load_dotenv(ENV_FILE)

    session_id = os.getenv("IG_SESSION_ID", "").strip()
    csrf_token = os.getenv("IG_CSRF_TOKEN", "").strip()
    own_user_id = os.getenv("IG_USER_ID", "").strip()

    missing = []
    if not session_id:
        missing.append("IG_SESSION_ID")
    if not csrf_token:
        missing.append("IG_CSRF_TOKEN")
    if not own_user_id:
        missing.append("IG_USER_ID")

    if missing:
        raise SystemExit(
            f"\n[LIVE DRIVER] Missing .env variables: {', '.join(missing)}\n\n"
            f"Run this to extract cookies from your open Chrome tab:\n"
            f"  python3 scene_intelligence/ig_live_driver.py --extract-cookies\n\n"
            f"Then add IG_USER_ID manually (your Instagram numeric user ID):\n"
            f"  python3 scene_intelligence/ig_live_driver.py --whoami\n"
        )

    print(f"[LIVE DRIVER] Loaded credentials from .env (user_id={own_user_id})")

    # Identity gate: whose session is this actually?
    me = verify_session(session_id, csrf_token)
    username = str(me.get("username") or "").strip().lower()
    pk = str(me.get("pk") or "").strip()

    if username != EXPECTED_IG_USERNAME:
        shown = f"@{username}" if username else "an UNVERIFIABLE account"
        raise SystemExit(
            f"\n[LIVE DRIVER] IDENTITY CHECK FAILED — session belongs to {shown}, "
            f"not @{EXPECTED_IG_USERNAME}.\n"
            f"The cookies in .env were extracted from the wrong Chrome profile "
            f"(only the profile named 'Inch of Shadow' is correct - shown as "
            f"'Amir (Inch of Shadow)' in the macOS picker).\n"
            f"Re-extract from the right profile before any live run. "
            f"No action was taken."
        )
    if pk and pk != own_user_id:
        raise SystemExit(
            f"\n[LIVE DRIVER] IDENTITY CHECK FAILED — session pk={pk} does not "
            f"match IG_USER_ID={own_user_id} in .env. Fix .env before any live "
            f"run. No action was taken."
        )
    if not pk:
        print("[LIVE DRIVER] WARNING: username verified but pk unavailable "
              "from endpoints; proceeding on username match.")
    print(f"[LIVE DRIVER] Session identity verified: @{username}"
          + (f" (pk={pk})" if pk else ""))

    return RequestsBrowserDriver(
        session_id=session_id,
        csrf_token=csrf_token,
        own_user_id=own_user_id,
    )


# ---------------------------------------------------------------------------
# Cookie extraction helpers (one-time setup)
# ---------------------------------------------------------------------------

def extract_cookies_from_chrome() -> dict:
    """
    Extract IG session cookies from the current Chrome tab via JavaScript.
    Requires the Claude-in-Chrome MCP to be active and an instagram.com tab open.

    This is a helper for initial .env setup — not used in normal operation.
    Returns {'sessionid': ..., 'csrftoken': ...} or raises on failure.
    """
    # This function is invoked by the --extract-cookies CLI flag.
    # It cannot run standalone; it requires the Chrome MCP context.
    # Actual extraction is performed by the Cowork session, not this script.
    raise NotImplementedError(
        "Cookie extraction requires the Claude-in-Chrome MCP context.\n"
        "Ask Claude (Cowork) to run --extract-cookies for you."
    )


def verify_session(session_id: str, csrf_token: str) -> dict:
    """
    Test that the provided cookies are valid.
    Tries multiple endpoints in order — some require extra cookies that
    may not be present, so we fall back gracefully.
    Returns a user dict with at least 'username' and 'pk' on success.
    Raises SystemExit on auth failure.
    """
    session = requests.Session()
    session.headers.update({**_BASE_HEADERS, "X-CSRFToken": csrf_token})
    session.cookies.set("sessionid", session_id, domain=".instagram.com")
    session.cookies.set("csrftoken", csrf_token, domain=".instagram.com")

    # --- Attempt 1: web_profile_info for a known public account -----------
    # Lightweight, works with just sessionid + csrftoken.
    # If the session is valid, it returns 200. If expired, returns 401.
    probe_handle = "instagram"  # always exists, always public
    r1 = session.get(
        f"{IG_API_BASE}/users/web_profile_info/",
        params={"username": probe_handle},
        headers={"Referer": f"{IG_WEB}/{probe_handle}/"},
        timeout=15,
    )
    if r1.status_code == 401:
        raise SystemExit("Session invalid or expired. Re-extract cookies.")
    if r1.status_code == 429:
        raise SystemExit("Rate limited. Wait a few minutes and try again.")

    # --- Attempt 2: account_security_info (returns own user info) ---------
    r2 = session.get(
        f"{IG_API_BASE}/accounts/current_user/",
        params={"edit": "true"},
        headers={"Referer": f"{IG_WEB}/accounts/edit/"},
        timeout=15,
    )
    if r2.status_code == 200:
        try:
            data = r2.json()
            user = data.get("user", {})
            if user.get("username"):
                return user
        except ValueError:
            pass

    # --- Attempt 3: parse username from /accounts/edit/ HTML --------------
    r3 = session.get(
        f"{IG_WEB}/accounts/edit/",
        headers={
            "Referer": IG_WEB,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        timeout=15,
    )
    if r3.status_code == 200:
        # Instagram embeds username in the HTML as "username":"..."
        m = re.search(r'"username"\s*:\s*"([^"]+)"', r3.text)
        pk_m = re.search(r'"pk"\s*:\s*"?(\d+)"?', r3.text)
        if m:
            return {"username": m.group(1), "pk": pk_m.group(1) if pk_m else ""}

    # --- Attempt 4: check if probe returned 200 but we couldn't get user --
    if r1.status_code == 200:
        # Session is valid but we can't extract username from these endpoints.
        # Return a minimal dict — _cmd_whoami will handle missing username.
        return {"username": "", "pk": ""}

    raise SystemExit(
        f"Could not verify session (status codes: probe={r1.status_code}, "
        f"edit={r2.status_code}). Try re-extracting cookies."
    )


# ---------------------------------------------------------------------------
# CLI — setup utilities
# ---------------------------------------------------------------------------

def _cmd_whoami():
    """Print the current user ID and username (to add IG_USER_ID to .env)."""
    load_dotenv(ENV_FILE)
    session_id = os.getenv("IG_SESSION_ID", "").strip()
    csrf_token = os.getenv("IG_CSRF_TOKEN", "").strip()

    if not session_id or not csrf_token:
        print("ERROR: IG_SESSION_ID and IG_CSRF_TOKEN must be set in .env first.")
        print("Run --extract-cookies first (requires Chrome MCP).")
        sys.exit(1)

    user = verify_session(session_id, csrf_token)
    uid = str(user.get("pk") or user.get("id", "")).strip()
    username = user.get("username", "").strip()

    if username:
        print(f"\nLogged in as: @{username} (id={uid or 'unknown'})")
    else:
        print("\nSession is valid but username could not be extracted automatically.")
        print("Find your numeric user ID in the Application tab:")
        print("  DevTools -> Application -> Cookies -> instagram.com -> ds_user_id")
        uid = input("Paste your ds_user_id here: ").strip()

    if uid:
        set_key(str(ENV_FILE), "IG_USER_ID", str(uid))
        print(f"\nDone — IG_USER_ID={uid} written to .env automatically.")
    else:
        print("\nWARNING: Could not determine user ID. Set IG_USER_ID manually in .env.")


def _cmd_test_driver():
    """Dry-run: load driver, fetch own profile, print result."""
    driver = build_live_driver()
    print("\n[TEST] Verifying session...")
    load_dotenv(ENV_FILE)
    sid = os.getenv("IG_SESSION_ID", "")
    csrf = os.getenv("IG_CSRF_TOKEN", "")
    user = verify_session(sid, csrf)
    print(f"  Logged in as: @{user.get('username')} (id={user.get('pk')})")
    driver.close()
    print("[TEST] Driver OK.")


def _cmd_extract_cookies_instructions():
    """Print instructions for extracting cookies via Chrome DevTools."""
    print("""
Cookie Extraction (one-time setup)
===================================
Option A — via Chrome DevTools (manual):
  1. Open instagram.com and make sure you are logged in.
  2. Open DevTools → Application → Cookies → instagram.com
  3. Copy the value of 'sessionid' and 'csrftoken'.
  4. Add to your .env file:
       IG_SESSION_ID=<sessionid value>
       IG_CSRF_TOKEN=<csrftoken value>
  5. Run:  python3 scene_intelligence/ig_live_driver.py --whoami
     (This verifies the session and writes IG_USER_ID to .env automatically.)

Option B — via Chrome Console (faster):
  1. Open instagram.com, logged in.
  2. Open DevTools → Console.
  3. Paste:
       console.log('SID:', document.cookie.match(/sessionid=([^;]+)/)?.[1]);
       console.log('CSRF:', document.cookie.match(/csrftoken=([^;]+)/)?.[1]);
  4. Copy the values and add to .env as above.
  5. Run --whoami to verify and auto-write IG_USER_ID.
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ig_live_driver setup utilities")
    parser.add_argument("--whoami", action="store_true",
                        help="Verify session and print/save IG_USER_ID")
    parser.add_argument("--test", action="store_true",
                        help="Test driver configuration end-to-end")
    parser.add_argument("--extract-cookies", action="store_true",
                        help="Print instructions for extracting Instagram cookies")
    args = parser.parse_args()

    if args.whoami:
        _cmd_whoami()
    elif args.test:
        _cmd_test_driver()
    elif args.extract_cookies:
        _cmd_extract_cookies_instructions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
