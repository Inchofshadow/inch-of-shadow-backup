# Bio Manager — Design Spec

**Date:** 2026-04-08
**Status:** Design
**Location:** Release Manager > /bios (sidebar under Tools)

---

## Problem

Updating artist bios across 6 platforms (Bandcamp, Spotify, SoundCloud, YouTube, RA, Apple Music) is manual and tedious. When keywords, releases, or links change, each platform needs updating individually. There's no central place to see what's currently live on each platform or to generate updated bios.

## Solution

A Bio Manager page in the Release Manager that:
1. Shows current bios for all platforms at all times (editable)
2. Generates AI-drafted bios per platform using artist variables and keywords
3. Displays current vs generated side-by-side for comparison
4. Provides copy buttons, undo, and "Applied" confirmation per platform
5. Links directly to each platform's edit page

## Data Storage

### New File: `artist_profile.json` (project root)

Stores artist-level data separate from release-level data. Other tools (SEO Copy, Promotion Engine) can reference this in the future.

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
      "current": "",
      "previous": null,
      "char_limit": 400,
      "applied": false,
      "applied_date": null
    },
    "spotify": {
      "current": "",
      "previous": null,
      "char_limit": 1500,
      "applied": false,
      "applied_date": null
    },
    "soundcloud": {
      "current": "",
      "previous": null,
      "char_limit": 4000,
      "applied": false,
      "applied_date": null
    },
    "youtube": {
      "current": "",
      "previous": null,
      "char_limit": 1000,
      "applied": false,
      "applied_date": null
    },
    "ra_intro": {
      "current": "",
      "previous": null,
      "char_limit": 256,
      "applied": false,
      "applied_date": null
    },
    "ra_full": {
      "current": "",
      "previous": null,
      "char_limit": null,
      "applied": false,
      "applied_date": null
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

### Field Definitions

- **current**: The bio text as it should be on the platform right now.
- **previous**: The last version before the current one. Used for undo. Set when "Use This" is clicked.
- **char_limit**: Platform character limit. `null` means no documented limit.
- **applied**: Whether the user has confirmed they pasted this bio into the actual platform.
- **applied_date**: ISO timestamp of when "Applied" was clicked.

### Excluded Labels

The artist profile must never include Software Zero Records in the `labels` array. This is a hard rule.

## Page Layout

### Route: `/bios`

Sidebar placement: under "Tools" group, after "SEO Copy".

### Sections

**1. Artist Variables (collapsible)**

Editable fields for keywords, labels, venues, links. Changes save via API call on blur. These variables feed into bio generation.

- Keywords: tag-style input (add/remove, like keyword clusters UI)
- Labels: tag-style input
- Venues: tag-style input
- Links: labeled text inputs per platform
- Booking email: text input

**2. Generate Button**

"Generate All Bios" button. Calls Claude Haiku. Generates all 7 bio variants at once. Shows loading state. Cost: ~$0.003-0.005.

**3. Platform Cards (stacked, one per platform)**

Each card shows:

```
┌─ Bandcamp (400 chars) ──────────── [Edit on Bandcamp ↗] ─┐
│                                                            │
│  Current Bio                 │  Generated Bio              │
│  ┌────────────────────┐      │  ┌────────────────────┐    │
│  │ editable textarea  │      │  │ read-only display   │    │
│  │ with char counter  │      │  │ with char counter   │    │
│  └────────────────────┘      │  └────────────────────┘    │
│  [Save Edit] [Copy]          │  [Use This] [Copy]         │
│                                                            │
│  [Undo]  [Applied ✓]                                      │
└────────────────────────────────────────────────────────────┘
```

**Left side (Current Bio):**
- Editable textarea showing the current bio
- Character counter (with over-limit warning matching existing `.char-counter` pattern)
- "Save Edit" button -- saves manual edits to `artist_profile.json`
- "Copy" button -- copies text to clipboard

**Right side (Generated Bio):**
- Hidden until "Generate All Bios" is clicked
- Read-only display of the AI-generated bio
- Character counter
- "Use This" button -- moves generated bio to current side, saves previous for undo
- "Copy" button -- copies text to clipboard

**Bottom row:**
- "Undo" button -- reverts current to previous. Disabled when no previous exists.
- "Applied" button -- user clicks after pasting into the platform. Turns green with checkmark. Stores timestamp.

**Platform header:**
- Platform name + character limit
- "Edit on [Platform]" link -- opens the platform's edit page in a new tab

### Platform Display Order

1. Bandcamp (400 chars)
2. Spotify (1,500 chars)
3. SoundCloud (4,000 chars)
4. YouTube (1,000 chars)
5. RA - Intro (256 chars)
6. RA - Full Bio (no limit)
7. Apple Music (no limit)

RA gets two cards (intro and full bio) because they have separate fields that must not repeat content.

## Bio Generation

### New File: `release_manager/bio_manager.py`

Same architecture as `seo_copy_generator.py` and `keyword_cluster_generator.py`:
- Uses Claude Haiku (`claude-haiku-4-5-20251001`)
- Same API key (`ANTHROPIC_API_KEY` from `.env`)
- Cost: ~$0.003-0.005 per generation

### What Gets Sent to Claude

1. **Artist variables** from `artist_profile.json`: keywords, labels, venues, collaborators, location
2. **Latest release** metadata from `releases/` directory (most recent by date)
3. **Platform specs**: character limits and formatting rules per platform
4. **Current bios** as voice/style reference -- Claude should maintain the established voice
5. **Platform-specific rules**:
   - Bandcamp: 400 chars, Google-indexed, genre keywords matter
   - Spotify: 1,500 chars, NLP reads for categorization, mood keywords important
   - SoundCloud: 4,000 chars, casual, DJ/producer audience, no text links (icon links handle it), include booking email
   - YouTube: 1,000 chars, include streaming and social links as text
   - RA intro: 256 chars, brief artist summary
   - RA full: don't repeat intro, expand on sound/history/releases
   - Apple Music: first person, conversational, no press language, no exclamation points

### System Prompt

```
You are a bio writer for a Berlin-based electronic music artist. Write platform-specific
artist bios that maintain a consistent voice while respecting each platform's conventions
and character limits. The voice is: atmospheric, evocative, understated. Not a press release.
Not marketing copy. Reads like an artist describing their own world.

Never mention Software Zero Records.
Use "Double Figure band" (keep "band").
```

### Claude Output Format

Returns JSON with all 7 bio variants:

```json
{
  "bandcamp": "...",
  "spotify": "...",
  "soundcloud": "...",
  "youtube": "...",
  "ra_intro": "...",
  "ra_full": "...",
  "apple_music": "..."
}
```

## API Endpoints

### 1. `GET /bios` -- Page route
Loads `artist_profile.json`, lists latest release, renders template.

### 2. `POST /api/bios/generate` -- Generate bios
Calls Claude with artist variables + latest release. Returns generated bios. Does NOT save to `artist_profile.json` (user must click "Use This" per platform).

Response: `{ "ok": true, "bios": { "bandcamp": "...", ... } }`

### 3. `PUT /api/bios/save` -- Save a bio
Body: `{ "platform": "bandcamp", "bio": "...", "source": "edit|generate" }`

If source is "generate" (Use This was clicked): moves current to previous, sets new current.
If source is "edit" (Save Edit was clicked): updates current directly, does not touch previous.

Response: `{ "ok": true }`

### 4. `PUT /api/bios/undo` -- Undo a bio
Body: `{ "platform": "bandcamp" }`

Swaps current and previous.

Response: `{ "ok": true }`

### 5. `PUT /api/bios/applied` -- Mark as applied
Body: `{ "platform": "bandcamp" }`

Sets `applied: true` and `applied_date` to now.

Response: `{ "ok": true }`

### 6. `PUT /api/bios/profile` -- Update artist variables
Body: `{ "keywords": [...], "labels": [...], "venues": [...], "links": {...}, "booking_email": "..." }`

Updates `artist_profile.json` variables (not bios).

Response: `{ "ok": true }`

## Files Changed

| File | Change |
|------|--------|
| `artist_profile.json` | New. Artist-level data + bios storage. |
| `release_manager/bio_manager.py` | New. Bio generation logic, profile load/save helpers. |
| `release_manager/webapp.py` | Add `/bios` route + 5 API endpoints. |
| `release_manager/templates/bios.html` | New. Bio Manager page. |
| `release_manager/static/css/pages/bios.css` | New. Styles for bio cards, side-by-side layout. |
| `release_manager/templates/base.html` | Add "Bio Manager" link to sidebar under Tools. |

## What This Does NOT Include

- Automatic platform updates (no API access to update bios on Bandcamp, Spotify, etc.)
- Bio version history beyond one undo level
- Scheduled regeneration
- Per-release bio variants (this is artist-level, not release-level)
