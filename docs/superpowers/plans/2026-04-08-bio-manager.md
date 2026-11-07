# Bio Manager — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Bio Manager page to the Release Manager that centralizes artist bio management across 7 platform slots (Bandcamp, Spotify, SoundCloud, YouTube, RA intro, RA full, Apple Music) with AI generation, side-by-side comparison, inline editing, undo, and "Applied" confirmation.

**Architecture:** New `artist_profile.json` in project root stores artist variables and bios. New `bio_manager.py` module handles profile I/O and Claude API generation. New `/bios` route and 5 API endpoints in `webapp.py`. New `bios.html` template with side-by-side cards. CSS in `release_manager/static/style.css`.

**Tech Stack:** Python 3.9+, Flask, Claude Haiku API (anthropic SDK), vanilla JS, single `style.css` file

**Spec:** `docs/superpowers/specs/2026-04-08-bio-manager-design.md`

---

### Task 1: Create artist_profile.json with Initial Data

**Files:**
- Create: `artist_profile.json`

- [ ] **Step 1: Create the initial artist profile**

Create `artist_profile.json` in the project root with the actual artist data:

```json
{
  "artist": "Inch of Shadow",
  "location": "Berlin",
  "labels": ["MM Discos", "Stereo Society", "NaNa Disc"],
  "venues": ["About Blank", "Beate Uwe", "KitKat"],
  "collaborators": ["Double Figure band", "La Groove Machine", "Status Zero"],
  "keywords": ["dark disco", "EBM", "acid techno", "electro", "analog synthesizers", "hypnotic", "melancholic", "industrial", "cinematic", "underground"],
  "booking_email": "inchofshadow@gmail.com",
  "links": {
    "spotify": "https://open.spotify.com/artist/5k4SyH7JRPMJe1RHYMI2CT",
    "bandcamp": "https://inchofshadow.bandcamp.com",
    "soundcloud": "https://soundcloud.com/inch-of-shadow",
    "instagram": "https://www.instagram.com/inch_of_shadow/",
    "beatport": "https://www.beatport.com/artist/inch-of-shadow/1276949",
    "youtube": "https://www.youtube.com/@InchofShadow",
    "apple_music": "https://music.apple.com/us/artist/inch-of-shadow/1784503341",
    "ra": "https://ra.co/dj/inchofshadow"
  },
  "edit_urls": {
    "bandcamp": "https://inchofshadow.bandcamp.com/settings",
    "spotify": "https://artists.spotify.com",
    "soundcloud": "https://soundcloud.com/you/edit",
    "youtube": "https://studio.youtube.com",
    "ra": "https://ra.co/dj/inchofshadow/edit",
    "apple_music": "https://artists.apple.com"
  },
  "bios": {
    "bandcamp": {
      "current": "Acid-soaked machines and melancholic grooves from Berlin's underground. Inch of Shadow moves between dark disco, EBM, techno, and electro \u2014 raw, hypnotic, industrial, cinematic, and always searching for something deeper. Released on MM Discos. Heard at About Blank, Beate Uwe, and KitKat.",
      "previous": null,
      "char_limit": 400,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "spotify": {
      "current": "Inch of Shadow is a Berlin-based electronic music project exploring the darker edges of the dancefloor.\n\nBuilt around analog synthesizers and hardware machines, the sound moves between EBM, dark disco, acid techno, and electro \u2014 where mechanical rhythms meet cinematic tension. Pulsing basslines, cold sequences, and shadowed atmospheres shape a world somewhere between industrial motion and melancholic introspection.\n\nInfluenced by the raw, hypnotic energy of underground clubs and the discipline of analog synthesis, Inch of Shadow focuses on minimal elements: rhythm, texture, and pressure. Each track unfolds slowly, driven by evolving machines and controlled distortion \u2014 from acid-drenched dancefloor tools to slow, cinematic explorations.\n\nRooted in Berlin's late-night electronic culture, the project navigates the space between club ritual and sonic architecture, where darkness becomes structure and repetition becomes momentum. Released on MM Discos.",
      "previous": null,
      "char_limit": 1500,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "soundcloud": {
      "current": "Slow-burning electronics shaped by dark disco, acid, electro, and EBM. Berlin-based producer, DJ.\n\nBuilt around analog synthesizers and hardware machines, the sound moves between dark disco, EBM, acid techno, and electro \u2014 where mechanical rhythms meet cinematic tension. Raw, hypnotic, melancholic, and industrial. Each track unfolds slowly, driven by evolving machines and controlled distortion.\n\nReleases on MM Discos, Stereo Society, and NaNa Disc. One half of Double Figure band.\n\nBooking: inchofshadow@gmail.com",
      "previous": null,
      "char_limit": 4000,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "youtube": {
      "current": "Inch of Shadow \u2014 slow-burning electronics shaped by dark disco, acid, electro, and EBM from Berlin's underground.\n\nBuilt around analog synthesizers and hardware machines, the sound moves between dark disco, EBM, acid techno, and electro \u2014 where mechanical rhythms meet cinematic tension. Raw, hypnotic, melancholic, and industrial.\n\nReleases on MM Discos, Stereo Society, and NaNa Disc. One half of Double Figure band.\n\nStream everywhere:\nSpotify: https://open.spotify.com/artist/5k4SyH7JRPMJe1RHYMI2CT\nApple Music: https://music.apple.com/us/artist/inch-of-shadow/1784503341\nBandcamp: https://inchofshadow.bandcamp.com\nBeatport: https://www.beatport.com/artist/inch-of-shadow/1276949\nSoundCloud: https://soundcloud.com/inch-of-shadow\n\nFollow:\nInstagram: https://www.instagram.com/inch_of_shadow/\nResident Advisor: https://ra.co/dj/inchofshadow\n\nBooking: inchofshadow@gmail.com",
      "previous": null,
      "char_limit": 1000,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "ra_intro": {
      "current": "Slow-burning electronics shaped by dark disco, acid, electro, and EBM. Berlin-based producer and DJ. Built around analog synthesizers and hardware machines \u2014 raw, hypnotic, melancholic, and industrial.",
      "previous": null,
      "char_limit": 256,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "ra_full": {
      "current": "The sound moves between dark disco, EBM, acid techno, and electro \u2014 where mechanical rhythms meet cinematic tension. Each track unfolds slowly, driven by evolving machines and controlled distortion, from acid-drenched dancefloor tools to slow, cinematic explorations.\n\nOne half of Double Figure band. Releases on MM Discos, Stereo Society, and NaNa Disc. Played at About Blank, Beate Uwe, and KitKat.",
      "previous": null,
      "char_limit": null,
      "applied": true,
      "applied_date": "2026-04-08T00:00:00"
    },
    "apple_music": {
      "current": "",
      "previous": null,
      "char_limit": null,
      "applied": false,
      "applied_date": null
    }
  }
}
```

