"""
scene_intelligence/extract_ra.py
---------------------------------
Tool 1 — Scene Intelligence Engine: Resident Advisor Extractor

Fetches DJs/artists and labels from the Resident Advisor internal GraphQL API
for genres matching Inch of Shadow's sound profile.

Targets:
  Dark Disco / Nu-Disco, Electro, EBM / Industrial, Acid, Techno, Downtempo

Output:
  scene_intelligence/ra_contacts.json   (flat list, standard contact dict format)

Usage:
  python3 scene_intelligence/extract_ra.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent.parent
OUTPUT_DIR  = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "ra_contacts.json"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RA_GRAPHQL      = "https://ra.co/graphql"
REQUEST_DELAY   = 1.5
TIMEOUT         = 12
LIMIT_PER_GENRE = 50  # max contacts per genre per type (dj or label)

# ---------------------------------------------------------------------------
# Genre mapping: (ra_name_fragment, genre_main, genre_sub, match_score)
# match_score: Dark Disco/Acid/Electro = 5, Techno/EBM/Downtempo = 4
# ---------------------------------------------------------------------------
GENRE_MAP: list[tuple[str, str, str, int]] = [
    ("dark disco",  "Electronic", "Dark Disco",  5),
    ("nu-disco",    "Electronic", "Dark Disco",  5),
    ("electro",     "Electronic", "Electro",     5),
    ("acid",        "Electronic", "Acid",        5),
    ("ebm",         "Electronic", "EBM",         4),
    ("industrial",  "Electronic", "EBM",         4),
    ("techno",      "Electronic", "Techno",      4),
    ("downtempo",   "Electronic", "Downtempo",   4),
]

# ---------------------------------------------------------------------------
# GraphQL queries
# ---------------------------------------------------------------------------
GENRE_LIST_QUERY = """
query {
  genres {
    id
    name
    slug
  }
}
"""

DJ_LIST_QUERY = """
query GetDJList($genreId: ID!, $page: Int!) {
  djList(
    filters: { genres: [$genreId] }
    page: $page
    pageSize: 50
  ) {
    data {
      id
      name
      slug
      country { name }
    }
    totalResults
  }
}
"""

LABEL_LIST_QUERY = """
query GetLabelList($genreId: ID!, $page: Int!) {
  labelList(
    filters: { genres: [$genreId] }
    page: $page
    pageSize: 50
  ) {
    data {
      id
      name
      slug
      country { name }
    }
    totalResults
  }
}
"""

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _headers() -> dict:
    return {
        "User-Agent":   "InchOfShadowSceneIntelligence/1.0",
        "Content-Type": "application/json",
        "Origin":       "https://ra.co",
        "Referer":      "https://ra.co/",
        "Accept":       "application/json",
    }


def _post(payload: dict) -> dict | None:
    try:
        r = requests.post(RA_GRAPHQL, json=payload, headers=_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [rate limit] waiting 30s...", flush=True)
            time.sleep(30)
            return None
        print(f"  [HTTP {r.status_code}] RA request failed", flush=True)
        return None
    except requests.RequestException as exc:
        print(f"  [error] {exc}", flush=True)
        return None

# ---------------------------------------------------------------------------
# Genre resolution
# ---------------------------------------------------------------------------

def fetch_genres() -> list[dict]:
    print("  Fetching RA genre list...", flush=True)
    data = _post({"query": GENRE_LIST_QUERY})
    time.sleep(REQUEST_DELAY)
    if not data:
        return []
    return data.get("data", {}).get("genres", []) or []


def _genre_mapping(name: str) -> tuple[str, str, int] | None:
    n = name.lower()
    for fragment, genre_main, genre_sub, score in GENRE_MAP:
        if fragment in n:
            return genre_main, genre_sub, score
    return None


def filter_target_genres(all_genres: list[dict]) -> list[dict]:
    seen_ids: set[str] = set()
    targets = []
    for g in all_genres:
        mapping = _genre_mapping(g.get("name", ""))
        if mapping and g["id"] not in seen_ids:
            genre_main, genre_sub, score = mapping
            seen_ids.add(g["id"])
            targets.append({
                "id": g["id"], "name": g["name"], "slug": g.get("slug", ""),
                "genre_main": genre_main, "genre_sub": genre_sub, "match_score": score,
            })
    return targets

# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_djs(genre_id: str, page: int = 1) -> list[dict]:
    data = _post({"query": DJ_LIST_QUERY, "variables": {"genreId": genre_id, "page": page}})
    time.sleep(REQUEST_DELAY)
    if data and data.get("errors"):
        print(f"    [API error] {data['errors']}")
    return (data or {}).get("data", {}).get("djList", {}).get("data", []) or []


def fetch_labels(genre_id: str, page: int = 1) -> list[dict]:
    data = _post({"query": LABEL_LIST_QUERY, "variables": {"genreId": genre_id, "page": page}})
    time.sleep(REQUEST_DELAY)
    if data and data.get("errors"):
        print(f"    [API error] {data['errors']}")
    return (data or {}).get("data", {}).get("labelList", {}).get("data", []) or []

# ---------------------------------------------------------------------------
# Contact assembly
# ---------------------------------------------------------------------------

def _make_contact(item: dict, contact_type: str, genre_main: str, genre_sub: str, score: int) -> dict:
    slug    = item.get("slug", "")
    name    = item.get("name", "").strip()
    country = (item.get("country") or {}).get("name", "")
    url     = f"https://ra.co/dj/{slug}" if contact_type == "dj" else f"https://ra.co/labels/{slug}"
    return {
        "name":        name,
        "url":         url if slug else "",
        "category":    contact_type,
        "source":      "resident_advisor",
        "genre_main":  genre_main,
        "genre_sub":   genre_sub,
        "location":    country,
        "match_score": str(score),
    }


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_ra() -> list[dict]:
    all_genres = fetch_genres()
    if not all_genres:
        print("  ERROR: Could not fetch RA genre list. Check connectivity.")
        return []

    target_genres = filter_target_genres(all_genres)
    if not target_genres:
        print("  ERROR: No target genres matched in RA genre list.")
        return []

    print(f"  Found {len(target_genres)} target genres:")
    for g in target_genres:
        print(f"    - {g['name']} (sub={g['genre_sub']}, score={g['match_score']})")
    print()

    contacts:  list[dict] = []
    seen_keys: set[str]   = set()

    def _add(contact: dict) -> None:
        key = dedup_key(contact["name"])
        if not key or key in seen_keys:
            return
        seen_keys.add(key)
        contacts.append(contact)

    for genre in target_genres:
        gid, gname = genre["id"], genre["name"]
        gm, gs, score = genre["genre_main"], genre["genre_sub"], genre["match_score"]

        print(f"  [{gname}] Fetching DJs...", end=" ", flush=True)
        dj_count = 0
        for item in fetch_djs(gid)[:LIMIT_PER_GENRE]:
            if item.get("name"):
                _add(_make_contact(item, "dj", gm, gs, score))
                dj_count += 1
        print(f"{dj_count}")

        print(f"  [{gname}] Fetching Labels...", end=" ", flush=True)
        label_count = 0
        for item in fetch_labels(gid)[:LIMIT_PER_GENRE]:
            if item.get("name"):
                _add(_make_contact(item, "label", gm, gs, score))
                label_count += 1
        print(f"{label_count}")

    print()
    return contacts


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("\nScene Intelligence — Resident Advisor Extractor")
    print("=" * 50)

    contacts = extract_ra()
    if not contacts:
        print("  No contacts extracted. ra_contacts.json not written.")
        sys.exit(1)

    cats: dict[str, int] = {}
    for c in contacts:
        cats[c.get("category", "other")] = cats.get(c.get("category", "other"), 0) + 1
    print("  By category:")
    for cat, count in sorted(cats.items()):
        print(f"    {cat:<10} {count}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 50}")
    print(f"  Total: {len(contacts)} contacts")
    print(f"  Saved: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print()


if __name__ == "__main__":
    main()
