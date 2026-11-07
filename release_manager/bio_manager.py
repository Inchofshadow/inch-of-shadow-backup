"""
release_manager/bio_manager.py
-------------------------------
Artist profile I/O and bio generation via Claude API.

Uses claude-opus-5-5 for bio generation (upgraded from Haiku 4.5 on 2026-10-20,
G-04, paid from the Max plan's monthly API credits). Reads artist variables
from artist_profile.json and generates platform-specific bios.

API cost: ~$0.03-0.10 per full generation (all platforms, thinking included).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-5-5"
# Opus 5.5 always thinks and the thinking counts toward max_tokens, so leave room.
MAX_TOKENS = 16000
EFFORT = "medium"

PROJECT_ROOT = Path(__file__).parent.parent
PROFILE_PATH = PROJECT_ROOT / "artist_profile.json"

PLATFORM_ORDER = [
    "bandcamp", "spotify", "soundcloud", "youtube",
    "ra_intro", "ra_full", "apple_music",
]

PLATFORM_LABELS = {
    "bandcamp": "Bandcamp",
    "spotify": "Spotify",
    "soundcloud": "SoundCloud",
    "youtube": "YouTube",
    "ra_intro": "RA - Intro",
    "ra_full": "RA - Full Bio",
    "apple_music": "Apple Music",
}


def load_profile() -> dict:
    """Load artist_profile.json. Returns empty dict if missing."""
    if not PROFILE_PATH.exists():
        return {}
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile: dict) -> None:
    """Save artist_profile.json."""
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _build_system_prompt() -> str:
    """Build the system prompt for bio generation. Bios are public, so until the songs are
    announced (positioning.md PUBLIC STATUS) they speak for the electronic lane: producer and DJ."""
    from release_manager.brand_context import brief
    return (
        "You are the bio writer for Inch of Shadow. Write platform-specific artist bios that keep one "
        "voice while respecting each platform's conventions and character limits. Atmospheric, "
        "evocative, understated. Not a press release, not marketing copy.\n\n"
        f"{brief({'lane': 'light'})}\n\n"
        "Hard rules:\n"
        "- Never mention Software Zero Records.\n"
        "- Double Figure is a PAST duo, always past tense: 'was one half of the duo Double Figure'. Include it "
        "ONLY in the Spotify, Apple Music, and YouTube bios. Do NOT mention it in the Bandcamp, SoundCloud, or RA bios.\n"
        "- 'Dark dance wave' leads the bios, inside the first sentence, on top of the genre words.\n"
        "- Never use a double dash (two hyphens) or an em dash. Use commas and full stops.\n"
        "- Front-load identity, Berlin, and the core genre keywords in the first sentence of every bio.\n"
        "- Respect character limits exactly. Count carefully.\n\n"
        "Return valid JSON only, no markdown, no explanation, no code fences."
    )


def _build_user_prompt(profile: dict, latest_release: dict | None = None) -> str:
    """Build the user prompt with artist variables and platform rules."""
    # Artist context
    artist_ctx = (
        f"Artist: {profile.get('artist', 'Inch of Shadow')}\n"
        f"Location: {profile.get('location', 'Berlin')}\n"
        f"Keywords: {', '.join(profile.get('keywords', []))}\n"
        f"Labels: {', '.join(profile.get('labels', []))}\n"
        f"Venues: {', '.join(profile.get('venues', []))}\n"
        f"Collaborators: {', '.join(profile.get('collaborators', []))}\n"
        f"Booking: {profile.get('booking_email', '')}\n"
    )

    # Latest release context
    release_ctx = ""
    if latest_release:
        meta = latest_release.get("metadata", {})
        release_ctx = (
            f"\nLatest release: {meta.get('title', '')} ({meta.get('release_type', 'Single')})\n"
            f"Genre: {meta.get('genre_primary', '')}"
        )
        if meta.get("genre_secondary"):
            release_ctx += f" / {meta['genre_secondary']}"
        release_ctx += f"\nRelease date: {latest_release.get('release_date', '')}\n"

    # Current bios as voice reference
    bios = profile.get("bios", {})
    voice_ref = ""
    spotify_bio = bios.get("spotify", {}).get("current", "")
    if spotify_bio:
        voice_ref = f"\nVoice reference (Spotify bio -- maintain this style):\n{spotify_bio}\n"

    # Links for YouTube bio
    links = profile.get("links", {})
    links_text = "\nArtist links:\n"
    for platform, url in links.items():
        links_text += f"  {platform}: {url}\n"

    # Platform rules
    platform_rules = (
        "\nGenerate bios for ALL of these platforms. Return as a JSON object with these exact keys:\n\n"
        "1. \"bandcamp\" (max 400 chars): Google-indexed. Genre keywords matter. Short, evocative.\n\n"
        "2. \"spotify\" (max 1500 chars): NLP reads this for categorization. Mood keywords important. "
        "Multiple paragraphs. Include labels. Mention that he was one half of the duo Double Figure (past tense). "
        "Can include the italic quote at the end if fitting.\n\n"
        "3. \"soundcloud\" (max 4000 chars): Casual, DJ/producer audience. Do NOT include platform "
        "links as text (SoundCloud has icon links). Include booking email at the end.\n\n"
        "4. \"youtube\" (max 1000 chars): Include streaming links and social links as plain text "
        "(YouTube doesn't have icon links). Include booking email. Use the artist links provided. "
        "Mention that he was one half of the duo Double Figure (past tense).\n\n"
        "5. \"ra_intro\" (max 256 chars): Brief artist summary for RA's intro field.\n\n"
        "6. \"ra_full\" (no limit): Expand on sound, history, releases. Do NOT repeat the intro.\n\n"
        "7. \"apple_music\" (no limit): First person, conversational. Apple assembles the displayed bio "
        "from structured Q&A answers, so write it as the artist answering in their own voice. No press "
        "language. No exclamation points. No all caps. No ampersands (write 'and'). Lead the first "
        "sentence with the sound and Berlin. Mention that he was one half of the duo Double Figure (past tense).\n"
    )

    return (
        f"Artist information:\n{artist_ctx}"
        f"{release_ctx}"
        f"{voice_ref}"
        f"{links_text}"
        f"{platform_rules}"
    )


def generate_bios(profile: dict, latest_release: dict | None = None, provider: str = "claude") -> dict:
    """Call Claude API and return generated bios for all platforms.

    Args:
        profile: full artist_profile.json dict
        latest_release: optional latest release dict from releases/

    Returns:
        dict with platform keys and bio strings, plus _usage info.

    Raises:
        ValueError: if ANTHROPIC_API_KEY is not set or response is invalid
        anthropic.APIError: on API errors
    """
    from release_manager import writers_ai

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(profile, latest_release)

    # Machine-27: the same prompts to Claude (default) or GPT
    raw, usage = writers_ai.write(system_prompt, user_prompt, provider=provider, max_tokens=MAX_TOKENS,
                                  effort=EFFORT, what="bios", claude_model=MODEL)

    # Strip markdown code fences if model added them
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) > 1:
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

    result = json.loads(raw)

    # Validate: must have at least some platform keys
    valid_keys = set(PLATFORM_ORDER)
    found = set(result.keys()) & valid_keys
    if not found:
        raise ValueError("Response contains no valid platform bios")

    # Fill missing platforms with empty string
    for pid in PLATFORM_ORDER:
        if pid not in result:
            result[pid] = ""

    result["_usage"] = {
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "model": usage["model"],
    }

    # Last pass (2026-10-15): invisible characters, dashes, curly quotes.
    from release_manager.copy_pass import finalise_bios
    return finalise_bios(result)
