# Curator Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Discover playlist curators on Spotify and SoundCloud who curate playlists matching Inch of Shadow's genres (dark disco, acid, electro, EBM, techno, etc.), add them to Scene Intelligence as a new `curator` category, and expose them in the Promotion Engine's contact picker for playlist-pitch campaigns.

**Architecture:** New `scene_intelligence/discover_curators.py` follows the pattern of `discover_contacts.py` — a single CLI script with two phases (Spotify, SoundCloud). Genre keywords and thresholds live in `scene_intelligence/curator_config.py`. Each phase: search platform for playlists matching genre keywords → fetch playlist metadata → aggregate playlists by owner → filter editorial/low-follower owners → add qualifying owners to `enriched_contacts.json` as `category: "curator"`, `sub_type: "spotify" | "soundcloud"`. Sheets integration adds a new "Curators" tab in `push_to_sheets.py`. Promotion Engine gains a `curator` option in its category filter. Reuses existing Spotify/SoundCloud client-credentials OAuth helpers (no new env vars).

**Tech Stack:** Python 3.9+, `requests`, `python-dotenv`, existing `SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET`/`SOUNDCLOUD_CLIENT_ID`/`SOUNDCLOUD_CLIENT_SECRET` env vars, `gspread` for Sheets, Flask for Promotion Engine UI, `pytest` (new) for unit tests.

---

## File Structure

**New files:**
- `scene_intelligence/curator_config.py` — genre keywords, thresholds, platform constants
- `scene_intelligence/discover_curators.py` — main discovery script (Spotify + SoundCloud phases)
- `tests/__init__.py` — empty, marks tests as a package
- `tests/test_curator_config.py` — tests for genre matching and filter helpers
- `tests/test_discover_curators.py` — tests for pure-logic functions (aggregation, dedup)

**Modified files:**
- `scene_intelligence/utils.py` — add `"curator": "3"` to `CATEGORY_DEFAULT_SCORE`
- `scene_intelligence/push_to_sheets.py` — add "Curators" tab to tabs list, `_SYNC_TABS`, `_TAB_CONFIG`
- `release_manager/webapp.py` — add `"curator"` to the Promotion Engine category filter dropdown
- `release_manager/templates/promotion.html` (or equivalent) — add curator option in filter UI
- `requirements.txt` — add `pytest`
- `CLAUDE.md` — add `python3 scene_intelligence/discover_curators.py` to key commands

---

## Data Model

A curator contact added to `enriched_contacts.json`:

```json
{
  "name": "Dark Disco Weekly",
  "category": "curator",
  "sub_type": "spotify",
  "source": "curator_discovery",
  "url": "https://open.spotify.com/user/12345",
  "genre_main": "Electronic",
  "genre_sub": "dark disco / acid / electro",
  "location": "",
  "match_score": "3",

  "spotify_id": "12345",
  "spotify_url": "https://open.spotify.com/user/12345",

  "playlist_count": 4,
  "playlist_total_followers": 12500,
  "top_playlist_name": "Dark Disco 2026",
  "top_playlist_followers": 8200,
  "top_playlist_url": "https://open.spotify.com/playlist/abc123",
  "playlist_genres": "dark disco, acid, electro",
  "playlist_urls": "https://open.spotify.com/playlist/abc123 | https://open.spotify.com/playlist/def456",
  "discovered_via": "search:dark disco,search:acid"
}
```

SoundCloud curator rows use `sub_type: "soundcloud"` and populate `soundcloud_user_id`, `soundcloud_url`, `soundcloud_followers` etc. alongside the shared `playlist_*` fields.

---

### Task 1: Set up pytest and test package

**Files:**
- Create: `tests/__init__.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add pytest to requirements**

Open `requirements.txt` and append `pytest` on a new line.

- [ ] **Step 2: Install pytest**

Run: `pip3 install pytest`
Expected: `Successfully installed pytest-...` or "already satisfied"

- [ ] **Step 3: Create empty tests package marker**

Create `tests/__init__.py` with a single comment line:

```python
# Marker file so pytest treats tests/ as a package.
```

- [ ] **Step 4: Verify pytest runs**

Run: `pytest tests/ -v`
Expected: "no tests ran" (exit code 5 is fine — no tests exist yet)

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "chore: add pytest for unit tests on new discovery logic"
```

---

### Task 2: Create curator_config module with genre keywords and thresholds

**Files:**
- Create: `scene_intelligence/curator_config.py`
- Test: `tests/test_curator_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_curator_config.py`:

```python
from scene_intelligence.curator_config import (
    GENRE_KEYWORDS,
    match_genres,
    is_editorial_owner,
    SPOTIFY_MIN_PLAYLIST_FOLLOWERS,
    SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS,
)


def test_genre_keywords_non_empty():
    assert len(GENRE_KEYWORDS) >= 8
    assert "dark disco" in GENRE_KEYWORDS
    assert "acid" in GENRE_KEYWORDS
    assert "ebm" in GENRE_KEYWORDS


def test_match_genres_finds_keyword_in_title():
    matches = match_genres("Dark Disco 2026 - Best Tracks")
    assert "dark disco" in matches


def test_match_genres_is_case_insensitive():
    matches = match_genres("ACID TECHNO VIBES")
    assert "acid techno" in matches or "acid" in matches


def test_match_genres_scans_description():
    matches = match_genres(
        title="Generic Title",
        description="A playlist of dark disco, EBM, and electro music."
    )
    assert "dark disco" in matches
    assert "ebm" in matches
    assert "electro" in matches


def test_match_genres_empty_on_no_match():
    assert match_genres("Top 40 Pop Hits") == []


def test_is_editorial_owner_detects_spotify():
    assert is_editorial_owner("Spotify", "spotify") is True
    assert is_editorial_owner("spotify", "") is True


def test_is_editorial_owner_allows_user():
    assert is_editorial_owner("Berlin DJ", "berlindj123") is False


def test_thresholds_are_sane():
    assert SPOTIFY_MIN_PLAYLIST_FOLLOWERS >= 100
    assert SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS >= 50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_curator_config.py -v`
