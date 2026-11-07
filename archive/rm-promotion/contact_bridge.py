"""
release_manager/contact_bridge.py
-----------------------------------
Connects release genre context to Scene Intelligence contacts.

Given a release's genre, scores and ranks all 920 SI contacts
specifically for that release — not just by generic match_score,
but by how well each contact's genre_sub aligns with this release's sound.

Used by:
  - Promotion Engine: "Add Targets" panel ranked for this release
  - Engagement Engine: daily queue boosted toward genre-relevant contacts

No external APIs. Reads enriched_contacts.json locally.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from release_manager.paths import repo_root

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT = repo_root()   # canonical main repo root (robust to git worktrees)
_ENRICHED_CONTACTS_FILE = _PROJECT_ROOT / "scene_intelligence" / "enriched_contacts.json"
_CONTEXT_FILE = _PROJECT_ROOT / "scene_intelligence" / "release_context.json"

# ---------------------------------------------------------------------------
# Genre keyword map
# Maps a genre name (lowercase) to a list of matching substrings
# checked against contact genre_sub field (case-insensitive).
# Built from actual genre_sub values found in enriched_contacts.json.
# ---------------------------------------------------------------------------

GENRE_KEYWORD_MAP: dict[str, list[str]] = {
    "acid":       ["acid", "acid techno", "acid house", "303"],
    "dark disco": ["dark disco", "darkwave", "dark wave", "disco", "nu-disco",
                   "italo disco", "italo", "cosmic", "balearic", "dance-punk"],
    "ebm":        ["ebm", "cold wave", "coldwave", "body music",
                   "new beat", "dark electro", "electroclash", "electronic body"],
    "electro":    ["electro", "electro-industrial", "electroclash", "bleep",
                   "electro body"],
    "techno":     ["techno", "minimal techno", "industrial techno", "rave"],
    "trance":     ["trance", "psychedelic trance", "progressive trance"],
    "downtempo":  ["downtempo", "trip-hop", "ambient", "chillout", "slowmo",
                   "slow motion"],
    "cinematic":  ["cinematic", "ambient", "neoclassical", "experimental",
                   "soundtrack"],
    "slowmo":     ["slowmo", "slow motion", "downtempo", "cinematic"],
    "minimal":    ["minimal", "minimal techno", "minimal synth", "wave"],
    "darkwave":   ["darkwave", "dark wave", "dark disco", "post-punk",
                   "coldwave", "cold wave", "minimal synth", "synth"],
    "industrial": ["industrial", "power electronics", "noise",
                   "dark electro", "post-industrial"],
    "house":      ["house", "deep house", "tech house", "outsider house",
                   "dance"],
    "disco":      ["disco", "italo disco", "nu-disco", "dark disco",
                   "cosmic", "balearic", "dance"],
    "experimental": ["experimental", "ambient", "noise", "abstract",
                     "outsider"],
}

# EU/Berlin location keywords for location bonus
_EU_KEYWORDS = {
    "berlin", "germany", "de", "deutschland",
    "france", "paris", "uk", "london", "amsterdam", "netherlands",
    "belgium", "brussels", "austria", "vienna", "italy", "rome", "milan",
    "spain", "barcelona", "madrid", "sweden", "stockholm", "denmark",
    "copenhagen", "finland", "helsinki", "norway", "oslo", "switzerland",
    "zurich", "warsaw", "poland", "prague", "czech", "budapest", "hungary",
    "bucharest", "romania", "athens", "greece", "lisbon", "portugal",
    "eu", "europe", "european",
}


# ---------------------------------------------------------------------------
# Genre matching helpers
# ---------------------------------------------------------------------------

def _get_keywords_for_genre(genre: str) -> list[str]:
    """Return keyword list for a genre string (case-insensitive lookup)."""
    if not genre:
        return []
    key = genre.strip().lower()
    # Direct match
    if key in GENRE_KEYWORD_MAP:
        return GENRE_KEYWORD_MAP[key]
    # Partial match — check if any map key is contained in the genre string
    matched: list[str] = []
    for map_key, keywords in GENRE_KEYWORD_MAP.items():
        if map_key in key or key in map_key:
            matched.extend(keywords)
    return matched


def _genre_sub_matches(genre_sub: str, keywords: list[str]) -> list[str]:
    """
    Return which keywords were found in genre_sub.
    genre_sub format: "Dark Disco / EBM / Post-Punk"
    """
    if not genre_sub or not keywords:
        return []
    sub_lower = genre_sub.lower()
    return [kw for kw in keywords if kw.lower() in sub_lower]


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def _build_boss_label_map(contacts: list[dict]) -> dict[str, str]:
    """Build a map from label_boss name (lowercase) -> label display name.

    Used to show DJs which label they run.
    """
    boss_map: dict[str, str] = {}
    for c in contacts:
        if c.get("category") != "label":
            continue
        boss = c.get("label_boss", "")
        if boss:
            boss_map[boss.lower()] = c.get("name", "")
    return boss_map


def score_contacts_for_release(
    contacts: list[dict],
    genre_primary: str,
    genre_secondary: str = "",
    added_names: set[str] | None = None,
) -> list[dict]:
    """
    Score and rank contacts for a specific release genre.

    Adds to each contact dict:
      - release_score (int, 0-10): genre-aware score for this release
      - match_reasons (list[str]): human-readable reasons for the score
      - added (bool): whether already in this release's campaign

    Returns contacts sorted by release_score descending.
    Only includes categories relevant to promotion: dj, label, media,
    promoter, venue.
    """
    if added_names is None:
        added_names = set()

    primary_keywords = _get_keywords_for_genre(genre_primary)
    secondary_keywords = _get_keywords_for_genre(genre_secondary)

    # Build boss <-> label lookup
    boss_label_map = _build_boss_label_map(contacts)

    result = []

    for c in contacts:
        cat = c.get("category", "")
        if cat not in ("dj", "label", "media", "venue", "promoter", "distributor"):
            continue

        # Base score from SI (1-5)
        raw = c.get("match_score", "2")
        try:
            base = int(raw)
        except (ValueError, TypeError):
            base = 2

        score = base
        reasons: list[str] = []

        genre_sub = c.get("genre_sub", "")
        has_genre_match = False

        # Primary genre match (+3)
        if primary_keywords:
            hits = _genre_sub_matches(genre_sub, primary_keywords)
            if hits:
                score += 3
                reasons.append(f"{genre_primary} match")
                has_genre_match = True

        # Secondary genre match (+2)
        if secondary_keywords:
            hits2 = _genre_sub_matches(genre_sub, secondary_keywords)
            if hits2:
                score += 2
                reasons.append(f"{genre_secondary} match")
                has_genre_match = True

        # Location bonus: Berlin/EU (+1)
        location = (c.get("location") or "").lower()
        if any(kw in location for kw in _EU_KEYWORDS):
            score += 1
            reasons.append("EU-based")

        # Activity bonus: active in 2024-2025 (+1)
        last_year = str(c.get("discogs_last_year", "") or "")
        yt_upload = str(c.get("youtube_last_upload", "") or "")
        sc_tracks = c.get("soundcloud_tracks", "")
        try:
            sc_tracks_int = int(sc_tracks)
        except (ValueError, TypeError):
            sc_tracks_int = 0
        if last_year >= "2024" or yt_upload >= "2024" or sc_tracks_int > 0:
            score += 1
            reasons.append("Active recently")

        # Email available (+1)
        demo_email = c.get("demo_email", "")
        discogs_email = c.get("discogs_email", "")
        has_real_email = (
            (demo_email and demo_email not in ("DM ONLY", "NO DEMOS"))
            or discogs_email
        )
        if has_real_email:
            score += 1
            reasons.append("Email available")

        # Cap at 10
        score = min(score, 10)

        result.append({
            "name": c.get("name", ""),
            "category": cat,
            "sub_type": c.get("sub_type", ""),
            "genre_sub": genre_sub,
            "location": c.get("location", ""),
            "score": base,           # original SI score 1-5
            "release_score": score,  # genre-aware score 0-10
            "match_reasons": reasons,
            "has_genre_match": has_genre_match,
            "has_email": bool(
                (c.get("demo_email", "") or c.get("discogs_email", ""))
                and c.get("demo_email", "") not in ("DM ONLY", "NO DEMOS")
            ),
            "dm_only": c.get("demo_email", "") == "DM ONLY",
            "no_demos": c.get("demo_email", "") == "NO DEMOS",
            "tier": c.get("tier", ""),
            "url": c.get("url", ""),
            "added": c.get("name", "") in added_names,
            "soundcloud_url": c.get("soundcloud_url", ""),
            "spotify_url": c.get("spotify_url", ""),
            "youtube_url": c.get("youtube_url", ""),
            "discogs_url": c.get("discogs_url", ""),
            "label_boss": c.get("label_boss", ""),
            "is_label_boss": bool(c.get("is_label_boss")),
            "boss_of_label": boss_label_map.get(c.get("name", "").lower(), ""),
        })

    result.sort(key=lambda x: (x["release_score"], x["score"]), reverse=True)
    return result


def get_genre_bonus(contact: dict, genre_primary: str,
                    genre_secondary: str = "") -> int:
    """
    Return a priority bonus (0-30) for use in engagement queue building.
    Used by _build_platform_queue() to boost genre-relevant contacts.
    """
    primary_keywords = _get_keywords_for_genre(genre_primary)
    secondary_keywords = _get_keywords_for_genre(genre_secondary)
    genre_sub = contact.get("genre_sub", "")

    bonus = 0
    if primary_keywords and _genre_sub_matches(genre_sub, primary_keywords):
        bonus += 20
    if secondary_keywords and _genre_sub_matches(genre_sub, secondary_keywords):
        bonus += 10
    return bonus


# ---------------------------------------------------------------------------
# Release context — shared across Promotion + Engagement
# ---------------------------------------------------------------------------

def get_active_release_context() -> dict:
    """
    Load the currently active release context.
    Returns dict with keys: slug, title, genre_primary, genre_secondary
    or empty dict if none set.
    """
    if not _CONTEXT_FILE.exists():
        return {}
    try:
        with open(_CONTEXT_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def set_active_release_context(slug: str, title: str,
                                genre_primary: str,
                                genre_secondary: str = "") -> None:
    """Save the active release context for use across all tools."""
    _CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": slug,
        "title": title,
        "genre_primary": genre_primary,
        "genre_secondary": genre_secondary,
        "set_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(_CONTEXT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def clear_active_release_context() -> None:
    """Clear the active release context."""
    if _CONTEXT_FILE.exists():
        _CONTEXT_FILE.unlink()
