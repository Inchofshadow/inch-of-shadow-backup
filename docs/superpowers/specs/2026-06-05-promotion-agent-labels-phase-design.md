# Promotion Agent (Labels phase) — Design Spec

**Date:** 2026-06-05
**Status:** Approved (brainstorming), pending implementation plan

## Goal

Extend the `promotion-expert` agent with a second channel: **labels (demo outreach)**. The
agent curates demo-safe label targets for a release, drafts a personalized pitch hook per
label in Amir's voice, routes each target (email / manual DM / skip), and captures outcomes.
Tool 4 (Email Outreach) does the actual sending; the agent never touches SMTP.

## Why / context

Tool 4 already composes and sends label emails (`label_pre`/`label_post` templates, SMTP,
batch send, rate-limiting, per-target "personal hook" field). The agent adds the judgment
Tool 4 lacks: which labels truly fit this release, demo-rule safety (never email a NO-DEMOS
label), per-label voice, and the outcome learning the Farewell post-mortem showed was
missing. This is the second slice of the phased promotion agent (DJ channel shipped first).

## Architecture (approach B: agent channel + one tested helper)

```
/promo <release>  ->  promotion-expert  (DJ channel + NEW label channel)
   label channel reads:
     scene_intelligence/enriched_contacts.json  (labels: demo_email, tier, label_boss, genre)
     scene_intelligence/promotion_log.json       (READ-ONLY: already-pitched for this release)
     releases/<slug>.json + scene_intelligence/release_context.json
     scene_intelligence/ig_voice_profile.json
   helper: scene_intelligence/promo_label_shortlist.py
     -> demo-safe EMAIL targets + DM-ONLY list + excluded NO-DEMOS count
   ->  proposes: curated list (routed email / DM / skip) + a personalized hook per email target
   ->  Amir pastes hooks into Tool 4's per-target hook field + batch-sends
   ->  Amir reports outcomes; agent records promo_latest_status / last_engaged on the contact
```

Send handoff is advise-and-draft (chosen over writing `promotion_log` directly, which
sidesteps the known worktree-split bug where the RM server writes `promotion_log` from the
`curator-discovery` worktree copy).

## Demo-rule data (where it lives)

The `demo_email` field on a label carries one of: a real address (email-pitchable), the
literal `"DM ONLY"` (25 labels -> manual DM), or `"NO DEMOS"` (3 labels -> skip). Some SC
descriptions also say "not accepting demos" / "use the form" (secondary skip/flag signal).
`tier` (big/mid/small) and `label_boss` come from the contact record. `discogs_email` is a
fallback address.

## Helper: `promo_label_shortlist.py` (tested, no network)

- `is_email(value)` -> bool (a real address, i.e. contains "@" and is not "DM ONLY"/"NO DEMOS").
- `demo_route(label)` -> `"email" | "dm" | "skip"` from `demo_email` (and a "no demos" /
  "not accepting demos" scan of the SC description as a secondary skip signal).
- `shortlist(labels, existing_names, release_genre, limit=30)` -> email-route labels with a
  dark-electronic family genre match (reuse the genre logic), not already pitched, sorted by
  tier (big > mid > small) then relevance. Also returns the DM-ONLY names and the skipped
  count via a small result dict: `{"email": [...], "dm_only": [...], "skipped": N}`.
- CLI: `python3 scene_intelligence/promo_label_shortlist.py <slug> [--limit N]` prints the
  three buckets. Pure helpers unit-tested; CLI exercised manually.

The genre-match helper from `promo_dj_shortlist.py` is reused (import it) - do not duplicate.

## Capabilities (label channel)

1. **Target curation + demo routing** - helper buckets labels into email / DM-only / skip;
   agent applies genre-tier fit and dedup vs `promotion_log`; reports counts (nothing dropped
   silently).
2. **Personalized hook drafting** - per email target, a short hook in Amir's voice on why the
   track fits that label's catalog (uses `label_boss`, `genre`, `tier`). Register by timing:
   pre-release = demo angle + private link (`label_pre`); post-release = out-now + public
   links (`label_post`).
3. **Send handoff** - Amir pastes hooks into Tool 4's per-target hook field and batch-sends.
   Agent never fires SMTP.
4. **Outcome capture** - on Amir's report, update `promo_latest_status` / `last_engaged` on
   the contact (same learning loop as the DJ phase).

## Boundaries

- Agent curates and drafts; Amir sends via Tool 4. Never SMTP, never auto-send.
- Demo rules absolute: never email NO-DEMOS / "not accepting demos"; route DM-ONLY to manual;
  flag "use the form" rather than auto-email.
- Dedup: never re-pitch a label already pitched for this release (reads `promotion_log`).
- Own-release-label nuance: the "never engage own-release labels" rule is about engagement
  automation, not demo pitching. Re-pitching MM Discos / Stereo Society / NaNa Disc is
  legitimate - the agent FLAGS them, does not exclude them; Amir decides.
- Copy: professional, peer-to-peer industry register in Amir's voice (not clickbait). No
  double dash, no em dash.
- Scope: label channel only; DJ channel unchanged; never touches CC engagement state.

## Components to build

1. `scene_intelligence/promo_label_shortlist.py` (+ `tests/test_promo_label_shortlist.py`).
2. `.claude/agents/promotion-expert.md` - add a Label-channel section (edit existing file).
3. `.claude/skills/promo/SKILL.md` - one-line note that it now covers labels too (edit).

## Out of scope (later phases / other specs)

- Playlists (needs a curator DB), press channels.
- Writing `promotion_log` directly / fixing the worktree-split bug (a separate fix).
- Web-UI / Tool-3 integration ("path C").