Expected: ModuleNotFoundError for `scene_intelligence.curator_config`

- [ ] **Step 3: Write minimal implementation**

Create `scene_intelligence/curator_config.py`:

```python
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
    "melodic techno",
    "post-punk",
    "cold wave",
    "cosmic disco",
    "italo disco",
    "minimal wave",
    "synthwave",
    "dark wave",
    "acid",
    "electro",
    "ebm",
    "techno",
    "slowmo",
    "cinematic",
    "hypnotic",
    "berlin",
]

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_curator_config.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add scene_intelligence/curator_config.py tests/test_curator_config.py
git commit -m "feat(si): add curator_config with genre keywords and filters"
```

---

### Task 3: Add "curator" to CATEGORY_DEFAULT_SCORE

**Files:**
- Modify: `scene_intelligence/utils.py`

- [ ] **Step 1: Add curator to the score map**

Edit `scene_intelligence/utils.py`. Change:

```python
CATEGORY_DEFAULT_SCORE: dict[str, str] = {
    "distributor": "3",
    "platform":    "3",
    "venue":       "3",
    "promoter":    "3",
    "label":       "2",
    "dj":          "2",
    "artist":      "2",
    "personal":    "2",
    "media":       "2",
    "other":       "1",
}
```

To:

```python
CATEGORY_DEFAULT_SCORE: dict[str, str] = {
    "distributor": "3",
    "platform":    "3",
    "venue":       "3",
    "promoter":    "3",
    "curator":     "3",
    "label":       "2",
    "dj":          "2",
    "artist":      "2",
    "personal":    "2",
    "media":       "2",
    "other":       "1",
}
```

- [ ] **Step 2: Verify import still works**

Run: `python3 -c "from scene_intelligence.utils import CATEGORY_DEFAULT_SCORE; print(CATEGORY_DEFAULT_SCORE['curator'])"`
Expected: `3`

- [ ] **Step 3: Commit**

```bash
git add scene_intelligence/utils.py
git commit -m "feat(si): register curator category with default score 3"
```

---

### Task 4: Write pure-logic helpers for aggregating playlists by owner

**Files:**
- Test: `tests/test_discover_curators.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_discover_curators.py`:

```python
"""Pure-logic tests for discover_curators. API calls are covered by manual smoke tests."""

from scene_intelligence.discover_curators import (
    aggregate_playlists_by_owner,
    build_candidate_row,
    filter_existing,
)


def _pl(playlist_id, name, followers, owner_id, owner_name, genres, url=""):
    return {
        "id": playlist_id,
        "name": name,
        "followers": followers,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "matched_genres": genres,
        "url": url or f"https://open.spotify.com/playlist/{playlist_id}",
    }


def test_aggregate_groups_playlists_by_owner_id():
    playlists = [
        _pl("p1", "Dark Disco", 2000, "user1", "DJ One", ["dark disco"]),
        _pl("p2", "Acid Cuts",   800, "user1", "DJ One", ["acid"]),
        _pl("p3", "EBM Nights", 1500, "user2", "DJ Two", ["ebm"]),
    ]
    owners = aggregate_playlists_by_owner(playlists)

    assert len(owners) == 2
    u1 = owners["user1"]
    assert u1["playlist_count"] == 2
    assert u1["playlist_total_followers"] == 2800
    assert u1["top_playlist_followers"] == 2000
    assert u1["top_playlist_name"] == "Dark Disco"
    assert set(u1["playlist_genres"]) == {"dark disco", "acid"}


def test_aggregate_sorts_top_playlist_by_follower_count():
    playlists = [
        _pl("p1", "Small",  100, "user1", "DJ One", ["dark disco"]),
        _pl("p2", "Big",   5000, "user1", "DJ One", ["dark disco"]),
    ]
    owners = aggregate_playlists_by_owner(playlists)
    assert owners["user1"]["top_playlist_name"] == "Big"


def test_build_candidate_row_for_spotify():
    owner = {
        "owner_id": "user42",
        "owner_name": "Berlin Curator",
        "playlist_count": 3,
        "playlist_total_followers": 4200,
        "top_playlist_name": "Dark Disco 2026",
        "top_playlist_followers": 3000,
        "top_playlist_url": "https://open.spotify.com/playlist/xyz",
        "playlist_genres": ["dark disco", "acid"],
        "playlist_urls": ["https://open.spotify.com/playlist/xyz"],
        "discovered_via": ["search:dark disco"],
    }
    row = build_candidate_row(owner, platform="spotify")

    assert row["name"] == "Berlin Curator"
    assert row["category"] == "curator"
    assert row["sub_type"] == "spotify"
    assert row["source"] == "curator_discovery"
    assert row["spotify_id"] == "user42"
    assert row["spotify_url"] == "https://open.spotify.com/user/user42"
    assert row["match_score"] == "3"
    assert row["playlist_count"] == 3
    assert row["playlist_total_followers"] == 4200
    assert row["top_playlist_name"] == "Dark Disco 2026"
    assert row["playlist_genres"] == "dark disco, acid"


def test_build_candidate_row_for_soundcloud():
    owner = {
        "owner_id": "sc_user_99",
        "owner_name": "SC Curator",
        "owner_permalink_url": "https://soundcloud.com/sc-curator",
        "owner_followers": 1800,
        "playlist_count": 2,
        "playlist_total_followers": 600,
        "top_playlist_name": "Acid Set",
        "top_playlist_followers": 400,
        "top_playlist_url": "https://soundcloud.com/sc-curator/sets/acid-set",
        "playlist_genres": ["acid"],
        "playlist_urls": ["https://soundcloud.com/sc-curator/sets/acid-set"],
        "discovered_via": ["search:acid"],
    }
    row = build_candidate_row(owner, platform="soundcloud")

    assert row["sub_type"] == "soundcloud"
    assert row["soundcloud_user_id"] == "sc_user_99"
    assert row["soundcloud_url"] == "https://soundcloud.com/sc-curator"
    assert row["soundcloud_followers"] == "1800"


def test_filter_existing_drops_duplicates_by_name():
    candidates = [
        {"name": "Berlin Curator", "spotify_id": "new1"},
        {"name": "Someone Else", "spotify_id": "new2"},
    ]
    existing = {
        "names": {"berlincurator"},
        "spotify_ids": set(),
        "soundcloud_user_ids": set(),
    }
    fresh = filter_existing(candidates, existing)
    assert len(fresh) == 1
    assert fresh[0]["name"] == "Someone Else"


def test_filter_existing_drops_duplicates_by_platform_id():
    candidates = [
        {"name": "Unique Name A", "spotify_id": "taken_id"},
        {"name": "Unique Name B", "soundcloud_user_id": "taken_sc"},
    ]
    existing = {
        "names": set(),
        "spotify_ids": {"taken_id"},
        "soundcloud_user_ids": {"taken_sc"},
    }
    assert filter_existing(candidates, existing) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_discover_curators.py -v`