- [ ] **Step 2: Verify JSON is valid**

Run: `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python3 -c "import json; d=json.load(open('artist_profile.json')); print('OK:', len(d['bios']), 'platforms,', len(d['keywords']), 'keywords')"`

Expected: `OK: 7 platforms, 10 keywords`

- [ ] **Step 3: Add to .gitignore if needed, then commit**

Check if `artist_profile.json` should be in `.gitignore` (it contains an email address but no API keys — it's safe to commit).

```bash
git add artist_profile.json
git commit -m "feat: add artist_profile.json with initial bio data

Stores artist-level variables (keywords, labels, venues, links) and
current bios for 7 platform slots. Pre-populated with bios written
during the April 8 bio sprint."
```

---

### Task 2: Bio Manager Module (bio_manager.py)

**Files:**
- Create: `release_manager/bio_manager.py`

This module handles loading/saving `artist_profile.json` and generating bios via Claude API.

- [ ] **Step 1: Create the module with profile I/O helpers**

Create `release_manager/bio_manager.py`:

```python
"""
release_manager/bio_manager.py
-------------------------------
Artist profile I/O and bio generation via Claude API.

Uses claude-haiku-4-5 for bio generation. Reads artist variables
from artist_profile.json and generates platform-specific bios.

API cost: ~$0.003-0.005 per full generation (all platforms).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

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
```

- [ ] **Step 2: Add the bio generation functions**

Append to `release_manager/bio_manager.py`:

```python
def _build_system_prompt() -> str:
    """Build the system prompt for bio generation."""
    return (
        "You are a bio writer for a Berlin-based electronic music artist. Write platform-specific "
        "artist bios that maintain a consistent voice while respecting each platform's conventions "
        "and character limits. The voice is: atmospheric, evocative, understated. Not a press release. "
        "Not marketing copy. Reads like an artist describing their own world.\n\n"
        "Hard rules:\n"
        "- Never mention Software Zero Records.\n"
        "- Use 'Double Figure band' (always keep the word 'band').\n"
        "- Respect character limits exactly. Count carefully.\n\n"
        "Return valid JSON only -- no markdown, no explanation, no code fences."
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
        "Multiple paragraphs. Include labels. Can include the italic quote at the end if fitting.\n\n"
        "3. \"soundcloud\" (max 4000 chars): Casual, DJ/producer audience. Do NOT include platform "
        "links as text (SoundCloud has icon links). Include booking email at the end.\n\n"
        "4. \"youtube\" (max 1000 chars): Include streaming links and social links as plain text "
        "(YouTube doesn't have icon links). Include booking email. Use the artist links provided.\n\n"
        "5. \"ra_intro\" (max 256 chars): Brief artist summary for RA's intro field.\n\n"
        "6. \"ra_full\" (no limit): Expand on sound, history, releases. Do NOT repeat the intro.\n\n"
        "7. \"apple_music\" (no limit): First person, conversational. No press language. "
        "No exclamation points. No all caps.\n"
    )

    return (
        f"Artist information:\n{artist_ctx}"
        f"{release_ctx}"
        f"{voice_ref}"
        f"{links_text}"
        f"{platform_rules}"
    )


def generate_bios(profile: dict, latest_release: dict | None = None) -> dict:
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
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(profile, latest_release)

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

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
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }

    return result
```

- [ ] **Step 3: Verify the module loads**

Run: `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python3 -c "from release_manager.bio_manager import load_profile, PLATFORM_ORDER; p = load_profile(); print('OK:', len(p.get('bios',{})), 'bios,', len(PLATFORM_ORDER), 'platforms')"`

Expected: `OK: 7 bios, 7 platforms`

- [ ] **Step 4: Commit**

```bash
git add release_manager/bio_manager.py
git commit -m "feat: add bio manager module

Profile I/O (load/save artist_profile.json) and Claude Haiku bio
generation for 7 platform slots. Maintains artist voice, respects
character limits, includes platform-specific formatting rules."
```

---

### Task 3: API Endpoints in webapp.py

**Files:**
- Modify: `release_manager/webapp.py`

Add the `/bios` page route and 5 API endpoints.

- [ ] **Step 1: Add the page route and generate endpoint**

In `release_manager/webapp.py`, find the `# Engagement Queue` section comment. Insert BEFORE it:

```python
# ---------------------------------------------------------------------------
# Bio Manager
# ---------------------------------------------------------------------------

@app.route("/bios")
def bios_page():
    """Bio Manager page."""
    from release_manager.bio_manager import load_profile, PLATFORM_ORDER, PLATFORM_LABELS
    profile = load_profile()
    return render_template(
        "bios.html",
        profile=profile,
        platform_order=PLATFORM_ORDER,
        platform_labels=PLATFORM_LABELS,
    )


@app.route("/api/bios/generate", methods=["POST"])
def api_bios_generate():
    """Generate bios for all platforms via Claude API."""
    from release_manager.bio_manager import load_profile, generate_bios

    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    # Get latest release for context
    releases = list_releases()
    latest = releases[-1] if releases else None

    try:
        result = generate_bios(profile, latest)
        return jsonify({"ok": True, "bios": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)[:200]}"}), 500
```

- [ ] **Step 2: Add save, undo, applied, and profile endpoints**

Directly after the generate endpoint, add:

```python
@app.route("/api/bios/save", methods=["PUT"])
def api_bios_save():
    """Save a bio for a specific platform."""
    from release_manager.bio_manager import load_profile, save_profile

    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()
    bio = data.get("bio", "")
    source = data.get("source", "edit")

    if not platform:
        return jsonify({"error": "No platform specified."}), 400
    if not isinstance(bio, str):
        return jsonify({"error": "Bio must be a string."}), 400

    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400

    if source == "generate":
        # "Use This" -- save previous for undo
        bios[platform]["previous"] = bios[platform].get("current", "")
        bios[platform]["current"] = bio
        bios[platform]["applied"] = False
        bios[platform]["applied_date"] = None
    else:
        # "Save Edit" -- direct edit, no undo tracking
        bios[platform]["current"] = bio
        bios[platform]["applied"] = False
        bios[platform]["applied_date"] = None

    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/undo", methods=["PUT"])
def api_bios_undo():
    """Undo a bio change for a specific platform."""
    from release_manager.bio_manager import load_profile, save_profile

    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()

    if not platform:
        return jsonify({"error": "No platform specified."}), 400

    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400

    prev = bios[platform].get("previous")
    if prev is None:
        return jsonify({"error": "Nothing to undo."}), 400

    # Swap current and previous
    bios[platform]["previous"] = bios[platform]["current"]
    bios[platform]["current"] = prev
    bios[platform]["applied"] = False
    bios[platform]["applied_date"] = None

    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/applied", methods=["PUT"])
def api_bios_applied():
    """Mark a bio as applied on the platform."""
    from release_manager.bio_manager import load_profile, save_profile

    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()

    if not platform:
        return jsonify({"error": "No platform specified."}), 400

    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400

    bios[platform]["applied"] = True
    bios[platform]["applied_date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/profile", methods=["PUT"])
def api_bios_profile():
    """Update artist profile variables (not bios)."""
    from release_manager.bio_manager import load_profile, save_profile

    data = request.get_json(silent=True) or {}

    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    # Update only the variable fields, not bios
    for field in ["keywords", "labels", "venues", "collaborators", "booking_email"]:
        if field in data:
            profile[field] = data[field]

    if "links" in data and isinstance(data["links"], dict):
        profile["links"] = data["links"]

    save_profile(profile)
    return jsonify({"ok": True})
```

- [ ] **Step 3: Verify the app loads**

Run: `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python3 -c "from release_manager.webapp import app; print('OK')"`

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add release_manager/webapp.py
git commit -m "feat: add Bio Manager routes and API endpoints

GET /bios page route, POST /api/bios/generate, PUT /api/bios/save,
PUT /api/bios/undo, PUT /api/bios/applied, PUT /api/bios/profile."
```

---

### Task 4: Bio Manager Template (bios.html)

**Files:**
- Create: `release_manager/templates/bios.html`

The template shows artist variables (collapsible), generate button, and platform cards with side-by-side current/generated bios. Uses safe DOM construction (createElement/textContent) to prevent XSS.

- [ ] **Step 1: Create the HTML template**

Create `release_manager/templates/bios.html`:

```html
{% extends "base.html" %}
{% block title %}Bio Manager{% endblock %}

{% block content %}
<div class="resizer-page">
    <h1>Bio Manager</h1>
    <p class="form-subtitle">Manage your artist bios across all platforms. Edit, generate, compare, and apply.</p>

    <!-- Artist Variables (collapsible) -->
    <div class="section">
        <details id="bio-vars-details">
            <summary><h2 style="display:inline;">Artist Variables</h2></summary>
            <div class="bio-vars-grid">
                <div class="form-group">
                    <label>Keywords</label>
                    <div class="bio-tag-container" id="bio-var-keywords" data-field="keywords">
                        {% for kw in profile.get('keywords', []) %}
                        <span class="bio-var-tag">{{ kw }}<button type="button" class="bio-var-tag-rm">x</button></span>
                        {% endfor %}
                        <input type="text" class="bio-var-add" placeholder="Add keyword..." />
                    </div>
                </div>
                <div class="form-group">
                    <label>Labels</label>
                    <div class="bio-tag-container" id="bio-var-labels" data-field="labels">
                        {% for lb in profile.get('labels', []) %}
                        <span class="bio-var-tag">{{ lb }}<button type="button" class="bio-var-tag-rm">x</button></span>
                        {% endfor %}
                        <input type="text" class="bio-var-add" placeholder="Add label..." />
                    </div>
                </div>
                <div class="form-group">
                    <label>Venues</label>
                    <div class="bio-tag-container" id="bio-var-venues" data-field="venues">
                        {% for v in profile.get('venues', []) %}
                        <span class="bio-var-tag">{{ v }}<button type="button" class="bio-var-tag-rm">x</button></span>
                        {% endfor %}
                        <input type="text" class="bio-var-add" placeholder="Add venue..." />
                    </div>
                </div>
                <div class="form-group">
                    <label>Booking Email</label>
                    <input type="email" class="form-input" id="bio-var-email" value="{{ profile.get('booking_email', '') }}" />
                </div>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary btn-sm" id="bio-save-vars-btn">Save Variables</button>
                <span class="seo-status" id="bio-vars-status"></span>
            </div>
        </details>
    </div>

    <!-- Generate Button -->
    <div class="form-actions" style="margin-bottom: 1.5rem;">
        <button type="button" class="btn btn-accent" id="bio-generate-btn">Generate All Bios</button>
        <span class="seo-status" id="bio-gen-status"></span>
    </div>

    <!-- Platform Cards -->
    <div id="bio-cards">
        {% set bios = profile.get('bios', {}) %}
        {% set edit_urls = profile.get('edit_urls', {}) %}
        {% for pid in platform_order %}
            {% set bio = bios.get(pid, {}) %}
            {% set label = platform_labels.get(pid, pid) %}
            {% set limit = bio.get('char_limit') %}
            {% set edit_url = edit_urls.get(pid.replace('_intro','').replace('_full',''), '') %}
            <div class="bio-card" data-platform="{{ pid }}">
                <div class="bio-card-header">
                    <span class="bio-card-title">{{ label }}{% if limit %} ({{ limit }} chars){% endif %}</span>
                    {% if edit_url %}
                    <a href="{{ edit_url }}" target="_blank" rel="noopener" class="bio-edit-link">Edit on {{ label.split(' - ')[0] }} &#8599;</a>
                    {% endif %}
                </div>
                <div class="bio-card-body">
                    <div class="bio-side bio-current">
                        <div class="bio-side-label">Current Bio</div>
                        <textarea class="bio-textarea" data-platform="{{ pid }}" data-limit="{{ limit or '' }}">{{ bio.get('current', '') }}</textarea>
                        <div class="bio-side-footer">
                            <span class="char-counter bio-char-count"></span>
                            <button type="button" class="btn btn-secondary btn-sm bio-save-edit-btn" data-platform="{{ pid }}">Save Edit</button>
                            <button type="button" class="btn btn-secondary btn-sm bio-copy-btn" data-side="current" data-platform="{{ pid }}">Copy</button>
                        </div>
                    </div>
                    <div class="bio-side bio-generated" style="display:none;">
                        <div class="bio-side-label">Generated Bio</div>
                        <div class="bio-gen-text" data-platform="{{ pid }}"></div>
                        <div class="bio-side-footer">
                            <span class="char-counter bio-gen-char-count"></span>
                            <button type="button" class="btn btn-accent btn-sm bio-use-btn" data-platform="{{ pid }}">Use This</button>
                            <button type="button" class="btn btn-secondary btn-sm bio-copy-btn" data-side="generated" data-platform="{{ pid }}">Copy</button>
                        </div>
                    </div>
                </div>
                <div class="bio-card-actions">
                    <button type="button" class="btn btn-secondary btn-sm bio-undo-btn" data-platform="{{ pid }}" {% if not bio.get('previous') %}disabled{% endif %}>Undo</button>
                    <button type="button" class="btn btn-sm bio-applied-btn {% if bio.get('applied') %}bio-applied-active{% endif %}" data-platform="{{ pid }}">
                        {% if bio.get('applied') %}Applied &#10003;{% else %}Mark Applied{% endif %}
                    </button>
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<script>
(function () {
    var generateBtn = document.getElementById('bio-generate-btn');
    var genStatus   = document.getElementById('bio-gen-status');
    var saveVarsBtn = document.getElementById('bio-save-vars-btn');
    var varsStatus  = document.getElementById('bio-vars-status');

    // -- Character counters --
    function updateCharCount(textarea) {
        var card = textarea.closest('.bio-card');
        var counter = card.querySelector('.bio-current .bio-char-count');
        var limit = textarea.dataset.limit ? parseInt(textarea.dataset.limit) : null;
        var len = textarea.value.length;
        if (limit) {
            counter.textContent = len + ' / ' + limit;
            counter.className = 'char-counter bio-char-count';
            if (len > limit) counter.classList.add('char-over');
            else if (len > limit * 0.9) counter.classList.add('char-warn');
            else counter.classList.add('char-ok');
        } else {
            counter.textContent = len + ' chars';
            counter.className = 'char-counter bio-char-count';
        }
    }

    document.querySelectorAll('.bio-textarea').forEach(function (ta) {
        updateCharCount(ta);
        ta.addEventListener('input', function () { updateCharCount(this); });
    });

    // -- Save Edit --
    document.querySelectorAll('.bio-save-edit-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var pid = this.dataset.platform;
            var ta = document.querySelector('.bio-textarea[data-platform="' + pid + '"]');
            fetch('/api/bios/save', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ platform: pid, bio: ta.value, source: 'edit' }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.ok) { btn.textContent = 'Saved!'; setTimeout(function () { btn.textContent = 'Save Edit'; }, 1500); }
            });
        });
    });

    // -- Copy --
    document.querySelectorAll('.bio-copy-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var pid = this.dataset.platform;
            var side = this.dataset.side;
            var text = '';
            if (side === 'current') {
                text = document.querySelector('.bio-textarea[data-platform="' + pid + '"]').value;
            } else {
                text = document.querySelector('.bio-gen-text[data-platform="' + pid + '"]').textContent;
            }
            navigator.clipboard.writeText(text).then(function () {
                btn.textContent = 'Copied!';
                setTimeout(function () { btn.textContent = 'Copy'; }, 1500);
            });
        });
    });

    // -- Undo --
    document.querySelectorAll('.bio-undo-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var pid = this.dataset.platform;
            fetch('/api/bios/undo', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ platform: pid }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.ok) { location.reload(); }
                else if (d.error) { alert(d.error); }
            });
        });
    });

    // -- Applied --
    document.querySelectorAll('.bio-applied-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var pid = this.dataset.platform;
            var self = this;
            fetch('/api/bios/applied', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ platform: pid }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.ok) {
                    self.textContent = 'Applied \u2713';
                    self.classList.add('bio-applied-active');
                }
            });
        });
    });

    // -- Use This --
    document.querySelectorAll('.bio-use-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var pid = this.dataset.platform;
            var genText = document.querySelector('.bio-gen-text[data-platform="' + pid + '"]').textContent;
            var ta = document.querySelector('.bio-textarea[data-platform="' + pid + '"]');
            fetch('/api/bios/save', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ platform: pid, bio: genText, source: 'generate' }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.ok) {
                    ta.value = genText;
                    updateCharCount(ta);
                    // Enable undo
                    var undoBtn = document.querySelector('.bio-undo-btn[data-platform="' + pid + '"]');
                    if (undoBtn) undoBtn.disabled = false;
                    // Reset applied
                    var appliedBtn = document.querySelector('.bio-applied-btn[data-platform="' + pid + '"]');
                    if (appliedBtn) {
                        appliedBtn.textContent = 'Mark Applied';
                        appliedBtn.classList.remove('bio-applied-active');
                    }
                    btn.textContent = 'Accepted!';
                    setTimeout(function () { btn.textContent = 'Use This'; }, 1500);
                }
            });
        });
    });

    // -- Generate All --
    generateBtn.addEventListener('click', function () {
        generateBtn.disabled = true;
        genStatus.textContent = 'Generating bios...';

        fetch('/api/bios/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: '{}',
        }).then(function (r) { return r.json(); }).then(function (d) {
            generateBtn.disabled = false;
            if (d.error) {
                genStatus.textContent = 'Error: ' + d.error;
                return;
            }
            var bios = d.bios || {};
            genStatus.textContent = '';
            if (bios._usage) {
                genStatus.textContent = 'Tokens: ' + bios._usage.input_tokens + ' in / ' + bios._usage.output_tokens + ' out';
            }

            // Show generated bios
            document.querySelectorAll('.bio-card').forEach(function (card) {
                var pid = card.dataset.platform;
                var genSide = card.querySelector('.bio-generated');
                var genTextEl = card.querySelector('.bio-gen-text');
                var genCounter = card.querySelector('.bio-gen-char-count');
                var text = bios[pid] || '';

                genTextEl.textContent = text;
                genSide.style.display = '';

                var limit = card.querySelector('.bio-textarea').dataset.limit;
                limit = limit ? parseInt(limit) : null;
                var len = text.length;
                if (limit) {
                    genCounter.textContent = len + ' / ' + limit;
                    genCounter.className = 'char-counter bio-gen-char-count';
                    if (len > limit) genCounter.classList.add('char-over');
                    else if (len > limit * 0.9) genCounter.classList.add('char-warn');
                    else genCounter.classList.add('char-ok');
                } else {
                    genCounter.textContent = len + ' chars';
                    genCounter.className = 'char-counter bio-gen-char-count';
                }
            });
        }).catch(function () {
            generateBtn.disabled = false;
            genStatus.textContent = 'Network error';
        });
    });

    // -- Save Variables --
    function getTagValues(containerId) {
        var tags = [];
        document.querySelectorAll('#' + containerId + ' .bio-var-tag').forEach(function (tag) {
            var text = tag.childNodes[0].textContent.trim();
            if (text) tags.push(text);
        });
        return tags;
    }

    // Wire up tag removal
    document.querySelectorAll('.bio-var-tag-rm').forEach(function (btn) {
        btn.addEventListener('click', function () { this.parentElement.remove(); });
    });

    // Wire up tag addition
    document.querySelectorAll('.bio-var-add').forEach(function (input) {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && this.value.trim()) {
                e.preventDefault();
                var val = this.value.trim();
                var tag = document.createElement('span');
                tag.className = 'bio-var-tag';
                tag.appendChild(document.createTextNode(val));
                var rm = document.createElement('button');
                rm.type = 'button';
                rm.className = 'bio-var-tag-rm';
                rm.textContent = 'x';
                rm.addEventListener('click', function () { tag.remove(); });
                tag.appendChild(rm);
                this.parentElement.insertBefore(tag, this);
                this.value = '';
            }
        });
    });

    saveVarsBtn.addEventListener('click', function () {
        var data = {
            keywords: getTagValues('bio-var-keywords'),
            labels: getTagValues('bio-var-labels'),
            venues: getTagValues('bio-var-venues'),
            booking_email: document.getElementById('bio-var-email').value,
        };
        fetch('/api/bios/profile', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.ok) {
                varsStatus.textContent = 'Saved!';
                setTimeout(function () { varsStatus.textContent = ''; }, 1500);
            }
        });
    });
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Verify template syntax**

