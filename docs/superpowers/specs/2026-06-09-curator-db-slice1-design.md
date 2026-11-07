# Curator DB - Slice 1 Design Spec

**Date:** 2026-06-09
**Status:** Approved (brainstorming), pending implementation plan

## Goal

Build the first slice of the playlist-curator system for Inch of Shadow: resurrect the
already-built discovery engine onto main, enrich playlist targets via the Spotify API,
store curators as contacts, and produce a ranked, contact-routed pitch sheet for The
Deceiver (release 2026-07-10, dark EBM/electro) and Farewell (live). Pitch DRAFTING and an
agent front are later slices.

## Why / context

Most of this was already built and stranded on the `curator-discovery` branch:
`discover_curators.py` (539-line Spotify + SoundCloud engine), `curator_config.py` (genre
keywords + thresholds), and their tests. The engine already writes curators into
`enriched_contacts.json` as `category:"curator"` contacts (deduped, with backup) and has
`fetch_spotify_playlist_detail()` returning description + followers + owner. Plus a manual
reference-artist research method + 17 hand-picked targets in
`playlist_curator_targets.json` (the handoff). Slice 1 unifies these and adds the only
genuinely missing logic: contact extraction + ranking.

## Data model: curator = contact

A curator is a contact in `enriched_contacts.json` with `category:"curator"`,
`sub_type:"spotify"` (owner-keyed; dedup by `spotify_id`/name). It carries:
- owner identity (name, `spotify_url`, `spotify_id`),
- their playlists (the engine's existing aggregate fields: `top_playlist_name/followers/url`,
  `playlist_total_followers`, `playlist_count`, plus a per-playlist list with fit),
- `contact` `{ig, email, route, submission}` - extracted from playlist descriptions,
- `fit` (best tier across their playlists: top | good | partial),
- `source` (manual | engine), `confidence` (manual=high, engine=low),
- `reference_artists` + `cross_list_count` (how many same-lane artists they were
  "discovered on" - the ranking signal),
- reused promo fields (`promo_latest_status`, `last_engaged`) for outcome tracking, exactly
  like DJs and labels.

This makes curators a natural third promotion channel (DJ -> label -> playlist) reusing the
existing pipeline (dedup, scoring, Sheets, outcome tracking).

## Routing (free vs paid)

Per curator, `contact.route` is set automatically:
- **free** - an IG handle or email was found in a playlist description; Amir DMs/emails directly.
- **paid** - no direct contact found; `contact.submission` defaults to **groover** (EU-focused,
  fits the Berlin/dark-electronic scene; SubmitHub is the alternative Amir can choose per pitch).

The DB never submits, pays, or DMs - it routes and (in Slice 2) drafts. Amir executes.
The value on cost is maximizing free routes by extracting contacts from descriptions; a
meaningful share will still be paid (many descriptions carry no contact).

## Ranking + legitimacy (rank by real-list signal, not vanity)

Save/follower count is a vanity number: many high-save dark-electronic playlists are bot
farms or pay-to-play lists with no real listeners, and a placement only pays off if real,
engaged listeners save/complete the track (which is what nudges Spotify's own algorithm).
So the ranker weights **legitimacy over raw saves**:

- Primary sort: `fit` tier (top > good > partial).
- Then `cross_list_count` - how many same-lane reference artists this curator was
  "discovered on." A list driving streams for multiple real artists is the strongest
  legitimacy + relevance signal. Weighted ABOVE saves.
- Then `saves` (tiebreaker only).

Plus a legitimacy flag: a curator with high saves but `cross_list_count == 0` (engine-only
keyword hit, never confirmed via a reference artist) is flagged `suspect: true` / low
confidence - a likely farm to vet manually before pitching, not auto-trusted.

## Components to build

1. **Resurrect from the branch -> main** (file-copy, verify they run on current main; no merge
   of the stale branch): `scene_intelligence/curator_config.py`,
   `scene_intelligence/discover_curators.py`, `tests/test_curator_config.py`,
   `tests/test_discover_curators.py`.
2. **New `scene_intelligence/curator_enrich.py`** (+ `tests/test_curator_enrich.py`):
   - `extract_contact(description) -> {ig, email, route, submission}` (pure, regex, tested:
     IG handle, email, and the free/paid + groover-default routing).
   - flow: read the staging file -> for each target with a Spotify URL, parse the playlist id,
     call `fetch_spotify_playlist_detail` (reused from the engine) -> fill saves + description +
     contact -> upsert a `category:"curator"` contact into `enriched_contacts.json` (reusing the
     engine's load/backup/save + dedup). Manual targets get `source:"manual"`, `confidence:"high"`.
3. **New `scene_intelligence/curator_pitch_sheet.py`** (+ `tests/test_curator_pitch_sheet.py`):
   - `rank(curators) -> ranked list` (pure, tested: sort by fit tier, then cross_list_count,
     then saves - per the legitimacy rules above) and a `suspect` flag for high-saves /
     zero-cross-list curators.
   - CLI: prints the ranked pitch sheet (playlist · curator · saves · fit · cross-list ·
     contact · route · suspect?) for a release slug, pitching The Deceiver + Farewell.
4. **Staging file** `scene_intelligence/playlist_curator_targets.json` (the existing 17) stays
   as the low-friction place Amir pastes reference-artist "Discovered on" findings (name, url,
   fit, reference_artist). The enricher reads it.

The resurrected engine plugs in as the **expander**: `discover_curators.py --spotify` appends
`source:"engine", confidence:"low"` curator-contacts (keyword-search candidates), deduped.

## Data flow

paste targets in staging -> `curator_enrich.py` (Spotify API enrich + write curator-contacts)
-> optional `discover_curators.py --spotify` (low-confidence expander) -> `curator_pitch_sheet.py`
(rank) -> pitch sheet. Outcomes later recorded on the curator-contacts like DJs/labels.

## Boundaries

- Never submits, pays, or DMs. Routes (free vs paid, Groover default) and, in Slice 2, drafts.
  Amir executes.
- Spotify API only (Amir's own creds, official, free tier) for playlist search + metadata +
  descriptions. "Discovered on" (which playlists drive an artist's streams) is NOT in the API -
  Amir supplies that manually into the staging file.
- No Playwright / scraping (project rule).
- Additive to `enriched_contacts.json`: backup before write, dedup, never delete contacts.
- Curators-as-contacts reuse the promo outcome fields; no new tracking store.

## Out of scope (later slices)

- Pitch drafting per curator in Amir's voice (Slice 2 - reuse `seo_copy_generator.py`'s
  `spotify_pitch`).
- A `/curators` skill/agent front + the promotion agent's playlist channel (Slice 3).
- The RM Curator pill/badge UI + Sheets curator column (on the branch; later).
- Auto-resolving a playlist URL from a name via search (manual URL paste for now).