Expected: ModuleNotFoundError for `scene_intelligence.discover_curators`

- [ ] **Step 3: Write minimal implementation (logic only, no API yet)**

Create `scene_intelligence/discover_curators.py` with just the pure helpers:

```python
"""
scene_intelligence/discover_curators.py
----------------------------------------
Tool 1 -- Scene Intelligence Engine: Playlist Curator Discovery

Finds playlist curators on Spotify and SoundCloud who curate playlists
matching Inch of Shadow's genre keywords, and adds them to
enriched_contacts.json as category="curator".

Usage:
  python3 scene_intelligence/discover_curators.py                   # Both phases
  python3 scene_intelligence/discover_curators.py --spotify          # Phase 1 only
  python3 scene_intelligence/discover_curators.py --soundcloud       # Phase 2 only
  python3 scene_intelligence/discover_curators.py --dry-run          # Preview, don't save
  python3 scene_intelligence/discover_curators.py --limit 50         # Cap at N owners per platform
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key


# ---------------------------------------------------------------------------
# Pure-logic helpers (unit-tested)
# ---------------------------------------------------------------------------

def aggregate_playlists_by_owner(playlists: list[dict]) -> dict[str, dict]:
    """Group playlists by owner_id. Returns {owner_id: aggregate_info}.

    Each playlist dict must have: id, name, followers, owner_id, owner_name,
    matched_genres, url. Optional: owner_permalink_url, owner_followers.
    """
    owners: dict[str, dict] = {}
    for p in playlists:
        oid = p["owner_id"]
        if oid not in owners:
            owners[oid] = {
                "owner_id": oid,
                "owner_name": p["owner_name"],
                "owner_permalink_url": p.get("owner_permalink_url", ""),
                "owner_followers": p.get("owner_followers", 0),
                "playlists": [],
                "playlist_count": 0,
                "playlist_total_followers": 0,
                "top_playlist_name": "",
                "top_playlist_followers": 0,
                "top_playlist_url": "",
                "playlist_genres": set(),
                "playlist_urls": [],
                "discovered_via": set(),
            }
        o = owners[oid]
        o["playlists"].append(p)
        o["playlist_count"] += 1
        o["playlist_total_followers"] += p["followers"]
        o["playlist_urls"].append(p["url"])
        for g in p["matched_genres"]:
            o["playlist_genres"].add(g)
            o["discovered_via"].add(f"search:{g}")
        if p["followers"] > o["top_playlist_followers"]:
            o["top_playlist_followers"] = p["followers"]
            o["top_playlist_name"] = p["name"]
            o["top_playlist_url"] = p["url"]

    # Convert sets to sorted lists for deterministic output.
    for o in owners.values():
        o["playlist_genres"] = sorted(o["playlist_genres"])
        o["discovered_via"] = sorted(o["discovered_via"])
    return owners


def build_candidate_row(owner: dict, platform: str) -> dict:
    """Convert an aggregated owner dict into an enriched_contacts.json row."""
    row = {
        "name": owner["owner_name"],
        "category": "curator",
        "sub_type": platform,
        "source": "curator_discovery",
        "url": "",
        "genre_main": "Electronic",
        "genre_sub": " / ".join(owner["playlist_genres"]),
        "location": "",
        "match_score": "3",
        "playlist_count": owner["playlist_count"],
        "playlist_total_followers": owner["playlist_total_followers"],
        "top_playlist_name": owner["top_playlist_name"],
        "top_playlist_followers": owner["top_playlist_followers"],
        "top_playlist_url": owner["top_playlist_url"],
        "playlist_genres": ", ".join(owner["playlist_genres"]),
        "playlist_urls": " | ".join(owner["playlist_urls"]),
        "discovered_via": ",".join(owner["discovered_via"]),
    }
    if platform == "spotify":
        row["spotify_id"] = owner["owner_id"]
        row["spotify_url"] = f"https://open.spotify.com/user/{owner['owner_id']}"
        row["url"] = row["spotify_url"]
    elif platform == "soundcloud":
        row["soundcloud_user_id"] = owner["owner_id"]
        row["soundcloud_url"] = owner.get("owner_permalink_url", "")
        row["soundcloud_followers"] = str(owner.get("owner_followers", 0))
        row["url"] = row["soundcloud_url"]
    return row


def filter_existing(candidates: list[dict], existing: dict) -> list[dict]:
    """Drop candidates that already exist in the contacts file.

    existing is expected to have:
      names:                 set of dedup_key(name)
      spotify_ids:           set of spotify user ids
      soundcloud_user_ids:   set of soundcloud user ids (as strings)
    """
    fresh = []
    for c in candidates:
        if dedup_key(c["name"]) in existing["names"]:
            continue
        sid = c.get("spotify_id", "")
        if sid and sid in existing["spotify_ids"]:
            continue
        scid = str(c.get("soundcloud_user_id", "") or "")
        if scid and scid in existing["soundcloud_user_ids"]:
            continue
        fresh.append(c)
    return fresh
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_discover_curators.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scene_intelligence/discover_curators.py tests/test_discover_curators.py
git commit -m "feat(si): add curator aggregation and dedup helpers"
```

