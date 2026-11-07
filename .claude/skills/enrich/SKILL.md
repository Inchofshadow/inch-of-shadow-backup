---
name: enrich
description: Run Scene Intelligence enrichment scripts (Discogs, SoundCloud, Spotify, YouTube, URLs, emails, classify). Use when the user wants to enrich contacts, update SI data, or run enrichment passes.
argument-hint: [--discogs|--sc|--spotify|--yt|--urls|--emails|--classify|--all]
---

> **PARKED 2026-11-07 (strategy review M5, Amir's yes):** the enrichment scripts live in `archive/si-discovery/` now. The final "Push to Sheets?" step is retired: Amir decided no more pushes, the sheet stays as it is. Run any step only when Amir asks for it in that task; never on a routine.

# Enrich Scene Intelligence Contacts

Run one or more SI enrichment scripts from the project root and report results.

## Step 1: Parse flags

Read `$ARGUMENTS` and determine which scripts to run:

| Flag | Script | What it does |
|------|--------|-------------|
| `--discogs` | `python3 archive/si-discovery/re_enrich_discogs.py` | Second-pass Discogs with improved name handling |
| `--soundcloud` or `--sc` | `python3 archive/si-discovery/enrich_soundcloud.py` | SoundCloud resolve + search (DJs only by default) |
| `--spotify` | `python3 archive/si-discovery/enrich_spotify.py` | Spotify resolve + search (DJs only by default) |
| `--youtube` or `--yt` | `python3 archive/si-discovery/enrich_youtube.py` | YouTube Phase 1 only (direct, cheap). Do NOT run `--search` unless user explicitly asks -- costs 100 API units per contact |
| `--urls` | `python3 archive/si-discovery/enrich_urls.py` | Social links from Discogs/MusicBrainz/Wikidata |
| `--emails` | `python3 archive/si-discovery/scrape_label_emails.py` | Scrape label websites for demo emails |
| `--classify` | `python3 archive/si-discovery/classify_subtypes.py` | Re-run sub-type classification + relevance scoring |
| `--all` | All of the above, in the order listed | Full enrichment pass |

If no flags are provided, ask the user which enrichments to run. List the options.

## Step 2: Run scripts

**HARD RULE - pre-announce API calls (added 2026-07-05, audit item 21):** before running
ANY script that hits the SoundCloud API (`enrich_soundcloud.py`, and `enrich_urls.py` when
it resolves SC links), state the estimated call count (roughly 1-3 calls per contact in
scope) and WAIT for the user's confirmation. Same spirit for Spotify/YouTube: announce
scope before firing. Never start API-calling scripts as a silent side effect of this skill.

Run each selected script sequentially from the project root directory. They all modify `scene_intelligence/enriched_contacts.json` in place -- do NOT run them in parallel.

**Pass-through flags:**
- If user says "all categories" or `--all-categories`, pass `--all` to `enrich_soundcloud.py` and `enrich_spotify.py` (otherwise they default to DJs only)
- If user asks for YouTube search (Phase 2), warn about API quota cost first (100 units per search, 100k/day limit), then pass `--search` to `enrich_youtube.py`
- If user asks for dry-run on classify, pass `--dry-run` to `classify_subtypes.py`

## Step 3: Report summary

After all scripts complete, report:
- Which scripts ran
- Key numbers from each (contacts enriched, new matches found, errors)
- Total contacts in `enriched_contacts.json`

## Step 4: Offer Sheets push

Ask: "Push to Sheets?" If yes, run `python3 scene_intelligence/push_to_sheets.py` and report the result.

## Notes

- All scripts require API keys in `.env` (DISCOGS_TOKEN, SPOTIFY_CLIENT_ID/SECRET, SOUNDCLOUD_CLIENT_ID/SECRET, YOUTUBE_API_KEY)
- If a script fails (missing key, network error), report the error and continue with remaining scripts
- YouTube Phase 2 search is expensive -- always warn before running it
- Spotify Related Artists API returns 403 in Dev Mode -- this is a known limitation, not a bug
