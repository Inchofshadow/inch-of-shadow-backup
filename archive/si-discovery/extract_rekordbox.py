"""
scene_intelligence/extract_rekordbox.py
----------------------------------------
Extract artists and labels from a Rekordbox XML library export.

Filters non-electronic genres (rock, pop, hip-hop, etc.) while keeping
tracks that appear in DJ/gig playlists regardless of genre tag.
Deduplicates against existing enriched_contacts.json.

Only adds artists/labels with 2+ tracks to avoid one-off noise.

Usage:
  python3 scene_intelligence/extract_rekordbox.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key, CATEGORY_DEFAULT_SCORE

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR       = Path(__file__).parent.parent
DATA_FILE      = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"
REKORDBOX_XML  = BASE_DIR / "data" / "rekordbox_library.xml"

MIN_TRACKS     = 2   # minimum tracks to qualify as a contact

# ---------------------------------------------------------------------------
# Genre filtering
# ---------------------------------------------------------------------------

# If genre contains ANY of these -> exclude (unless overridden or in a gig playlist)
_EXCLUDE_GENRE = re.compile(
    r"\b(rock|metal|blues|classical|folk|country|ska|reggae|r&b|soul"
    r"|hip[- ]?hop|rap|glam|arena|shoegaze|slowcore|chanson)\b",
    re.IGNORECASE,
)

# Override: these keywords KEEP a track even if an exclude keyword also matches
_KEEP_GENRE = re.compile(
    r"\b(electro|techno|house|synth|wave|kraut|electronic|ebm|industrial"
    r"|acid|post[- ]?punk|electroclash|coldwave|dark|minimal|ambient"
    r"|disco|trance|italo|idm|downtempo|leftfield|balearic|breaks)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Playlists to EXCLUDE (non-electronic / personal)
# ---------------------------------------------------------------------------
_EXCLUDE_PLAYLISTS = {
    "WEDDING INTRO", "WEDDING DANCE",
    "Psychedicelic rock",   # typo in actual data
    "Psychedelic rock",
    "Slow", "guitar romano", "Teder GTR", "My Minor",
    "Hip Hop (1)", "Songs", "Untitled Playlist",
}

# ---------------------------------------------------------------------------
# Skip these artist names (own projects, compilations, junk)
# ---------------------------------------------------------------------------
_SKIP_ARTISTS = {
    "various", "variousartists", "va", "unknown", "unknownartist",
    "doublefigure", "inchofshadow",
}

# ---------------------------------------------------------------------------
# Skip these label names (download sites, junk)
# ---------------------------------------------------------------------------
_SKIP_LABEL_WORDS = (
    "mp3db", "pmedia", "n/a", "ftpdj", "djsoundtop", "sharingdb",
    "clapcrate", "electronicfresh", "dazed digital",
)

# ---------------------------------------------------------------------------
# Venue / promoter / media contacts from playlist metadata
# ---------------------------------------------------------------------------
_PLAYLIST_CONTACTS = [
    {
        "name": "SOHO Tel Aviv",
        "category": "venue",
        "location": "Tel Aviv",
        "genre_main": "Disco",
        "genre_sub": "Electronic, Indie Dance",
    },
    {
        "name": "Tortured Garden Berlin",
        "category": "promoter",
        "location": "Berlin",
        "genre_main": "Disco",
        "genre_sub": "New Wave, EBM",
    },
    {
        "name": "The Code",
        "category": "promoter",
        "location": "",
        "genre_main": "Electronic",
        "genre_sub": "",
    },
    {
        "name": "Shape of Us",
        "category": "promoter",
        "location": "",
        "genre_main": "Techno",
        "genre_sub": "",
    },
    {
        "name": "Teder.fm",
        "category": "media",
        "location": "Tel Aviv",
        "genre_main": "Electronic",
        "genre_sub": "",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_relevant_genre(genre: str) -> bool | None:
    """True = keep, False = exclude, None = no genre tag."""
    if not genre.strip():
        return None
    if _KEEP_GENRE.search(genre):
        return True
    if _EXCLUDE_GENRE.search(genre):
        return False
    return True  # unknown genre -> keep


def _normalize_genre(genre: str) -> str:
    """Pick a clean main genre from messy Rekordbox genre strings."""
    g = genre.strip().lower()
    if not g:
        return ""
    for label, pattern in [
        ("Techno",      r"\btechno\b"),
        ("Electro",     r"\belectro\b"),
        ("House",       r"\bhouse\b"),
        ("Disco",       r"\bdisco\b"),
        ("EBM",         r"\bebm\b"),
        ("Darkwave",    r"\bdark\s?wave\b"),
        ("Ambient",     r"\bambient\b"),
        ("Trance",      r"\btrance\b"),
        ("Acid",        r"\bacid\b"),
        ("IDM",         r"\bidm\b"),
        ("Industrial",  r"\bindustrial\b"),
        ("Minimal",     r"\bminimal\b"),
        ("Downtempo",   r"\bdowntempo\b"),
        ("Italo Disco", r"\bitalo\b"),
        ("Synthpop",    r"\bsynth\s?pop\b"),
        ("New Wave",    r"\bnew\s?wave\b"),
        ("New Beat",    r"\bnew\s?beat\b"),
        ("Krautrock",   r"\bkraut\b"),
        ("Breaks",      r"\bbreaks?\b"),
        ("Dub",         r"\bdub\b"),
        ("Balearic",    r"\bbalearic\b"),
        ("Post-Punk",   r"\bpost[- ]?punk\b"),
        ("Coldwave",    r"\bcold\s?wave\b"),
        ("Trip-Hop",    r"\btrip[- ]?hop\b"),
        ("Electronic",  r"\belectronic\b"),
    ]:
        if re.search(pattern, g):
            return label
    # Fallback: first segment cleaned up
    return genre.split(",")[0].split(";")[0].strip().title()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence — Rekordbox Extract")
    print("=" * 46)

    if not REKORDBOX_XML.exists():
        print(f"ERROR: {REKORDBOX_XML} not found.")
        sys.exit(1)

    # ---- Parse XML --------------------------------------------------------
    tree = ET.parse(str(REKORDBOX_XML))
    root = tree.getroot()

    # Build track dict: id -> attributes
    all_tracks: dict[str, dict] = {}
    for t in root.findall(".//COLLECTION/TRACK"):
        tid = t.get("TrackID", "")
        if tid:
            all_tracks[tid] = {
                "artist": t.get("Artist", "").strip(),
                "genre":  t.get("Genre", "").strip(),
                "label":  t.get("Label", "").strip(),
                "year":   t.get("Year", "").strip(),
                "plays":  int(t.get("PlayCount", "0") or "0"),
            }

    print(f"  Total tracks in library: {len(all_tracks)}")

    # ---- Build playlist membership ----------------------------------------
    track_playlists: dict[str, set[str]] = {}
    for node in root.iter("NODE"):
        if node.get("Type") != "1":
            continue
        pname = node.get("Name", "")
        if pname in _EXCLUDE_PLAYLISTS:
            continue
        for tref in node.findall("TRACK"):
            key = tref.get("Key", "")
            if key:
                track_playlists.setdefault(key, set()).add(pname)

    # ---- Filter tracks ----------------------------------------------------
    relevant_tracks: list[dict] = []
    excluded = 0
    for tid, track in all_tracks.items():
        in_playlist = tid in track_playlists
        genre_ok = _is_relevant_genre(track["genre"])

        if genre_ok is False and not in_playlist:
            excluded += 1
            continue

        relevant_tracks.append(track)

    print(f"  Relevant tracks:         {len(relevant_tracks)}")
    print(f"  Excluded (non-electronic): {excluded}")

    # ---- Aggregate artists ------------------------------------------------
    artists: dict[str, dict] = {}
    for track in relevant_tracks:
        artist = track["artist"]
        if not artist:
            continue

        key = dedup_key(artist)
        if not key or key in _SKIP_ARTISTS:
            continue

        if key not in artists:
            artists[key] = {
                "name": artist,
                "tracks": 0,
                "genres": {},
                "labels": [],
                "plays": 0,
            }
        a = artists[key]
        a["tracks"] += 1
        a["plays"] += track["plays"]

        genre = track["genre"].strip()
        if genre:
            a["genres"][genre] = a["genres"].get(genre, 0) + 1

        label = track["label"].strip()
        if label and label not in a["labels"]:
            a["labels"].append(label)

    # ---- Aggregate labels -------------------------------------------------
    labels: dict[str, dict] = {}
    for track in relevant_tracks:
        label = track["label"]
        if not label:
            continue

        key = dedup_key(label)
        if not key:
            continue

        # Skip junk labels
        if any(x in label.lower() for x in _SKIP_LABEL_WORDS):
            continue

        if key not in labels:
            labels[key] = {
                "name": label,
                "tracks": 0,
                "genres": {},
            }
        l = labels[key]
        l["tracks"] += 1

        genre = track["genre"].strip()
        if genre:
            l["genres"][genre] = l["genres"].get(genre, 0) + 1

    print(f"  Unique artists (all):    {len(artists)}")
    print(f"  Unique labels  (all):    {len(labels)}")
    print(f"  Min tracks threshold:    {MIN_TRACKS}")

    # ---- Load existing contacts -------------------------------------------
    existing: list[dict] = []
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            existing = json.load(f)

    existing_keys: set[str] = {dedup_key(c.get("name", "")) for c in existing}
    overlap_artists = sum(1 for k in artists if k in existing_keys)
    overlap_labels  = sum(1 for k in labels if k in existing_keys)
    print(f"\n  Already in contacts:")
    print(f"    Artists: {overlap_artists}")
    print(f"    Labels:  {overlap_labels}")

    # ---- Build new contacts -----------------------------------------------
    new_contacts: list[dict] = []

    # Artists -> DJs
    for key, a in sorted(artists.items(), key=lambda x: -x[1]["tracks"]):
        if key in existing_keys:
            continue
        if a["tracks"] < MIN_TRACKS:
            continue

        top_genre = ""
        if a["genres"]:
            top_raw = max(a["genres"], key=a["genres"].get)
            top_genre = _normalize_genre(top_raw)

        score = "3" if a["tracks"] >= 5 else "2"

        new_contacts.append({
            "name":             a["name"],
            "category":         "dj",
            "source":           "rekordbox",
            "url":              "",
            "genre_main":       top_genre,
            "genre_sub":        "",
            "location":         "",
            "match_score":      score,
            "rekordbox_tracks": str(a["tracks"]),
            "rekordbox_plays":  str(a["plays"]),
        })
        existing_keys.add(key)

    # Labels
    for key, l in sorted(labels.items(), key=lambda x: -x[1]["tracks"]):
        if key in existing_keys:
            continue
        if l["tracks"] < MIN_TRACKS:
            continue

        top_genre = ""
        if l["genres"]:
            top_raw = max(l["genres"], key=l["genres"].get)
            top_genre = _normalize_genre(top_raw)

        score = "3" if l["tracks"] >= 5 else "2"

        new_contacts.append({
            "name":             l["name"],
            "category":         "label",
            "source":           "rekordbox",
            "url":              "",
            "genre_main":       top_genre,
            "genre_sub":        "",
            "location":         "",
            "match_score":      score,
            "rekordbox_tracks": str(l["tracks"]),
        })
        existing_keys.add(key)

    # Venue / promoter / media contacts
    for pc in _PLAYLIST_CONTACTS:
        key = dedup_key(pc["name"])
        if key in existing_keys:
            continue
        new_contacts.append({
            "name":        pc["name"],
            "category":    pc["category"],
            "source":      "rekordbox",
            "url":         "",
            "genre_main":  pc.get("genre_main", ""),
            "genre_sub":   pc.get("genre_sub", ""),
            "location":    pc.get("location", ""),
            "match_score": CATEGORY_DEFAULT_SCORE.get(pc["category"], "2"),
        })
        existing_keys.add(key)

    # ---- Summary ----------------------------------------------------------
    cats: dict[str, int] = {}
    for c in new_contacts:
        cat = c["category"]
        cats[cat] = cats.get(cat, 0) + 1

    print(f"\n  New contacts to add:     {len(new_contacts)}")
    for cat, count in sorted(cats.items()):
        print(f"    {cat}: {count}")

    # Top new artists
    new_artists = [c for c in new_contacts if c["category"] == "dj"]
    if new_artists:
        print(f"\n  Top new artists (by track count):")
        for c in new_artists[:20]:
            tc = c.get("rekordbox_tracks", "")
            genre = c.get("genre_main", "")
            parts = [f"{tc} tracks"]
            if genre:
                parts.append(genre)
            print(f"    {c['name'][:35]:<35}  {' | '.join(parts)}")
        if len(new_artists) > 20:
            print(f"    ... and {len(new_artists) - 20} more")

    # Top new labels
    new_labels = [c for c in new_contacts if c["category"] == "label"]
    if new_labels:
        print(f"\n  Top new labels (by track count):")
        for c in new_labels[:15]:
            tc = c.get("rekordbox_tracks", "")
            genre = c.get("genre_main", "")
            parts = [f"{tc} tracks"]
            if genre:
                parts.append(genre)
            print(f"    {c['name'][:35]:<35}  {' | '.join(parts)}")
        if len(new_labels) > 15:
            print(f"    ... and {len(new_labels) - 15} more")

    # ---- Save -------------------------------------------------------------
    existing.extend(new_contacts)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n  Total contacts now:      {len(existing)}")
    print(f"  Saved to: {DATA_FILE.name}")
    print()


if __name__ == "__main__":
    main()