---

### Task 5: Add Spotify playlist search and playlist-detail fetch

**Files:**
- Modify: `scene_intelligence/discover_curators.py`

- [ ] **Step 1: Append Spotify API layer**

Append to `scene_intelligence/discover_curators.py`:

```python
# ---------------------------------------------------------------------------
# Spotify API layer (reuses client-credentials pattern from enrich_spotify.py)
# ---------------------------------------------------------------------------

import base64
import json
import os
import time

import requests
from dotenv import load_dotenv

BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

load_dotenv(BASE_DIR / ".env")
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SC_CLIENT_ID          = os.getenv("SOUNDCLOUD_CLIENT_ID", "")
SC_CLIENT_SECRET      = os.getenv("SOUNDCLOUD_CLIENT_SECRET", "")

SPOTIFY_TOKEN_URL  = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_PLAYLIST_URL = "https://api.spotify.com/v1/playlists/{id}"

SC_TOKEN_URL   = "https://secure.soundcloud.com/oauth/token"
SC_PLAYLISTS_URL = "https://api.soundcloud.com/playlists"

API_DELAY  = 1.0
TIMEOUT    = 10

_spotify_token: dict = {"access_token": "", "expires_at": 0.0}
_sc_token: dict      = {"access_token": "", "expires_at": 0.0}


def _spotify_auth() -> str:
    if _spotify_token["access_token"] and time.time() < _spotify_token["expires_at"]:
        return _spotify_token["access_token"]
    creds = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {creds}"},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        print(f"  [SPOTIFY AUTH] HTTP {r.status_code}: {r.text[:200]}")
        return ""
    data = r.json()
    _spotify_token["access_token"] = data["access_token"]
    _spotify_token["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return _spotify_token["access_token"]


def _spotify_get(url: str, params: dict | None = None) -> dict | None:
    token = _spotify_auth()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 5))
            print(f"  [RATE LIMIT] waiting {retry}s...")
            time.sleep(retry)
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            return r.json() if r.status_code == 200 else None
        if r.status_code in (401, 404):
            if r.status_code == 401:
                _spotify_token["access_token"] = ""
            return None
        print(f"  [HTTP {r.status_code}] {url}")
        return None
    except requests.RequestException as exc:
        print(f"  [request error] {exc}")
        return None


def search_spotify_playlists(keyword: str, limit: int = 50) -> list[dict]:
    """Search Spotify playlists for a keyword. Returns raw playlist summaries.

    Spotify /search returns up to 50 per call; we make one call per keyword.
    """
    data = _spotify_get(SPOTIFY_SEARCH_URL, params={
        "q": keyword,
        "type": "playlist",
        "limit": min(limit, 50),
    })
    time.sleep(API_DELAY)
    if not data:
        return []
    items = (data.get("playlists") or {}).get("items") or []
    return [p for p in items if p]


def fetch_spotify_playlist_detail(playlist_id: str) -> dict | None:
    """Fetch playlist detail including followers.total and owner info."""
    data = _spotify_get(
        SPOTIFY_PLAYLIST_URL.format(id=playlist_id),
        params={"fields": "id,name,description,followers.total,owner(id,display_name,external_urls)"},
    )
    time.sleep(API_DELAY)
    return data
```

- [ ] **Step 2: Smoke-test the auth and search**

Run: `python3 -c "from scene_intelligence.discover_curators import search_spotify_playlists; r = search_spotify_playlists('dark disco', 5); print(len(r), [p['name'] for p in r[:3]])"`
Expected: A non-zero count and three playlist names printed. If you see `0 []`, your Spotify credentials aren't loading — check `.env`.

- [ ] **Step 3: Commit**

```bash
git add scene_intelligence/discover_curators.py
git commit -m "feat(si): add Spotify playlist search + detail fetch for curator discovery"
```

---

### Task 6: Assemble the Spotify discovery phase

**Files:**
- Modify: `scene_intelligence/discover_curators.py`

- [ ] **Step 1: Append the Spotify phase function**

Append to `scene_intelligence/discover_curators.py`:

