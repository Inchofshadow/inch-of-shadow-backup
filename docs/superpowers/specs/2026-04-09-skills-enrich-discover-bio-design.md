# Skills Design: /enrich, /discover, /bio

**Date:** 2026-04-09
**Status:** Approved

## Overview

Three new conversational skills for the Inch of Shadow project, wrapping existing Scene Intelligence scripts and Bio Manager functionality into quick slash commands.

All skills follow the existing skill format (YAML frontmatter + markdown instructions) used by `/sync` and `/release-prep`.

---

## Skill 1: /enrich

### Purpose
Run one or more SI enrichment scripts and get a summary without remembering individual commands and flags.

### Location
`.claude/skills/enrich/SKILL.md`

### Arguments
Parsed from `$ARGUMENTS`:

| Flag | Script | Notes |
|------|--------|-------|
| `--discogs` | `re_enrich_discogs.py` | Second-pass Discogs (improved name handling) |
| `--soundcloud` / `--sc` | `enrich_soundcloud.py` | Two-phase: resolve URLs + search by name |
| `--spotify` | `enrich_spotify.py` | Two-phase: resolve URLs + search by name |
| `--youtube` / `--yt` | `enrich_youtube.py` | Phase 1 only by default (cheap). Add `--search` for Phase 2 (expensive!) |
| `--urls` | `enrich_urls.py` | Social links from Discogs/MusicBrainz/Wikidata |
| `--emails` | `scrape_label_emails.py` | Scrape label websites for demo emails |
| `--classify` | `classify_subtypes.py` | Re-run sub-type classification + relevance scoring |
| `--all` | All of the above | In sequence |
| (none) | Interactive | Ask user which to run |

### Behavior
1. Parse flags from `$ARGUMENTS`
2. If no flags, ask user which enrichments to run (list options)
3. Run each selected script sequentially from project root (they all modify `enriched_contacts.json` in place)
4. After each script, capture and summarize its output (contacts enriched, new matches, errors)
5. After all scripts complete, show combined summary
6. Ask "Push to Sheets?" -- if yes, run `python3 scene_intelligence/push_to_sheets.py`

### Script pass-through flags
- `enrich_soundcloud.py`: pass `--all` if user wants all categories (not just DJs)
- `enrich_spotify.py`: pass `--all` if user wants all categories
- `enrich_youtube.py`: only run Phase 1 (direct) by default. Warn before Phase 2 (`--search`) due to API quota cost (100 units per search)
- `classify_subtypes.py`: support `--dry-run` pass-through

### Notes
- All scripts require `.env` with API keys (DISCOGS_TOKEN, SPOTIFY_CLIENT_ID/SECRET, SOUNDCLOUD_CLIENT_ID/SECRET, YOUTUBE_API_KEY)
- YouTube API has 100,000 units/day quota -- Phase 2 search is expensive, always warn
- Scripts run sequentially because they all read/write `enriched_contacts.json`

---

## Skill 2: /discover

### Purpose
Find new contacts via network crawling and extraction sources.

### Location
`.claude/skills/discover/SKILL.md`

### Arguments
Parsed from `$ARGUMENTS`:

| Flag | Script | Notes |
|------|--------|-------|
| `--spotify` | `discover_contacts.py --spotify` | Related Artists (3+ seed threshold) |
| `--youtube` / `--yt` | `discover_contacts.py --youtube` | YouTube Subscriptions (2+ seed threshold) |
| `--discogs` | `discover_contacts.py --discogs` | Label Rosters (2+ label threshold) |
| `--rekordbox` | `extract_rekordbox.py` | Requires fresh XML at `data/rekordbox_library.xml` |
| `--ra` | `extract_ra.py` | Resident Advisor GraphQL API |
| `--dry-run` | Pass to `discover_contacts.py` | Preview without saving |
| `--limit N` | Pass to `discover_contacts.py` | Cap at N new contacts (default 100) |
| `--all` | Spotify + YouTube + Discogs | All 3 discovery phases (not Rekordbox/RA) |
| (none) | All 3 discovery phases | Same as `--all` |

### Behavior
1. Parse flags from `$ARGUMENTS`
2. If `--rekordbox`, check `data/rekordbox_library.xml` exists. If missing, warn user they need to export from Rekordbox first (File > Export Collection in XML format)
3. Run selected scripts sequentially
4. Report summary: new contacts found, top discoveries ranked by frequency, source breakdown
5. Ask "Run classify + push to Sheets?" -- if yes, run `classify_subtypes.py` then `push_to_sheets.py`

