"""
release_manager/seo_copy_generator.py
--------------------------------------
Generates platform-specific SEO copy for music releases using the Claude API.

Uses claude-opus-5-5 for generation (upgraded from Haiku 4.5 on 2026-10-20,
paid from the Max plan's monthly API credits).
Only sends release metadata (title, artist, genre, description, release date, BPM, key)
to Anthropic's API. No audio, no images, no personal contact data.

API cost: ~$0.03-0.10 per full generation (all platforms, Opus 5.5 pricing,
thinking included).
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-5-5"
# Opus 5.5 always thinks and the thinking counts toward max_tokens, so leave room.
MAX_TOKENS = 16000
EFFORT = "medium"

_SPECS_PATH = Path(__file__).resolve().parent / "seo_platform_specs.json"


def _load_specs() -> dict:
    """Load platform specs (genre vocabularies, front-load flags). Returns {} if missing."""
    try:
        with open(_SPECS_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}

# Platforms available for generation
PLATFORMS = [
    {"id": "spotify",    "label": "Spotify",     "fields": ["Pitch (500 chars)", "Artist Pick (140 chars)"]},
    {"id": "youtube",    "label": "YouTube",     "fields": ["Title options (3x)", "Description"]},
    {"id": "instagram",  "label": "Instagram",   "fields": ["Caption + hashtags"]},
    {"id": "beatport",   "label": "Beatport",    "fields": ["Release description"]},
    {"id": "bandcamp",   "label": "Bandcamp",    "fields": ["About text", "Tags"]},
    {"id": "soundcloud", "label": "SoundCloud",  "fields": ["Track description"]},
    {"id": "apple_music","label": "Apple Music", "fields": ["Bio paragraph"]},
]

TONES = [
    {"id": "authentic",     "label": "Authentic",     "description": "Natural first-person artist voice, personal, direct"},
    {"id": "professional",  "label": "Professional",  "description": "Polished, press-ready, third-person where appropriate"},
    {"id": "hype",          "label": "Hype",          "description": "Energetic, fan-facing, builds excitement"},
]


def _build_release_context(release: dict) -> str:
    """Extract release metadata into a compact context string for the prompt."""
    meta = release.get("metadata", {})
    tracks = release.get("tracks", [])

    lines = [
        f"Artist: {meta.get('artist', 'Inch of Shadow')}",
        f"Release title: {meta.get('title', '')}",
        f"Release type: {meta.get('release_type', 'Single')}",
        f"Primary genre: {meta.get('genre_primary', '')}",
    ]
    if meta.get("genre_secondary"):
        lines.append(f"Secondary genre: {meta.get('genre_secondary', '')}")
    if meta.get("description"):
        lines.append(f"Description: {meta.get('description', '')}")
    if release.get("release_date"):
        lines.append(f"Release date: {release.get('release_date', '')}")

    # Track details
    if tracks:
        track_lines = []
        for t in tracks[:3]:  # max 3 tracks to keep prompt tight
            parts = [t.get("title", "")]
            if t.get("bpm"):
                parts.append(f"{t['bpm']} BPM")
            if t.get("key"):
                parts.append(f"key: {t['key']}")
            track_lines.append(", ".join(p for p in parts if p))
        lines.append(f"Tracks: {' | '.join(track_lines)}")

    # Platform tags (moods, Spotify tags)
    ptags = release.get("platform_tags", {})
    spotify_tags = ptags.get("spotify", {})
    if spotify_tags.get("moods"):
        lines.append(f"Moods: {', '.join(spotify_tags['moods'])}")

    return "\n".join(lines)


def _build_system_prompt(tone: str, release: dict | None = None) -> str:
    """The writer's brief: the lane (Pinocchio and every non-song release: electronic, dance music),
    then the facts and voice read live from docs/brand (proof.md, voice.md)."""
    from release_manager.brand_context import brief
    tone_instructions = {
        "authentic": (
            "Write in his warm register: first person where the field allows, a real person glad you are "
            "here, not a brand. Describe how the track sounds, never what it means."
        ),
        "professional": (
            "Write in polished, press-ready language, third person where the field is a bio or a pitch. "
            "Still restrained and concrete: sound, place, facts."
        ),
        "hype": (
            "Write with more energy for release day: strong verbs, short rhythmic sentences. No hype "
            "superlatives, no marketing filler: the energy comes from the sound words."
        ),
    }
    return (
        "You are the SEO copywriter for Inch of Shadow's releases. You write platform-specific copy.\n\n"
        f"{brief(release)}\n\n"
        f"Tone: {tone_instructions.get(tone, tone_instructions['authentic'])}\n\n"
        "Hard rules:\n"
        "- Never use a double dash (two hyphens) or an em dash in output copy. Use commas and full stops.\n"
        "- Never invent statistics, follower counts, stream numbers, or algorithm percentages.\n"
        "- Never mention Software Zero Records.\n"
        "- No clickbait, listicle hooks, 'POV:', or 'wait for it'. No feedback asks. No lines about the message itself.\n"
        "- Front-load identity and the most-searched genre keyword of THIS release in the first sentence or line of every field.\n"
        "- Genre tags go in tags and metadata fields; artistic words ('dark dance wave') go in sentences.\n\n"
        "Always respect character limits exactly. Return valid JSON only, no markdown, no explanation."
    )


def _build_user_prompt(release_context: str, platforms: list[str], specs: dict | None = None) -> str:
    platform_set = set(platforms)

    instructions = []

    if "spotify" in platform_set:
        instructions.append(
            '"spotify_pitch": a Spotify for Artists pitch (max 490 chars). '
            'Structure: emotional hook → personal story/inspiration → sound/mood description → '
            'playlist suggestion (name 1-2 specific Spotify editorial playlists). '
            'No stats, no hype, no follower counts. Start with feeling, not facts.'
        )
        instructions.append(
            '"spotify_artist_pick": a custom message for the Spotify Artist Pick feature (max 135 chars). '
            'Short, personal, directs listeners to the release.'
        )

    if "youtube" in platform_set:
        instructions.append(
            '"youtube_titles": array of 3 YouTube video title options (max 60 chars each). '
            'Front-load the most important keyword. No clickbait, no ALL CAPS, no "Official Video" unless needed.'
        )
        instructions.append(
            '"youtube_description": a YouTube video description (max 500 chars). '
            'First line (max 100 chars) is the hook -- it shows before "Show more". '
            'Then: 2-3 sentences about the track. Then: streaming links placeholder [LINKS]. '
            'Then: genre/mood keywords as a natural paragraph (not a list).'
        )

    if "instagram" in platform_set:
        instructions.append(
            '"instagram_caption": an Instagram caption (max 150 chars before "more", aim for 80-120 chars for the first line). '
            'Evocative, visual, matches the dark aesthetic. Do NOT use hashtags in the caption body. '
            'Then "instagram_hashtags": array of exactly 5 relevant hashtags (without #, lowercase). '
            'Genre-specific and scene-specific only -- no generic music hashtags like #newmusic or #music.'
        )

    if "beatport" in platform_set:
        instructions.append(
            '"beatport_description": a release description for Beatport (max 450 chars). '
            'Focus on the sound: groove, texture, energy level, peak-time vs warm-up, DJ usability. '
            'Beatport buyers are DJs -- speak to them.'
        )

    if "bandcamp" in platform_set:
        instructions.append(
            '"bandcamp_about": an album/release "about" text for Bandcamp (max 450 chars). '
            'Can be more personal and fan-facing than Beatport. Include the story, mood, inspiration. '
            'Bandcamp fans read this.'
        )
        instructions.append(
            '"bandcamp_tags": array of exactly 10 tags for Bandcamp (lowercase, no #). '
            'Mix of: genre tags, mood tags, scene tags, BPM range if applicable. '
            'No generic tags like "music" or "electronic".'
        )

    if "soundcloud" in platform_set:
        instructions.append(
            '"soundcloud_description": a SoundCloud track description (max 450 chars). '
            'Can include: mood, inspiration, production notes. SoundCloud audience includes both listeners and producers -- '
            'a subtle nod to production approach is appropriate.'
        )

    if "apple_music" in platform_set:
        instructions.append(
            '"apple_music_bio": a short artist bio paragraph for Apple Music (max 250 chars). '
            'Factual, third-person, genre-defining. Apple Music bio is set via distributor -- '
            'write this as a standalone paragraph that fits into a longer bio.'
        )

    prompt = (
        f"Release information:\n{release_context}\n\n"
        f"Generate the following platform copy and return as a single JSON object:\n"
        + "\n".join(f"- {inst}" for inst in instructions)
    )

    # Spec-driven genre/tag vocabulary (canonical spellings per platform, from
    # seo_platform_specs.json cross_platform_summary.genre_vocabularies)
    vocab = (specs or {}).get("cross_platform_summary", {}).get("genre_vocabularies", {})
    vocab_key_for = {
        "soundcloud": "soundcloud",
        "beatport": "beatport",
        "bandcamp": "bandcamp",
        "instagram": "instagram",
        "spotify": "spotify_apple",
        "apple_music": "spotify_apple",
    }
    vocab_lines = []
    seen_keys = set()
    for pid in platforms:
        key = vocab_key_for.get(pid)
        if key and key in vocab and key not in seen_keys:
            seen_keys.add(key)
            vocab_lines.append(f"- {pid}: {vocab[key]}")
    if vocab_lines:
        prompt += (
            "\n\nGenre/tag vocabulary (use these canonical spellings exactly; do not invent "
            "genres or put mood words in genre/tag fields):\n" + "\n".join(vocab_lines)
        )

    return prompt


def generate_copy(
    release: dict,
    platforms: list[str],
    tone: str = "authentic",
    provider: str = "claude",
) -> dict:
    """
    Call the Claude API and return a dict of generated copy fields.

    Args:
        release: full release dict from releases/<slug>.json
        platforms: list of platform IDs to generate copy for
        tone: "authentic" | "professional" | "hype"

    Returns:
        dict with generated copy fields, or raises on error.

    Raises:
        ValueError: if ANTHROPIC_API_KEY is not set
        anthropic.APIError: on API errors
    """
    from release_manager import writers_ai

    specs = _load_specs()
    release_context = _build_release_context(release)
    system_prompt = _build_system_prompt(tone, release)
    user_prompt = _build_user_prompt(release_context, platforms, specs)

    # Machine-27: the same prompts to Claude (default) or GPT
    raw, usage = writers_ai.write(system_prompt, user_prompt, provider=provider, max_tokens=MAX_TOKENS,
                                  effort=EFFORT, what="copy", claude_model=MODEL)

    # Strip markdown code fences if model added them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    result = json.loads(raw)

    # Attach usage info (for transparency, not shown to user)
    result["_usage"] = {
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "model": usage["model"],
    }

    # Last pass (2026-10-15): clean every field, check the Instagram caption.
    from release_manager.copy_pass import finalise_copy
    return finalise_copy(result, release)