```python
# ---------------------------------------------------------------------------
# Phase 1: Spotify curator discovery
# ---------------------------------------------------------------------------

from curator_config import (  # type: ignore[import-not-found]
    GENRE_KEYWORDS,
    match_genres,
    is_editorial_owner,
    SPOTIFY_MIN_PLAYLIST_FOLLOWERS,
    SPOTIFY_MIN_OWNER_TOTAL,
)


def discover_spotify_curators(limit: int) -> list[dict]:
    """Run Spotify phase. Returns list of candidate rows (not yet deduped)."""
    print(f"  Phase 1: Spotify playlist search ({len(GENRE_KEYWORDS)} keywords)")
    all_playlists: dict[str, dict] = {}  # playlist_id -> normalized summary

    for i, keyword in enumerate(GENRE_KEYWORDS):
        print(f"    [{i+1:>2}/{len(GENRE_KEYWORDS)}] q={keyword!r:<22}", end="  ", flush=True)
        hits = search_spotify_playlists(keyword, limit=50)
        added = 0
        for p in hits:
            pid = p.get("id")
            if not pid or pid in all_playlists:
                continue
            owner = p.get("owner") or {}
            owner_id = owner.get("id", "")
            owner_name = owner.get("display_name", "") or owner_id
            if is_editorial_owner(owner_name, owner_id):
                continue
            # Genre filter against the playlist name + description
            matched = match_genres(p.get("name", ""), p.get("description", "") or "")
            if keyword not in matched:
                matched.append(keyword)
            all_playlists[pid] = {
                "id": pid,
                "name": p.get("name", ""),
                "description": p.get("description", "") or "",
                "owner_id": owner_id,
                "owner_name": owner_name,
                "matched_genres": matched,
                "url": (p.get("external_urls") or {}).get("spotify", f"https://open.spotify.com/playlist/{pid}"),
                "_needs_followers": True,
            }
            added += 1
        print(f"+{added} new playlists")

    print(f"  Playlists gathered: {len(all_playlists)}")

    # Fetch follower counts (search endpoint doesn't include them)
    print(f"  Fetching follower counts for {len(all_playlists)} playlists...")
    qualifying: list[dict] = []
    for i, (pid, summary) in enumerate(all_playlists.items()):
        detail = fetch_spotify_playlist_detail(pid)
        if not detail:
            continue
        followers = (detail.get("followers") or {}).get("total") or 0
        if followers < SPOTIFY_MIN_PLAYLIST_FOLLOWERS:
            continue
        summary["followers"] = followers
        summary.pop("_needs_followers", None)
        qualifying.append(summary)
        if (i + 1) % 25 == 0:
            print(f"    fetched {i+1}/{len(all_playlists)}, qualifying so far: {len(qualifying)}")

    print(f"  Qualifying playlists (>= {SPOTIFY_MIN_PLAYLIST_FOLLOWERS} followers): {len(qualifying)}")

    owners = aggregate_playlists_by_owner(qualifying)
    print(f"  Unique owners before filter: {len(owners)}")

    candidates: list[dict] = []
    for owner in owners.values():
        if owner["playlist_total_followers"] < SPOTIFY_MIN_OWNER_TOTAL:
            continue
        candidates.append(build_candidate_row(owner, platform="spotify"))

    candidates.sort(key=lambda c: -c["playlist_total_followers"])
    candidates = candidates[:limit]
    print(f"  Spotify candidates kept: {len(candidates)}")
    return candidates
```

- [ ] **Step 2: Smoke-test the phase with a small limit and no save**

Temporarily add this at module bottom for a one-off check (remove after):

```python
if __name__ == "__main__" and "--probe-spotify" in sys.argv:
    candidates = discover_spotify_curators(limit=5)
    for c in candidates:
        print(f"  - {c['name']:<30} {c['playlist_count']} pls, {c['playlist_total_followers']} followers")
```

Run: `python3 scene_intelligence/discover_curators.py --probe-spotify`
Expected: 1-5 curator rows printed. If 0, relax `SPOTIFY_MIN_PLAYLIST_FOLLOWERS` in `curator_config.py` temporarily to verify the pipeline runs.

Then remove the `--probe-spotify` block before committing.

- [ ] **Step 3: Commit**

```bash
git add scene_intelligence/discover_curators.py
git commit -m "feat(si): Spotify curator discovery phase"
```

---

### Task 7: Add SoundCloud playlist search and curator aggregation

**Files:**
- Modify: `scene_intelligence/discover_curators.py`

- [ ] **Step 1: Append SoundCloud API + phase**

Append to `scene_intelligence/discover_curators.py`:

