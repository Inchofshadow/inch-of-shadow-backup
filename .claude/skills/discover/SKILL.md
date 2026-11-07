---
name: discover
description: Discover new contacts via network crawling (Spotify Related Artists, YouTube Subscriptions, Discogs Label Rosters) and extraction sources (Rekordbox, Resident Advisor). Use when the user wants to find new contacts, grow the database, or run discovery.
argument-hint: [--spotify|--yt|--discogs|--rekordbox|--ra|--dry-run|--limit N|--all]
---

> **PARKED 2026-11-07 (strategy review M5, Amir's yes):** the discovery scripts live in `archive/si-discovery/` now (`extract_ra.py` stays in `scene_intelligence/`). The last step's Google Sheets push is retired: Amir decided no more pushes, the sheet stays as it is. Run any step only when Amir asks for it in that task; never on a routine.

# Discover New Contacts

Find new contacts by crawling network graphs and extraction sources.

## Step 1: Parse flags

Read `$ARGUMENTS` and determine which discovery sources to run:

| Flag | Script | What it does |
|------|--------|-------------|
| `--spotify` | `python3 archive/si-discovery/discover_contacts.py --spotify` | Related Artists (3+ seed threshold). Note: API returns 403 in Dev Mode -- warn user |
| `--youtube` or `--yt` | `python3 archive/si-discovery/discover_contacts.py --youtube` | YouTube Subscriptions (2+ seed threshold) |
| `--discogs` | `python3 archive/si-discovery/discover_contacts.py --discogs` | Label Rosters (2+ label threshold) |
| `--rekordbox` | `python3 archive/si-discovery/extract_rekordbox.py` | Extract from Rekordbox XML library |
| `--ra` | `python3 scene_intelligence/extract_ra.py` | Resident Advisor GraphQL (DJs + labels by genre) |
| `--dry-run` | Pass to `discover_contacts.py` | Preview without saving |
| `--limit N` | Pass to `discover_contacts.py` | Cap new contacts at N (default 100) |
| `--all` | Spotify + YouTube + Discogs | All 3 network crawl phases |

If no flags are provided, run all 3 discovery phases (Spotify + YouTube + Discogs) with default limit.

## Step 2: Check prerequisites

- If `--rekordbox`: check that `data/rekordbox_library.xml` exists. If missing, tell the user: "Rekordbox XML not found. Export from Rekordbox first: File > Export Collection in XML format, save to `data/rekordbox_library.xml`"
- If `--spotify`: warn that Spotify Related Artists API returns 403 in Dev Mode (known limitation). Ask if user wants to proceed anyway.

## Step 3: Run scripts

Run selected scripts sequentially from the project root.

**Important notes:**
- `discover_contacts.py` appends new contacts to `enriched_contacts.json`
- `extract_rekordbox.py` also appends to `enriched_contacts.json`
- `extract_ra.py` outputs to `scene_intelligence/ra_contacts.json` (separate file) -- inform user this needs manual merge or they can review and add selectively

## Step 4: Report summary

After all scripts complete, report:
- New contacts found (count by source)
- Top discoveries ranked by frequency (show top 10-15)
- Source breakdown (which APIs/sources contributed)
- Total contacts now in database

## Step 5: Offer post-processing

Ask: "Run classify + push to Sheets?" If yes:
1. Run `python3 archive/si-discovery/classify_subtypes.py` (sub-types + scoring)
2. Run `python3 scene_intelligence/push_to_sheets.py` (publish to Sheets)

## Notes

- Default limit is 100 new contacts to prevent noise
- Spotify discovery requires SPOTIFY_CLIENT_ID/SECRET in `.env`
- YouTube discovery requires YOUTUBE_API_KEY in `.env`
- Discogs discovery requires DISCOGS_TOKEN in `.env`
- Rekordbox requires fresh XML export (data can be stale)
- RA extraction hits GraphQL API directly (no key needed, but rate-limited)