Run the Flask app and visit `http://localhost:5001/bios` in browser. The page should render with all 7 platform cards showing current bios.

- [ ] **Step 3: Commit**

```bash
git add release_manager/templates/bios.html
git commit -m "feat: add Bio Manager page template

Side-by-side current/generated bios, inline editing, copy buttons,
undo, 'Applied' confirmation, artist variables section. Uses safe
DOM construction for dynamic content."
```

---

### Task 5: CSS Styles for Bio Manager

**Files:**
- Modify: `release_manager/static/style.css`

- [ ] **Step 1: Add bio manager styles**

At the end of `release_manager/static/style.css`, before any `@media` responsive breakpoint, add:

```css
/* ============================================================
   Bio Manager
   ============================================================ */

.bio-vars-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}

.bio-tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    min-height: 36px;
    align-items: center;
}

.bio-var-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border: 1px solid var(--border-color);
    border-radius: 3px;
    font-size: 12px;
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.bio-var-tag-rm {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 11px;
    padding: 0 2px;
    opacity: 0.5;
}

.bio-var-tag-rm:hover {
    opacity: 1;
    color: var(--color-overdue);
}

.bio-var-add {
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 12px;
    padding: 4px;
    flex: 1;
    min-width: 100px;
    font-family: var(--font-main);
    outline: none;
}

.bio-var-add::placeholder {
    color: var(--text-secondary);
    opacity: 0.5;
}

.bio-card {
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-secondary);
    overflow: hidden;
}

.bio-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-tertiary);
}

.bio-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-accent);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.bio-edit-link {
    font-size: 12px;
    color: var(--text-secondary);
    text-decoration: none;
}

.bio-edit-link:hover {
    color: var(--text-accent);
}

.bio-card-body {
    display: flex;
    gap: 1px;
    background: var(--border-color);
}

.bio-side {
    flex: 1;
    padding: 1rem;
    background: var(--bg-secondary);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.bio-side-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.bio-textarea {
    width: 100%;
    min-height: 120px;
    padding: 0.75rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 13px;
    font-family: var(--font-main);
    line-height: 1.5;
    resize: vertical;
}

.bio-textarea:focus {
    outline: none;
    border-color: var(--text-accent);
}

.bio-gen-text {
    padding: 0.75rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
    min-height: 120px;
}

.bio-side-footer {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.bio-card-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--border-color);
}

.bio-applied-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
}

.bio-applied-active {
    background: var(--color-done);
    border-color: var(--color-done);
    color: #fff;
}

@media (max-width: 768px) {
    .bio-card-body { flex-direction: column; }
    .bio-vars-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Commit**

```bash
git add release_manager/static/style.css
git commit -m "feat: add CSS styles for Bio Manager