```python
# ---------------------------------------------------------------------------
# SoundCloud API layer (reuses client-credentials pattern from enrich_soundcloud.py)
# ---------------------------------------------------------------------------

def _sc_auth() -> str:
    if _sc_token["access_token"] and time.time() < _sc_token["expires_at"]:
        return _sc_token["access_token"]
    creds = base64.b64encode(f"{SC_CLIENT_ID}:{SC_CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        SC_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {creds}"},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        print(f"  [SC AUTH] HTTP {r.status_code}: {r.text[:200]}")
        return ""
    data = r.json()
    _sc_token["access_token"] = data["access_token"]
    _sc_token["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return _sc_token["access_token"]


def _sc_get(url: str, params: dict | None = None) -> list | dict | None:
    token = _sc_auth()
    if not token:
        return None
    headers = {"Authorization": f"OAuth {token}"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [SC RATE LIMIT] sleeping 10s")
            time.sleep(10)
            return None
        if r.status_code in (401, 404):
            if r.status_code == 401:
                _sc_token["access_token"] = ""
            return None
        print(f"  [SC HTTP {r.status_code}] {url}")
        return None
    except requests.RequestException as exc:
        print(f"  [sc request error] {exc}")
        return None


def search_soundcloud_playlists(keyword: str, limit: int = 50) -> list[dict]:
    """Search SoundCloud playlists. Returns playlists with nested user info."""
    data = _sc_get(SC_PLAYLISTS_URL, params={"q": keyword, "limit": min(limit, 200)})
    time.sleep(API_DELAY)
    if not data:
        return []
    if isinstance(data, dict):
        data = data.get("collection") or []
    return [p for p in data if p]


# ---------------------------------------------------------------------------
# Phase 2: SoundCloud curator discovery
# ---------------------------------------------------------------------------

from curator_config import (  # type: ignore[import-not-found]
    SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS,
    SOUNDCLOUD_MIN_OWNER_TOTAL,
)


def discover_soundcloud_curators(limit: int) -> list[dict]:
    """Run SoundCloud phase. Returns list of candidate rows (not yet deduped)."""
    print(f"  Phase 2: SoundCloud playlist search ({len(GENRE_KEYWORDS)} keywords)")
    all_playlists: dict[str, dict] = {}

    for i, keyword in enumerate(GENRE_KEYWORDS):
        print(f"    [{i+1:>2}/{len(GENRE_KEYWORDS)}] q={keyword!r:<22}", end="  ", flush=True)
        hits = search_soundcloud_playlists(keyword, limit=50)
        added = 0
        for p in hits:
            pid = str(p.get("id") or "")
            if not pid or pid in all_playlists:
                continue
            user = p.get("user") or {}
            followers = int(p.get("likes_count") or 0) + int(p.get("reposts_count") or 0)
            if followers < SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS:
                continue
            matched = match_genres(p.get("title", "") or "", p.get("description", "") or "")
            if keyword not in matched:
                matched.append(keyword)
            all_playlists[pid] = {
                "id": pid,
                "name": p.get("title", ""),
                "description": p.get("description", "") or "",
                "followers": followers,
                "owner_id": str(user.get("id") or ""),
                "owner_name": user.get("username") or user.get("full_name") or "",
                "owner_permalink_url": user.get("permalink_url", ""),
                "owner_followers": int(user.get("followers_count") or 0),
                "matched_genres": matched,
                "url": p.get("permalink_url", ""),
            }
            added += 1
        print(f"+{added} new playlists")

    print(f"  Playlists qualifying: {len(all_playlists)}")

    owners = aggregate_playlists_by_owner(list(all_playlists.values()))
    print(f"  Unique owners before filter: {len(owners)}")

    candidates: list[dict] = []
    for owner in owners.values():
        if owner["playlist_total_followers"] < SOUNDCLOUD_MIN_OWNER_TOTAL:
            continue
        candidates.append(build_candidate_row(owner, platform="soundcloud"))

    candidates.sort(key=lambda c: -c["playlist_total_followers"])
    candidates = candidates[:limit]
    print(f"  SoundCloud candidates kept: {len(candidates)}")
    return candidates
```

**Note on SoundCloud "followers":** the SoundCloud public API does not expose a per-playlist follower count the same way Spotify does. We use `likes_count + reposts_count` as a proxy for playlist reach — high enough on either metric signals an active playlist that other users engage with. This is documented in the phase for future tuning.

- [ ] **Step 2: Smoke-test the phase**

Run a one-off probe similar to Spotify's:

```python
# Temporary probe at module bottom:
if __name__ == "__main__" and "--probe-soundcloud" in sys.argv:
    candidates = discover_soundcloud_curators(limit=5)
    for c in candidates:
        print(f"  - {c['name']:<30} {c['playlist_count']} pls, {c['playlist_total_followers']} signals")
```

Run: `python3 scene_intelligence/discover_curators.py --probe-soundcloud`
Expected: 1-5 curator rows printed. Remove the probe block before committing.

- [ ] **Step 3: Commit**

```bash
git add scene_intelligence/discover_curators.py
git commit -m "feat(si): SoundCloud curator discovery phase"
```

---

### Task 8: Wire up the main() CLI with dedup and save

**Files:**
- Modify: `scene_intelligence/discover_curators.py`

- [ ] **Step 1: Append main, load/save, backup, CLI parsing**

Append to `scene_intelligence/discover_curators.py`:

