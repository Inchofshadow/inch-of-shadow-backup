# Promotion Agent (Phase 1: DJ channel) — Design Spec

**Date:** 2026-06-03
**Status:** Approved (brainstorming), pending implementation plan

## Goal

A `/promo` skill + `promotion-expert` subagent — the promotion "Brain." Phase 1 covers the
**DJ channel only**: pick DJ targets for a release, draft DMs in Amir's voice, propose a
volume-safe send plan, and capture outcomes going forward. It is a data-builder: it works
with what exists, flags gaps, and accumulates outcome data per campaign (no backfill).

## Why / context

Tool 3 (Promotion Engine) and Tool 4 (Email Outreach, SMTP + templates) already handle
discovery and email sending. The promotion agent is the strategist Brain on top, starting
with the channel the Farewell post-mortem flagged as the missing play-driver: DJs. DJ promo
already has a head start — a persistent pool, a voice template, and per-contact promo
tracking exist.

This is one slice of a larger system. Out of scope for Phase 1: labels, playlists, press
(later phases); email sending (Tool 4); web-UI integration (a possible Tool-3 path "C"
later). Each later channel is its own spec.

## Architecture (approach B: agent + one tested helper)

```
/promo <release>  ->  promotion-expert subagent (Brain; DJ channel in Phase 1)
   reads:  scene_intelligence/dj_promo_targets.json   (the pool + per-release send/status)
           plans/dj-promo-dm-template.md                (Amir's voice: cold/warm variants)
           scene_intelligence/ig_voice_profile.json     (voice grounding)
           releases/<slug>.json + scene_intelligence/release_context.json
           docs/sc-agent-context.md, docs/ig-engagement-sop.md (DM etiquette, caps, exclusions)
   helper: scene_intelligence/promo_dj_shortlist.py
           -> shortlist NEW DJ candidates from enriched_contacts.json
              (genre fit + SoundCloud reach + not already in pool + not protected)
   ->  proposes: target list + drafted DMs + a batched, volume-safe send plan
   ->  writes per-release send-flags/status into dj_promo_targets.json (on Amir's confirm)
   ->  Amir sends the DMs manually; reports back; agent records outcomes
```

## Data structures

`scene_intelligence/dj_promo_targets.json` (exists): `{created, note, targets: [...]}`. Each
target: `name`, `ig_handle`, `sc_url`, `tier` (warm | cold | ...), `genre`,
`preferred_channel` (ig | sc), `in_si_db`, `notes`, and `releases` (dict keyed by release
slug -> `{send: true|false|null, status: "pending"|"sent"|"replied"|"played"|...}`).

The agent reads/updates `releases[<slug>]` for the active release and may append new targets
(from the helper shortlist) on Amir's confirm. It also updates the contact's
`promo_latest_status` / `last_engaged` in `enriched_contacts.json` when Amir reports an
outcome.

## Capabilities (Phase 1, DJ channel)

1. **Target selection** — review the pool for the active release: recommend per-release
   `send` flags, and use the helper to shortlist NEW candidates from the 565 SI DJs (genre
   fit + SC reach + not already in pool + not protected). Amir approves who is in.
2. **DM drafting** — personalize `dj-promo-dm-template.md` per target in Amir's voice: warm
   vs cold variant (warm = prior contact / collaborator -> adds the WAV offer + a personal
   line), filling name, track, one-line hook, and the SoundCloud track link. Channel per
   `preferred_channel`.
3. **Send plan** — propose a batched schedule that respects DM-volume safety: split across
   2-3 days, warm contacts first, varied text per message. The agent refuses a single-day
   blast. The agent plans; Amir sends.
4. **Outcome capture** — as Amir reports back ("X replied", "Y played it on SC", "Z wants
   the WAV"), update `status` in `dj_promo_targets.json` and `promo_latest_status` /
   `last_engaged` on the contact. Builds the data going forward.

## DM-sending model + boundaries

- **The agent drafts and plans only. Amir sends the DMs manually.** Not CC (the SOP forbids
  CC opening DMs during an engagement session), not auto-send, not during any engagement run.
- **Volume safety:** send plan always splits across 2-3 days, warm first, varied text
  (bot-warning history + the Farewell "12-in-a-day was too many" lesson). Refuse single-day
  blasts.
- **Exclusions:** never pitch personal friends, own-release labels (MM Discos, Stereo
  Society, NaNa Disc), or anyone marked `no_longer_engage`.
- **Copy:** in Amir's voice, channel-appropriate. DJ DMs are genuine and peer-to-peer (the
  Ilayda-template register), so not clickbait. Clickbait is NOT globally banned — it is
  situational and Amir's call for audience-facing content; just not the register for peer
  DMs. No double dash, no em dash anywhere (single hyphen with spaces, or sentence breaks).
- **Scope fences:** DJ channel only; does not touch Tool 4 email (labels/media, later);
  writes only to its own working file `dj_promo_targets.json` (on confirm) + contact promo
  fields; never edits CC's engagement state files.

## Helper: `promo_dj_shortlist.py` (tested, no network)

- `genre_match(release_genre, dj_genre)` -> bool (case-insensitive token overlap on the
  core genres, e.g. ebm / acid / electro / techno / dark disco).
- `shortlist(djs, existing_names, release_genre, min_sc_followers=200)` -> ranked list of DJ
  candidates not already in the pool, with a genre match and SC reach, excluding any with a
  protected/`no_longer_engage` flag. Sorted by relevance_score then soundcloud_followers.
- CLI: `python3 scene_intelligence/promo_dj_shortlist.py <release-slug> [--limit N]` prints
  the shortlist. Pure helpers are unit-tested; the CLI wiring is exercised manually.

## Components to build

1. `.claude/skills/promo/SKILL.md` — the `/promo` front door (gitignored, local-only).
2. `.claude/agents/promotion-expert.md` — the Brain, DJ channel in Phase 1 (gitignored).
3. `scene_intelligence/promo_dj_shortlist.py` (+ `tests/test_promo_dj_shortlist.py`) — the
   candidate-shortlisting helper.

## Out of scope (later phases / other specs)

- Label, playlist, press channels.
- Email sending (Tool 4 already does it).
- Web-UI / Tool 3 integration (possible path "C" later).
- Contactability consolidation as a standalone project (the agent flags gaps incrementally).
- Deep cross-channel outcome analytics (accumulates first).
