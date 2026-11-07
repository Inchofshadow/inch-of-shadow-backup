"""
release_manager/storage.py
----------------------------
JSON file I/O for release files in the releases/ directory.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from release_manager.paths import repo_root

BASE_DIR     = repo_root()   # canonical main repo root (robust to git worktrees)
RELEASES_DIR = BASE_DIR / "releases"


def ensure_releases_dir() -> Path:
    """Create releases/ if it doesn't exist. Returns the path."""
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    return RELEASES_DIR


def release_path(slug: str) -> Path:
    """Return the full path for a release JSON file."""
    return RELEASES_DIR / f"{slug}.json"


def release_exists(slug: str) -> bool:
    """Check if a release JSON file exists."""
    return release_path(slug).exists()


def iter_release_paths() -> list[Path]:
    """Real release files only. Stats-capture backups live in releases/ and
    some end in .json (e.g. farewell-single.bak.20260724_180207_sc_stats.json),
    so a bare *.json glob renders each backup as a release card (2026-07-28:
    homepage showed Farewell 4x, The Deceiver 6x). Same filter as
    scene_intelligence/release_weekly_health.py::iter_release_paths."""
    return [p for p in sorted(RELEASES_DIR.glob("*.json")) if ".bak" not in p.name]


def _migrate_distribution(data: dict) -> None:
    """Migrate old distribution fields to new schema in-place."""
    dist = data.get("distribution", {})
    # Migrate old boolean 'submitted' to 'status' string
    if "submitted" in dist and "status" not in dist:
        dist["status"] = "submitted" if dist.pop("submitted") else "draft"
    elif "submitted" in dist:
        dist.pop("submitted", None)
    # Ensure new fields exist
    dist.setdefault("status", "draft")
    dist.setdefault("distributor_id", "")
    dist.setdefault("approved_date", "")


def load_release(slug: str) -> dict | None:
    """Load a release JSON file by slug. Returns None if not found."""
    path = release_path(slug)
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"warning: release {slug!r} unreadable, skipping: {e}", file=sys.stderr)
        return None
    _migrate_distribution(data)
    return data


def save_release(data: dict) -> Path:
    """Save a release dict to its JSON file. Updates 'updated_at'. Returns path.

    Runs reconcile_release() first so redundant fields (checklist vs.
    distribution block vs. timeline) stay in sync on every write.
    """
    # Local import to avoid circular dependency (reconcile imports from checklist,
    # which is unrelated to storage, but keeps storage.py import-clean).
    from release_manager.reconcile import reconcile_release
    reconcile_release(data)

    ensure_releases_dir()
    data["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    path = release_path(data["slug"])
    # Atomic write (audit P2-10): a crash mid-dump must not leave a
    # half-written release JSON behind.
    from scene_intelligence.json_io import atomic_write_json
    atomic_write_json(path, data)
    return path


def list_releases() -> list[dict]:
    """Load all release JSON files, return sorted by release_date."""
    ensure_releases_dir()
    releases = []
    for path in iter_release_paths():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"warning: release file {path.name} unreadable, skipping: {e}", file=sys.stderr)
            continue
        _migrate_distribution(data)
        releases.append(data)
    releases.sort(key=lambda r: r.get("release_date", ""))
    return releases


def find_release(slug_or_partial: str) -> dict | None:
    """Find a release by exact slug or unique partial match.

    Returns the release dict if exactly one match, None if zero or ambiguous.
    Prints candidates when ambiguous.
    """
    # Exact match first
    exact = load_release(slug_or_partial)
    if exact:
        return exact

    # Partial match
    ensure_releases_dir()
    candidates = []
    for path in iter_release_paths():
        if slug_or_partial in path.stem:
            with open(path, encoding="utf-8") as f:
                candidates.append(json.load(f))

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        print(f"  Ambiguous slug '{slug_or_partial}'. Did you mean:")
        for c in candidates:
            print(f"    - {c['slug']}")
        return None
    return None


def delete_release(slug: str) -> bool:
    """Delete a release JSON file by slug. Returns True if deleted."""
    path = release_path(slug)
    if path.exists():
        path.unlink()
        return True
    return False


def unique_slug(slug: str) -> str:
    """If slug already exists, append -2, -3, etc."""
    if not release_exists(slug):
        return slug
    n = 2
    while release_exists(f"{slug}-{n}"):
        n += 1
    return f"{slug}-{n}"