```python
# ---------------------------------------------------------------------------
# Data I/O + dedup + main
# ---------------------------------------------------------------------------

import argparse
import shutil
from datetime import datetime


def _load_contacts() -> list[dict]:
    with open(ENRICHED_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_contacts(contacts: list[dict]) -> None:
    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def _backup_contacts() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "scene_intelligence" / "backups" / f"contacts_{stamp}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENRICHED_FILE, dest)
    return dest


def _build_existing_keys(contacts: list[dict]) -> dict:
    return {
        "names":                {dedup_key(c.get("name", "")) for c in contacts if c.get("name")},
        "spotify_ids":          {c["spotify_id"] for c in contacts if c.get("spotify_id")},
        "soundcloud_user_ids":  {str(c["soundcloud_user_id"]) for c in contacts if c.get("soundcloud_user_id")},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spotify",    action="store_true", help="Run Spotify phase only")
    parser.add_argument("--soundcloud", action="store_true", help="Run SoundCloud phase only")
    parser.add_argument("--dry-run",    action="store_true", help="Preview, do not save")
    parser.add_argument("--limit", type=int, default=100, help="Max candidates per platform")
    args = parser.parse_args()

    both = not args.spotify and not args.soundcloud

    contacts = _load_contacts()
    existing = _build_existing_keys(contacts)
    print(f"Loaded {len(contacts)} existing contacts.\n")

    all_candidates: list[dict] = []
    if args.spotify or both:
        all_candidates.extend(discover_spotify_curators(args.limit))
        print()
    if args.soundcloud or both:
        all_candidates.extend(discover_soundcloud_curators(args.limit))
        print()

    fresh = filter_existing(all_candidates, existing)
    dropped = len(all_candidates) - len(fresh)
    print(f"Candidates: {len(all_candidates)} total, {dropped} already known, {len(fresh)} new.\n")

    if args.dry_run:
        print("DRY RUN -- top 10 fresh candidates:")
        for c in fresh[:10]:
            print(f"  [{c['sub_type']:<10}] {c['name']:<30} {c['playlist_count']:>2} pl  "
                  f"{c['playlist_total_followers']:>7} followers  "
                  f"top: {c['top_playlist_name'][:35]}")
        return 0

    if fresh:
        backup = _backup_contacts()
        print(f"Backup: {backup}")
        contacts.extend(fresh)
        _save_contacts(contacts)
        print(f"Added {len(fresh)} curators. Total contacts: {len(contacts)}.")
    else:
        print("No new curators to add.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run unit tests to confirm nothing broke**

Run: `pytest tests/ -v`
Expected: all tests pass

- [ ] **Step 3: Dry-run end-to-end**

Run: `python3 scene_intelligence/discover_curators.py --dry-run --limit 10`
Expected: output shows counts per phase and a preview of top 10 new candidates. No change to `enriched_contacts.json`.

Confirm the preview rows look reasonable (real curator names, matching genres). If they look bad, tune `curator_config.py` thresholds or GENRE_KEYWORDS.

- [ ] **Step 4: Commit**

```bash
git add scene_intelligence/discover_curators.py
git commit -m "feat(si): discover_curators CLI with dry-run, backup, and save"
```

---

### Task 9: Add Curators tab to push_to_sheets.py

**Files:**
- Modify: `scene_intelligence/push_to_sheets.py`

- [ ] **Step 1: Locate the tabs list and _SYNC_TABS**

Read `scene_intelligence/push_to_sheets.py` around line 885 (`_SYNC_TABS`) and line 1052 (tabs list). Hold both in context for the edits below.

- [ ] **Step 2: Add "Curators" to _SYNC_TABS**

Change:

```python
_SYNC_TABS = ["Labels", "DJs", "Venues", "Media", "Promoters", "Distributors", "Platforms", "All Contacts"]
```

To:

```python
_SYNC_TABS = ["Labels", "DJs", "Venues", "Media", "Promoters", "Distributors", "Platforms", "Curators", "All Contacts"]
```

- [ ] **Step 3: Add "Curators" to the tabs list in the push routine**

In the `tabs = [...]` block (around line 1052), insert a Curators entry before "All Contacts":

```python
tabs = [
    ("A&R Targets",  None),
    ("Labels",       lambda r: r.get("category") == "label"),
    ("DJs",          lambda r: r.get("category") in ("dj", "artist", "personal")),
    ("Venues",       lambda r: r.get("category") == "venue"),
    ("Media",        lambda r: r.get("category") == "media"),
    ("Promoters",    lambda r: r.get("category") == "promoter"),
    ("Distributors", lambda r: r.get("category") == "distributor"),
    ("Platforms",    lambda r: r.get("category") == "platform"),
    ("Curators",     lambda r: r.get("category") == "curator"),
    ("All Contacts", lambda r: True),
]
```

- [ ] **Step 4: Verify the tab gets the standard HEADERS config**

Search for `_TAB_CONFIG` in the file. If "Curators" has no entry, it falls through to the standard headers — that is correct for first shipping. No code change needed. (If a later pass wants curator-specific columns like `top_playlist_name`, that's a follow-up.)

Run:

```bash
python3 -c "from scene_intelligence import push_to_sheets as p; print('Curators' in p._SYNC_TABS)"
```

Expected: `True`

- [ ] **Step 5: Smoke-test (no sync, so it's safe)**

Run: `python3 scene_intelligence/push_to_sheets.py --no-sync`
Expected: output includes a `Curators  N rows` line. If there are no curators yet (discovery hasn't run), N = 0 is correct.

- [ ] **Step 6: Commit**

```bash
git add scene_intelligence/push_to_sheets.py
git commit -m "feat(si): Curators tab in Google Sheets push"
```

---

### Task 10: Add curator button to Promotion Engine category filter

**Files:**
- Modify: `release_manager/templates/promotion.html`
- Modify: `release_manager/static/style.css` (add a badge colour for curator)

The Promotion Engine category filter is a row of button pills in `release_manager/templates/promotion.html` lines ~121-128, inside `<div class="promo-cat-filters">`. Each button has a `data-cat` attribute that the page's JS uses to filter the contact list client-side. Category badges on each contact row use a `badge-<category>` class for colour.

- [ ] **Step 1: Add the Curator button pill**

Edit `release_manager/templates/promotion.html`. Change:

```html
<div class="promo-cat-filters">
    <button class="promo-cat-btn active" data-cat="all">All</button>
    <button class="promo-cat-btn" data-cat="media">Media</button>
    <button class="promo-cat-btn" data-cat="label">Labels</button>
    <button class="promo-cat-btn" data-cat="dj">DJs</button>
    <button class="promo-cat-btn" data-cat="promoter">Promos</button>
    <button class="promo-cat-btn" data-cat="venue">Venues</button>
</div>
```

To (add Curators button after Venues):

```html
<div class="promo-cat-filters">
    <button class="promo-cat-btn active" data-cat="all">All</button>
    <button class="promo-cat-btn" data-cat="media">Media</button>
    <button class="promo-cat-btn" data-cat="label">Labels</button>
    <button class="promo-cat-btn" data-cat="dj">DJs</button>
    <button class="promo-cat-btn" data-cat="promoter">Promos</button>
    <button class="promo-cat-btn" data-cat="venue">Venues</button>
    <button class="promo-cat-btn" data-cat="curator">Curators</button>
