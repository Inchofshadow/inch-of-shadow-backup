"""
release_manager/models.py
--------------------------
Data structures, constants, validation, and factory functions for releases.
"""

from __future__ import annotations

import re
from datetime import datetime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1

RELEASE_TYPES = ["Single", "EP", "Album"]

VALID_KEYS = [
    "C", "Cm", "C#", "C#m", "Db", "Dbm",
    "D", "Dm", "D#", "D#m", "Eb", "Ebm",
    "E", "Em",
    "F", "Fm", "F#", "F#m", "Gb", "Gbm",
    "G", "Gm", "G#", "G#m", "Ab", "Abm",
    "A", "Am", "A#", "A#m", "Bb", "Bbm",
    "B", "Bm",
]

ALL_PLATFORMS = [
    "spotify", "apple_music", "beatport", "traxsource",
    "bandcamp", "soundcloud", "audius", "catalog",
    "youtube_music", "deezer", "tidal",
]

DISTRIBUTION_STATUSES = ["draft", "submitted", "approved", "live", "rejected"]

DEFAULT_ARTIST = "Inch of Shadow"
WRITER_LEGAL_NAME = "Amir Miller"


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def make_slug(title: str, release_type: str) -> str:
    """Generate a filesystem-safe slug from title + type.

    Example: 'Dark Disco Acid', 'EP' -> 'dark-disco-acid-ep'
    """
    raw = f"{title} {release_type}".lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_date(date_str: str) -> bool:
    """Validate YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_duration(duration_str: str) -> bool:
    """Validate M:SS or MM:SS format."""
    return bool(re.match(r"^\d{1,2}:\d{2}$", duration_str))


def validate_bpm(bpm: int | float) -> bool:
    """Validate BPM is in a reasonable range."""
    return 60 <= bpm <= 200


# ---------------------------------------------------------------------------
# Factory: new release dict
# ---------------------------------------------------------------------------

def new_release_dict(
    title: str,
    release_type: str,
    release_date: str,
    genre_primary: str = "",
    genre_secondary: str = "",
    artist: str = DEFAULT_ARTIST,
    description: str = "",
) -> dict:
    """Create a complete release dict ready for JSON serialization."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    year = release_date[:4] if release_date else str(datetime.now().year)

    return {
        "schema_version": SCHEMA_VERSION,
        "slug": make_slug(title, release_type),
        "created_at": now,
        "updated_at": now,

        "metadata": {
            "title": title,
            "artist": artist,
            "release_type": release_type,
            "genre_primary": genre_primary,
            "genre_secondary": genre_secondary,
            "catalog_number": "",
            "copyright": f"{year} {artist}",
            "copyright_p": f"{year} {artist}",
            "description": description,
            "language": "en",
            "explicit": False,
        },

        "release_date": release_date,

        "distribution": {
            "distributor": "Symphonic",
            "distributor_id": "",
            "upc": "",
            "status": "draft",
            "submitted_date": "",
            "approved_date": "",
            "live_date": "",
            "notes": "",
        },

        "tracks": [],

        "platform_links": {p: "" for p in ALL_PLATFORMS},

        "platform_tags": {
            "spotify": {"genre": "", "subgenres": [], "moods": [], "cultures": []},
            "beatport": {"genre": "", "subgenre": ""},
            "traxsource": {"genre": ""},
            "bandcamp": {"tags": []},
        },

        "checklist": [],
        "timeline": [],
        "notes": "",
    }


# ---------------------------------------------------------------------------
# Factory: new track dict
# ---------------------------------------------------------------------------

def new_track_dict(
    number: int,
    title: str,
    artist: str = DEFAULT_ARTIST,
    bpm: int | float = 0,
    key: str = "",
    duration: str = "",
    genre_primary: str = "",
    genre_secondary: str = "",
) -> dict:
    """Create a track dict with default credits."""
    return {
        "number": number,
        "title": title,
        "artist": artist,
        "featured_artist": "",
        "remix_artist": "",
        "bpm": bpm,
        "key": key,
        "duration": duration,
        "isrc": "",
        "genre_primary": genre_primary,
        "genre_secondary": genre_secondary,
        "credits": {
            "producer": DEFAULT_ARTIST,
            "mixer": DEFAULT_ARTIST,
            "mastering": DEFAULT_ARTIST,
            "writer": WRITER_LEGAL_NAME,
        },
        "notes": "",
    }


# ---------------------------------------------------------------------------
# Validation: release completeness
# ---------------------------------------------------------------------------

def validate_release(data: dict) -> list[str]:
    """Check a release dict for completeness.

    Returns a list of warning strings (empty = fully valid).
    """
    warnings: list[str] = []
    meta = data.get("metadata", {})

    # Required metadata
    if not meta.get("title"):
        warnings.append("Title is missing")
    if not meta.get("artist"):
        warnings.append("Artist is missing")
    if not data.get("release_date"):
        warnings.append("Release date is missing")
    elif not validate_date(data["release_date"]):
        warnings.append(f"Release date format invalid: {data['release_date']}")
    if not meta.get("release_type"):
        warnings.append("Release type is missing")

    # Copyright
    if not meta.get("copyright"):
        warnings.append("Copyright line is missing")

    # Distribution
    dist = data.get("distribution", {})
    if not dist.get("upc"):
        warnings.append("UPC missing (assigned by distributor)")
    if not dist.get("distributor"):
        warnings.append("Distributor not set")
    if dist.get("status", "draft") == "draft":
        warnings.append("Not yet submitted to distributor")

    # Tracks
    tracks = data.get("tracks", [])
    if not tracks:
        warnings.append("No tracks added")
    for t in tracks:
        prefix = f"Track {t.get('number', '?')} — {t.get('title', 'Untitled')}"
        if not t.get("isrc"):
            warnings.append(f"{prefix}: ISRC missing (assigned by distributor)")
        if not t.get("bpm"):
            warnings.append(f"{prefix}: BPM missing")
        if not t.get("key"):
            warnings.append(f"{prefix}: Key missing")
        if not t.get("duration"):
            warnings.append(f"{prefix}: Duration missing")
        credits = t.get("credits", {})
        if not credits.get("mastering"):
            warnings.append(f"{prefix}: Mastering credit missing")

    return warnings
