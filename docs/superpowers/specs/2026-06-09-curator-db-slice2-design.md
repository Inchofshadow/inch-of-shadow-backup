# Curator DB - Slice 2 (pitch drafting + outcome tracking) Design Spec

**Date:** 2026-06-09
**Status:** Approved (brainstorming), pending implementation plan

## Goal

Systematize curator pitching: add a **playlist/curator channel** to the existing
`promotion-expert` agent that drafts per-curator pitches in Amir's voice (free IG DM +
concise Groover variant), and track outcomes per curator - including auto-detecting playlist
adds via the Spotify API. Consumes the curator DB built in Slice 1.

## Why / context

Slice 1 produced the curator DB (curators as `category:"curator"` contacts, ranked, tiered,
with verified free/paid routes). Amir then hand-drafted 3 DMs to prove the voice. Slice 2
turns that into a repeatable capability, reusing the promotion agent's existing channel
pattern (DJ, Label) so curators become the third channel with the same drafting + outcome
machinery.

## Architecture: curators as the 3rd promotion channel

The `promotion-expert` agent gains a Playlist/Curator channel alongside DJ and Label. It
reads curator-contacts + their playlists + the active release, and drafts route-appropriate
pitches. `/promo` is the front for all three channels. No new agent.

## Components to build

1. **`plans/curator-pitch-template.md`** (new) - two templates in Amir's voice, like
   `dj-promo-dm-template.md`:
   - **Free IG DM**: warm, personal (the register of the 3 hand-drafted DMs) - greeting,
     a line about their playlist, the track + one-line vibe, the Spotify link, a light tease
     of the upcoming release, thanks.
   - **Groover**: concise/direct (1-2 lines: genre fit + the hook) for skim-heavy curators.
   - Placeholders: `[CURATOR] [PLAYLIST] [TRACK] [LINK] [VIBE]`.
2. **`.claude/agents/promotion-expert.md`** (edit) - add a "Playlist/Curator channel"
   section (capabilities + rules below).
3. **`.claude/skills/promo/SKILL.md`** (edit) - one line: now covers DJ + Label + Curator.
4. **`scene_intelligence/curator_check_adds.py`** (+ `tests/test_curator_check_adds.py`) -
   auto-detect playlist adds:
   - `track_id_from_url(url)` and `track_in_playlist(track_id, playlist_track_ids)` (pure,
     tested).
   - CLI: for the active release, get its Spotify track id; for each curator that has been
     pitched (`promo_latest_status` in {sent, pitched}), fetch the curator's playlist tracks
     via the Spotify API (reusing `discover_curators` auth) and, if the release track id is
     present, set `promo_latest_status = "added"`. Pre-announces the call count (1 per pitched
     playlist).

## Capabilities (curator channel of the agent)

1. **Target selection** - read curator-contacts; prioritize by Slice 1's tier: free verified
   routes = draft all; paid = the proven (cross-list >=2, top/good fit) set; skip `suspect`
   and unverified-free (flag them). Uses `curator_pitch_sheet` ordering.
2. **Pitch drafting** - per curator, route-appropriate (free -> warm IG DM; paid -> concise
   Groover), personalized to THAT playlist + its genre, in Amir's voice, with the live track
   link pulled from `releases/<slug>.json` (Farewell now; The Deceiver at its release), plus a
   light tease of the upcoming one. No clickbait, no em dash, no double dash.
3. **Outcome capture** - log per curator on the contact (`promo_latest_status`: sent / added /
   passed / ignored; `last_engaged`). Manual reporting from Amir AND auto-detection of adds via
   `curator_check_adds.py`.

## Boundaries

- The agent DRAFTS only. Amir sends IG DMs and submits to Groover manually. Never sends, pays,
  or submits.
- Drafting makes no API calls. The only API use is `curator_check_adds.py` (read-only Spotify
  playlist-track fetches), always pre-announced with the call count.
- Respects the Slice 1 tier: never silently drafts for `suspect`/unverified curators.
- Copy: peer-to-peer, in Amir's voice, no clickbait, no em dash, no double dash.
- Scope: curator channel only; DJ and Label channels unchanged; does not modify the DB-build
  scripts (`curator_enrich`, `curator_pitch_sheet`) - it consumes their output.
- Outcome tracking reuses existing contact promo fields; no new store.

## Out of scope (later)

- A dedicated `/curators` skill (the `/promo` front already covers it).
- The RM Curator pill/badge UI + Sheets curator column (on the branch).
- Auto-sending or Groover automation (always manual).