</div>
```

- [ ] **Step 2: Confirm the filter JS handles arbitrary data-cat values**

The filter JS lives in `release_manager/static/app.js`. Grep to confirm it compares `data-cat` on the button against the `data-cat` attribute set on each contact row (line ~180 in the template: `data-cat="{{ c.category }}"`):

```bash
grep -n "data-cat\|promo-cat-btn" release_manager/static/app.js | head
```

The filter should be category-agnostic (a direct string match). If it is, no JS change is needed. If it has a hardcoded list of categories, extend that list to include `"curator"`.

- [ ] **Step 3: Add a curator badge colour to style.css**

Badges on contact rows use class `badge-<category>` (see promotion.html line 190). Grep existing badge styles:

```bash
grep -n "badge-dj\|badge-label\|badge-media" release_manager/static/style.css
```

Below the last `badge-<existing>` rule, add:

```css
.badge-curator {
    background: #6a4c93;
    color: #fff;
}
```

(Purple distinguishes curators from existing categories. Tweak to taste.)

- [ ] **Step 4: Start the Flask app and click through**

Run: `python3 -m release_manager.webapp`
Navigate to `http://localhost:5001/promotion` and select a release. Click the Curators button; the contact list should show only curator rows (empty if discovery hasn't been run yet — that's fine). Confirm the Curator badge renders with the new colour.

Stop the server with Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add release_manager/templates/promotion.html release_manager/static/style.css
git commit -m "feat(rm): add Curator pill and badge to Promotion Engine"
```

---

### Task 11: Run real discovery and push to Sheets

**Files:** none (operational task)

- [ ] **Step 1: Dry-run once more**

Run: `python3 scene_intelligence/discover_curators.py --dry-run --limit 50`
Expected: ~20-80 fresh candidates. Spot-check 5 names — search them on Spotify/SoundCloud and confirm they are real human curators in your genre space.

If too many junk results appear (K-pop playlists, generic "chill" lists, etc.), either:
- Tighten `SPOTIFY_MIN_PLAYLIST_FOLLOWERS` in `curator_config.py` (e.g., 500 -> 1000)
- Drop generic keywords like `"techno"` alone; keep only multi-word variants

Re-run the dry-run until the preview is mostly-good.

- [ ] **Step 2: Save for real**

Run: `python3 scene_intelligence/discover_curators.py --limit 50`
Expected: backup file written under `scene_intelligence/backups/`; new contacts appended; "Total contacts" goes up.

- [ ] **Step 3: Push to Sheets**

Run: `python3 scene_intelligence/push_to_sheets.py`
Expected: output includes `Curators  N rows` with the count you just added. Open the Google Sheet and confirm the Curators tab populated.

- [ ] **Step 4: Inspect one row in the Sheet**

Scroll through the Curators tab. Verify: `name`, `sub_type` (spotify or soundcloud), `url`, `genre_sub`, and `match_score` (3) all look right.

- [ ] **Step 5: Commit any ad-hoc tuning made to curator_config.py**

If you adjusted thresholds or keywords in step 1:

```bash
git add scene_intelligence/curator_config.py
git commit -m "tune(si): curator discovery thresholds after first real run"
```

---

### Task 12: Document the new command in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find the "Key commands" or equivalent section**

The CLAUDE.md in the repo root has a tools section. The user's auto-memory references key commands for SI (`discover_contacts.py`, `classify_subtypes.py`, etc.). Add `discover_curators.py` alongside them.

- [ ] **Step 2: Add the line**

If there's a bulleted commands list, insert:

```markdown
- `python3 scene_intelligence/discover_curators.py --dry-run` -- preview curators before saving
- `python3 scene_intelligence/discover_curators.py` -- run Spotify + SoundCloud curator discovery
```

If CLAUDE.md does not have a commands list, just add a one-line mention under the Scene Intelligence tool description.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document discover_curators command"
```

---

## Verification Checklist

After all tasks:

- [ ] `pytest tests/ -v` passes (14 tests total: 8 in test_curator_config + 6 in test_discover_curators)
- [ ] `python3 scene_intelligence/discover_curators.py --dry-run` runs end-to-end and prints sensible candidates
- [ ] `enriched_contacts.json` contains curator rows with `category: "curator"`, `sub_type: "spotify" | "soundcloud"`
- [ ] Google Sheets has a Curators tab populated with the expected count
- [ ] Promotion Engine filter dropdown shows "Curator" and filters correctly
- [ ] `scene_intelligence/backups/` contains a backup from the first real run
- [ ] CLAUDE.md documents the new command

## Open Questions for Later

These are explicitly out of scope for this plan and left for future iterations:

1. **Curator contact info extraction.** Spotify doesn't expose user bios via the public API for regular users. A follow-up could scrape profile pages for bio links (IG, Twitter, email) to make curators actionable for outreach.
2. **Curator-specific Sheet columns.** For now the Curators tab uses the standard `HEADERS`. A dedicated column layout (top_playlist_name, playlist_count, playlist_total_followers) would make the tab more useful — add to `_TAB_CONFIG` in a follow-up.
3. **Periodic refresh.** Playlists and followers change. A quarterly re-run is fine manually; auto-refresh would live in a separate scheduler task.
4. **Dedup against existing contacts by Spotify/SC URL.** Current dedup is by name and by platform user id. If an existing DJ already has a `spotify_id` they'll be matched. But a curator who is also already in SI under a different name (e.g., a label's Spotify account) won't auto-merge.
