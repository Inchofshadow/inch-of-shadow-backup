---
name: release-prep
description: Prepare everything needed for a new music release -- SoundCloud description, tags, cross-platform SEO copy, premiere contacts, and release checklist. Use when the user mentions releasing a track, uploading a set, or preparing a release.
argument-hint: [track/release name]
---

# Release Prep for Inch of Shadow

You are preparing a release for Inch of Shadow. Two lanes: songs (guitars and voice, the main line, not public yet) and the electronic lane (dark disco, acid, electro, EBM, Berlin underground).

## Step 1: Find or create the release JSON

Check if a release JSON already exists in `releases/` that matches $ARGUMENTS (by title or slug).
- If it exists, read it and use the metadata already filled in (don't re-ask for info that's there).
- If it doesn't exist, you'll create one after gathering info.

## Step 2: Gather information

Ask the user for any missing details (don't assume):
- **What is it?** Track, remix, DJ set, EP?
- **Title** -- full title including featured artists, remixer, venue if a set
- **Genre/vibe** -- dark disco, acid, EBM, techno, slowmo, etc.
- **Tracklist** (if DJ set)
- **BPM and key** (if known)
- **Event/venue** (if live recording)
- **Date** of recording or release
- **Collaborators** -- remixer, featured artists, label
- **Is there a video?** YouTube link?
- **Which platforms** is this going on? (SoundCloud, Bandcamp, Spotify, etc.)
- **Is there a premiere planned?** If yes, with whom?

## Step 3: Generate outputs

Once you have the details, generate ALL of the following:

### SoundCloud
- **Track title** (formatted: `Artist @ Event -- Description | City Date` for sets, or `Artist - Title (Remix)` for tracks)
- **Description** -- atmospheric opening line about the mood/vibe, tracklist if DJ set, video link if exists, booking email at end. NOT a press release. Human and evocative.
- **Tags** -- 5 specific tags (e.g., `darkdisco`, `acid`, `ebm`, `djset`, `berlin`). Never use generic tags like `electronic` or `music`.

### Instagram
- **Caption** -- keyword-rich, evocative, max 125 chars visible before "...more". No hashtags in caption body.
- **Hashtags** -- exactly 5, niche and scene-specific (e.g., `#darkdisco`, `#acidtechno`, `#berlinmusic`). No generic ones.

### YouTube
Do NOT invent title options. The title format, description order, credits, tags and hashtags
are fixed in `../youtube/PLAYBOOK.md` section 5.4, and
`python3 ../youtube/tools/yt_release.py <slug> --draft` writes the file from the release
record. Your part is the one sentence on how the track sounds (never what it means) and the
lead link, in place of the [TODO lines.

### Bandcamp (if applicable)
- **About text** (max 450 chars) -- personal, fan-facing, story/mood/inspiration
- **Tags** -- 10 tags, mix of genre + mood + scene

### Beatport
- Not used for new releases (bridge plan v2). Skip unless Amir adds it back.

## Step 4: Save to release JSON

Save all generated copy into the release JSON file at `releases/<slug>.json` under a `seo_copy` key:

```json
{
  "seo_copy": {
    "generated_at": "2026-03-17T14:30:00",
    "tone": "authentic",
    "soundcloud": {
      "title": "...",
      "description": "...",
      "tags": ["darkdisco", "acid", "ebm", "berlin", "djset"]
    },
    "instagram": {
      "caption": "...",
      "hashtags": ["darkdisco", "acidtechno", "berlinmusic", "ebm", "underground"]
    },
    "youtube": {
      "titles": ["...", "...", "..."],
      "description": "..."
    },
    "bandcamp": {
      "about": "...",
      "tags": ["...", "..."]
    },
    "beatport": {
      "description": "..."
    },
    "premiere_contacts": [
      {"name": "...", "url": "...", "reason": "..."}
    ]
  }
}
```

Only include platforms that are relevant to this release. Merge into the existing JSON -- don't overwrite other fields.

If the release JSON doesn't exist yet, create one with the full schema (copy structure from an existing release in `releases/`).

**Important:** After saving, tell the user the file path and that they can view/edit it in the Release Manager web UI.

## Step 5: Premiere contacts

Read `scene_intelligence/enriched_contacts.json` and find the top 5 premiere/media contacts for this release based on:
- Contacts with sub_type "premiere" or "radio" or "press"
- Genre match (compare release genre to contact's genre_main/genre_sub)
- Relevance score (higher = better)

Save them in the `seo_copy.premiere_contacts` array and also display them to the user with name, platform, URL, and a one-line reason why they're a good fit.

## Step 6: Release checklist

Based on `plans/seo-strategy.md` section 9, output a tailored checklist for this specific release. Only include platforms the user is releasing on. Include timing notes (e.g., "Spotify pitch needed 31-40 days before release").

If the release JSON already has a `checklist`, don't overwrite it -- just show the user what's missing.

## Style rules
- Write like a human, not a press release
- Bio mentions: "Inch of Shadow", Berlin, relevant labels (MM Discos, Stereo Society, NaNa Disc)
- Booking email: inchofshadow@gmail.com
- No emojis unless user requests
- Respect all character limits from `release_manager/seo_platform_specs.json`
