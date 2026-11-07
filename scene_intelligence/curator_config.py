"""
scene_intelligence/curator_config.py
-------------------------------------
Genre keywords, thresholds, and filter helpers for curator discovery.

Edit GENRE_KEYWORDS to tune which playlists qualify. Keep entries lowercase.
"""

from __future__ import annotations

# Order matters for match_genres — longer multi-word keywords should come
# before their single-word substrings so "acid techno" is matched before "acid".
GENRE_KEYWORDS: list[str] = [
    "dark disco",
    "acid techno",
    "industrial techno",
    "dark techno",
    "melodic techno",
    "cosmic disco",
    "italo disco",
    "minimal wave",
    "cold wave",
    "coldwave",
    "dark wave",
    "darkwave",
    "darksynth",
    "post-punk",
    "ebm",
    "aggrotech",
    "slowmo",
]
# NOTE: "electro" and "synthwave" were tried 2026-06-15 but pulled mainstream EDM /
# retro-gaming-synthwave noise (Deep House 2026, Night Drive, etc), so they are dropped.
# "italo disco" / "melodic techno" are kept but skew adjacent — prune candidates by hand.

# A playlist must have at least this many followers to count its owner as a curator.
SPOTIFY_MIN_PLAYLIST_FOLLOWERS = 500
SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS = 100

# An owner with total playlist followers below this is dropped even if they qualify on one playlist.
SPOTIFY_MIN_OWNER_TOTAL = 500
SOUNDCLOUD_MIN_OWNER_TOTAL = 100

# Editorial / platform-run accounts to skip.
_EDITORIAL_OWNER_IDS: set[str] = {"spotify", "spotifyforartists"}
_EDITORIAL_DISPLAY_NAMES: set[str] = {"spotify"}


def match_genres(title: str = "", description: str = "") -> list[str]:
    """Return the list of GENRE_KEYWORDS found in the title or description.

    Case-insensitive. Preserves keyword order from GENRE_KEYWORDS so
    multi-word keywords rank before their substrings.
    """
    blob = f"{title} {description}".lower()
    return [kw for kw in GENRE_KEYWORDS if kw in blob]


def is_editorial_owner(display_name: str, owner_id: str) -> bool:
    """Detect Spotify-run and platform-editorial accounts we don't treat as curators."""
    if (owner_id or "").strip().lower() in _EDITORIAL_OWNER_IDS:
        return True
    if (display_name or "").strip().lower() in _EDITORIAL_DISPLAY_NAMES:
        return True
    return False