### Notes
- `discover_contacts.py` uses Spotify Related Artists API which returns 403 in Dev Mode -- this is a known limitation, warn if `--spotify` selected
- `extract_ra.py` outputs to `ra_contacts.json` (separate file) -- needs manual merge or note to user
- `extract_rekordbox.py` appends directly to `enriched_contacts.json`
- Default `--limit` is 100 to prevent noise

---

## Skill 3: /bio

### Purpose
Conversational bio management -- generate, tweak, check, compare across all 7 platforms. Complements the web UI at `/bios` with faster iteration and quality checks.

### Location
`.claude/skills/bio/SKILL.md`

### Arguments
Parsed from `$ARGUMENTS` (flexible, natural language):

| Argument | Action |
|----------|--------|
| (none) | Show current bios for all platforms with char counts and applied status |
| `generate` | Generate all 7 platform bios via Claude API |
| `[platform]` | Show or generate bio for a specific platform (e.g., `soundcloud`, `spotify`, `bandcamp`, `youtube`, `ra`, `apple`) |
| `check` | Quality check: character limits, keyword coverage, Software Zero rule, missing bios |
| `compare` | Side-by-side current vs generated for all platforms |
| Free text | Natural language instruction (e.g., "make bandcamp bio mention new EP", "regenerate RA intro darker") |

### Platforms and limits

| Platform | Char Limit | Key Rules |
|----------|-----------|-----------|
| Bandcamp | 400 | SEO-optimized, genre keywords |
| Spotify | 1,500 | NLP-categorized, mood keywords, paragraph format |
| SoundCloud | 4,000 | Casual, DJ audience, booking email, no text links |
| YouTube | 1,000 | Streaming/social links as text, booking email |
| RA Intro | 256 | Brief artist summary |
| RA Full | No limit | Expanded sound, history, releases, non-repetitive with intro |
| Apple Music | No limit | First-person, conversational |

### Behavior

**Show (`/bio` or `/bio [platform]`):**
1. Read bios from `release_manager/bios/artist_bios.json`
2. Read artist profile from `release_manager/bios/artist_profile.json`
3. Display each bio with: platform name, character count / limit, applied status + date, the bio text
4. If a specific platform is requested, show only that one

**Generate (`/bio generate` or `/bio [platform] generate`):**
1. Read artist profile (keywords, labels, venues, booking email)
2. Read latest release from `releases/` for context
3. Read current Spotify bio as voice reference
4. Read platform specs from `release_manager/seo_platform_specs.json`
5. Call Claude API (or `bio_manager.py` generate function) with all context
6. Show generated bios with char counts
7. Ask user which to save (all, specific platforms, or none)
8. Save accepted bios to `artist_bios.json`

**Check (`/bio check`):**
1. Read all current bios
2. Check each for:
   - Character limit exceeded
   - "Software Zero" mentioned (forbidden)
   - Current keywords present
   - Booking email present (where required: SoundCloud, YouTube)
   - Empty / missing bios
3. Report issues found, or "all clear"

**Compare (`/bio compare`):**
1. Read current bios and most recent generated bios
2. Show side-by-side for each platform
3. Highlight differences (length, keywords, tone)

**Natural language tweaks (`/bio [instruction]`):**
1. Parse which platform(s) the instruction targets
2. Read current bio for that platform
3. Regenerate with user instruction as additional guidance
4. Show result with char count
5. Ask to save or iterate

### Hard Rules
- NEVER mention Software Zero Records in any bio
- Use "Double Figure" for band references
- Respect all character limits
- Maintain consistent voice across platforms
- Booking email: inchofshadow@gmail.com

### Files
- `release_manager/bios/artist_bios.json` -- stored bios (read/write)
- `release_manager/bios/artist_profile.json` -- artist variables (read)
- `release_manager/seo_platform_specs.json` -- platform rules and limits (read)
- `release_manager/bio_manager.py` -- generation logic (reference)

---

## Shared Design Decisions

1. **Sequential execution** -- all scripts modify `enriched_contacts.json` in place, cannot run in parallel
2. **Summary reporting** -- every skill ends with a clear summary of what happened
3. **Optional Sheets push** -- never automatic, always ask
4. **Existing skill format** -- YAML frontmatter (`name`, `description`, `argument-hint`) + markdown body with numbered steps
5. **Error handling** -- if a script fails (missing API key, network error), report the error and continue with remaining scripts