Side-by-side card layout, tag inputs for variables, textarea styling,
char counters, Applied state, responsive breakpoints. Dark theme."
```

---

### Task 6: Add Sidebar Link

**Files:**
- Modify: `release_manager/templates/base.html`

- [ ] **Step 1: Add Bio Manager to sidebar**

In `release_manager/templates/base.html`, find the Tools group (around line 42-48). After the SEO Copy link (line 47), add:

```html
                    <a href="{{ url_for('bios_page') }}" class="sidebar-link{% if request.endpoint == 'bios_page' %} active{% endif %}">Bio Manager</a>
```

So the Tools group becomes:
```html
                <div class="sidebar-group">
                    <div class="sidebar-group-label">Tools</div>
                    <a href="{{ url_for('autopilot_page') }}" class="sidebar-link{% if request.endpoint == 'autopilot_page' %} active{% endif %}">Autopilot</a>
                    <a href="{{ url_for('artwork_resizer_page') }}" class="sidebar-link{% if request.endpoint == 'artwork_resizer_page' %} active{% endif %}">Artwork Resizer</a>
                    <a href="{{ url_for('video_resizer_page') }}" class="sidebar-link{% if request.endpoint == 'video_resizer_page' %} active{% endif %}">Video Resizer</a>
                    <a href="{{ url_for('seo_copy_page') }}" class="sidebar-link{% if request.endpoint == 'seo_copy_page' %} active{% endif %}">SEO Copy</a>
                    <a href="{{ url_for('bios_page') }}" class="sidebar-link{% if request.endpoint == 'bios_page' %} active{% endif %}">Bio Manager</a>
                </div>
