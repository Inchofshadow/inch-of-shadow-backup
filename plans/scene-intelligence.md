# Tool 1 -- Scene Intelligence Engine

**Location:** `scene_intelligence/`
**Status:** Partial
**Last updated:** 2026-03-16
**Purpose:** Research pipeline for the Berlin electronic music scene. Extract contacts (labels, venues, DJs, blogs) from data exports, enrich via APIs, push to Google Sheets.

---

## Data Pipeline

```
Raw Sources (6)                    Enrichment APIs (6)         Output
─────────────────                  ─────────────────           ──────
Instagram ZIP (600+ following)     Discogs (28.9% matched)     enriched_contacts.json (920)
YouTube ZIP (299 subscriptions)    Spotify (6.6% matched)      Google Sheets (9 tabs)
SoundCloud (86 curated)            YouTube Data API (9.1%)     Backups (auto, max 20)
Resident Advisor (GraphQL)         SoundCloud API (59.7%)
ChatGPT PDF (13 distributors)      MusicBrainz (optional)
Rekordbox XML (2.5 MB library)     Wikidata SPARQL (optional)
                                   ↓
                          raw_contacts.json (1,122 entries)
                                   ↓ dedup + classify
                          enriched_contacts.json (920 unique)
                                   ↓
                          Google Sheets (9 tabs, ~20s push)
```

---

## Contact Database -- Current Numbers

| Category | Count | % | Default Score |
|----------|-------|---|---------------|
| DJ | 623 | 67.7% | 2 |
| Label | 181 | 19.7% | 2 |
| Media | 41 | 4.5% | 2 |
| Venue | 35 | 3.8% | 3 |
| Promoter | 19 | 2.1% | 3 |
| Platform | 10 | 1.1% | 3 |
| Distributor | 9 | 1.0% | 3 |
| Other | 2 | 0.2% | 1 |
| **Total** | **920** | | |

---

## Match Scores (genre relevance to Inch of Shadow)

| Score | Count | % | Meaning |
|-------|-------|---|---------|
| 5 | 86 | 9.3% | Perfect -- dark disco, darkwave, acid, electro, EBM, minimal synth |
| 4 | 14 | 1.5% | Strong -- techno, downtempo, slowmo, industrial, disco, minimal |
| 3 | 211 | 22.9% | Medium -- house, post-punk, experimental, ambient |
| 2 | 548 | 59.6% | Weak -- default for categories without genre inference |
| 1 | 60 | 6.5% | Very weak / unknown |

Genre coverage: 88.8% of contacts have genre_main (817/920).

---

## Enrichment Coverage

| Source | Contacts Enriched | Key Data Added |
|--------|-------------------|----------------|
| Discogs | 266 (28.9%) | genres, country, email (27 demo emails found), releases, labels, website |
| SoundCloud | 549 (59.7%) | user ID, followers, tracks, city, country, description |
| Spotify | 61 (6.6%) | popularity, followers, genres, Spotify URL |
| YouTube | 84 (9.1%) | subscribers, views, video count, last upload, country |
| MusicBrainz | optional | URLs, cross-reference |
| Wikidata | optional | venue capacity, location enrichment |

Additional data points:
- 27 demo emails found via Discogs
- 57 contacts with sub-type classification (media: radio/premiere/press/production/channel/shop; promoter: party/event/booking/management)
- 19 DJs cross-referenced against 181-label database (label connections)
- Relevance scoring: 0-100 on all contacts (includes SC followers + EU location bonus)
- A&R tab: 25 actionable media contacts (premiere/press/radio) with auto-filled Opportunity

---

## Scripts (15 files)

