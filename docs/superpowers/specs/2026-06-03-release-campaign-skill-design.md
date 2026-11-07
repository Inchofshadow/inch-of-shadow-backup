# Release/Campaign Skill — Design Spec

**Date:** 2026-06-03
**Status:** Approved (brainstorming), pending implementation plan

## Goal

A stage-aware `/release` skill that owns a music release end-to-end — plan, prep, release
day, capture outcomes, post-mortem — and closes a learning loop so each release improves
the next. It orchestrates existing pieces (never duplicates them) and is the connective
tissue + measurement layer that the Farewell post-mortem showed was missing.

## Why (from the Farewell post-mortem)

Farewell could not be measured: outcomes (label replies, a DJ boss playing the track on
SC) were never captured, channels were narrow (labels-only), and lessons lived in static
prose. This skill fixes the structural gap: capture outcomes with low friction going
forward, and feed lessons back into the next release's planning.

## Architecture (approach B: skill + thin helper)

```
/release <name>
   -> release_status.py detect_stage(releases/<slug>.json, today)
   -> /release skill drives that stage: shows status + next actions,
      runs safe automatable steps only on confirmation (guide + do-on-confirm)
   -> delegates to existing pieces:
        PLAN        : read plans/release-lessons.md + plans/release-platform-deadlines.md
        PREP        : call the release-prep skill
        RELEASE DAY : walk plans/release-day-playbook.md; offer ig-expert for reel/caption/Canva
        CAPTURE     : ig_fetch_insights.py (auto, pre-announced) + conversational quick-log
        POST-MORTEM : release_status.py aggregate(slug) -> skill synthesizes -> append lessons
```

The orchestration, voice, and judgment live in the skill (prose). The two things that are
real data work — stage detection and post-mortem stat aggregation — live in a small,
tested Python helper. `release-prep` stays exactly as-is; the skill calls it.

## The five stages (auto-detected, user-overridable)

1. **Plan** (before prep) — surface last release's lessons (`plans/release-lessons.md`) so
   they are applied, plus platform deadlines (Spotify pitch T-31/40, pre-saves at T-14,
   r/EBM 30-day cooldown — the Farewell misses).
2. **Prep** — delegate to `release-prep` (SEO copy, premiere contacts, checklist). No dup.
3. **Release day** — walk `plans/release-day-playbook.md` ordered steps; offer `ig-expert`
   for the reel/caption + Canva art.
4. **Capture** (release day -> ~T+25) — auto-pull IG/SC/DSP stats (pre-announced API
   calls); user conversationally quick-logs human outcomes, skill structures + saves them.
5. **Post-mortem** — aggregate everything into a report (like the Farewell one), then
   append dated/tagged lessons to `plans/release-lessons.md`. The Plan stage of the next
   release reads them. This closes the learning loop.

## Data model

Single source per release, in the main repo (sidesteps the RM worktree-split bug).

`releases/<slug>.json` gains:
```json
"stage": "capture",
"outcomes": {
  "stats": {
    "ig": {"reach": 0, "saved": 0, "shares": 0, "views": 0},
    "sc": {"plays": null, "reposts": null},
    "dsp": {"spotify_saves": null}
  },
  "human": [
    {"who": "Mechatronica", "type": "label", "event": "replied",
     "sentiment": "interested", "note": "...", "logged": "2026-06-03"},
    {"who": "DJ X", "type": "dj", "event": "played_on_sc", "note": "..."}
  ]
}
```

New file `plans/release-lessons.md`: accumulating, dated, release-tagged lessons. Seeded
from Farewell's Part E so existing knowledge is not lost. Written by the post-mortem
stage, read by the plan stage.

## Helper: `release_status.py` (two jobs, both testable, no network in tests)

1. `detect_stage(release, today)` -> `plan | prep | release_day | capture | post_mortem`
   from `release_date` vs `today` plus checklist/outcome state. A stored `stage` field can
   override the inferred value.
2. `aggregate(slug)` -> pulls this release's IG insights (matched by date/permalink from
   `scene_intelligence/ig_insights.json`), SC tracker, DSP, and the `promotion_log`
   campaign into one summary dict the skill turns into the post-mortem.

## Boundaries

- No posting, DMs, or live engagement (that is the artist / CC).
- Nothing fires without confirmation; IG insight fetches are pre-announced with call
  counts.
- Does not own outreach detail. When the Promotion agent is built later, it owns
  `promotion_log`; `/release` only reads it for the post-mortem. For now `/release`
  captures outcomes into the release JSON, so there is no dependency on the unbuilt agent.
- Inherits all standing rules (no double-dash, no Software Zero, IG risk caps, genre
  spelling "Synthwave") via the skills/agents it delegates to.

## Components to build

1. `.claude/skills/release/SKILL.md` — the stage-aware orchestrator skill.
2. `scene_intelligence/release_status.py` (+ `tests/test_release_status.py`) — stage
   detection + post-mortem aggregation.
3. `plans/release-lessons.md` — the accumulating lessons store, seeded from Farewell Part E.
4. Release JSON additions (`stage`, `outcomes`) — written by the skill/helper; backward
   compatible (absent on old releases, created on first use).

## Out of scope

- The Promotion agent (separate, next project).
- Live engagement / posting automation.
- Backfilling Farewell's historical outcomes (post-mortem already extracted the lessons).
