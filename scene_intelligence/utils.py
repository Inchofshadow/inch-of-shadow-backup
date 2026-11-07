"""
scene_intelligence/utils.py
----------------------------
Shared utilities for the Scene Intelligence pipeline.
Extracted to avoid duplication across extract, enrich, and push scripts.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Deduplication key
# ---------------------------------------------------------------------------

def dedup_key(name: str) -> str:
    """Normalize name to lowercase alphanumeric for deduplication."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


# ---------------------------------------------------------------------------
# Category-based fallback scores
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Normalize raw contacts
# ---------------------------------------------------------------------------

# Bucket processing order (multi_source first so cross-source entries win)
_SOURCE_BUCKETS: list[tuple[str, str]] = [
    ("multi_source",      "multi"),
    ("youtube",           "youtube"),
    ("instagram",         "instagram"),
    ("soundcloud",        "soundcloud"),
    ("resident_advisor",  "resident_advisor"),
    ("chatgpt_labels",    "chatgpt"),
]


def normalize_raw_contacts(
    raw: dict,
    extra_fields: dict[str, str] | None = None,
) -> list[dict]:
    """Flatten bucketed raw_contacts.json into a deduplicated list.

    Parameters
    ----------
    raw : dict
        The raw contacts dict keyed by source bucket.
    extra_fields : dict, optional
        Additional fields (with default values) to append to every row.
        Used by push_to_sheets to add ``{"discogs_url": ""}``.
    """
    seen: set[str] = set()
    rows: list[dict] = []

    def _add(entry: dict, fallback_source: str) -> None:
        name = (entry.get("name") or entry.get("username") or "").strip()
        if not name:
            return
        key = dedup_key(name)
        if not key or key in seen:
            return
        seen.add(key)
        row = {
            "name":        name,
            "category":    entry.get("category") or entry.get("type") or "other",
            "sub_type":    entry.get("sub_type", ""),
            "source":      entry.get("source", fallback_source),
            "url":         entry.get("url", ""),
            "genre_main":  entry.get("genre_main", ""),
            "genre_sub":   entry.get("genre_sub", ""),
            "location":    entry.get("location", ""),
            "match_score": entry.get("match_score", ""),
        }
        if extra_fields:
            for k, v in extra_fields.items():
                row.setdefault(k, v)
        rows.append(row)

    for bucket_key, fallback in _SOURCE_BUCKETS:
        for entry in raw.get(bucket_key, []):
            _add(entry, fallback)

    return rows