| Script | Lines | Purpose | Status |
|--------|-------|---------|--------|
| `extract_contacts.py` | 915 | Extract from 4 sources (YouTube, Instagram, ChatGPT PDF, SoundCloud). 50+ genre keywords, 100+ known account mappings, 80+ genre overrides, 40+ location overrides | Done |
| `extract_ra.py` | 294 | Resident Advisor GraphQL extractor (genre-filtered DJs + labels, 1.5s delay, 429 backoff) | Done |
| `extract_rekordbox.py` | 437 | Rekordbox XML parser (filters non-electronic, dedup, min 2 tracks) | Done |
| `enrich_contacts.py` | 340 | Discogs API enrichment (labels + DJs, email extraction, 1s rate limit) | Done |
| `re_enrich_discogs.py` | 351 | Discogs re-enrichment with cleaned names + known mappings | Done |
| `enrich_spotify.py` | 421 | Spotify Web API enrichment (Phase 1: direct URLs, Phase 2: search DJs) | Partial |
| `enrich_youtube.py` | 665 | YouTube Data API enrichment (Phase 1: direct, Phase 2: search, Phase 3: activity) | Partial |
| `enrich_soundcloud.py` | 449 | SoundCloud API enrichment (Phase 1: resolve URLs, Phase 2: search by name, 80% confidence min) | Done |
| `enrich_urls.py` | 627 | URL/social enrichment from Discogs, MusicBrainz, Wikidata (3 passes) | Partial |
| `discover_contacts.py` | 864 | Network discovery via Spotify related artists + YouTube subscriptions | Partial |
| `classify_subtypes.py` | 432 | Sub-type classification for media/promoter contacts (radio/premiere/press/party/booking etc.) | Done |
| `fetch_youtube_subs.py` | 232 | YouTube OAuth 2.0 subscription fetcher (replaces Google Takeout) | Done |
| `update_scores.py` | 59 | One-shot patch: applies category-based default scores | Done |
| `push_to_sheets.py` | 873 | Google Sheets publisher (9 tabs, formatting, rate limiter, batch API, ~20s) | Done |
| `utils.py` | 98 | Shared: dedup_key(), normalize_raw_contacts(), scoring weights | Done |

---

## Key Commands

```bash
python3 scene_intelligence/push_to_sheets.py              # push to sheet (with sync-back)
python3 scene_intelligence/push_to_sheets.py --no-sync    # push without sync-back
python3 scene_intelligence/classify_subtypes.py            # re-run sub-type classification
python3 scene_intelligence/discover_contacts.py            # discover new contacts via APIs
python3 scene_intelligence/re_enrich_discogs.py            # re-enrich Discogs data
python3 scene_intelligence/enrich_soundcloud.py            # enrich with SoundCloud data
python3 scene_intelligence/enrich_soundcloud.py --all      # enrich all categories (not just DJs)
python3 scene_intelligence/enrich_soundcloud.py --force    # re-enrich already-enriched contacts
python3 scene_intelligence/extract_rekordbox.py            # extract from Rekordbox XML
```

---

## Google Sheets Output (9 tabs)

| Tab | Contents |
|-----|----------|
| A&R Targets | Premiere, press, radio contacts |
| Labels | Demo submission targets |
| DJs | Producers + DJs |
| Venues | Clubs, festivals |
| Media | Blogs, podcasts, radio |
| Promoters | Party organizers |
| Distributors | Distribution platforms |
| Platforms | DSPs + streaming |
| All Contacts | Everything combined |

Features: frozen headers, colored bold headers, clickable hyperlinks, filter views, category + score dropdowns, promo list column, SoundCloud URL + SC Followers columns, sync-back (category/score/delete/promo_list changes sync from Sheets to JSON).

---

## API Rate Limits

| Service | Limit | Implementation |
|---------|-------|----------------|
| Discogs | 60 req/min (token) | 1s delay between calls |
| Google Sheets | 60 req/min/user | Smart rate limiter in push script |
| YouTube Data API | Project quota | Batch 50 IDs/call |
| Spotify | Variable | Client Credentials flow |
| SoundCloud | Variable | Client Credentials flow, 0.5s delay, 429 backoff |
| Resident Advisor | Custom | 1.5s delay, 30s backoff on 429 |
| MusicBrainz | Unlimited | 0.5s courtesy delay |

---

## Backup System

Auto-backup before each Sheets push. Location: `scene_intelligence/backups/`. Filename: `contacts_YYYYMMDD_HHMMSS.json`. Max 20 kept (oldest auto-deleted).

---

## Deferred / Incomplete

| Feature | Status | Notes |
|---------|--------|-------|
| Fuzzy deduplication | Code exists (95% threshold) | Not verified for production use |
| Verification tracking | Field exists (verification_status) | No manual workflow yet |
| SMTP email validation | Not started | 27 Discogs demo emails to validate |
| YouTube enrichment Phase 2-3 | Optional | Search (100 units/call, expensive) + activity feed |
| Spotify full exploration | Optional | Related artists (403 in Dev Mode), playlists, recommendations |
| Wikidata SPARQL enrichment | Optional | Venues + labels (location, capacity, genre) |
| RM web UI integration | Not started | Browse/edit contacts in Flask UI instead of spreadsheet |
| Tool 4 bridge (Promo Engine) | Not started | promo_list field ready in Sheets |

---

## Notes

- Rekordbox: requires fresh XML export (File > Export Collection in xml format) to `data/rekordbox_library.xml`
- Spotify Related Artists API returns 403 (Dev Mode hard block) -- cannot be fixed without extended quota
- Google Sheets is the single source of truth for all contact/industry data across tools
