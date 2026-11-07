"""
scene_intelligence/ig_import_manual_2026-06-03.py
-------------------------------------------------
One-off importer for the manually-followed IG accounts Amir hand-picked from
the 2026-06-01 export review (ig_manual_import_review_2026-06-03.md).

Safe by design:
  - Backs up enriched_contacts.json (timestamped) before writing.
  - Append-only: dedups against existing contacts by dedup_key, never edits
    or deletes any existing row.
  - Only the explicitly-selected accounts below are added.

Excluded on purpose:
  - disco.suicide  -> Amir will verify category later (held).
  - All 38 automation follows, 10 already-in-SI, and the rest of the 76.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key, CATEGORY_DEFAULT_SCORE
from extract_contacts import infer_genre, infer_location, genre_match_score

BASE = Path(__file__).parent.parent
ENRICHED = BASE / "scene_intelligence" / "enriched_contacts.json"

ADDED_DATE = "2026-06-03"
SOURCE = "instagram_manual"

# handle, category, notes, extra-fields
SELECTIONS = [
    ("__dopplereffekt__", "dj", "Dopplereffekt - electro act. Manually followed.", {}),
    ("ben.buecken", "dj", "Manually followed.", {}),
    ("daribone", "dj",
     "Member / label boss of Mechatronica (Berlin electro label; in SI as "
     "'mechatronicamusic'). In touch via SoundCloud during the 2026 SC campaign "
     "- loves the track.",
     {"label_connections": "Mechatronica"}),
    ("ilayddab", "dj", "In touch - sent her Farewell, she liked it (2026).", {}),
    ("transgression_music", "dj", "Manually followed.", {}),
    ("blankwave.wav", "media",
     "In touch via DM - will send a DJ set (2026-06).", {}),
    ("afterhoursounds", "media",
     "Manually followed. Not yet contacted - needs outreach.",
     {"outreach_status": "not_contacted"}),
]


def build_contact(handle: str, category: str, notes: str, extra: dict) -> dict:
    gm, gs = infer_genre(handle)
    score = genre_match_score(gm, gs) or CATEGORY_DEFAULT_SCORE.get(category, "1")
    contact = {
        "name": handle,
        "category": category,
        "source": SOURCE,
        "url": f"https://www.instagram.com/_u/{handle}",
        "genre_main": gm,
        "genre_sub": gs,
        "location": infer_location(handle),
        "match_score": score,
        "discogs_url": "",
        "discogs_genres": "",
        "discogs_country": "",
        "discogs_email": "",
        "discogs_releases": "",
        "discogs_last_year": "",
        "discogs_website": "",
        "discogs_labels": "",
        "discogs_found": False,
        "discogs_match_confidence": "",
        "verification_status": "?",
        "ig_username": handle,
        "ig_followed_manually": True,
        "added_at": ADDED_DATE,
        "added_via": "ig_manual_review_2026-06-03",
        "notes": notes,
    }
    contact.update(extra)
    return contact


def main() -> None:
    with open(ENRICHED, encoding="utf-8") as f:
        contacts = json.load(f)

    existing = {dedup_key(c.get("name", "")) for c in contacts if c.get("name")}

    # --- backup BEFORE writing ---
    backup = ENRICHED.parent / f"enriched_contacts.bak.{ADDED_DATE.replace('-', '')}_pre_ig_manual_import.json"
    with open(backup, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    added, skipped = [], []
    for handle, category, notes, extra in SELECTIONS:
        if dedup_key(handle) in existing:
            skipped.append(handle)
            continue
        contacts.append(build_contact(handle, category, notes, extra))
        existing.add(dedup_key(handle))
        added.append((handle, category))

    with open(ENRICHED, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"Backup written: {backup.name}")
    print(f"Contacts before: {len(contacts) - len(added)}  ->  after: {len(contacts)}")
    print(f"\nAdded ({len(added)}):")
    for h, c in added:
        print(f"   + {h:<22} [{c}]")
    if skipped:
        print(f"\nSkipped (already in SI) ({len(skipped)}): {', '.join(skipped)}")
    print("\nHeld (not imported): disco.suicide  (Amir to verify category later)")


if __name__ == "__main__":
    main()
