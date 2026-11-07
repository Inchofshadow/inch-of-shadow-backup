#!/usr/bin/env python3
"""
Description Scorer for Inch of Shadow.

Scores a platform bio or description BEFORE you post it, against the things that
actually matter for an artist (not B2B blog SEO). Recalibrated from the AD Labs
control-panel quality checker: dropped FAQ / internal-link / keyword-density
checks; added char-limit fit, front-loading, genre and location presence, and
Amir's voice rules.

Checks:
  - Fits the platform character limit (and is not wastefully short)
  - Has substance (not empty)
  - Mentions a core genre (discoverability)
  - Mentions Berlin (scene SEO)
  - Front-loads identity in the visible window (platforms truncate)
  - Voice: no double dashes, no emojis (unless allowed), no clickbait
  - Never mentions banned terms (Software Zero)
  - Sentences are not absurd run-ons

Usage:
  python3 description_scorer.py spotify_bio --text "..."
  python3 description_scorer.py bandcamp_artist_bio --file bio.txt
  python3 description_scorer.py soundcloud_profile_description --from-profile soundcloud
  python3 description_scorer.py --list

Char limits are read from release_manager/seo_platform_specs.json when available.
"""

from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPECS_FILE = ROOT / "release_manager" / "seo_platform_specs.json"
PROFILE_FILE = ROOT / "artist_profile.json"

PASS_SCORE = 80

# Core genres for Inch of Shadow (discoverability). From the brand + specs.
CORE_GENRES = [
    "dark disco", "acid", "electro", "ebm", "techno", "downtempo",
    "coldwave", "post punk", "disco", "industrial",
]

# Banned hard terms: never appear in public copy.
BANNED_TERMS = ["software zero"]

# Clickbait / hype phrasings that break the artist voice.
CLICKBAIT = [
    "wait for this", "you won't believe", "you wont believe", "pov:",
    "don't miss", "dont miss", "out now go stream", "smash that",
    "link in bio now", "drop everything", "must listen", "game changer",
    "game-changer", "insane", "this is fire",
]

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF←-⇿⬀-⯿]"
)

# Fallback limits if the specs file is unreadable. Field name -> max chars.
FALLBACK_LIMITS = {
    "spotify_bio": 1500,
    "spotify_pitch": 500,
    "spotify_artist_pick": 140,
    "bandcamp_artist_bio": 400,
    "soundcloud_profile_description": 4000,
    "soundcloud_track_description": 4000,
    "youtube_channel_description": 1000,
    "youtube_description": 5000,
    "instagram_bio": 150,
    "instagram_caption": 2200,
}

# How many leading chars are visible before a platform truncates.
VISIBLE_WINDOW = {
    "instagram_bio": 150,
    "instagram_caption": 125,
    "spotify_bio": 200,
    "youtube_channel_description": 150,
    "soundcloud_profile_description": 200,
    "bandcamp_artist_bio": 400,
}


def load_limits() -> dict:
    """Field -> max-chars, parsed from the specs quick reference if possible."""
    limits = dict(FALLBACK_LIMITS)
    try:
        specs = json.loads(SPECS_FILE.read_text(encoding="utf-8"))
        qr = specs.get("cross_platform_summary", {}).get(
            "character_limits_quick_reference", {}
        )
        for key, val in qr.items():
            m = re.search(r"\d+", str(val))
            if m:
                limits[key] = int(m.group())
    except (OSError, ValueError):
        pass
    return limits


def _check(name, passed, score, message, weight):
    return {"name": name, "passed": passed, "score": score, "message": message, "weight": weight}


