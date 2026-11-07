"""Third-party Instagram data provider (HikerAPI) -- replaces every direct
Instagram read the toolchain used to make while logged in as Amir.

Why (2026-09-14): four 429s in two weeks (09-02, 09-05, 09-06, 09-14 -- the
last after eight fully quiet days) showed Instagram now fingerprints our
Python client; the flag does not decay. A provider reads public data from its
own accounts and servers, so Amir's account and address never touch
Instagram for reads again. Cost ~$0.0006 per request.

Key: HIKERAPI_KEY in the repo .env (never in chat). All calls are logged on
the daily ledger as kind="provider" (own cap, no IG timing law).
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
BASE_URL = "https://api.hikerapi.com"
TIMEOUT = 30


class ProviderError(RuntimeError):
    """Non-200 from the provider (auth, balance, upstream). Never an IG event."""


def api_key(env_file: Path = ENV_FILE) -> str:
    key = os.getenv("HIKERAPI_KEY", "").strip()
    if not key and env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            key = os.getenv("HIKERAPI_KEY", "").strip()
        except ImportError:
            pass
    return key


def available() -> bool:
    return bool(api_key())


class Provider:
    """Thin client. Every public method = one provider request."""

    def __init__(self, key: Optional[str] = None, session: Optional[requests.Session] = None,
                 base_url: str = BASE_URL, sleep: float = 0.0):
        self.key = key or api_key()
        if not self.key:
            raise ProviderError("HIKERAPI_KEY missing (put it in .env)")
        self.s = session or requests.Session()
        self.base = base_url.rstrip("/")
        self.sleep = sleep
        self.calls = 0

    def _get(self, path: str, **params):
        r = self.s.get(self.base + path, params=params, timeout=TIMEOUT,
                       headers={"x-access-key": self.key, "accept": "application/json"})
        self.calls += 1
        if self.sleep:
            time.sleep(self.sleep)
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise ProviderError(f"provider {r.status_code} on {path}: {r.text[:160]}")
        try:
            return r.json()
        except ValueError as exc:
            raise ProviderError(f"provider returned non-JSON on {path}") from exc

    # -- profile ------------------------------------------------------------
    def profile(self, username: str) -> Optional[dict]:
        """Normalised profile, or None if the account does not exist."""
        u = self._get("/v1/user/by/username", username=username)
        if not u or not u.get("pk"):
            return None
        return normalise_profile(u)

    # -- recency ------------------------------------------------------------
    def newest_post_epoch(self, user_id: str | int, amount: int = 3) -> Optional[int]:
        """Epoch seconds of the newest post among the first `amount` returned
        (max, not first: pinned posts come first and can be old)."""
        items = self._get("/v1/user/medias", user_id=str(user_id), amount=amount)
        if not isinstance(items, list):
            return None
        ts = [_epoch(it.get("taken_at")) for it in items if isinstance(it, dict)]
        ts = [t for t in ts if t]
        return max(ts) if ts else None

    # -- followers (builder) -----------------------------------------------
    def followers_page(self, user_id: str | int, max_id: Optional[str] = None):
        """One page of a user's followers -> (users, next_max_id).
        Users carry pk/username/full_name/is_private/is_verified only."""
        params = {"user_id": str(user_id)}
        if max_id:
            params["max_id"] = max_id
        data = self._get("/v1/user/followers/chunk", **params)
        users, nxt = _unpack_chunk(data)
        return [normalise_follower(u) for u in users], nxt

    def balance(self) -> Optional[dict]:
        try:
            return self._get("/sys/balance")
        except ProviderError:
            return None


# --- normalisers (pure, tested) ---------------------------------------------

def _epoch(v) -> Optional[int]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    try:
        return int(datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def normalise_profile(u: dict) -> dict:
    return {
        "id": str(u.get("pk") or u.get("id") or ""),
        "username": u.get("username") or "",
        "full_name": u.get("full_name") or "",
        "biography": u.get("biography") or "",
        "category_name": u.get("category_name") or u.get("category") or "",
        "is_private": bool(u.get("is_private")),
        "is_verified": bool(u.get("is_verified")),
        "follower_count": _int(u.get("follower_count")),
        "following_count": _int(u.get("following_count")),
        "media_count": _int(u.get("media_count")),
        "external_url": u.get("external_url") or "",
        "city_name": u.get("city_name") or "",
    }


def normalise_follower(u: dict) -> dict:
    return {
        "pk": str(u.get("pk") or u.get("id") or ""),
        "username": u.get("username") or "",
        "full_name": u.get("full_name") or "",
        "is_private": bool(u.get("is_private")),
        "is_verified": bool(u.get("is_verified")),
    }


def _int(v) -> Optional[int]:
    try:
        return None if v is None else int(v)
    except (TypeError, ValueError):
        return None


def _unpack_chunk(data):
    """HikerAPI chunk endpoints return [users, next_max_id] or a dict."""
    if isinstance(data, list) and len(data) == 2 and isinstance(data[0], list):
        return data[0], (data[1] or None)
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        return (data.get("users") or data.get("items") or []), (data.get("next_max_id") or None)
    return [], None


def legacy_user_body(p: dict) -> dict:
    """Wrap a normalised profile in the shape ig_audit_queue_freshness walks
    (Instagram's web_profile_info: data.user.edge_*.count)."""
    return {"data": {"user": {
        "id": p["id"], "username": p["username"], "full_name": p["full_name"],
        "biography": p["biography"], "category_name": p["category_name"],
        "is_private": p["is_private"], "is_verified": p["is_verified"],
        "edge_followed_by": {"count": p["follower_count"]},
        "edge_follow": {"count": p["following_count"]},
        "edge_owner_to_timeline_media": {"count": p["media_count"], "edges": []},
        "external_url": p["external_url"],
    }}}
