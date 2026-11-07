---
name: bio
description: Generate, tweak, check, and compare artist bios across all platforms (Bandcamp, Spotify, SoundCloud, YouTube, RA, Apple Music). Use when the user mentions bios, artist description, profile text, or wants to update platform bios.
argument-hint: [generate|check|compare|soundcloud|spotify|bandcamp|youtube|ra|apple|or free text instruction]
---

# Bio Manager -- Conversational Interface

Manage Inch of Shadow artist bios across 7 platforms. Generate, tweak, quality-check, and compare.

## Platforms and limits

| Platform | Char Limit | Key Rules |
|----------|-----------|-----------|
| Bandcamp | 400 | SEO-optimized, genre keywords |
| Spotify | 1,500 | NLP-categorized, mood keywords, paragraph format |
| SoundCloud | 4,000 | Casual, DJ audience, booking email, no text links |
| YouTube | 1,000 | Streaming/social links as text, booking email |
| RA Intro | 256 | Brief artist summary |
| RA Full | No limit | Expanded sound, history, releases. Must NOT repeat RA Intro |
| Apple Music | No limit | First-person, conversational |

## Key files

- `artist_profile.json` (PROJECT ROOT) -- single source of truth. Holds BOTH the artist variables (keywords, labels, venues, collaborators, booking_email) AND the stored bios under the `bios` key (read/write). This is the file `bio_manager.py` actually uses (`PROFILE_PATH = PROJECT_ROOT / "artist_profile.json"`). There is no `release_manager/bios/` directory.
- `release_manager/seo_platform_specs.json` -- platform rules and character limits (read)
- `release_manager/bio_manager.py` -- generation logic and Claude API call (reference for prompt structure)

## Hard rules

- **NEVER** mention Software Zero Records in any bio
- Double Figure is a prior band (duo) Amir is part of. Include it ONLY in the Spotify, Apple Music, and YouTube bios, phrased as "one half of the band Double Figure". Do NOT mention it in Bandcamp, SoundCloud, or RA bios
- Never use a double dash or em dash in bio copy (single dash with spaces, or a new sentence)
- Respect all character limits strictly
- Booking email: inchofshadow@gmail.com
- No emojis unless user requests
- Maintain consistent voice across platforms (use current Spotify bio as voice reference)

## Step 1: Parse intent

Read `$ARGUMENTS` and determine what the user wants:

| Argument | Action |
|----------|--------|
| (none) | **Show** -- display all current bios with char counts and applied status |
| `generate` | **Generate** -- generate all 7 platform bios |
| `[platform name]` | **Platform** -- show or generate bio for that specific platform |
| `check` | **Check** -- quality audit across all bios |
| `compare` | **Compare** -- side-by-side current vs last generated |
| Any other text | **Tweak** -- natural language instruction to modify specific bio(s) |

## Action: Show

1. Read `artist_profile.json`
2. For each platform, display:
   - Platform name
   - Character count / limit (e.g., "342 / 400")
   - Applied status + date (if tracked)
   - The bio text
3. If a specific platform is named in `$ARGUMENTS`, show only that one

## Action: Generate

1. Read artist profile from `artist_profile.json` (keywords, labels, venues, booking email)
2. Read the latest release from `releases/` directory for context (title, genre, date)
3. Read current Spotify bio as voice reference
4. Read platform specs from `release_manager/seo_platform_specs.json`
5. Reference the prompt structure in `release_manager/bio_manager.py` -- use the same system prompt and per-platform rules
6. Call Claude API to generate bios for all 7 platforms (or just the requested one)
7. Display each generated bio with character count
8. Ask user which to save: "Save all?", "Save [specific platforms]?", or "Discard?"
9. Save accepted bios to `artist_profile.json`

## Action: Check

1. Read all current bios from `artist_profile.json`
2. Read artist profile for current keywords
3. Check each bio for:
   - **Limit exceeded:** character count > platform limit
   - **Forbidden terms:** "Software Zero" appears anywhere
   - **Keywords missing:** current artist keywords not present
   - **Booking email missing:** SoundCloud and YouTube should include inchofshadow@gmail.com
   - **Empty bios:** platform has no bio at all
   - **RA repetition:** RA Full should not repeat RA Intro verbatim
4. Report all issues found, grouped by platform
5. If no issues: "All bios pass quality checks."

## Action: Compare

1. Read current bios and most recently generated bios (if available in `artist_profile.json`)
2. For each platform, show:
   - Current bio (with char count)
   - Generated bio (with char count)
   - Key differences: length change, keywords added/removed, tone shift
3. If no generated bios exist, suggest running `/bio generate` first

## Action: Tweak

1. Parse which platform(s) the instruction targets (e.g., "make the bandcamp bio mention the new EP" -> Bandcamp)
2. If unclear which platform, ask
3. Read the current bio for that platform
4. Read artist profile and platform specs for context
5. Call Claude API with:
   - The current bio
   - The user's instruction as modification guidance
   - Platform rules and character limit
6. Display the tweaked bio with char count
7. Ask to save or iterate further

## Notes

- The web UI at `/bios` handles versioning (undo), applied-status tracking, and side-by-side visual comparison. This skill complements it for faster conversational iteration.
- When saving bios, preserve the existing JSON structure in `artist_profile.json` -- only update the platforms the user approved.
- If `artist_profile.json` or `artist_profile.json` doesn't exist, warn the user and suggest setting up via the web UI first.