def score_text(field: str, text: str, allow_emoji: bool = False) -> dict:
    limits = load_limits()
    limit = limits.get(field)
    visible = VISIBLE_WINDOW.get(field, 120)
    text = text or ""
    lower = text.lower()
    length = len(text)
    checks = []

    # 1. Char limit fit
    if limit:
        if length > limit:
            checks.append(_check("char_limit", False, 0,
                f"Over limit: {length}/{limit} chars (will be truncated)", 5))
        elif length < limit * 0.4 and length > 0:
            checks.append(_check("char_limit", True, 75,
                f"Short: {length}/{limit} chars (room to say more)", 5))
        else:
            checks.append(_check("char_limit", True, 100,
                f"Length good: {length}/{limit} chars", 5))
    else:
        checks.append(_check("char_limit", True, 100,
            f"Length: {length} chars (no documented limit)", 3))

    # 2. Substance
    if length == 0:
        checks.append(_check("substance", False, 0, "Empty", 5))
    elif length < 20:
        checks.append(_check("substance", False, 40, f"Very thin ({length} chars)", 5))
    else:
        checks.append(_check("substance", True, 100, "Has substance", 5))

    # 3. Genre present
    genres_found = [g for g in CORE_GENRES if g in lower]
    if genres_found:
        checks.append(_check("genre", True, 100,
            f"Genre present: {', '.join(genres_found[:3])}", 4))
    else:
        checks.append(_check("genre", False, 50,
            "No core genre mentioned (hurts discoverability)", 4))

    # 4. Location present
    if "berlin" in lower:
        checks.append(_check("location", True, 100, "Berlin mentioned", 3))
    else:
        checks.append(_check("location", False, 60,
            "Berlin not mentioned (scene SEO)", 3))

    # 5. Front-loaded identity
    head = lower[:visible]
    if any(g in head for g in CORE_GENRES) or "berlin" in head or "inch of shadow" in head:
        checks.append(_check("front_loaded", True, 100,
            f"Identity front-loaded (first {visible} chars)", 4))
    else:
        checks.append(_check("front_loaded", False, 55,
            f"First {visible} visible chars miss genre/location/name", 4))

    # 6. No double dashes (hard voice rule)
    if "--" in text or "—" in text or "–" in text:
        checks.append(_check("no_double_dash", False, 0,
            "Contains a double/em/en dash (use single dash with spaces)", 4))
    else:
        checks.append(_check("no_double_dash", True, 100, "No double dashes", 4))

    # 7. No emojis
    emojis = EMOJI_RE.findall(text)
    if emojis and not allow_emoji:
        checks.append(_check("no_emoji", False, 40,
            f"Contains emoji ({len(emojis)}); not the artist voice", 2))
    else:
        checks.append(_check("no_emoji", True, 100, "No emojis", 2))

    # 8. No clickbait
    hits = [p for p in CLICKBAIT if p in lower]
    if hits:
        checks.append(_check("no_clickbait", False, 30,
            f"Clickbait phrasing: {', '.join(hits[:3])}", 3))
    else:
        checks.append(_check("no_clickbait", True, 100, "No clickbait phrasing", 3))

    # 9. Banned terms (hard)
    banned_hits = [b for b in BANNED_TERMS if b in lower]
    if banned_hits:
        checks.append(_check("banned_terms", False, 0,
            f"BANNED term present: {', '.join(banned_hits)}", 5))
    else:
        checks.append(_check("banned_terms", True, 100, "No banned terms", 5))

    # 10. Sentence sanity
    sentences = [s for s in re.split(r"[.!?\n]+", text) if s.strip()]
    longest = max((len(s.split()) for s in sentences), default=0)
    if longest > 45:
        checks.append(_check("sentence_sanity", False, 60,
            f"A sentence runs {longest} words (consider breaking it up)", 2))
    else:
        checks.append(_check("sentence_sanity", True, 100, "Sentence length fine", 2))

    total_w = sum(c["weight"] for c in checks)
    overall = round(sum(c["score"] * c["weight"] for c in checks) / total_w)
    return {
        "field": field,
        "length": length,
        "limit": limit,
        "overall": overall,
        "passed": overall >= PASS_SCORE and all(
            c["passed"] for c in checks if c["name"] in ("char_limit", "banned_terms")
        ),
        "checks": checks,
    }


def print_report(result: dict) -> None:
    status = "PASS" if result["passed"] else "FAIL"
    print(f"\n{result['field']}  ->  {result['overall']}/100  [{status}]")
    print(f"  length: {result['length']}" + (f" / {result['limit']}" if result["limit"] else ""))
    fails = [c for c in result["checks"] if not c["passed"]]
    if fails:
        print("\n  Issues (highest weight first):")
        for c in sorted(fails, key=lambda x: -x["weight"]):
            print(f"   [{c['weight']}] {c['name']}: {c['message']}")
    else:
        print("  All checks passed.")
    print()


def get_profile_bio(platform: str) -> str:
    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    bios = data.get("bios", {})
    entry = bios.get(platform)
    if not entry:
        sys.exit(f"No bio for '{platform}' in artist_profile.json. Available: "
                 + ", ".join(bios.keys()))
    return entry.get("current", "") or ""


def parse_args():
    parser = ArgumentParser(description="Score an Inch of Shadow platform description.")
    parser.add_argument("field", nargs="?", help="Field name, e.g. spotify_bio (see --list).")
    parser.add_argument("--text", help="The text to score.")
    parser.add_argument("--file", type=Path, help="Read the text from a file.")
    parser.add_argument("--from-profile", metavar="PLATFORM",
                        help="Pull the current bio from artist_profile.json (e.g. soundcloud).")
    parser.add_argument("--allow-emoji", action="store_true", help="Do not penalize emojis.")
    parser.add_argument("--list", action="store_true", help="List known fields and limits.")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print("Known fields and char limits:")
        for k, v in sorted(load_limits().items()):
            print(f"  {k}: {v}")
        return

    if not args.field:
        sys.exit("Provide a field (e.g. spotify_bio). Use --list to see options.")

    if args.text is not None:
        text = args.text
    elif args.file:
        text = args.file.read_text(encoding="utf-8")
    elif args.from_profile:
        text = get_profile_bio(args.from_profile)
    else:
        sys.exit("Provide the text via --text, --file, or --from-profile.")

    result = score_text(args.field, text, allow_emoji=args.allow_emoji)
    print_report(result)


if __name__ == "__main__":
    main()
