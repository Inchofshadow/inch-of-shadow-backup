"""
scene_intelligence/update_scores.py
-------------------------------------
One-shot patch: applies category-based default match_scores to any
contact in enriched_contacts.json that currently has an empty score.

Run once after enrich_contacts.py:
  python3 scene_intelligence/update_scores.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import CATEGORY_DEFAULT_SCORE

BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"


def main() -> None:
    print("\nScene Intelligence — Score Patcher")
    print("=" * 42)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found. Run enrich_contacts.py first.")
        return

    with open(ENRICHED_FILE, encoding="utf-8") as f:
        contacts: list[dict] = json.load(f)

    print(f"  Loaded {len(contacts)} contacts")

    patched: dict[str, int] = {}
    already_scored = 0

    for contact in contacts:
        if contact.get("match_score") != "":
            already_scored += 1
            continue
        cat     = contact.get("category", "other")
        default = CATEGORY_DEFAULT_SCORE.get(cat, "1")
        contact["match_score"] = default
        patched[cat] = patched.get(cat, 0) + 1

    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"\n  Scores added: {sum(patched.values())}")
    for cat in ("distributor", "platform", "venue", "label", "dj", "media", "other"):
        if cat in patched:
            print(f"    {cat:<12} {patched[cat]:>4}  → score {CATEGORY_DEFAULT_SCORE[cat]}")
    print(f"\n  Already scored (unchanged): {already_scored}")
    print(f"  Saved to: scene_intelligence/enriched_contacts.json\n")


if __name__ == "__main__":
    main()