```

- [ ] **Step 2: Commit**

```bash
git add release_manager/templates/base.html
git commit -m "feat: add Bio Manager to sidebar navigation"
```

---

### Task 7: End-to-End Test

**Files:** No new files -- manual verification

- [ ] **Step 1: Run the app**

```bash
cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python3 -m release_manager.webapp
```

- [ ] **Step 2: Verify page loads**

Visit `http://localhost:5001/bios`. Check:
- Sidebar shows "Bio Manager" link under Tools
- All 7 platform cards render with current bios
- Character counters show correct counts
- Artist Variables section is collapsible

- [ ] **Step 3: Test manual editing**

1. Edit a Bandcamp bio in the textarea. Click "Save Edit". Refresh. Verify it persisted.
2. Click "Copy" on a bio. Paste in a text editor. Verify text is correct.

- [ ] **Step 4: Test generate flow**

1. Click "Generate All Bios"
2. Verify: generated bios appear on the right side of each card
3. Verify: character counters update for generated bios

- [ ] **Step 5: Test Use This / Undo / Applied**

1. Click "Use This" on a generated bio. Verify: left side textarea updates.
2. Click "Undo". Verify: previous bio restored.
3. Click "Mark Applied". Verify: button turns green with checkmark.

- [ ] **Step 6: Test artist variables**

1. Open Artist Variables section
2. Add a keyword, remove a label
3. Click "Save Variables". Refresh. Verify changes persisted.

- [ ] **Step 7: Test "Edit on Platform" links**

Click "Edit on Bandcamp" link. Verify it opens `https://inchofshadow.bandcamp.com/settings` in a new tab.

- [ ] **Step 8: Final commit if needed**

```bash
git add -A
git commit -m "fix: address issues found during Bio Manager testing"
```
